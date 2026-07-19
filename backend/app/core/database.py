"""
MongoDB Database configuration using Motor and Beanie
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
from loguru import logger

from app.core.config import settings

# Global MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None


async def connect_to_mongodb():
    """Connect to MongoDB"""
    global mongodb_client
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Import all document models
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
        
        # Initialize Beanie with document models
        await init_beanie(
            database=mongodb_client.studyai,
            document_models=[
                User,
                Subject,
                UploadedFile,
                StudySession,
                VectorMetadata,
                ChatHistory,
                GeneratedNote,
                Quiz,
                QuizQuestion,
                QuizAttempt,
                Flashcard,
                RevisionSheet,
                ImportantQuestion,
                Bookmark,
                Notification,
                StudyPlan,
            ]
        )
        
        logger.info("Connected to MongoDB successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("Closed MongoDB connection")


def get_database():
    """Get MongoDB database instance"""
    return mongodb_client.studyai
