"""
Search endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/")
async def search(current_user: User = Depends(get_current_active_user)):
    """Search across subjects - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Search endpoint not yet implemented"
    )
