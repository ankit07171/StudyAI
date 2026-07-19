"""
Chat History MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatHistory(Document):
    """Chat History document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Message details
    role: str  # "user" or "assistant"
    message: str
    
    # Context and citations (for assistant messages)
    context_used: Optional[List[Dict[str, Any]]] = None  # Retrieved chunks
    citations: Optional[List[Dict[str, Any]]] = None  # Page numbers and file references
    confidence_score: Optional[float] = None
    
    # Retrieved vector IDs (for tracking which chunks were used)
    vector_ids_used: Optional[List[str]] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "chat_history"
        indexes = [
            "subject_id",
            "user_id",
            [("subject_id", 1), ("created_at", -1)],
            [("user_id", 1), ("subject_id", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "message": "Explain deadlock in operating systems",
                "subject_id": "507f1f77bcf86cd799439011"
            }
        }
