"""
History Routes - Scan history and progress tracking endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status, Query
from datetime import datetime

from ..models import (
    ScanHistoryResponse,
    SimpleScanResponse,
    ProgressComparisonResponse,
    SortOrder
)
from ...services.firestore_client import get_firestore_client
from ...services.error_handler import get_error_handler
from ...services.performance_optimizer import get_performance_optimizer

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# GET /api/v1/history/user/{user_id} - Get scan history
# ============================================================

@router.get(
    "/history/user/{user_id}",
    response_model=ScanHistoryResponse,
    summary="Get user scan history",
    description="""
    Retrieve complete scan history for a user with pagination.

    **Features:**
    - Paginated results (limit/offset)
    - Sort by timestamp (ascending/descending)
    - Includes scan summary data
    - Total scan count

    **Default**: Returns 10 most recent scans
    """
)
async def get_scan_history(
    user_id: str,
    limit: int = Query(10, ge=1, le=100, description="Max number of scans to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order (asc/desc)")
):
    """Get paginated scan history for user"""

    firestore_client = get_firestore_client()
    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()

    try:
        logger.info(f"Retrieving scan history for user {user_id} (limit={limit}, offset={offset})")

        async with optimizer.profile("get_scan_history"):

            # Get scans from Firestore
            scans = await firestore_client.get_user_scan_history(
                user_id=user_id,
                limit=limit + 1,  # Get one extra to check if there's more
                start_after=None  # TODO: Implement proper pagination with start_after
            )

            # Check if there are more scans
            has_more = len(scans) > limit
            if has_more:
                scans = scans[:limit]

            # Convert to simple responses
            simple_scans = []
            for scan in scans:
                simple_scans.append(SimpleScanResponse(
                    scan_id=scan.scan_id,
                    body_signature_id=scan.body_signature_id,
                    timestamp=scan.timestamp,
                    body_type=scan.aesthetic_score.body_type.value,
                    body_fat_percent=scan.measurements.body_fat_percent,
                    overall_score=scan.aesthetic_score.overall_score,
                    confidence=scan.confidence.overall_confidence
                ))

            # Get total count (from user profile)
            user_profile = await firestore_client.get_user_profile(user_id)
            total_scans = user_profile.total_scans if user_profile else len(simple_scans)

            response = ScanHistoryResponse(
                user_id=user_id,
                total_scans=total_scans,
                scans=simple_scans,
                has_more=has_more
            )

            logger.info(f"Retrieved {len(simple_scans)} scans for user {user_id}")

            return response

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Get Scan History",
            user_id=user_id,
            context={"limit": limit, "offset": offset},
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan history: {str(e)}"
        )


# ============================================================
# GET /api/v1/history/user/{user_id}/progress - Get progress comparison
# ============================================================

@router.get(
    "/history/user/{user_id}/progress",
    response_model=ProgressComparisonResponse,
    summary="Get progress comparison",
    description="""
    Compare current scan with previous scan to track progress.

    **Features:**
    - Automatic comparison with scan from N weeks ago
    - Body fat changes
    - Aesthetic score improvements
    - Adonis Index changes
    - Symmetry improvements
    - Progress summary

    **Default**: Compares with scan from 4 weeks ago
    """
)
async def get_progress_comparison(
    user_id: str,
    weeks_back: int = Query(4, ge=1, le=52, description="Weeks to look back for comparison")
):
    """Get progress comparison between current and previous scan"""

    firestore_client = get_firestore_client()
    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()

    try:
        logger.info(f"Generating progress comparison for user {user_id} ({weeks_back} weeks)")

        async with optimizer.profile("get_progress_comparison"):

            # Get progress comparison from Firestore
            comparison = await firestore_client.get_progress_comparison(
                user_id=user_id,
                weeks_back=weeks_back
            )

            if not comparison:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No scan found from {weeks_back} weeks ago for comparison"
                )

            # Check if comparison indicates "no historical data"
            if comparison.get("status") == "no_historical_data":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=comparison.get("message")
                )

            response = ProgressComparisonResponse(
                user_id=user_id,
                time_between_scans_days=comparison["time_between_scans_days"],
                changes=comparison["changes"],
                body_type_changed=comparison["body_type_changed"],
                progress_summary=comparison["progress_summary"]
            )

            logger.info(f"Progress comparison generated for user {user_id}")

            return response

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Get Progress Comparison",
            user_id=user_id,
            context={"weeks_back": weeks_back},
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate progress comparison: {str(e)}"
        )


# ============================================================
# GET /api/v1/history/user/{user_id}/latest - Get latest scan
# ============================================================

@router.get(
    "/history/user/{user_id}/latest",
    response_model=SimpleScanResponse,
    summary="Get latest scan",
    description="Retrieve user's most recent scan"
)
async def get_latest_scan(user_id: str):
    """Get user's most recent scan"""

    firestore_client = get_firestore_client()
    error_handler = get_error_handler()

    try:
        logger.info(f"Retrieving latest scan for user {user_id}")

        # Get latest scan
        latest_scan = await firestore_client.get_latest_scan(user_id)

        if not latest_scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No scans found for user {user_id}"
            )

        response = SimpleScanResponse(
            scan_id=latest_scan.scan_id,
            body_signature_id=latest_scan.body_signature_id,
            timestamp=latest_scan.timestamp,
            body_type=latest_scan.aesthetic_score.body_type.value,
            body_fat_percent=latest_scan.measurements.body_fat_percent,
            overall_score=latest_scan.aesthetic_score.overall_score,
            confidence=latest_scan.confidence.overall_confidence
        )

        logger.info(f"Retrieved latest scan {latest_scan.scan_id} for user {user_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Get Latest Scan",
            user_id=user_id,
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest scan: {str(e)}"
        )
