"""
SSE telemetry stream for the Microduck frontend viewer.

Run standalone:
    python -m rcs_env.serve.sse_qpos --port 8110

It loads a Microduck variant, steps a random policy, and publishes the 21-dim
MuJoCo qpos on an SSE endpoint (``/stream``). Any SSE client (the Vue viewer's
EventSource) can subscribe. Pure stdlib + mujoco (no FastAPI, which is not in
the sim venv).
"""
from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple

import numpy as np

from rcs_env.envs.microduck import MicroduckEnv


class QposHandler(BaseHTTPRequestHandler):
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
        env = MicroduckEnv(variant="walk")
        env.reset(seed=0)
        try:
            while not self.wfile.closed:
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                qpos = env.engine.qpos().tolist()
                payload = json.dumps(
                    {
                        "device_id": "microduck-01",
                        "ts": time.time(),
                        "data": {"qpos": qpos, "reward": float(reward)},
                    }
                )
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.05)
                if terminated or truncated:
                    env.reset(seed=0)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


def make_server(port: int = 8110) -> ThreadingHTTPServer:
    """Build (but do not start) the SSE server on the given port."""
    return ThreadingHTTPServer(("0.0.0.0", port), QposHandler)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8110)
    ap.add_argument("--variant", default="walk")
    args = ap.parse_args()
    server = make_server(port=args.port)
    print(f"[sse] Microduck qpos stream on http://localhost:{args.port}/stream")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
