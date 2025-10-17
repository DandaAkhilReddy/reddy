"""
Step 8: Schema Validation & Type Conversion
Validates and normalizes GPT-4o extracted measurements
"""
import logging
from typing import Dict, Any, Optional, List, Tuple
from pydantic import ValidationError
from ..models.schemas import BodyMeasurements, MuscleDefinition

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates and normalizes body measurement data"""

    # Conversion constants
    INCHES_TO_CM = 2.54
    LBS_TO_KG = 0.453592

    # Human-plausible ranges (cm, %)
    MEASUREMENT_RANGES = {
        "chest_circumference_cm": (50, 200),
        "waist_circumference_cm": (50, 200),
        "hip_circumference_cm": (50, 200),
        "bicep_circumference_cm": (15, 70),
        "thigh_circumference_cm": (30, 100),
        "calf_circumference_cm": (20, 70),
        "shoulder_width_cm": (30, 80),
        "body_fat_percent": (3, 60),
        "posture_rating": (0, 10),
    }

    def validate(
        self,
        raw_data: Dict[str, Any]
    ) -> Tuple[Optional[BodyMeasurements], List[str]]:
        """
        Validate and convert raw measurements to BodyMeasurements model

        Args:
            raw_data: Raw dict from JSON extraction

        Returns:
            Tuple of (BodyMeasurements or None, list of validation errors)
        """
        logger.debug(f"Validating {len(raw_data)} measurement fields")
        errors = []

        # Step 1: Normalize keys (handle variations)
        normalized_data = self._normalize_keys(raw_data)

        # Step 2: Type coercion (string -> float)
        coerced_data = self._coerce_types(normalized_data, errors)

        # Step 3: Unit conversion (if needed)
        converted_data = self._convert_units(coerced_data, errors)

        # Step 4: Range validation
        validated_data = self._validate_ranges(converted_data, errors)

        # Step 5: Try to create Pydantic model
        try:
            measurements = BodyMeasurements(**validated_data)
            logger.info(f"✅ Validation succeeded with {len(errors)} warnings")
            return measurements, errors

        except ValidationError as e:
            logger.error(f"❌ Pydantic validation failed: {e}")
            for error in e.errors():
                field = error.get('loc', ['unknown'])[0]
                msg = error.get('msg', 'validation error')
                errors.append(f"{field}: {msg}")

            return None, errors

    def _normalize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize key names to match schema

        Handles variations like:
        - "chest" -> "chest_circumference_cm"
        - "waistCircumference" -> "waist_circumference_cm"

        Args:
            data: Raw data dict

        Returns:
            Normalized data dict
        """
        normalized = {}

        # Key mapping for common variations
        key_map = {
            "chest": "chest_circumference_cm",
            "chest_cm": "chest_circumference_cm",
            "waist": "waist_circumference_cm",
            "waist_cm": "waist_circumference_cm",
            "hip": "hip_circumference_cm",
            "hip_cm": "hip_circumference_cm",
            "bicep": "bicep_circumference_cm",
            "bicep_cm": "bicep_circumference_cm",
            "thigh": "thigh_circumference_cm",
            "thigh_cm": "thigh_circumference_cm",
            "calf": "calf_circumference_cm",
            "calf_cm": "calf_circumference_cm",
            "shoulder": "shoulder_width_cm",
            "shoulder_width": "shoulder_width_cm",
            "bodyfat": "body_fat_percent",
            "body_fat": "body_fat_percent",
            "bf_percent": "body_fat_percent",
            "posture": "posture_rating",
            "muscle_def": "muscle_definition",
        }

        for key, value in data.items():
            # Convert camelCase to snake_case
            snake_key = self._camel_to_snake(key)

            # Apply mapping if exists
            normalized_key = key_map.get(snake_key, snake_key)

            normalized[normalized_key] = value

        return normalized

    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _coerce_types(
        self,
        data: Dict[str, Any],
        errors: List[str]
    ) -> Dict[str, Any]:
        """
        Coerce types to expected formats

        Args:
            data: Normalized data
            errors: Error list to append to

        Returns:
            Type-coerced data
        """
        coerced = {}

        for key, value in data.items():
            # Handle muscle_definition enum
            if key == "muscle_definition":
                if isinstance(value, str):
                    value_lower = value.lower()
                    if value_lower in ["low", "moderate", "high"]:
                        coerced[key] = value_lower
                    else:
                        errors.append(
                            f"muscle_definition: '{value}' not in [low, moderate, high]"
                        )
                        coerced[key] = "moderate"  # Default
                else:
                    coerced[key] = "moderate"

            # Handle numeric fields
            elif key in self.MEASUREMENT_RANGES:
                try:
                    coerced[key] = float(value)
                except (ValueError, TypeError):
                    errors.append(
                        f"{key}: Could not convert '{value}' to float"
                    )
                    # Don't include invalid values
            else:
                # Unknown key, keep as-is
                coerced[key] = value

        return coerced

    def _convert_units(
        self,
        data: Dict[str, Any],
        errors: List[str]
    ) -> Dict[str, Any]:
        """
        Convert units to metric if needed

        Detects if values are likely in inches and converts to cm

        Args:
            data: Type-coerced data
            errors: Error list to append to

        Returns:
            Unit-converted data
        """
        converted = {}

        for key, value in data.items():
            # Check if circumference measurement is likely in inches
            if key.endswith("_cm") and isinstance(value, (int, float)):
                # Heuristic: chest < 50 is likely inches
                if "circumference" in key and value < 50:
                    converted_value = value * self.INCHES_TO_CM
                    errors.append(
                        f"{key}: Converted {value} inches -> {converted_value:.1f} cm"
                    )
                    converted[key] = converted_value
                else:
                    converted[key] = value
            else:
                converted[key] = value

        return converted

    def _validate_ranges(
        self,
        data: Dict[str, Any],
        errors: List[str]
    ) -> Dict[str, Any]:
        """
        Validate measurements are within human-plausible ranges

        Args:
            data: Unit-converted data
            errors: Error list to append to

        Returns:
            Range-validated data (out-of-range values removed)
        """
        validated = {}

        for key, value in data.items():
            if key in self.MEASUREMENT_RANGES:
                min_val, max_val = self.MEASUREMENT_RANGES[key]

                if isinstance(value, (int, float)):
                    if min_val <= value <= max_val:
                        validated[key] = value
                    else:
                        errors.append(
                            f"{key}: Value {value} out of range [{min_val}, {max_val}]"
                        )
                        # Don't include out-of-range values
            else:
                # Not a measurement field, keep as-is
                validated[key] = value

        return validated

    def check_completeness(self, measurements: BodyMeasurements) -> float:
        """
        Calculate data completeness score

        Args:
            measurements: Validated BodyMeasurements

        Returns:
            Completeness score (0.0 to 1.0)
        """
        # Required fields for full completeness
        required_fields = [
            "chest_circumference_cm",
            "waist_circumference_cm",
            "hip_circumference_cm",
            "bicep_circumference_cm",
            "thigh_circumference_cm",
            "calf_circumference_cm",
            "shoulder_width_cm",
            "body_fat_percent",
            "posture_rating",
            "muscle_definition",
        ]

        present_count = 0
        for field in required_fields:
            value = getattr(measurements, field, None)
            if value is not None:
                present_count += 1

        return present_count / len(required_fields)


# Global validator instance
data_validator = DataValidator()


def validate_measurements(
    raw_data: Dict[str, Any]
) -> Tuple[Optional[BodyMeasurements], List[str], float]:
    """
    Convenience function to validate measurements

    Args:
        raw_data: Raw measurement dict

    Returns:
        Tuple of (BodyMeasurements or None, errors, completeness_score)
    """
    measurements, errors = data_validator.validate(raw_data)

    if measurements:
        completeness = data_validator.check_completeness(measurements)
        return measurements, errors, completeness
    else:
        return None, errors, 0.0
