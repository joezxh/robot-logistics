"""Floor blueprint data model — 23 zone types covering 6 scenarios."""
from __future__ import annotations
import math
from typing import Literal, Optional
from pydantic import BaseModel, Field, conlist


# v2.2 spec §13.3.2 — Zone types grouped by scenario
ZONE_TYPES = frozenset({
    # E-commerce
    "flow_rack", "high_rack", "mezzanine", "automated", "temp", "temp_bagged", "returns",
    # Manufacturing
    "production_line", "wip_buffer", "parts_storage", "staging",
    # Cold-chain
    "cold_zone", "frozen_zone", "ambient_zone", "loading_bay",
    # Port
    "container_yard", "customs_area",
    # Reverse logistics
    "returns_received", "qc_staging", "reshelving", "disposal",
    # Multi-floor
    "floor_1", "floor_2", "floor_3", "elevator_shaft",
})


class Bounds(BaseModel):
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    h: float = Field(default=0, ge=0)


class TempRange(BaseModel):
    min: float
    max: float


class WallSegment(BaseModel):
    id: str
    x0: float
    z0: float
    x1: float
    z1: float
    h: float = 3.5
    kind: Literal["wall", "glass", "rack", "fence"] = "wall"

    def length(self) -> float:
        return math.hypot(self.x1 - self.x0, self.z1 - self.z0)


class Zone(BaseModel):
    id: str
    ref: str
    type: str  # validated against ZONE_TYPES at use sites
    x: float
    z: float
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    name: Optional[str] = None
    site_node_ids: list[str] = Field(default_factory=list)
    temperature_range: Optional[TempRange] = None
    batch_tracking: bool = False
    hazard_level: Optional[Literal["none", "low", "medium", "high"]] = None
    customs_regulated: bool = False
    current_load_pct: float = Field(default=0.0, ge=0, le=100)


class Facility(BaseModel):
    id: str
    ref: str
    type: str
    x: float
    z: float
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    h: float = Field(default=2.5, gt=0)


class Dock(BaseModel):
    id: str
    ref: str
    x: float
    z: float
    direction: Literal["N", "S", "E", "W"] = "N"
    door_w: float = Field(default=4.0, gt=0)


class Corridor(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    w: float = Field(default=3.0, gt=0)
    bidirectional: bool = True


class Marking(BaseModel):
    id: str
    kind: Literal["lane", "stop", "crossing", "work_zone", "evac"] = "lane"
    points: conlist(conlist(float, min_length=2, max_length=2), min_length=2) = []
    color: str = "#fbbf24"


class Floor(BaseModel):
    id: str
    z: float
    bounds: Bounds
    walls: list[WallSegment] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)
    facilities: list[Facility] = Field(default_factory=list)


class FloorShell(BaseModel):
    bounds: Bounds
    walls: list[WallSegment] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)
    facilities: list[Facility] = Field(default_factory=list)
    docks: list[Dock] = Field(default_factory=list)
    corridors: list[Corridor] = Field(default_factory=list)
    markings: list[Marking] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    floors: list[Floor] = Field(default_factory=list)

    def zones_by_type(self, zone_type: str) -> list[Zone]:
        return [z for z in self.zones if z.type == zone_type]

    def total_zone_area_m2(self) -> float:
        return sum(z.w * z.d for z in self.zones)
