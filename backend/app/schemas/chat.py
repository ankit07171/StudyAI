"""
Chat Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """Chat message request schema"""
    subject_id: str  # MongoDB ObjectId as string
    message: str


class Citation(BaseModel):
    """Citation schema"""
    file_name: str
    page_number: int
    chunk_text: str


class ChatMessageResponse(BaseModel):
    """Chat message response schema"""
    id: str  # MongoDB ObjectId as string
    role: str
    message: str
    citations: Optional[List[Citation]] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChatHistoryResponse(BaseModel):
    """Chat history response schema"""
    subject_id: str  # MongoDB ObjectId as string
    messages: List[ChatMessageResponse]
    total_messages: int
