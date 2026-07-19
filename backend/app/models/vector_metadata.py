"""
Vector Metadata MongoDB Document Model
Stores metadata for chunks stored in Pinecone
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime


class VectorMetadata(Document):
    """Vector Metadata document model - maps to Pinecone vectors"""
    file_id: Indexed(str)  # Reference to UploadedFile._id
    subject_id: Indexed(str)  # Reference to Subject._id for faster filtering
    
    # Pinecone vector identifier
    vector_id: Indexed(str, unique=True)  # ID in Pinecone
    
    # Chunk metadata
    chunk_text: str  # Full chunk text (stored in MongoDB for retrieval)
    chunk_index: int
    page_number: Optional[int] = None
    
    # Additional metadata
    chunk_type: str = "text"  # text, table, formula, definition, etc.
    
    # Context (for better retrieval)
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "vector_metadata"
        indexes = [
            "vector_id",
            "file_id",
            "subject_id",
            [("subject_id", 1), ("file_id", 1)],
            [("file_id", 1), ("page_number", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "vector_id": "vec_12345",
                "chunk_text": "Deadlock is a situation where...",
                "chunk_index": 0,
                "page_number": 15,
                "chunk_type": "text"
            }
        }
