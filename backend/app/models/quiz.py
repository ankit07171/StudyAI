"""
Quiz MongoDB Document Models
"""
from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Question type enumeration"""
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    MATCH_FOLLOWING = "match_following"
    SCENARIO = "scenario"
    NUMERICAL = "numerical"


class DifficultyLevel(str, Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizMode(str, Enum):
    """Quiz mode enumeration"""
    PRACTICE = "practice"
    TIMED = "timed"
    EXAM = "exam"


class QuizQuestion(Document):
    """Quiz Question document model"""
    quiz_id: Indexed(str)  # Reference to Quiz._id
    
    # Question details
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    
    # Options (for MCQ, True/False, Match Following)
    options: Optional[List[str]] = None
    correct_answer: Any  # Can be string, list, or dict depending on question type
    
    # Explanation
    explanation: Optional[str] = None
    
    # Metadata
    marks: int = 1
    topic: Optional[str] = None
    reference_page: Optional[int] = None
    reference_file: Optional[str] = None
    
    # Vector reference (which chunk was used to generate this question)
    source_vector_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "quiz_questions"
        indexes = [
            "quiz_id",
            [("quiz_id", 1), ("question_type", 1)],
        ]


class Quiz(Document):
    """Quiz document model"""
    subject_id: Indexed(str)  # Reference to Subject._id
    user_id: Indexed(str)  # Reference to User._id
    
    # Quiz details
    title: str
    description: Optional[str] = None
    quiz_mode: QuizMode = QuizMode.PRACTICE
    
    # Settings
    time_limit_minutes: Optional[int] = None
    total_marks: int = 0
    passing_marks: int = 0
    
    # Question references (stored separately for flexibility)
    question_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "quizzes"
        indexes = [
            "subject_id",
            "user_id",
            [("subject_id", 1), ("created_at", -1)],
        ]


class QuizAttempt(Document):
    """Quiz Attempt document model"""
    quiz_id: Indexed(str)  # Reference to Quiz._id
    user_id: Indexed(str)  # Reference to User._id
    subject_id: Indexed(str)  # Reference to Subject._id
    
    # Attempt details
    answers: Dict[str, Any]  # {question_id: answer}
    score: float = 0.0
    max_score: int = 0
    percentage: float = 0.0
    
    # Time tracking
    time_taken_seconds: Optional[int] = None
    
    # Analysis
    correct_count: int = 0
    incorrect_count: int = 0
    skipped_count: int = 0
    weak_topics: Optional[List[str]] = None
    
    # Status
    is_completed: bool = False
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Settings:
        name = "quiz_attempts"
        indexes = [
            "quiz_id",
            "user_id",
            "subject_id",
            [("user_id", 1), ("quiz_id", 1)],
            [("user_id", 1), ("completed_at", -1)],
        ]
