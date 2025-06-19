import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

class AIService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    async def call_llm(self, messages: List[Dict[str, str]], model: str = "gpt-4o", max_tokens: int = 1500, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Centralized OpenAI API call with basic error handling
        Returns both content and token usage information
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return {
                "content": response.choices[0].message.content.strip(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
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
        generation_metadata = objectives_and_structure["metadata"]
        
        # Step 2: Find and score resources
        resources = await self._find_resources(topic, grade)
        
        # Step 3: Assemble final lesson plan
        final_plan = await self._assemble_lesson_plan(objectives, structure, resources)
        
        result = {
            "plan": final_plan,
            "generation_metadata": generation_metadata
        }
        
        if show_thoughts:
            result["thoughts"] = {
                "objectives_reasoning": f"Generated {len(objectives)} learning objectives based on {topic} for grade {grade}",
                "structure_reasoning": f"Created {duration}-minute lesson with intro, main activity, and assessment",
                "resources_reasoning": f"Found {len(resources)} relevant resources and scored them for age-appropriateness"
            }
        
        return result
    
    async def evaluate_lesson_plan(self, lesson_plan: Dict[str, Any], topic: str, grade: str, duration: int) -> Dict[str, Any]:
        """
        Developer-facing evaluation system to assess lesson plan quality
        Returns scores for objective clarity, age appropriateness, and completeness
        """
        evaluation_prompt = f"""
        Evaluate this lesson plan for {grade} grade students on "{topic}" ({duration} minutes).
        
        Lesson Plan:
        {json.dumps(lesson_plan, indent=2)}
        
        Rate each dimension from 0.0 to 5.0 and provide brief reasoning:
        
        1. Objective Clarity: Are learning objectives specific, measurable, and use action verbs?
        2. Age Appropriateness: Is content suitable for {grade} grade level in language and complexity?
        3. Completeness: Does it include all required sections with sufficient detail?
        
        Respond with valid JSON:
        {{
          "objective_clarity": {{"score": 0.0-1.0, "reasoning": "brief explanation"}},
          "age_appropriateness": {{"score": 0.0-1.0, "reasoning": "brief explanation"}},
          "completeness": {{"score": 0.0-1.0, "reasoning": "brief explanation"}},
          "overall_score": 0.0-1.0,
          "suggestions": ["improvement suggestion 1", "improvement suggestion 2"]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert curriculum evaluator. Provide objective, constructive assessments."},
            {"role": "user", "content": evaluation_prompt}
        ]
        
        try:
            llm_result = await self.call_llm(messages, max_tokens=800, temperature=0.3)
            content = llm_result["content"]
            
            # Clean up JSON formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            evaluation = json.loads(content)
            return evaluation
            
        except Exception as e:
            # Return default evaluation if LLM call fails
            return {
                "objective_clarity": {"score": 0.7, "reasoning": "Evaluation failed, default score"},
                "age_appropriateness": {"score": 0.7, "reasoning": "Evaluation failed, default score"},
                "completeness": {"score": 0.7, "reasoning": "Evaluation failed, default score"},
                "overall_score": 0.7,
                "suggestions": ["Manual review needed - evaluation system error"]
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
        
        llm_result = await self.call_llm(messages, max_tokens=1500)
        content = llm_result["content"]
        token_usage = llm_result["usage"]

        # Capture generation metadata
        metadata = {
            "prompt_used": prompt,
            "system_prompt": "You are an expert curriculum designer with 20+ years of experience creating engaging, age-appropriate lesson plans. Always respond with valid JSON.",
            "model": "gpt-4o",
            "max_tokens": 1500,
            "temperature": 0.7,
            "generated_at": datetime.now().isoformat(),
            "token_usage": token_usage
        }

        try:
            # Remove any markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            result["metadata"] = metadata
            return result
        except json.JSONDecodeError as e:
            # Fallback: return structured data even if JSON parsing fails
            print(f"JSON parsing failed: {e}")
            metadata["parsing_failed"] = True
            metadata["raw_response"] = content[:500]  # Store first 500 chars for debugging
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
                },
                "metadata": metadata
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