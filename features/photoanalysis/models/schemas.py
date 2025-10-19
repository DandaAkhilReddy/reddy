"""
Pydantic models for data validation and API schemas
Implements the complete data structure for the 20-step analysis
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BodyType(str, Enum):
    """Body type classifications (Step 14)"""
    VTAPER = "V-Taper"
    CLASSIC = "Classic"
    RECTANGULAR = "Rectangular"
    APPLE = "Apple"
    PEAR = "Pear"
    BALANCED = "Balanced"


class AngleType(str, Enum):
    """Photo angle classifications (Step 3)"""
    FRONT = "front"
    BACK = "back"
    SIDE = "side"
    UNKNOWN = "unknown"


class ImageQuality(BaseModel):
    """Image quality metrics (Step 1)"""
    width: int
    height: int
    file_size_kb: float
    format: str
    sharpness_score: float
    has_exif: bool
    orientation: Optional[int] = None
    is_valid: bool
    quality_score: float = Field(ge=0, le=100)


class PhotoAngle(BaseModel):
    """Photo angle detection result (Step 3)"""
    angle_type: AngleType
    confidence: float = Field(ge=0, le=1)
    detected_pose_keypoints: int
    is_standing: bool


class BodyMeasurements(BaseModel):
    """Anthropometric measurements from AI analysis (Steps 6-10)"""
    # Core circumference measurements (cm)
    chest_circumference_cm: float = Field(ge=50, le=200)
    waist_circumference_cm: float = Field(ge=50, le=200)
    hip_circumference_cm: float = Field(ge=50, le=200)

    # Limb measurements (cm)
    bicep_circumference_cm: float = Field(ge=20, le=60)
    thigh_circumference_cm: float = Field(ge=30, le=100)
    calf_circumference_cm: Optional[float] = Field(None, ge=20, le=60)

    # Width measurements (cm)
    shoulder_width_cm: Optional[float] = Field(None, ge=30, le=80)

    # Body composition
    body_fat_percent: float = Field(ge=3, le=60)
    estimated_weight_kg: Optional[float] = Field(None, ge=30, le=300)

    # Qualitative assessments
    posture_rating: float = Field(ge=0, le=10)
    muscle_definition: Optional[str] = None

    @validator('waist_circumference_cm')
    def waist_reasonable(cls, v, values):
        """Ensure waist is reasonable relative to chest"""
        if 'chest_circumference_cm' in values:
            chest = values['chest_circumference_cm']
            if v > chest * 1.5:  # Waist shouldn't be 50% larger than chest
                raise ValueError(f"Waist ({v}cm) seems too large relative to chest ({chest}cm)")
        return v


class BodyRatios(BaseModel):
    """Calculated body ratios (Steps 11-12)"""
    # Golden Ratio & Adonis Index (Step 11)
    shoulder_to_waist_ratio: float
    adonis_index: float
    golden_ratio_deviation: float

    # Symmetry ratios (Step 12)
    waist_to_hip_ratio: float
    chest_to_waist_ratio: float
    arm_to_chest_ratio: float
    leg_to_torso_ratio: Optional[float] = None

    # Overall symmetry
    symmetry_score: float = Field(ge=0, le=100)


class AestheticScore(BaseModel):
    """Comprehensive aesthetic scoring (Step 14)"""
    overall_score: float = Field(ge=0, le=100)

    # Component scores
    golden_ratio_score: float = Field(ge=0, le=40)
    symmetry_score: float = Field(ge=0, le=30)
    composition_score: float = Field(ge=0, le=20)
    posture_score: float = Field(ge=0, le=10)

    # Classification
    body_type: BodyType
    body_type_confidence: float = Field(ge=0, le=1)


class WHOOPData(BaseModel):
    """WHOOP wearable data integration (Step 4, 18)"""
    user_id: str
    recovery_score: Optional[float] = Field(None, ge=0, le=100)
    strain_score: Optional[float] = Field(None, ge=0, le=21)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    hrv_ms: Optional[float] = None
    resting_heart_rate: Optional[int] = None
    last_updated: Optional[datetime] = None
    has_data: bool = False


class PersonalizedRecommendations(BaseModel):
    """AI-generated insights and recommendations (Step 18)"""
    workout_plan: str
    nutrition_plan: str
    recovery_advice: Optional[str] = None
    progress_comparison: Optional[str] = None
    key_focus_areas: List[str]
    estimated_timeline_weeks: Optional[int] = None


class ConfidenceMetrics(BaseModel):
    """Confidence scoring (Step 9)"""
    overall_score: float = Field(ge=0, le=1)
    photo_count_factor: float = Field(ge=0, le=1)
    consistency_factor: float = Field(ge=0, le=1)
    ai_confidence_factor: float = Field(ge=0, le=1)
    data_completeness_factor: float = Field(ge=0, le=1)
    validation_quality_factor: float = Field(ge=0, le=1)
    meets_threshold: bool
    factors_breakdown: Dict[str, Any]

    # Backward compatibility properties
    @property
    def overall_confidence(self) -> float:
        """Alias for overall_score (backward compatibility)"""
        return self.overall_score

    @property
    def measurement_completeness(self) -> float:
        """Alias for data_completeness_factor (backward compatibility)"""
        return self.data_completeness_factor


class ScanResult(BaseModel):
    """Complete scan result object (Step 16)"""
    # Identification
    scan_id: str
    body_signature_id: str  # Format: {BodyType}-BF{%}-{Hash}-AI{ratio}
    user_id: str
    timestamp: datetime

    # Image references
    image_urls: Dict[str, str]  # {angle: url}
    image_quality: Dict[str, ImageQuality]
    detected_angles: Dict[str, PhotoAngle]

    # Measurements & Analysis
    measurements: BodyMeasurements
    ratios: BodyRatios
    aesthetic_score: AestheticScore
    composition_hash: str  # 6-char SHA256 hash (Step 13)

    # External Data
    whoop_data: Optional[WHOOPData] = None

    # Confidence & Metadata
    confidence: ConfidenceMetrics
    processing_time_sec: float
    api_version: str = "2.0"

    # Personalization
    recommendations: Optional[PersonalizedRecommendations] = None

    # Legacy compatibility
    legacy_health_score: Optional[float] = None


class ScanRequest(BaseModel):
    """API request for body scan analysis"""
    user_id: str
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    age: Optional[int] = Field(None, ge=13, le=120)
    gender: Optional[str] = None
    fitness_goal: Optional[str] = None
    include_recommendations: bool = True
    whoop_access_token: Optional[str] = None


class ScanResponse(BaseModel):
    """API response for body scan"""
    success: bool
    scan_result: Optional[ScanResult] = None
    error: Optional[str] = None
    warnings: List[str] = []


class UserProfile(BaseModel):
    """User profile data (Step 4 validation)"""
    uid: str
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_goal: Optional[str] = None
    total_scans: int = 0
    last_scan_at: Optional[datetime] = None
    whoop_connected: bool = False
    whoop_user_id: Optional[str] = None


class ErrorLog(BaseModel):
    """Error logging structure (Step 19)"""
    error_id: str
    timestamp: datetime
    step: str
    error_type: str
    error_message: str
    user_id: Optional[str] = None
    scan_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = {}
