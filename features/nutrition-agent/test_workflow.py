"""
Standalone Test Script for Nutrition Agent Workflow
Tests the complete daily meal plan generation end-to-end
"""
import asyncio
from datetime import date, datetime
from models.schemas import (
    ActivityLevel, NutritionGoal, UserPreferences,
    DietaryRestriction
)
from workflows.daily_plan import generate_daily_plan


def print_section_header(title: str):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_macro_profile(plan):
    """Print macro targets in formatted table"""
    macros = plan.macro_targets

    print("MACRO TARGETS:")
    print(f"  Calories:  {macros.calories:.0f} cal")
    print(f"  Protein:   {macros.protein_g:.0f}g ({macros.protein_percent*100:.0f}%)")
    print(f"  Carbs:     {macros.carbs_g:.0f}g ({macros.carbs_percent*100:.0f}%)")
    print(f"  Fats:      {macros.fat_g:.0f}g ({macros.fat_percent*100:.0f}%)")
    print(f"\n  TDEE:      {macros.tdee:.0f} cal")

    if macros.deficit_surplus < 0:
        print(f"  Deficit:   {abs(macros.deficit_surplus)} cal/day (for {macros.goal.value})")
    elif macros.deficit_surplus > 0:
        print(f"  Surplus:   {macros.deficit_surplus} cal/day (for {macros.goal.value})")
    else:
        print(f"  Strategy:  Maintenance (for {macros.goal.value})")


def print_meals(plan):
    """Print meal breakdown"""
    print("\nMEAL BREAKDOWN:")

    for i, meal in enumerate(plan.meals, 1):
        print(f"\n  {i}. {meal.name} ({meal.meal_type.value.upper()})")
        print(f"     Calories: {meal.calories:.0f} | "
              f"P:{meal.protein_g:.0f}g C:{meal.carbs_g:.0f}g F:{meal.fat_g:.0f}g")

        # Show foods in meal
        if meal.foods:
            print(f"     Foods:")
            for food in meal.foods:
                print(f"       - {food.name} ({food.serving_size})")


def print_recipes(plan):
    """Print recipe suggestions"""
    if not plan.recipe_suggestions:
        print("\nNo recipe suggestions available")
        return

    print("\nRECIPE SUGGESTIONS:")

    for meal_name, recipes in plan.recipe_suggestions.items():
        print(f"\n  For {meal_name}:")
        for recipe in recipes:
            print(f"    - {recipe.name}")
            print(f"      Macros: P:{recipe.protein_per_serving}g "
                  f"C:{recipe.carbs_per_serving}g "
                  f"F:{recipe.fat_per_serving}g "
                  f"({recipe.calories_per_serving} cal)")
            print(f"      Time: {recipe.prep_time_minutes + recipe.cook_time_minutes} min "
                  f"| Difficulty: {recipe.difficulty}")
            print(f"      Tags: {', '.join(recipe.tags)}")


def print_accuracy_summary(plan):
    """Print accuracy and match scores"""
    print("\nACCURACY SUMMARY:")
    print(f"  Calorie Match:     {plan.calorie_accuracy_percent:.1f}%")
    print(f"  Macro Balance:     {plan.macro_balance_score*100:.1f}%")

    # Calculate individual macro accuracy
    if plan.macro_targets.protein_g > 0:
        protein_acc = (plan.actual_protein_g / plan.macro_targets.protein_g) * 100
        print(f"  Protein Accuracy:  {protein_acc:.1f}%")

    if plan.macro_targets.carbs_g > 0:
        carbs_acc = (plan.actual_carbs_g / plan.macro_targets.carbs_g) * 100
        print(f"  Carbs Accuracy:    {carbs_acc:.1f}%")

    if plan.macro_targets.fat_g > 0:
        fat_acc = (plan.actual_fat_g / plan.macro_targets.fat_g) * 100
        print(f"  Fat Accuracy:      {fat_acc:.1f}%")

    print(f"\n  Actual Totals:")
    print(f"    {plan.actual_calories:.0f} cal | "
          f"P:{plan.actual_protein_g:.0f}g "
          f"C:{plan.actual_carbs_g:.0f}g "
          f"F:{plan.actual_fat_g:.0f}g")


async def test_weight_loss_plan():
    """Test Case 1: Weight Loss Plan"""
    print_section_header("TEST 1: WEIGHT LOSS PLAN")

    preferences = UserPreferences(
        meals_per_day=4,
        dietary_restrictions=[],
        allergies=[],
        disliked_foods=["liver"],
        max_prep_time_minutes=45
    )

    plan = await generate_daily_plan(
        user_id="test_user_1",
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        goal=NutritionGoal.WEIGHT_LOSS,
        preferences=preferences,
        plan_date=date.today()
    )

    print_macro_profile(plan)
    print_meals(plan)
    print_recipes(plan)
    print_accuracy_summary(plan)

    return plan


