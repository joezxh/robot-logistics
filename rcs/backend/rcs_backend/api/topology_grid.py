"""REST endpoints for site_grid (AGV nav cells)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from rcs_backend.models.site_grid import SiteGrid

router = APIRouter()

_store: dict[str, SiteGrid] = {}


def _grid_capacity(grid: SiteGrid) -> tuple[int, int]:
    cols = max(1, int(grid.bounds.w / grid.resolution))
    rows = max(1, int(grid.bounds.d / grid.resolution))
    return cols, rows


@router.get("/grid/{site_id}", response_model=SiteGrid)
async def get_grid(site_id: str) -> SiteGrid:
    g = _store.get(site_id)
    if g is None:
        raise HTTPException(status_code=404, detail=f"grid '{site_id}' not found")
    return g


@router.put("/grid/{site_id}")
async def put_grid(site_id: str, grid: SiteGrid) -> dict:
    cols, rows = _grid_capacity(grid)
    cell_count = sum(len(row) for row in grid.cells)
    capacity = cols * rows
    if cell_count > capacity:
        raise HTTPException(
            status_code=422,
            detail=f"cells ({cell_count}) exceed grid capacity ({capacity})",
        )
    _store[site_id] = grid
    return {"site_id": site_id, "ok": True, "cell_count": cell_count}
