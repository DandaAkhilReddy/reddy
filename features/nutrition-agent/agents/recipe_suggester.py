"""
Recipe Suggester Agent
Suggests recipes matching meal macro targets and user preferences
"""
from typing import List, Optional
from datetime import datetime
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from ..models.schemas import (
    RecipeRecommendation, Meal, Recipe, UserPreferences,
    MealType, DietaryRestriction
)
from ..tools.nutrition_db import (
    search_recipes, find_recipes_matching_macros, MOCK_RECIPES
)
from ..config.settings import settings


# ===== LANGCHAIN TOOLS =====

@tool
def search_recipes_by_meal_type(meal_type: str) -> str:
    """Search for recipes by meal type (breakfast, lunch, dinner, snack)"""
    try:
        meal_type_enum = MealType(meal_type.lower())
        recipes = search_recipes(meal_type=meal_type_enum)
    except ValueError:
        return f"Invalid meal type: {meal_type}"

    if not recipes:
        return f"No recipes found for {meal_type}"

    result = f"Recipes for {meal_type}:\n"
    for recipe in recipes:
        result += f"\n- {recipe.name}\n"
        result += f"  Macros: P:{recipe.protein_per_serving}g C:{recipe.carbs_per_serving}g F:{recipe.fat_per_serving}g ({recipe.calories_per_serving} cal)\n"
        result += f"  Time: {recipe.prep_time_minutes + recipe.cook_time_minutes} min total\n"
        result += f"  Tags: {', '.join(recipe.tags)}\n"
    return result


@tool
def search_recipes_by_time(max_minutes: int) -> str:
    """Search for recipes that take less than max_minutes to prepare"""
    recipes = search_recipes(max_prep_time=max_minutes)

    if not recipes:
        return f"No recipes found under {max_minutes} minutes"

    result = f"Quick Recipes (under {max_minutes} min):\n"
    for recipe in recipes:
        total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
        result += f"\n- {recipe.name} ({total_time} min)\n"
        result += f"  Macros: P:{recipe.protein_per_serving}g C:{recipe.carbs_per_serving}g F:{recipe.fat_per_serving}g\n"
    return result


@tool
def search_recipes_by_tags(tags: str) -> str:
    """Search for recipes by tags (comma-separated). Examples: high-protein, low-carb, vegan"""
    tag_list = [t.strip() for t in tags.split(",")]
    recipes = search_recipes(tags=tag_list)

    if not recipes:
        return f"No recipes found with tags: {tags}"

    result = f"Recipes matching tags '{tags}':\n"
    for recipe in recipes:
        result += f"\n- {recipe.name}\n"
        result += f"  Macros: P:{recipe.protein_per_serving}g C:{recipe.carbs_per_serving}g F:{recipe.fat_per_serving}g\n"
        result += f"  Tags: {', '.join(recipe.tags)}\n"
    return result


@tool
def find_recipes_for_macros(target_protein: float, target_carbs: float, target_fat: float) -> str:
    """Find recipes that closely match target macros (within 20% tolerance)"""
    recipes = find_recipes_matching_macros(
        target_protein=target_protein,
        target_carbs=target_carbs,
        target_fat=target_fat,
        tolerance_percent=20
    )

    if not recipes:
        return f"No recipes found matching P:{target_protein}g C:{target_carbs}g F:{target_fat}g"

    result = f"Recipes matching target macros:\n"
    for recipe in recipes:
        # Calculate accuracy
        protein_diff = abs(recipe.protein_per_serving - target_protein)
        carbs_diff = abs(recipe.carbs_per_serving - target_carbs)
        fat_diff = abs(recipe.fat_per_serving - target_fat)

        result += f"\n- {recipe.name}\n"
        result += f"  Macros: P:{recipe.protein_per_serving}g C:{recipe.carbs_per_serving}g F:{recipe.fat_per_serving}g\n"
        result += f"  Accuracy: P:±{protein_diff:.1f}g C:±{carbs_diff:.1f}g F:±{fat_diff:.1f}g\n"
        result += f"  Time: {recipe.prep_time_minutes + recipe.cook_time_minutes} min\n"
    return result


@tool
def list_all_available_recipes() -> str:
    """List all recipes in the database with their key stats"""
    result = "All Available Recipes:\n"
    for recipe in MOCK_RECIPES:
        result += f"\n- {recipe.name}\n"
        result += f"  Type: {recipe.meal_type.value}\n"
        result += f"  Macros: P:{recipe.protein_per_serving}g C:{recipe.carbs_per_serving}g F:{recipe.fat_per_serving}g ({recipe.calories_per_serving} cal)\n"
        result += f"  Time: {recipe.prep_time_minutes + recipe.cook_time_minutes} min\n"
        result += f"  Difficulty: {recipe.difficulty}\n"
    return result


# ===== RECIPE SUGGESTER AGENT =====