async def test_muscle_gain_plan():
    """Test Case 2: Muscle Gain Plan"""
    print_section_header("TEST 2: MUSCLE GAIN PLAN")

    preferences = UserPreferences(
        meals_per_day=5,
        dietary_restrictions=[],
        allergies=[],
        disliked_foods=[],
        max_prep_time_minutes=60
    )

    plan = await generate_daily_plan(
        user_id="test_user_2",
        activity_level=ActivityLevel.VERY_ACTIVE,
        goal=NutritionGoal.MUSCLE_GAIN,
        preferences=preferences,
        plan_date=date.today()
    )

    print_macro_profile(plan)
    print_meals(plan)
    print_recipes(plan)
    print_accuracy_summary(plan)

    return plan


async def test_vegan_plan():
    """Test Case 3: Vegan Diet Plan"""
    print_section_header("TEST 3: VEGAN DIET PLAN")

    preferences = UserPreferences(
        meals_per_day=3,
        dietary_restrictions=[DietaryRestriction.VEGAN],
        allergies=["nuts"],
        disliked_foods=[],
        max_prep_time_minutes=30
    )

    plan = await generate_daily_plan(
        user_id="test_user_3",
        activity_level=ActivityLevel.LIGHTLY_ACTIVE,
        goal=NutritionGoal.MAINTENANCE,
        preferences=preferences,
        plan_date=date.today()
    )

    print_macro_profile(plan)
    print_meals(plan)
    print_recipes(plan)
    print_accuracy_summary(plan)

    return plan


async def test_recomp_plan():
    """Test Case 4: Body Recomposition Plan"""
    print_section_header("TEST 4: BODY RECOMPOSITION PLAN")

    preferences = UserPreferences(
        meals_per_day=4,
        dietary_restrictions=[],
        allergies=[],
        disliked_foods=["fish"],
        max_prep_time_minutes=40
    )

    plan = await generate_daily_plan(
        user_id="test_user_4",
        activity_level=ActivityLevel.VERY_ACTIVE,
        goal=NutritionGoal.RECOMP,
        preferences=preferences,
        plan_date=date.today()
    )

    print_macro_profile(plan)
    print_meals(plan)
    print_recipes(plan)
    print_accuracy_summary(plan)

    return plan


async def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("  NUTRITION AGENT WORKFLOW - END-TO-END TESTS")
    print("="*60)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing complete workflow: Macro Calculation -> Meal Planning -> Recipe Suggestions")

    results = []

    try:
        # Test 1: Weight Loss
        plan1 = await test_weight_loss_plan()
        results.append(("Weight Loss Plan", "PASS", plan1))

    except Exception as e:
        print(f"\n[FAIL] Weight Loss Plan: {str(e)}")
        results.append(("Weight Loss Plan", "FAIL", str(e)))

    try:
        # Test 2: Muscle Gain
        plan2 = await test_muscle_gain_plan()
        results.append(("Muscle Gain Plan", "PASS", plan2))

    except Exception as e:
        print(f"\n[FAIL] Muscle Gain Plan: {str(e)}")
        results.append(("Muscle Gain Plan", "FAIL", str(e)))

    try:
        # Test 3: Vegan
        plan3 = await test_vegan_plan()
        results.append(("Vegan Diet Plan", "PASS", plan3))

    except Exception as e:
        print(f"\n[FAIL] Vegan Diet Plan: {str(e)}")
        results.append(("Vegan Diet Plan", "FAIL", str(e)))

    try:
        # Test 4: Recomposition
        plan4 = await test_recomp_plan()
        results.append(("Body Recomposition", "PASS", plan4))

    except Exception as e:
        print(f"\n[FAIL] Body Recomposition: {str(e)}")
        results.append(("Body Recomposition", "FAIL", str(e)))

    # Print summary
    print_section_header("TEST SUMMARY")

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = len(results) - passed

    for test_name, status, _ in results:
        status_symbol = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"  {status_symbol} {test_name}")

    print(f"\n  Total: {len(results)} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed == 0:
        print("\n  [SUCCESS] All tests passed!")
    else:
        print(f"\n  [WARNING] {failed} test(s) failed")

    print("\n" + "="*60 + "\n")

    return results


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())
