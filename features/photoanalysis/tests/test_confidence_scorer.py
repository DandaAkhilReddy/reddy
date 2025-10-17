"""
Test Step 9: Confidence Scoring
"""
import pytest
from services.confidence_scorer import ConfidenceScorer
from models.schemas import BodyMeasurements


class TestConfidenceScorer:
    """Test multi-factor confidence scoring"""

    def setup_method(self):
        self.scorer = ConfidenceScorer()
        self.sample_measurements = BodyMeasurements(
            chest_circumference_cm=100.0,
            waist_circumference_cm=85.0,
            hip_circumference_cm=95.0,
            bicep_circumference_cm=35.0,
            thigh_circumference_cm=55.0,
            calf_circumference_cm=38.0,
            shoulder_width_cm=45.0,
            body_fat_percent=15.0,
            posture_rating=8.0,
            muscle_definition="moderate"
        )

    def test_optimal_confidence_score(self):
        """Test confidence score with optimal conditions"""
        confidence = self.scorer.calculate_confidence(
            measurements=self.sample_measurements,
            photo_count=3,
            completeness_score=1.0,
            ai_finish_reason="stop",
            extraction_strategy="direct_parse",
            validation_errors=[]
        )

        assert confidence.overall_score >= 0.90
        assert confidence.meets_threshold is True
        assert confidence.photo_count_factor == 1.0
        assert confidence.ai_confidence_factor >= 0.95

    def test_photo_count_factor_three_photos(self):
        """Test photo count factor with 3 photos"""
        factor = self.scorer._calculate_photo_factor(3)
        assert factor == 1.0

    def test_photo_count_factor_two_photos(self):
        """Test photo count factor with 2 photos"""
        factor = self.scorer._calculate_photo_factor(2)
        assert factor == 0.75

    def test_photo_count_factor_one_photo(self):
        """Test photo count factor with 1 photo"""
        factor = self.scorer._calculate_photo_factor(1)
        assert factor == 0.50

    def test_consistency_factor_good_measurements(self):
        """Test consistency with anatomically plausible measurements"""
        factor = self.scorer._calculate_consistency_factor(self.sample_measurements)
        assert factor >= 0.80

    def test_consistency_factor_inconsistent_bodyfat_muscle(self):
        """Test consistency with mismatched body fat and muscle definition"""
        measurements = BodyMeasurements(
            chest_circumference_cm=100.0,
            waist_circumference_cm=85.0,
            hip_circumference_cm=95.0,
            bicep_circumference_cm=35.0,
            thigh_circumference_cm=55.0,
            calf_circumference_cm=38.0,
            shoulder_width_cm=45.0,
            body_fat_percent=25.0,  # High body fat
            posture_rating=8.0,
            muscle_definition="high"  # But high muscle definition
        )

        factor = self.scorer._calculate_consistency_factor(measurements)
        assert factor < 1.0  # Should be penalized

    def test_consistency_factor_bicep_thigh_issue(self):
        """Test consistency when bicep > thigh (anatomically unusual)"""
        measurements = BodyMeasurements(
            chest_circumference_cm=100.0,
            waist_circumference_cm=85.0,
            hip_circumference_cm=95.0,
            bicep_circumference_cm=60.0,  # Unusually large
            thigh_circumference_cm=55.0,
            calf_circumference_cm=38.0,
            shoulder_width_cm=45.0,
            body_fat_percent=15.0,
            posture_rating=8.0,
            muscle_definition="moderate"
        )

        factor = self.scorer._calculate_consistency_factor(measurements)
        assert factor < 0.80  # Should have significant penalty

    def test_ai_confidence_factor_optimal(self):
        """Test AI confidence with optimal conditions"""
        factor = self.scorer._calculate_ai_factor("stop", "direct_parse")
        assert factor >= 0.95

    def test_ai_confidence_factor_markdown(self):
        """Test AI confidence with markdown extraction"""
        factor = self.scorer._calculate_ai_factor("stop", "markdown_strip")
        assert 0.90 <= factor < 1.0

    def test_ai_confidence_factor_error_fix(self):
        """Test AI confidence when error fixing was needed"""
        factor = self.scorer._calculate_ai_factor("stop", "error_fix")
        assert 0.70 <= factor < 0.85

    def test_ai_confidence_factor_length_finish(self):
        """Test AI confidence when hit token limit"""
        factor = self.scorer._calculate_ai_factor("length", "direct_parse")
        assert factor < 0.80

    def test_validation_quality_no_errors(self):
        """Test validation quality with no errors"""
        factor = self.scorer._calculate_validation_factor([])
        assert factor == 1.0

    def test_validation_quality_few_errors(self):
        """Test validation quality with few errors"""
        errors = ["Warning 1", "Warning 2"]
        factor = self.scorer._calculate_validation_factor(errors)
        assert 0.80 <= factor < 1.0

    def test_validation_quality_many_errors(self):
        """Test validation quality with many errors"""
        errors = [f"Error {i}" for i in range(10)]
        factor = self.scorer._calculate_validation_factor(errors)
        assert factor == 0.50

    def test_below_threshold_confidence(self):
        """Test confidence score below threshold"""
        confidence = self.scorer.calculate_confidence(
            measurements=self.sample_measurements,
            photo_count=1,  # Low
            completeness_score=0.50,  # Low
            ai_finish_reason="length",  # Not ideal
            extraction_strategy="error_fix",  # Had to fix errors
            validation_errors=["Error 1", "Error 2", "Error 3"]  # Multiple errors
        )

        assert confidence.overall_score < 0.70
        assert confidence.meets_threshold is False

    def test_factors_breakdown_present(self):
        """Test that factors breakdown is present"""
        confidence = self.scorer.calculate_confidence(
            measurements=self.sample_measurements,
            photo_count=3,
            completeness_score=1.0,
            ai_finish_reason="stop",
            extraction_strategy="direct_parse",
            validation_errors=[]
        )

        assert "photo_count" in confidence.factors_breakdown
        assert "consistency" in confidence.factors_breakdown
        assert "ai_finish" in confidence.factors_breakdown
        assert "extraction_method" in confidence.factors_breakdown
        assert "completeness_percent" in confidence.factors_breakdown

    def test_weighted_average_calculation(self):
        """Test that weighted average is calculated correctly"""
        # Manually verify weighted calculation
        confidence = self.scorer.calculate_confidence(
            measurements=self.sample_measurements,
            photo_count=3,  # 1.0 * 0.20 = 0.20
            completeness_score=1.0,  # 1.0 * 0.20 = 0.20
            ai_finish_reason="stop",
            extraction_strategy="direct_parse",  # ~1.0 * 0.20 = 0.20
            validation_errors=[]  # 1.0 * 0.10 = 0.10
        )

        # If consistency is also ~1.0 (0.30), total should be ~1.0
        # Allow some variance for consistency checks
        assert 0.85 <= confidence.overall_score <= 1.0
