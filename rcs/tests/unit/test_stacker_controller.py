import pytest
from rcs.controllers.stacker import StackerController
from rcs.state.profile import DeviceProfile, Morphology, Limits
from rcs.state.joint import JointState
from rcs.state.command import Command, CommandType


@pytest.fixture
def stacker_profile():
    return DeviceProfile(
        device_id="stacker-01",
        morphology=Morphology.STACKER,
        num_joints=2,
        control_hz=50,
        limits=Limits(
            pos_lower=[-5.0, -10.0],
            pos_upper=[5.0, 10.0],
            vel_max=[1.0, 2.0],
            acc_max=[2.0, 4.0],
        ),
        home_joints=[0.0, 0.0],
    )


def test_stacker_reaches_lift_target(stacker_profile):
    ctrl = StackerController(stacker_profile)
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[2.0, 0.0]))
    cur = JointState(positions=[0.0, 0.0], velocities=[0.0, 0.0], efforts=[0.0, 0.0], device_id="stacker-01")
    last = cur
    for _ in range(400):
        last = ctrl.update(cur)
    assert abs(last.positions[0] - 2.0) < 0.05
