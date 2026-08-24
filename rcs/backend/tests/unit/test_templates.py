"""6 scenario template factory."""
import pytest
from rcs.topology.templates import (
    list_templates, get_template, SCENARIO_IDS, TemplateBundle, TemplateInfo,
)
from rcs.models.floor_shell import FloorShell
from rcs.models.site_grid import SiteGrid


def test_scenario_ids_count():
    assert len(SCENARIO_IDS) == 6
    assert "ecommerce" in SCENARIO_IDS
    assert "multi_floor" in SCENARIO_IDS


def test_list_templates_returns_six():
    templates = list_templates()
    assert len(templates) == 6
    for t in templates:
        assert isinstance(t, TemplateInfo)
        assert t.scenario_id
        assert t.bounds
        assert t.zone_count >= 1


def test_get_ecommerce_template():
    bundle = get_template("ecommerce")
    assert isinstance(bundle.shell, FloorShell)
    assert isinstance(bundle.grid, SiteGrid)
    assert bundle.shell.bounds.w > 0
    zone_types = {z.type for z in bundle.shell.zones}
    assert "flow_rack" in zone_types or "high_rack" in zone_types


def test_get_cold_chain_template():
    bundle = get_template("cold_chain")
    zone_types = {z.type for z in bundle.shell.zones}
    assert "cold_zone" in zone_types
    assert "frozen_zone" in zone_types


def test_get_port_template():
    bundle = get_template("port")
    zone_types = {z.type for z in bundle.shell.zones}
    assert "container_yard" in zone_types
    assert "customs_area" in zone_types


def test_get_multi_floor_has_floors():
    bundle = get_template("multi_floor")
    assert len(bundle.shell.floors) >= 3


def test_get_unknown_template_raises():
    with pytest.raises(KeyError):
        get_template("not_a_real_scenario")


def test_templates_have_scenario_metadata():
    bundle = get_template("reverse_logistics")
    assert bundle.shell.metadata.get("scenario") == "reverse_logistics"