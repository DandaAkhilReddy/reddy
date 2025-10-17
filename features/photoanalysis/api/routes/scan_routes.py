"""
Scan Routes - Photo upload and scan creation endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

from ..models import (
    CreateScanRequest, ScanCreatedResponse, DetailedScanResponse,
    SimpleScanResponse, ScanStatus, FitnessGoal
)
from ...models.schemas import (
    BodyMeasurements, BodyRatios, AestheticScore, ConfidenceMetrics,
    ImageQuality, PhotoAngle, ScanResult, BodyType, AngleType
)
from ...services.scan_assembler import assemble_scan_result
from ...services.firestore_client import get_firestore_client
from ...services.error_handler import get_error_handler, safe_execute, PhotoAnalysisError
from ...services.performance_optimizer import get_performance_optimizer, ImageOptimizer
from ...services.vision_pipeline import run_vision_analysis
from ...utils.image_validator import validate_image

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# DEPENDENCY: Get current user
# ============================================================

async def get_current_user(user_id: str = Form(...)) -> str:
    """
    Dependency to get current user from request
    In production, this would extract user from JWT token
    """
    # TODO: Replace with actual JWT token validation
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required"
        )
    return user_id


# ============================================================
# POST /api/v1/scans - Create new scan
# ============================================================

@router.post(
    "/scans",
    response_model=ScanCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create new body scan",
    description="""
    Upload 3 photos (front, side, back) to create a new body composition scan.

    **Requirements:**
    - 3 images (front, side, back angles)
    - Each image: 100KB - 10MB
    - Format: JPEG, PNG
    - Resolution: 480×640 to 4000×6000 pixels
    - Clear, well-lit photos of standing person

    **Processing:**
    - Estimated time: 20-30 seconds
    - Returns scan_id immediately
    - Use GET /scans/{scan_id} to retrieve results
    """
)
async def create_scan(
    front_image: UploadFile = File(..., description="Front view photo"),
    side_image: UploadFile = File(..., description="Side view photo"),
    back_image: UploadFile = File(..., description="Back view photo"),
    user_id: str = Form(..., description="User identifier"),
    height_cm: float = Form(None, description="User height in cm"),
    gender: str = Form(None, description="User gender (male/female)"),
    fitness_goal: str = Form("maintain", description="Fitness goal")
):
    """Create new scan from 3 uploaded photos"""

    error_handler = get_error_handler()
    optimizer = get_performance_optimizer()
    firestore_client = get_firestore_client()

    try:
        # Generate scan ID
        scan_id = f"scan_{uuid.uuid4().hex[:12]}"

        logger.info(f"Creating scan {scan_id} for user {user_id}")

        # Profile the operation
        async with optimizer.profile("create_scan"):

            # Read image data
            front_bytes = await front_image.read()
            side_bytes = await side_image.read()
            back_bytes = await back_image.read()

            # Steps 1-9: Run complete AI vision pipeline
            async with optimizer.profile("vision_pipeline_steps_1_9"):
                try:
                    measurements, confidence, pipeline_metadata = await run_vision_analysis(
                        front_image=front_bytes,
                        side_image=side_bytes,
                        back_image=back_bytes,
                        user_id=user_id,
                        height_cm=height_cm,
                        gender=gender,
                        filename_front=front_image.filename,
                        filename_side=side_image.filename,
                        filename_back=back_image.filename
                    )

                    logger.info(
                        f"Vision pipeline complete | Confidence: {confidence.overall_confidence:.2f} | "
                        f"Steps: {len(pipeline_metadata.get('steps_completed', []))}/9"
                    )

                except PhotoAnalysisError as e:
                    logger.error(f"Vision pipeline failed: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Photo analysis failed: {str(e)}"
                    )

            # Steps 10-16: Assemble complete scan result with mathematical analysis
            async with optimizer.profile("assemble_scan_result"):
                # Mock image URLs (in production, upload to Firebase Storage first)
                image_urls = {
                    "front": f"https://storage.reddyfit.com/{user_id}/{scan_id}/front.jpg",
                    "side": f"https://storage.reddyfit.com/{user_id}/{scan_id}/side.jpg",
                    "back": f"https://storage.reddyfit.com/{user_id}/{scan_id}/back.jpg"
                }

                # Extract quality and angle data from pipeline metadata
                image_quality = {
                    angle: ImageQuality(
                        quality_score=pipeline_metadata['image_quality'][angle],
                        is_valid=True,
                        width=1024,  # After preprocessing
                        height=1024
                    )
                    for angle in ["front", "side", "back"]
                }

                detected_angles = {
                    angle: PhotoAngle(
                        angle_type=AngleType[metadata['angle'].upper()],
                        confidence=metadata['confidence'],
                        detected_pose_keypoints=17,
                        is_standing=True
                    )
                    for angle, metadata in pipeline_metadata['angle_detection'].items()
                }

                # Assemble complete scan result
                scan_result = assemble_scan_result(
                    user_id=user_id,
                    measurements=measurements,
                    confidence=confidence,
                    image_urls=image_urls,
                    image_quality=image_quality,
                    detected_angles=detected_angles,
                    height_cm=height_cm or 178,
                    gender=gender or "male",
                    processing_time_sec=25.0
                )

                # Override scan_id
                scan_result.scan_id = scan_id

            # Step 3: Save to Firestore
            async with optimizer.profile("save_to_firestore"):
                success, error_msg = await firestore_client.save_scan_result(scan_result)

                if not success:
                    logger.error(f"Failed to save scan: {error_msg}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to save scan results"
                    )

        # Estimate processing time
        estimated_time = ImageOptimizer.estimate_processing_time(3, 1.0)

        logger.info(f"Scan {scan_id} created successfully")

        return ScanCreatedResponse(
            scan_id=scan_id,
            status=ScanStatus.COMPLETED,
            message="Scan created successfully",
            estimated_processing_time_sec=estimated_time
        )

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Create Scan",
            user_id=user_id,
            scan_id=scan_id,
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scan: {str(e)}"
        )


# ============================================================
# GET /api/v1/scans/{scan_id} - Get scan results
# ============================================================

@router.get(
    "/scans/{scan_id}",
    response_model=DetailedScanResponse,
    summary="Get scan results",
    description="Retrieve complete body scan results by scan ID"
)
async def get_scan(scan_id: str):
    """Get detailed scan results"""

    firestore_client = get_firestore_client()
    error_handler = get_error_handler()

    try:
        # Extract user_id from scan_id (in production, get from token)
        # For now, we'll need to query Firestore
        # TODO: Implement proper user extraction from JWT

        # For demonstration, we'll return a 404 if scan not found
        # In production, this would query Firestore

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Scan retrieval endpoint not yet implemented. Use Firestore client directly."
        )

    except HTTPException:
        raise
    except Exception as e:
        await error_handler.log_error(
            error=e,
            step="Get Scan",
            scan_id=scan_id,
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan: {str(e)}"
        )
