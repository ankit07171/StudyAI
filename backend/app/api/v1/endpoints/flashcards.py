"""
Flashcards endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/generate")
async def generate_flashcards(current_user: User = Depends(get_current_active_user)):
    """Generate flashcards - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Flashcards generation endpoint not yet implemented"
    )
