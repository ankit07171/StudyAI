"""
Revision sheet endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/generate")
async def generate_revision_sheet(current_user: User = Depends(get_current_active_user)):
    """Generate revision sheet - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Revision sheet generation endpoint not yet implemented"
    )
