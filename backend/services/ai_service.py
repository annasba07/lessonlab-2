import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    async def call_llm(self, messages: List[Dict[str, str]], model: str = "gpt-4o", max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Centralized OpenAI API call with basic error handling
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    async def generate_lesson_plan(self, topic: str, grade: str, duration: int, show_thoughts: bool = False) -> Dict[str, Any]:
        """
        Lesson plan generation pipeline
        """
        
        # Step 1: Generate objectives and structure in one call (performance optimization)
        objectives_and_structure = await self._generate_objectives_and_structure(topic, grade, duration)
        objectives = objectives_and_structure["objectives"]
        structure = objectives_and_structure["structure"]
        
        # Step 2: Find and score resources
        resources = await self._find_resources(topic, grade)
        
        # Step 3: Assemble final lesson plan
        final_plan = await self._assemble_lesson_plan(objectives, structure, resources)
        
        result = {"plan": final_plan}
        
        if show_thoughts:
            result["thoughts"] = {
                "objectives_reasoning": f"Generated {len(objectives)} learning objectives based on {topic} for grade {grade}",
                "structure_reasoning": f"Created {duration}-minute lesson with intro, main activity, and assessment",
                "resources_reasoning": f"Found {len(resources)} relevant resources and scored them for age-appropriateness"
            }
        
        return result
        prompt = f"""
        Create a {duration}-minute lesson structure with these objectives:
        {chr(10).join(objectives)}
        
        Include: Introduction (5-10 min), Main Activity, Assessment, and timing for each section.
        """
        
        messages = [{"role": "user", "content": prompt}]
        content = await self.call_llm(messages, max_tokens=500)
        
        return {
            "introduction": "Engage students with topic overview",
            "main_activity": content,
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
    
    async def _generate_objectives_and_structure(self, topic: str, grade: str, duration: int):
        """
        Combined API call to generate both objectives and lesson structure (performance optimization)
        """
        prompt = f"""
        Create a comprehensive lesson plan foundation for {grade} grade students on "{topic}" ({duration} minutes).

        Provide a complete response with both learning objectives and lesson structure.

        Format your response as valid JSON:
        {{
          "objectives": [
            "Specific, measurable learning objective 1",
            "Specific, measurable learning objective 2", 
            "Specific, measurable learning objective 3"
          ],
          "structure": {{
            "introduction": "Brief description of lesson introduction (5-10 minutes)",
            "main_activity": "Detailed description of the main learning activity with student engagement",
            "assessment": "Description of how student learning will be assessed",
            "timing": "{duration} minutes total with time breakdown"
          }}
        }}

        Requirements:
        - 3-5 clear, measurable learning objectives appropriate for {grade} grade
        - Age-appropriate activities and language
        - Include timing breakdown for each section
        - Focus on student engagement and active learning
        """

        messages = [
            {"role": "system", "content": "You are an expert curriculum designer with 20+ years of experience creating engaging, age-appropriate lesson plans. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        content = await self.call_llm(messages, max_tokens=1500)

        try:
            # Remove any markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            return result
        except json.JSONDecodeError as e:
            # Fallback: return structured data even if JSON parsing fails
            print(f"JSON parsing failed: {e}")
            return {
                "objectives": [
                    f"Students will understand key concepts about {topic}",
                    f"Students will be able to apply {topic} knowledge in practical situations",
                    f"Students will demonstrate comprehension through assessment activities"
                ],
                "structure": {
                    "introduction": "Engage students with topic overview and prior knowledge activation",
                    "main_activity": content[:200] if content else "Interactive lesson activity",
                    "assessment": "Quick formative assessment to check understanding",
                    "timing": f"{duration} minutes total"
                }
            }

    async def _assemble_lesson_plan(self, objectives, structure, resources):
        return {
            "title": f"Lesson Plan: {objectives[0] if objectives else 'Custom Topic'}",
            "objectives": objectives,
            "structure": structure,
            "resources": resources,
            "materials_needed": ["Whiteboard", "Handouts", "Computer/Projector"],
            "differentiation": "Provide visual aids for visual learners, allow verbal responses for auditory learners"
        }