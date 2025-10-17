"""
Configuration management for ReddyFit Body Scan Analysis
Loads environment variables and provides typed settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with validation"""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 2000
    openai_timeout: int = 45

    # Firebase Configuration
    firebase_project_id: str
    firebase_storage_bucket: str
    firebase_credentials_path: Path

    # WHOOP API Configuration
    whoop_client_id: Optional[str] = None
    whoop_client_secret: Optional[str] = None
    whoop_redirect_uri: str = "http://localhost:8000/auth/whoop/callback"
    whoop_api_base_url: str = "https://api.prod.whoop.com/developer"

    # Application Configuration
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # Sentry Monitoring
    sentry_dsn: Optional[str] = None

    # Image Processing Limits
    max_image_size_mb: int = 10
    min_image_size_kb: int = 100
    min_image_resolution: tuple = (480, 640)
    max_image_resolution: tuple = (4000, 6000)
    optimal_image_size: int = 1024  # Max dimension for processing
    image_quality: int = 85  # JPEG compression quality

    # Performance Settings
    max_processing_time_sec: int = 45
    target_processing_time_sec: int = 30
    api_retry_attempts: int = 3
    api_retry_delay: float = 1.0  # Initial delay in seconds

    # Analysis Thresholds
    min_confidence_score: float = 0.70
    min_sharpness_score: float = 50.0
    golden_ratio: float = 1.618

    # Body Type Classification Thresholds
    vtaper_min_shoulder_waist_ratio: float = 1.4
    vtaper_max_body_fat: float = 18.0
    apple_min_waist_hip_ratio: float = 0.95
    pear_max_waist_hip_ratio: float = 0.80

    # Aesthetic Score Weights
    weight_golden_ratio: float = 0.40
    weight_symmetry: float = 0.30
    weight_composition: float = 0.20
    weight_posture: float = 0.10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Validate critical settings on import
def validate_settings():
    """Validate that critical settings are properly configured"""
    errors = []

    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        errors.append("OPENAI_API_KEY is not configured")

    if not settings.firebase_credentials_path.exists():
        errors.append(f"Firebase credentials file not found: {settings.firebase_credentials_path}")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))


# Validate on module import if not in test mode
if settings.app_env != "test":
    try:
        validate_settings()
    except ValueError as e:
        if settings.debug:
            print(f"WARNING: {e}")
        else:
            raise
