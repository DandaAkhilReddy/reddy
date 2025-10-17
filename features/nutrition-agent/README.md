# ReddyFit Nutrition Agent 🥗🤖

AI-powered nutrition planning system that generates personalized daily meal plans based on body composition, recovery metrics, and user preferences.

## Overview

The Nutrition Agent is a multi-agent AI system built with **LangChain**, **LangGraph**, and **OpenAI GPT-4** that automates personalized nutrition planning by:

1. **Calculating macro targets** based on body composition (from photo analysis), activity level, and goals
2. **Planning balanced meals** that hit macro targets while respecting dietary restrictions
3. **Suggesting recipes** that match meal requirements and user preferences

### Key Features

✅ **Recovery-Aware Nutrition** - Integrates WHOOP recovery data to adjust calories dynamically
✅ **Body Composition Integration** - Uses photo analysis data for accurate BMR calculations
✅ **Multi-Factor Macro Calculation** - BMR, TDEE, activity multipliers, recovery adjustments
✅ **Smart Meal Planning** - Splits macros across 3-6 meals with food database search
✅ **Recipe Recommendations** - Suggests recipes matching macro targets and preferences
✅ **Dietary Restriction Support** - Vegan, vegetarian, keto, paleo, gluten-free, etc.
✅ **LangGraph Workflow** - Orchestrates 3 agents sequentially with error handling

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Daily Plan Workflow                        │
│                      (LangGraph)                             │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Macro      │    │     Meal     │    │   Recipe     │
│  Calculator  │───▶│   Planner    │───▶│  Suggester   │
│    Agent     │    │    Agent     │    │    Agent     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Body Metrics │    │  Nutrition   │    │   Recipe     │
│ Photo API    │    │   Database   │    │   Database   │
│ WHOOP API    │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Agent Components

1. **Macro Calculator Agent** (`agents/macro_calculator.py`)
   - Fetches body composition from photo analysis
   - Retrieves WHOOP recovery metrics
   - Calculates BMR using Katch-McArdle formula (lean mass based)
   - Calculates TDEE with activity multipliers
   - Adjusts for nutrition goal (deficit/surplus)
   - Adjusts for recovery score (low recovery → more calories)
   - Returns personalized `MacroProfile`

2. **Meal Planner Agent** (`agents/meal_planner.py`)
   - Splits macros across 3-6 meals (breakfast, lunch, dinner, snacks)
   - Searches food database for macro-matching foods
   - Builds balanced meals (protein + carbs + fats + veggies)
   - Respects dietary restrictions and allergies
   - Validates totals match targets (within 5%)
   - Returns structured `MealPlanSuggestion`

3. **Recipe Suggester Agent** (`agents/recipe_suggester.py`)
   - Finds recipes matching meal macro targets
   - Filters by dietary restrictions and prep time
   - Scores recipes by macro accuracy (protein > carbs > fats)
   - Returns top 2-3 recipes per meal
   - Returns `RecipeRecommendation` with match scores

### Workflow Orchestration

**LangGraph State Machine** (`workflows/daily_plan.py`)

Sequential execution with error handling:
```
1. Calculate Macros → MacroCalculation
2. Plan Meals → MealPlanSuggestion
3. Suggest Recipes → RecipeRecommendation
4. Assemble → DailyPlan
```

---

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key
- Photo analysis API running (localhost:7000)
- WHOOP API (optional, uses mock data if unavailable)

### Setup

```bash
# Navigate to feature directory
cd features/nutrition-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.7

# Agent Configuration
AGENT_VERBOSE=true
AGENT_MAX_ITERATIONS=10

# Integration Endpoints
PHOTO_ANALYSIS_API=http://localhost:7000/api/photoanalysis
WHOOP_API=http://localhost:7000/api/whoop

# Optional: Nutrition APIs (not yet implemented)
NUTRITIONIX_APP_ID=your_app_id
NUTRITIONIX_API_KEY=your_api_key
USDA_API_KEY=your_usda_key
```

---

## Usage

### Quick Start

```python
import asyncio
from models.schemas import ActivityLevel, NutritionGoal, UserPreferences
from workflows.daily_plan import generate_daily_plan

async def main():
    # Define user preferences
    preferences = UserPreferences(
        meals_per_day=4,
        dietary_restrictions=[],
        allergies=[],
        disliked_foods=["liver"],
        max_prep_time_minutes=45
    )

    # Generate daily plan
    plan = await generate_daily_plan(
        user_id="user_123",
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=NutritionGoal.WEIGHT_LOSS,
        preferences=preferences
    )

    # Access results
    print(f"Calorie Target: {plan.macro_targets.calories} cal")
    print(f"Meals: {len(plan.meals)}")
    print(f"Accuracy: {plan.macro_balance_score * 100:.1f}%")

asyncio.run(main())
```

