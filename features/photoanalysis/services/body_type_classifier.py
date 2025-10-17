"""
Body Type Classifier (Step 14)
Classifies body type and calculates aesthetic score
"""
from typing import Tuple
from ..models.schemas import BodyType, BodyMeasurements, BodyRatios, AestheticScore


def classify_body_type(
    ratios: BodyRatios,
    measurements: BodyMeasurements
) -> Tuple[BodyType, float]:
    """
    Classify body type based on proportions

    Classification logic:
    - V-Taper: Broad shoulders, narrow waist (athletic)
    - Classic: Well-proportioned, balanced ratios
    - Rectangular: Straight body lines, minimal taper
    - Apple: Weight concentrated in midsection
    - Pear: Weight concentrated in lower body
    - Balanced: All ratios within ideal ranges

    Args:
        ratios: BodyRatios object
        measurements: BodyMeasurements object

    Returns:
        Tuple of (BodyType, confidence_score)
    """
    stw = ratios.shoulder_to_waist_ratio
    whr = ratios.waist_to_hip_ratio
    ctw = ratios.chest_to_waist_ratio
    symmetry = ratios.symmetry_score

    # Classification rules with confidence scoring
    classifications = []

    # V-Taper classification
    if stw >= 1.4 and ctw >= 1.3:
        if stw >= 1.6:
            classifications.append((BodyType.VTAPER, 0.95))  # Very confident
        else:
            classifications.append((BodyType.VTAPER, 0.80))

    # Classic/Balanced classification
    if 1.35 <= stw <= 1.55 and symmetry >= 80:
        classifications.append((BodyType.CLASSIC, 0.85))

    # Balanced (all ratios ideal)
    if 1.4 <= stw <= 1.7 and 0.85 <= whr <= 0.95 and symmetry >= 85:
        classifications.append((BodyType.BALANCED, 0.90))

    # Rectangular (minimal taper)
    if stw < 1.2 and abs(whr - 1.0) < 0.1:
        classifications.append((BodyType.RECTANGULAR, 0.85))

    # Apple (weight in midsection)
    if whr > 0.95 and measurements.body_fat_percent > 20:
        classifications.append((BodyType.APPLE, 0.80))

    # Pear (weight in lower body)
    if whr < 0.85 and measurements.hip_circumference_cm > measurements.chest_circumference_cm:
        classifications.append((BodyType.PEAR, 0.75))

    # Return highest confidence classification
    if classifications:
        # Sort by confidence (descending)
        classifications.sort(key=lambda x: x[1], reverse=True)
        return classifications[0]

    # Default to Rectangular if no clear classification
    return (BodyType.RECTANGULAR, 0.60)


def calculate_golden_ratio_score(ratios: BodyRatios) -> float:
    """
    Score based on proximity to golden ratio

    Golden ratio is 1.618. Perfect score if Adonis Index = 1.618.
    Max score: 40 points.

    Args:
        ratios: BodyRatios object

    Returns:
        Score 0-40
    """
    GOLDEN_RATIO = 1.618
    adonis_index = ratios.adonis_index

    # Calculate deviation from golden ratio
    deviation = abs(adonis_index - GOLDEN_RATIO)

    # Perfect score if within 0.05 of golden ratio
    if deviation <= 0.05:
        return 40.0

    # Linear decay: 0.5 deviation = 0 points
    if deviation >= 0.5:
        return 0.0

    score = 40 * (1 - (deviation / 0.5))

    return round(score, 1)


def calculate_symmetry_component_score(ratios: BodyRatios) -> float:
    """
    Score based on overall body symmetry

    Max score: 30 points.

    Args:
        ratios: BodyRatios object

    Returns:
        Score 0-30
    """
    # Symmetry score is 0-100, convert to 0-30
    symmetry_score = ratios.symmetry_score
    component_score = (symmetry_score / 100) * 30

    return round(component_score, 1)


