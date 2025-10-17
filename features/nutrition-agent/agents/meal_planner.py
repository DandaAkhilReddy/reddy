"""
Meal Planner Agent
Creates daily meal structure to hit macro targets
"""
from typing import List, Optional
from datetime import datetime
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from ..models.schemas import (
    MealPlanSuggestion, MacroProfile, UserPreferences,
    Meal, Food, MealType, DietaryRestriction
)
from ..tools.nutrition_db import (
    search_foods, search_high_protein_foods,
    search_low_carb_foods, MOCK_FOODS
)
from ..config.settings import settings


# ===== LANGCHAIN TOOLS =====

@tool
def search_protein_foods(min_protein: float = 20.0) -> str:
    """Search for high-protein foods"""
    foods = search_high_protein_foods(min_protein_g=min_protein)
    if not foods:
        return "No high-protein foods found"

    result = "High-Protein Foods:\n"
    for food in foods[:5]:
        result += f"- {food.name}: {food.protein_g}g protein, {food.calories} cal ({food.serving_size})\n"
    return result


@tool
def search_carb_foods(query: str = "") -> str:
    """Search for carbohydrate-rich foods"""
    carb_foods = [f for f in MOCK_FOODS if f.carbs_g > 20]

    if query:
        carb_foods = [f for f in carb_foods if query.lower() in f.name.lower()]

    if not carb_foods:
        return "No carb foods found"

    result = "Carbohydrate Foods:\n"
    for food in carb_foods[:5]:
        result += f"- {food.name}: {food.carbs_g}g carbs, {food.calories} cal ({food.serving_size})\n"
    return result


@tool
def search_fat_foods(query: str = "") -> str:
    """Search for healthy fat sources"""
    fat_foods = [f for f in MOCK_FOODS if f.fat_g > 10]

    if query:
        fat_foods = [f for f in fat_foods if query.lower() in f.name.lower()]

    if not fat_foods:
        return "No fat foods found"

    result = "Healthy Fat Sources:\n"
    for food in fat_foods[:5]:
        result += f"- {food.name}: {food.fat_g}g fat, {food.calories} cal ({food.serving_size})\n"
    return result


@tool
def search_any_food(query: str) -> str:
    """Search for any food by name"""
    foods = search_foods(query, limit=5)
    if not foods:
        return f"No foods found matching '{query}'"

    result = f"Foods matching '{query}':\n"
    for food in foods:
        result += f"- {food.name}: P:{food.protein_g}g C:{food.carbs_g}g F:{food.fat_g}g ({food.calories} cal, {food.serving_size})\n"
    return result


@tool
def calculate_meal_macros(protein_g: float, carbs_g: float, fat_g: float) -> str:
    """Calculate total calories from macros"""
    calories = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
    return f"Total: {calories:.0f} calories (P:{protein_g}g C:{carbs_g}g F:{fat_g}g)"


# ===== MEAL PLANNER AGENT =====

