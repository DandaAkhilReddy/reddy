"""
Step 6: Anthropic Claude Vision Client with Retry Logic
Robust async client for Claude API Vision with exponential backoff
"""
import asyncio
import logging
import base64
from typing import Dict, Any, Optional, Tuple
from anthropic import AsyncAnthropic, AnthropicError, APITimeoutError, RateLimitError
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ClaudeVisionClient:
    """Async client for Claude Vision with retry logic"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.temperature = settings.anthropic_temperature
        self.max_tokens = settings.anthropic_max_tokens
        self.timeout = settings.anthropic_timeout
        self.retry_attempts = settings.api_retry_attempts
        self.retry_delay = settings.api_retry_delay

    async def analyze_body_photos(
        self,
        images_base64: list[str],
        prompt: str,
        attempt: int = 1
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Send images to Claude Vision for body analysis

        Args:
            images_base64: List of base64-encoded images
            prompt: Text prompt for analysis
            attempt: Current attempt number (for logging)

        Returns:
            Tuple of (response_text, metadata)

        Raises:
            AnthropicError: If all retry attempts fail
        """
        try:
            logger.info(
                f"Calling Claude Vision (attempt {attempt}/{self.retry_attempts})"
            )

            # Build messages array with images
            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]

            # Add images (Claude supports multiple images)
            for img_b64 in images_base64:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64
                    }
                })

            # Make API call with timeout
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{
                        "role": "user",
                        "content": content
                    }]
                ),
                timeout=self.timeout
            )

            # Extract response text
            response_text = response.content[0].text

            # Build metadata for tracking
            metadata = {
                "model": response.model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                "stop_reason": response.stop_reason,
                "attempt": attempt,
            }

            # Estimate cost (Claude 3.5 Sonnet: $3/MTok input, $15/MTok output)
            input_cost = (metadata["input_tokens"] / 1_000_000) * 3.0
            output_cost = (metadata["output_tokens"] / 1_000_000) * 15.0
            metadata["estimated_cost_usd"] = round(input_cost + output_cost, 4)

            logger.info(
                f"✅ Claude response received | "
                f"Tokens: {metadata['total_tokens']} | "
                f"Cost: ${metadata['estimated_cost_usd']}"
            )

            return response_text, metadata

        except APITimeoutError as e:
            logger.error(f"⏱️ API timeout on attempt {attempt}: {e}")
            return await self._handle_retry(images_base64, prompt, attempt, e)

        except RateLimitError as e:
            logger.error(f"🚦 Rate limit hit on attempt {attempt}: {e}")
            return await self._handle_retry(images_base64, prompt, attempt, e)

        except AnthropicError as e:
            logger.error(f"❌ Anthropic API error on attempt {attempt}: {e}")
            return await self._handle_retry(images_base64, prompt, attempt, e)

        except asyncio.TimeoutError as e:
            logger.error(f"⏱️ Request timeout ({self.timeout}s) on attempt {attempt}")
            return await self._handle_retry(images_base64, prompt, attempt, e)

        except Exception as e:
            logger.error(f"💥 Unexpected error on attempt {attempt}: {e}")
            return await self._handle_retry(images_base64, prompt, attempt, e)

    async def _handle_retry(
        self,
        images_base64: list[str],
        prompt: str,
        attempt: int,
        error: Exception
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Handle retry logic with exponential backoff

        Args:
            images_base64: Original images
            prompt: Original prompt
            attempt: Current attempt number
            error: Exception that triggered retry

        Returns:
            Result from retry attempt

        Raises:
            AnthropicError: If max retries exceeded
        """
        if attempt >= self.retry_attempts:
            logger.error(
                f"❌ Max retry attempts ({self.retry_attempts}) exceeded"
            )
            raise AnthropicError(
                f"Failed after {self.retry_attempts} attempts: {str(error)}"
            )

        # Exponential backoff: 1s, 2s, 4s
        delay = self.retry_delay * (2 ** (attempt - 1))
        logger.warning(f"⏳ Retrying in {delay}s...")
        await asyncio.sleep(delay)

        # Retry recursively
        return await self.analyze_body_photos(images_base64, prompt, attempt + 1)


# Global client instance
claude_vision_client = ClaudeVisionClient()


async def call_claude_vision(
    images_base64: list[str],
    prompt: str
) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to call Claude Vision

    Args:
        images_base64: List of base64-encoded images
        prompt: Text prompt for analysis

    Returns:
        Tuple of (response_text, metadata)
    """
    return await claude_vision_client.analyze_body_photos(images_base64, prompt)
