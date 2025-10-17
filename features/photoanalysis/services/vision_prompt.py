"""
Step 5: Build Optimized Vision Prompt
Engineered prompts for Claude Vision to extract body measurements
"""
from typing import Dict, Any, Optional


class VisionPromptEngine:
    """Generates optimized prompts for Claude Vision analysis"""

    def __init__(self):
        self.user_prompt_template = self._build_user_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build system prompt (Note: Claude uses system parameter, not system message)

        Returns:
            System message string
        """
        return (
            "You are an expert body composition analyst with training in kinesiology and anthropometry. "
            "Analyze physique photos precisely and output valid JSON only. "
            "Be accurate, methodical, and data-driven in your assessments."
        )

    def _build_user_prompt(self) -> str:
        """
        Build user prompt template (<150 tokens)

        Returns:
            User prompt string
        """
        return """Analyze these 3 body photos (front, side, back) of the person.

Output ONLY a valid JSON object with these exact fields:

{
  "chest_circumference_cm": <number>,
  "waist_circumference_cm": <number>,
  "hip_circumference_cm": <number>,
  "bicep_circumference_cm": <number>,
  "thigh_circumference_cm": <number>,
  "calf_circumference_cm": <number>,
  "shoulder_width_cm": <number>,
  "body_fat_percent": <number>,
  "posture_rating": <number 0-10>,
  "muscle_definition": "<low|moderate|high>"
}

All measurements in centimeters. Be precise. No explanation, only JSON."""

    def build_prompt(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build complete text prompt for Claude (images passed separately)

        Args:
            user_context: Optional context (height, gender, etc.)

        Returns:
            Complete text prompt
        """
        # Start with template
        user_prompt = self.user_prompt_template

        # Optionally enhance with user context
        if user_context:
            context_str = self._format_context(user_context)
            if context_str:
                user_prompt = f"{context_str}\n\n{user_prompt}"

        return user_prompt

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format user context into prompt enhancement

        Args:
            context: User profile data

        Returns:
            Context string or empty if no useful context
        """
        parts = []

        if "height_cm" in context and context["height_cm"]:
            parts.append(f"Person's height: {context['height_cm']}cm")

        if "gender" in context and context["gender"]:
            parts.append(f"Gender: {context['gender']}")

        if "age" in context and context["age"]:
            parts.append(f"Age: {context['age']}")

        if parts:
            return "Context: " + ", ".join(parts) + "."

        return ""

    def estimate_token_count(self) -> int:
        """
        Estimate token count of prompts (excluding images)

        Returns:
            Approximate token count
        """
        # Rough estimation: ~4 chars per token
        total_chars = len(self.system_prompt) + len(self.user_prompt_template)
        return total_chars // 4


# Global prompt engine
vision_prompt_engine = VisionPromptEngine()


def build_vision_prompt(
    user_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to build Claude vision prompt

    Args:
        user_context: Optional user context

    Returns:
        Text prompt for Claude
    """
    return vision_prompt_engine.build_prompt(user_context)
