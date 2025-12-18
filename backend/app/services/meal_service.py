"""
Meal Service - Business logic for meal operations
"""
from typing import List, Optional, Dict
from app.services.rag_service import search_meals, get_meal_by_id
from app.models.meal import (
    Meal,
    MealCategory,
    DietaryTag,
    NutritionInfo,
    MealRecommendation
)
import json
from pathlib import Path


async def get_all_meals() -> List[Dict]:
    """Get all available meals"""
    data_path = Path(__file__).parent.parent / "data" / "meals.json"
    
    if not data_path.exists():
        return []
    
    with open(data_path, 'r') as f:
        return json.load(f)


async def get_meal_details(meal_id: str) -> Optional[Dict]:
    """Get detailed information for a specific meal"""
    result = await get_meal_by_id(meal_id)
    
    if not result:
        return None
    
    # Load full meal data
    meals = await get_all_meals()
    for meal in meals:
        if meal["id"] == meal_id:
            return meal
    
    return None


async def filter_meals_by_criteria(
    category: Optional[MealCategory] = None,
    dietary_tags: Optional[List[DietaryTag]] = None,
    max_calories: Optional[int] = None,
    min_protein: Optional[float] = None,
    exclude_allergens: Optional[List[str]] = None
) -> List[Dict]:
    """Filter meals by various criteria"""
    meals = await get_all_meals()
    filtered = meals
    
    # Apply filters
    if category:
        filtered = [m for m in filtered if m["category"] == category.value]
    
    if dietary_tags:
        tag_values = [tag.value for tag in dietary_tags]
        filtered = [
            m for m in filtered
            if any(tag in m["dietary_tags"] for tag in tag_values)
        ]
    
    if max_calories:
        filtered = [m for m in filtered if m["nutrition"]["calories"] <= max_calories]
    
    if min_protein:
        filtered = [m for m in filtered if m["nutrition"]["protein"] >= min_protein]
    
    if exclude_allergens:
        filtered = [
            m for m in filtered
            if not any(allergen in m.get("allergens", []) for allergen in exclude_allergens)
        ]
    
    return filtered


async def get_popular_meals(limit: int = 10) -> List[Dict]:
    """Get most popular meals"""
    meals = await get_all_meals()
    
    # Sort by popularity score
    sorted_meals = sorted(
        meals,
        key=lambda m: m.get("popularity_score", 0),
        reverse=True
    )
    
    return sorted_meals[:limit]


async def calculate_meal_score(
    meal: Dict,
    user_preferences: Dict
) -> float:
    """
    Calculate how well a meal matches user preferences
    
    Args:
        meal: Meal dictionary
        user_preferences: User preferences dictionary
        
    Returns:
        Score from 0.0 to 1.0
    """
    score = 0.0
    factors = 0
    
    # Check dietary restrictions match
    if "dietary_restrictions" in user_preferences:
        required_tags = user_preferences["dietary_restrictions"]
        meal_tags = meal["dietary_tags"]
        
        matches = sum(1 for tag in required_tags if tag in meal_tags)
        if required_tags:
            score += matches / len(required_tags)
            factors += 1
    
    # Check calorie target
    if "calorie_target" in user_preferences:
        target = user_preferences["calorie_target"]
        actual = meal["nutrition"]["calories"]
        
        # Calculate how close to target (within 20% is perfect)
        diff = abs(actual - target) / target
        calorie_score = max(0, 1 - diff) if diff <= 0.5 else 0
        
        score += calorie_score
        factors += 1
    
    # Check protein goals
    if "min_protein" in user_preferences:
        target = user_preferences["min_protein"]
        actual = meal["nutrition"]["protein"]
        
        protein_score = min(1.0, actual / target) if target > 0 else 0.5
        score += protein_score
        factors += 1
    
    # Add popularity factor
    score += meal.get("popularity_score", 0.5)
    factors += 1
    
    return score / factors if factors > 0 else 0.5


async def generate_meal_plan(
    user_preferences: Dict,
    days: int = 7,
    meals_per_day: int = 3
) -> Dict[str, List[Dict]]:
    """
    Generate a meal plan for multiple days
    
    Args:
        user_preferences: User dietary preferences
        days: Number of days to plan
        meals_per_day: Meals per day (default 3: breakfast, lunch, dinner)
        
    Returns:
        Dictionary mapping day to list of meals
    """
    meal_plan = {}
    
    categories = [MealCategory.BREAKFAST, MealCategory.LUNCH, MealCategory.DINNER]
    
    for day in range(1, days + 1):
        day_meals = []
        
        for category in categories[:meals_per_day]:
            # Get meals for this category
            meals = await filter_meals_by_criteria(category=category)
            
            if not meals:
                continue
            
            # Score each meal
            scored_meals = [
                {
                    **meal,
                    "match_score": await calculate_meal_score(meal, user_preferences)
                }
                for meal in meals
            ]
            
            # Sort by score
            scored_meals.sort(key=lambda m: m["match_score"], reverse=True)
            
            # Pick top meal (in production, add variety logic)
            if scored_meals:
                day_meals.append(scored_meals[0])
        
        meal_plan[f"day_{day}"] = day_meals
    
    return meal_plan
