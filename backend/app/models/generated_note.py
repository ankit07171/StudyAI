"""
Generated Note MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class NoteType(str, Enum):
    """Note type enumeration"""
    COMPLETE = "complete"
    CHAPTER = "chapter"
    SUMMARY = "summary"
    FORMULA_SHEET = "formula_sheet"
    KEYWORD = "keyword"


class GeneratedNote(Document):
    """Generated Note document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Note details
    title: str
    note_type: NoteType = NoteType.COMPLETE
    content: str  # Markdown formatted content
    
    # Metadata
    chapter_name: Optional[str] = None
    source_files: Optional[List[str]] = None  # List of UploadedFile._id
    source_vector_ids: Optional[List[str]] = None  # Pinecone vector IDs used
    
    # Export tracking
    exported_pdf: Optional[str] = None
    exported_docx: Optional[str] = None
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "generated_notes"
        indexes = [
            "subject_id",
            "user_id",
            [("subject_id", 1), ("note_type", 1)],
            [("user_id", 1), ("subject_id", 1)],
        ]
