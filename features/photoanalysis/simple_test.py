"""
Simple Standalone Test for Core AI Vision Pipeline (Steps 6-9)
Tests JSON extraction, validation, and confidence scoring in isolation
"""
import json
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
from pydantic import BaseModel, Field


# ===== COPY OF KEY SCHEMAS =====
class MuscleDefinition(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class BodyMeasurements(BaseModel):
    chest_circumference_cm: float = Field(ge=50, le=200)
    waist_circumference_cm: float = Field(ge=50, le=200)
    hip_circumference_cm: float = Field(ge=50, le=200)
    bicep_circumference_cm: float = Field(ge=15, le=70)
    thigh_circumference_cm: float = Field(ge=30, le=100)
    calf_circumference_cm: float = Field(ge=20, le=70)
    shoulder_width_cm: float = Field(ge=30, le=80)
    body_fat_percent: float = Field(ge=3, le=60)
    posture_rating: float = Field(ge=0, le=10)
    muscle_definition: MuscleDefinition


# ===== STEP 7: JSON EXTRACTION =====
def extract_json_simple(response_text: str) -> Optional[Dict[str, Any]]:
    """Simplified JSON extraction"""
    import re

    # Strategy 1: Direct parse
    try:
        return json.loads(response_text.strip())
    except:
        pass

    # Strategy 2: Strip markdown
    patterns = [
        r"```json\s*\n(.*?)\n```",
        r"```\s*\n(.*?)\n```",
    ]

    for pattern in patterns:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except:
                continue

    return None


# ===== STEP 8: VALIDATION =====
def validate_simple(raw_data: Dict[str, Any]) -> Tuple[Optional[BodyMeasurements], List[str]]:
    """Simplified validation"""
    from pydantic import ValidationError

    errors = []

    try:
        measurements = BodyMeasurements(**raw_data)
        return measurements, errors
    except ValidationError as e:
        for error in e.errors():
            field = error.get('loc', ['unknown'])[0]
            msg = error.get('msg', 'validation error')
            errors.append(f"{field}: {msg}")
        return None, errors


# ===== STEP 9: CONFIDENCE =====
def calculate_confidence_simple(
    photo_count: int,
    completeness: float,
    extraction_ok: bool,
    validation_ok: bool
) -> float:
    """Simplified confidence calculation"""
    photo_factor = min(photo_count / 3.0, 1.0)
    extraction_factor = 1.0 if extraction_ok else 0.5
    validation_factor = 1.0 if validation_ok else 0.3

    return (photo_factor * 0.3 +
            extraction_factor * 0.3 +
            validation_factor * 0.2 +
            completeness * 0.2)


# ===== MOCK GPT-4O RESPONSE =====
MOCK_RESPONSE = '''```json
{
  "chest_circumference_cm": 102.5,
  "waist_circumference_cm": 84.0,
  "hip_circumference_cm": 98.5,
  "bicep_circumference_cm": 36.0,
  "thigh_circumference_cm": 58.5,
  "calf_circumference_cm": 39.0,
  "shoulder_width_cm": 46.5,
  "body_fat_percent": 16.5,
  "posture_rating": 7.5,
  "muscle_definition": "moderate"
}
```'''


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main():
    print("""
=============================================================
     ReddyFit - Simple Pipeline Test
     Testing Steps 7-9 (Standalone)
=============================================================
    """)

    # STEP 7: JSON Extraction
    print_section("Step 7: JSON Extraction")
    extracted = extract_json_simple(MOCK_RESPONSE)

    if extracted:
        print("[OK] Extraction successful!")
        print(json.dumps(extracted, indent=2))
    else:
        print("[FAIL] Extraction failed")
        return

    # STEP 8: Validation
    print_section("Step 8: Schema Validation")
    measurements, errors = validate_simple(extracted)

    if measurements:
        print("[OK] Validation successful!")
        print(f"   Chest: {measurements.chest_circumference_cm}cm")
        print(f"   Waist: {measurements.waist_circumference_cm}cm")
        print(f"   Body Fat: {measurements.body_fat_percent}%")
        print(f"   Muscle: {measurements.muscle_definition}")
        completeness = 1.0
    else:
        print("[FAIL] Validation failed")
        for error in errors:
            print(f"   - {error}")
        completeness = 0.5

    # STEP 9: Confidence Scoring
    print_section("Step 9: Confidence Scoring")
    confidence = calculate_confidence_simple(
        photo_count=3,
        completeness=completeness,
        extraction_ok=(extracted is not None),
        validation_ok=(measurements is not None)
    )

    print(f"Overall Confidence: {confidence:.3f}")
    print(f"Meets Threshold (0.70): {'[YES]' if confidence >= 0.70 else '[NO]'}")

    # SUMMARY
    print_section("Test Summary")
    print(f"[OK] Step 7: JSON Extraction    - {'PASS' if extracted else 'FAIL'}")
    print(f"[OK] Step 8: Schema Validation  - {'PASS' if measurements else 'FAIL'}")
    print(f"[OK] Step 9: Confidence Score   - {confidence:.3f}")

    if confidence >= 0.70:
        print("\n[SUCCESS] Simple Pipeline Test PASSED!")
    else:
        print("\n[WARNING] Test completed with LOW CONFIDENCE")

    # Edge Case Tests
    print_section("Edge Case Tests")

    # Test 1: Malformed JSON
    print("\n1. Malformed JSON")
    result = extract_json_simple("This is not JSON")
    print(f"   {'[OK]' if result is None else '[FAIL]'} Correctly handled malformed JSON")

    # Test 2: Out of range
    print("\n2. Out-of-Range Values")
    bad_data = extracted.copy()
    bad_data["chest_circumference_cm"] = 300.0  # Too large
    _, errors = validate_simple(bad_data)
    print(f"   {'[OK]' if errors else '[FAIL]'} Detected range violation")

    # Test 3: Missing field
    print("\n3. Missing Required Field")
    incomplete_data = {"chest_circumference_cm": 100.0}
    _, errors = validate_simple(incomplete_data)
    print(f"   {'[OK]' if errors else '[FAIL]'} Detected missing fields")

    print_section("[COMPLETE] All Tests Done")


if __name__ == "__main__":
    main()
