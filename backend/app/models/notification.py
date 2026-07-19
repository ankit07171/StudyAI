"""
Notification MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification type enumeration"""
    NOTES_READY = "notes_ready"
    QUIZ_READY = "quiz_ready"
    UPLOAD_COMPLETE = "upload_complete"
    STUDY_REMINDER = "study_reminder"
    REVISION_REMINDER = "revision_reminder"
    GENERAL = "general"


class Notification(Document):
    """Notification document model"""
    user_id: Indexed(str)  # Reference to User._id
    
    # Notification details
    notification_type: NotificationType
    title: str
    message: str
    
    # Link (optional)
    action_url: Optional[str] = None
    
    # Status
    is_read: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            [("user_id", 1), ("is_read", 1)],
            [("user_id", 1), ("created_at", -1)],
        ]
