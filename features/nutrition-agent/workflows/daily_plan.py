"""
Daily Meal Plan Workflow
Orchestrates all nutrition agents to create complete daily meal plans
"""
from typing import TypedDict, Annotated, Optional
from datetime import datetime, date
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from ..models.schemas import (
    DailyPlan, MacroCalculation, MealPlanSuggestion, RecipeRecommendation,
    UserPreferences, ActivityLevel, NutritionGoal, MacroProfile
)
from ..agents.macro_calculator import calculate_user_macros
from ..agents.meal_planner import plan_daily_meals
from ..agents.recipe_suggester import suggest_meal_recipes


# ===== WORKFLOW STATE =====

class DailyPlanState(TypedDict):
    """State for daily meal plan workflow"""
    # Inputs
    user_id: str
    activity_level: ActivityLevel
    goal: NutritionGoal
    preferences: UserPreferences
    plan_date: date

    # Agent outputs
    macro_calculation: Optional[MacroCalculation]
    meal_plan: Optional[MealPlanSuggestion]
    recipe_recommendation: Optional[RecipeRecommendation]

    # Final output
    daily_plan: Optional[DailyPlan]

    # Error handling
    errors: Annotated[list[str], operator.add]
    status: str  # "running", "completed", "failed"


# ===== WORKFLOW NODES =====

async def calculate_macros_node(state: DailyPlanState) -> DailyPlanState:
    """
    Node 1: Calculate macro targets
    """
    try:
        print(f"[Step 1/3] Calculating macro targets for user {state['user_id']}...")

        macro_calculation = await calculate_user_macros(
            user_id=state["user_id"],
            activity_level=state["activity_level"],
            goal=state["goal"]
        )

        print(f"  Macros: {macro_calculation.target_calories:.0f} cal | "
              f"P:{macro_calculation.macro_profile.protein_g:.0f}g "
              f"C:{macro_calculation.macro_profile.carbs_g:.0f}g "
              f"F:{macro_calculation.macro_profile.fat_g:.0f}g")

        state["macro_calculation"] = macro_calculation
        return state

    except Exception as e:
        error_msg = f"Macro calculation failed: {str(e)}"
        print(f"  ERROR: {error_msg}")
        state["errors"].append(error_msg)
        state["status"] = "failed"
        return state


async def plan_meals_node(state: DailyPlanState) -> DailyPlanState:
    """
    Node 2: Plan meals to hit macro targets
    """
    try:
        if not state.get("macro_calculation"):
            raise ValueError("No macro calculation available")

        print(f"[Step 2/3] Planning {state['preferences'].meals_per_day} meals...")

        meal_plan = await plan_daily_meals(
            user_id=state["user_id"],
            macro_profile=state["macro_calculation"].macro_profile,
            preferences=state["preferences"]
        )

        print(f"  Created {len(meal_plan.meals)} meals")
        print(f"  Total: {meal_plan.total_calories:.0f} cal | "
              f"P:{meal_plan.total_protein_g:.0f}g "
              f"C:{meal_plan.total_carbs_g:.0f}g "
              f"F:{meal_plan.total_fat_g:.0f}g")
        print(f"  Accuracy: {meal_plan.accuracy_score*100:.1f}%")

        state["meal_plan"] = meal_plan
        return state

    except Exception as e:
        error_msg = f"Meal planning failed: {str(e)}"
        print(f"  ERROR: {error_msg}")
        state["errors"].append(error_msg)
        state["status"] = "failed"
        return state


