"""
Vision Pipeline Orchestrator (Steps 1-9)
Complete workflow from uploaded photos to validated body measurements
Updated: 2025-10-19
"""
import logging
import base64
from typing import Tuple, Optional, Dict, Any, List
import asyncio

from ..models.schemas import (
    BodyMeasurements,
    ImageQuality,
    PhotoAngle,
    UserProfile,
    ConfidenceMetrics
)
from ..utils.image_validator import validate_image
from ..utils.image_processor import process_image
from ..utils.angle_detector import detect_angles
from .user_profile_validator import validate_user_profile
from .vision_prompt import build_vision_prompt
from .claude_vision_client import call_claude_vision
from .json_extractor import extract_json
from .data_validator import validate_measurements
from .confidence_scorer import calculate_scan_confidence
from .performance_optimizer import get_performance_optimizer
from .error_handler import get_error_handler, PhotoAnalysisError, AIAnalysisError

logger = logging.getLogger(__name__)


class VisionPipeline:
    """
    Orchestrates the complete AI vision pipeline (Steps 1-9)

    Flow:
    1. Validate 3 images
    2. Preprocess images
    3. Detect angles (front/side/back)
    4. Validate user profile
    5. Build Claude vision prompt
    6. Call Claude Vision API
    7. Extract JSON measurements
    8. Validate data schema
    9. Calculate confidence score

    Returns validated BodyMeasurements with confidence metrics
    """

    def __init__(self):
        self.performance_optimizer = get_performance_optimizer()
        self.error_handler = get_error_handler()

    async def analyze_photos(
        self,
        front_image: bytes,
        side_image: bytes,
        back_image: bytes,
        user_id: str,
        height_cm: float,
        weight_kg: Optional[float] = None,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        filename_front: str = "front.jpg",
        filename_side: str = "side.jpg",
        filename_back: str = "back.jpg"
    ) -> Tuple[BodyMeasurements, ConfidenceMetrics, Dict[str, Any]]:
        """
        Run complete vision analysis pipeline

        Args:
            front_image: Front view image bytes
            side_image: Side view image bytes
            back_image: Back view image bytes
            user_id: User identifier
            height_cm: User height in centimeters
            weight_kg: User weight in kilograms (optional)
            gender: User gender (optional)
            age: User age (optional)
            filename_front: Front image filename
            filename_side: Side image filename
            filename_back: Back image filename

        Returns:
            Tuple of (BodyMeasurements, ConfidenceMetrics, pipeline_metadata)

        Raises:
            PhotoAnalysisError: If pipeline fails at any step
            AIAnalysisError: If Claude Vision API fails
        """
        logger.info(f"🚀 Starting vision pipeline for user {user_id}")

        try:
            async with self.performance_optimizer.profile("complete_vision_pipeline"):
                # Track pipeline metadata
                metadata = {
                    "user_id": user_id,
                    "steps_completed": [],
                    "errors": [],
                    "timing": {}
                }

                # =============================================
                # STEP 1: Validate Image Quality
                # =============================================
                logger.info("Step 1: Validating image quality...")

                async with self.performance_optimizer.profile("step_1_validation"):
                    quality_results = await self._step1_validate_images(
                        front_image, side_image, back_image,
                        filename_front, filename_side, filename_back
                    )

                metadata["steps_completed"].append("step_1_validation")
                metadata["image_quality"] = {
                    "front": quality_results["front"].quality_score,
                    "side": quality_results["side"].quality_score,
                    "back": quality_results["back"].quality_score
                }

                # =============================================
                # STEP 2: Preprocess Images
                # =============================================
                logger.info("Step 2: Preprocessing images...")

                async with self.performance_optimizer.profile("step_2_preprocessing"):
                    processed_images = await self._step2_preprocess_images(
                        front_image, side_image, back_image,
                        quality_results
                    )

                metadata["steps_completed"].append("step_2_preprocessing")

                # =============================================
                # STEP 3: Detect Angles
                # =============================================
                logger.info("Step 3: Detecting photo angles...")

                async with self.performance_optimizer.profile("step_3_angle_detection"):
                    angle_results = await self._step3_detect_angles(processed_images)

                metadata["steps_completed"].append("step_3_angle_detection")
                metadata["angle_detection"] = {
                    label: {
                        "angle": result.angle_type.value,
                        "confidence": result.confidence
                    }
                    for label, result in angle_results.items()
                }

                # =============================================
                # STEP 4: Validate User Profile
                # =============================================
                logger.info("Step 4: Validating user profile...")

                async with self.performance_optimizer.profile("step_4_profile_validation"):
                    user_profile = await self._step4_validate_profile(
                        user_id, height_cm, weight_kg, gender, age
                    )

                metadata["steps_completed"].append("step_4_profile_validation")
                metadata["user_profile"] = {
                    "height_cm": user_profile.height_cm,
                    "has_whoop": user_profile.whoop_data is not None
                }

                # =============================================
                # STEP 5: Build Vision Prompt
                # =============================================
                logger.info("Step 5: Building Claude vision prompt...")

                async with self.performance_optimizer.profile("step_5_prompt_building"):
                    prompt, context = await self._step5_build_prompt(user_profile)

                metadata["steps_completed"].append("step_5_prompt_building")

                # =============================================
                # STEP 6: Call Claude Vision API
                # =============================================
                logger.info("Step 6: Calling Claude Vision API...")

                async with self.performance_optimizer.profile("step_6_vision_api"):
                    vision_response, api_metadata = await self._step6_call_vision_api(
                        processed_images, prompt
                    )

                metadata["steps_completed"].append("step_6_vision_api")
                metadata["vision_api"] = api_metadata

                # =============================================
                # STEP 7: Extract JSON Measurements
                # =============================================
                logger.info("Step 7: Extracting measurements from response...")

                async with self.performance_optimizer.profile("step_7_json_extraction"):
                    raw_measurements = await self._step7_extract_json(vision_response)

                metadata["steps_completed"].append("step_7_json_extraction")

                # =============================================
                # STEP 8: Validate Data Schema
                # =============================================
                logger.info("Step 8: Validating measurement schema...")

                async with self.performance_optimizer.profile("step_8_schema_validation"):
                    validated_measurements = await self._step8_validate_schema(
                        raw_measurements, user_profile
                    )

                metadata["steps_completed"].append("step_8_schema_validation")

                # =============================================
                # STEP 9: Calculate Confidence Score
                # =============================================
                logger.info("Step 9: Calculating confidence metrics...")

                async with self.performance_optimizer.profile("step_9_confidence_scoring"):
                    confidence_metrics = await self._step9_calculate_confidence(
                        validated_measurements,
                        quality_results,
                        angle_results,
                        api_metadata
                    )

                metadata["steps_completed"].append("step_9_confidence_scoring")
                metadata["confidence"] = {
                    "overall": confidence_metrics.overall_confidence,
                    "measurement_completeness": confidence_metrics.measurement_completeness
                }

                logger.info(
                    f"✅ Vision pipeline complete | "
                    f"Confidence: {confidence_metrics.overall_confidence:.2f} | "
                    f"Steps: {len(metadata['steps_completed'])}/9"
                )

                return validated_measurements, confidence_metrics, metadata

        except Exception as e:
            # Log error with full context
            await self.error_handler.log_error(
                error=e,
                step="Vision Pipeline",
                user_id=user_id,
                context=metadata,
                severity="error"
            )

            # Re-raise as PhotoAnalysisError
            raise PhotoAnalysisError(
                f"Vision pipeline failed: {str(e)}",
                step=metadata.get("steps_completed", [])[-1] if metadata.get("steps_completed") else "unknown"
            )

    # =============================================
    # STEP IMPLEMENTATIONS
    # =============================================

    async def _step1_validate_images(
        self,
        front_image: bytes,
        side_image: bytes,
        back_image: bytes,
        filename_front: str,
        filename_side: str,
        filename_back: str
    ) -> Dict[str, ImageQuality]:
        """Step 1: Validate image quality for all 3 photos"""

        # Validate in parallel
        results = await asyncio.gather(
            asyncio.to_thread(validate_image, front_image, filename_front),
            asyncio.to_thread(validate_image, side_image, filename_side),
            asyncio.to_thread(validate_image, back_image, filename_back)
        )

        quality_map = {
            "front": results[0],
            "side": results[1],
            "back": results[2]
        }

        # Check all images are valid
        for label, quality in quality_map.items():
            if not quality.is_valid:
                raise PhotoAnalysisError(
                    f"{label.capitalize()} image failed validation: "
                    f"Quality score {quality.quality_score}/100. "
                    f"Issues: {quality.issues}",
                    step="step_1_validation"
                )

        logger.info(
            f"✅ Step 1 complete | Quality scores: "
            f"Front={quality_map['front'].quality_score}, "
            f"Side={quality_map['side'].quality_score}, "
            f"Back={quality_map['back'].quality_score}"
        )

        return quality_map

    async def _step2_preprocess_images(
        self,
        front_image: bytes,
        side_image: bytes,
        back_image: bytes,
        quality_results: Dict[str, ImageQuality]
    ) -> Dict[str, Tuple[bytes, Any]]:
        """Step 2: Preprocess images (rotation, normalization, resize)"""

        # Preprocess in parallel
        images = [
            (front_image, quality_results["front"].orientation),
            (side_image, quality_results["side"].orientation),
            (back_image, quality_results["back"].orientation)
        ]

        results = await asyncio.gather(
            asyncio.to_thread(process_image, images[0][0], images[0][1]),
            asyncio.to_thread(process_image, images[1][0], images[1][1]),
            asyncio.to_thread(process_image, images[2][0], images[2][1])
        )

        processed_map = {
            "front": results[0],
            "side": results[1],
            "back": results[2]
        }

        logger.info("✅ Step 2 complete | All images preprocessed")

        return processed_map

    async def _step3_detect_angles(
        self,
        processed_images: Dict[str, Tuple[bytes, Any]]
    ) -> Dict[str, PhotoAngle]:
        """Step 3: Detect and validate photo angles"""

        # Prepare images for angle detection
        images_for_detection = [
            (processed_images["front"][1], "front"),
            (processed_images["side"][1], "side"),
            (processed_images["back"][1], "back")
        ]

        # Detect angles
        angle_results = await asyncio.to_thread(detect_angles, images_for_detection)

        logger.info(
            f"✅ Step 3 complete | Angles: "
            f"Front={angle_results['front'].angle_type.value} "
            f"({angle_results['front'].confidence:.2f}), "
            f"Side={angle_results['side'].angle_type.value} "
            f"({angle_results['side'].confidence:.2f}), "
            f"Back={angle_results['back'].angle_type.value} "
            f"({angle_results['back'].confidence:.2f})"
        )

        return angle_results

    async def _step4_validate_profile(
        self,
        user_id: str,
        height_cm: float,
        weight_kg: Optional[float],
        gender: Optional[str],
        age: Optional[int]
    ) -> UserProfile:
        """Step 4: Validate user profile and fetch WHOOP data"""

        user_profile = await validate_user_profile(
            user_id=user_id,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender,
            age=age,
            fetch_whoop=True
        )

        logger.info(
            f"✅ Step 4 complete | Height: {user_profile.height_cm}cm | "
            f"WHOOP: {'Yes' if user_profile.whoop_data else 'No'}"
        )

        return user_profile

    async def _step5_build_prompt(
        self,
        user_profile: UserProfile
    ) -> Tuple[str, Dict[str, Any]]:
        """Step 5: Build optimized Claude vision prompt"""

        # Build context from user profile
        from .user_profile_validator import user_profile_validator
        context = user_profile_validator.build_ai_context(user_profile)

        # Build prompt
        prompt = build_vision_prompt(user_context=context)

        logger.info(
            f"✅ Step 5 complete | Prompt length: {len(prompt)} chars | "
            f"Context fields: {len(context)}"
        )

        return prompt, context

    async def _step6_call_vision_api(
        self,
        processed_images: Dict[str, Tuple[bytes, Any]],
        prompt: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Step 6: Call Claude Vision API with retry logic"""

        # Convert images to base64
        images_base64 = [
            base64.b64encode(processed_images["front"][0]).decode('utf-8'),
            base64.b64encode(processed_images["side"][0]).decode('utf-8'),
            base64.b64encode(processed_images["back"][0]).decode('utf-8')
        ]

        # Call Claude Vision
        response_text, metadata = await call_claude_vision(images_base64, prompt)

        logger.info(
            f"✅ Step 6 complete | Tokens: {metadata['total_tokens']} | "
            f"Cost: ${metadata['estimated_cost_usd']}"
        )

        return response_text, metadata

    async def _step7_extract_json(self, vision_response: str) -> Dict[str, Any]:
        """Step 7: Extract JSON measurements from response"""

        raw_measurements, strategy = await asyncio.to_thread(
            extract_json, vision_response
        )

        if not raw_measurements:
            raise PhotoAnalysisError(
                "Failed to extract JSON from Claude Vision response",
                step="step_7_json_extraction"
            )

        logger.info(
            f"✅ Step 7 complete | Extracted {len(raw_measurements)} fields | Strategy: {strategy}"
        )

        return raw_measurements

    async def _step8_validate_schema(
        self,
        raw_measurements: Dict[str, Any],
        user_profile: UserProfile
    ) -> BodyMeasurements:
        """Step 8: Validate and convert measurements to schema"""

        validated_measurements, errors, completeness = await asyncio.to_thread(
            validate_measurements,
            raw_measurements
        )

        if not validated_measurements:
            raise PhotoAnalysisError(
                f"Measurement validation failed: {errors}",
                step="step_8_schema_validation"
            )

        logger.info(
            f"✅ Step 8 complete | All measurements validated | Completeness: {completeness:.2%}"
        )

        return validated_measurements

    async def _step9_calculate_confidence(
        self,
        measurements: BodyMeasurements,
        quality_results: Dict[str, ImageQuality],
        angle_results: Dict[str, PhotoAngle],
        api_metadata: Dict[str, Any]
    ) -> ConfidenceMetrics:
        """Step 9: Calculate multi-factor confidence score"""

        # Calculate average image quality
        avg_quality = (
            quality_results["front"].quality_score +
            quality_results["side"].quality_score +
            quality_results["back"].quality_score
        ) / 3

        # Calculate average angle confidence
        avg_angle_confidence = (
            angle_results["front"].confidence +
            angle_results["side"].confidence +
            angle_results["back"].confidence
        ) / 3

        # Calculate confidence
        confidence_metrics = await asyncio.to_thread(
            calculate_confidence_score,
            measurements=measurements,
            image_quality=avg_quality,
            angle_confidence=avg_angle_confidence,
            api_success=True
        )

        logger.info(
            f"✅ Step 9 complete | Confidence: {confidence_metrics.overall_confidence:.2f}"
        )

        return confidence_metrics


# Global pipeline instance
vision_pipeline = VisionPipeline()


async def run_vision_analysis(
    front_image: bytes,
    side_image: bytes,
    back_image: bytes,
    user_id: str,
    height_cm: float,
    **kwargs
) -> Tuple[BodyMeasurements, ConfidenceMetrics, Dict[str, Any]]:
    """
    Convenience function to run complete vision analysis

    Args:
        front_image: Front view image bytes
        side_image: Side view image bytes
        back_image: Back view image bytes
        user_id: User identifier
        height_cm: User height in centimeters
        **kwargs: Additional optional parameters (weight_kg, gender, age, etc.)

    Returns:
        Tuple of (BodyMeasurements, ConfidenceMetrics, metadata)

    Raises:
        PhotoAnalysisError: If analysis fails
    """
    return await vision_pipeline.analyze_photos(
        front_image=front_image,
        side_image=side_image,
        back_image=back_image,
        user_id=user_id,
        height_cm=height_cm,
        **kwargs
    )
