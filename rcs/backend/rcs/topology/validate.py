"""Validate FloorShell blueprints."""
from __future__ import annotations
from pydantic import BaseModel
from rcs.models.floor_shell import FloorShell, ZONE_TYPES


class ValidationError(ValueError):
    """Raised when a shell fails hard validation (e.g. duplicate IDs)."""


class ValidationReport(BaseModel):
    errors: list[str] = []
    warnings: list[str] = []
    ok: bool = True


def validate_shell(shell: FloorShell, max_bounds_m: float = 500.0) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Bounds check
    if shell.bounds.w > max_bounds_m or shell.bounds.d > max_bounds_m:
        errors.append(
            f"bounds {shell.bounds.w}x{shell.bounds.d} exceed max {max_bounds_m}m"
        )

    # 2. Duplicate wall IDs
    wall_ids = [w.id for w in shell.walls]
    if len(wall_ids) != len(set(wall_ids)):
        errors.append("duplicate wall IDs detected")

    # 3. Zone geometry
    for z in shell.zones:
        if z.w <= 0 or z.d <= 0:
            errors.append(f"zone {z.id} has zero width/depth")
        if z.x < -0.01 or z.z < -0.01:
            errors.append(f"zone {z.id} has negative origin")
        if z.x + z.w > shell.bounds.w + 0.01 or z.z + z.d > shell.bounds.d + 0.01:
            errors.append(f"zone {z.id} extends outside bounds")

    # 4. Unknown zone type
    for z in shell.zones:
        if z.type not in ZONE_TYPES:
            warnings.append(f"zone {z.id} has unknown type '{z.type}'")

    return ValidationReport(errors=errors, warnings=warnings, ok=len(errors) == 0)