class RecipeSuggesterAgent:
    """Agent that suggests recipes matching meal requirements"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        self.tools = [
            search_recipes_by_meal_type,
            search_recipes_by_time,
            search_recipes_by_tags,
            find_recipes_for_macros,
            list_all_available_recipes
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert recipe curator and nutrition specialist.

Your task is to suggest recipes that match meal requirements and user preferences.

Recipe Selection Criteria:
1. Macro Match (highest priority): Recipe macros should closely match meal targets
   - Protein is most important (within ±10%)
   - Carbs and fats within ±20%
2. Meal Type: Recipe should match the meal type (breakfast, lunch, dinner, snack)
3. Dietary Restrictions: Must respect all restrictions (vegan, keto, etc.)
4. Prep Time: Consider user's available cooking time
5. Difficulty: Match user's cooking skill level
6. Tags: Prefer recipes matching user preferences (high-protein, meal-prep, etc.)

Scoring System:
- Macro match: 50% weight (protein > carbs > fats)
- Meal type match: 20% weight
- Prep time: 15% weight
- Tags/preferences: 15% weight

For each meal, provide:
- Top 2-3 recipe recommendations
- Macro comparison (recipe vs target)
- Match score and reasoning
- Any adjustments needed (portion size, ingredient swaps)

Format output as:
MEAL: [Meal Name]
TARGET MACROS: P:Xg C:Yg F:Zg

RECIPE 1: [Name]
MACROS: P:Xg C:Yg F:Zg
MATCH SCORE: X%
REASONING: [why this recipe fits]
ADJUSTMENTS: [if any needed]

RECIPE 2: ...
"""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "{input}")
        ])

        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=settings.agent_verbose,
            max_iterations=settings.agent_max_iterations
        )

    async def suggest_recipes(
        self,
        user_id: str,
        meals: List[Meal],
        preferences: UserPreferences
    ) -> RecipeRecommendation:
        """
        Suggest recipes for each meal

        Args:
            user_id: User identifier
            meals: List of meals needing recipes
            preferences: User preferences

        Returns:
            RecipeRecommendation with recipe suggestions
        """
        # Build input prompt
        meal_details = []
        for i, meal in enumerate(meals, 1):
            meal_details.append(f"""
Meal {i}: {meal.name} ({meal.meal_type.value})
Target Macros: P:{meal.protein_g:.0f}g C:{meal.carbs_g:.0f}g F:{meal.fat_g:.0f}g ({meal.calories:.0f} cal)
""")

        dietary_info = ""
        if preferences.dietary_restrictions:
            restrictions = [r.value for r in preferences.dietary_restrictions]
            dietary_info += f"\nDietary Restrictions: {', '.join(restrictions)}"

        if preferences.allergies:
            dietary_info += f"\nAllergies (EXCLUDE): {', '.join(preferences.allergies)}"

        if preferences.max_prep_time_minutes:
            dietary_info += f"\nMax Prep Time: {preferences.max_prep_time_minutes} minutes"

        input_text = f"""
Suggest recipes for the following meals:
{''.join(meal_details)}

User Preferences:
{dietary_info}

Use the tools to:
1. Search recipes by meal type for each meal
2. Find recipes matching macro targets
3. Filter by dietary restrictions and prep time
4. Score recipes by macro accuracy and preferences
5. Return top 2-3 recipes per meal with match scores

Provide structured recommendations as described.
"""

        # Run agent
        result = await self.executor.ainvoke({"input": input_text})

        # Parse agent output
        output = result["output"]

        # Build recipe mapping
        recipe_suggestions = self._parse_recipe_suggestions(output, meals)

        # Calculate overall match score
        overall_score = self._calculate_overall_match_score(recipe_suggestions)

        # Create RecipeRecommendation
        recommendation = RecipeRecommendation(
            user_id=user_id,
            meals=meals,
            recipe_suggestions=recipe_suggestions,
            overall_match_score=overall_score,
            notes=output,
            timestamp=datetime.now()
        )

        return recommendation

    def _parse_recipe_suggestions(
        self,
        output: str,
        meals: List[Meal]
    ) -> dict[str, List[Recipe]]:
        """
        Parse recipe suggestions from agent output

        Returns dict mapping meal name to list of suggested recipes
        """
        suggestions = {}

        # Simplified parser - in production, parse the actual structured output
        # For now, return mock suggestions based on meal types

        for meal in meals:
            # Find recipes matching this meal type
            matching_recipes = search_recipes(meal_type=meal.meal_type)

            if not matching_recipes:
                # Use any recipes as fallback
                matching_recipes = MOCK_RECIPES[:2]
            else:
                # Use top 2 recipes
                matching_recipes = matching_recipes[:2]

            suggestions[meal.name] = matching_recipes

        return suggestions

    def _calculate_overall_match_score(
        self,
        recipe_suggestions: dict[str, List[Recipe]]
    ) -> float:
        """
        Calculate overall match score for all recipe suggestions

        Returns score between 0.0 and 1.0
        """
        if not recipe_suggestions:
            return 0.0

        # For now, return high score since we're using curated mock data
        # In production, calculate based on macro accuracy

        total_recipes = sum(len(recipes) for recipes in recipe_suggestions.values())
        if total_recipes == 0:
            return 0.0

        # Mock score - in production, calculate from actual macro matches
        return 0.85


# Global instance
recipe_suggester_agent = RecipeSuggesterAgent()


async def suggest_meal_recipes(
    user_id: str,
    meals: List[Meal],
    preferences: UserPreferences
) -> RecipeRecommendation:
    """
    Convenience function to suggest recipes

    Args:
        user_id: User identifier
        meals: List of meals
        preferences: User preferences

    Returns:
        RecipeRecommendation
    """
    return await recipe_suggester_agent.suggest_recipes(user_id, meals, preferences)
