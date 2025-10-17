"""
Step 4: User Profile Validation
Validates user data and fetches WHOOP recovery metrics for personalized analysis
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..models.schemas import UserProfile, WHOOPData
from ..config.settings import settings

logger = logging.getLogger(__name__)


class UserProfileValidator:
    """Validates and enriches user profile data"""

    def __init__(self):
        self.min_height_cm = 100
        self.max_height_cm = 250
        self.min_weight_kg = 30
        self.max_weight_kg = 300
        self.min_age = 13
        self.max_age = 100

    async def validate_and_enrich_profile(
        self,
        user_id: str,
        height_cm: Optional[float] = None,
        weight_kg: Optional[float] = None,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        fetch_whoop: bool = True
    ) -> UserProfile:
        """
        Validate user profile data and optionally fetch WHOOP metrics

        Args:
            user_id: User identifier
            height_cm: Height in centimeters
            weight_kg: Weight in kilograms
            gender: Gender (male/female/other)
            age: Age in years
            fetch_whoop: Whether to fetch WHOOP data

        Returns:
            Validated and enriched UserProfile

        Raises:
            ValueError: If required data is invalid
        """
        logger.info(f"Validating profile for user {user_id}")

        # Validate height
        validated_height = self._validate_height(height_cm)

        # Validate weight (optional)
        validated_weight = self._validate_weight(weight_kg) if weight_kg else None

        # Validate gender (optional but helpful for AI)
        validated_gender = self._validate_gender(gender) if gender else None

        # Validate age (optional)
        validated_age = self._validate_age(age) if age else None

        # Fetch WHOOP data if requested
        whoop_data = None
        if fetch_whoop:
            whoop_data = await self._fetch_whoop_data(user_id)

        # Create user profile
        user_profile = UserProfile(
            user_id=user_id,
            height_cm=validated_height,
            weight_kg=validated_weight,
            gender=validated_gender,
            age=validated_age,
            whoop_data=whoop_data,
            profile_validated_at=datetime.now()
        )

        logger.info(
            f"✅ Profile validated for user {user_id} | "
            f"Height: {validated_height}cm | "
            f"WHOOP: {'Yes' if whoop_data else 'No'}"
        )

        return user_profile

    def _validate_height(self, height_cm: Optional[float]) -> float:
        """
        Validate height is within reasonable range

        Args:
            height_cm: Height in centimeters

        Returns:
            Validated height

        Raises:
            ValueError: If height is invalid or missing
        """
        if height_cm is None:
            raise ValueError(
                "Height is required for body scan analysis. "
                "Please provide height in centimeters (e.g., 178)."
            )

        if not isinstance(height_cm, (int, float)):
            raise ValueError(
                f"Height must be a number, got {type(height_cm).__name__}"
            )

        if not (self.min_height_cm <= height_cm <= self.max_height_cm):
            raise ValueError(
                f"Height must be between {self.min_height_cm}-{self.max_height_cm}cm, "
                f"got {height_cm}cm"
            )

        return float(height_cm)

    def _validate_weight(self, weight_kg: Optional[float]) -> Optional[float]:
        """
        Validate weight is within reasonable range

        Args:
            weight_kg: Weight in kilograms

        Returns:
            Validated weight or None if not provided

        Raises:
            ValueError: If weight is invalid
        """
        if weight_kg is None:
            return None

        if not isinstance(weight_kg, (int, float)):
            raise ValueError(
                f"Weight must be a number, got {type(weight_kg).__name__}"
            )

        if not (self.min_weight_kg <= weight_kg <= self.max_weight_kg):
            raise ValueError(
                f"Weight must be between {self.min_weight_kg}-{self.max_weight_kg}kg, "
                f"got {weight_kg}kg"
            )

        return float(weight_kg)

    def _validate_gender(self, gender: Optional[str]) -> Optional[str]:
        """
        Validate and normalize gender

        Args:
            gender: Gender string

        Returns:
            Normalized gender (male/female/other) or None
        """
        if gender is None:
            return None

        gender_lower = gender.lower().strip()

        # Normalize variations
        if gender_lower in ["m", "male", "man"]:
            return "male"
        elif gender_lower in ["f", "female", "woman"]:
            return "female"
        else:
            return "other"

    def _validate_age(self, age: Optional[int]) -> Optional[int]:
        """
        Validate age is within reasonable range

        Args:
            age: Age in years

        Returns:
            Validated age or None

        Raises:
            ValueError: If age is invalid
        """
        if age is None:
            return None

        if not isinstance(age, int):
            raise ValueError(
                f"Age must be an integer, got {type(age).__name__}"
            )

        if not (self.min_age <= age <= self.max_age):
            raise ValueError(
                f"Age must be between {self.min_age}-{self.max_age}, got {age}"
            )

        return age

    async def _fetch_whoop_data(self, user_id: str) -> Optional[WHOOPData]:
        """
        Fetch WHOOP recovery data for user

        Args:
            user_id: User identifier

        Returns:
            WHOOPData if available, else None
        """
        try:
            # Import WHOOP client (only if needed)
            try:
                from whoop.api_client import get_whoop_recovery
            except ImportError:
                logger.warning("WHOOP client not available - skipping WHOOP data")
                return None

            # Fetch WHOOP data
            whoop_data = await get_whoop_recovery(user_id)

            if whoop_data:
                logger.info(
                    f"✅ WHOOP data fetched | "
                    f"Recovery: {whoop_data.recovery_score}% | "
                    f"Strain: {whoop_data.strain_score}"
                )
                return whoop_data
            else:
                logger.info(f"No WHOOP data found for user {user_id}")
                return None

        except Exception as e:
            logger.warning(f"Failed to fetch WHOOP data: {str(e)}")
            # Non-critical - continue without WHOOP data
            return None

    def build_ai_context(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Build context dictionary for AI vision prompt

        Args:
            user_profile: Validated user profile

        Returns:
            Dictionary of context data for prompt enhancement
        """
        context = {}

        # Always include height (required)
        context["height_cm"] = user_profile.height_cm

        # Optional fields
        if user_profile.gender:
            context["gender"] = user_profile.gender

        if user_profile.age:
            context["age"] = user_profile.age

        if user_profile.weight_kg:
            context["weight_kg"] = user_profile.weight_kg

        # WHOOP context
        if user_profile.whoop_data:
            whoop = user_profile.whoop_data
            context["whoop_recovery"] = whoop.recovery_score
            context["whoop_strain"] = whoop.strain_score

        return context


# Global validator instance
user_profile_validator = UserProfileValidator()


async def validate_user_profile(
    user_id: str,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    gender: Optional[str] = None,
    age: Optional[int] = None,
    fetch_whoop: bool = True
) -> UserProfile:
    """
    Convenience function to validate user profile

    Args:
        user_id: User identifier
        height_cm: Height in centimeters (required)
        weight_kg: Weight in kilograms (optional)
        gender: Gender (optional)
        age: Age in years (optional)
        fetch_whoop: Whether to fetch WHOOP data (default: True)

    Returns:
        Validated UserProfile

    Raises:
        ValueError: If required data is invalid
    """
    return await user_profile_validator.validate_and_enrich_profile(
        user_id=user_id,
        height_cm=height_cm,
        weight_kg=weight_kg,
        gender=gender,
        age=age,
        fetch_whoop=fetch_whoop
    )