async def suggest_recipes_node(state: DailyPlanState) -> DailyPlanState:
    """
    Node 3: Suggest recipes for each meal
    """
    try:
        if not state.get("meal_plan"):
            raise ValueError("No meal plan available")

        print(f"[Step 3/3] Suggesting recipes for meals...")

        recipe_recommendation = await suggest_meal_recipes(
            user_id=state["user_id"],
            meals=state["meal_plan"].meals,
            preferences=state["preferences"]
        )

        total_recipes = sum(
            len(recipes)
            for recipes in recipe_recommendation.recipe_suggestions.values()
        )
        print(f"  Suggested {total_recipes} recipes")
        print(f"  Match score: {recipe_recommendation.overall_match_score*100:.1f}%")

        state["recipe_recommendation"] = recipe_recommendation
        return state

    except Exception as e:
        error_msg = f"Recipe suggestion failed: {str(e)}"
        print(f"  ERROR: {error_msg}")
        state["errors"].append(error_msg)
        state["status"] = "failed"
        return state


async def assemble_plan_node(state: DailyPlanState) -> DailyPlanState:
    """
    Node 4: Assemble final daily plan
    """
    try:
        if not all([
            state.get("macro_calculation"),
            state.get("meal_plan"),
            state.get("recipe_recommendation")
        ]):
            raise ValueError("Missing required components for daily plan")

        print(f"[Finalizing] Assembling daily plan...")

        # Calculate accuracy metrics
        macro_profile = state["macro_calculation"].macro_profile
        meal_plan = state["meal_plan"]

        calorie_accuracy = (meal_plan.total_calories / macro_profile.calories) * 100
        protein_accuracy = (meal_plan.total_protein_g / macro_profile.protein_g) * 100

        macro_balance_score = (
            protein_accuracy +
            (meal_plan.total_carbs_g / macro_profile.carbs_g) * 100 +
            (meal_plan.total_fat_g / macro_profile.fat_g) * 100
        ) / 3

        # Create DailyPlan
        daily_plan = DailyPlan(
            user_id=state["user_id"],
            date=state["plan_date"],
            goal=state["goal"],
            macro_targets=macro_profile,
            meals=meal_plan.meals,
            recipe_suggestions=state["recipe_recommendation"].recipe_suggestions,
            actual_calories=meal_plan.total_calories,
            actual_protein_g=meal_plan.total_protein_g,
            actual_carbs_g=meal_plan.total_carbs_g,
            actual_fat_g=meal_plan.total_fat_g,
            calorie_accuracy_percent=calorie_accuracy,
            macro_balance_score=macro_balance_score / 100,
            notes=f"Generated by AI nutrition agent system. "
                  f"Macro calculation: {state['macro_calculation'].calculation_notes[:100]}..."
        )

        print(f"\n=== DAILY PLAN COMPLETE ===")
        print(f"Date: {daily_plan.date}")
        print(f"Goal: {daily_plan.goal.value}")
        print(f"Meals: {len(daily_plan.meals)}")
        print(f"Calorie Accuracy: {daily_plan.calorie_accuracy_percent:.1f}%")
        print(f"Macro Balance: {daily_plan.macro_balance_score*100:.1f}%")
        print(f"===========================\n")

        state["daily_plan"] = daily_plan
        state["status"] = "completed"
        return state

    except Exception as e:
        error_msg = f"Plan assembly failed: {str(e)}"
        print(f"  ERROR: {error_msg}")
        state["errors"].append(error_msg)
        state["status"] = "failed"
        return state


def should_continue(state: DailyPlanState) -> str:
    """
    Determine if workflow should continue or end
    """
    if state.get("status") == "failed":
        return "end"

    if state.get("daily_plan"):
        return "end"

    return "continue"


# ===== WORKFLOW GRAPH =====

def create_daily_plan_workflow() -> StateGraph:
    """
    Create LangGraph workflow for daily meal planning

    Flow:
    1. Calculate Macros
    2. Plan Meals
    3. Suggest Recipes
    4. Assemble Plan
    """
    workflow = StateGraph(DailyPlanState)

    # Add nodes
    workflow.add_node("calculate_macros", calculate_macros_node)
    workflow.add_node("plan_meals", plan_meals_node)
    workflow.add_node("suggest_recipes", suggest_recipes_node)
    workflow.add_node("assemble_plan", assemble_plan_node)

    # Define edges (sequential flow)
    workflow.set_entry_point("calculate_macros")

    workflow.add_edge("calculate_macros", "plan_meals")
    workflow.add_edge("plan_meals", "suggest_recipes")
    workflow.add_edge("suggest_recipes", "assemble_plan")
    workflow.add_edge("assemble_plan", END)

    return workflow.compile()


