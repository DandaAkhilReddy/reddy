"""
Body Metrics Tool - Integration with Photo Analysis
"""
import httpx
from typing import Optional
from ..models.schemas import BodyComposition
from ..config.settings import settings


async def get_latest_body_scan(user_id: str) -> Optional[BodyComposition]:
    """
    Fetch latest body scan from photo analysis API

    Args:
        user_id: User identifier

    Returns:
        BodyComposition object or None if not found
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.photo_analysis_api}/scans/user/{user_id}/latest",
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                return BodyComposition(**data)
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"API error: {response.status_code}")

    except Exception as e:
        # For now, return mock data for development
        return _get_mock_body_composition(user_id)


def _get_mock_body_composition(user_id: str) -> BodyComposition:
    """
    Generate mock body composition for development

    Args:
        user_id: User identifier

    Returns:
        Mock BodyComposition
    """
    from datetime import datetime

    return BodyComposition(
        user_id=user_id,
        weight_kg=75.0,
        height_cm=175.0,
        body_fat_percent=18.0,
        lean_mass_kg=61.5,  # 75kg * (1 - 0.18)
        age=28,
        gender="male",
        scan_date=datetime.now()
    )


def calculate_bmr(body_comp: BodyComposition) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation

    Args:
        body_comp: Body composition data

    Returns:
        BMR in calories/day
    """
    # Mifflin-St Jeor equation:
    # Men: BMR = 10W + 6.25H - 5A + 5
    # Women: BMR = 10W + 6.25H - 5A - 161
    # W = weight in kg, H = height in cm, A = age in years

    bmr = (10 * body_comp.weight_kg) + \
          (6.25 * body_comp.height_cm) - \
          (5 * body_comp.age)

    if body_comp.gender.lower() == "male":
        bmr += 5
    elif body_comp.gender.lower() == "female":
        bmr -= 161
    else:
        # Default to average
        bmr -= 78

    return bmr


def calculate_lean_mass_bmr(body_comp: BodyComposition) -> float:
    """
    Calculate BMR using Katch-McArdle formula (lean mass based)
    More accurate for individuals with known body composition

    Args:
        body_comp: Body composition data

    Returns:
        BMR in calories/day
    """
    # Katch-McArdle formula: BMR = 370 + (21.6 * lean_mass_kg)
    return 370 + (21.6 * body_comp.lean_mass_kg)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure

    Args:
        bmr: Basal metabolic rate
        activity_level: Activity level (sedentary, lightly_active, etc.)

    Returns:
        TDEE in calories/day
    """
    multipliers = {
        "sedentary": settings.sedentary_multiplier,
        "lightly_active": settings.lightly_active_multiplier,
        "moderately_active": settings.moderately_active_multiplier,
        "very_active": settings.very_active_multiplier,
        "extra_active": settings.extra_active_multiplier
    }

    multiplier = multipliers.get(activity_level, 1.55)  # Default to moderately active
    return bmr * multiplier


def estimate_ideal_weight_range(
    height_cm: float,
    body_fat_target: float,
    gender: str
) -> tuple[float, float]:
    """
    Estimate ideal weight range based on height and target body fat

    Args:
        height_cm: Height in centimeters
        body_fat_target: Target body fat percentage
        gender: Gender

    Returns:
        Tuple of (min_weight_kg, max_weight_kg)
    """
    # Using BMI as rough guide
    # Healthy BMI: 18.5 - 24.9

    height_m = height_cm / 100
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)

    # Adjust for body fat target
    # Higher muscle mass means higher healthy weight
    if body_fat_target < 15:  # Athletic
        min_weight *= 1.05
        max_weight *= 1.10
    elif body_fat_target < 20:  # Fit
        min_weight *= 1.02
        max_weight *= 1.05

    return (round(min_weight, 1), round(max_weight, 1))
