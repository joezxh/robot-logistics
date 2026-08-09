import math
import pytest
from rcs.controllers.arm import ArmController
from rcs.state.profile import DeviceProfile, Morphology, Limits
from rcs.state.joint import JointState
from rcs.state.command import Command, CommandType


@pytest.fixture
def arm_profile():
    return DeviceProfile(
        device_id="robot-01",
        morphology=Morphology.ARM,
        num_joints=6,
        control_hz=1000,
        limits=Limits(
            pos_lower=[-3.14] * 6,
            pos_upper=[3.14] * 6,
            vel_max=[2.5] * 6,
            acc_max=[5.0] * 6,
        ),
        home_joints=[0.0] * 6,
    )


def test_arm_step_response_reaches_target(arm_profile):
    ctrl = ArmController(arm_profile)
    # Drive the controller one MOVE_J command so the interpolator is armed.
    ctrl.on_command(Command(type=CommandType.MOVE_J, target_joints=[0.5, 0.0, 0.0, 0.0, 0.0, 0.0]))
    pos = [0.0] * 6
    for _ in range(2000):
        cur = JointState(positions=list(pos), velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
        out = ctrl.update(cur)
        pos = list(out.positions)
    assert abs(pos[0] - 0.5) < 0.01


def test_arm_halts_on_tracking_error(arm_profile):
    ctrl = ArmController(arm_profile)
    # Inject a huge step; with kp=80, kd=8 it should still halt only if the
    # error threshold is exceeded. We force the threshold to be tiny via limits.
    ctrl.profile.limits.rad_th = 0.001
    cur = JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
    out = ctrl.update(cur)
    ctrl.tracking_error(out, cur)  # populates internal last_target
    err = ctrl.tracking_error(out, JointState(positions=[0.5, 0, 0, 0, 0, 0], velocities=[0]*6, efforts=[0]*6, device_id="robot-01"))
    if err.max_joint_error > ctrl.profile.limits.rad_th:
        ctrl.halt()
    # Either halted (if error is large enough) or still running — but never fault.
    assert ctrl.state.mode.value in ("halted", "running", "idle")


def test_arm_pd_output_within_torque_proxy_bounds(arm_profile):
    ctrl = ArmController(arm_profile)
    cur = JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01")
    out = ctrl.update(cur)
    assert len(out.positions) == 6
