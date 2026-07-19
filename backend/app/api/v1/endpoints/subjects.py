"""
Subject management endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from loguru import logger
from beanie import PydanticObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.generated_note import GeneratedNote
from app.models.quiz import Quiz
from app.models.flashcard import Flashcard
from app.models.chat_history import ChatHistory
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse,
    SubjectWithStats
)

router = APIRouter()


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subject"""
    try:
        new_subject = Subject(
            user_id=str(current_user.id),
            name=subject_data.name,
            code=subject_data.code,
            semester=subject_data.semester,
            description=subject_data.description,
            total_pdfs=0,
            total_pages=0,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow()
        )
        
        await new_subject.insert()
        
        logger.info(f"Subject created: {new_subject.name} for user {current_user.id}")
        
        # Convert to dict and ensure IDs are strings
        subject_dict = new_subject.model_dump()
        subject_dict['id'] = str(new_subject.id)
        subject_dict['user_id'] = str(new_subject.user_id)
        
        return SubjectResponse(**subject_dict)
        
    except Exception as e:
        logger.error(f"Subject creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subject"
        )


@router.get("/", response_model=List[SubjectWithStats])
async def get_subjects(current_user: User = Depends(get_current_active_user)):
    """Get all subjects for current user"""
    try:
        subjects = await Subject.find(
            Subject.user_id == str(current_user.id)
        ).sort(-Subject.last_accessed).to_list()
        
        # Add statistics for each subject
        subjects_with_stats = []
        for subject in subjects:
            subject_dict = subject.model_dump()
            
            # Convert ObjectIds to strings
            subject_dict['id'] = str(subject.id)
            subject_dict['user_id'] = str(subject.user_id)
            
            # Count related documents
            notes_count = await GeneratedNote.find(
                GeneratedNote.subject_id == str(subject.id)
            ).count()
            
            quizzes_count = await Quiz.find(
                Quiz.subject_id == str(subject.id)
            ).count()
            
            flashcards_count = await Flashcard.find(
                Flashcard.subject_id == str(subject.id)
            ).count()
            
            chat_messages_count = await ChatHistory.find(
                ChatHistory.subject_id == str(subject.id)
            ).count()
            
            # Add stats
            subject_dict.update({
                'notes_count': notes_count,
                'quizzes_count': quizzes_count,
                'flashcards_count': flashcards_count,
                'chat_messages_count': chat_messages_count
            })
            
            subjects_with_stats.append(SubjectWithStats(**subject_dict))
        
        return subjects_with_stats
        
    except Exception as e:
        logger.error(f"Get subjects error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subjects"
        )


@router.get("/{subject_id}", response_model=SubjectWithStats)
async def get_subject(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific subject"""
    try:
        subject = await Subject.find_one(
            Subject.id == PydanticObjectId(subject_id),
            Subject.user_id == str(current_user.id)
        )
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Update last accessed
        subject.last_accessed = datetime.utcnow()
        await subject.save()
        
        # Add statistics
        subject_dict = subject.model_dump()
        
        # Convert ObjectIds to strings
        subject_dict['id'] = str(subject.id)
        subject_dict['user_id'] = str(subject.user_id)
        
        notes_count = await GeneratedNote.find(
            GeneratedNote.subject_id == str(subject.id)
        ).count()
        
        quizzes_count = await Quiz.find(
            Quiz.subject_id == str(subject.id)
        ).count()
        
        flashcards_count = await Flashcard.find(
            Flashcard.subject_id == str(subject.id)
        ).count()
        
        chat_messages_count = await ChatHistory.find(
            ChatHistory.subject_id == str(subject.id)
        ).count()
        
        subject_dict.update({
            'notes_count': notes_count,
            'quizzes_count': quizzes_count,
            'flashcards_count': flashcards_count,
            'chat_messages_count': chat_messages_count
        })
        
        return SubjectWithStats(**subject_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get subject error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subject"
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    subject_update: SubjectUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a subject"""
    try:
        subject = await Subject.find_one(
            Subject.id == subject_id,
            Subject.user_id == str(current_user.id)
        )
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Update fields
        if subject_update.name is not None:
            subject.name = subject_update.name
        if subject_update.code is not None:
            subject.code = subject_update.code
        if subject_update.semester is not None:
            subject.semester = subject_update.semester
        if subject_update.description is not None:
            subject.description = subject_update.description
        
        subject.updated_at = datetime.utcnow()
        await subject.save()
        
        logger.info(f"Subject updated: {subject_id}")
        
        # Convert to dict and ensure IDs are strings
        subject_dict = subject.model_dump()
        subject_dict['id'] = str(subject.id)
        subject_dict['user_id'] = str(subject.user_id)
        
        return SubjectResponse(**subject_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subject update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subject"
        )


@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a subject and all associated data"""
    try:
        subject = await Subject.find_one(
            Subject.id == subject_id,
            Subject.user_id == str(current_user.id)
        )
        
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Delete associated vectors from Pinecone
        from app.services.rag.vector_store import vector_store
        vector_store.delete_by_subject(subject_id)
        
        # Delete subject (will cascade delete related docs)
        await subject.delete()
        
        logger.info(f"Subject deleted: {subject_id}")
        return {"message": "Subject deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subject deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subject"
        )
