"""
Bookmarks endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_bookmarks(current_user: User = Depends(get_current_active_user)):
    """Get all bookmarks - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Bookmarks endpoint not yet implemented"
    )
