"""
Main API router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    subjects,
    upload,
    chat,
    notes,
    quiz,
    flashcards,
    revision,
    questions,
    study_plan,
    search,
    bookmarks,
    notifications,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["Subjects"])
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(notes.router, prefix="/notes", tags=["Notes"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])
api_router.include_router(revision.router, prefix="/revision", tags=["Revision"])
api_router.include_router(questions.router, prefix="/questions", tags=["Important Questions"])
api_router.include_router(study_plan.router, prefix="/study-plan", tags=["Study Plan"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
