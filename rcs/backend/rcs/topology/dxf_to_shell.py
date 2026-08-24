"""Convert parsed DXF document into FloorShell model.

When the DXF document has no FLOOR layer entities, we build `bounds` via
`Bounds.model_construct(w=0.0, d=0.0)` to bypass the model's `gt=0`
constraint — an empty shell legitimately carries zero bounds. The strict
`Bounds(w, d)` constructor is used as soon as a FLOOR LWPOLYLINE provides
real values.
"""
from __future__ import annotations
import uuid
from rcs.topology.dxf_parser import DxfDocument, DxfEntity
from rcs.models.floor_shell import (
    FloorShell, WallSegment, Zone, Facility, Bounds,
)


def dxf_to_shell(doc: DxfDocument) -> FloorShell:
    """Group DXF entities by layer to produce a FloorShell."""
    walls: list[WallSegment] = []
    zones: list[Zone] = []
    facilities: list[Facility] = []
    text_refs: dict[tuple[float, float], str] = {}

    # First pass: collect TEXT entities for zone references. Key by exact
    # position AND by position rounded to 1 decimal so the zone-match step
    # (which uses zone center to 1 decimal) finds the nearest label.
    for e in doc.entities:
        if e.type in ("TEXT", "MTEXT") and e.vertices:
            x, y = e.vertices[0][0], e.vertices[0][1]
            text_refs[(x, y)] = e.text.strip()
            text_refs[(round(x, 1), round(y, 1))] = e.text.strip()

    floor_bounds_found = False
    bounds = Bounds.model_construct(w=0.0, d=0.0)

    for e in doc.entities:
        layer = e.layer.upper()
        if layer == "FLOOR" and e.type == "LWPOLYLINE":
            xs = [v[0] for v in e.vertices]
            zs = [v[1] for v in e.vertices]
            bounds = Bounds(w=max(xs) - min(xs), d=max(zs) - min(zs))
            floor_bounds_found = True
        elif layer == "WALLS" and e.type in ("LINE", "LWPOLYLINE"):
            if e.type == "LINE" and len(e.vertices) == 2:
                walls.append(WallSegment(
                    id=f"w-{uuid.uuid4().hex[:8]}",
                    x0=e.vertices[0][0], z0=e.vertices[0][1],
                    x1=e.vertices[1][0], z1=e.vertices[1][1],
                ))
            elif e.type == "LWPOLYLINE":
                for i in range(len(e.vertices) - 1):
                    walls.append(WallSegment(
                        id=f"w-{uuid.uuid4().hex[:8]}",
                        x0=e.vertices[i][0], z0=e.vertices[i][1],
                        x1=e.vertices[i + 1][0], z1=e.vertices[i + 1][1],
                    ))
        elif layer == "ZONES" and e.type == "LWPOLYLINE":
            xs = [v[0] for v in e.vertices]
            zs = [v[1] for v in e.vertices]
            x_min, x_max = min(xs), max(xs)
            z_min, z_max = min(zs), max(zs)
            cx, cz = (x_min + x_max) / 2, (z_min + z_max) / 2
            ref = (
                text_refs.get((cx, cz))
                or text_refs.get((round(cx, 1), round(cz, 1)))
                or f"Z-{uuid.uuid4().hex[:4]}"
            )
            zones.append(Zone(
                id=f"z-{uuid.uuid4().hex[:8]}",
                ref=ref, type="staging",
                x=x_min, z=z_min,
                w=x_max - x_min, d=z_max - z_min,
            ))
        elif layer == "FACILITIES" and e.type == "CIRCLE":
            cx, cz = e.vertices[0]
            facilities.append(Facility(
                id=f"f-{uuid.uuid4().hex[:8]}",
                ref=f"F-{uuid.uuid4().hex[:4]}",
                type="generic",
                x=cx - e.radius, z=cz - e.radius,
                w=2 * e.radius, d=2 * e.radius,
            ))

    shell_kwargs: dict = dict(
        walls=walls, zones=zones, facilities=facilities,
        metadata={"source": "dxf", "entity_count": len(doc.entities)},
    )
    if not floor_bounds_found:
        shell_kwargs["bounds"] = Bounds.model_construct(w=0.0, d=0.0)
    else:
        shell_kwargs["bounds"] = bounds
    return FloorShell(**shell_kwargs)