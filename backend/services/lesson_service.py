from supabase import create_client, Client
from services.ai_service import AIService
import os
import uuid
from datetime import datetime

class LessonService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.supabase: Client = create_client(url, key)
        self.ai_service = AIService()
    
    async def generate_lesson(self, request, user_id: str):
        # Generate lesson using AI service
        lesson_plan = await self.ai_service.generate_lesson_plan(
            topic=request.topic,
            grade=request.grade,
            duration=request.duration,
            show_thoughts=request.show_agent_thoughts
        )
        
        # Save to database
        lesson_id = str(uuid.uuid4())
        lesson_data = {
            "id": lesson_id,
            "user_id": user_id,
            "topic": request.topic,
            "grade": request.grade,
            "duration": request.duration,
            "plan": lesson_plan["plan"],
            "agent_thoughts": lesson_plan.get("thoughts") if request.show_agent_thoughts else None,
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into Supabase
        self.supabase.table("lesson_plans").insert(lesson_data).execute()
        
        return lesson_data
    
    async def get_user_lessons(self, user_id: str):
        response = self.supabase.table("lesson_plans").select("*").eq("user_id", user_id).execute()
        return response.data
    
    async def get_lesson(self, lesson_id: str, user_id: str):
        response = self.supabase.table("lesson_plans").select("*").eq("id", lesson_id).eq("user_id", user_id).single().execute()
        return response.data