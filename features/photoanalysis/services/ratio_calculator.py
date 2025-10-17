"""
Golden Ratio & Body Ratios Calculator (Step 11)
Calculates Adonis Index and all key body proportions
"""
from typing import Dict, Tuple
from ..models.schemas import BodyMeasurements, BodyRatios


# Golden Ratio constant
GOLDEN_RATIO = 1.618

# Ideal ratio ranges (for scoring)
IDEAL_RATIOS = {
    "shoulder_to_waist": (1.4, 1.7),      # V-taper ideal
    "waist_to_hip_male": (0.85, 0.95),    # Male ideal
    "waist_to_hip_female": (0.65, 0.75),  # Female ideal
    "chest_to_waist": (1.2, 1.4),         # Upper body proportion
    "arm_to_chest": (0.36, 0.40),         # Arm development
    "thigh_to_waist": (0.70, 0.85),       # Leg proportion
}


def calculate_adonis_index(
    shoulder_width_cm: float,
    waist_circumference_cm: float
) -> float:
    """
    Calculate Adonis Index (shoulder-to-waist ratio)

    The Adonis Index is considered optimal at the golden ratio (1.618)

    Args:
        shoulder_width_cm: Shoulder width in cm
        waist_circumference_cm: Waist circumference in cm

    Returns:
        Adonis index (ratio)
    """
    if waist_circumference_cm <= 0:
        raise ValueError("Waist circumference must be positive")

    adonis_index = shoulder_width_cm / waist_circumference_cm
    return round(adonis_index, 3)


def calculate_golden_ratio_deviation(actual_ratio: float) -> float:
    """
    Calculate how close a ratio is to the golden ratio

    Args:
        actual_ratio: The actual measured ratio

    Returns:
        Score from 0-100 (100 = perfect golden ratio)
    """
    # Calculate percentage deviation from golden ratio
    deviation = abs(actual_ratio - GOLDEN_RATIO) / GOLDEN_RATIO

    # Convert to score (0% deviation = 100, >50% deviation = 0)
    if deviation >= 0.5:
        score = 0
    else:
        score = 100 * (1 - (deviation / 0.5))

    return round(score, 1)


def calculate_waist_to_hip_ratio(
    waist_circumference_cm: float,
    hip_circumference_cm: float
) -> float:
    """
    Calculate waist-to-hip ratio (WHR)

    Lower is better. Indicator of health and aesthetics.
    - Males: <0.90 is healthy, 0.85-0.95 is ideal
    - Females: <0.85 is healthy, 0.65-0.75 is ideal

    Args:
        waist_circumference_cm: Waist circumference in cm
        hip_circumference_cm: Hip circumference in cm

    Returns:
        Waist-to-hip ratio
    """
    if hip_circumference_cm <= 0:
        raise ValueError("Hip circumference must be positive")

    whr = waist_circumference_cm / hip_circumference_cm
    return round(whr, 3)


def calculate_chest_to_waist_ratio(
    chest_circumference_cm: float,
    waist_circumference_cm: float
) -> float:
    """
    Calculate chest-to-waist ratio

    Indicator of upper body development. Ideal is 1.2-1.4.

    Args:
        chest_circumference_cm: Chest circumference in cm
        waist_circumference_cm: Waist circumference in cm

    Returns:
        Chest-to-waist ratio
    """
    if waist_circumference_cm <= 0:
        raise ValueError("Waist circumference must be positive")

    ratio = chest_circumference_cm / waist_circumference_cm
    return round(ratio, 3)


def calculate_arm_to_chest_ratio(
    bicep_circumference_cm: float,
    chest_circumference_cm: float
) -> float:
    """
    Calculate arm-to-chest ratio

    Indicator of arm development relative to torso.
    Ideal is 0.36-0.40.

    Args:
        bicep_circumference_cm: Bicep circumference in cm
        chest_circumference_cm: Chest circumference in cm

    Returns:
        Arm-to-chest ratio
    """
    if chest_circumference_cm <= 0:
        raise ValueError("Chest circumference must be positive")

    ratio = bicep_circumference_cm / chest_circumference_cm
    return round(ratio, 3)


