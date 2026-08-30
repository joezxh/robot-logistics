"""rcs-sim-core: C++ MuJoCo simulation core for robot-control-stack.

This package wraps the compiled ``_core`` extension, which exposes two pybind11
submodules:

* ``rcs.common``  - Pose, Robot, Kinematics, RobotType, RobotPlatform, config/state bases
* ``rcs.sim``     - Sim, SimRobot, SimGripper, SimTilburgHand, SimCameraSet, Renderer, GuiServer

Typical usage::

    import rcs
    sim = rcs.sim.Sim(xml_path, rcs.sim.SimConfig())
    robot = rcs.sim.SimRobot(sim, "robot0_")
    robot.set_qpos([0, -0.78, 0, -1.57, 0, 1.0, 0])

The higher-level, pure-Python environment layer lives in
``robot_logic.simulation.backend.rcs_env`` and imports from this core.
"""
import os
import sys

# ``_core.pyd`` links against ``mujoco.dll``. On Windows, when the extension
# module is loaded the OS does not automatically search the mujoco package's
# own DLL directory, which surfaces as "DLL load failed: 找不到指定的模块".
# Registering that directory on the process DLL search path here fixes it for
# any clean ``import rcs`` without requiring mujoco to be imported first.
if sys.platform == "win32":
    try:
        import mujoco as _mujoco  # noqa: F401

        os.add_dll_directory(os.path.dirname(_mujoco.__file__))
    except Exception:  # noqa: BLE001  (let a real _core import error surface below)
        pass

from rcs import _core as _core  # noqa: F401  (compiled extension)
from rcs._core import common, sim  # noqa: F401

__all__ = ["common", "sim", "_core"]
