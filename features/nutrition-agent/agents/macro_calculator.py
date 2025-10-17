"""
Macro Calculator Agent
Calculates personalized macro targets based on body composition, goals, and recovery
"""
from datetime import datetime
from typing import Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from ..models.schemas import (
    MacroCalculation, MacroProfile, BodyComposition,
    ActivityLevel, NutritionGoal
)
from ..tools.body_metrics import (
    get_latest_body_scan, calculate_bmr,
    calculate_lean_mass_bmr, calculate_tdee
)
from ..tools.recovery_data import (
    get_whoop_recovery, adjust_calories_for_recovery
)
from ..config.settings import settings


# ===== LANGCHAIN TOOLS =====

@tool
async def fetch_body_composition(user_id: str) -> str:
    """Fetch user's body composition from latest photo analysis scan"""
    body_comp = await get_latest_body_scan(user_id)
    if body_comp:
        return f"""
Body Composition:
- Weight: {body_comp.weight_kg}kg
- Height: {body_comp.height_cm}cm
- Body Fat: {body_comp.body_fat_percent}%
- Lean Mass: {body_comp.lean_mass_kg}kg
- Age: {body_comp.age}
- Gender: {body_comp.gender}
"""
    return "No body composition data available"


@tool
async def fetch_recovery_metrics(user_id: str) -> str:
    """Fetch user's latest WHOOP recovery metrics"""
    whoop_data = await get_whoop_recovery(user_id)
    if whoop_data:
        return f"""
WHOOP Recovery Metrics:
- Recovery Score: {whoop_data.recovery_score}/100
- Strain Score: {whoop_data.strain_score}/21
- Sleep: {whoop_data.sleep_hours} hours
- HRV: {whoop_data.hrv_ms}ms
- Resting HR: {whoop_data.resting_hr_bpm}bpm

Interpretation: {'Optimal recovery' if whoop_data.recovery_score >= 67 else 'Moderate recovery' if whoop_data.recovery_score >= 34 else 'Poor recovery - prioritize rest'}
"""
    return "No recovery data available"


@tool
def calculate_bmr_from_stats(weight_kg: float, height_cm: float, age: int, gender: str, lean_mass_kg: float) -> str:
    """Calculate Basal Metabolic Rate using both standard and lean mass formulas"""
    # Create mock BodyComposition for calculation
    from datetime import datetime
    body_comp = BodyComposition(
        user_id="temp",
        weight_kg=weight_kg,
        height_cm=height_cm,
        body_fat_percent=((weight_kg - lean_mass_kg) / weight_kg) * 100,
        lean_mass_kg=lean_mass_kg,
        age=age,
        gender=gender,
        scan_date=datetime.now()
    )

    standard_bmr = calculate_bmr(body_comp)
    lean_mass_bmr = calculate_lean_mass_bmr(body_comp)

    return f"""
BMR Calculations:
- Standard (Mifflin-St Jeor): {standard_bmr:.0f} calories/day
- Lean Mass (Katch-McArdle): {lean_mass_bmr:.0f} calories/day
Recommended: Use lean mass BMR ({lean_mass_bmr:.0f}) as it accounts for body composition
"""


@tool
def calculate_tdee_from_bmr(bmr: float, activity_level: str) -> str:
    """Calculate Total Daily Energy Expenditure from BMR and activity level"""
    tdee = calculate_tdee(bmr, activity_level)
    return f"""
TDEE Calculation:
- BMR: {bmr:.0f} calories/day
- Activity Level: {activity_level}
- TDEE: {tdee:.0f} calories/day
"""


# ===== MACRO CALCULATOR AGENT =====

