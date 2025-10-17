"""
Scan Result Assembler (Step 16)
Orchestrates all mathematical analysis steps and assembles complete scan result
"""
from typing import Dict, Optional
from datetime import datetime
import uuid

from ..models.schemas import (
    BodyMeasurements, BodyRatios, AestheticScore,
    ScanResult, ConfidenceMetrics, ImageQuality,
    PhotoAngle, WHOOPData
)

# Import all analysis services
from .ratio_calculator import calculate_all_body_ratios
from .symmetry_analyzer import detect_asymmetries, get_symmetry_recommendations
from .hash_generator import generate_composition_hash, validate_hash_uniqueness
from .body_type_classifier import (
    classify_body_type,
    calculate_aesthetic_score,
    get_body_type_recommendations
)
from .id_generator import generate_body_signature_id


def assemble_scan_result(
    user_id: str,
    measurements: BodyMeasurements,
    confidence: ConfidenceMetrics,
    image_urls: Dict[str, str],
    image_quality: Dict[str, ImageQuality],
    detected_angles: Dict[str, PhotoAngle],
    height_cm: Optional[float] = None,
    gender: Optional[str] = None,
    whoop_data: Optional[WHOOPData] = None,
    processing_time_sec: float = 0.0
) -> ScanResult:
    """
    Assemble complete scan result by running all mathematical analysis steps

    This function orchestrates Steps 10-15:
    - Step 10: Extract anthropometric measurements ✓ (implicit in measurements)
    - Step 11: Calculate body ratios & Adonis Index ✓
    - Step 12: Analyze symmetry ✓
    - Step 13: Generate composition hash ✓
    - Step 14: Classify body type & aesthetic score ✓
    - Step 15: Generate unique body signature ID ✓

    Args:
        user_id: User identifier
        measurements: BodyMeasurements from AI analysis
        confidence: ConfidenceMetrics from Step 9
        image_urls: Dictionary of {angle: url}
        image_quality: Dictionary of {angle: ImageQuality}
        detected_angles: Dictionary of {angle: PhotoAngle}
        height_cm: User height (optional, for additional calculations)
        gender: User gender (optional, affects ideal ranges)
        whoop_data: WHOOP data (optional)
        processing_time_sec: Total processing time

    Returns:
        Complete ScanResult object
    """
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())

    # STEP 11: Calculate all body ratios
    print("[Step 11] Calculating body ratios...")
    body_ratios = calculate_all_body_ratios(measurements, gender)

    # STEP 12: Analyze symmetry
    print("[Step 12] Analyzing symmetry...")
    asymmetries = detect_asymmetries(measurements, body_ratios, gender)

    # STEP 13: Generate composition hash
    print("[Step 13] Generating composition hash...")
    composition_hash = generate_composition_hash(measurements, body_ratios)

    # Validate hash uniqueness (in production, would check against Firestore)
    # For now, just validate format
    is_unique = validate_hash_uniqueness(composition_hash, user_id, existing_scans=None)
    if not is_unique:
        # In production, would handle collision (add salt, retry, etc.)
        print(f"[WARNING] Hash collision detected: {composition_hash}")

    # STEP 14: Classify body type and calculate aesthetic score
    print("[Step 14] Classifying body type...")
    body_type, body_type_confidence = classify_body_type(body_ratios, measurements)

    print("[Step 14] Calculating aesthetic score...")
    aesthetic_score = calculate_aesthetic_score(
        body_ratios,
        body_type,
        measurements,
        body_type_confidence
    )

    # STEP 15: Generate unique body signature ID
    print("[Step 15] Generating body signature ID...")
    body_signature_id = generate_body_signature_id(
        body_type,
        measurements.body_fat_percent,
        composition_hash,
        body_ratios.adonis_index
    )

    # STEP 16: Assemble complete scan result
    print("[Step 16] Assembling scan result...")

    scan_result = ScanResult(
        # Identification
        scan_id=scan_id,
        body_signature_id=body_signature_id,
        user_id=user_id,
        timestamp=datetime.now(),

        # Image references
        image_urls=image_urls,
        image_quality=image_quality,
        detected_angles=detected_angles,

        # Measurements & Analysis (Steps 10-14)
        measurements=measurements,
        ratios=body_ratios,
        aesthetic_score=aesthetic_score,
        composition_hash=composition_hash,

        # External Data
        whoop_data=whoop_data,

        # Confidence & Metadata
        confidence=confidence,
        processing_time_sec=processing_time_sec,
        api_version="2.0"
    )

    print(f"[COMPLETE] Scan assembled: {body_signature_id}")

    return scan_result


