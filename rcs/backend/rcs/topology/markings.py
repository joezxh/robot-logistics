"""Generate floor markings (lanes, stop lines) from FloorShell."""
from __future__ import annotations
import uuid
from rcs.models.floor_shell import FloorShell, Marking


def generate_markings(shell: FloorShell, lane_w: float = 1.0) -> list[Marking]:
    out: list[Marking] = []

    zone_map = {z.id: z for z in shell.zones}
    for c in shell.corridors:
        if c.from_zone not in zone_map or c.to_zone not in zone_map:
            continue
        a, b = zone_map[c.from_zone], zone_map[c.to_zone]
        ax = a.x + a.w / 2
        az = a.z + a.d / 2
        bx = b.x + b.w / 2
        bz = b.z + b.d / 2
        out.append(Marking(
            id=f"m-lane-{uuid.uuid4().hex[:6]}",
            kind="lane",
            points=[[ax, az], [bx, bz]],
            color="#fbbf24",
        ))
        if c.bidirectional:
            out.append(Marking(
                id=f"m-lane-{uuid.uuid4().hex[:6]}",
                kind="lane",
                points=[[bx, bz], [ax, az]],
                color="#fbbf24",
            ))

    for d in shell.docks:
        out.append(Marking(
            id=f"m-stop-{uuid.uuid4().hex[:6]}",
            kind="stop",
            points=[[d.x - 1.5, d.z], [d.x + 1.5, d.z]],
            color="#ef4444",
        ))

    return out
