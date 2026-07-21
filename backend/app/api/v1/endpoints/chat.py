"""
Chat endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger
from beanie import PydanticObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.uploaded_file import UploadedFile
from app.models.chat_history import ChatHistory
from app.services.rag.vector_store import vector_store
from app.services.llm.llm_service import llm_service

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """Request model for chat message"""
    subject_id: str
    message: str


@router.post("/message")
async def send_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Send chat message, get AI response, and persist both to history"""
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

        # Save the user's message first
        user_msg = ChatHistory(
            subject_id=request.subject_id,
            user_id=str(current_user.id),
            role="user",
            message=request.message,
        )
        await user_msg.insert()

        # Retrieve relevant content from vector store
        retrieved_docs = vector_store.query(
            query_text=request.message,
            subject_id=request.subject_id,
            top_k=5
        )

        if not retrieved_docs:
            context = "No specific context found in the uploaded materials."
        else:
            context = "\n\n".join([doc['text'] for doc in retrieved_docs])

        system_prompt = """You are an AI study assistant helping students understand their study materials.
Use the provided context from PDFs to answer questions accurately.
If the context doesn't contain the answer, say so clearly but still try to help based on your general knowledge.
Be concise, clear, and helpful."""

        user_prompt = f"""Context from study materials:
{context}

Question: {request.message}

Provide a helpful answer based on the context above."""

        logger.info(f"Generating chat response for subject {request.subject_id}")
        response_text = llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024
        )

        # Save the assistant's response
        assistant_msg = ChatHistory(
            subject_id=request.subject_id,
            user_id=str(current_user.id),
            role="assistant",
            message=response_text,
            context_used=retrieved_docs if retrieved_docs else None,
        )
        await assistant_msg.insert()

        return {
            "id": str(assistant_msg.id),
            "role": "assistant",
            "message": response_text,
            "created_at": assistant_msg.created_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/subject/{subject_id}")
async def get_chat_history(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get chat history for a subject, ordered oldest to newest"""
    try:
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

        messages = await ChatHistory.find(
            ChatHistory.subject_id == subject_id,
            ChatHistory.user_id == str(current_user.id)
        ).sort("+created_at").to_list()

        return [
            {
                "id": str(m.id),
                "role": m.role,
                "message": m.message,
                "created_at": m.created_at,
            }
            for m in messages
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )