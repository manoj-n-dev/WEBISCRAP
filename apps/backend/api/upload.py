from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from auth.dependencies import get_current_user
from models.user import User
import os
import shutil
import uuid

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
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
        
        # 2. Add to a session cache if we are uploading to an existing conversation
        # Note: In a real app we'd pass session_id as a query param or form data
        # For MVP we just return the parsed text.
        
        return {
            "status": "success", 
            "message": "File uploaded and parsed successfully.",
            "file_id": file_id,
            "filename": file.filename,
            "extracted_length": len(parsed_text),
            "preview": parsed_text[:500] + "..." if len(parsed_text) > 500 else parsed_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
