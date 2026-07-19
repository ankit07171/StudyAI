"""
Revision Sheet MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class RevisionSheet(Document):
    """Revision Sheet document model - One page revision guides"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Content
    title: str
    content: str  # Full markdown formatted content
    
    # Sections (structured data)
    formulas: Optional[str] = None
    definitions: Optional[str] = None
    keywords: Optional[str] = None
    memory_tricks: Optional[str] = None
    diagrams: Optional[str] = None  # Mermaid diagrams
    exam_tips: Optional[str] = None
    
    # Source tracking
    source_vector_ids: Optional[List[str]] = None
    
    # Export tracking
    exported_pdf: Optional[str] = None
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "revision_sheets"
        indexes = [
            "subject_id",
            "user_id",
            [("user_id", 1), ("subject_id", 1)],
        ]
