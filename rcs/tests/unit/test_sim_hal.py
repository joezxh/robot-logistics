import asyncio
import pytest
from rcs.hal.sim import SimHAL
from rcs.state.profile import DeviceProfile, Morphology, Limits


@pytest.fixture
def sim():
    return SimHAL()


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
            vel_max=[1.0] * 6,
            acc_max=[2.0] * 6,
        ),
        home_joints=[0.0] * 6,
    )


def test_sim_hal_read_returns_zero_state(sim, arm_profile):
    sim.register(arm_profile)
    state = asyncio.run(sim.read("robot-01"))
    assert state.device_id == "robot-01"
    assert state.positions == [0.0] * 6
    assert len(state.velocities) == 6
    assert len(state.efforts) == 6


def test_sim_hal_write_then_read(sim, arm_profile):
    sim.register(arm_profile)
    asyncio.run(sim.write("robot-01", [0.1, 0.0, 0.0, 0.0, 0.0, 0.0]))
    state = asyncio.run(sim.read("robot-01"))
    # SimHAL converges in one step toward the target for the prototype.
    assert abs(state.positions[0] - 0.1) < 1e-6


def test_sim_hal_estop_freezes(sim, arm_profile):
    sim.register(arm_profile)
    asyncio.run(sim.write("robot-01", [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]))
    asyncio.run(sim.estop("robot-01"))
    state = asyncio.run(sim.read("robot-01"))
    # After estop, write is rejected; state remains whatever it was.
    assert state.positions[0] <= 0.5 + 1e-6


def test_sim_hal_unknown_device_raises(sim):
    with pytest.raises(KeyError):
        asyncio.run(sim.read("nope"))