def calculate_leg_to_torso_ratio(
    thigh_circumference_cm: float,
    waist_circumference_cm: float
) -> float:
    """
    Calculate leg-to-torso ratio

    Indicator of lower body development.
    Ideal is 0.70-0.85.

    Args:
        thigh_circumference_cm: Thigh circumference in cm
        waist_circumference_cm: Waist circumference in cm

    Returns:
        Leg-to-torso ratio
    """
    if waist_circumference_cm <= 0:
        raise ValueError("Waist circumference must be positive")

    ratio = thigh_circumference_cm / waist_circumference_cm
    return round(ratio, 3)


def score_ratio(actual: float, ideal_range: Tuple[float, float]) -> float:
    """
    Score a ratio based on how close it is to ideal range

    Args:
        actual: Actual measured ratio
        ideal_range: (min, max) tuple of ideal range

    Returns:
        Score from 0-100
    """
    min_ideal, max_ideal = ideal_range
    mid_ideal = (min_ideal + max_ideal) / 2

    # Perfect score if within ideal range
    if min_ideal <= actual <= max_ideal:
        # Closer to middle is better
        deviation_from_mid = abs(actual - mid_ideal)
        range_width = (max_ideal - min_ideal) / 2

        if range_width > 0:
            score = 100 - (50 * (deviation_from_mid / range_width))
        else:
            score = 100

        return max(80, min(100, score))  # 80-100 if in range

    # Partial score if outside range
    if actual < min_ideal:
        # Below range
        deviation = (min_ideal - actual) / min_ideal
    else:
        # Above range
        deviation = (actual - max_ideal) / max_ideal

    # Exponential decay for out-of-range values
    if deviation >= 0.5:
        score = 0
    else:
        score = 80 * (1 - (deviation / 0.5))

    return max(0, min(80, score))  # Max 80 if outside range


def calculate_all_body_ratios(
    measurements: BodyMeasurements,
    gender: str = None
) -> BodyRatios:
    """
    Calculate all body ratios

    Args:
        measurements: BodyMeasurements object with all measurements
        gender: "male" or "female" (affects ideal ranges)

    Returns:
        BodyRatios object with all calculated ratios
    """
    # Extract measurements
    chest = measurements.chest_circumference_cm
    waist = measurements.waist_circumference_cm
    hips = measurements.hip_circumference_cm
    bicep = measurements.bicep_circumference_cm
    thigh = measurements.thigh_circumference_cm

    # Use shoulder width if available, otherwise estimate from chest
    if measurements.shoulder_width_cm:
        shoulders = measurements.shoulder_width_cm
    else:
        # Rough estimate: shoulders ≈ chest * 1.15
        shoulders = chest * 1.15

    # Calculate core ratios
    shoulder_to_waist = calculate_adonis_index(shoulders, waist)
    waist_to_hip = calculate_waist_to_hip_ratio(waist, hips)
    chest_to_waist = calculate_chest_to_waist_ratio(chest, waist)
    arm_to_chest = calculate_arm_to_chest_ratio(bicep, chest)

    # Optional: leg to torso (if thigh provided)
    leg_to_torso = None
    if thigh:
        leg_to_torso = calculate_leg_to_torso_ratio(thigh, waist)

    # Adonis Index vs Golden Ratio
    adonis_index = shoulder_to_waist
    golden_ratio_deviation = abs(adonis_index - GOLDEN_RATIO)

    # Calculate symmetry score (0-100)
    symmetry_score = calculate_symmetry_score_from_ratios(
        shoulder_to_waist,
        waist_to_hip,
        chest_to_waist,
        arm_to_chest,
        leg_to_torso,
        gender
    )

    # Create BodyRatios object
    body_ratios = BodyRatios(
        shoulder_to_waist_ratio=shoulder_to_waist,
        adonis_index=adonis_index,
        golden_ratio_deviation=golden_ratio_deviation,
        waist_to_hip_ratio=waist_to_hip,
        chest_to_waist_ratio=chest_to_waist,
        arm_to_chest_ratio=arm_to_chest,
        leg_to_torso_ratio=leg_to_torso,
        symmetry_score=symmetry_score
    )

    return body_ratios


