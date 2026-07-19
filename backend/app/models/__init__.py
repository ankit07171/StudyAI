"""
Database models package
"""
from app.models.user import User
from app.models.subject import Subject
from app.models.uploaded_file import UploadedFile
from app.models.study_session import StudySession
from app.models.vector_metadata import VectorMetadata
from app.models.chat_history import ChatHistory
from app.models.generated_note import GeneratedNote
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.models.flashcard import Flashcard
from app.models.revision_sheet import RevisionSheet
from app.models.important_question import ImportantQuestion
from app.models.bookmark import Bookmark
from app.models.notification import Notification
from app.models.study_plan import StudyPlan

__all__ = [
    "User",
    "Subject",
    "UploadedFile",
    "StudySession",
    "VectorMetadata",
    "ChatHistory",
    "GeneratedNote",
    "Quiz",
    "QuizQuestion",
    "QuizAttempt",
    "Flashcard",
    "RevisionSheet",
    "ImportantQuestion",
    "Bookmark",
    "Notification",
    "StudyPlan",
]
