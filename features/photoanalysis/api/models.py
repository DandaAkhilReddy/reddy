"""
API Request/Response Models
Pydantic models specific to API layer (separate from internal schemas)
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


# ============================================================
# ENUMS
# ============================================================

class FitnessGoal(str, Enum):
    """Fitness goal options"""
    MUSCLE_GAIN = "muscle_gain"
    FAT_LOSS = "fat_loss"
    ATHLETIC_PERFORMANCE = "athletic"
    MAINTENANCE = "maintain"


class SortOrder(str, Enum):
    """Sort order for lists"""
    ASC = "asc"
    DESC = "desc"


# ============================================================
# SCAN REQUESTS
# ============================================================

class CreateScanRequest(BaseModel):
    """Request to create a new scan (multipart form data)"""
    user_id: str = Field(..., description="User identifier")
    height_cm: Optional[float] = Field(None, description="User height in cm", ge=100, le=250)
    gender: Optional[str] = Field(None, description="User gender (male/female)")
    fitness_goal: Optional[FitnessGoal] = Field(
        FitnessGoal.MAINTENANCE,
        description="Primary fitness goal"
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "height_cm": 178,
                "gender": "male",
                "fitness_goal": "muscle_gain"
            }
        }


# ============================================================
# SCAN RESPONSES
# ============================================================

class ScanStatus(str, Enum):
    """Scan processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SimpleScanResponse(BaseModel):
    """Simplified scan response (for lists)"""
    scan_id: str
    body_signature_id: str
    timestamp: datetime
    body_type: str
    body_fat_percent: float
    overall_score: float
    confidence: float

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_1234567890",
                "body_signature_id": "VTaper-BF12.5-A3F7C2-AI1.56",
                "timestamp": "2025-10-17T10:30:00Z",
                "body_type": "V-Taper",
                "body_fat_percent": 12.5,
                "overall_score": 85.0,
                "confidence": 0.92
            }
        }


class DetailedScanResponse(BaseModel):
    """Detailed scan response (single scan)"""
    scan_id: str
    body_signature_id: str
    user_id: str
    timestamp: datetime

    # Body metrics
    measurements: Dict[str, float]
    ratios: Dict[str, float]
    aesthetic_score: Dict[str, Any]

    # Metadata
    confidence: Dict[str, Any]
    processing_time_sec: float
    image_urls: Dict[str, str]

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_1234567890",
                "body_signature_id": "VTaper-BF12.5-A3F7C2-AI1.56",
                "user_id": "user_abc123",
                "timestamp": "2025-10-17T10:30:00Z",
                "measurements": {
                    "chest_cm": 105.0,
                    "waist_cm": 80.0,
                    "body_fat_percent": 12.5
                },
                "ratios": {
                    "adonis_index": 1.56,
                    "symmetry_score": 85.0
                },
                "aesthetic_score": {
                    "overall_score": 85.0,
                    "body_type": "V-Taper"
                },
                "confidence": {
                    "overall_confidence": 0.92,
                    "is_reliable": True
                },
                "processing_time_sec": 28.5,
                "image_urls": {
                    "front": "https://storage.example.com/front.jpg"
                }
            }
        }


class ScanCreatedResponse(BaseModel):
    """Response after creating a scan"""
    scan_id: str
    status: ScanStatus
    message: str
    estimated_processing_time_sec: float

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_1234567890",
                "status": "processing",
                "message": "Scan created successfully. Processing photos...",
                "estimated_processing_time_sec": 25.0
            }
        }


# ============================================================
# RECOMMENDATION REQUESTS/RESPONSES
# ============================================================

class GenerateRecommendationsRequest(BaseModel):
    """Request to generate AI recommendations"""
    scan_id: str = Field(..., description="Scan ID to generate recommendations for")
    fitness_goal: FitnessGoal = Field(
        FitnessGoal.MAINTENANCE,
        description="Primary fitness goal"
    )
    dietary_restrictions: Optional[List[str]] = Field(
        default=[],
        description="List of dietary restrictions (vegan, keto, etc.)"
    )
    meals_per_day: Optional[int] = Field(
        default=3,
        description="Number of meals per day",
        ge=2,
        le=6
    )

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_1234567890",
                "fitness_goal": "muscle_gain",
                "dietary_restrictions": ["gluten_free"],
                "meals_per_day": 4
            }
        }


class RecommendationsResponse(BaseModel):
    """AI-generated recommendations response"""
    scan_id: str
    workout_plan: str
    nutrition_plan: str
    recovery_advice: Optional[str]
    key_focus_areas: List[str]
    estimated_timeline_weeks: int
    generated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "scan_id": "scan_1234567890",
                "workout_plan": "4-day Upper/Lower split focusing on shoulder width...",
                "nutrition_plan": "Daily macros: 2400 cal, 180g protein, 300g carbs, 70g fat...",
                "recovery_advice": "WHOOP recovery: 85% - High intensity workout recommended",
                "key_focus_areas": [
                    "Build wider shoulders",
                    "Maintain low body fat",
                    "Improve posture"
                ],
                "estimated_timeline_weeks": 28,
                "generated_at": "2025-10-17T10:35:00Z"
            }
        }


# ============================================================
# HISTORY REQUESTS/RESPONSES
# ============================================================

class ScanHistoryRequest(BaseModel):
    """Request for scan history"""
    limit: Optional[int] = Field(10, description="Max number of scans", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Pagination offset", ge=0)
    sort_order: Optional[SortOrder] = Field(SortOrder.DESC, description="Sort by timestamp")


class ScanHistoryResponse(BaseModel):
    """Response with scan history"""
    user_id: str
    total_scans: int
    scans: List[SimpleScanResponse]
    has_more: bool

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "total_scans": 15,
                "scans": [
                    {
                        "scan_id": "scan_latest",
                        "body_signature_id": "VTaper-BF12.5-A3F7C2-AI1.56",
                        "timestamp": "2025-10-17T10:30:00Z",
                        "body_type": "V-Taper",
                        "body_fat_percent": 12.5,
                        "overall_score": 85.0,
                        "confidence": 0.92
                    }
                ],
                "has_more": True
            }
        }


class ProgressComparisonRequest(BaseModel):
    """Request for progress comparison"""
    weeks_back: Optional[int] = Field(4, description="Weeks to look back", ge=1, le=52)


class ProgressComparisonResponse(BaseModel):
    """Response with progress comparison"""
    user_id: str
    time_between_scans_days: int
    changes: Dict[str, float]
    body_type_changed: bool
    progress_summary: List[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "time_between_scans_days": 28,
                "changes": {
                    "body_fat_change_percent": -1.5,
                    "aesthetic_score_change": 3.5,
                    "adonis_index_change": 0.08
                },
                "body_type_changed": False,
                "progress_summary": [
                    "Lost 1.5% body fat - Excellent!",
                    "Aesthetic score improved by 3.5 points"
                ]
            }
        }


# ============================================================
# HEALTH CHECK
# ============================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    checks: Dict[str, Dict[str, str]]
    error_statistics: Optional[Dict[str, int]]

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-17T10:30:00Z",
                "checks": {
                    "ai_api": {"status": "up", "message": "OK"},
                    "firestore": {"status": "up", "message": "OK"},
                    "sentry": {"status": "up"}
                },
                "error_statistics": {}
            }
        }


# ============================================================
# ERROR RESPONSES
# ============================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Any] = None
    request_id: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": ["Field 'user_id' is required"],
                "request_id": "req_1234567890"
            }
        }