def calculate_composition_score(measurements: BodyMeasurements) -> float:
    """
    Score based on body composition (body fat percentage)

    Max score: 20 points.

    Ideal body fat:
    - Males: 10-15%
    - Females: 18-24%

    Args:
        measurements: BodyMeasurements object

    Returns:
        Score 0-20
    """
    bf_percent = measurements.body_fat_percent

    # Scoring based on body fat ranges
    # For now, use male standards (can be adjusted with gender parameter)

    if 10 <= bf_percent <= 15:
        # Ideal range
        score = 20.0
    elif 8 <= bf_percent < 10 or 15 < bf_percent <= 18:
        # Athletic range
        score = 18.0
    elif 5 <= bf_percent < 8 or 18 < bf_percent <= 22:
        # Fitness range
        score = 15.0
    elif bf_percent < 5 or bf_percent > 30:
        # Too low or too high
        score = 5.0
    else:
        # Average range
        score = 12.0

    return score


def calculate_posture_score(posture_rating: float) -> float:
    """
    Score based on posture rating

    Max score: 10 points.

    Args:
        posture_rating: Posture rating from 0-10

    Returns:
        Score 0-10
    """
    # Posture rating is already 0-10, just use it directly
    return round(posture_rating, 1)


def calculate_aesthetic_score(
    ratios: BodyRatios,
    body_type: BodyType,
    measurements: BodyMeasurements,
    body_type_confidence: float
) -> AestheticScore:
    """
    Calculate comprehensive aesthetic score

    Components:
    - Golden Ratio Score: 40% weight (0-40 points)
    - Symmetry Score: 30% weight (0-30 points)
    - Composition Score: 20% weight (0-20 points)
    - Posture Score: 10% weight (0-10 points)

    Total: 0-100 points

    Args:
        ratios: BodyRatios object
        body_type: Classified body type
        measurements: BodyMeasurements object
        body_type_confidence: Confidence in body type classification

    Returns:
        AestheticScore object
    """
    # Calculate component scores
    golden_ratio_score = calculate_golden_ratio_score(ratios)
    symmetry_score = calculate_symmetry_component_score(ratios)
    composition_score = calculate_composition_score(measurements)
    posture_score = calculate_posture_score(measurements.posture_rating)

    # Calculate overall score (sum of components)
    overall_score = (
        golden_ratio_score +
        symmetry_score +
        composition_score +
        posture_score
    )

    # Create AestheticScore object
    aesthetic_score = AestheticScore(
        overall_score=round(overall_score, 1),
        golden_ratio_score=golden_ratio_score,
        symmetry_score=symmetry_score,
        composition_score=composition_score,
        posture_score=posture_score,
        body_type=body_type,
        body_type_confidence=body_type_confidence
    )

    return aesthetic_score


def get_body_type_description(body_type: BodyType) -> str:
    """
    Get detailed description of body type

    Args:
        body_type: BodyType enum

    Returns:
        Description string
    """
    descriptions = {
        BodyType.VTAPER: (
            "V-Taper physique: Characterized by broad shoulders and a narrow waist, "
            "creating the classic athletic 'V' shape. This body type is often associated "
            "with excellent upper body development and aesthetic proportions."
        ),
        BodyType.CLASSIC: (
            "Classic physique: Well-proportioned with balanced muscle development "
            "across all body parts. This timeless physique represents symmetry and "
            "harmonious proportions."
        ),
        BodyType.RECTANGULAR: (
            "Rectangular physique: Characterized by relatively straight body lines "
            "with minimal taper from shoulders to waist. This body type may benefit "
            "from targeted shoulder and back development to create more taper."
        ),
        BodyType.APPLE: (
            "Apple shape: Weight tends to be concentrated in the midsection. "
            "This body type may benefit from core training and body fat reduction "
            "to improve proportions."
        ),
        BodyType.PEAR: (
            "Pear shape: Weight is primarily stored in the lower body (hips and thighs). "
            "This body type often has a narrower upper body relative to the lower body."
        ),
        BodyType.BALANCED: (
            "Balanced physique: Exceptional overall proportions with all body ratios "
            "within ideal ranges. This represents excellent symmetry and development "
            "across all muscle groups."
        ),
    }

    return descriptions.get(body_type, "Body type description not available.")


