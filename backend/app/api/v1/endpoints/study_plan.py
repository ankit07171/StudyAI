"""
Study plan endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/create")
async def create_study_plan(current_user: User = Depends(get_current_active_user)):
    """Create study plan - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Study plan creation endpoint not yet implemented"
    )
