"""
Study Plan MongoDB Document Model
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StudyPlan(Document):
    """Study Plan document model - Personalized study planner"""
    user_id: Indexed(str)  # Reference to User._id
    subject_id: Indexed(str)  # Reference to Subject._id
    
    # Plan details
    title: str
    exam_date: datetime
    daily_study_hours: int
    total_days: int
    
    # Schedule (list of daily plans)
    schedule: List[Dict[str, Any]]
    # Example: [
    #   {"day": 1, "date": "2024-01-01", "topics": ["Chapter 1"], "duration": 2, "tasks": ["Read", "Practice"]},
    # ]
    
    # Progress tracking
    completed_days: int = 0
    completion_percentage: int = 0
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "study_plans"
        indexes = [
            "user_id",
            "subject_id",
            [("user_id", 1), ("subject_id", 1)],
            [("user_id", 1), ("is_active", 1)],
        ]
