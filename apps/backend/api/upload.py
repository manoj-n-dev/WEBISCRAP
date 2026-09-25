import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from loguru import logger

from auth.dependencies import get_current_user
from core.config import settings
from memory.session_store import redis_store
from models.user import User
from parsers.document_parser import DocumentParseError, TABULAR_EXTENSIONS, parse_upload

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".png", ".jpg", ".jpeg", ".xlsx", ".xls"}
_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _looks_like_text(header: bytes) -> bool:
    """Text in ANY common encoding: UTF-8/UTF-16 (BOM) or a legacy 8-bit code page. Binary content has NUL bytes.
    (Never decode a fixed-size slice as UTF-8: a multi-byte character cut in half falsely fails Telugu/Hindi files.)"""
    if header.startswith((b"\xff\xfe", b"\xfe\xff")):
        return True
    return b"\x00" not in header[:4096]


def validate_file_magic_bytes(header: bytes, ext: str) -> bool:
    """M-01: Verify file content signature against the declared extension."""
    if len(header) == 0:
        return False
    if header.startswith(b"MZ") or header.startswith(b"\x7fELF"):
        return False
    if ext == ".pdf":
        return header.startswith(b"%PDF-")
    if ext == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if ext in (".jpg", ".jpeg"):
        return header.startswith(b"\xff\xd8\xff")
    if ext in (".docx", ".xlsx"):
        return header.startswith(b"PK\x03\x04")
    if ext == ".xls":
        # Real BIFF (OLE) or ZIP, or an HTML/XML/CSV/TSV table that a tool saved with an .xls extension.
        return header.startswith(_OLE) or header.startswith(b"PK\x03\x04") or _looks_like_text(header)
    if ext in (".csv", ".txt", ".md", ".json"):
        return _looks_like_text(header)
    return True


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str | None = Query(default=None, max_length=64),
    current_user: User = Depends(get_current_user),
):
    """Upload a file (PDF, DOCX, CSV, XLSX, XLS, image). Parsed off the event loop; tabular files are also stored
    as exact rows so they never need a lossy LLM extraction."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension. Use PDF, DOCX, CSV, XLSX, XLS, PNG or JPG.")

    # N11 — Enforce Content-Length BEFORE buffering the body.
    # If the client declares a size that already exceeds the limit we can reject
    # the request at the header stage without reading a single byte off the wire.
    declared_size = file.size  # set by Starlette from the Content-Length header
    if declared_size is not None and declared_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")

    user_id = str(current_user.id)
    if session_id and not await redis_store.claim_session(session_id, user_id):
        raise HTTPException(status_code=403, detail="Not authorized to upload to this session")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    try:
        size, first = 0, True
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                if first:
                    if not validate_file_magic_bytes(chunk, ext):
                        raise HTTPException(status_code=400, detail=f"File content does not match declared file extension ('{ext}'). Upload rejected.")
                    first = False
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 20MB.")
                buffer.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="The file is empty.")

        try:
            parsed_text, records = await run_in_threadpool(parse_upload, file_path)
        except DocumentParseError as e:
            raise HTTPException(status_code=422, detail=str(e))

        text_for_store = parsed_text[: settings.MAX_UPLOAD_TEXT_CHARS]
        kind = "table" if ext in TABULAR_EXTENSIONS else ("image" if ext in (".png", ".jpg", ".jpeg") else "document")
        if session_id:
            await redis_store.save_uploaded_context(session_id, file_id, text_for_store)
            if records:
                await redis_store.save_uploaded_rows(session_id, file_id, records[: settings.MAX_DATASET_ROWS])
            await redis_store.save_upload_meta(session_id, file_id, {"name": file.filename, "kind": kind, "size": size})
            await redis_store.set_session_title_if_missing(session_id, file.filename)

        return {
            "status": "success",
            "message": "File uploaded and parsed successfully.",
            "file_id": file_id,
            "filename": file.filename,
            "size": size,
            "kind": kind,
            "rows": len(records) if records else None,
            "columns": len(records[0]) if records else None,
            "extracted_length": len(parsed_text),
            "preview": text_for_store[:500] + ("..." if len(text_for_store) > 500 else ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the upload.")
    finally:
        try:      # H-06: the raw file is never kept
            os.remove(file_path)
        except OSError:
            pass
