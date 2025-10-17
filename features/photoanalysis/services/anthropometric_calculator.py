"""
Anthropometric Measurements Calculator (Step 10)
Processes body measurements and calculates derived metrics
"""
from typing import Dict, Optional
from ..models.schemas import BodyMeasurements


def extract_measurements(body_measurements: BodyMeasurements) -> Dict[str, float]:
    """
    Extract and validate measurements from schema

    Args:
        body_measurements: Validated BodyMeasurements object

    Returns:
        Dictionary of measurement name -> value (cm or %)
    """
    measurements = {
        # Core circumferences (cm)
        "chest": body_measurements.chest_circumference_cm,
        "waist": body_measurements.waist_circumference_cm,
        "hips": body_measurements.hip_circumference_cm,

        # Limb measurements (cm)
        "bicep": body_measurements.bicep_circumference_cm,
        "thigh": body_measurements.thigh_circumference_cm,

        # Body composition
        "body_fat_percent": body_measurements.body_fat_percent,
        "posture_rating": body_measurements.posture_rating,
    }

    # Add optional measurements if present
    if body_measurements.calf_circumference_cm:
        measurements["calf"] = body_measurements.calf_circumference_cm

    if body_measurements.shoulder_width_cm:
        measurements["shoulders"] = body_measurements.shoulder_width_cm

    if body_measurements.estimated_weight_kg:
        measurements["weight_kg"] = body_measurements.estimated_weight_kg

    return measurements


def calculate_derived_metrics(
    measurements: Dict[str, float],
    height_cm: Optional[float] = None
) -> Dict[str, float]:
    """
    Calculate derived body metrics from raw measurements

    Args:
        measurements: Dictionary of body measurements
        height_cm: User height in cm (optional)

    Returns:
        Dictionary of derived metrics
    """
    derived = {}

    # BMI (if weight and height provided)
    if "weight_kg" in measurements and height_cm:
        weight_kg = measurements["weight_kg"]
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        derived["bmi"] = round(bmi, 1)

        # BMI category
        if bmi < 18.5:
            derived["bmi_category"] = "Underweight"
        elif bmi < 25:
            derived["bmi_category"] = "Normal"
        elif bmi < 30:
            derived["bmi_category"] = "Overweight"
        else:
            derived["bmi_category"] = "Obese"

    # Lean Body Mass (if weight and body fat % provided)
    if "weight_kg" in measurements and "body_fat_percent" in measurements:
        weight_kg = measurements["weight_kg"]
        bf_percent = measurements["body_fat_percent"]

        fat_mass_kg = weight_kg * (bf_percent / 100)
        lean_mass_kg = weight_kg - fat_mass_kg

        derived["fat_mass_kg"] = round(fat_mass_kg, 1)
        derived["lean_mass_kg"] = round(lean_mass_kg, 1)
        derived["lean_mass_percent"] = round(100 - bf_percent, 1)

    # Body Surface Area - Mosteller formula (if weight and height provided)
    if "weight_kg" in measurements and height_cm:
        weight_kg = measurements["weight_kg"]
        bsa_m2 = ((weight_kg * height_cm) / 3600) ** 0.5
        derived["body_surface_area_m2"] = round(bsa_m2, 2)

    # Frame Size Estimate (based on wrist to height ratio, if wrist provided)
    # Not implemented yet - would need wrist circumference

    # Muscle Mass Index approximation (if lean mass calculated)
    if "lean_mass_kg" in derived and height_cm:
        height_m = height_cm / 100
        muscle_mass_index = derived["lean_mass_kg"] / (height_m ** 2)
        derived["muscle_mass_index"] = round(muscle_mass_index, 1)

    return derived


