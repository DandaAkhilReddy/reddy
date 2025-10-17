"""
Step 5: Build Optimized Vision Prompt
Engineered prompts for GPT-4o Vision to extract body measurements
"""
from typing import Dict, Any, Optional


class VisionPromptEngine:
    """Generates optimized prompts for GPT-4o Vision analysis"""

    def __init__(self):
        self.system_prompt = self._build_system_prompt()
        self.user_prompt_template = self._build_user_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build system prompt (<50 tokens for efficiency)

        Returns:
            System message string
        """
        return (
            "You are an expert body composition analyst. "
            "Analyze physique photos precisely and output valid JSON only."
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

    def build_messages(
        self,
        images_base64: list[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> list[Dict[str, Any]]:
        """
        Build complete message array for GPT-4o

        Args:
            images_base64: List of 3 base64-encoded images
            user_context: Optional context (height, gender, etc.)

        Returns:
            Messages array for OpenAI API
        """
        # System message
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        # User message with images
        content = []

        # Add text prompt
        user_prompt = self.user_prompt_template

        # Optionally enhance with user context
        if user_context:
            context_str = self._format_context(user_context)
            if context_str:
                user_prompt = f"{context_str}\n\n{user_prompt}"

        content.append({
            "type": "text",
            "text": user_prompt
        })

        # Add images
        for idx, img_b64 in enumerate(images_base64):
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}",
                    "detail": "high"  # High detail for precise measurements
                }
            })

        messages.append({
            "role": "user",
            "content": content
        })

        return messages

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


def build_vision_messages(
    images_base64: list[str],
    user_context: Optional[Dict[str, Any]] = None
) -> list[Dict[str, Any]]:
    """
    Convenience function to build GPT-4o messages

    Args:
        images_base64: List of base64 images
        user_context: Optional user context

    Returns:
        OpenAI messages array
    """
    return vision_prompt_engine.build_messages(images_base64, user_context)
