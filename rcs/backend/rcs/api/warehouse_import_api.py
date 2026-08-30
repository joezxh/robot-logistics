"""REST endpoints for importing warehouse_theatre_3d data into RCS backend."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from rcs.services.warehouse_converter import convert_to_floor_shell, convert_to_site_map
from rcs.db import models, session as db_session

router = APIRouter()


@router.post("/import/warehouse-theatre", summary="Import warehouse_theatre_3d blueprint")
async def import_warehouse_theatre() -> dict:
    """One-shot import: convert the embedded DEFAULT_SHELL blueprint and
    persist it as both a TopologyShell (3-D visualisation) and a SiteMap
    (node/edge graph for path planning).

    The operation is idempotent — it uses ``site_id = "warehouse-theatre-3d"``
    and ``map_name = "warehouse-theatre-3d"``.  Re-running replaces the
    existing data (shell data is overwritten; site map nodes/edges are
    updated and a new version snapshot is created).
    """
    shell_data = convert_to_floor_shell()
    nodes, edges = convert_to_site_map()

    site_id = "warehouse-theatre-3d"
    map_name = "E-Commerce Warehouse (WT3D)"

    async for s in db_session.session():
        # ── 1. Save / update TopologyShell ────────────────────────────────
        shell_row = await s.get(models.TopologyShell, site_id)
        if shell_row is None:
            shell_row = models.TopologyShell(site_id=site_id)
        shell_row.name = map_name
        shell_row.width_m = shell_data["bounds"]["w"]
        shell_row.depth_m = shell_data["bounds"]["d"]
        shell_row.height_m = shell_data["bounds"].get("h", 0)
        shell_row.data = shell_data
        s.add(shell_row)

        # ── 2. Save / update SiteMap ──────────────────────────────────────
        result = await s.execute(
            select(models.SiteMap).where(models.SiteMap.name == map_name)
        )
        map_row = result.scalar_one_or_none()
        if map_row is None:
            map_row = models.SiteMap(
                name=map_name,
                nodes_json=nodes,
                edges_json=edges,
                current_version=1,
            )
            s.add(map_row)
            await s.flush()
            # initial version snapshot
            s.add(models.SiteMapVersion(
                map_id=map_row.map_id, version=1,
                nodes_json=nodes, edges_json=edges,
                note="import from warehouse_theatre_3d",
            ))
        else:
            map_row.nodes_json = nodes
            map_row.edges_json = edges
            map_row.current_version += 1
            s.add(map_row)
            s.add(models.SiteMapVersion(
                map_id=map_row.map_id, version=map_row.current_version,
                nodes_json=nodes, edges_json=edges,
                note=f"re-import v{map_row.current_version}",
            ))

        # ── 3. Save / update TopologyGrid (zone records) ──────────────────
        # Remove old grid rows for this site, then insert fresh ones.
        from sqlalchemy import delete as sql_delete
        await s.execute(
            sql_delete(models.TopologyGrid)
            .where(models.TopologyGrid.site_id == site_id)
        )
        for z in shell_data.get("zones", []):
            grid_row = models.TopologyGrid(
                site_id=site_id,
                zone_id=z["id"],
                zone_type=_zone_type_int(z["type"]),
                center_m=[z["x"] + z["w"] / 2, z["z"] + z["d"] / 2],
                size_m=[z["w"], z["d"]],
                rotation_deg=0.0,
                data={"ref": z["ref"], "type": z["type"]},
            )
            s.add(grid_row)

        await s.commit()

        # Refresh to get generated IDs
        await s.refresh(shell_row)
        await s.refresh(map_row)

        return {
            "ok": True,
            "site_id": site_id,
            "map_id": map_row.map_id,
            "map_version": map_row.current_version,
            "zone_count": len(shell_data.get("zones", [])),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "shell": {
                "bounds": shell_data["bounds"],
                "wall_count": len(shell_data.get("walls", [])),
                "zone_count": len(shell_data.get("zones", [])),
                "facility_count": len(shell_data.get("facilities", [])),
                "dock_count": len(shell_data.get("docks", [])),
            },
        }

    raise RuntimeError("db session closed")


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


# Map zone type string → integer code (matches TopologyGrid.zone_type convention)
_ZONE_TYPE_MAP = {
    "flow_rack": 1, "high_rack": 2, "mezzanine": 3, "automated": 4,
    "temp": 5, "temp_bagged": 6, "returns": 7, "rack": 8,
}


def _zone_type_int(ztype: str) -> int:
    return _ZONE_TYPE_MAP.get(ztype, 0)