def generate_quick_summary(scan_result: ScanResult) -> Dict[str, any]:
    """
    Generate quick summary of scan results

    Args:
        scan_result: Complete ScanResult object

    Returns:
        Dictionary with key highlights
    """
    summary = {
        "body_signature": scan_result.body_signature_id,
        "body_type": scan_result.aesthetic_score.body_type.value,
        "overall_score": scan_result.aesthetic_score.overall_score,
        "body_fat_percent": scan_result.measurements.body_fat_percent,
        "adonis_index": scan_result.ratios.adonis_index,
        "symmetry_score": scan_result.ratios.symmetry_score,
        "confidence": scan_result.confidence.overall_confidence,
        "is_reliable": scan_result.confidence.is_reliable
    }

    # Add quick insights
    if scan_result.aesthetic_score.overall_score >= 80:
        summary["performance"] = "Excellent physique"
    elif scan_result.aesthetic_score.overall_score >= 70:
        summary["performance"] = "Good physique"
    elif scan_result.aesthetic_score.overall_score >= 60:
        summary["performance"] = "Average physique"
    else:
        summary["performance"] = "Room for improvement"

    return summary


def generate_detailed_report(scan_result: ScanResult, gender: Optional[str] = None) -> Dict[str, any]:
    """
    Generate detailed analysis report

    Args:
        scan_result: Complete ScanResult object
        gender: User gender (optional)

    Returns:
        Comprehensive report dictionary
    """
    # Extract components
    measurements = scan_result.measurements
    ratios = scan_result.ratios
    aesthetic = scan_result.aesthetic_score

    # Detect asymmetries
    asymmetries = detect_asymmetries(measurements, ratios, gender)

    # Get recommendations
    body_type_recs = get_body_type_recommendations(
        aesthetic.body_type,
        ratios,
        measurements
    )

    symmetry_recs = get_symmetry_recommendations(asymmetries, ratios)

    # Combine recommendations
    all_recommendations = list(set(body_type_recs + symmetry_recs))

    report = {
        "summary": generate_quick_summary(scan_result),

        "body_composition": {
            "body_fat_percent": measurements.body_fat_percent,
            "estimated_weight_kg": measurements.estimated_weight_kg,
            "posture_rating": f"{measurements.posture_rating}/10"
        },

        "measurements": {
            "chest_cm": measurements.chest_circumference_cm,
            "waist_cm": measurements.waist_circumference_cm,
            "hips_cm": measurements.hip_circumference_cm,
            "bicep_cm": measurements.bicep_circumference_cm,
            "thigh_cm": measurements.thigh_circumference_cm
        },

        "key_ratios": {
            "adonis_index": ratios.adonis_index,
            "waist_to_hip": ratios.waist_to_hip_ratio,
            "chest_to_waist": ratios.chest_to_waist_ratio,
            "arm_to_chest": ratios.arm_to_chest_ratio
        },

        "aesthetic_breakdown": {
            "overall_score": aesthetic.overall_score,
            "golden_ratio_score": f"{aesthetic.golden_ratio_score}/40",
            "symmetry_score": f"{aesthetic.symmetry_score}/30",
            "composition_score": f"{aesthetic.composition_score}/20",
            "posture_score": f"{aesthetic.posture_score}/10"
        },

        "body_type": {
            "classification": aesthetic.body_type.value,
            "confidence": f"{aesthetic.body_type_confidence*100:.1f}%"
        },

        "asymmetries": asymmetries,

        "recommendations": all_recommendations,

        "confidence": {
            "overall": f"{scan_result.confidence.overall_confidence*100:.1f}%",
            "is_reliable": scan_result.confidence.is_reliable,
            "photo_count": scan_result.confidence.photo_count_factor,
            "data_completeness": scan_result.confidence.data_completeness
        }
    }

    return report


