"""
Important Question MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class QuestionCategory(str, Enum):
    """Question category enumeration"""
    THEORY = "theory"
    NUMERICAL = "numerical"
    CASE_STUDY = "case_study"
    APPLICATION = "application"
    HOT = "hot"  # Higher Order Thinking


class ImportantQuestion(Document):
    """Important Question document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Question details
    question_text: str
    marks: str  # "2", "5", "10", or "long"
    category: QuestionCategory = QuestionCategory.THEORY
    difficulty: str  # "easy", "medium", "hard"
    
    # Answer
    model_answer: Optional[str] = None
    
    # Metadata
    topic: Optional[str] = None
    chapter: Optional[str] = None
    reference_pages: Optional[str] = None  # Comma-separated page numbers
    reference_files: Optional[str] = None  # Comma-separated file names
    source_vector_id: Optional[str] = None  # Pinecone vector ID
    
    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "important_questions"
        indexes = [
            "subject_id",
            "user_id",
            [("subject_id", 1), ("marks", 1)],
            [("subject_id", 1), ("difficulty", 1)],
        ]
