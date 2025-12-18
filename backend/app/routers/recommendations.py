"""
Recommendations Router - Meal recommendations and filtering
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.meal import (
    RecommendationRequest,
    RecommendationResponse,
    MealRecommendation,
    Meal,
    MealCategory,
    DietaryTag
)
from app.services.meal_service import (
    get_all_meals,
    get_meal_details,
    filter_meals_by_criteria,
    get_popular_meals,
    calculate_meal_score
)
from app.services.rag_service import search_meals

router = APIRouter()


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get personalized meal recommendations
    
    Args:
        request: Recommendation request with user preferences
        
    Returns:
        Recommended meals with reasoning
    """
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        # Build search query from preferences
        query_parts = []
        
        if request.dietary_restrictions:
            tags = [tag.value for tag in request.dietary_restrictions]
            query_parts.append(f"dietary preferences: {', '.join(tags)}")
        
        if request.calorie_target:
            query_parts.append(f"around {request.calorie_target} calories")
        
        if request.meal_category:
            query_parts.append(f"{request.meal_category.value}")
        
        if request.exclude_ingredients:
            query_parts.append(f"without {', '.join(request.exclude_ingredients)}")
        
        query = " ".join(query_parts) if query_parts else "healthy meals"
        
        # Search using RAG
        meals = await search_meals(
            query=query,
            category=request.meal_category.value if request.meal_category else None,
            max_results=request.max_results
        )
        
        if not meals:
            raise HTTPException(status_code=404, detail="No meals found matching criteria")
        
        # Convert to recommendations
        recommendations = []
        for meal_data in meals:
            # Get full meal details
            full_meal = await get_meal_details(meal_data['id'])
            
            if not full_meal:
                continue
            
            # Calculate relevance score
            relevance = meal_data.get('relevance_score', 0.8)
            
            # Generate reasoning
            reasoning = _generate_reasoning(
                full_meal,
                request.dietary_restrictions,
                request.calorie_target
            )
            
            # Find matching preferences
            matches = []
            if request.dietary_restrictions:
                meal_tags = full_meal['dietary_tags']
                for tag in request.dietary_restrictions:
                    if tag.value in meal_tags:
                        matches.append(f"Matches {tag.value} diet")
            
            if request.calorie_target:
                cal_diff = abs(full_meal['nutrition']['calories'] - request.calorie_target)
                if cal_diff < 100:
                    matches.append(f"Close to {request.calorie_target} calorie target")
            
            recommendations.append(MealRecommendation(
                meal=Meal(**full_meal),
                relevance_score=relevance,
                reasoning=reasoning,
                matches_preferences=matches
            ))
        
        return RecommendationResponse(
            recommendations=recommendations,
            total_found=len(recommendations),
            query_understanding=query
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/meal/{meal_id}")
async def get_meal(meal_id: str):
    """
    Get detailed information about a specific meal
    
    Args:
        meal_id: Meal identifier
        
    Returns:
        Meal details
    """
    meal = await get_meal_details(meal_id)
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return meal


@router.get("/browse")
async def browse_meals(
    category: Optional[MealCategory] = Query(None),
    dietary_tag: Optional[DietaryTag] = Query(None),
    max_calories: Optional[int] = Query(None, ge=0, le=2000),
    min_protein: Optional[float] = Query(None, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Browse meals with filters
    
    Args:
        category: Filter by meal category
        dietary_tag: Filter by dietary tag
        max_calories: Maximum calories
        min_protein: Minimum protein
        limit: Maximum results
        
    Returns:
        Filtered list of meals
    """
    try:
        meals = await filter_meals_by_criteria(
            category=category,
            dietary_tags=[dietary_tag] if dietary_tag else None,
            max_calories=max_calories,
            min_protein=min_protein
        )
        
        return {
            "total": len(meals),
            "meals": meals[:limit]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error browsing meals: {str(e)}"
        )


@router.get("/popular")
async def get_popular(limit: int = Query(10, ge=1, le=50)):
    """
    Get most popular meals
    
    Args:
        limit: Number of meals to return
        
    Returns:
        List of popular meals
    """
    try:
        meals = await get_popular_meals(limit=limit)
        
        return {
            "total": len(meals),
            "meals": meals
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching popular meals: {str(e)}"
        )


def _generate_reasoning(
    meal: dict,
    dietary_restrictions: Optional[List[DietaryTag]],
    calorie_target: Optional[int]
) -> str:
    """Generate reasoning for why a meal is recommended"""
    reasons = []
    
    # Dietary match
    if dietary_restrictions:
        meal_tags = meal['dietary_tags']
        matching = [tag.value for tag in dietary_restrictions if tag.value in meal_tags]
        if matching:
            reasons.append(f"Matches your {', '.join(matching)} preferences")
    
    # Calorie alignment
    if calorie_target:
        calories = meal['nutrition']['calories']
        if abs(calories - calorie_target) < 50:
            reasons.append(f"Perfect for your {calorie_target} calorie target")
        elif abs(calories - calorie_target) < 100:
            reasons.append(f"Close to your {calorie_target} calorie target")
    
    # Nutritional highlights
    protein = meal['nutrition']['protein']
    if protein > 25:
        reasons.append(f"High in protein ({protein}g)")
    
    fiber = meal['nutrition'].get('fiber', 0)
    if fiber > 8:
        reasons.append(f"Excellent fiber content ({fiber}g)")
    
    # Popularity
    popularity = meal.get('popularity_score', 0)
    if popularity > 0.9:
        reasons.append("Highly rated by customers")
    
    if not reasons:
        reasons.append("Balanced and nutritious option")
    
    return ". ".join(reasons) + "."
