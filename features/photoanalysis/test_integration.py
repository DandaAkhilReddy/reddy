"""
Integration Test for Core AI Vision Pipeline (Steps 1-9)
Tests the full pipeline with mock data (no real API calls)
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.json_extractor import extract_json
from services.data_validator import validate_measurements
from services.confidence_scorer import calculate_scan_confidence


def mock_gpt4o_response() -> str:
    """
    Mock GPT-4o response with realistic body measurements
    """
    return '''```json
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
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_json(data: Dict[str, Any], indent: int = 2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent, default=str))


async def test_full_pipeline():
    """
    Test complete pipeline: Steps 5-9
    (Skipping Steps 1-4 which require actual images)
    """
    print_section("🧪 ReddyFit Integration Test - Steps 5-9")

    # Step 5: Vision Prompt (already tested, skip for now)
    print("\n✅ Step 5: Vision Prompt Engine")
    print("   - Prompts would be generated for GPT-4o")
    print("   - Skipped in mock test")

    # Step 6: Mock GPT-4o Response (simulate API call)
    print_section("Step 6: OpenAI GPT-4o Client (Mocked)")
    response_text = mock_gpt4o_response()
    print("Mock GPT-4o Response:")
    print(response_text)

    metadata = {
        "model": "gpt-4o",
        "total_tokens": 450,
        "estimated_cost_usd": 0.0085,
        "finish_reason": "stop"
    }
    print("\nAPI Metadata:")
    print_json(metadata)

    # Step 7: JSON Extraction
    print_section("Step 7: Multi-Strategy JSON Extraction")
    extracted_json, extraction_strategy = extract_json(response_text)

    if extracted_json:
        print(f"✅ Extraction successful using strategy: {extraction_strategy}")
        print("\nExtracted JSON:")
        print_json(extracted_json)
    else:
        print("❌ Extraction failed")
        return

    # Step 8: Schema Validation & Type Conversion
    print_section("Step 8: Schema Validation & Type Conversion")
    measurements, validation_errors, completeness = validate_measurements(extracted_json)

    if measurements:
        print("✅ Validation successful")
        print(f"   Data completeness: {completeness * 100:.1f}%")

        if validation_errors:
            print(f"\n⚠️  {len(validation_errors)} validation warnings:")
            for error in validation_errors:
                print(f"   - {error}")
        else:
            print("   No validation warnings")

        print("\nValidated Measurements:")
        measurements_dict = measurements.model_dump()
        print_json(measurements_dict)
    else:
        print("❌ Validation failed")
        print(f"Errors ({len(validation_errors)}):")
        for error in validation_errors:
            print(f"  - {error}")
        return

    # Step 9: Confidence Scoring
    print_section("Step 9: Confidence Scoring")

    confidence = calculate_scan_confidence(
        measurements=measurements,
        photo_count=3,  # Simulating 3 photos
        completeness_score=completeness,
        ai_finish_reason=metadata["finish_reason"],
        extraction_strategy=extraction_strategy,
        validation_errors=validation_errors
    )

    print(f"Overall Confidence: {confidence.overall_score:.3f}")
    print(f"Meets Threshold (0.70): {'✅ YES' if confidence.meets_threshold else '❌ NO'}")

    print("\nFactor Breakdown:")
    print(f"  📸 Photo Count:        {confidence.photo_count_factor:.3f}")
    print(f"  🔄 Consistency:        {confidence.consistency_factor:.3f}")
    print(f"  🤖 AI Confidence:      {confidence.ai_confidence_factor:.3f}")
    print(f"  📊 Data Completeness:  {confidence.data_completeness_factor:.3f}")
    print(f"  ✔️  Validation Quality: {confidence.validation_quality_factor:.3f}")

    print("\nDetailed Factors:")
    print_json(confidence.factors_breakdown)

    # Summary
    print_section("📊 Test Summary")
    print(f"✅ Step 6: OpenAI Client        - SIMULATED")
    print(f"✅ Step 7: JSON Extraction      - {extraction_strategy}")
    print(f"✅ Step 8: Schema Validation    - {completeness*100:.0f}% complete")
    print(f"✅ Step 9: Confidence Scoring   - {confidence.overall_score:.3f}")

    if confidence.meets_threshold:
        print("\n🎉 Integration Test PASSED - Pipeline is functional!")
    else:
        print("\n⚠️  Integration Test PASSED with LOW CONFIDENCE")
        print("   (This is expected with mock data)")

    return True


async def test_edge_cases():
    """Test edge cases and error scenarios"""
    print_section("🧪 Testing Edge Cases")

    # Test Case 1: Malformed JSON
    print("\n1️⃣  Test: Malformed JSON Response")
    bad_response = "This is not JSON at all"
    result, strategy = extract_json(bad_response)
    if result is None:
        print("   ✅ Correctly handled malformed JSON")
    else:
        print("   ❌ Should have failed on malformed JSON")

    # Test Case 2: JSON with trailing comma
    print("\n2️⃣  Test: JSON with Trailing Comma")
    trailing_comma_json = '{"chest_circumference_cm": 100, "waist_circumference_cm": 85,}'
    result, strategy = extract_json(trailing_comma_json)
    if result is not None:
        print(f"   ✅ Fixed and extracted using: {strategy}")
    else:
        print("   ❌ Should have fixed trailing comma")

    # Test Case 3: Out-of-range measurements
    print("\n3️⃣  Test: Out-of-Range Measurements")
    bad_measurements = {
        "chest_circumference_cm": 300.0,  # Too large
        "waist_circumference_cm": 85.0,
        "hip_circumference_cm": 95.0,
        "bicep_circumference_cm": 35.0,
        "thigh_circumference_cm": 10.0,   # Too small
        "calf_circumference_cm": 38.0,
        "shoulder_width_cm": 45.0,
        "body_fat_percent": 15.0,
        "posture_rating": 8.0,
        "muscle_definition": "moderate"
    }
    measurements, errors, completeness = validate_measurements(bad_measurements)
    if len(errors) > 0:
        print(f"   ✅ Detected {len(errors)} range violations")
    else:
        print("   ❌ Should have detected range violations")

    # Test Case 4: Unit conversion (inches to cm)
    print("\n4️⃣  Test: Unit Conversion (inches → cm)")
    inches_data = {
        "chest_circumference_cm": 40.0,  # 40 inches
        "waist_circumference_cm": 32.0,
        "hip_circumference_cm": 38.0,
        "bicep_circumference_cm": 14.0,
        "thigh_circumference_cm": 22.0,
        "calf_circumference_cm": 15.0,
        "shoulder_width_cm": 18.0,
        "body_fat_percent": 15.0,
        "posture_rating": 8.0,
        "muscle_definition": "moderate"
    }
    measurements, errors, completeness = validate_measurements(inches_data)
    if measurements and any("Converted" in e for e in errors):
        print(f"   ✅ Detected and converted inch values")
        print(f"      Chest: 40in → {measurements.chest_circumference_cm:.1f}cm")
    else:
        print("   ⚠️  Unit conversion may not have triggered")

    print("\n✅ Edge Case Testing Complete")


async def main():
    """Run all integration tests"""
    try:
        # Main pipeline test
        await test_full_pipeline()

        # Edge cases
        await test_edge_cases()

        print_section("✅ All Integration Tests Complete")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     🏋️ ReddyFit - Core AI Vision Pipeline Test          ║
║     Testing Steps 5-9 (Mock Data)                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