def calculate_ideal_weight_range(
    height_cm: float,
    gender: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate ideal weight range based on height

    Uses Hamwi formula with adjustments

    Args:
        height_cm: Height in centimeters
        gender: "male" or "female" (optional)

    Returns:
        Dictionary with min, max, and ideal weight in kg
    """
    height_inches = height_cm / 2.54

    if gender and gender.lower() == "female":
        # Hamwi formula for females: 100 lbs for first 5 feet, +5 lbs per inch
        if height_inches <= 60:
            base_lbs = 100
        else:
            base_lbs = 100 + (5 * (height_inches - 60))
    else:
        # Hamwi formula for males: 106 lbs for first 5 feet, +6 lbs per inch
        # Default to male if not specified
        if height_inches <= 60:
            base_lbs = 106
        else:
            base_lbs = 106 + (6 * (height_inches - 60))

    # Convert to kg
    ideal_weight_kg = base_lbs * 0.453592

    # Range is typically ±10%
    min_weight_kg = ideal_weight_kg * 0.9
    max_weight_kg = ideal_weight_kg * 1.1

    return {
        "ideal_weight_kg": round(ideal_weight_kg, 1),
        "min_weight_kg": round(min_weight_kg, 1),
        "max_weight_kg": round(max_weight_kg, 1)
    }


def calculate_body_fat_category(body_fat_percent: float, gender: Optional[str] = None) -> str:
    """
    Categorize body fat percentage

    Args:
        body_fat_percent: Body fat percentage (0-60)
        gender: "male" or "female" (optional)

    Returns:
        Category string
    """
    if gender and gender.lower() == "female":
        # Female categories
        if body_fat_percent < 14:
            return "Essential Fat"
        elif body_fat_percent < 21:
            return "Athletes"
        elif body_fat_percent < 25:
            return "Fitness"
        elif body_fat_percent < 32:
            return "Average"
        else:
            return "Obese"
    else:
        # Male categories (default)
        if body_fat_percent < 6:
            return "Essential Fat"
        elif body_fat_percent < 14:
            return "Athletes"
        elif body_fat_percent < 18:
            return "Fitness"
        elif body_fat_percent < 25:
            return "Average"
        else:
            return "Obese"


def analyze_measurement_distribution(measurements: Dict[str, float]) -> Dict[str, str]:
    """
    Analyze where user carries most muscle/fat

    Args:
        measurements: Dictionary of body measurements

    Returns:
        Dictionary of distribution insights
    """
    insights = {}

    # Upper vs Lower body
    if "chest" in measurements and "thigh" in measurements:
        chest = measurements["chest"]
        thigh = measurements["thigh"]

        # Typical chest:thigh ratio is around 1.5-1.7
        ratio = chest / thigh

        if ratio > 1.8:
            insights["distribution"] = "Upper body dominant"
        elif ratio < 1.3:
            insights["distribution"] = "Lower body dominant"
        else:
            insights["distribution"] = "Balanced upper/lower"

    # Arm development
    if "bicep" in measurements and "chest" in measurements:
        bicep = measurements["bicep"]
        chest = measurements["chest"]

        # Ideal arm:chest ratio is roughly 0.36-0.38
        arm_ratio = bicep / chest

        if arm_ratio > 0.40:
            insights["arm_development"] = "Well-developed arms"
        elif arm_ratio < 0.32:
            insights["arm_development"] = "Underdeveloped arms"
        else:
            insights["arm_development"] = "Proportional arms"

    # Leg development
    if "thigh" in measurements and "calf" in measurements:
        thigh = measurements["thigh"]
        calf = measurements["calf"]

        # Ideal thigh:calf ratio is around 1.4-1.6
        leg_ratio = thigh / calf

        if leg_ratio > 1.7:
            insights["leg_development"] = "Disproportionate (work calves)"
        elif leg_ratio < 1.3:
            insights["leg_development"] = "Excellent calf development"
        else:
            insights["leg_development"] = "Balanced leg proportions"

    return insights


def get_measurement_summary(
    body_measurements: BodyMeasurements,
    height_cm: Optional[float] = None,
    gender: Optional[str] = None
) -> Dict[str, any]:
    """
    Complete measurement analysis

    Args:
        body_measurements: BodyMeasurements object
        height_cm: User height in cm (optional)
        gender: User gender (optional)

    Returns:
        Comprehensive measurement summary
    """
    # Extract base measurements
    measurements = extract_measurements(body_measurements)

    # Calculate derived metrics
    derived = calculate_derived_metrics(measurements, height_cm)

    # Body fat category
    bf_category = calculate_body_fat_category(
        body_measurements.body_fat_percent,
        gender
    )

    # Ideal weight range (if height provided)
    ideal_weight = None
    if height_cm:
        ideal_weight = calculate_ideal_weight_range(height_cm, gender)

    # Distribution analysis
    distribution = analyze_measurement_distribution(measurements)

    return {
        "raw_measurements": measurements,
        "derived_metrics": derived,
        "body_fat_category": bf_category,
        "ideal_weight_range": ideal_weight,
        "distribution_analysis": distribution
    }
