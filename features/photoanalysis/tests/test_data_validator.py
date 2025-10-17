"""
Test Step 8: Data Validation & Type Conversion
"""
import pytest
from services.data_validator import DataValidator
from models.schemas import BodyMeasurements


class TestDataValidator:
    """Test schema validation and type conversion"""

    def setup_method(self):
        self.validator = DataValidator()

    def test_validate_clean_data(self):
        """Test validation with clean, valid data"""
        raw_data = {
            "chest_circumference_cm": 100.0,
            "waist_circumference_cm": 85.0,
            "hip_circumference_cm": 95.0,
            "bicep_circumference_cm": 35.0,
            "thigh_circumference_cm": 55.0,
            "calf_circumference_cm": 38.0,
            "shoulder_width_cm": 45.0,
            "body_fat_percent": 15.0,
            "posture_rating": 8.0,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        assert measurements is not None
        assert isinstance(measurements, BodyMeasurements)
        assert measurements.chest_circumference_cm == 100.0
        assert len(errors) == 0

    def test_type_coercion_string_to_float(self):
        """Test coercion of string numbers to float"""
        raw_data = {
            "chest_circumference_cm": "100",
            "waist_circumference_cm": "85.5",
            "hip_circumference_cm": 95.0,
            "bicep_circumference_cm": 35.0,
            "thigh_circumference_cm": 55.0,
            "calf_circumference_cm": 38.0,
            "shoulder_width_cm": 45.0,
            "body_fat_percent": "15",
            "posture_rating": 8,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        assert measurements is not None
        assert measurements.chest_circumference_cm == 100.0
        assert measurements.waist_circumference_cm == 85.5
        assert measurements.body_fat_percent == 15.0

    def test_key_normalization_camelcase(self):
        """Test normalization of camelCase keys"""
        raw_data = {
            "chestCircumferenceCm": 100.0,
            "waistCircumferenceCm": 85.0,
            "hipCircumferenceCm": 95.0,
            "bicepCircumferenceCm": 35.0,
            "thighCircumferenceCm": 55.0,
            "calfCircumferenceCm": 38.0,
            "shoulderWidthCm": 45.0,
            "bodyFatPercent": 15.0,
            "postureRating": 8.0,
            "muscleDefinition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        assert measurements is not None
        assert measurements.chest_circumference_cm == 100.0

    def test_key_normalization_short_names(self):
        """Test normalization of shortened key names"""
        raw_data = {
            "chest": 100.0,
            "waist": 85.0,
            "hip": 95.0,
            "bicep": 35.0,
            "thigh": 55.0,
            "calf": 38.0,
            "shoulder": 45.0,
            "bodyfat": 15.0,
            "posture": 8.0,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        assert measurements is not None
        # Should have some warnings about key normalization
        assert measurements.chest_circumference_cm == 100.0

    def test_unit_conversion_inches_to_cm(self):
        """Test automatic unit conversion from inches to cm"""
        raw_data = {
            "chest_circumference_cm": 40.0,  # Likely inches (40in -> 101.6cm)
            "waist_circumference_cm": 32.0,  # Likely inches (32in -> 81.3cm)
            "hip_circumference_cm": 38.0,    # Likely inches
            "bicep_circumference_cm": 14.0,  # Likely inches
            "thigh_circumference_cm": 22.0,  # Likely inches
            "calf_circumference_cm": 15.0,   # Likely inches
            "shoulder_width_cm": 18.0,       # Likely inches
            "body_fat_percent": 15.0,
            "posture_rating": 8.0,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        assert measurements is not None
        # Should have warnings about unit conversion
        assert any("Converted" in error for error in errors)
        # Values should be converted to cm
        assert measurements.chest_circumference_cm > 40.0  # Should be ~101.6

    def test_range_validation_out_of_range(self):
        """Test rejection of out-of-range values"""
        raw_data = {
            "chest_circumference_cm": 300.0,  # Too large
            "waist_circumference_cm": 85.0,
            "hip_circumference_cm": 95.0,
            "bicep_circumference_cm": 35.0,
            "thigh_circumference_cm": 10.0,   # Too small
            "calf_circumference_cm": 38.0,
            "shoulder_width_cm": 45.0,
            "body_fat_percent": 70.0,         # Too high
            "posture_rating": 8.0,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        # Should have errors for out-of-range values
        assert len(errors) > 0
        assert any("out of range" in error.lower() for error in errors)

    def test_muscle_definition_enum(self):
        """Test muscle_definition enum validation"""
        for valid_value in ["low", "moderate", "high"]:
            raw_data = {
                "chest_circumference_cm": 100.0,
                "waist_circumference_cm": 85.0,
                "hip_circumference_cm": 95.0,
                "bicep_circumference_cm": 35.0,
                "thigh_circumference_cm": 55.0,
                "calf_circumference_cm": 38.0,
                "shoulder_width_cm": 45.0,
                "body_fat_percent": 15.0,
                "posture_rating": 8.0,
                "muscle_definition": valid_value
            }

            measurements, errors = self.validator.validate(raw_data)
            assert measurements is not None
            assert measurements.muscle_definition == valid_value

    def test_invalid_muscle_definition(self):
        """Test invalid muscle_definition value"""
        raw_data = {
            "chest_circumference_cm": 100.0,
            "waist_circumference_cm": 85.0,
            "hip_circumference_cm": 95.0,
            "bicep_circumference_cm": 35.0,
            "thigh_circumference_cm": 55.0,
            "calf_circumference_cm": 38.0,
            "shoulder_width_cm": 45.0,
            "body_fat_percent": 15.0,
            "posture_rating": 8.0,
            "muscle_definition": "extreme"  # Invalid
        }

        measurements, errors = self.validator.validate(raw_data)

        # Should default to "moderate" with error
        assert measurements is not None
        assert measurements.muscle_definition == "moderate"
        assert any("muscle_definition" in error for error in errors)

    def test_completeness_score_full_data(self):
        """Test completeness score with all fields present"""
        measurements = BodyMeasurements(
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

        completeness = self.validator.check_completeness(measurements)
        assert completeness == 1.0

    def test_missing_fields(self):
        """Test validation with missing required fields"""
        raw_data = {
            "chest_circumference_cm": 100.0,
            "waist_circumference_cm": 85.0,
            # Missing other required fields
        }

        measurements, errors = self.validator.validate(raw_data)

        # Pydantic should fail validation due to missing required fields
        assert measurements is None
        assert len(errors) > 0

    def test_invalid_type_coercion(self):
        """Test handling of values that can't be coerced"""
        raw_data = {
            "chest_circumference_cm": "not_a_number",
            "waist_circumference_cm": 85.0,
            "hip_circumference_cm": 95.0,
            "bicep_circumference_cm": 35.0,
            "thigh_circumference_cm": 55.0,
            "calf_circumference_cm": 38.0,
            "shoulder_width_cm": 45.0,
            "body_fat_percent": 15.0,
            "posture_rating": 8.0,
            "muscle_definition": "moderate"
        }

        measurements, errors = self.validator.validate(raw_data)

        # Should have error about coercion failure
        assert len(errors) > 0
        assert any("could not convert" in error.lower() for error in errors)
