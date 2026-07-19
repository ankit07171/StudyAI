"""
Subject Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubjectBase(BaseModel):
    """Base subject schema"""
    name: str
    code: Optional[str] = None
    semester: Optional[str] = None
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    """Subject creation schema"""
    pass


class SubjectUpdate(BaseModel):
    """Subject update schema"""
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[str] = None
    description: Optional[str] = None


class SubjectResponse(SubjectBase):
    """Subject response schema"""
    id: str  # MongoDB ObjectId as string
    user_id: str  # MongoDB ObjectId as string
    total_pdfs: int
    total_pages: int
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SubjectWithStats(SubjectResponse):
    """Subject with statistics"""
    notes_count: int = 0
    quizzes_count: int = 0
    flashcards_count: int = 0
    chat_messages_count: int = 0
