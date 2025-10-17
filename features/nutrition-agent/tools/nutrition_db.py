"""
Nutrition Database Tool - Food and recipe search
Currently uses mock data, can be extended to use real APIs
"""
from typing import List, Optional
from ..models.schemas import Food, Recipe, Ingredient, MealType


# ===== MOCK FOOD DATABASE =====

MOCK_FOODS = [
    # Proteins
    Food(name="Chicken Breast (grilled)", serving_size="100g", calories=165, protein_g=31, carbs_g=0, fat_g=3.6, fiber_g=0),
    Food(name="Salmon (grilled)", serving_size="100g", calories=206, protein_g=22, carbs_g=0, fat_g=13, fiber_g=0),
    Food(name="Eggs (whole)", serving_size="2 large", calories=140, protein_g=12, carbs_g=1, fat_g=10, fiber_g=0),
    Food(name="Greek Yogurt (non-fat)", serving_size="1 cup", calories=100, protein_g=17, carbs_g=7, fat_g=0, fiber_g=0),
    Food(name="Whey Protein Powder", serving_size="1 scoop (30g)", calories=120, protein_g=24, carbs_g=3, fat_g=1, fiber_g=0),

    # Carbs
    Food(name="Brown Rice (cooked)", serving_size="1 cup", calories=216, protein_g=5, carbs_g=45, fat_g=1.8, fiber_g=3.5),
    Food(name="Sweet Potato (baked)", serving_size="1 medium", calories=103, protein_g=2, carbs_g=24, fat_g=0.2, fiber_g=4),
    Food(name="Oatmeal (cooked)", serving_size="1 cup", calories=154, protein_g=6, carbs_g=27, fat_g=3, fiber_g=4),
    Food(name="Whole Wheat Bread", serving_size="2 slices", calories=160, protein_g=8, carbs_g=28, fat_g=2, fiber_g=4),
    Food(name="Banana", serving_size="1 medium", calories=105, protein_g=1, carbs_g=27, fat_g=0.4, fiber_g=3),

    # Fats
    Food(name="Avocado", serving_size="1/2 medium", calories=120, protein_g=1, carbs_g=6, fat_g=11, fiber_g=5),
    Food(name="Almonds", serving_size="1 oz (23 nuts)", calories=164, protein_g=6, carbs_g=6, fat_g=14, fiber_g=3.5),
    Food(name="Olive Oil", serving_size="1 tbsp", calories=119, protein_g=0, carbs_g=0, fat_g=14, fiber_g=0),
    Food(name="Peanut Butter", serving_size="2 tbsp", calories=188, protein_g=8, carbs_g=7, fat_g=16, fiber_g=2),

    # Vegetables
    Food(name="Broccoli (steamed)", serving_size="1 cup", calories=55, protein_g=4, carbs_g=11, fat_g=0.6, fiber_g=5),
    Food(name="Spinach (cooked)", serving_size="1 cup", calories=41, protein_g=5, carbs_g=7, fat_g=0.5, fiber_g=4),
    Food(name="Bell Peppers", serving_size="1 cup", calories=30, protein_g=1, carbs_g=7, fat_g=0.3, fiber_g=2),
]


def search_foods(query: str, limit: int = 10) -> List[Food]:
    """
    Search for foods in database

    Args:
        query: Search query
        limit: Maximum results

    Returns:
        List of matching foods
    """
    query_lower = query.lower()
    results = [
        food for food in MOCK_FOODS
        if query_lower in food.name.lower()
    ]
    return results[:limit]


def get_food_by_name(name: str) -> Optional[Food]:
    """
    Get specific food by exact name

    Args:
        name: Food name

    Returns:
        Food object or None
    """
    for food in MOCK_FOODS:
        if food.name.lower() == name.lower():
            return food
    return None


def search_high_protein_foods(min_protein_g: float = 20) -> List[Food]:
    """
    Find foods high in protein

    Args:
        min_protein_g: Minimum protein grams

    Returns:
        List of high-protein foods
    """
    return [food for food in MOCK_FOODS if food.protein_g >= min_protein_g]


def search_low_carb_foods(max_carbs_g: float = 10) -> List[Food]:
    """
    Find low-carb foods

    Args:
        max_carbs_g: Maximum carb grams

    Returns:
        List of low-carb foods
    """
    return [food for food in MOCK_FOODS if food.carbs_g <= max_carbs_g]


# ===== MOCK RECIPE DATABASE =====

