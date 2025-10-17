"""
Pydantic schemas for Nutrition Agent
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime, date


# ===== ENUMS =====

class NutritionGoal(str, Enum):
    """User's nutrition goal"""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    RECOMP = "recomposition"  # Lose fat + gain muscle


class ActivityLevel(str, Enum):
    """Physical activity level"""
    SEDENTARY = "sedentary"              # Little/no exercise
    LIGHTLY_ACTIVE = "lightly_active"    # 1-3 days/week
    MODERATELY_ACTIVE = "moderately_active"  # 3-5 days/week
    VERY_ACTIVE = "very_active"          # 6-7 days/week
    EXTRA_ACTIVE = "extra_active"        # 2x per day + physical job


class MealType(str, Enum):
    """Type of meal"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"


class DietaryRestriction(str, Enum):
    """Dietary restrictions"""
    NONE = "none"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    HALAL = "halal"
    KOSHER = "kosher"


# ===== USER PREFERENCES =====

class UserPreferences(BaseModel):
    """User preferences for meal planning"""
    dietary_restrictions: List[DietaryRestriction] = [DietaryRestriction.NONE]
    allergies: List[str] = []
    disliked_foods: List[str] = []
    preferred_cuisines: List[str] = ["american", "italian", "asian"]
    meals_per_day: int = Field(default=3, ge=1, le=8)
    cooking_time_minutes: Optional[int] = Field(default=30, ge=5, le=120)
    budget_per_day_usd: Optional[float] = Field(default=None, ge=5, le=200)


# ===== BODY COMPOSITION =====

class BodyComposition(BaseModel):
    """Body composition from photo analysis"""
    user_id: str
    weight_kg: float = Field(ge=30, le=300)
    height_cm: float = Field(ge=120, le=250)
    body_fat_percent: float = Field(ge=3, le=60)
    lean_mass_kg: float = Field(ge=20, le=200)
    age: int = Field(ge=13, le=120)
    gender: str = Field(pattern="^(male|female|other)$")
    scan_date: datetime


# ===== WHOOP DATA =====

class WHOOPMetrics(BaseModel):
    """WHOOP recovery metrics"""
    user_id: str
    recovery_score: float = Field(ge=0, le=100)
    strain_score: float = Field(ge=0, le=21)
    sleep_hours: float = Field(ge=0, le=24)
    hrv_ms: Optional[float] = Field(default=None, ge=0)
    resting_hr_bpm: Optional[int] = Field(default=None, ge=30, le=200)
    date: date


# ===== MACROS =====

class MacroProfile(BaseModel):
    """Daily macro targets"""
    calories: float = Field(ge=800, le=6000)
    protein_g: float = Field(ge=50, le=500)
    carbs_g: float = Field(ge=50, le=800)
    fat_g: float = Field(ge=20, le=300)
    fiber_g: Optional[float] = Field(default=25, ge=10, le=100)

    # Calculated fields
    protein_percent: float = Field(ge=0.10, le=0.50)
    carbs_percent: float = Field(ge=0.20, le=0.70)
    fat_percent: float = Field(ge=0.15, le=0.50)

    # Goal context
    goal: NutritionGoal
    tdee: float  # Total daily energy expenditure
    deficit_surplus: int  # Positive for surplus, negative for deficit

    class Config:
        json_schema_extra = {
            "example": {
                "calories": 2200,
                "protein_g": 165,
                "carbs_g": 220,
                "fat_g": 73,
                "fiber_g": 30,
                "protein_percent": 0.30,
                "carbs_percent": 0.40,
                "fat_percent": 0.30,
                "goal": "muscle_gain",
                "tdee": 2000,
                "deficit_surplus": 200
            }
        }


# ===== FOOD & NUTRITION =====

class Food(BaseModel):
    """Individual food item"""
    name: str
    serving_size: str
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    fiber_g: Optional[float] = Field(default=0, ge=0)
    food_id: Optional[str] = None  # External DB ID


class Meal(BaseModel):
    """Single meal with foods"""
    name: str
    meal_type: MealType
    foods: List[Food]
    time: Optional[str] = None  # e.g., "08:00", "12:30"

    # Aggregated macros
    total_calories: float = Field(ge=0)
    total_protein_g: float = Field(ge=0)
    total_carbs_g: float = Field(ge=0)
    total_fat_g: float = Field(ge=0)

    notes: Optional[str] = None


# ===== RECIPES =====

class Ingredient(BaseModel):
    """Recipe ingredient"""
    name: str
    amount: str  # e.g., "2 cups", "150g"
    food: Optional[Food] = None


class Recipe(BaseModel):
    """Complete recipe with instructions"""
    name: str
    description: Optional[str] = None
    meal_type: MealType
    ingredients: List[Ingredient]
    instructions: List[str]
    prep_time_minutes: int = Field(ge=0, le=120)
    cook_time_minutes: int = Field(ge=0, le=240)
    servings: int = Field(ge=1, le=12)

    # Nutrition per serving
    calories_per_serving: float
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float

    # Metadata
    cuisine: Optional[str] = None
    difficulty: Optional[str] = Field(default="medium", pattern="^(easy|medium|hard)$")
    tags: List[str] = []
    recipe_url: Optional[str] = None


# ===== MEAL PLANS =====

class DailyPlan(BaseModel):
    """Complete daily meal plan"""
    user_id: str
    date: date
    goal: NutritionGoal
    macro_targets: MacroProfile
    meals: List[Meal]

    # Actual totals
    actual_calories: float
    actual_protein_g: float
    actual_carbs_g: float
    actual_fat_g: float

    # Accuracy metrics
    calorie_accuracy_percent: float  # How close to target
    macro_balance_score: float = Field(ge=0, le=1.0)  # 0-1, how balanced

    # Context
    recovery_score: Optional[float] = None  # From WHOOP
    notes: Optional[str] = None


class WeeklyPlan(BaseModel):
    """Weekly meal prep plan"""
    user_id: str
    start_date: date
    end_date: date
    daily_plans: List[DailyPlan]

    # Shopping list
    shopping_list: Dict[str, str]  # {ingredient: amount}
    estimated_cost_usd: Optional[float] = None

    # Batch cooking suggestions
    batch_recipes: List[Recipe] = []
    prep_time_total_minutes: Optional[int] = None


# ===== AGENT OUTPUTS =====

class MacroCalculation(BaseModel):
    """Output from macro calculator agent"""
    user_id: str
    body_composition: BodyComposition
    activity_level: ActivityLevel
    goal: NutritionGoal
    recovery_score: Optional[float] = None

    # Calculated values
    bmr: float  # Basal metabolic rate
    tdee: float  # Total daily energy expenditure
    target_calories: float
    macro_profile: MacroProfile

    # Reasoning
    calculation_notes: str
    timestamp: datetime


class MealPlanSuggestion(BaseModel):
    """Output from meal planner agent"""
    meal_structure: List[Meal]
    matches_macros: bool
    macro_deviation_percent: float
    suggestions: List[str]  # Tips for the user


class RecipeRecommendation(BaseModel):
    """Output from recipe suggester agent"""
    recipes: List[Recipe]
    match_score: float = Field(ge=0, le=1.0)
    reasoning: str