def calculate_symmetry_score_from_ratios(
    shoulder_to_waist: float,
    waist_to_hip: float,
    chest_to_waist: float,
    arm_to_chest: float,
    leg_to_torso: float = None,
    gender: str = None
) -> float:
    """
    Calculate overall symmetry score from individual ratios

    Each ratio is scored against ideal range, then averaged.

    Args:
        shoulder_to_waist: Shoulder:waist ratio
        waist_to_hip: Waist:hip ratio
        chest_to_waist: Chest:waist ratio
        arm_to_chest: Arm:chest ratio
        leg_to_torso: Leg:torso ratio (optional)
        gender: "male" or "female" (affects WHR ideal)

    Returns:
        Overall symmetry score (0-100)
    """
    scores = []

    # Score shoulder:waist
    scores.append(score_ratio(shoulder_to_waist, IDEAL_RATIOS["shoulder_to_waist"]))

    # Score waist:hip (gender-dependent)
    if gender and gender.lower() == "female":
        whr_ideal = IDEAL_RATIOS["waist_to_hip_female"]
    else:
        whr_ideal = IDEAL_RATIOS["waist_to_hip_male"]
    scores.append(score_ratio(waist_to_hip, whr_ideal))

    # Score chest:waist
    scores.append(score_ratio(chest_to_waist, IDEAL_RATIOS["chest_to_waist"]))

    # Score arm:chest
    scores.append(score_ratio(arm_to_chest, IDEAL_RATIOS["arm_to_chest"]))

    # Score leg:torso (if available)
    if leg_to_torso:
        scores.append(score_ratio(leg_to_torso, IDEAL_RATIOS["thigh_to_waist"]))

    # Calculate weighted average
    overall_score = sum(scores) / len(scores)

    return round(overall_score, 1)


def get_ratio_interpretation(ratio_name: str, value: float, gender: str = None) -> str:
    """
    Get human-readable interpretation of a ratio

    Args:
        ratio_name: Name of the ratio (e.g., "shoulder_to_waist")
        value: Actual ratio value
        gender: User gender (optional)

    Returns:
        Interpretation string
    """
    interpretations = {
        "shoulder_to_waist": {
            "ranges": [(0, 1.2, "Narrow shoulders"), (1.2, 1.4, "Average"),
                      (1.4, 1.7, "Athletic V-taper"), (1.7, 2.0, "Excellent V-taper"),
                      (2.0, 10, "Elite V-taper")],
        },
        "waist_to_hip": {
            "ranges": [(0, 0.7, "Low risk (healthy)"), (0.7, 0.85, "Moderate"),
                      (0.85, 0.95, "Average"), (0.95, 10, "High risk")],
        },
        "chest_to_waist": {
            "ranges": [(0, 1.1, "Underdeveloped chest"), (1.1, 1.2, "Average"),
                      (1.2, 1.4, "Well-developed"), (1.4, 10, "Excellent development")],
        },
        "arm_to_chest": {
            "ranges": [(0, 0.32, "Underdeveloped arms"), (0.32, 0.36, "Average"),
                      (0.36, 0.40, "Well-proportioned"), (0.40, 10, "Overdeveloped arms")],
        },
    }

    if ratio_name not in interpretations:
        return "No interpretation available"

    ranges = interpretations[ratio_name]["ranges"]

    for min_val, max_val, desc in ranges:
        if min_val <= value < max_val:
            return desc

    return "Out of normal range"
