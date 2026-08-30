"""DXF ASCII parser — pure function, zero dependencies.

Supports entities: LINE, LWPOLYLINE, CIRCLE, TEXT, MTEXT, HATCH.
Parses DXF group codes (code on one line, value on next).
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

_ENTITY_TYPES = {"LINE", "LWPOLYLINE", "CIRCLE", "TEXT", "MTEXT", "HATCH"}


class DxfEntity(BaseModel):
    type: Literal["LINE", "LWPOLYLINE", "CIRCLE", "TEXT", "MTEXT", "HATCH"]
    layer: str = "0"
    vertices: list[list[float]] = Field(default_factory=list)  # [[x,y], ...]
    text: str = ""
    radius: float = 0.0


class DxfDocument(BaseModel):
    entities: list[DxfEntity] = Field(default_factory=list)
    header_units: str = "m"


def parse_dxf(text: str) -> DxfDocument:
    """Parse DXF ASCII text into a DxfDocument.

    Raises ValueError if the input does not start with a valid DXF section.
    """
    if not text or not text.strip().startswith("0"):
        raise ValueError("invalid DXF: missing group codes")

    lines = text.splitlines()
    i = 0
    entities: list[DxfEntity] = []
    header_units = "m"
    in_entities = False
    current: dict | None = None
    pending_vx: float | None = None
    pending_vy: float | None = None
    pending_vertex_codes: set[int] = set()

    while i < len(lines):
        code_str = lines[i].strip()
        if i + 1 >= len(lines):
            break
        value = lines[i + 1].strip()

        if not code_str.isdigit() and code_str[0:1] != "-":
            i += 1
            continue

        try:
            code = int(code_str)
        except ValueError:
            i += 1
            continue

        # Section markers
        if code == 0 and value == "SECTION":
            # peek ahead for ENTITIES
            if i + 3 < len(lines) and lines[i + 2].strip() == "2":
                section_name = lines[i + 3].strip()
                if section_name == "ENTITIES":
                    in_entities = True
                i += 4
                continue
        if code == 0 and value == "ENDSEC":
            in_entities = False
            i += 2
            continue
        if code == 0 and value == "EOF":
            break

        if not in_entities:
            # Capture header units
            if code == 70 and header_units == "m":
                # crude heuristic: 6 = meters
                if value == "6":
                    header_units = "m"
                elif value == "1":
                    header_units = "in"
            i += 2
            continue

        # Entity start
        if code == 0 and value in _ENTITY_TYPES:
            if current is not None:
                entities.append(_finalize_entity(current))
            current = {"type": value, "layer": "0", "vertices": [], "text": "", "radius": 0.0}
            pending_vx = None
            pending_vy = None
            i += 2
            continue

        if current is None:
            i += 2
            continue

        if code == 8:  # layer
            current["layer"] = value
        elif code == 10:  # primary x
            pending_vx = float(value)
        elif code == 20:  # primary y
            pending_vy = float(value)
            if pending_vx is not None:
                current["vertices"].append([pending_vx, pending_vy])
                pending_vx = None
                pending_vy = None
        elif code == 11:  # secondary x (LINE end)
            pending_vx = float(value)
        elif code == 21:  # secondary y (LINE end)
            pending_vy = float(value)
            if pending_vx is not None:
                current["vertices"].append([pending_vx, pending_vy])
                pending_vx = None
                pending_vy = None
        elif code == 40:  # TEXT height or CIRCLE radius
            if current["type"] == "CIRCLE":
                current["radius"] = float(value)
        elif code == 1:  # text content
            current["text"] = value

        i += 2

    if current is not None:
        entities.append(_finalize_entity(current))

    return DxfDocument(entities=entities, header_units=header_units)


def _finalize_entity(raw: dict) -> DxfEntity:
    return DxfEntity(
        type=raw["type"],
        layer=raw["layer"],
        vertices=raw["vertices"],
        text=raw["text"],
        radius=raw["radius"],
    )
