"""
PDF Upload endpoints - MongoDB/Beanie version
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from loguru import logger

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.uploaded_file import UploadedFile

router = APIRouter()

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB, matches the frontend copy


@router.post("/")
async def upload_pdf(
    subject_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a PDF file to a subject"""

    # Validate the subject exists and belongs to this user
    from beanie import PydanticObjectId
    try:
        subject = await Subject.get(PydanticObjectId(subject_id))
    except Exception:
        subject = None

    if not subject or subject.user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    # Validate file type
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    # Read into memory once so we can check size and write it
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds 50MB limit")

    # Build a unique on-disk filename, keep the original name for display
    subject_dir = UPLOAD_DIR / subject_id
    subject_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = subject_dir / unique_name

    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to write uploaded file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save file")

    # Try to get page count (optional, don't fail the upload if this breaks)
    total_pages = 0
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        total_pages = len(reader.pages)
    except Exception as e:
        logger.warning(f"Could not read PDF page count: {e}")

    try:
        uploaded_file = UploadedFile(
            subject_id=subject_id,
            filename=unique_name,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(contents),
            mime_type=file.content_type or "application/pdf",
            total_pages=total_pages,
        )
        await uploaded_file.insert()

        # Keep subject stats in sync
        subject.total_pdfs = (subject.total_pdfs or 0) + 1
        subject.total_pages = (subject.total_pages or 0) + total_pages
        await subject.save()

        logger.info(f"File uploaded: {file.filename} -> subject {subject_id}")

        return {
            "id": str(uploaded_file.id),
            "filename": uploaded_file.original_filename,
            "file_size": uploaded_file.file_size,
            "total_pages": uploaded_file.total_pages,
            "uploaded_at": uploaded_file.uploaded_at,
        }

    except Exception as e:
        # Roll back the file on disk if the DB write failed
        if file_path.exists():
            os.remove(file_path)
        logger.error(f"Upload DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save file record")