class MealPlannerAgent:
    """Agent that creates meal plans hitting macro targets"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        self.tools = [
            search_protein_foods,
            search_carb_foods,
            search_fat_foods,
            search_any_food,
            calculate_meal_macros
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert meal planning nutritionist.

Your task is to create a daily meal plan that hits specific macro targets.

Steps:
1. Determine number of meals (3-6) based on user preferences
2. Split macro targets across meals:
   - Breakfast: ~25-30% of daily calories
   - Lunch: ~30-35% of daily calories
   - Dinner: ~30-35% of daily calories
   - Snacks: Remaining calories
3. For each meal, search for foods that match the macro split
4. Build balanced meals with:
   - Protein source (meat, fish, eggs, protein powder)
   - Carb source (rice, oats, bread, potato)
   - Fat source (oils, nuts, avocado)
   - Optional: vegetables
5. Respect dietary restrictions (vegan, vegetarian, keto, etc.)
6. Validate that total macros across all meals match targets (within 5%)

Important:
- Use realistic serving sizes
- Balance variety across meals
- Consider meal timing and digestion
- Avoid allergens
- Make meals practical and easy to prepare

Provide the final meal plan in this format:
MEAL 1 (Breakfast):
- Food 1: amount
- Food 2: amount
TOTALS: P:Xg C:Yg F:Zg (Calories)

MEAL 2 (Lunch):
...

DAILY TOTALS: P:Xg C:Yg F:Zg (Calories)
ACCURACY: % match to targets"""),
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

    async def plan_meals(
        self,
        user_id: str,
        macro_profile: MacroProfile,
        preferences: UserPreferences
    ) -> MealPlanSuggestion:
        """
        Create meal plan hitting macro targets

        Args:
            user_id: User identifier
            macro_profile: Macro targets
            preferences: User preferences

        Returns:
            MealPlanSuggestion with structured meals
        """
        # Build input prompt
        dietary_info = ""
        if preferences.dietary_restrictions:
            restrictions = [r.value for r in preferences.dietary_restrictions]
            dietary_info += f"\nDietary Restrictions: {', '.join(restrictions)}"

        if preferences.allergies:
            dietary_info += f"\nAllergies: {', '.join(preferences.allergies)}"

        if preferences.disliked_foods:
            dietary_info += f"\nDisliked Foods: {', '.join(preferences.disliked_foods)}"

        input_text = f"""
Create a meal plan for a user with these macro targets:
- Calories: {macro_profile.calories:.0f}
- Protein: {macro_profile.protein_g:.0f}g ({macro_profile.protein_percent*100:.0f}%)
- Carbs: {macro_profile.carbs_g:.0f}g ({macro_profile.carbs_percent*100:.0f}%)
- Fats: {macro_profile.fat_g:.0f}g ({macro_profile.fat_percent*100:.0f}%)

Goal: {macro_profile.goal.value}
Number of Meals: {preferences.meals_per_day}
{dietary_info}

Use the tools to:
1. Search for high-protein foods
2. Search for carb sources
3. Search for fat sources
4. Build {preferences.meals_per_day} balanced meals
5. Validate totals match targets

Provide the structured meal plan as described.
"""

        # Run agent
        result = await self.executor.ainvoke({"input": input_text})

        # Parse agent output
        output = result["output"]

        # Build meals from output
        meals = self._parse_meals_from_output(output, preferences.meals_per_day)

        # Calculate totals
        total_calories = sum(m.calories for m in meals)
        total_protein = sum(m.protein_g for m in meals)
        total_carbs = sum(m.carbs_g for m in meals)
        total_fat = sum(m.fat_g for m in meals)

        # Calculate accuracy
        calorie_accuracy = (total_calories / macro_profile.calories) * 100
        protein_accuracy = (total_protein / macro_profile.protein_g) * 100
        carbs_accuracy = (total_carbs / macro_profile.carbs_g) * 100
        fat_accuracy = (total_fat / macro_profile.fat_g) * 100

        overall_accuracy = (
            calorie_accuracy + protein_accuracy + carbs_accuracy + fat_accuracy
        ) / 4

        # Create MealPlanSuggestion
        suggestion = MealPlanSuggestion(
            user_id=user_id,
            macro_targets=macro_profile,
            meals=meals,
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            accuracy_score=overall_accuracy / 100,
            notes=output,
            timestamp=datetime.now()
        )

        return suggestion

    def _parse_meals_from_output(self, output: str, num_meals: int) -> List[Meal]:
        """
        Parse meals from agent output

        This is a simplified parser - in production you'd want more robust parsing
        """
        meals = []

        # Try to extract meal structure from output
        # For now, create sample meals based on common patterns

        meal_types = [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER, MealType.SNACK]

        for i in range(num_meals):
            meal_type = meal_types[i] if i < len(meal_types) else MealType.SNACK

            # Extract foods from output (simplified)
            # In production, you'd parse the structured output more carefully
            foods = self._extract_foods_for_meal(output, i)

            # Calculate meal totals
            calories = sum(f.calories for f in foods)
            protein = sum(f.protein_g for f in foods)
            carbs = sum(f.carbs_g for f in foods)
            fat = sum(f.fat_g for f in foods)

            meal = Meal(
                meal_type=meal_type,
                name=f"{meal_type.value.title()} {i+1}",
                foods=foods,
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fat_g=fat
            )
            meals.append(meal)

        return meals

    def _extract_foods_for_meal(self, output: str, meal_index: int) -> List[Food]:
        """
        Extract foods for a specific meal from output

        Simplified implementation - returns sample foods
        In production, parse the actual agent output
        """
        # This is a placeholder - would parse agent output in production
        # For now, return sample foods based on meal index

        if meal_index == 0:  # Breakfast
            return [
                Food(name="Oatmeal (cooked)", serving_size="1 cup",
                     calories=154, protein_g=6, carbs_g=27, fat_g=3, fiber_g=4),
                Food(name="Whey Protein Powder", serving_size="1 scoop",
                     calories=120, protein_g=24, carbs_g=3, fat_g=1, fiber_g=0),
                Food(name="Banana", serving_size="1 medium",
                     calories=105, protein_g=1, carbs_g=27, fat_g=0.4, fiber_g=3),
            ]
        elif meal_index == 1:  # Lunch
            return [
                Food(name="Chicken Breast (grilled)", serving_size="150g",
                     calories=248, protein_g=47, carbs_g=0, fat_g=5.4, fiber_g=0),
                Food(name="Brown Rice (cooked)", serving_size="1 cup",
                     calories=216, protein_g=5, carbs_g=45, fat_g=1.8, fiber_g=3.5),
                Food(name="Broccoli (steamed)", serving_size="1 cup",
                     calories=55, protein_g=4, carbs_g=11, fat_g=0.6, fiber_g=5),
            ]
        elif meal_index == 2:  # Dinner
            return [
                Food(name="Salmon (grilled)", serving_size="150g",
                     calories=309, protein_g=33, carbs_g=0, fat_g=19.5, fiber_g=0),
                Food(name="Sweet Potato (baked)", serving_size="1 medium",
                     calories=103, protein_g=2, carbs_g=24, fat_g=0.2, fiber_g=4),
                Food(name="Spinach (cooked)", serving_size="1 cup",
                     calories=41, protein_g=5, carbs_g=7, fat_g=0.5, fiber_g=4),
            ]
        else:  # Snack
            return [
                Food(name="Greek Yogurt (non-fat)", serving_size="1 cup",
                     calories=100, protein_g=17, carbs_g=7, fat_g=0, fiber_g=0),
                Food(name="Almonds", serving_size="1 oz",
                     calories=164, protein_g=6, carbs_g=6, fat_g=14, fiber_g=3.5),
            ]


# Global instance
meal_planner_agent = MealPlannerAgent()


async def plan_daily_meals(
    user_id: str,
    macro_profile: MacroProfile,
    preferences: UserPreferences
) -> MealPlanSuggestion:
    """
    Convenience function to plan meals

    Args:
        user_id: User identifier
        macro_profile: Macro targets
        preferences: User preferences

    Returns:
        MealPlanSuggestion
    """
    return await meal_planner_agent.plan_meals(user_id, macro_profile, preferences)