def get_body_type_recommendations(
    body_type: BodyType,
    ratios: BodyRatios,
    measurements: BodyMeasurements
) -> list:
    """
    Get training recommendations based on body type

    Args:
        body_type: Classified body type
        ratios: BodyRatios object
        measurements: BodyMeasurements object

    Returns:
        List of recommendations
    """
    recommendations = []

    if body_type == BodyType.VTAPER:
        recommendations.append("Maintain shoulder width with overhead press and lateral raises")
        recommendations.append("Keep waist tight with core training and diet control")
        recommendations.append("Balance with leg development to avoid top-heavy appearance")

    elif body_type == BodyType.CLASSIC:
        recommendations.append("Focus on progressive overload across all muscle groups")
        recommendations.append("Maintain balanced training split (push/pull/legs)")
        recommendations.append("Fine-tune proportions with targeted isolation work")

    elif body_type == BodyType.RECTANGULAR:
        recommendations.append("Prioritize shoulder and back width (lateral raises, pull-ups)")
        recommendations.append("Build upper chest (incline press)")
        recommendations.append("Tighten waist through fat loss and core training")

    elif body_type == BodyType.APPLE:
        recommendations.append("Focus on calorie deficit for fat loss")
        recommendations.append("High-protein diet to preserve muscle")
        recommendations.append("Increase cardio and HIIT training")
        recommendations.append("Build shoulders to improve upper body proportions")

    elif body_type == BodyType.PEAR:
        recommendations.append("Build upper body (chest, shoulders, back)")
        recommendations.append("Maintain leg development without overemphasis")
        recommendations.append("Focus on creating upper body width")

    elif body_type == BodyType.BALANCED:
        recommendations.append("Maintain current balanced approach")
        recommendations.append("Focus on strength progression")
        recommendations.append("Fine-tune any minor weak points")

    # Add body fat specific recommendations
    bf_percent = measurements.body_fat_percent
    if bf_percent > 20:
        recommendations.append("Reduce body fat to reveal muscle definition")
    elif bf_percent < 10:
        recommendations.append("Consider slight bulk to build more muscle mass")

    return recommendations


def calculate_improvement_potential(
    current_score: float,
    ratios: BodyRatios,
    measurements: BodyMeasurements
) -> dict:
    """
    Estimate improvement potential

    Args:
        current_score: Current aesthetic score
        ratios: BodyRatios object
        measurements: BodyMeasurements object

    Returns:
        Dictionary with improvement estimates
    """
    potential = {}

    # Estimate potential score if improvements are made
    estimated_potential = current_score

    # Body fat optimization potential
    bf_percent = measurements.body_fat_percent
    if bf_percent > 15:
        # Could gain 5-10 points by reducing body fat to 12%
        potential_bf_improvement = min(10, (bf_percent - 12) * 0.5)
        estimated_potential += potential_bf_improvement
        potential["body_fat_reduction"] = f"+{potential_bf_improvement:.1f} points"

    # Shoulder development potential
    stw = ratios.shoulder_to_waist_ratio
    if stw < 1.5:
        # Could gain 3-8 points by improving shoulder:waist ratio
        potential_shoulder_improvement = min(8, (1.6 - stw) * 10)
        estimated_potential += potential_shoulder_improvement
        potential["shoulder_development"] = f"+{potential_shoulder_improvement:.1f} points"

    # Symmetry improvement potential
    if ratios.symmetry_score < 80:
        # Could gain 2-5 points by improving symmetry
        potential_symmetry_improvement = (80 - ratios.symmetry_score) * 0.1
        estimated_potential += potential_symmetry_improvement
        potential["symmetry_improvement"] = f"+{potential_symmetry_improvement:.1f} points"

    # Cap at 95 (100 is near impossible)
    estimated_potential = min(95, estimated_potential)

    potential["current_score"] = current_score
    potential["estimated_potential"] = round(estimated_potential, 1)
    potential["improvement_range"] = f"{current_score:.1f} → {estimated_potential:.1f}"

    return potential
