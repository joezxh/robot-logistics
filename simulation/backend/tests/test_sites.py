"""Unit tests for the SiteManager."""
from __future__ import annotations

import pytest

from backend.algorithm.simulator.site_manager import SiteManager, Site


def test_seeds_default_sites() -> None:
    mgr = SiteManager()
    sites = mgr.list()
    assert len(sites) >= 5
    assert any(s["kind"] == "dock" for s in sites)
    assert any(s["kind"] == "warehouse" for s in sites)


def test_add_new_site() -> None:
    mgr = SiteManager()
    site = mgr.add({"id": "dock-X", "kind": "dock", "name": "Dock X", "x": 5.0, "z": -2.0})
    assert site.id == "dock-X"
    assert site.position == [5.0, 0.0, -2.0]
    assert "dock-X" in mgr.sites


def test_add_duplicate_raises() -> None:
    mgr = SiteManager()
    mgr.add({"id": "rack-Z", "kind": "warehouse", "name": "Z"})
    with pytest.raises(ValueError):
        mgr.add({"id": "rack-Z", "kind": "warehouse", "name": "Z"})


def test_update_site() -> None:
    mgr = SiteManager()
    site = mgr.update("dock-A", {"status": "blocked", "x": 9.9, "name": "Dock A'"})
    assert site.status == "blocked"
    assert site.position[0] == 9.9
    assert site.name == "Dock A'"


def test_update_unknown_raises() -> None:
    mgr = SiteManager()
    with pytest.raises(KeyError):
        mgr.update("nope", {"name": "X"})


def test_remove_site() -> None:
    mgr = SiteManager()
    site = mgr.remove("dock-A")
    assert site.id == "dock-A"
    assert "dock-A" not in mgr.sites


def test_remove_unknown_raises() -> None:
    mgr = SiteManager()
    with pytest.raises(KeyError):
        mgr.remove("missing")


def test_site_to_dict_shape() -> None:
    mgr = SiteManager()
    d = mgr.list()[0]
    for key in ("id", "kind", "name", "position", "width", "height", "depth", "rotation", "color", "status"):
        assert key in d
