"""
PDF Upload endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/")
async def upload_pdf(current_user: User = Depends(get_current_active_user)):
    """Upload PDF file - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF upload endpoint not yet implemented"
    )
