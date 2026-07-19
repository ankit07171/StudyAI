"""
User management endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information"""
    try:
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
        
        if user_update.email is not None:
            # Check if email is already taken
            existing = await User.find_one(
                User.email == user_update.email,
                User.id != current_user.id
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            current_user.email = user_update.email
        
        # Save changes
        await current_user.save()
        
        logger.info(f"User updated: {current_user.id}")
        return current_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/me")
async def delete_current_user(current_user: User = Depends(get_current_active_user)):
    """Delete current user account"""
    try:
        await current_user.delete()
        
        logger.info(f"User deleted: {current_user.id}")
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"User deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
