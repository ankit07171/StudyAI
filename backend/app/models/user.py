"""
User MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime


class User(Document):
    """User document model"""
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    
    # Authentication
    is_active: bool = True
    is_verified: bool = False
    google_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Password reset
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "google_id",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "username": "student123",
                "full_name": "John Doe"
            }
        }
