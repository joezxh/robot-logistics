import os

import mujoco

# Assets live at <repo>/simulation/backend/assets/robots/microduck (see
# microduck_cfg._ASSETS_ROOT). test file is at rcs_env/tests/, so go up 3 levels.
MICRODUCK_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "robots", "microduck",
)

VARIANT_XMLS = (
    "robot_walk.xml",
    "robot_groundcontact.xml",
    "robot_allcollisions.xml",
    "robot_groundcontact_rollers.xml",
    "robot_walk_backlash.xml",
    "robot_groundcontact_backlash.xml",
    "robot_groundcontact_rollers_backlash.xml",
)


def test_all_variants_present_and_load():
    for xml in VARIANT_XMLS:
        path = os.path.join(MICRODUCK_DIR, xml)
        assert os.path.exists(path), f"missing MJCF: {path}"
        m = mujoco.MjModel.from_xml_path(path)
        assert m.nu == 14, f"{xml}: expected nu=14, got {m.nu}"


def test_walk_joint_order_matches_policy_order():
    # microduck_cfg is created in Task 3 (P1+P2 backend plan); skip until then.
    try:
        from rcs_env.envs.microduck_cfg import POLICY_JOINTS
    except ModuleNotFoundError:
        import pytest
        pytest.skip("microduck_cfg not yet created (Task 3)")
    m = mujoco.MjModel.from_xml_path(os.path.join(MICRODUCK_DIR, "robot_walk.xml"))
    joints = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
    assert joints[0] == "trunk_base_freejoint"
    assert tuple(joints[1:]) == POLICY_JOINTS
