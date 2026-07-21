"""
Flashcards endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger
import json
from beanie import PydanticObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.flashcard import Flashcard
from app.models.uploaded_file import UploadedFile
from app.services.rag.vector_store import vector_store
from app.services.llm.llm_service import llm_service

router = APIRouter()


class FlashcardsGenerateRequest(BaseModel):
    """Request model for flashcard generation"""
    subject_id: str
    card_count: int = Field(default=15, ge=1, le=50)
    topic: Optional[str] = None


@router.post("/generate")
async def generate_flashcards(
    request: FlashcardsGenerateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate flashcards from subject's uploaded PDFs"""
    try:
        # Verify subject exists and belongs to user
        subject = await Subject.get(PydanticObjectId(request.subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

        # Check if subject has processed files
        processed_files = await UploadedFile.find(
            UploadedFile.subject_id == request.subject_id,
            UploadedFile.is_processed == True
        ).to_list()

        if not processed_files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No processed PDFs found in this subject. Please upload and wait for processing to complete."
            )

        # Retrieve content from vector store
        query_text = request.topic or "key concepts definitions terms formulas important facts"
        retrieved_docs = vector_store.query(
            query_text=query_text,
            subject_id=request.subject_id,
            top_k=30
        )

        if not retrieved_docs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve content from vector store"
            )

        content = "\n\n".join([doc['text'] for doc in retrieved_docs])

        system_prompt = """You are an expert educator who creates high-quality flashcards from study materials.
Generate flashcards in valid JSON format only, with no additional text."""

        user_prompt = f"""Generate {request.card_count} flashcards from the following study material.

Content:
{content}

Requirements:
- Front: a short, clear question or term
- Back: a concise, accurate answer or definition (2-4 sentences max)
- Assign a difficulty: easy, medium, or hard
- Identify the topic for each card
{f"- Focus specifically on: {request.topic}" if request.topic else ""}

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "front": "Question or term here",
    "back": "Answer or definition here",
    "topic": "Topic name",
    "difficulty": "medium"
  }}
]

Do not include any text outside the JSON array."""

        logger.info(f"Generating flashcards for subject {request.subject_id}")
        response = llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4096
        )

        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            cards_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse flashcards JSON: {e}")
            logger.error(f"Response was: {response[:500]}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse generated flashcards. Please try again."
            )

        created_cards = []
        for c_data in cards_data:
            card = Flashcard(
                subject_id=request.subject_id,
                user_id=str(current_user.id),
                front=c_data.get('front', ''),
                back=c_data.get('back', ''),
                topic=c_data.get('topic'),
                difficulty=c_data.get('difficulty', 'medium'),
                created_at=datetime.utcnow()
            )
            await card.insert()
            created_cards.append(card)

        logger.info(f"Generated {len(created_cards)} flashcards")

        return {
            "count": len(created_cards),
            "cards": [
                {
                    "id": str(c.id),
                    "front": c.front,
                    "topic": c.topic,
                    "difficulty": c.difficulty
                }
                for c in created_cards
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Flashcard generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate flashcards"
        )


@router.get("/subject/{subject_id}")
async def get_flashcards(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all flashcards for a subject"""
    try:
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

        # NOTE: positional args, not `&` — see questions.py bug for why
        cards = await Flashcard.find(
            Flashcard.subject_id == subject_id,
            Flashcard.user_id == str(current_user.id)
        ).sort(-Flashcard.created_at).to_list()

        cards_response = []
        for c in cards:
            c_dict = c.model_dump()
            c_dict['id'] = str(c.id)
            cards_response.append(c_dict)

        return cards_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching flashcards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch flashcards"
        )


@router.patch("/{card_id}/review")
async def review_flashcard(
    card_id: str,
    remembered: bool,
    current_user: User = Depends(get_current_active_user)
):
    """Mark a flashcard as reviewed, updating spaced-repetition metadata"""
    try:
        card = await Flashcard.get(PydanticObjectId(card_id))
        if not card or card.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

        card.review_count += 1
        card.last_reviewed = datetime.utcnow()
        card.ease_factor = max(1.3, card.ease_factor + (0.1 if remembered else -0.2))
        card.is_mastered = remembered and card.review_count >= 3
        await card.save()

        return {"id": str(card.id), "review_count": card.review_count, "is_mastered": card.is_mastered}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing flashcard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update flashcard"
        )


@router.delete("/{card_id}")
async def delete_flashcard(
    card_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a flashcard"""
    try:
        card = await Flashcard.get(PydanticObjectId(card_id))
        if not card or card.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

        await card.delete()
        return {"deleted": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting flashcard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete flashcard"
        )