"""
Recovery Data Tool - Integration with WHOOP API
"""
import httpx
from typing import Optional
from datetime import date, datetime
from ..models.schemas import WHOOPMetrics
from ..config.settings import settings


async def get_whoop_recovery(user_id: str, date_param: Optional[date] = None) -> Optional[WHOOPMetrics]:
    """
    Fetch WHOOP recovery metrics

    Args:
        user_id: User identifier
        date_param: Specific date (defaults to today)

    Returns:
        WHOOPMetrics or None
    """
    if date_param is None:
        date_param = date.today()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.whoop_api}/{user_id}",
                params={"date": date_param.isoformat()},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                return WHOOPMetrics(**data)
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"WHOOP API error: {response.status_code}")

    except Exception as e:
        # For now, return mock data
        return _get_mock_whoop_data(user_id, date_param)


def _get_mock_whoop_data(user_id: str, date_param: date) -> WHOOPMetrics:
    """
    Generate mock WHOOP data for development

    Args:
        user_id: User identifier
        date_param: Date

    Returns:
        Mock WHOOPMetrics
    """
    return WHOOPMetrics(
        user_id=user_id,
        recovery_score=75.0,  # Good recovery
        strain_score=12.5,    # Moderate strain
        sleep_hours=7.5,
        hrv_ms=65.0,
        resting_hr_bpm=58,
        date=date_param
    )


def adjust_calories_for_recovery(
    base_calories: float,
    recovery_score: float,
    goal: str
) -> tuple[float, str]:
    """
    Adjust calorie target based on WHOOP recovery score

    Args:
        base_calories: Base calorie target
        recovery_score: WHOOP recovery score (0-100)
        goal: Nutrition goal (weight_loss, muscle_gain, etc.)

    Returns:
        Tuple of (adjusted_calories, reasoning)
    """
    # Recovery score interpretation:
    # 67-100: Green (optimal recovery)
    # 34-66: Yellow (adequate recovery)
    # 0-33: Red (poor recovery)

    reasoning = ""

    if recovery_score >= 67:
        # Green zone - proceed as planned or push slightly harder
        if goal == "muscle_gain":
            adjustment = 1.05  # 5% increase for muscle building
            reasoning = "High recovery allows for increased calories to support muscle growth"
        elif goal == "weight_loss":
            adjustment = 1.0  # Maintain deficit
            reasoning = "High recovery, maintaining planned deficit"
        else:
            adjustment = 1.0
            reasoning = "Optimal recovery, proceeding with plan"

    elif recovery_score >= 34:
        # Yellow zone - maintain or slight adjustment
        if goal == "weight_loss":
            adjustment = 1.05  # 5% increase to support recovery
            reasoning = "Moderate recovery, slightly increasing calories to aid recovery"
        else:
            adjustment = 1.0
            reasoning = "Moderate recovery, maintaining planned intake"

    else:
        # Red zone - prioritize recovery
        if goal == "weight_loss":
            adjustment = 1.10  # 10% increase
            reasoning = "Low recovery requires more calories for repair and adaptation"
        elif goal == "muscle_gain":
            adjustment = 1.15  # 15% increase
            reasoning = "Low recovery - significantly increasing calories to support recovery"
        else:
            adjustment = 1.10
            reasoning = "Poor recovery detected, increasing calories to support body's needs"

    adjusted_calories = base_calories * adjustment

    return (round(adjusted_calories), reasoning)


def adjust_macros_for_strain(
    base_macros: dict,
    strain_score: float
) -> dict:
    """
    Adjust macro ratios based on strain score

    Args:
        base_macros: Dictionary with protein_g, carbs_g, fat_g
        strain_score: WHOOP strain score (0-21)

    Returns:
        Adjusted macros dictionary
    """
    # High strain (>15) = need more carbs for recovery
    # Low strain (<10) = can reduce carbs slightly

    if strain_score > 15:
        # High strain - increase carbs by 10%
        carb_multiplier = 1.10
        # Reduce fat slightly to maintain calories
        fat_multiplier = 0.95
        protein_multiplier = 1.0
    elif strain_score < 10:
        # Low strain - standard ratios
        carb_multiplier = 1.0
        fat_multiplier = 1.0
        protein_multiplier = 1.0
    else:
        # Moderate strain - slight carb increase
        carb_multiplier = 1.05
        fat_multiplier = 0.98
        protein_multiplier = 1.0

    adjusted = {
        "protein_g": round(base_macros["protein_g"] * protein_multiplier),
        "carbs_g": round(base_macros["carbs_g"] * carb_multiplier),
        "fat_g": round(base_macros["fat_g"] * fat_multiplier)
    }

    return adjusted


def interpret_recovery_score(recovery_score: float) -> str:
    """
    Get human-readable interpretation of recovery score

    Args:
        recovery_score: WHOOP recovery score (0-100)

    Returns:
        Interpretation string
    """
    if recovery_score >= 67:
        return "Optimal - Body is well-recovered and ready for training"
    elif recovery_score >= 34:
        return "Adequate - Moderate recovery, can handle normal activity"
    else:
        return "Poor - Body needs rest and recovery, avoid intense training"


def get_nutrition_recommendations_from_whoop(whoop_data: WHOOPMetrics) -> list[str]:
    """
    Generate nutrition recommendations based on WHOOP metrics

    Args:
        whoop_data: WHOOP metrics

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Recovery-based
    if whoop_data.recovery_score < 34:
        recommendations.append("Prioritize anti-inflammatory foods (berries, fatty fish, turmeric)")
        recommendations.append("Increase protein intake for recovery (1.0g per lb bodyweight)")
        recommendations.append("Stay well-hydrated (aim for clear urine)")

    # Sleep-based
    if whoop_data.sleep_hours < 7.0:
        recommendations.append("Consider magnesium supplement before bed")
        recommendations.append("Reduce caffeine after 2 PM")
        recommendations.append("Eat last meal 2-3 hours before bed")

    # Strain-based
    if whoop_data.strain_score > 15:
        recommendations.append("Increase complex carbs for glycogen replenishment")
        recommendations.append("Time carbs around workouts for optimal recovery")
        recommendations.append("Consider post-workout protein shake (20-30g)")

    # HRV-based (if available)
    if whoop_data.hrv_ms and whoop_data.hrv_ms < 50:
        recommendations.append("Reduce stimulants (caffeine, pre-workout)")
        recommendations.append("Focus on whole, unprocessed foods")
        recommendations.append("Consider stress-reducing adaptogens (ashwagandha)")

    return recommendations if recommendations else ["No specific recommendations - metrics look good!"]
