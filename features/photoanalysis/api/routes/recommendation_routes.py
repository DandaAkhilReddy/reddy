"""
Recommendation Routes - AI-powered workout and nutrition recommendations
"""
import logging
from fastapi import APIRouter, HTTPException, status, Body
from datetime import datetime

from ..models import (
    GenerateRecommendationsRequest,
    RecommendationsResponse
)
from ...services.firestore_client import get_firestore_client
from ...services.recommendation_engine import get_recommendation_engine
from ...services.error_handler import get_error_handler
from ...services.performance_optimizer import get_performance_optimizer

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# POST /api/v1/recommendations/{scan_id} - Generate recommendations
# ============================================================

@router.post(
    "/recommendations/{scan_id}",
    response_model=RecommendationsResponse,
    summary="Generate AI recommendations",
    description="""
    Generate personalized workout and nutrition recommendations based on scan results.

    **Features:**
    - Body type-specific workout plans
    - WHOOP recovery-aware recommendations
    - Nutrition plans with macro calculations
    - Progress timeline estimation
    - Key focus areas identification

    **Integration:**
    - Uses recommendation_engine.py (Step 18)
    - Integrates with nutrition-agent for meal plans
    - WHOOP data awareness
    """
)
async def generate_recommendations(
    scan_id: str,
    request: GenerateRecommendationsRequest = Body(...)
):
    """Generate AI-powered recommendations for a scan"""

    firestore_client = get_firestore_client()
    recommendation_engine = get_recommendation_engine()
    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()

    try:
        logger.info(f"Generating recommendations for scan {scan_id}")

        async with optimizer.profile("generate_recommendations"):

            # Step 1: Retrieve scan from Firestore
            async with optimizer.profile("retrieve_scan"):
                # Extract user_id from scan_id (format: scan_<hash>)
                # In production, would get user_id from JWT token
                # For now, we need to query Firestore by scan_id

                # Placeholder: Get from cache or Firestore
                scan_result = await firestore_client.get_scan_by_id(
                    user_id="placeholder_user",  # TODO: Get from token
                    scan_id=scan_id
                )

                if not scan_result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Scan {scan_id} not found"
                    )

            # Step 2: Check cache for existing recommendations
            cache_key = f"recommendations:{scan_id}:{request.fitness_goal}"
            cached_recommendations = await optimizer.cache.get(cache_key)

            if cached_recommendations:
                logger.info(f"Returning cached recommendations for {scan_id}")
                return RecommendationsResponse(**cached_recommendations)

            # Step 3: Generate recommendations
            async with optimizer.profile("ai_recommendation_generation"):
                user_preferences = {
                    "dietary_restrictions": request.dietary_restrictions,
                    "meals_per_day": request.meals_per_day
                }

                recommendations = await recommendation_engine.generate_recommendations(
                    scan_result=scan_result,
                    user_preferences=user_preferences,
                    fitness_goal=request.fitness_goal
                )

            # Step 4: Format response
            response = RecommendationsResponse(
                scan_id=scan_id,
                workout_plan=recommendations.workout_plan,
                nutrition_plan=recommendations.nutrition_plan,
                recovery_advice=recommendations.recovery_advice,
                key_focus_areas=recommendations.key_focus_areas,
                estimated_timeline_weeks=recommendations.estimated_timeline_weeks,
                generated_at=datetime.now()
            )

            # Step 5: Cache recommendations (1 hour TTL)
            await optimizer.cache.set(cache_key, response.dict(), ttl=3600)

            logger.info(f"Recommendations generated successfully for {scan_id}")

            return response

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Generate Recommendations",
            scan_id=scan_id,
            context={"fitness_goal": request.fitness_goal},
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


# ============================================================
# GET /api/v1/recommendations/{scan_id} - Get cached recommendations
# ============================================================

@router.get(
    "/recommendations/{scan_id}",
    response_model=RecommendationsResponse,
    summary="Get recommendations",
    description="Retrieve previously generated recommendations for a scan"
)
async def get_recommendations(scan_id: str, fitness_goal: str = "maintain"):
    """Get cached recommendations for a scan"""

    optimizer = get_performance_optimizer()
    error_handler = get_error_handler()

    try:
        # Check cache
        cache_key = f"recommendations:{scan_id}:{fitness_goal}"
        cached_recommendations = await optimizer.cache.get(cache_key)

        if cached_recommendations:
            logger.info(f"Retrieved cached recommendations for {scan_id}")
            return RecommendationsResponse(**cached_recommendations)

        # Not in cache - return 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No recommendations found for scan {scan_id}. Generate them first with POST /recommendations/{scan_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Get Recommendations",
            scan_id=scan_id,
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recommendations: {str(e)}"
        )
