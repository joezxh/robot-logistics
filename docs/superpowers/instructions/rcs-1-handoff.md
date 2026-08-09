# RCS-1 Handoff

## What ships

- `backend/rcs/` — isolated subpackage; no Phase 1-5 service is modified.
- `backend/main.py` — one new import + one `include_router` + lifespan chain.
- `scripts/verify_rcs1.sh` — end-to-end smoke + JSON receipt.
- New deps: none (the spec mentions `uvloop==0.19.0` as a soft opt-in; the user
  has not asked for it and the tests pass on the stock `uvicorn`).

## How to run

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000
# In another shell:
curl http://127.0.0.1:8000/api/rcs/registry
curl -X POST http://127.0.0.1:8000/api/rcs/robot-01/command \
  -H "Content-Type: application/json" \
  -d '{"type":"move_j","target_joints":[0.1,0,0,0,0,0]}'
curl http://127.0.0.1:8000/api/rcs/robot-01/state
```

## How to test

```bash
python -m pytest backend/tests backend/rcs/tests -v
bash scripts/verify_rcs1.sh
```

The verify script writes a JSON receipt to
`docs/superpowers/specs/verify_artifacts/rcs1-*.json`. Expected fields:

- `post_command_state.mode` is `running` (or `idle` if the trajectory already finished)
- `estop_state.mode` is `e_stop`
- `summary.ok` is `true`

### Windows / WSL notes

`bash scripts/verify_rcs1.sh` works on Windows when invoked from PowerShell.
The script auto-detects WSL (`/proc/version` contains "Microsoft") and routes
the HTTP smoke test through `powershell.exe` (Invoke-WebRequest) because WSL
cannot reach a Windows-host localhost over the loopback interface. On
Linux/macOS the script uses `curl` directly. Override the interpreter with
`PYTHON_BIN=...` if you want a specific `python` binary.

## Out of scope (RCS-2..5 + Phase 5 follow-ups)

- Gazebo/real HAL implementations — only SimHAL is provided.
- AlertEngine subscription — EventBus is in place but has no subscribers.
- supervisor role model — clear_estop is currently allowed for any
  authenticated user; tighten when RBAC is added in RCS-5/Phase 5 HMI.
- IK singularity avoidance — numerical solver; out-of-workspace raises `NoSolution`.
- Multi-machine map planning — AGV uses point-to-point trapezoidal; map
  planning belongs to RCS-3.
- Frontend panels — RCS-5.
- Auto-idle on trajectory completion — controllers stay in `running` mode
  once a command finishes; the `/state` accept-either test
  (`mode in ("running", "idle")`) accommodates this.
