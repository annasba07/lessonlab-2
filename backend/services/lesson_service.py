from supabase import create_client, Client
from services.ai_service import AIService
import os
import uuid
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class LessonService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables are required")
            
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
        
        # Generate title if not provided
        title = request.title or f"{request.topic} - Grade {request.grade}"
        
        # Save to database
        lesson_id = str(uuid.uuid4())
        lesson_data = {
            "id": lesson_id,
            "user_id": user_id,
            "title": title,
            "topic": request.topic,
            "grade": request.grade,
            "duration": request.duration,
            "plan_json": lesson_plan["plan"],
            "agent_thoughts": lesson_plan.get("thoughts") if request.show_agent_thoughts else None,
            "generation_metadata": lesson_plan.get("generation_metadata"),
        }
        
        # Insert into Supabase
        result = self.supabase.table("lesson_plans").insert(lesson_data).execute()
        
        # Return the created lesson with timestamps
        if result.data:
            lesson_record = result.data[0]
            
            # Start background evaluation (fire-and-forget)
            asyncio.create_task(self._evaluate_lesson_async(
                lesson_id=lesson_id,
                lesson_plan=lesson_plan["plan"],
                topic=request.topic,
                grade=request.grade,
                duration=request.duration
            ))
            
            return lesson_record
        else:
            raise Exception("Failed to create lesson plan")
    
    async def get_user_lessons(self, user_id: str):
        response = self.supabase.table("lesson_plans").select("*").eq("user_id", user_id).execute()
        return response.data
    
    async def get_lesson(self, lesson_id: str, user_id: str):
        response = self.supabase.table("lesson_plans").select("*").eq("id", lesson_id).eq("user_id", user_id).single().execute()
        return response.data
    
    async def _evaluate_lesson_async(self, lesson_id: str, lesson_plan: dict, topic: str, grade: str, duration: int):
        """
        Background evaluation task - runs after user gets their lesson plan
        """
        try:
            logger.info(f"Starting background evaluation for lesson {lesson_id}")
            
            # Run AI evaluation
            evaluation = await self.ai_service.evaluate_lesson_plan(lesson_plan, topic, grade, duration)
            
            # Update the lesson plan with evaluation results
            update_result = self.supabase.table("lesson_plans").update({
                "evaluation": evaluation
            }).eq("id", lesson_id).execute()
            
            if update_result.data:
                logger.info(f"Evaluation completed for lesson {lesson_id}, overall score: {evaluation.get('overall_score', 'unknown')}")
            else:
                logger.warning(f"Failed to update lesson {lesson_id} with evaluation results")
                
        except Exception as e:
            logger.error(f"Background evaluation failed for lesson {lesson_id}: {str(e)}")
            # Don't re-raise - this is a background task
    
    async def rate_lesson(self, lesson_id: str, user_id: str, rating: bool):
        """
        Submit a user rating for a lesson plan
        """
        try:
            # Verify the lesson belongs to the user and update the rating
            update_result = self.supabase.table("lesson_plans").update({
                "user_rating": rating
            }).eq("id", lesson_id).eq("user_id", user_id).execute()
            
            if update_result.data:
                rating_text = "thumbs up" if rating else "thumbs down"
                logger.info(f"User rating '{rating_text}' submitted for lesson {lesson_id}")
                return True
            else:
                logger.warning(f"Failed to update rating for lesson {lesson_id} - lesson not found or not owned by user")
                return False
                
        except Exception as e:
            logger.error(f"Failed to rate lesson {lesson_id}: {str(e)}")
            raise Exception(f"Failed to submit rating: {str(e)}")

    async def revise_lesson(self, lesson_id: str, user_id: str, feedback: str) -> Dict[str, Any]:
        """
        Revise an existing lesson plan based on user feedback
        Now stores revisions in lesson_revisions table for history
        """
        try:
            # Get original lesson
            original_lesson_data = self.supabase.table("lesson_plans").select("*").eq("id", lesson_id).eq("user_id", user_id).execute()
            
            if not original_lesson_data.data:
                return None
            
            original_lesson = original_lesson_data.data[0]
            
            # Generate revised lesson plan using AI service
            revision_result = await self.ai_service.revise_lesson_plan(
                original_plan=original_lesson["plan_json"],
                feedback=feedback,
                topic=original_lesson["topic"],
                grade=original_lesson["grade"],
                duration=original_lesson["duration"]
            )
            
            # Get the next revision number
            current_revision_number = original_lesson.get("current_revision_number", 0)
            next_revision_number = current_revision_number + 1
            
            # Store the revision in the lesson_revisions table
            revision_data = {
                "lesson_id": lesson_id,
                "revision_number": next_revision_number,
                "revised_plan_json": revision_result["plan"],
                "revision_feedback": feedback,
                "revision_metadata": revision_result["metadata"]
            }
            
            revision_result_db = self.supabase.table("lesson_revisions").insert(revision_data).execute()
            
            if not revision_result_db.data:
                raise Exception("Failed to store revision in lesson_revisions table")
            
            # Update the lesson_plans table with the latest revision (for backward compatibility)
            # and increment the current_revision_number
            updated_lesson = self.supabase.table("lesson_plans").update({
                "revised_plan_json": revision_result["plan"],  # Keep latest revision here
                "revision_feedback": feedback,  # Keep latest feedback here
                "current_revision_number": next_revision_number,
                "updated_at": datetime.now().isoformat(),
                "user_rating": None  # Reset rating for revised lesson
            }).eq("id", lesson_id).eq("user_id", user_id).execute()
            
            if not updated_lesson.data:
                raise Exception("Failed to update lesson with revision")
            
            return self._format_lesson(updated_lesson.data[0])
            
        except Exception as e:
            logger.error(f"Error revising lesson {lesson_id}: {str(e)}")
            raise

    async def get_lesson_revisions(self, lesson_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all revisions for a lesson plan
        """
        try:
            # Verify the lesson belongs to the user
            lesson_check = self.supabase.table("lesson_plans").select("id").eq("id", lesson_id).eq("user_id", user_id).execute()
            if not lesson_check.data:
                return []
            
            # Get all revisions for this lesson
            revisions_result = self.supabase.table("lesson_revisions").select("*").eq("lesson_id", lesson_id).order("revision_number").execute()
            
            return revisions_result.data if revisions_result.data else []
            
        except Exception as e:
            logger.error(f"Error getting revisions for lesson {lesson_id}: {str(e)}")
            return []

    def _format_lesson(self, lesson_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format lesson data from database for API response"""
        return {
            "id": lesson_data["id"],
            "user_id": lesson_data["user_id"],
            "title": lesson_data.get("title"),
            "topic": lesson_data["topic"],
            "grade": lesson_data["grade"],
            "duration": lesson_data["duration"],
            "plan_json": lesson_data["plan_json"],
            "agent_thoughts": lesson_data.get("agent_thoughts"),
            "evaluation": lesson_data.get("evaluation"),
            "generation_metadata": lesson_data.get("generation_metadata"),
            # Backward compatibility: Keep existing fields
            "revised_plan_json": lesson_data.get("revised_plan_json"),
            "revision_feedback": lesson_data.get("revision_feedback"),
            # New fields for revision history
            "current_revision_number": lesson_data.get("current_revision_number", 0),
            "user_rating": lesson_data.get("user_rating"),
            "created_at": lesson_data["created_at"],
            "updated_at": lesson_data["updated_at"]
        }