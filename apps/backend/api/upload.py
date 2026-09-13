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

def validate_file_magic_bytes(header: bytes, ext: str) -> bool:
    """
    M-01: Verify file content signature against declared extension.
    Rejects disguised executables, scripts, or corrupt files.
    """
    if len(header) == 0:
        return False
        
    # Immediate rejection of binary executable headers (PE/Windows or ELF/Linux)
    if header.startswith(b"MZ") or header.startswith(b"\x7fELF"):
        return False

    if ext == ".pdf":
        return header.startswith(b"%PDF-")
    elif ext == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    elif ext in (".jpg", ".jpeg"):
        return header.startswith(b"\xff\xd8\xff")
    elif ext in (".docx", ".xlsx"):
        # Modern Office files are ZIP archives starting with PK\x03\x04
        return header.startswith(b"PK\x03\x04")
    elif ext == ".xls":
        # Legacy OLE compound document or ZIP
        return header.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1") or header.startswith(b"PK\x03\x04")
    elif ext in (".csv", ".txt", ".md", ".json"):
        # Text files: Ensure it is decodable as text without null bytes
        try:
            sample = header[:512].decode("utf-8")
            if "\x00" in sample:
                return False
            return True
        except UnicodeDecodeError:
            return False
            
    return True

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a file (PDF, DOCX, CSV, Image) for parsing.
    Protected with M-01 magic-byte verification and 20MB file size limit.
    """
    file_id = str(uuid.uuid4())
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    ext = os.path.splitext(file.filename)[1].lower()
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.csv', '.png', '.jpg', '.jpeg', '.xlsx', '.xls'}
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")
        
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # 20MB size limit
    MAX_FILE_SIZE = 20 * 1024 * 1024
    
    try:
        size = 0
        first_chunk = True
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024): # read in 1MB chunks
                if first_chunk:
                    # M-01: Validate file magic bytes on first chunk before writing
                    if not validate_file_magic_bytes(chunk, ext):
                        raise HTTPException(
                            status_code=400,
                            detail=f"File content does not match declared file extension '{ext}'. Upload rejected."
                        )
                    first_chunk = False
                    
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
                buffer.write(chunk)
            
        # 1. Parse the uploaded file
        from parsers.document_parser import extract_text_from_file
        parsed_text = extract_text_from_file(file_path)
        
        # H-06: Delete raw file immediately after parsing — only parsed text is persisted in Redis.
        # Render's filesystem is ephemeral; we must not rely on it for durable storage.
        try:
            os.remove(file_path)
        except OSError:
            pass  # Non-critical: file will be garbage-collected on next restart anyway
        
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

