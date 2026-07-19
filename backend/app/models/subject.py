"""
Subject MongoDB Document Model
"""
from beanie import Document, Link, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime

from app.models.user import User


class Subject(Document):
    """Subject document model"""
    user_id: Indexed(str)  # Reference to User._id
    
    name: str
    code: Optional[str] = None
    semester: Optional[str] = None
    description: Optional[str] = None
    
    # Metadata
    total_pdfs: int = 0
    total_pages: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "subjects"
        indexes = [
            "user_id",
            [("user_id", 1), ("name", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Operating System",
                "code": "CS301",
                "semester": "Semester 5",
                "description": "Study materials for Operating System"
            }
        }
