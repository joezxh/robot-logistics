import pytest
from rcs.controllers.agv import AgvController
from rcs.state.profile import DeviceProfile, Morphology, Limits
from rcs.state.joint import JointState
from rcs.state.command import Command, CommandType


@pytest.fixture
def agv_profile():
    return DeviceProfile(
        device_id="agv-01",
        morphology=Morphology.AGV,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-2.0, -2.0],
            pos_upper=[2.0, 2.0],
            vel_max=[1.0, 1.0],
            acc_max=[2.0, 2.0],
        ),
        home_joints=[0.0, 0.0],
    )


def test_agv_reaches_linear_velocity_target(agv_profile):
    ctrl = AgvController(agv_profile)
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[1.0, 0.0]))
    cur = JointState(positions=[0.0, 0.0], velocities=[0.0, 0.0], efforts=[0.0, 0.0], device_id="agv-01")
    last = cur
    for _ in range(200):
        last = ctrl.update(cur)
    assert abs(last.positions[0] - 1.0) < 0.02
