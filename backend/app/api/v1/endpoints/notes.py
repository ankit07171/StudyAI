"""
Notes generation endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger
from beanie import PydanticObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.generated_note import GeneratedNote, NoteType
from app.models.uploaded_file import UploadedFile
from app.services.rag.vector_store import vector_store
from app.services.llm.llm_service import llm_service

router = APIRouter()


class NotesGenerateRequest(BaseModel):
    """Request model for notes generation"""
    subject_id: str
    title: str
    note_type: NoteType = NoteType.COMPLETE
    chapter_name: Optional[str] = None


@router.post("/generate")
async def generate_notes(
    request: NotesGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate notes from subject's uploaded PDFs"""
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
        # Use a broad query to get comprehensive content
        query_text = "complete content concepts definitions examples formulas key topics explanations"
        retrieved_docs = vector_store.query(
            query_text=query_text,
            subject_id=request.subject_id,
            top_k=50
        )
        
        if not retrieved_docs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve content from vector store"
            )
        
        # Combine retrieved content
        content = "\n\n".join([doc['text'] for doc in retrieved_docs])
        
        # Build prompt based on note type
        if request.note_type == NoteType.COMPLETE:
            system_prompt = """You are an expert educator who creates comprehensive study notes from study materials.
Generate well-structured notes in Markdown format."""
            user_prompt = f"""Generate comprehensive study notes from the following material.

Content:
{content}

Requirements:
- Use clear headings and subheadings (##, ###)
- Use bullet points for lists
- Include important definitions
- Highlight key formulas
- Provide examples where relevant
- Organize by topics/concepts
- Use Markdown formatting (bold, italic, code blocks for formulas)
- Make it easy to read and study from

Generate complete, well-structured notes."""
        
        elif request.note_type == NoteType.SUMMARY:
            system_prompt = """You are an expert educator who creates concise summaries of study materials.
Generate a summary in Markdown format."""
            user_prompt = f"""Generate a concise summary of the following study material.

Content:
{content}

Requirements:
- Focus on key concepts and main points
- Keep it brief but comprehensive
- Use bullet points
- Highlight important terms
- Make it suitable for quick revision

Generate a well-structured summary."""
        
        elif request.note_type == NoteType.FORMULA_SHEET:
            system_prompt = """You are an expert educator who creates formula sheets from study materials.
Generate a formula sheet in Markdown format."""
            user_prompt = f"""Extract all formulas, equations, and mathematical expressions from the following material.

Content:
{content}

Requirements:
- List all formulas clearly
- Include variable definitions
- Group by topic/chapter
- Use LaTeX or code blocks for formulas
- Add brief explanations where needed

Generate a comprehensive formula sheet."""
        
        elif request.note_type == NoteType.KEYWORD:
            system_prompt = """You are an expert educator who creates keyword/key concept sheets from study materials.
Generate a keyword sheet in Markdown format."""
            user_prompt = f"""Extract all important keywords, terms, and concepts from the following material.

Content:
{content}

Requirements:
- List important terms and their definitions
- Highlight key concepts
- Include acronyms and their meanings
- Group by topic
- Make it suitable for quick reference

Generate a comprehensive keyword sheet."""
        
        else:
            system_prompt = """You are an expert educator who creates study notes from study materials.
Generate notes in Markdown format."""
            user_prompt = f"""Generate study notes from the following material.

Content:
{content}

Generate well-structured notes in Markdown format."""
        
        # Generate notes using LLM
        logger.info(f"Generating {request.note_type.value} notes for subject {request.subject_id}")
        response = llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=4096
        )
        
        # Create note record
        note = GeneratedNote(
            subject_id=request.subject_id,
            user_id=str(current_user.id),
            title=request.title,
            note_type=request.note_type,
            content=response,
            chapter_name=request.chapter_name,
            source_files=[str(f.id) for f in processed_files],
            generated_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await note.insert()
        
        logger.info(f"Notes generated: {note.id}")
        
        return {
            "id": str(note.id),
            "title": note.title,
            "note_type": note.note_type,
            "chapter_name": note.chapter_name,
            "generated_at": note.generated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Notes generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate notes"
        )


@router.get("/subject/{subject_id}")
async def get_notes(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all notes for a subject"""
    try:
        # Verify subject belongs to user
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        notes = await GeneratedNote.find(
            GeneratedNote.subject_id == subject_id,
            GeneratedNote.user_id == str(current_user.id)
        ).sort(-GeneratedNote.generated_at).to_list()
        
        notes_response = []
        for note in notes:
            note_dict = note.model_dump()
            note_dict['id'] = str(note.id)
            # Don't send full content in list view
            note_dict['content_preview'] = note.content[:200] + "..." if len(note.content) > 200 else note.content
            note_dict.pop('content', None)
            notes_response.append(note_dict)
        
        return notes_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notes"
        )


@router.get("/{note_id}")
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific note with full content"""
    try:
        note = await GeneratedNote.get(PydanticObjectId(note_id))
        if not note or note.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        note_dict = note.model_dump()
        note_dict['id'] = str(note.id)
        
        return note_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch note"
        )
