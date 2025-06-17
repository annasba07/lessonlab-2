import openai
import os
from typing import Dict, Any

class AIService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    async def generate_lesson_plan(self, topic: str, grade: str, duration: int, show_thoughts: bool = False) -> Dict[str, Any]:
        """
        Lesson plan generation pipeline
        """
        
        # Step 1: Parse topic and grade into learning objectives
        objectives = await self._generate_objectives(topic, grade)
        
        # Step 2: Create lesson structure
        structure = await self._create_lesson_structure(objectives, duration)
        
        # Step 3: Find and score resources
        resources = await self._find_resources(topic, grade)
        
        # Step 4: Assemble final lesson plan
        final_plan = await self._assemble_lesson_plan(objectives, structure, resources)
        
        result = {"plan": final_plan}
        
        if show_thoughts:
            result["thoughts"] = {
                "objectives_reasoning": f"Generated {len(objectives)} learning objectives based on {topic} for grade {grade}",
                "structure_reasoning": f"Created {duration}-minute lesson with intro, main activity, and assessment",
                "resources_reasoning": f"Found {len(resources)} relevant resources and scored them for age-appropriateness"
            }
        
        return result
    
    async def _generate_objectives(self, topic: str, grade: str):
        prompt = f"""
        Create 3-5 specific learning objectives for a {grade} grade lesson on "{topic}".
        Format as a list of clear, measurable objectives.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        # Parse response into structured objectives
        return [obj.strip() for obj in response.choices[0].message.content.split('\n') if obj.strip()]
    
    async def _create_lesson_structure(self, objectives, duration):
        prompt = f"""
        Create a {duration}-minute lesson structure with these objectives:
        {chr(10).join(objectives)}
        
        Include: Introduction (5-10 min), Main Activity, Assessment, and timing for each section.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return {
            "introduction": "Engage students with topic overview",
            "main_activity": response.choices[0].message.content,
            "assessment": "Quick formative assessment",
            "timing": f"{duration} minutes total"
        }
    
    async def _find_resources(self, topic: str, grade: str):
        # Mock resource finding - in real implementation, this would search YouTube/Google
        return [
            {
                "title": f"Educational video about {topic}",
                "type": "video",
                "url": "https://example.com/video",
                "score": 0.9,
                "reasoning": f"Highly relevant to {topic}, appropriate for grade {grade}"
            },
            {
                "title": f"Interactive worksheet on {topic}",
                "type": "worksheet",
                "url": "https://example.com/worksheet",
                "score": 0.8,
                "reasoning": "Good practice material with clear instructions"
            }
        ]
    
    async def _assemble_lesson_plan(self, objectives, structure, resources):
        return {
            "title": f"Lesson Plan: {objectives[0] if objectives else 'Custom Topic'}",
            "objectives": objectives,
            "structure": structure,
            "resources": resources,
            "materials_needed": ["Whiteboard", "Handouts", "Computer/Projector"],
            "differentiation": "Provide visual aids for visual learners, allow verbal responses for auditory learners"
        }