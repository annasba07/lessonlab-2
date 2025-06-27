from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from services.lesson_service import LessonService
from utils.auth import get_current_user

router = APIRouter()
lesson_service = LessonService()

class LessonRequest(BaseModel):
    topic: str
    grade: str
    duration: int = 60  # minutes
    title: Optional[str] = None
    show_agent_thoughts: bool = False

class LessonResponse(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    topic: str
    grade: str
    duration: int
    plan_json: dict
    agent_thoughts: Optional[dict] = None
    evaluation: Optional[dict] = None  # Background evaluation results
    generation_metadata: Optional[dict] = None  # AI generation metadata
    revised_plan_json: Optional[dict] = None
    revision_feedback: Optional[str] = None
    user_rating: Optional[bool] = None
    created_at: str
    updated_at: str

class RatingRequest(BaseModel):
    rating: bool

class RatingResponse(BaseModel):
    message: str
    rating: bool

class RevisionRequest(BaseModel):
    feedback: str

class RevisionHistoryResponse(BaseModel):
    lesson_id: str
    revisions: List[Dict[str, Any]]

@router.post("/generate", response_model=LessonResponse)
async def generate_lesson(
    request: LessonRequest, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        result = await lesson_service.generate_lesson(request, current_user["user_id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[LessonResponse])
async def get_lessons(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        lessons = await lesson_service.get_user_lessons(current_user["user_id"])
        return lessons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        lesson = await lesson_service.get_lesson(lesson_id, current_user["user_id"])
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        return lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{lesson_id}/rating", response_model=RatingResponse)
async def rate_lesson(
    lesson_id: str,
    rating_request: RatingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Validate rating (boolean validation is automatic with Pydantic)
        
        result = await lesson_service.rate_lesson(lesson_id, current_user["user_id"], rating_request.rating)
        if not result:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        return RatingResponse(message="Rating submitted successfully", rating=rating_request.rating)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{lesson_id}/revise", response_model=LessonResponse)
async def revise_lesson(
    lesson_id: str,
    request: RevisionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Revise an existing lesson plan based on teacher feedback
    """
    try:
        if not request.feedback.strip():
            raise HTTPException(status_code=400, detail="Feedback cannot be empty")
        
        result = await lesson_service.revise_lesson(
            lesson_id, 
            current_user["user_id"], 
            request.feedback
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lesson_id}/revisions", response_model=RevisionHistoryResponse)
async def get_lesson_revisions(
    lesson_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get revision history for a lesson plan
    """
    try:
        revisions = await lesson_service.get_lesson_revisions(lesson_id, current_user["user_id"])
        
        return RevisionHistoryResponse(
            lesson_id=lesson_id,
            revisions=revisions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))