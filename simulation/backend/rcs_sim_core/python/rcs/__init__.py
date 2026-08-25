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
from rcs import _core as _core  # noqa: F401  (compiled extension)
from rcs._core import common, sim  # noqa: F401

__all__ = ["common", "sim", "_core"]
