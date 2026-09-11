import io
import json
import os
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from auth.dependencies import get_current_user
from models.user import User
from memory.session_store import redis_store
from agents.exporter import sanitize_cell_value

router = APIRouter()

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

@router.get("/download/{filename}")
async def download_export(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download an exported file by filename.
    """
    # Simple path traversal protection
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    # Verify ownership based on filename prefix
    if not filename.startswith(f"{current_user.id}_"):
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
        
    file_path = os.path.join(EXPORT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path, 
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/{format}")
async def export_session_format(
    format: str,
    session_id: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """
    Directly export a session's dataset in the requested format (csv, excel, json, markdown).
    """
    format_lower = format.lower()
    if format_lower not in ["csv", "excel", "json", "markdown"]:
        raise HTTPException(status_code=400, detail=f"Unsupported export format '{format}'")

    owner_id = await redis_store.get_session_owner(session_id)
    if not owner_id or owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to export this session data")

    data = await redis_store.get_session_data(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this session")

    if isinstance(data, dict):
        dataset = data.get("cleaned_data") or data.get("extracted_data") or [data]
    elif isinstance(data, list):
        dataset = data
    else:
        dataset = [data]

    df = pd.DataFrame(dataset)
    df = df.map(sanitize_cell_value)

    if format_lower == "csv":
        csv_str = df.to_csv(index=False)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="webiscrap_{session_id}.csv"'}
        )
    elif format_lower == "excel":
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        return Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="webiscrap_{session_id}.xlsx"'}
        )
    elif format_lower == "json":
        json_str = df.to_json(orient="records", indent=2)
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="webiscrap_{session_id}.json"'}
        )
    elif format_lower == "markdown":
        md_str = df.to_markdown(index=False)
        return Response(
            content=md_str,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="webiscrap_{session_id}.md"'}
        )

