"""Tests for SimRenderer offscreen camera rendering."""
from __future__ import annotations

import numpy as np
import pytest


def test_sim_renderer_available():
    """Test SimRenderer.available() returns boolean"""
    from rcs_env.renderer import SimRenderer
    result = SimRenderer.available()
    assert isinstance(result, bool)


def test_sim_renderer_returns_dict():
    """Test SimRenderer.render() returns rgb/depth dict when available"""
    from rcs_env.renderer import SimRenderer

    if not SimRenderer.available():
        pytest.skip("MuJoCo not available")

    import mujoco
    model = mujoco.MjModel.from_xml_string("""
    <mujoco model="test">
        <worldbody>
            <body name="test_body" pos="0 0 0.5">
                <geom type="box" size="0.1 0.1 0.1"/>
            </body>
        </worldbody>
    </mujoco>
    """)
    data = mujoco.MjData(model)
    renderer = SimRenderer(model, data, camera_name="default")

    result = renderer.render()

    assert "rgb" in result
    assert "depth" in result
    assert isinstance(result["rgb"], np.ndarray)
    assert result["rgb"].dtype == np.uint8
