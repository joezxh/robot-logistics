"""
SSE telemetry stream for the Microduck frontend viewer.

Run standalone:
    python -m rcs_env.serve.sse_qpos --port 8110
    python -m rcs_env.serve.sse_qpos --policy models/microduck-walk-ppo.onnx

It loads a Microduck variant and publishes the 21-dim MuJoCo qpos on an SSE
endpoint (``/stream``). With ``--policy`` it steps a trained policy (SB3 .zip or
ONNX .onnx) so the viewer shows learned locomotion; otherwise it steps a random
policy. Pure stdlib + mujoco (no FastAPI, which is not in the sim venv).
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional

import numpy as np

from rcs_env.envs.microduck import MicroduckEnv
from rcs_env.envs.twin import DigitalTwinSink, InMemoryTransport
from rcs_env.envs.wrappers import DigitalTwinWrapper


def _load_policy(path: str):
    if path.endswith(".onnx"):
        from rcs_env.onnx.microduck_onnx import MicroduckOnnxPolicy
        return MicroduckOnnxPolicy(path)
    if path.endswith(".zip"):
        from stable_baselines3 import PPO
        return PPO.load(path, device="cpu")
    raise SystemExit(f"unsupported policy file (need .onnx or .zip): {path}")


def _policy_predict(policy, obs):
    try:
        result = policy.predict(obs, deterministic=True)
    except TypeError:
        result = policy.predict(obs)
    if isinstance(result, tuple):
        return result[0]
    return result


class PolicyThread(threading.Thread):
    """Steps the env with a trained/random policy and pushes telemetry to the sink."""

    def __init__(self, env: MicroduckEnv, sink: DigitalTwinSink,
                 policy=None, hz: float = 50.0, stop: Optional[threading.Event] = None):
        super().__init__(daemon=True)
        self.env = env
        self.sink = sink
        self.policy = policy
        self.period = 1.0 / hz
        self._stop = stop or threading.Event()
        self.obs, _ = env.reset(seed=0)

    def run(self) -> None:
        while not self._stop.is_set():
            if self.policy is not None:
                action = np.asarray(
                    _policy_predict(self.policy, self.obs), dtype=float
                ).reshape(-1)
            else:
                action = self.env.action_space.sample()
            out = self.env.step(action)
            if len(out) == 5:
                self.obs, _reward, term, trunc, info = out
                done = term or trunc
            else:
                self.obs, _reward, done, info = out
            if done:
                self.obs, _info = self.env.reset()
            if self.sink is not None:
                self.sink.push(info)
            time.sleep(self.period)


class QposHandler(BaseHTTPRequestHandler):
    env: MicroduckEnv
    sink: DigitalTwinSink
    stop: threading.Event

    def do_GET(self):
        if self.path == "/stream" or self.path.startswith("/stream?"):
            self._stream()
        else:
            self.send_response(404)
            self.end_headers()

    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        try:
            while not self.stop.is_set():
                qpos = self.env.unwrapped.engine.qpos().tolist()
                payload = json.dumps(
                    {
                        "device_id": "microduck-01",
                        "ts": time.time(),
                        "data": {"qpos": qpos},
                    }
                )
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.02)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


def make_server(port: int = 8110, variant: str = "walk",
                policy: Optional[str] = None, hz: float = 50.0) -> ThreadingHTTPServer:
    """Build (but do not start) the SSE server; optionally driven by a policy."""
    sink = DigitalTwinSink(device_id="microduck-01", transport=InMemoryTransport(), rate=0)
    base_env = MicroduckEnv(variant=variant)
    base_env.reset(seed=0)
    # Wrap so every step also emits a digital-twin telemetry record into `sink`.
    env = DigitalTwinWrapper(base_env, sink=sink)
    stop = threading.Event()
    p = _load_policy(policy) if policy is not None else None
    # sink is owned by the wrapper; pass None so we don't double-push.
    PolicyThread(env, None, policy=p, hz=hz, stop=stop).start()
    QposHandler.env = env
    QposHandler.sink = sink
    QposHandler.stop = stop
    return ThreadingHTTPServer(("0.0.0.0", port), QposHandler)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8110)
    ap.add_argument("--variant", default="walk")
    ap.add_argument("--policy", default=None, help=".onnx or .zip policy to drive the env")
    ap.add_argument("--hz", type=float, default=50.0)
    args = ap.parse_args()
    server = make_server(port=args.port, variant=args.variant, policy=args.policy, hz=args.hz)
    print(f"[sse] Microduck qpos stream on http://localhost:{args.port}/stream"
          + (f" (policy={args.policy})" if args.policy else ""))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.RequestHandlerClass.stop.set()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
