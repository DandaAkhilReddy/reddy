"""
Symmetry Coefficient Analyzer (Step 12)
Analyzes body symmetry and identifies asymmetries
"""
from typing import List, Dict, Tuple
from ..models.schemas import BodyMeasurements, BodyRatios


def calculate_symmetry_score(body_ratios: BodyRatios, gender: str = None) -> float:
    """
    Calculate overall body symmetry score

    Analyzes 6 key ratios and compares to ideal proportions.
    Score is 0-100 (100 = perfect symmetry)

    Args:
        body_ratios: BodyRatios object with all calculated ratios
        gender: "male" or "female" (affects ideal ranges)

    Returns:
        Symmetry score (0-100)
    """
    # This is already calculated in ratio_calculator, just return it
    return body_ratios.symmetry_score


def detect_asymmetries(
    measurements: BodyMeasurements,
    body_ratios: BodyRatios,
    gender: str = None
) -> List[str]:
    """
    Identify specific body asymmetries and imbalances

    Args:
        measurements: BodyMeasurements object
        body_ratios: BodyRatios object
        gender: User gender (optional)

    Returns:
        List of asymmetry descriptions
    """
    asymmetries = []

    # Check shoulder-to-waist ratio
    stw_ratio = body_ratios.shoulder_to_waist_ratio
    if stw_ratio < 1.2:
        asymmetries.append("Narrow shoulders relative to waist")
    elif stw_ratio > 1.8:
        asymmetries.append("Very broad shoulders (elite proportion)")

    # Check waist-to-hip ratio
    whr = body_ratios.waist_to_hip_ratio

    if gender and gender.lower() == "female":
        if whr < 0.65:
            asymmetries.append("Very narrow waist (excellent proportion)")
        elif whr > 0.85:
            asymmetries.append("Wide waist relative to hips (health risk)")
    else:  # Male
        if whr < 0.85:
            asymmetries.append("Narrow waist (low health risk)")
        elif whr > 0.95:
            asymmetries.append("Wide waist relative to hips (health risk)")

    # Check chest-to-waist ratio
    ctw_ratio = body_ratios.chest_to_waist_ratio
    if ctw_ratio < 1.1:
        asymmetries.append("Underdeveloped chest")
    elif ctw_ratio > 1.5:
        asymmetries.append("Very well-developed chest")

    # Check arm-to-chest ratio
    atc_ratio = body_ratios.arm_to_chest_ratio
    if atc_ratio < 0.32:
        asymmetries.append("Underdeveloped arms")
    elif atc_ratio > 0.42:
        asymmetries.append("Overdeveloped arms (may lack proportion)")

    # Check leg-to-torso ratio (if available)
    if body_ratios.leg_to_torso_ratio:
        ltt_ratio = body_ratios.leg_to_torso_ratio
        if ltt_ratio < 0.65:
            asymmetries.append("Underdeveloped legs")
        elif ltt_ratio > 0.90:
            asymmetries.append("Very well-developed legs")

    # Check body fat percentage
    bf_percent = measurements.body_fat_percent
    if bf_percent < 8:
        asymmetries.append("Very low body fat (may be unsustainable)")
    elif bf_percent > 25:
        asymmetries.append("High body fat (consider reduction)")

    return asymmetries


def analyze_muscle_balance(measurements: BodyMeasurements) -> Dict[str, str]:
    """
    Analyze muscle development balance across body

    Args:
        measurements: BodyMeasurements object

    Returns:
        Dictionary of balance assessments
    """
    balance = {}

    chest = measurements.chest_circumference_cm
    waist = measurements.waist_circumference_cm
    bicep = measurements.bicep_circumference_cm
    thigh = measurements.thigh_circumference_cm

    # Upper body assessment
    chest_waist_diff = chest - waist
    if chest_waist_diff < 10:
        balance["upper_body"] = "Minimal taper - focus on chest/back"
    elif chest_waist_diff < 20:
        balance["upper_body"] = "Moderate taper - average development"
    else:
        balance["upper_body"] = "Excellent taper - well developed"

    # Arm size relative to chest
    expected_bicep = chest * 0.38  # Ideal proportion
    bicep_diff = bicep - expected_bicep

    if bicep_diff < -3:
        balance["arms"] = "Underdeveloped - prioritize arm work"
    elif bicep_diff > 3:
        balance["arms"] = "Overdeveloped - may lack proportion"
    else:
        balance["arms"] = "Well-proportioned to torso"

    # Leg development
    if thigh:
        expected_thigh = waist * 0.75  # Rough ideal
        thigh_diff = thigh - expected_thigh

        if thigh_diff < -5:
            balance["legs"] = "Underdeveloped - focus on leg training"
        elif thigh_diff > 5:
            balance["legs"] = "Well-developed legs"
        else:
            balance["legs"] = "Balanced leg development"

    return balance