# ===== PUBLIC API =====

async def generate_daily_plan(
    user_id: str,
    activity_level: ActivityLevel,
    goal: NutritionGoal,
    preferences: UserPreferences,
    plan_date: Optional[date] = None
) -> DailyPlan:
    """
    Generate complete daily meal plan

    Args:
        user_id: User identifier
        activity_level: Physical activity level
        goal: Nutrition goal
        preferences: User preferences
        plan_date: Date for the plan (defaults to today)

    Returns:
        Complete DailyPlan

    Raises:
        Exception: If workflow fails
    """
    if plan_date is None:
        plan_date = date.today()

    # Initialize state
    initial_state: DailyPlanState = {
        "user_id": user_id,
        "activity_level": activity_level,
        "goal": goal,
        "preferences": preferences,
        "plan_date": plan_date,
        "macro_calculation": None,
        "meal_plan": None,
        "recipe_recommendation": None,
        "daily_plan": None,
        "errors": [],
        "status": "running"
    }

    # Create and run workflow
    workflow = create_daily_plan_workflow()

    print(f"\n{'='*50}")
    print(f"DAILY MEAL PLAN WORKFLOW")
    print(f"User: {user_id}")
    print(f"Goal: {goal.value}")
    print(f"Activity: {activity_level.value}")
    print(f"Date: {plan_date}")
    print(f"{'='*50}\n")

    try:
        # Run workflow
        final_state = await workflow.ainvoke(initial_state)

        # Check for errors
        if final_state["status"] == "failed":
            error_summary = "; ".join(final_state["errors"])
            raise Exception(f"Workflow failed: {error_summary}")

        if not final_state.get("daily_plan"):
            raise Exception("Workflow completed but no daily plan was generated")

        return final_state["daily_plan"]

    except Exception as e:
        print(f"\n[WORKFLOW ERROR] {str(e)}\n")
        raise


async def generate_weekly_plan(
    user_id: str,
    activity_level: ActivityLevel,
    goal: NutritionGoal,
    preferences: UserPreferences,
    start_date: Optional[date] = None
) -> list[DailyPlan]:
    """
    Generate weekly meal plan (7 days)

    Args:
        user_id: User identifier
        activity_level: Activity level
        goal: Nutrition goal
        preferences: User preferences
        start_date: Start date (defaults to today)

    Returns:
        List of 7 DailyPlan objects
    """
    if start_date is None:
        start_date = date.today()

    print(f"\n{'='*50}")
    print(f"WEEKLY MEAL PLAN WORKFLOW")
    print(f"User: {user_id}")
    print(f"Week starting: {start_date}")
    print(f"{'='*50}\n")

    weekly_plans = []

    for day_offset in range(7):
        from datetime import timedelta
        plan_date = start_date + timedelta(days=day_offset)

        print(f"\n--- Day {day_offset + 1}/7: {plan_date.strftime('%A, %B %d')} ---\n")

        try:
            daily_plan = await generate_daily_plan(
                user_id=user_id,
                activity_level=activity_level,
                goal=goal,
                preferences=preferences,
                plan_date=plan_date
            )
            weekly_plans.append(daily_plan)

        except Exception as e:
            print(f"[ERROR] Failed to generate plan for {plan_date}: {str(e)}")
            # Continue with other days even if one fails
            continue

    print(f"\n{'='*50}")
    print(f"WEEKLY PLAN COMPLETE: {len(weekly_plans)}/7 days generated")
    print(f"{'='*50}\n")

    return weekly_plans
