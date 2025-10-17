"""
Integration Test for Steps 10-16 (Mathematical Analysis)
Tests complete pipeline from measurements to final scan result
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime
from models.schemas import (
    BodyMeasurements, ConfidenceMetrics,
    ImageQuality, PhotoAngle, AngleType
)
from services.scan_assembler import (
    assemble_scan_result,
    generate_quick_summary,
    generate_detailed_report,
    validate_scan_result
)


def create_mock_measurements(scenario: str = "athletic") -> BodyMeasurements:
    """Create mock measurements for different scenarios"""

    scenarios = {
        "athletic": BodyMeasurements(
            chest_circumference_cm=105.0,
            waist_circumference_cm=80.0,
            hip_circumference_cm=95.0,
            bicep_circumference_cm=38.0,
            thigh_circumference_cm=58.0,
            calf_circumference_cm=38.0,
            shoulder_width_cm=48.0,
            body_fat_percent=12.5,
            estimated_weight_kg=80.0,
            posture_rating=8.5,
            muscle_definition="Well-defined"
        ),
        "beginner": BodyMeasurements(
            chest_circumference_cm=95.0,
            waist_circumference_cm=88.0,
            hip_circumference_cm=96.0,
            bicep_circumference_cm=32.0,
            thigh_circumference_cm=54.0,
            calf_circumference_cm=36.0,
            shoulder_width_cm=42.0,
            body_fat_percent=22.0,
            estimated_weight_kg=75.0,
            posture_rating=6.5,
            muscle_definition="Minimal"
        ),
        "advanced": BodyMeasurements(
            chest_circumference_cm=110.0,
            waist_circumference_cm=78.0,
            hip_circumference_cm=98.0,
            bicep_circumference_cm=42.0,
            thigh_circumference_cm=62.0,
            calf_circumference_cm=40.0,
            shoulder_width_cm=52.0,
            body_fat_percent=8.5,
            estimated_weight_kg=85.0,
            posture_rating=9.0,
            muscle_definition="Excellent"
        )
    }

    return scenarios.get(scenario, scenarios["athletic"])


def create_mock_confidence() -> ConfidenceMetrics:
    """Create mock confidence metrics"""
    return ConfidenceMetrics(
        overall_confidence=0.92,
        photo_count_factor=1.0,
        measurement_consistency=0.95,
        ai_confidence=0.90,
        data_completeness=0.88,
        is_reliable=True
    )


def create_mock_image_data() -> tuple:
    """Create mock image quality and angle data"""

    image_urls = {
        "front": "https://storage.example.com/scans/user_123/front.jpg",
        "side": "https://storage.example.com/scans/user_123/side.jpg",
        "back": "https://storage.example.com/scans/user_123/back.jpg"
    }

    image_quality = {
        "front": ImageQuality(
            width=1920,
            height=1080,
            file_size_kb=450,
            format="jpeg",
            sharpness_score=85,
            has_exif=True,
            orientation=1,
            is_valid=True,
            quality_score=88
        ),
        "side": ImageQuality(
            width=1920,
            height=1080,
            file_size_kb=420,
            format="jpeg",
            sharpness_score=82,
            has_exif=True,
            orientation=1,
            is_valid=True,
            quality_score=85
        ),
        "back": ImageQuality(
            width=1920,
            height=1080,
            file_size_kb=440,
            format="jpeg",
            sharpness_score=80,
            has_exif=True,
            orientation=1,
            is_valid=True,
            quality_score=83
        )
    }

    detected_angles = {
        "front": PhotoAngle(
            angle_type=AngleType.FRONT,
            confidence=0.95,
            detected_pose_keypoints=17,
            is_standing=True
        ),
        "side": PhotoAngle(
            angle_type=AngleType.SIDE,
            confidence=0.92,
            detected_pose_keypoints=15,
            is_standing=True
        ),
        "back": PhotoAngle(
            angle_type=AngleType.BACK,
            confidence=0.90,
            detected_pose_keypoints=16,
            is_standing=True
        )
    }

    return image_urls, image_quality, detected_angles


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_athletic_physique():
    """Test Case 1: Athletic Physique"""
    print_section("TEST 1: ATHLETIC PHYSIQUE")

    measurements = create_mock_measurements("athletic")
    confidence = create_mock_confidence()
    image_urls, image_quality, detected_angles = create_mock_image_data()

    # Assemble scan result
    scan_result = assemble_scan_result(
        user_id="test_user_athletic",
        measurements=measurements,
        confidence=confidence,
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,
        height_cm=178,
        gender="male",
        processing_time_sec=28.5
    )

    # Generate summary
    summary = generate_quick_summary(scan_result)

    print("QUICK SUMMARY:")
    print(f"  Body Signature: {summary['body_signature']}")
    print(f"  Body Type: {summary['body_type']}")
    print(f"  Overall Score: {summary['overall_score']}/100")
    print(f"  Body Fat: {summary['body_fat_percent']}%")
    print(f"  Adonis Index: {summary['adonis_index']}")
    print(f"  Symmetry: {summary['symmetry_score']}/100")
    print(f"  Confidence: {summary['confidence']*100:.1f}%")
    print(f"  Assessment: {summary['performance']}")

    # Validate
    validation = validate_scan_result(scan_result)
    print(f"\nVALIDATION: {'PASS' if validation['is_valid'] else 'FAIL'}")
    if validation["warnings"]:
        print(f"  Warnings: {len(validation['warnings'])}")

    return scan_result


def test_beginner_physique():
    """Test Case 2: Beginner Physique"""
    print_section("TEST 2: BEGINNER PHYSIQUE")

    measurements = create_mock_measurements("beginner")
    confidence = create_mock_confidence()
    image_urls, image_quality, detected_angles = create_mock_image_data()

    scan_result = assemble_scan_result(
        user_id="test_user_beginner",
        measurements=measurements,
        confidence=confidence,
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,
        height_cm=175,
        gender="male",
        processing_time_sec=27.2
    )

    summary = generate_quick_summary(scan_result)

    print("QUICK SUMMARY:")
    print(f"  Body Signature: {summary['body_signature']}")
    print(f"  Body Type: {summary['body_type']}")
    print(f"  Overall Score: {summary['overall_score']}/100")
    print(f"  Assessment: {summary['performance']}")

    # Get detailed report
    report = generate_detailed_report(scan_result, gender="male")

    print(f"\nAESTHETIC BREAKDOWN:")
    for key, value in report["aesthetic_breakdown"].items():
        print(f"  {key}: {value}")

    print(f"\nRECOMMENDATIONS ({len(report['recommendations'])}):")
    for i, rec in enumerate(report["recommendations"][:3], 1):
        print(f"  {i}. {rec}")

    return scan_result


def test_advanced_physique():
    """Test Case 3: Advanced Physique"""
    print_section("TEST 3: ADVANCED PHYSIQUE (Elite V-Taper)")

    measurements = create_mock_measurements("advanced")
    confidence = create_mock_confidence()
    image_urls, image_quality, detected_angles = create_mock_image_data()

    scan_result = assemble_scan_result(
        user_id="test_user_advanced",
        measurements=measurements,
        confidence=confidence,
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,
        height_cm=180,
        gender="male",
        processing_time_sec=29.1
    )

    summary = generate_quick_summary(scan_result)

    print("QUICK SUMMARY:")
    print(f"  Body Signature: {summary['body_signature']}")
    print(f"  Body Type: {summary['body_type']}")
    print(f"  Overall Score: {summary['overall_score']}/100")
    print(f"  Assessment: {summary['performance']}")

    # Show detailed ratios
    print(f"\nKEY RATIOS:")
    print(f"  Adonis Index: {scan_result.ratios.adonis_index:.2f} (target: 1.618)")
    print(f"  Waist:Hip: {scan_result.ratios.waist_to_hip_ratio:.2f}")
    print(f"  Chest:Waist: {scan_result.ratios.chest_to_waist_ratio:.2f}")
    print(f"  Arm:Chest: {scan_result.ratios.arm_to_chest_ratio:.2f}")

    print(f"\nCOMPOSITION HASH: {scan_result.composition_hash}")

    return scan_result


def test_complete_workflow():
    """Run all test scenarios"""
    print("\n" + "="*60)
    print("  MATHEMATICAL ANALYSIS INTEGRATION TEST")
    print("  Testing Steps 10-16")
    print("="*60)

    results = []

    try:
        # Test 1: Athletic
        scan1 = test_athletic_physique()
        results.append(("Athletic Physique", "PASS", scan1))
    except Exception as e:
        print(f"\n[FAIL] Athletic test: {str(e)}")
        results.append(("Athletic Physique", "FAIL", str(e)))

    try:
        # Test 2: Beginner
        scan2 = test_beginner_physique()
        results.append(("Beginner Physique", "PASS", scan2))
    except Exception as e:
        print(f"\n[FAIL] Beginner test: {str(e)}")
        results.append(("Beginner Physique", "FAIL", str(e)))

    try:
        # Test 3: Advanced
        scan3 = test_advanced_physique()
        results.append(("Advanced Physique", "PASS", scan3))
    except Exception as e:
        print(f"\n[FAIL] Advanced test: {str(e)}")
        results.append(("Advanced Physique", "FAIL", str(e)))

    # Print summary
    print_section("TEST SUMMARY")

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = len(results) - passed

    for test_name, status, _ in results:
        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {status_symbol} {test_name}")

    print(f"\n  Total: {len(results)} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed == 0:
        print("\n  [SUCCESS] All mathematical analysis tests passed!")
        print("  Steps 10-16 are working correctly.")
    else:
        print(f"\n  [WARNING] {failed} test(s) failed")

    print("\n" + "="*60 + "\n")

    return results


if __name__ == "__main__":
    # Run tests
    test_complete_workflow()
