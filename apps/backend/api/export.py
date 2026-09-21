import os
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from auth.dependencies import get_current_user
from core.export_utils import EXPORT_MEDIA, export_filename, render_export
from memory.session_store import redis_store
from models.user import User

router = APIRouter()

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


@router.get("/download/{filename}")
async def download_export(filename: str, current_user: User = Depends(get_current_user)):
    """Legacy: download a locally written debug export (kept for backwards compatibility)."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.startswith(f"{current_user.id}_"):
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    file_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")


@router.get("/{format}")
async def export_session_format(
    format: str,
    session_id: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Export a session's FULL dataset as csv | excel (.xlsx) | json | markdown."""
    fmt = format.lower()
    if fmt not in EXPORT_MEDIA:
        raise HTTPException(status_code=400, detail=f"Unsupported export format '{format}'")

    owner_id = await redis_store.get_session_owner(session_id)
    if not owner_id or owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to export this session data")

    data = await redis_store.get_session_data(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this session")

    if isinstance(data, dict):
        dataset = data.get("cleaned_data") or data.get("extracted_data") or []
    elif isinstance(data, list):
        dataset = data
    else:
        dataset = []
    if not dataset:
        raise HTTPException(status_code=404, detail="This session has no rows to export")

    content = await run_in_threadpool(render_export, fmt, dataset)   # pandas/openpyxl are CPU-bound
    filename = export_filename(fmt)
    return Response(
        content=content,
        media_type=EXPORT_MEDIA[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-store"},
    )