class MacroCalculatorAgent:
    """Agent that calculates personalized macro targets"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        self.tools = [
            fetch_body_composition,
            fetch_recovery_metrics,
            calculate_bmr_from_stats,
            calculate_tdee_from_bmr
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert nutrition coach and macro calculator.

Your task is to calculate personalized macro targets for a user based on:
1. Body composition (weight, height, body fat %, lean mass)
2. Activity level
3. Nutrition goal (weight loss, muscle gain, maintenance, recomposition)
4. Recovery score (from WHOOP if available)

Steps:
1. Fetch the user's body composition
2. Fetch recovery metrics if available
3. Calculate BMR using lean mass formula
4. Calculate TDEE based on activity level
5. Adjust calories for goal:
   - Weight loss: -500 cal/day (1 lb/week loss)
   - Muscle gain: +300-500 cal/day
   - Maintenance: TDEE
   - Recomposition: TDEE or slight deficit (-200)
6. Adjust for recovery score if available
7. Calculate macro split:
   - Protein: 0.8-1.0g per lb bodyweight (prioritize in deficit)
   - Fats: 20-30% of calories
   - Carbs: Remaining calories

Provide detailed reasoning for your calculations."""),
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

    async def calculate_macros(
        self,
        user_id: str,
        activity_level: ActivityLevel,
        goal: NutritionGoal
    ) -> MacroCalculation:
        """
        Calculate macro targets for user

        Args:
            user_id: User identifier
            activity_level: Physical activity level
            goal: Nutrition goal

        Returns:
            MacroCalculation with targets and reasoning
        """
        # Build input prompt
        input_text = f"""
Calculate macro targets for user {user_id} with:
- Activity Level: {activity_level.value}
- Goal: {goal.value}

Use the tools to:
1. Fetch body composition
2. Fetch recovery metrics
3. Calculate BMR
4. Calculate TDEE
5. Determine calorie target
6. Calculate macro split

Provide the final numbers in this format:
CALORIES: [number]
PROTEIN: [grams]
CARBS: [grams]
FATS: [grams]
REASONING: [your detailed explanation]
"""

        # Run agent
        result = await self.executor.ainvoke({"input": input_text})

        # Parse agent output
        output = result["output"]

        # Extract numbers from output (simple parsing)
        calories = self._extract_number(output, "CALORIES:")
        protein_g = self._extract_number(output, "PROTEIN:")
        carbs_g = self._extract_number(output, "CARBS:")
        fat_g = self._extract_number(output, "FATS:")

        # Get body composition for return object
        body_comp = await get_latest_body_scan(user_id)

        # Get recovery score
        whoop_data = await get_whoop_recovery(user_id)
        recovery_score = whoop_data.recovery_score if whoop_data else None

        # Calculate ratios
        total_cals_from_macros = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
        protein_percent = (protein_g * 4) / total_cals_from_macros
        carbs_percent = (carbs_g * 4) / total_cals_from_macros
        fat_percent = (fat_g * 9) / total_cals_from_macros

        # Calculate TDEE for reference
        bmr = calculate_lean_mass_bmr(body_comp)
        tdee = calculate_tdee(bmr, activity_level.value)
        deficit_surplus = int(calories - tdee)

        # Create MacroProfile
        macro_profile = MacroProfile(
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            protein_percent=protein_percent,
            carbs_percent=carbs_percent,
            fat_percent=fat_percent,
            goal=goal,
            tdee=tdee,
            deficit_surplus=deficit_surplus
        )

        # Create MacroCalculation
        calculation = MacroCalculation(
            user_id=user_id,
            body_composition=body_comp,
            activity_level=activity_level,
            goal=goal,
            recovery_score=recovery_score,
            bmr=bmr,
            tdee=tdee,
            target_calories=calories,
            macro_profile=macro_profile,
            calculation_notes=output,
            timestamp=datetime.now()
        )

        return calculation

    def _extract_number(self, text: str, prefix: str) -> float:
        """Extract number following a prefix in text"""
        import re
        pattern = f"{re.escape(prefix)}\\s*(\\d+(?:\\.\\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return 0.0


# Global instance
macro_calculator_agent = MacroCalculatorAgent()


async def calculate_user_macros(
    user_id: str,
    activity_level: ActivityLevel,
    goal: NutritionGoal
) -> MacroCalculation:
    """
    Convenience function to calculate macros

    Args:
        user_id: User identifier
        activity_level: Activity level
        goal: Nutrition goal

    Returns:
        MacroCalculation
    """
    return await macro_calculator_agent.calculate_macros(user_id, activity_level, goal)
