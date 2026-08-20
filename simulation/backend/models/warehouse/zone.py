"""Zone and facility models for warehouse floor plan."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


ZoneType = Literal["rack", "flow_rack", "automated", "high_rack", "mezzanine", "temp", "temp_bagged", "returns"]


class Bounds(BaseModel):
    w: float
    d: float


class Wall(BaseModel):
    x0: float
    z0: float
    x1: float
    z1: float
    h: float = 3.0
    dock_bumper: bool = False


class DockPlacement(BaseModel):
    ref: str
    x: float
    z: float
    w: float = 4.0
    d: float = 3.0
    direction: Literal["inbound", "outbound"] = "inbound"


class FacilityPlacement(BaseModel):
    ref: str
    kind: Literal["charger", "sorting", "packing", "qc", "entrance", "returns"]
    x: float
    z: float
    w: float = 2.0
    d: float = 2.0


class Corridor(BaseModel):
    x0: float
    z0: float
    x1: float
    z1: float
    main: bool = False


class Marking(BaseModel):
    type: str
    pts: list[tuple[float, float]]
    width: float = 0.1
    color: int = 0xffffff
    dashed: bool = False


class VehiclePlacement(BaseModel):
    ref: str
    x: float
    z: float
    w: float = 4.0
    d: float = 2.0
    flow: Literal["inbound", "outbound", "internal"] = "internal"
    cargo: list[str] = []


class ShellBlueprint(BaseModel):
    bounds: Bounds
    walls: list[Wall] = []
    docks: list[DockPlacement] = []
    facilities: list[FacilityPlacement] = []
    corridors: list[Corridor] = []
    markings: list[Marking] = []
    vehicles: list[VehiclePlacement] = []


class ZoneCell(BaseModel):
    aisle: int
    row: int
    col: int
    level: int
    qty: int = 0


class ZoneSlot(BaseModel):
    name: str
    occ: int = 0
    items: list[dict] = []


class ZoneBulk(BaseModel):
    name: str
    qty: int = 0


class Zone(BaseModel):
    ref: str
    type: ZoneType
    name: str | None = None
    x: float = 0
    z: float = 0
    w: float = 10
    d: float = 10
    levels: int | None = None
    cells: list[ZoneCell] = []
    slots: list[ZoneSlot] = []
    bulks: list[ZoneBulk] = []
    occ: dict | None = None


class Facility(BaseModel):
    ref: str
    kind: Literal["charger", "sorting", "packing", "qc", "entrance", "returns"]
    name: str | None = None
    x: float = 0
    z: float = 0
    w: float | None = None
    d: float | None = None


class Dock(BaseModel):
    ref: str
    direction: Literal["inbound", "outbound"]
    name: str | None = None
    x: float = 0
    z: float = 0
    w: float | None = None
    d: float | None = None
    slots: list[DockSlot] = []


class DockSlot(BaseModel):
    ref: str
    status: Literal["available", "occupied", "scheduled"] = "available"
