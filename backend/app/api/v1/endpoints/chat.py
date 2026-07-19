"""
Chat endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/")
async def send_message(current_user: User = Depends(get_current_active_user)):
    """Send chat message - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat endpoint not yet implemented"
    )


@router.get("/history/{subject_id}")
async def get_chat_history(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get chat history - To be implemented"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat history endpoint not yet implemented"
    )
