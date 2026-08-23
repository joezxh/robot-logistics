"""REST endpoints for DXF export.

Uses ezdxf when available; returns 503 + clear message otherwise.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from rcs_backend.models.floor_shell import FloorShell
from rcs_backend.services.shell_store import MemoryShellStore, default_memory_store

router = APIRouter()

_store = default_memory_store()


def _try_ezdxf():
    try:
        import ezdxf
        return ezdxf
    except ImportError:
        return None


@router.post("/export/dxf", summary="Export FloorShell to DXF (download)")
async def export_shell(shell: FloorShell) -> Response:
    ezdxf = _try_ezdxf()
    if ezdxf is None:
        raise HTTPException(
            status_code=503,
            detail="ezdxf not installed; install via `pip install 'rcs_backend[dxf]'`",
        )
    doc = ezdxf.new()
    msp = doc.modelspace()

    for w in shell.walls:
        msp.add_line(
            (w.x0, w.z0),
            (w.x1, w.z1),
            dxfattribs={"layer": "WALLS"},
        )
    for z in shell.zones:
        msp.add_lwpolyline(
            [(z.x, z.z), (z.x + z.w, z.z), (z.x + z.w, z.z + z.d), (z.x, z.z + z.d)],
            close=True, dxfattribs={"layer": "ZONES"},
        )

    body = doc_to_bytes(doc)
    return Response(
        content=body,
        media_type="application/dxf",
        headers={"Content-Disposition": "attachment; filename=shell.dxf"},
    )


@router.post("/export/dxf/{site_id}", summary="Export saved shell to DXF")
async def export_saved(
    site_id: str,
    store: MemoryShellStore = Depends(lambda: _store),
) -> Response:
    shell = await store.get_shell(site_id)
    if shell is None:
        raise HTTPException(status_code=404, detail=f"site_id '{site_id}' not found")
    return await export_shell(shell)


def doc_to_bytes(doc) -> bytes:
    import io
    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue().encode("utf-8")
