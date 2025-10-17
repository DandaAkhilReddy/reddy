"""
Step 6: OpenAI GPT-4o Client with Retry Logic
Robust async client for GPT-4o Vision API with exponential backoff
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from openai import AsyncOpenAI, OpenAIError, APITimeoutError, RateLimitError
from ..config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIVisionClient:
    """Async client for GPT-4o Vision with retry logic"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        self.timeout = settings.openai_timeout
        self.retry_attempts = settings.api_retry_attempts
        self.retry_delay = settings.api_retry_delay

    async def analyze_body_photos(
        self,
        messages: list[Dict[str, Any]],
        attempt: int = 1
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Send images to GPT-4o Vision for body analysis

        Args:
            messages: OpenAI messages array with images
            attempt: Current attempt number (for logging)

        Returns:
            Tuple of (response_text, metadata)

        Raises:
            OpenAIError: If all retry attempts fail
        """
        try:
            logger.info(
                f"Calling GPT-4o Vision (attempt {attempt}/{self.retry_attempts})"
            )

            # Make API call with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                ),
                timeout=self.timeout
            )

            # Extract response text
            response_text = response.choices[0].message.content

            # Build metadata for tracking
            metadata = {
                "model": response.model,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason,
                "attempt": attempt,
            }

            # Estimate cost (GPT-4o pricing: $5/1M input, $15/1M output)
            input_cost = (metadata["prompt_tokens"] / 1_000_000) * 5.0
            output_cost = (metadata["completion_tokens"] / 1_000_000) * 15.0
            metadata["estimated_cost_usd"] = round(input_cost + output_cost, 4)

            logger.info(
                f"✅ GPT-4o response received | "
                f"Tokens: {metadata['total_tokens']} | "
                f"Cost: ${metadata['estimated_cost_usd']}"
            )

            return response_text, metadata

        except APITimeoutError as e:
            logger.error(f"⏱️ API timeout on attempt {attempt}: {e}")
            return await self._handle_retry(messages, attempt, e)

        except RateLimitError as e:
            logger.error(f"🚦 Rate limit hit on attempt {attempt}: {e}")
            return await self._handle_retry(messages, attempt, e)

        except OpenAIError as e:
            logger.error(f"❌ OpenAI API error on attempt {attempt}: {e}")
            return await self._handle_retry(messages, attempt, e)

        except asyncio.TimeoutError as e:
            logger.error(f"⏱️ Request timeout ({self.timeout}s) on attempt {attempt}")
            return await self._handle_retry(messages, attempt, e)

        except Exception as e:
            logger.error(f"💥 Unexpected error on attempt {attempt}: {e}")
            return await self._handle_retry(messages, attempt, e)

    async def _handle_retry(
        self,
        messages: list[Dict[str, Any]],
        attempt: int,
        error: Exception
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Handle retry logic with exponential backoff

        Args:
            messages: Original messages array
            attempt: Current attempt number
            error: Exception that triggered retry

        Returns:
            Result from retry attempt

        Raises:
            OpenAIError: If max retries exceeded
        """
        if attempt >= self.retry_attempts:
            logger.error(
                f"❌ Max retry attempts ({self.retry_attempts}) exceeded"
            )
            raise OpenAIError(
                f"Failed after {self.retry_attempts} attempts: {str(error)}"
            )

        # Exponential backoff: 1s, 2s, 4s
        delay = self.retry_delay * (2 ** (attempt - 1))
        logger.warning(f"⏳ Retrying in {delay}s...")
        await asyncio.sleep(delay)

        # Retry recursively
        return await self.analyze_body_photos(messages, attempt + 1)


# Global client instance
openai_vision_client = OpenAIVisionClient()


async def call_gpt4o_vision(
    messages: list[Dict[str, Any]]
) -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function to call GPT-4o Vision

    Args:
        messages: OpenAI messages array with images

    Returns:
        Tuple of (response_text, metadata)
    """
    return await openai_vision_client.analyze_body_photos(messages)
