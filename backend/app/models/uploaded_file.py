"""
Uploaded File MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List
from datetime import datetime


class UploadedFile(Document):
    """Uploaded File document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    
    # File details
    filename: str
    original_filename: str
    file_path: str
    file_size: int  # in bytes
    mime_type: str = "application/pdf"
    
    # PDF metadata
    total_pages: int = 0
    total_words: int = 0
    
    # Processing status
    is_processed: bool = False
    processing_error: Optional[str] = None
    
    # Vector DB metadata - store Pinecone vector IDs
    vector_ids: List[str] = Field(default_factory=list)
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    class Settings:
        name = "uploaded_files"
        indexes = [
            "subject_id",
            "filename",
            [("subject_id", 1), ("uploaded_at", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "os_chapter1_12345.pdf",
                "original_filename": "OS Chapter 1.pdf",
                "file_size": 2048576,
                "total_pages": 45
            }
        }
