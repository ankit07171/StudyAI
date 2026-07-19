"""
Bookmark MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class BookmarkType(str, Enum):
    """Bookmark type enumeration"""
    NOTE = "note"
    QUIZ = "quiz"
    FLASHCARD = "flashcard"
    QUESTION = "question"
    CHAT = "chat"


class Bookmark(Document):
    """Bookmark document model"""
    user_id: Indexed(str)  # Reference to User._id
    
    # Bookmark details
    bookmark_type: BookmarkType
    reference_id: str  # ID of the bookmarked item
    title: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "bookmarks"
        indexes = [
            "user_id",
            [("user_id", 1), ("bookmark_type", 1)],
            [("user_id", 1), ("reference_id", 1)],
        ]
