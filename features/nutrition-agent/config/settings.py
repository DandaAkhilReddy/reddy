"""
Configuration for Nutrition Agent
"""
from pydantic_settings import BaseSettings
from typing import Optional


class NutritionAgentSettings(BaseSettings):
    """Settings for nutrition agent system"""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000

    # Agent Configuration
    agent_max_iterations: int = 10
    agent_timeout: int = 60
    agent_verbose: bool = True

    # Nutrition Database API (optional)
    nutritionix_api_key: Optional[str] = None
    nutritionix_app_id: Optional[str] = None
    usda_api_key: Optional[str] = None

    # Integration Endpoints
    photo_analysis_api: str = "http://localhost:7000/api/photoanalysis"
    whoop_api: str = "http://localhost:7000/api/whoop"

    # Meal Planning Defaults
    default_meals_per_day: int = 3
    default_protein_ratio: float = 0.30  # 30% of calories
    default_carb_ratio: float = 0.40     # 40% of calories
    default_fat_ratio: float = 0.30      # 30% of calories

    # Activity Multipliers (for TDEE calculation)
    sedentary_multiplier: float = 1.2
    lightly_active_multiplier: float = 1.375
    moderately_active_multiplier: float = 1.55
    very_active_multiplier: float = 1.725
    extra_active_multiplier: float = 1.9

    # Application Config
    app_env: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = NutritionAgentSettings()
