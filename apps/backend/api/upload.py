from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from auth.dependencies import get_current_user
from models.user import User
from memory.session_store import redis_store
import os
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file (PDF, DOCX, CSV, Image) for parsing.
    """
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower()
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg'}
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")
        
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # 20MB size limit
    MAX_FILE_SIZE = 20 * 1024 * 1024
    
    try:
        size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024): # read in 1MB chunks
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
                buffer.write(chunk)
            
        # 1. Parse the uploaded file
        from parsers.document_parser import extract_text_from_file
        parsed_text = extract_text_from_file(file_path)
        
        # FIX 13 (M4): Associate uploaded file context with the chat session in Redis
        if session_id:
            await redis_store.save_uploaded_context(session_id, file_id, parsed_text)
        
        return {
            "status": "success", 
            "message": "File uploaded and parsed successfully.",
            "file_id": file_id,
            "filename": file.filename,
            "extracted_length": len(parsed_text),
            "preview": parsed_text[:500] + "..." if len(parsed_text) > 500 else parsed_text
        }
    except HTTPException:
        # M2: Clean up partial file, then re-raise the HTTPException as-is (e.g. 413)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        # Clean up partial file on unexpected errors
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="An error occurred while processing the upload.")

