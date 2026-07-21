"""
Quiz endpoints - MongoDB/Beanie version
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
from app.models.quiz import Quiz, QuizQuestion, QuestionType, DifficultyLevel, QuizMode
from app.models.uploaded_file import UploadedFile
from app.services.rag.vector_store import vector_store
from app.services.llm.llm_service import llm_service

router = APIRouter()


class QuizGenerateRequest(BaseModel):
    """Request model for quiz generation"""
    subject_id: str
    title: str
    question_count: int = Field(default=10, ge=1, le=50)
    question_types: Optional[List[QuestionType]] = None
    difficulty: Optional[DifficultyLevel] = DifficultyLevel.MEDIUM
    quiz_mode: Optional[QuizMode] = QuizMode.PRACTICE
    time_limit_minutes: Optional[int] = None


@router.post("/generate")
async def generate_quiz(
    request: QuizGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate quiz from subject's uploaded PDFs"""
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
        query_text = "important concepts definitions formulas examples key topics"
        retrieved_docs = vector_store.query(
            query_text=query_text,
            subject_id=int(request.subject_id),
            top_k=30
        )
        
        if not retrieved_docs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve content from vector store"
            )
        
        # Combine retrieved content
        content = "\n\n".join([doc['text'] for doc in retrieved_docs])
        
        # Build prompt for quiz generation
        question_types_str = ", ".join([qt.value for qt in request.question_types]) if request.question_types else "mcq, true_false, short_answer"
        
        system_prompt = """You are an expert educator who creates high-quality quiz questions from study materials.
Generate questions in valid JSON format only, with no additional text."""

        user_prompt = f"""Generate {request.question_count} quiz questions from the following study material.

Content:
{content}

Requirements:
- Question types: {question_types_str}
- Difficulty level: {request.difficulty.value}
- Include a mix of conceptual and practical questions
- Provide clear explanations for each answer
- Assign appropriate marks (1 for easy, 2 for medium, 3 for hard)

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question_text": "Question text here",
    "question_type": "mcq",
    "difficulty": "medium",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Explanation here",
    "marks": 2,
    "topic": "Topic name"
  }}
]

Do not include any text outside the JSON array."""

        # Generate quiz using LLM
        logger.info(f"Generating quiz for subject {request.subject_id}")
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
            logger.error(f"Failed to parse quiz JSON: {e}")
            logger.error(f"Response was: {response[:500]}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse generated quiz. Please try again."
            )
        
        # Create quiz record
        quiz = Quiz(
            subject_id=request.subject_id,
            user_id=str(current_user.id),
            title=request.title,
            quiz_mode=request.quiz_mode,
            time_limit_minutes=request.time_limit_minutes,
            question_count=len(questions_data),
            created_at=datetime.utcnow()
        )
        await quiz.insert()
        
        # Create question records
        total_marks = 0
        for q_data in questions_data:
            question = QuizQuestion(
                quiz_id=str(quiz.id),
                question_text=q_data.get('question_text', ''),
                question_type=QuestionType(q_data.get('question_type', 'mcq')),
                difficulty=DifficultyLevel(q_data.get('difficulty', 'medium')),
                options=q_data.get('options'),
                correct_answer=q_data.get('correct_answer'),
                explanation=q_data.get('explanation'),
                marks=q_data.get('marks', 1),
                topic=q_data.get('topic'),
                created_at=datetime.utcnow()
            )
            await question.insert()
            total_marks += question.marks
        
        # Update quiz with total marks
        quiz.total_marks = total_marks
        quiz.passing_marks = int(total_marks * 0.4)  # 40% passing
        await quiz.save()
        
        logger.info(f"Quiz generated: {quiz.id} with {len(questions_data)} questions")
        
        return {
            "id": str(quiz.id),
            "title": quiz.title,
            "question_count": quiz.question_count,
            "total_marks": quiz.total_marks,
            "passing_marks": quiz.passing_marks,
            "quiz_mode": quiz.quiz_mode,
            "time_limit_minutes": quiz.time_limit_minutes,
            "created_at": quiz.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )


@router.get("/subject/{subject_id}")
async def get_quizzes(
    subject_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all quizzes for a subject"""
    try:
        # Verify subject belongs to user
        subject = await Subject.get(PydanticObjectId(subject_id))
        if not subject or subject.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
        
        quizzes = await Quiz.find(
            Quiz.subject_id == subject_id,
            Quiz.user_id == str(current_user.id)
        ).sort(-Quiz.created_at).to_list()
        
        quizzes_response = []
        for quiz in quizzes:
            quiz_dict = quiz.model_dump()
            quiz_dict['id'] = str(quiz.id)
            quizzes_response.append(quiz_dict)
        
        return quizzes_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quizzes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quizzes"
        )


@router.get("/{quiz_id}/questions")
async def get_quiz_questions(
    quiz_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get questions for a specific quiz"""
    try:
        quiz = await Quiz.get(PydanticObjectId(quiz_id))
        if not quiz or quiz.user_id != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
        
        questions = await QuizQuestion.find(
            QuizQuestion.quiz_id == quiz_id
        ).to_list()
        
        questions_response = []
        for q in questions:
            q_dict = q.model_dump()
            q_dict['id'] = str(q.id)
            # Don't send correct_answer in list view (for taking quiz)
            q_dict.pop('correct_answer', None)
            questions_response.append(q_dict)
        
        return questions_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quiz questions"
        )
