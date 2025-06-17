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
    created_at: str
    updated_at: str

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