def calculate_proportion_score(
    body_ratios: BodyRatios,
    measurements: BodyMeasurements
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate detailed proportion scores for each body area

    Args:
        body_ratios: BodyRatios object
        measurements: BodyMeasurements object

    Returns:
        Tuple of (overall_score, component_scores_dict)
    """
    component_scores = {}

    # Shoulder proportion (based on Adonis Index)
    adonis = body_ratios.adonis_index
    if 1.5 <= adonis <= 1.7:
        component_scores["shoulders"] = 100
    elif 1.4 <= adonis < 1.5 or 1.7 < adonis <= 1.8:
        component_scores["shoulders"] = 85
    elif 1.2 <= adonis < 1.4 or 1.8 < adonis <= 2.0:
        component_scores["shoulders"] = 70
    else:
        component_scores["shoulders"] = 50

    # Waist proportion (based on WHR)
    whr = body_ratios.waist_to_hip_ratio
    if 0.85 <= whr <= 0.95:
        component_scores["waist"] = 100
    elif 0.80 <= whr < 0.85 or 0.95 < whr <= 1.0:
        component_scores["waist"] = 80
    else:
        component_scores["waist"] = 60

    # Chest proportion
    ctw = body_ratios.chest_to_waist_ratio
    if 1.2 <= ctw <= 1.4:
        component_scores["chest"] = 100
    elif 1.1 <= ctw < 1.2 or 1.4 < ctw <= 1.5:
        component_scores["chest"] = 80
    else:
        component_scores["chest"] = 60

    # Arm proportion
    atc = body_ratios.arm_to_chest_ratio
    if 0.36 <= atc <= 0.40:
        component_scores["arms"] = 100
    elif 0.33 <= atc < 0.36 or 0.40 < atc <= 0.42:
        component_scores["arms"] = 80
    else:
        component_scores["arms"] = 60

    # Overall score (average of components)
    overall_score = sum(component_scores.values()) / len(component_scores)

    return (round(overall_score, 1), component_scores)


def get_symmetry_recommendations(
    asymmetries: List[str],
    body_ratios: BodyRatios
) -> List[str]:
    """
    Generate recommendations based on detected asymmetries

    Args:
        asymmetries: List of detected asymmetries
        body_ratios: BodyRatios object

    Returns:
        List of actionable recommendations
    """
    recommendations = []

    # Analyze asymmetries and suggest improvements
    for asymmetry in asymmetries:
        if "narrow shoulders" in asymmetry.lower():
            recommendations.append("Focus on lateral raises, overhead press, and rowing exercises")

        elif "underdeveloped chest" in asymmetry.lower():
            recommendations.append("Prioritize bench press, push-ups, and chest flies")

        elif "underdeveloped arms" in asymmetry.lower():
            recommendations.append("Add isolation work: bicep curls, tricep extensions")

        elif "underdeveloped legs" in asymmetry.lower():
            recommendations.append("Increase leg training frequency: squats, lunges, leg press")

        elif "wide waist" in asymmetry.lower():
            recommendations.append("Reduce calorie intake and increase cardio for fat loss")

        elif "high body fat" in asymmetry.lower():
            recommendations.append("Implement calorie deficit with high protein intake")

    # If no major asymmetries, provide maintenance advice
    if not recommendations:
        recommendations.append("Maintain balanced training across all muscle groups")
        recommendations.append("Focus on progressive overload to continue improvements")

    return recommendations


def compare_to_ideal_physique(
    body_ratios: BodyRatios,
    measurements: BodyMeasurements,
    target_physique: str = "athletic"
) -> Dict[str, any]:
    """
    Compare current measurements to ideal physique targets

    Args:
        body_ratios: BodyRatios object
        measurements: BodyMeasurements object
        target_physique: "athletic", "bodybuilder", "fitness", or "average"

    Returns:
        Dictionary with comparison results
    """
    # Define ideal targets for different physiques
    targets = {
        "athletic": {
            "shoulder_to_waist": 1.55,
            "waist_to_hip": 0.90,
            "chest_to_waist": 1.30,
            "body_fat": 12.0,
        },
        "bodybuilder": {
            "shoulder_to_waist": 1.65,
            "waist_to_hip": 0.88,
            "chest_to_waist": 1.40,
            "body_fat": 8.0,
        },
        "fitness": {
            "shoulder_to_waist": 1.45,
            "waist_to_hip": 0.92,
            "chest_to_waist": 1.25,
            "body_fat": 15.0,
        },
        "average": {
            "shoulder_to_waist": 1.35,
            "waist_to_hip": 0.95,
            "chest_to_waist": 1.20,
            "body_fat": 18.0,
        }
    }

    target = targets.get(target_physique, targets["athletic"])

    # Calculate differences
    differences = {
        "shoulder_to_waist_diff": body_ratios.shoulder_to_waist_ratio - target["shoulder_to_waist"],
        "waist_to_hip_diff": body_ratios.waist_to_hip_ratio - target["waist_to_hip"],
        "chest_to_waist_diff": body_ratios.chest_to_waist_ratio - target["chest_to_waist"],
        "body_fat_diff": measurements.body_fat_percent - target["body_fat"],
    }

    # Generate comparison summary
    summary = []
    if differences["shoulder_to_waist_diff"] < -0.1:
        summary.append("Shoulders need more development")
    elif differences["shoulder_to_waist_diff"] > 0.1:
        summary.append("Shoulders exceed target (excellent)")

    if differences["body_fat_diff"] > 3:
        summary.append("Reduce body fat by {:.1f}%".format(differences["body_fat_diff"]))
    elif differences["body_fat_diff"] < -2:
        summary.append("Body fat below target (very lean)")

    # Calculate overall proximity to target (0-100, 100 = perfect match)
    avg_deviation = sum(abs(d) for d in differences.values()) / len(differences)
    proximity_score = max(0, 100 - (avg_deviation * 20))

    return {
        "target_physique": target_physique,
        "target_values": target,
        "differences": differences,
        "proximity_score": round(proximity_score, 1),
        "summary": summary
    }