### Testing

Run the standalone test suite:

```bash
python test_workflow.py
```

This runs 4 test scenarios:
1. Weight Loss Plan (4 meals, moderate activity)
2. Muscle Gain Plan (5 meals, very active)
3. Vegan Diet Plan (3 meals, dietary restrictions)
4. Body Recomposition (4 meals, high protein)

### Using Individual Agents

```python
# Just calculate macros
from agents.macro_calculator import calculate_user_macros

macro_calc = await calculate_user_macros(
    user_id="user_123",
    activity_level=ActivityLevel.MODERATELY_ACTIVE,
    goal=NutritionGoal.MUSCLE_GAIN
)

print(f"TDEE: {macro_calc.tdee} cal")
print(f"Target: {macro_calc.target_calories} cal")
print(f"Protein: {macro_calc.macro_profile.protein_g}g")
```

```python
# Just plan meals
from agents.meal_planner import plan_daily_meals

meal_plan = await plan_daily_meals(
    user_id="user_123",
    macro_profile=macro_calc.macro_profile,
    preferences=preferences
)

for meal in meal_plan.meals:
    print(f"{meal.name}: {meal.calories} cal")
```

```python
# Just suggest recipes
from agents.recipe_suggester import suggest_meal_recipes

recipes = await suggest_meal_recipes(
    user_id="user_123",
    meals=meal_plan.meals,
    preferences=preferences
)

print(f"Match Score: {recipes.overall_match_score * 100}%")
```

---

## Data Models

### Core Schemas (`models/schemas.py`)

**MacroProfile**
```python
MacroProfile(
    calories=2000,           # Daily calorie target
    protein_g=150,           # Protein grams
    carbs_g=200,             # Carb grams
    fat_g=67,                # Fat grams
    protein_percent=0.30,    # 30% calories from protein
    carbs_percent=0.40,      # 40% from carbs
    fat_percent=0.30,        # 30% from fats
    goal=NutritionGoal.MUSCLE_GAIN,
    tdee=2300,               # Total daily energy expenditure
    deficit_surplus=300      # +300 cal surplus for muscle gain
)
```

**DailyPlan**
```python
DailyPlan(
    user_id="user_123",
    date=date.today(),
    goal=NutritionGoal.WEIGHT_LOSS,
    macro_targets=MacroProfile(...),
    meals=[...],              # List of Meal objects
    recipe_suggestions={...}, # Dict[meal_name, List[Recipe]]
    actual_calories=1950,     # Sum of all meals
    actual_protein_g=148,
    calorie_accuracy_percent=97.5,
    macro_balance_score=0.96
)
```

**UserPreferences**
```python
UserPreferences(
    meals_per_day=4,
    dietary_restrictions=[DietaryRestriction.VEGAN],
    allergies=["nuts", "shellfish"],
    disliked_foods=["liver", "anchovies"],
    max_prep_time_minutes=45
)
```

---

## Technical Details

### BMR Calculation

**Katch-McArdle Formula** (used by default, requires body composition):
```
BMR = 370 + (21.6 × lean_mass_kg)
```

**Mifflin-St Jeor Formula** (fallback, if lean mass unavailable):
```
Men:   BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
Women: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161
```

### TDEE Activity Multipliers

```python
sedentary         = 1.2   # Little/no exercise
lightly_active    = 1.375 # 1-3 days/week
moderately_active = 1.55  # 3-5 days/week
very_active       = 1.725 # 6-7 days/week
extra_active      = 1.9   # 2x/day + physical job
```

### Recovery-Based Calorie Adjustment

WHOOP recovery score zones:

| Recovery Score | Zone   | Adjustment                      |
|----------------|--------|---------------------------------|
| 67-100         | Green  | Proceed as planned or +5%       |
| 34-66          | Yellow | +5% if weight loss goal         |
| 0-33           | Red    | +10-15% to prioritize recovery  |

**Logic**: Low recovery means body needs more calories for repair and adaptation. High recovery allows pushing harder or maintaining deficit.

### Macro Split Guidelines

**Weight Loss** (calorie deficit):
- Protein: 35% (higher to preserve muscle)
- Carbs: 35%
- Fats: 30%

**Muscle Gain** (calorie surplus):
- Protein: 30%
- Carbs: 40% (fuel for training)
- Fats: 30%

**Maintenance / Recomposition**:
- Protein: 30-35%
- Carbs: 35-40%
- Fats: 25-30%

---

## API Integration

### Photo Analysis Integration

```python
# Fetches latest body scan
GET /api/photoanalysis/scans/user/{user_id}/latest

Response:
{
  "user_id": "user_123",
  "weight_kg": 75.0,
  "height_cm": 175.0,
  "body_fat_percent": 18.0,
  "lean_mass_kg": 61.5,
  "age": 28,
  "gender": "male",
  "scan_date": "2025-10-17T10:30:00Z"
}
```

