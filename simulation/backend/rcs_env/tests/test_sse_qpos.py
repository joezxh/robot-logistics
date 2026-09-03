"""
Smoke test: the SSE server emits at least one qpos frame.
"""
from __future__ import annotations

import threading
import time
import urllib.request

from rcs_env.serve import sse_qpos


def test_sse_emits_qpos_frame():
    server = sse_qpos.make_server(port=0)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        req = urllib.request.urlopen(f"http://127.0.0.1:{port}/stream", timeout=10)
        # Read one SSE frame: a "data: {...}\n\n" block.
        buf = b""
        deadline = time.time() + 8
        while b"\n\n" not in buf and time.time() < deadline:
            chunk = req.read(1)
            if not chunk:
                break
            buf += chunk
        req.close()
        assert b"data:" in buf, "no SSE data frame received"
        import json

        payload = json.loads(buf.decode("utf-8").split("data:", 1)[1].strip())
        assert "data" in payload and "qpos" in payload["data"]
        assert len(payload["data"]["qpos"]) == 21
    finally:
        server.shutdown()