def compare_scans(
    current_scan: ScanResult,
    previous_scan: ScanResult
) -> Dict[str, any]:
    """
    Compare two scans to show progress

    Args:
        current_scan: Latest scan result
        previous_scan: Previous scan result

    Returns:
        Dictionary with comparison results
    """
    # Calculate changes
    bf_change = (
        current_scan.measurements.body_fat_percent -
        previous_scan.measurements.body_fat_percent
    )

    score_change = (
        current_scan.aesthetic_score.overall_score -
        previous_scan.aesthetic_score.overall_score
    )

    adonis_change = (
        current_scan.ratios.adonis_index -
        previous_scan.ratios.adonis_index
    )

    symmetry_change = (
        current_scan.ratios.symmetry_score -
        previous_scan.ratios.symmetry_score
    )

    # Time difference
    time_diff = current_scan.timestamp - previous_scan.timestamp
    days_apart = time_diff.days

    comparison = {
        "time_between_scans_days": days_apart,

        "changes": {
            "body_fat_change_percent": round(bf_change, 1),
            "aesthetic_score_change": round(score_change, 1),
            "adonis_index_change": round(adonis_change, 2),
            "symmetry_score_change": round(symmetry_change, 1)
        },

        "body_type_changed": (
            current_scan.aesthetic_score.body_type !=
            previous_scan.aesthetic_score.body_type
        ),

        "progress_summary": []
    }

    # Generate progress summary
    if bf_change < -1:
        comparison["progress_summary"].append(
            f"Lost {abs(bf_change):.1f}% body fat - Excellent!"
        )
    elif bf_change > 1:
        comparison["progress_summary"].append(
            f"Gained {bf_change:.1f}% body fat"
        )

    if score_change > 5:
        comparison["progress_summary"].append(
            f"Aesthetic score improved by {score_change:.1f} points"
        )
    elif score_change < -5:
        comparison["progress_summary"].append(
            f"Aesthetic score decreased by {abs(score_change):.1f} points"
        )

    if adonis_change > 0.05:
        comparison["progress_summary"].append(
            "Improved shoulder:waist ratio (better V-taper)"
        )

    if not comparison["progress_summary"]:
        comparison["progress_summary"].append("Minimal changes - maintain consistency")

    return comparison


def validate_scan_result(scan_result: ScanResult) -> Dict[str, any]:
    """
    Validate that scan result is complete and accurate

    Args:
        scan_result: ScanResult to validate

    Returns:
        Dictionary with validation results
    """
    validation = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }

    # Check required fields
    if not scan_result.body_signature_id:
        validation["errors"].append("Missing body signature ID")
        validation["is_valid"] = False

    if not scan_result.composition_hash:
        validation["errors"].append("Missing composition hash")
        validation["is_valid"] = False

    # Check measurement ranges
    measurements = scan_result.measurements

    if measurements.waist_circumference_cm > measurements.chest_circumference_cm * 1.2:
        validation["warnings"].append("Waist larger than chest - may indicate measurement error")

    if measurements.body_fat_percent < 5 or measurements.body_fat_percent > 50:
        validation["warnings"].append("Body fat percentage seems extreme")

    # Check confidence
    if scan_result.confidence.overall_confidence < 0.7:
        validation["warnings"].append("Low confidence score - results may be unreliable")

    # Check aesthetic score components add up
    aesthetic = scan_result.aesthetic_score
    total = (
        aesthetic.golden_ratio_score +
        aesthetic.symmetry_score +
        aesthetic.composition_score +
        aesthetic.posture_score
    )

    if abs(total - aesthetic.overall_score) > 0.5:
        validation["errors"].append("Aesthetic score components don't sum correctly")
        validation["is_valid"] = False

    return validation
