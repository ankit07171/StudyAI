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
    """Send chat message and get AI response"""
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
        
        # Retrieve relevant content from vector store
        retrieved_docs = vector_store.query(
            query_text=request.message,
            subject_id=int(request.subject_id),
            top_k=5
        )
        
        if not retrieved_docs:
            # If no relevant docs found, still try to answer with general knowledge
            context = "No specific context found in the uploaded materials."
        else:
            context = "\n\n".join([doc['text'] for doc in retrieved_docs])
        
        # Build prompt
        system_prompt = """You are an AI study assistant helping students understand their study materials.
Use the provided context from PDFs to answer questions accurately.
If the context doesn't contain the answer, say so clearly but still try to help based on your general knowledge.
Be concise, clear, and helpful."""

        user_prompt = f"""Context from study materials:
{context}

Question: {request.message}

Provide a helpful answer based on the context above."""
        
        # Generate response using LLM
        logger.info(f"Generating chat response for subject {request.subject_id}")
        response = llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024
        )
        
        return {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow()
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
    """Get chat history for a subject (placeholder - returns empty list for now)"""
    try:
        # Verify subject belongs to user
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        # For now, return empty history
        # In a full implementation, this would fetch from a ChatMessage collection
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )
