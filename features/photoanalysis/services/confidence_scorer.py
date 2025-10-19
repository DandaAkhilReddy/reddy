"""
Step 9: Confidence Scoring System
Multi-factor confidence score for body scan reliability
Updated: 2025-10-19
"""
import logging
from typing import Dict, Any
from ..models.schemas import BodyMeasurements, ConfidenceMetrics
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for body scan results"""

    def __init__(self):
        self.min_threshold = settings.min_confidence_score

    def calculate_confidence(
        self,
        measurements: BodyMeasurements,
        photo_count: int,
        completeness_score: float,
        ai_finish_reason: str,
        extraction_strategy: str,
        validation_errors: list[str]
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence score

        Args:
            measurements: Validated body measurements
            photo_count: Number of photos analyzed (1-3)
            completeness_score: Data completeness (0.0-1.0)
            ai_finish_reason: OpenAI finish reason
            extraction_strategy: JSON extraction strategy used
            validation_errors: List of validation warnings

        Returns:
            ConfidenceMetrics with detailed breakdown
        """
        logger.debug("Calculating confidence score...")

        # Factor 1: Photo count (optimal is 3)
        photo_factor = self._calculate_photo_factor(photo_count)

        # Factor 2: Measurement consistency
        consistency_factor = self._calculate_consistency_factor(measurements)

        # Factor 3: AI confidence
        ai_factor = self._calculate_ai_factor(ai_finish_reason, extraction_strategy)

        # Factor 4: Data completeness
        completeness_factor = completeness_score

        # Factor 5: Validation quality
        validation_factor = self._calculate_validation_factor(validation_errors)

        # Weighted average (weights sum to 1.0)
        weights = {
            "photo": 0.20,
            "consistency": 0.30,
            "ai": 0.20,
            "completeness": 0.20,
            "validation": 0.10,
        }

        overall_score = (
            photo_factor * weights["photo"] +
            consistency_factor * weights["consistency"] +
            ai_factor * weights["ai"] +
            completeness_factor * weights["completeness"] +
            validation_factor * weights["validation"]
        )

        # Build confidence score object
        confidence = ConfidenceMetrics(
            overall_score=round(overall_score, 3),
            photo_count_factor=round(photo_factor, 3),
            consistency_factor=round(consistency_factor, 3),
            ai_confidence_factor=round(ai_factor, 3),
            data_completeness_factor=round(completeness_factor, 3),
            validation_quality_factor=round(validation_factor, 3),
            meets_threshold=overall_score >= self.min_threshold,
            factors_breakdown={
                "photo_count": f"{photo_count}/3 photos",
                "consistency": self._get_consistency_summary(measurements),
                "ai_finish": ai_finish_reason,
                "extraction_method": extraction_strategy,
                "validation_warnings": len(validation_errors),
                "completeness_percent": f"{completeness_score * 100:.1f}%",
            }
        )

        if confidence.meets_threshold:
            logger.info(
                f"✅ Confidence score: {overall_score:.3f} "
                f"(threshold: {self.min_threshold})"
            )
        else:
            logger.warning(
                f"⚠️ Confidence score: {overall_score:.3f} "
                f"below threshold: {self.min_threshold}"
            )

        return confidence

    def _calculate_photo_factor(self, photo_count: int) -> float:
        """
        Calculate photo count factor

        3 photos (front, side, back) = 1.0
        2 photos = 0.75
        1 photo = 0.50

        Args:
            photo_count: Number of photos (1-3)

        Returns:
            Factor score (0.0-1.0)
        """
        if photo_count >= 3:
            return 1.0
        elif photo_count == 2:
            return 0.75
        elif photo_count == 1:
            return 0.50
        else:
            return 0.0

    def _calculate_consistency_factor(self, measurements: BodyMeasurements) -> float:
        """
        Calculate measurement consistency factor

        Checks if ratios make anatomical sense:
        - Chest > Waist (usually)
        - Hip circumferences reasonable
        - Body fat % aligns with muscle definition

        Args:
            measurements: Body measurements

        Returns:
            Factor score (0.0-1.0)
        """
        score = 1.0

        # Check 1: Chest vs Waist (most people)
        if measurements.waist_circumference_cm > measurements.chest_circumference_cm:
            # Could be apple body type, minor deduction
            score -= 0.10

        # Check 2: Body fat % vs muscle definition alignment
        bf = measurements.body_fat_percent
        muscle = measurements.muscle_definition

        # High muscle definition but high body fat is inconsistent
        if muscle == "high" and bf > 20:
            score -= 0.15
        # Low muscle definition but very low body fat is inconsistent
        elif muscle == "low" and bf < 10:
            score -= 0.15

        # Check 3: Bicep/Thigh proportion (thigh should be larger)
        if measurements.bicep_circumference_cm > measurements.thigh_circumference_cm:
            # Anatomically unusual, significant deduction
            score -= 0.25

        # Check 4: Calf should be smaller than thigh
        if measurements.calf_circumference_cm > measurements.thigh_circumference_cm:
            score -= 0.20

        # Check 5: Shoulder width should be reasonable relative to chest
        shoulder_chest_ratio = measurements.shoulder_width_cm / measurements.chest_circumference_cm
        if shoulder_chest_ratio < 0.3 or shoulder_chest_ratio > 0.8:
            # Unusual ratio
            score -= 0.15

        return max(0.0, score)

    def _get_consistency_summary(self, measurements: BodyMeasurements) -> str:
        """Get human-readable consistency summary"""
        factor = self._calculate_consistency_factor(measurements)
        if factor >= 0.9:
            return "Excellent"
        elif factor >= 0.75:
            return "Good"
        elif factor >= 0.6:
            return "Fair"
        else:
            return "Poor"

    def _calculate_ai_factor(
        self,
        finish_reason: str,
        extraction_strategy: str
    ) -> float:
        """
        Calculate AI confidence factor

        Args:
            finish_reason: OpenAI finish reason
            extraction_strategy: JSON extraction method used

        Returns:
            Factor score (0.0-1.0)
        """
        score = 1.0

        # Finish reason scoring
        if finish_reason == "stop":
            # Normal completion
            score = 1.0
        elif finish_reason == "length":
            # Hit token limit, might be incomplete
            score = 0.70
        else:
            # content_filter, null, or other
            score = 0.50

        # Extraction strategy penalty
        strategy_scores = {
            "direct_parse": 1.0,        # Clean JSON
            "markdown_strip": 0.95,     # Had markdown wrapper
            "regex_extract": 0.85,      # Found embedded JSON
            "error_fix": 0.75,          # Had to fix errors
            "ai_repair": 0.60,          # Needed AI repair
        }

        extraction_score = strategy_scores.get(extraction_strategy, 0.50)

        # Weighted combination
        return (score * 0.6) + (extraction_score * 0.4)

    def _calculate_validation_factor(self, validation_errors: list[str]) -> float:
        """
        Calculate validation quality factor

        Args:
            validation_errors: List of validation warnings

        Returns:
            Factor score (0.0-1.0)
        """
        if len(validation_errors) == 0:
            return 1.0
        elif len(validation_errors) <= 2:
            # Minor issues
            return 0.85
        elif len(validation_errors) <= 5:
            # Moderate issues
            return 0.70
        else:
            # Many issues
            return 0.50


# Global scorer instance
confidence_scorer = ConfidenceScorer()


def calculate_scan_confidence(
    measurements: BodyMeasurements,
    photo_count: int,
    completeness_score: float,
    ai_finish_reason: str,
    extraction_strategy: str,
    validation_errors: list[str]
) -> ConfidenceMetrics:
    """
    Convenience function to calculate confidence score

    Args:
        measurements: Validated body measurements
        photo_count: Number of photos analyzed
        completeness_score: Data completeness (0.0-1.0)
        ai_finish_reason: OpenAI finish reason
        extraction_strategy: JSON extraction strategy
        validation_errors: Validation warnings

    Returns:
        ConfidenceMetrics object
    """
    return confidence_scorer.calculate_confidence(
        measurements=measurements,
        photo_count=photo_count,
        completeness_score=completeness_score,
        ai_finish_reason=ai_finish_reason,
        extraction_strategy=extraction_strategy,
        validation_errors=validation_errors
    )


def calculate_confidence_score(
    measurements: BodyMeasurements,
    image_quality: float,
    angle_confidence: float,
    api_success: bool
) -> ConfidenceMetrics:
    """
    Backward-compatible wrapper for vision_pipeline.py

    Converts old-style parameters to new confidence scoring system

    Args:
        measurements: Validated body measurements
        image_quality: Average image quality score (0-100)
        angle_confidence: Average angle detection confidence (0-1.0)
        api_success: Whether API call succeeded

    Returns:
        ConfidenceMetrics object
    """
    # Convert image quality and angle confidence to completeness score
    completeness_score = (image_quality / 100 + angle_confidence) / 2

    # Use defaults for new required parameters
    photo_count = 3  # Assume 3 photos (front, side, back)
    ai_finish_reason = "stop" if api_success else "error"
    extraction_strategy = "direct_parse"  # Assume best case
    validation_errors = []  # No validation errors available

    return calculate_scan_confidence(
        measurements=measurements,
        photo_count=photo_count,
        completeness_score=completeness_score,
        ai_finish_reason=ai_finish_reason,
        extraction_strategy=extraction_strategy,
        validation_errors=validation_errors
    )
