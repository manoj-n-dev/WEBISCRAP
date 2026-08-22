from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os
from auth.dependencies import get_current_user
from models.user import User

router = APIRouter()

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")

@router.get("/download/{filename}")
async def download_export(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download an exported file.
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