### WHOOP Integration

```python
# Fetches recovery metrics
GET /api/whoop/{user_id}?date=2025-10-17

Response:
{
  "user_id": "user_123",
  "recovery_score": 75.0,    # 0-100
  "strain_score": 12.5,      # 0-21
  "sleep_hours": 7.5,
  "hrv_ms": 65.0,
  "resting_hr_bpm": 58,
  "date": "2025-10-17"
}
```

---

## Roadmap

### Phase 1: Foundation ✅ (Complete)
- [x] Project structure
- [x] Pydantic schemas
- [x] Configuration system
- [x] Mock data for development

### Phase 2: Core Agents ✅ (Complete)
- [x] Macro Calculator Agent
- [x] Meal Planner Agent
- [x] Recipe Suggester Agent
- [x] LangGraph workflow

### Phase 3: Testing & Docs ✅ (Complete)
- [x] Standalone test script
- [x] Unit tests
- [x] README documentation

### Phase 4: Production (Upcoming)
- [ ] Real food database integration (Nutritionix, USDA)
- [ ] Recipe database expansion (100+ recipes)
- [ ] FastAPI REST endpoints
- [ ] Database persistence (Firebase)
- [ ] Meal tracking and logging
- [ ] Weekly plan generation
- [ ] Grocery list generation
- [ ] Meal prep instructions

### Phase 5: Advanced Features (Future)
- [ ] Photo-based food logging
- [ ] Restaurant menu analysis
- [ ] Macro tracking with automatic adjustments
- [ ] Social features (share meal plans)
- [ ] AI cooking assistant
- [ ] Supplement recommendations

---

## Contributing

### Code Structure

```
features/nutrition-agent/
├── config/
│   └── settings.py          # Configuration with Pydantic
├── models/
│   └── schemas.py           # All Pydantic data models (400+ lines)
├── agents/
│   ├── macro_calculator.py  # Agent 1: Macro calculation
│   ├── meal_planner.py      # Agent 2: Meal planning
│   └── recipe_suggester.py  # Agent 3: Recipe suggestions
├── workflows/
│   └── daily_plan.py        # LangGraph workflow orchestration
├── tools/
│   ├── body_metrics.py      # Photo analysis integration
│   ├── recovery_data.py     # WHOOP integration
│   └── nutrition_db.py      # Food/recipe database
├── tests/
│   └── test_*.py            # Unit tests (pytest)
├── test_workflow.py         # End-to-end test script
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

### Adding New Foods

Edit `tools/nutrition_db.py`:

```python
MOCK_FOODS.append(
    Food(
        name="Tilapia (baked)",
        serving_size="100g",
        calories=128,
        protein_g=26,
        carbs_g=0,
        fat_g=2.7,
        fiber_g=0
    )
)
```

### Adding New Recipes

```python
MOCK_RECIPES.append(
    Recipe(
        name="Protein Pancakes",
        meal_type=MealType.BREAKFAST,
        ingredients=[...],
        instructions=[...],
        prep_time_minutes=10,
        cook_time_minutes=15,
        calories_per_serving=350,
        protein_per_serving=30,
        carbs_per_serving=40,
        fat_per_serving=8,
        tags=["high-protein", "breakfast", "easy"]
    )
)
```

---

## Troubleshooting

### Agent Taking Too Long

Reduce `AGENT_MAX_ITERATIONS` in `.env`:
```env
AGENT_MAX_ITERATIONS=5  # Default: 10
```

### Macro Targets Too High/Low

Check:
1. Body composition data is accurate
2. Activity level matches actual activity
3. Recovery score is being fetched properly

### No Recipes Found

The mock database has limited recipes. Suggestions:
1. Increase `tolerance_percent` in `find_recipes_matching_macros()`
2. Add more recipes to `MOCK_RECIPES`
3. Integrate real recipe API (future phase)

### API Connection Errors

Mock data is used by default. To fix:
1. Ensure photo analysis API is running on localhost:7000
2. Ensure WHOOP API is configured
3. Check API keys in `.env`

---

## License

Part of the ReddyFit platform. See main project LICENSE.

---

## Contact

For questions or issues:
- GitHub Issues: https://github.com/DandaAkhilReddy/reddy/issues
- Feature requests welcome!

---

**Built with**:
- 🤖 OpenAI GPT-4-turbo
- 🔗 LangChain & LangGraph
- ✅ Pydantic for data validation
- 🐍 Python 3.10+

---

**Status**: ✅ Production-ready foundation (mock data)
**Next**: Real API integrations & FastAPI endpoints
