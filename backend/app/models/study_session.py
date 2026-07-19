"""
Study Session MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime


class StudySession(Document):
    """Study Session document model - tracks user study sessions per subject"""
    user_id: Indexed(str)  # Reference to User._id
    subject_id: Indexed(str)  # Reference to Subject._id
    
    # Session details
    session_name: Optional[str] = None
    duration_minutes: int = 0
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "study_sessions"
        indexes = [
            "user_id",
            "subject_id",
            [("user_id", 1), ("subject_id", 1)],
            [("user_id", 1), ("started_at", -1)],
        ]
