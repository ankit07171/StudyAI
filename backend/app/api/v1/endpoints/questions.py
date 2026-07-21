"""
Important questions endpoints - MongoDB/Beanie version
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from loguru import logger
import json
from beanie import PydanticObjectId

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.subject import Subject
from app.models.important_question import ImportantQuestion, QuestionCategory
from app.models.uploaded_file import UploadedFile
from app.services.rag.vector_store import vector_store
from app.services.llm.llm_service import llm_service

router = APIRouter()


class QuestionsGenerateRequest(BaseModel):
    """Request model for important questions generation"""
    subject_id: str
    question_count: int = Field(default=15, ge=1, le=50)
    marks_filter: Optional[List[str]] = None  # e.g., ["2", "5", "10"]
    difficulty_filter: Optional[List[str]] = None  # e.g., ["easy", "medium", "hard"]
    category_filter: Optional[List[QuestionCategory]] = None


@router.post("/generate")
async def generate_important_questions(
    request: QuestionsGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate important questions from subject's uploaded PDFs"""
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
        # Use a broad query to get diverse content
        query_text = "important questions exam topics concepts numerical problems case studies applications"
        retrieved_docs = vector_store.query(
            query_text=query_text,
            subject_id=request.subject_id,
            top_k=40
        )
        
        if not retrieved_docs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve content from vector store"
            )
        
        # Combine retrieved content
        content = "\n\n".join([doc['text'] for doc in retrieved_docs])
        
        # Build filters for prompt
        marks_str = ", ".join(request.marks_filter) if request.marks_filter else "2, 5, 10, long"
        difficulty_str = ", ".join(request.difficulty_filter) if request.difficulty_filter else "easy, medium, hard"
        categories_str = ", ".join([c.value for c in request.category_filter]) if request.category_filter else "theory, numerical, case_study, application"
        
        system_prompt = """You are an expert educator who identifies and creates important exam questions from study materials.
Generate questions in valid JSON format only, with no additional text."""

        user_prompt = f"""Generate {request.question_count} important exam questions from the following study material.

Content:
{content}

Requirements:
- Marks: {marks_str}
- Difficulty levels: {difficulty_str}
- Categories: {categories_str}
- Include a mix of theory, numerical, and application-based questions
- Provide model answers for each question
- Identify the topic/chapter for each question
- Mark reference pages if possible

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question_text": "Question text here",
    "marks": "5",
    "category": "theory",
    "difficulty": "medium",
    "model_answer": "Detailed answer here",
    "topic": "Topic name",
    "chapter": "Chapter name"
  }}
]

Do not include any text outside the JSON array."""

        # Generate questions using LLM
        logger.info(f"Generating important questions for subject {request.subject_id}")
        response = llm_service.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4096
        )
        
        # Parse JSON response
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            questions_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {e}")
            logger.error(f"Response was: {response[:500]}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse generated questions. Please try again."
            )
        
        # Create question records
        created_questions = []
        for q_data in questions_data:
            question = ImportantQuestion(
                subject_id=request.subject_id,
                user_id=str(current_user.id),
                question_text=q_data.get('question_text', ''),
                marks=q_data.get('marks', '5'),
                category=QuestionCategory(q_data.get('category', 'theory')),
                difficulty=q_data.get('difficulty', 'medium'),
                model_answer=q_data.get('model_answer'),
                topic=q_data.get('topic'),
                chapter=q_data.get('chapter'),
                generated_at=datetime.utcnow()
            )
            await question.insert()
            created_questions.append(question)
        
        logger.info(f"Generated {len(created_questions)} important questions")
        
        return {
            "count": len(created_questions),
            "questions": [
                {
                    "id": str(q.id),
                    "question_text": q.question_text,
                    "marks": q.marks,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "topic": q.topic
                }
                for q in created_questions
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Important questions generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate important questions"
        )


# @router.get("/subject/{subject_id}")
# async def get_important_questions(
    # subject_id: str,
    # marks: Optional[str] = None,
    # difficulty: Optional[str] = None,
    # category: Optional[str] = None,
    # current_user: User = Depends(get_current_active_user)
# ):
#     """Get important questions for a subject with optional filters"""
#     try:
#         # Verify subject belongs to user
#         subject = await Subject.get(PydanticObjectId(subject_id))
#         if not subject or subject.user_id != str(current_user.id):
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
#         # Build query
#         query_filter = ImportantQuestion.subject_id == subject_id
#         query_filter = query_filter & (ImportantQuestion.user_id == str(current_user.id))
        
#         if marks:
#             query_filter = query_filter & (ImportantQuestion.marks == marks)
#         if difficulty:
#             query_filter = query_filter & (ImportantQuestion.difficulty == difficulty)
#         if category:
#             query_filter = query_filter & (ImportantQuestion.category == category)
        
#         questions = await ImportantQuestion.find(
#             query_filter
#         ).sort(-ImportantQuestion.generated_at).to_list()
        
#         questions_response = []
#         for q in questions:
#             q_dict = q.model_dump()
#             q_dict['id'] = str(q.id)
#             # Don't send model_answer in list view
#             q_dict.pop('model_answer', None)
#             questions_response.append(q_dict)
        
#         return questions_response
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching important questions: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Failed to fetch important questions"
#         )

@router.get("/subject/{subject_id}")
async def get_important_questions(
    subject_id: str,
    marks: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get important questions for a subject with optional filters"""
    try:
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

        # Build conditions as a list, passed positionally to find()
        conditions = [
            ImportantQuestion.subject_id == subject_id,
            ImportantQuestion.user_id == str(current_user.id),
        ]
        if marks:
            conditions.append(ImportantQuestion.marks == marks)
        if difficulty:
            conditions.append(ImportantQuestion.difficulty == difficulty)
        if category:
            conditions.append(ImportantQuestion.category == category)

        questions = await ImportantQuestion.find(
            *conditions
        ).sort(-ImportantQuestion.generated_at).to_list()

        questions_response = []
        for q in questions:
            q_dict = q.model_dump()
            q_dict['id'] = str(q.id)
            q_dict.pop('model_answer', None)
            questions_response.append(q_dict)

        return questions_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching important questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch important questions"
        )


@router.get("/{question_id}")
async def get_question(
    question_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific question with model answer"""
    try:
        question = await ImportantQuestion.get(PydanticObjectId(question_id))
        if not question or question.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        
        question_dict = question.model_dump()
        question_dict['id'] = str(question.id)
        
        return question_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch question"
        )
