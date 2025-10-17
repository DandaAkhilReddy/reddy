"""
AI Recommendations Engine (Step 18)
Generates personalized workout, nutrition, and recovery recommendations

This service provides:
1. Workout recommendations based on body type and asymmetries
2. Nutrition planning integrated with body composition
3. WHOOP recovery-aware personalization
4. Progress tracking insights
5. Goal-specific guidance
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import date

from ..models.schemas import (
    ScanResult, PersonalizedRecommendations, WHOOPData,
    BodyType, BodyMeasurements, BodyRatios, AestheticScore
)
from ..services.symmetry_analyzer import detect_asymmetries, get_symmetry_recommendations
from ..services.body_type_classifier import get_body_type_recommendations

# Import nutrition agent (if available)
try:
    import sys
    from pathlib import Path
    nutrition_agent_path = Path(__file__).parent.parent.parent / "nutrition-agent"
    sys.path.insert(0, str(nutrition_agent_path))

    from models.schemas import (
        UserPreferences, ActivityLevel, NutritionGoal,
        DietaryRestriction
    )
    from workflows.daily_plan import generate_daily_plan

    NUTRITION_AGENT_AVAILABLE = True
except ImportError:
    NUTRITION_AGENT_AVAILABLE = False
    logging.warning("Nutrition agent not available - nutrition recommendations will be limited")


logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    AI-powered recommendation engine

    Generates personalized insights for:
    - Workout programming
    - Nutrition planning
    - Recovery optimization
    - Progress tracking
    """

    def __init__(self):
        """Initialize recommendation engine"""
        logger.info("Recommendation engine initialized")


    # ============================================================
    # MAIN RECOMMENDATION GENERATION
    # ============================================================

    async def generate_recommendations(
        self,
        scan_result: ScanResult,
        previous_scan: Optional[ScanResult] = None,
        user_preferences: Optional[Dict] = None,
        fitness_goal: str = "muscle_gain"
    ) -> PersonalizedRecommendations:
        """
        Generate complete personalized recommendations

        Args:
            scan_result: Current scan result
            previous_scan: Previous scan for progress tracking
            user_preferences: User dietary/fitness preferences
            fitness_goal: Primary goal (muscle_gain, fat_loss, maintain, athletic)

        Returns:
            PersonalizedRecommendations object
        """
        try:
            logger.info(f"Generating recommendations for scan {scan_result.scan_id}")

            # 1. Generate workout recommendations
            workout_plan = self._generate_workout_recommendations(
                scan_result.measurements,
                scan_result.ratios,
                scan_result.aesthetic_score,
                scan_result.whoop_data,
                fitness_goal
            )

            # 2. Generate nutrition recommendations
            nutrition_plan = await self._generate_nutrition_recommendations(
                scan_result.measurements,
                scan_result.whoop_data,
                user_preferences,
                fitness_goal
            )

            # 3. Generate recovery advice (WHOOP-aware)
            recovery_advice = self._generate_recovery_advice(
                scan_result.whoop_data,
                scan_result.measurements.body_fat_percent
            )

            # 4. Generate progress comparison (if previous scan available)
            progress_comparison = None
            if previous_scan:
                progress_comparison = self._generate_progress_insights(
                    scan_result,
                    previous_scan
                )

            # 5. Identify key focus areas
            focus_areas = self._identify_focus_areas(
                scan_result.aesthetic_score,
                scan_result.ratios,
                scan_result.measurements
            )

            # 6. Estimate timeline
            timeline_weeks = self._estimate_timeline(
                scan_result.aesthetic_score.overall_score,
                fitness_goal
            )

            # Assemble recommendations
            recommendations = PersonalizedRecommendations(
                workout_plan=workout_plan,
                nutrition_plan=nutrition_plan,
                recovery_advice=recovery_advice,
                progress_comparison=progress_comparison,
                key_focus_areas=focus_areas,
                estimated_timeline_weeks=timeline_weeks
            )

            logger.info("Recommendations generated successfully")
            return recommendations

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}", exc_info=True)
            raise


    # ============================================================
    # WORKOUT RECOMMENDATIONS
    # ============================================================

    def _generate_workout_recommendations(
        self,
        measurements: BodyMeasurements,
        ratios: BodyRatios,
        aesthetic: AestheticScore,
        whoop_data: Optional[WHOOPData],
        goal: str
    ) -> str:
        """
        Generate personalized workout recommendations

        Based on:
        - Body type classification
        - Symmetry analysis (target weak points)
        - Aesthetic score deficiencies
        - Recovery status (WHOOP)
        """
        recommendations = []

        # Header
        recommendations.append(f"**🏋️ PERSONALIZED WORKOUT PLAN - {goal.upper()}**\n")

        # Recovery-aware intensity
        intensity = self._determine_workout_intensity(whoop_data)
        recommendations.append(f"**Recommended Intensity:** {intensity}\n")

        # Body type specific recommendations
        body_type_recs = get_body_type_recommendations(
            aesthetic.body_type,
            ratios,
            measurements
        )

        recommendations.append("**Body Type Focus:**")
        for rec in body_type_recs[:3]:  # Top 3
            recommendations.append(f"- {rec}")
        recommendations.append("")

        # Symmetry-based corrections
        asymmetries = detect_asymmetries(measurements, ratios, gender=None)
        symmetry_recs = get_symmetry_recommendations(asymmetries, ratios)

        if symmetry_recs:
            recommendations.append("**Asymmetry Corrections:**")
            for rec in symmetry_recs[:3]:
                recommendations.append(f"- {rec}")
            recommendations.append("")

        # Aesthetic score improvements
        aesthetic_recs = self._generate_aesthetic_improvements(aesthetic, ratios)

        if aesthetic_recs:
            recommendations.append("**Aesthetic Improvements:**")
            for rec in aesthetic_recs:
                recommendations.append(f"- {rec}")
            recommendations.append("")

        # Split recommendation
        split_rec = self._recommend_training_split(aesthetic.body_type, goal)
        recommendations.append(f"**Recommended Split:** {split_rec}\n")

        # Weekly volume
        volume_rec = self._recommend_training_volume(
            aesthetic.body_type,
            whoop_data,
            goal
        )
        recommendations.append(f"**Weekly Volume:** {volume_rec}")

        return "\n".join(recommendations)


    def _determine_workout_intensity(
        self,
        whoop_data: Optional[WHOOPData]
    ) -> str:
        """
        Determine workout intensity based on WHOOP recovery

        Green (67-100): High intensity OK
        Yellow (34-66): Moderate intensity
        Red (0-33): Low intensity / active recovery
        """
        if not whoop_data or not whoop_data.recovery_score:
            return "Moderate (no recovery data available)"

        recovery = whoop_data.recovery_score

        if recovery >= 67:
            return "🟢 High Intensity (Recovery: {:.0f}% - Go hard!)".format(recovery)
        elif recovery >= 34:
            return "🟡 Moderate Intensity (Recovery: {:.0f}% - Steady work)".format(recovery)
        else:
            return "🔴 Low Intensity (Recovery: {:.0f}% - Active recovery only)".format(recovery)


    def _recommend_training_split(self, body_type: BodyType, goal: str) -> str:
        """Recommend training split based on body type and goal"""

        if goal == "muscle_gain":
            if body_type == BodyType.VTAPER:
                return "4-day Upper/Lower (maintain V-taper)"
            elif body_type == BodyType.RECTANGULAR:
                return "5-day Push/Pull/Legs (build width)"
            else:
                return "4-day Upper/Lower"

        elif goal == "fat_loss":
            return "3-day Full Body + 2 HIIT sessions"

        elif goal == "athletic":
            return "3-day Strength + 2 Conditioning"

        else:
            return "3-day Full Body"


    def _recommend_training_volume(
        self,
        body_type: BodyType,
        whoop_data: Optional[WHOOPData],
        goal: str
    ) -> str:
        """Recommend weekly training volume"""

        base_sets = 12  # Base sets per muscle group per week

        # Adjust for goal
        if goal == "muscle_gain":
            base_sets = 16
        elif goal == "fat_loss":
            base_sets = 10
        elif goal == "athletic":
            base_sets = 12

        # Adjust for recovery
        if whoop_data and whoop_data.recovery_score:
            if whoop_data.recovery_score < 34:
                base_sets = int(base_sets * 0.7)  # Reduce volume

        return f"{base_sets}-{base_sets + 4} sets per muscle group"


    def _generate_aesthetic_improvements(
        self,
        aesthetic: AestheticScore,
        ratios: BodyRatios
    ) -> List[str]:
        """Generate specific recommendations to improve aesthetic score"""

        improvements = []

        # Golden ratio improvements
        if aesthetic.golden_ratio_score < 30:
            if ratios.adonis_index < 1.4:
                improvements.append(
                    f"Build wider shoulders (current ratio: {ratios.adonis_index:.2f}, target: 1.618). "
                    "Focus on lateral raises, overhead press."
                )
            else:
                improvements.append(
                    f"Reduce waist size (current ratio: {ratios.adonis_index:.2f}). "
                    "Increase cardio, tighten nutrition."
                )

        # Symmetry improvements
        if aesthetic.symmetry_score < 20:
            improvements.append(
                "Add unilateral exercises (single-arm/leg work) to correct imbalances."
            )

        # Composition improvements
        if aesthetic.composition_score < 15:
            improvements.append(
                "Focus on fat loss to reveal muscle definition. Target 1% body fat loss per month."
            )

        # Posture improvements
        if aesthetic.posture_score < 7:
            improvements.append(
                "Improve posture: deadlifts, face pulls, core work. Stand tall in photos."
            )

        return improvements


    # ============================================================
    # NUTRITION RECOMMENDATIONS
    # ============================================================

    async def _generate_nutrition_recommendations(
        self,
        measurements: BodyMeasurements,
        whoop_data: Optional[WHOOPData],
        user_preferences: Optional[Dict],
        goal: str
    ) -> str:
        """
        Generate nutrition recommendations

        If nutrition agent is available, generates full meal plan.
        Otherwise, provides macro guidelines.
        """
        recommendations = []

        recommendations.append(f"**🍽️ NUTRITION PLAN - {goal.upper()}**\n")

        # Calculate basic macros
        estimated_weight = measurements.estimated_weight_kg or 75.0
        body_fat = measurements.body_fat_percent

        # Estimate lean body mass
        lean_mass_kg = estimated_weight * (1 - body_fat / 100)

        # Macro recommendations based on goal
        if goal == "muscle_gain":
            protein_g = lean_mass_kg * 2.2
            calories = estimated_weight * 38
            carbs_g = lean_mass_kg * 4.0
            fat_g = (calories - (protein_g * 4) - (carbs_g * 4)) / 9

        elif goal == "fat_loss":
            protein_g = lean_mass_kg * 2.4
            calories = estimated_weight * 28
            carbs_g = lean_mass_kg * 2.0
            fat_g = (calories - (protein_g * 4) - (carbs_g * 4)) / 9

        else:  # maintenance
            protein_g = lean_mass_kg * 2.0
            calories = estimated_weight * 33
            carbs_g = lean_mass_kg * 3.0
            fat_g = (calories - (protein_g * 4) - (carbs_g * 4)) / 9

        # Adjust for WHOOP recovery
        if whoop_data and whoop_data.recovery_score:
            if whoop_data.recovery_score < 34:
                calories *= 1.05  # Add 5% for recovery
                recommendations.append("**Recovery Boost:** +5% calories (low WHOOP recovery detected)\n")

        recommendations.append(f"**Daily Macro Targets:**")
        recommendations.append(f"- Calories: {calories:.0f} kcal")
        recommendations.append(f"- Protein: {protein_g:.0f}g ({protein_g / estimated_weight:.1f}g/kg bodyweight)")
        recommendations.append(f"- Carbs: {carbs_g:.0f}g")
        recommendations.append(f"- Fat: {fat_g:.0f}g\n")

        # Try to generate full meal plan if nutrition agent available
        if NUTRITION_AGENT_AVAILABLE:
            try:
                meal_plan = await self._generate_meal_plan(
                    measurements,
                    user_preferences,
                    goal
                )
                recommendations.append(meal_plan)
            except Exception as e:
                logger.warning(f"Meal plan generation failed: {str(e)}")
                recommendations.append(self._generate_basic_nutrition_tips(goal, body_fat))
        else:
            recommendations.append(self._generate_basic_nutrition_tips(goal, body_fat))

        return "\n".join(recommendations)


    async def _generate_meal_plan(
        self,
        measurements: BodyMeasurements,
        user_preferences: Optional[Dict],
        goal: str
    ) -> str:
        """Generate detailed meal plan using nutrition agent"""

        # Map goal to NutritionGoal enum
        goal_mapping = {
            "muscle_gain": NutritionGoal.MUSCLE_GAIN,
            "fat_loss": NutritionGoal.FAT_LOSS,
            "athletic": NutritionGoal.ATHLETIC_PERFORMANCE,
            "maintain": NutritionGoal.MAINTENANCE
        }

        nutrition_goal = goal_mapping.get(goal, NutritionGoal.MAINTENANCE)

        # Create user preferences
        preferences = UserPreferences(
            dietary_restrictions=[],
            meals_per_day=3,
            allergies=user_preferences.get("allergies", []) if user_preferences else [],
            cuisine_preferences=user_preferences.get("cuisine_preferences", []) if user_preferences else []
        )

        # Determine activity level (default to moderate)
        activity_level = ActivityLevel.MODERATE

        # Generate daily plan
        daily_plan = await generate_daily_plan(
            user_id="scan_user",
            activity_level=activity_level,
            goal=nutrition_goal,
            preferences=preferences,
            plan_date=date.today()
        )

        # Format meal plan
        plan_text = ["\n**📋 AI-Generated Meal Plan:**"]

        for i, meal in enumerate(daily_plan.meals, 1):
            plan_text.append(f"\n**Meal {i}:** {meal.name}")
            plan_text.append(f"  - {meal.calories:.0f} cal | P:{meal.protein_g:.0f}g C:{meal.carbs_g:.0f}g F:{meal.fat_g:.0f}g")

        plan_text.append(f"\n**Total:** {daily_plan.actual_calories:.0f} cal")
        plan_text.append(f"**Accuracy:** {daily_plan.macro_balance_score*100:.1f}% to targets")

        return "\n".join(plan_text)


    def _generate_basic_nutrition_tips(self, goal: str, body_fat: float) -> str:
        """Generate basic nutrition tips when meal plan unavailable"""

        tips = ["\n**Nutrition Tips:**"]

        if goal == "muscle_gain":
            tips.append("- Eat in slight surplus (200-300 cal above maintenance)")
            tips.append("- Prioritize protein at every meal")
            tips.append("- Time carbs around workouts")

        elif goal == "fat_loss":
            tips.append("- Maintain 300-500 cal deficit")
            tips.append("- Keep protein high to preserve muscle")
            tips.append("- Reduce carbs on rest days")

        if body_fat > 20:
            tips.append("- Focus on whole foods, reduce processed items")
            tips.append("- Track calories consistently")

        return "\n".join(tips)


    # ============================================================
    # RECOVERY RECOMMENDATIONS
    # ============================================================

    def _generate_recovery_advice(
        self,
        whoop_data: Optional[WHOOPData],
        body_fat: float
    ) -> Optional[str]:
        """Generate WHOOP-aware recovery recommendations"""

        if not whoop_data or not whoop_data.has_data:
            return "⌚ Connect WHOOP for personalized recovery insights"

        advice = []

        advice.append("**⌚ WHOOP RECOVERY INSIGHTS:**\n")

        # Recovery status
        recovery = whoop_data.recovery_score or 0
        if recovery >= 67:
            advice.append("🟢 **Excellent recovery** - Push hard today!")
        elif recovery >= 34:
            advice.append("🟡 **Moderate recovery** - Steady training intensity")
        else:
            advice.append("🔴 **Low recovery** - Prioritize rest and light activity")

        # Sleep
        if whoop_data.sleep_hours:
            if whoop_data.sleep_hours < 7:
                advice.append(f"\n⚠️ **Sleep:** {whoop_data.sleep_hours:.1f}h - Aim for 7-9h")
            else:
                advice.append(f"\n✅ **Sleep:** {whoop_data.sleep_hours:.1f}h - Good!")

        # HRV
        if whoop_data.hrv_ms:
            advice.append(f"**HRV:** {whoop_data.hrv_ms:.0f}ms")

        # RHR
        if whoop_data.resting_heart_rate:
            advice.append(f"**Resting HR:** {whoop_data.resting_heart_rate} bpm")

        # Strain
        if whoop_data.strain_score:
            advice.append(f"\n**Yesterday's Strain:** {whoop_data.strain_score:.1f}/21")

        return "\n".join(advice)


    # ============================================================
    # PROGRESS TRACKING
    # ============================================================

    def _generate_progress_insights(
        self,
        current_scan: ScanResult,
        previous_scan: ScanResult
    ) -> str:
        """Generate progress comparison insights"""

        from .scan_assembler import compare_scans

        comparison = compare_scans(current_scan, previous_scan)

        insights = []
        insights.append(f"**📈 PROGRESS ({comparison['time_between_scans_days']} days)**\n")

        changes = comparison['changes']

        # Body fat change
        bf_change = changes['body_fat_change_percent']
        if bf_change < -0.5:
            insights.append(f"✅ Body Fat: -{abs(bf_change):.1f}% (Excellent!)")
        elif bf_change > 0.5:
            insights.append(f"⚠️ Body Fat: +{bf_change:.1f}%")
        else:
            insights.append(f"➡️ Body Fat: ~{abs(bf_change):.1f}% (Minimal change)")

        # Aesthetic score
        score_change = changes['aesthetic_score_change']
        if score_change > 2:
            insights.append(f"✅ Aesthetic Score: +{score_change:.1f} points")
        elif score_change < -2:
            insights.append(f"⚠️ Aesthetic Score: {score_change:.1f} points")

        # Adonis index
        ai_change = changes['adonis_index_change']
        if ai_change > 0.02:
            insights.append(f"✅ Adonis Index: +{ai_change:.2f} (Better proportions!)")

        # Symmetry
        sym_change = changes['symmetry_score_change']
        if sym_change > 2:
            insights.append(f"✅ Symmetry: +{sym_change:.1f} points (More balanced!)")

        # Summary
        insights.append(f"\n**Summary:** {comparison['progress_summary'][0]}")

        return "\n".join(insights)


    # ============================================================
    # FOCUS AREAS & TIMELINE
    # ============================================================

    def _identify_focus_areas(
        self,
        aesthetic: AestheticScore,
        ratios: BodyRatios,
        measurements: BodyMeasurements
    ) -> List[str]:
        """Identify top 3-5 focus areas for improvement"""

        focus_areas = []

        # Check each component
        if aesthetic.golden_ratio_score < 28:  # 70% of 40
            focus_areas.append("Improve shoulder:waist ratio (widen shoulders or reduce waist)")

        if aesthetic.symmetry_score < 21:  # 70% of 30
            focus_areas.append("Correct muscle imbalances with unilateral training")

        if aesthetic.composition_score < 14:  # 70% of 20
            focus_areas.append(f"Reduce body fat from {measurements.body_fat_percent:.1f}% to <15%")

        if aesthetic.posture_score < 7:  # 70% of 10
            focus_areas.append("Improve posture and core strength")

        if measurements.posture_rating < 7:
            focus_areas.append("Work on standing posture and alignment")

        # Ensure we have at least one focus area
        if not focus_areas:
            focus_areas.append("Maintain current physique with consistent training")

        return focus_areas[:5]  # Max 5


    def _estimate_timeline(
        self,
        current_score: float,
        goal: str
    ) -> int:
        """
        Estimate weeks to reach goal

        Assumptions:
        - Can improve 1-2 aesthetic score points per month with consistent training
        - Fat loss: 1% body fat per month
        - Muscle gain: 0.5-1kg lean mass per month
        """
        if current_score >= 80:
            # Already excellent
            return 8  # Maintenance / minor refinements

        elif current_score >= 70:
            # Good, aiming for excellent (70 -> 80 = +10 points)
            # At 1.5 points/month = ~7 months
            return 28

        elif current_score >= 60:
            # Average, aiming for good (60 -> 75 = +15 points)
            # At 1.5 points/month = ~10 months
            return 40

        else:
            # Below average, need significant work
            # 50 -> 70 = +20 points at 1.5 points/month = ~14 months
            return 56


# ============================================================
# SINGLETON INSTANCE
# ============================================================

_recommendation_engine: Optional[RecommendationEngine] = None


def get_recommendation_engine() -> RecommendationEngine:
    """Get singleton recommendation engine instance"""
    global _recommendation_engine

    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()

    return _recommendation_engine
