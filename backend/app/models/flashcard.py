"""
Flashcard MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime


class Flashcard(Document):
    """Flashcard document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Flashcard content
    front: str  # Question
    back: str  # Answer
    
    # Metadata
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    source_vector_id: Optional[str] = None  # Pinecone vector ID
    
    # Spaced repetition
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    review_count: int = 0
    ease_factor: float = 2.5  # For spaced repetition algorithm
    
    # Status
    is_bookmarked: bool = False
    is_mastered: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "flashcards"
        indexes = [
            "subject_id",
            "user_id",
            [("subject_id", 1), ("topic", 1)],
            [("user_id", 1), ("next_review", 1)],
        ]
