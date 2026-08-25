# rcs-sim-core

C++ MuJoCo simulation core migrated from
[robot-control-stack](https://github.com/.../robot-control-stack) (`src/sim` + `src/pybind`).

This is the **physics kernel** behind `robot_logic.simulation`. It compiles to a
single Python extension module `rcs._core` exposing two pybind11 submodules:

| submodule            | contents |
|----------------------|----------|
| `rcs.common`         | `Pose`, `Robot`, `Kinematics`, `RobotType`, `RobotPlatform`, config/state base classes |
| `rcs.sim`            | `Sim`, `SimRobot`, `SimGripper`, `SimTilburgHand`, `SimCameraSet`, `Renderer`, `GuiServer`, `GuiClient` |

## Directory layout

```
rcs_sim_core/
├── CMakeLists.txt            # top-level build
├── pyproject.toml            # scikit-build-core
├── include/rcs/              # copied from robot-control-stack/include/rcs
│   ├── Pose.h  Robot.h  Kinematics.h  Camera.h  utils.h ...
├── src/
│   ├── rcs/                  # common lib sources (Pose/Robot/Kinematics/utils/Camera)
│   ├── sim/                  # Sim / SimRobot / SimGripper / SimTilburgHand / camera / renderer / gui_*
│   └── pybind/rcs.cpp        # pybind11 bindings (common + sim submodules only)
└── python/rcs/__init__.py    # thin re-export of the compiled _core
```

## Prerequisites (build host)

| dependency | why | install hint |
|-----------|-----|--------------|
| C++17 compiler | build | MSVC 2019+ / GCC 9+ / Clang 10+ |
| CMake >= 3.18 | build | `pip install cmake` |
| Ninja | build | `pip install ninja` |
| pybind11 | bindings | `pip install pybind11` |
| mujoco (C lib + headers) | physics | `pip install mujoco` (wheels ship lib+headers) |
| pinocchio | IK / kinematics | conda: `conda install -c conda-forge pinocchio` |
| Boost.Interprocess (headers) | shared-memory GUI | system `libboost-dev` or `pip install boost` (header-only) |
| Eigen3 (headers) | linear algebra | system `libeigen3-dev` |
| EGL / GL | offscreen render | system `libegl1 libgl1` (Linux); MuJoCo bundles on Windows |

If MuJoCo is not auto-discovered from the `mujoco` pip wheel, set
`MUJOCO_ROOT=<prefix with lib/ and include/>` before building.

## Build

```bash
cd robot-logic/simulation/backend/rcs_sim_core
pip install -e .            # scikit-build-core compiles rcs._core in place
```

Or a wheel:

```bash
python -m build            # produces dist/rcs_sim_core-*.whl
pip install dist/rcs_sim_core-*.whl
```

## Verify

```python
import rcs
print(rcs.sim.Sim, rcs.sim.SimRobot, rcs.sim.SimGripper, rcs.sim.SimCameraSet)
# expected: <class 'rcs._core.sim.Sim'> ...
```

## Notes

* The binding (`src/pybind/rcs.cpp`) was trimmed to **only** the `common` and `sim`
  submodules — robot-control-stack's operator/rpc Python layers are intentionally
  excluded; they are reimplemented in `robot_logic` as needed.
* Windows: link `opengl32`; MuJoCo provides the GL loader. Linux: link `EGL` + `GL`.
* `GuiServer`/`GuiClient` use Boost.Interprocess shared memory; the viewer side runs
  in a separate process via `mujoco.viewer`.
