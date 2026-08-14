"""In-memory sites (docks + warehouse zones) registry."""
from __future__ import annotations

from typing import Any


class Site:
    """A dock or a warehouse zone."""

    def __init__(
        self,
        site_id: str,
        kind: str,
        name: str,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        width: float = 2.0,
        height: float = 1.5,
        depth: float = 2.0,
        rotation: float = 0.0,
        status: str = "active",
        color: str = "#5eb0ff",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.id = site_id
        self.kind = kind  # dock | warehouse
        self.name = name
        self.position = [x, y, z]
        self.width = width
        self.height = height
        self.depth = depth
        self.rotation = rotation
        self.status = status
        self.color = color
        self.metadata = dict(metadata or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "status": self.status,
            "position": list(self.position),
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
            "rotation": self.rotation,
            "color": self.color,
            "metadata": dict(self.metadata),
        }


class SiteManager:
    """Holds a registry of dock and warehouse sites."""

    def __init__(self, seed: bool = True) -> None:
        self.sites: dict[str, Site] = {}
        if seed:
            self._seed()

    def _seed(self) -> None:
        # Default layout — three docks on the south side, two warehouse racks on the north.
        seed_data = [
            {"id": "dock-A", "kind": "dock", "name": "Dock A", "x": -6.0, "z": 7.0, "color": "#3b82f6"},
            {"id": "dock-B", "kind": "dock", "name": "Dock B", "x": -2.0, "z": 7.0, "color": "#5eb0ff"},
            {"id": "dock-C", "kind": "dock", "name": "Dock C", "x": 2.0, "z": 7.0, "color": "#a855f7"},
            {"id": "dock-D", "kind": "dock", "name": "Dock D", "x": 6.0, "z": 7.0, "color": "#06b6d4"},
            {"id": "rack-1", "kind": "warehouse", "name": "Rack 1", "x": -7.0, "z": -5.0, "color": "#8a98ad"},
            {"id": "rack-2", "kind": "warehouse", "name": "Rack 2", "x": -3.5, "z": -5.0, "color": "#8a98ad"},
            {"id": "rack-3", "kind": "warehouse", "name": "Rack 3", "x": 0.0, "z": -5.0, "color": "#8a98ad"},
            {"id": "rack-4", "kind": "warehouse", "name": "Rack 4", "x": 3.5, "z": -5.0, "color": "#8a98ad"},
            {"id": "rack-5", "kind": "warehouse", "name": "Rack 5", "x": 7.0, "z": -5.0, "color": "#8a98ad"},
        ]
        for s in seed_data:
            self.sites[s["id"]] = Site(
                site_id=s["id"], kind=s["kind"], name=s["name"],
                x=s["x"], z=s["z"], color=s["color"],
                width=2.5, height=2.0 if s["kind"] == "warehouse" else 1.5,
                depth=2.5,
            )

    def list(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.sites.values()]

    def get(self, site_id: str) -> Site:
        return self.sites[site_id]

    def add(self, payload: dict[str, Any]) -> Site:
        site_id = payload["id"]
        if site_id in self.sites:
            raise ValueError(f"site {site_id!r} already exists")
        site = Site(
            site_id=site_id,
            kind=payload["kind"],
            name=payload.get("name", site_id),
            x=float(payload.get("x", 0.0)),
            y=float(payload.get("y", 0.0)),
            z=float(payload.get("z", 0.0)),
            width=float(payload.get("width", 2.5)),
            height=float(payload.get("height", 1.5)),
            depth=float(payload.get("depth", 2.5)),
            rotation=float(payload.get("rotation", 0.0)),
            status=payload.get("status", "active"),
            color=payload.get("color", "#5eb0ff"),
            metadata=payload.get("metadata"),
        )
        self.sites[site_id] = site
        return site

    def update(self, site_id: str, payload: dict[str, Any]) -> Site:
        if site_id not in self.sites:
            raise KeyError(site_id)
        site = self.sites[site_id]
        for key, attr in (("name", "name"), ("status", "status"), ("color", "color")):
            if key in payload:
                setattr(site, attr, payload[key])
        if "x" in payload:
            site.position[0] = float(payload["x"])
        if "y" in payload:
            site.position[1] = float(payload["y"])
        if "z" in payload:
            site.position[2] = float(payload["z"])
        for key in ("width", "height", "depth", "rotation"):
            if key in payload:
                setattr(site, key, float(payload[key]))
        if "metadata" in payload:
            site.metadata = dict(payload["metadata"])
        return site

    def remove(self, site_id: str) -> Site:
        if site_id not in self.sites:
            raise KeyError(site_id)
        return self.sites.pop(site_id)
