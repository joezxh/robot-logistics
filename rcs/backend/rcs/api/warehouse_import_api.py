"""REST endpoints for importing warehouse_theatre_3d data into RCS backend.

The imported blueprint is persisted as a single ``UnifiedMap`` row — its
FloorShell lives in ``geometry_json`` and the node/edge graph for path planning
lives in ``topology_json``.
"""
from __future__ import annotations

from fastapi import APIRouter

from rcs.services.warehouse_converter import convert_to_floor_shell, convert_to_site_map
from rcs.services.control import control_unified_maps as um

router = APIRouter()

MAP_ID = "warehouse-theatre-3d"
MAP_NAME = "E-Commerce Warehouse (WT3D)"


@router.post("/import/warehouse-theatre", summary="Import warehouse_theatre_3d blueprint")
async def import_warehouse_theatre() -> dict:
    """One-shot import: convert the embedded DEFAULT_SHELL blueprint and persist
    it as a UnifiedMap (geometry = FloorShell, topology = node/edge graph).

    The operation is idempotent — it targets ``map_id = "warehouse-theatre-3d"``.
    Re-running replaces the existing data (geometry/topology are overwritten and
    ``current_version`` is bumped).
    """
    shell_data = convert_to_floor_shell()
    nodes, edges = convert_to_site_map()
    bounds = shell_data.get("bounds", {})

    existing = await um.get(MAP_ID)
    if existing is None:
        created = await um.create(
            map_id=MAP_ID,
            name=MAP_NAME,
            kind="warehouse",
            is_template=False,
            bounds=bounds,
            geometry=shell_data,
            topology={"nodes": nodes, "edges": edges},
        )
        version = created["current_version"]
    else:
        updated = await um.update(
            MAP_ID,
            name=MAP_NAME,
            geometry=shell_data,
            topology={"nodes": nodes, "edges": edges},
        )
        version = updated["current_version"]

    return {
        "ok": True,
        "site_id": MAP_ID,
        "map_id": MAP_ID,
        "map_version": version,
        "zone_count": len(shell_data.get("zones", [])),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "shell": {
            "bounds": bounds,
            "wall_count": len(shell_data.get("walls", [])),
            "zone_count": len(shell_data.get("zones", [])),
            "facility_count": len(shell_data.get("facilities", [])),
            "dock_count": len(shell_data.get("docks", [])),
        },
    }


@router.get("/import/warehouse-theatre/preview",
            summary="Preview converted data without saving")
async def preview_warehouse_theatre() -> dict:
    """Return the converted FloorShell + site-map graph without persisting.

    Useful for front-end validation / preview before committing.
    """
    shell_data = convert_to_floor_shell()
    nodes, edges = convert_to_site_map()
    return {
        "shell": shell_data,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "zone_count": len(shell_data.get("zones", [])),
            "facility_count": len(shell_data.get("facilities", [])),
            "dock_count": len(shell_data.get("docks", [])),
            "wall_count": len(shell_data.get("walls", [])),
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
    }