MOCK_RECIPES = [
    Recipe(
        name="Grilled Chicken with Brown Rice and Broccoli",
        description="Classic bodybuilding meal - high protein, complex carbs, vegetables",
        meal_type=MealType.LUNCH,
        ingredients=[
            Ingredient(name="Chicken Breast", amount="150g", food=get_food_by_name("Chicken Breast (grilled)")),
            Ingredient(name="Brown Rice", amount="1 cup cooked", food=get_food_by_name("Brown Rice (cooked)")),
            Ingredient(name="Broccoli", amount="1 cup steamed", food=get_food_by_name("Broccoli (steamed)")),
            Ingredient(name="Olive Oil", amount="1 tbsp", food=get_food_by_name("Olive Oil")),
        ],
        instructions=[
            "Season chicken breast with salt, pepper, and herbs",
            "Grill chicken for 6-7 minutes per side until internal temp reaches 165°F",
            "Cook brown rice according to package instructions",
            "Steam broccoli for 5 minutes",
            "Plate all components and drizzle with olive oil"
        ],
        prep_time_minutes=10,
        cook_time_minutes=25,
        servings=1,
        calories_per_serving=615,
        protein_per_serving=52,
        carbs_per_serving=56,
        fat_per_serving=20,
        cuisine="American",
        difficulty="easy",
        tags=["high-protein", "balanced", "meal-prep-friendly"]
    ),

    Recipe(
        name="Overnight Oats with Protein",
        description="Easy prep breakfast loaded with protein and fiber",
        meal_type=MealType.BREAKFAST,
        ingredients=[
            Ingredient(name="Oatmeal", amount="1 cup", food=get_food_by_name("Oatmeal (cooked)")),
            Ingredient(name="Protein Powder", amount="1 scoop", food=get_food_by_name("Whey Protein Powder")),
            Ingredient(name="Banana", amount="1 medium", food=get_food_by_name("Banana")),
            Ingredient(name="Almond Butter", amount="1 tbsp", food=get_food_by_name("Peanut Butter")),
        ],
        instructions=[
            "Mix oats with 1 cup milk or water",
            "Stir in protein powder",
            "Slice banana and add to mixture",
            "Add almond butter",
            "Refrigerate overnight (or minimum 2 hours)",
            "Optional: top with berries or nuts"
        ],
        prep_time_minutes=5,
        cook_time_minutes=0,
        servings=1,
        calories_per_serving=473,
        protein_per_serving=37,
        carbs_per_serving=60,
        fat_per_serving=9,
        cuisine="American",
        difficulty="easy",
        tags=["breakfast", "meal-prep", "no-cook", "high-protein"]
    ),

    Recipe(
        name="Salmon with Sweet Potato and Spinach",
        description="Omega-3 rich dinner with complex carbs and greens",
        meal_type=MealType.DINNER,
        ingredients=[
            Ingredient(name="Salmon", amount="150g", food=get_food_by_name("Salmon (grilled)")),
            Ingredient(name="Sweet Potato", amount="1 medium", food=get_food_by_name("Sweet Potato (baked)")),
            Ingredient(name="Spinach", amount="2 cups cooked", food=get_food_by_name("Spinach (cooked)")),
            Ingredient(name="Olive Oil", amount="1 tbsp", food=get_food_by_name("Olive Oil")),
        ],
        instructions=[
            "Preheat oven to 400°F",
            "Bake sweet potato for 45 minutes or until tender",
            "Season salmon with lemon, dill, salt, pepper",
            "Bake salmon for 12-15 minutes",
            "Sauté spinach in olive oil with garlic",
            "Serve together with lemon wedge"
        ],
        prep_time_minutes=10,
        cook_time_minutes=45,
        servings=1,
        calories_per_serving=555,
        protein_per_serving=38,
        carbs_per_serving=44,
        fat_per_serving=25,
        cuisine="Mediterranean",
        difficulty="medium",
        tags=["omega-3", "heart-healthy", "balanced"]
    ),
]


def search_recipes(
    meal_type: Optional[MealType] = None,
    max_prep_time: Optional[int] = None,
    tags: Optional[List[str]] = None
) -> List[Recipe]:
    """
    Search for recipes

    Args:
        meal_type: Filter by meal type
        max_prep_time: Maximum prep + cook time
        tags: Filter by tags

    Returns:
        List of matching recipes
    """
    results = MOCK_RECIPES.copy()

    if meal_type:
        results = [r for r in results if r.meal_type == meal_type]

    if max_prep_time:
        results = [
            r for r in results
            if (r.prep_time_minutes + r.cook_time_minutes) <= max_prep_time
        ]

    if tags:
        results = [
            r for r in results
            if any(tag in r.tags for tag in tags)
        ]

    return results


def find_recipes_matching_macros(
    target_protein: float,
    target_carbs: float,
    target_fat: float,
    tolerance_percent: float = 20
) -> List[Recipe]:
    """
    Find recipes that match target macros within tolerance

    Args:
        target_protein: Target protein grams
        target_carbs: Target carb grams
        target_fat: Target fat grams
        tolerance_percent: Allowed deviation percentage

    Returns:
        List of matching recipes
    """
    matches = []

    for recipe in MOCK_RECIPES:
        protein_match = abs(recipe.protein_per_serving - target_protein) / target_protein <= (tolerance_percent / 100)
        carbs_match = abs(recipe.carbs_per_serving - target_carbs) / target_carbs <= (tolerance_percent / 100)
        fat_match = abs(recipe.fat_per_serving - target_fat) / target_fat <= (tolerance_percent / 100)

        if protein_match and carbs_match and fat_match:
            matches.append(recipe)

    return matches
