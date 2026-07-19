"""
Authentication endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    PasswordReset,
    PasswordResetConfirm,
    GoogleAuthRequest
)

router = APIRouter()
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await User.find_one(
            {"$or": [
                {"email": user_data.email},
                {"username": user_data.username}
            ]}
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )
        
        # Save to MongoDB
        await new_user.insert()
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(new_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)})
        
        logger.info(f"New user registered: {new_user.email}")
        
        # Convert User to dict and ensure id is string
        user_dict = new_user.model_dump()
        user_dict['id'] = str(new_user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(**user_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user"""
    try:
        # Find user by email
        user = await User.find_one(User.email == user_data.email)
        
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        await user.save()
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        logger.info(f"User logged in: {user.email}")
        
        # Convert User to dict and ensure id is string
        user_dict = user.model_dump()
        user_dict['id'] = str(user.id)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(**user_dict)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/token", response_model=TokenResponse)
async def login_with_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with OAuth2 password form (for API docs)"""
    user = await User.find_one(User.email == form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await user.save()
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert User to dict and ensure id is string
    user_dict = user.model_dump()
    user_dict['id'] = str(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(**user_dict)
    )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        user = await User.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        new_access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/forgot-password")
async def forgot_password(data: PasswordReset):
    """Request password reset"""
    try:
        user = await User.find_one(User.email == data.email)
        
        if not user:
            # Don't reveal if email exists
            return {"message": "If the email exists, a reset link will be sent"}
        
        # Generate reset token (simplified - in production, use secure token and send email)
        reset_token = create_access_token(
            data={"sub": str(user.id), "type": "reset"},
            expires_delta=timedelta(hours=1)
        )
        
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        await user.save()
        
        # TODO: Send email with reset link
        logger.info(f"Password reset requested for: {user.email}")
        
        return {"message": "If the email exists, a reset link will be sent"}
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return {"message": "If the email exists, a reset link will be sent"}


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm):
    """Reset password with token"""
    try:
        payload = decode_token(data.token)
        
        if payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = payload.get("sub")
        user = await User.get(user_id)
        
        if not user or user.reset_token != data.token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        # Update password
        user.hashed_password = get_password_hash(data.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        await user.save()
        
        logger.info(f"Password reset successful for: {user.email}")
        
        return {"message": "Password reset successful"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/google", response_model=TokenResponse)
async def google_auth(data: GoogleAuthRequest):
    """Authenticate with Google OAuth"""
    try:
        # TODO: Implement Google OAuth verification
        # This is a placeholder - implement actual Google token verification
        
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google authentication not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )
