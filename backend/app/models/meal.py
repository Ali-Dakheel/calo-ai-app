"""
Meal-related Pydantic models and schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class MealCategory(str, Enum):
    """Meal category types"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class DietaryTag(str, Enum):
    """Dietary restriction tags"""
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"
    HALAL = "halal"


class NutritionInfo(BaseModel):
    """Nutritional information"""
    calories: int = Field(ge=0)
    protein: float = Field(ge=0, description="Protein in grams")
    carbs: float = Field(ge=0, description="Carbohydrates in grams")
    fats: float = Field(ge=0, description="Fats in grams")
    fiber: Optional[float] = Field(None, ge=0)
    sodium: Optional[float] = Field(None, ge=0)


class Meal(BaseModel):
    """Meal model"""
    id: str
    name: str
    description: str
    category: MealCategory
    dietary_tags: List[DietaryTag]
    nutrition: NutritionInfo
    ingredients: List[str]
    allergens: List[str] = []
    preparation_time: int = Field(..., description="Preparation time in minutes")
    price: float = Field(ge=0)
    image_url: Optional[str] = None
    popularity_score: float = Field(default=0.0, ge=0.0, le=1.0)


class MealRecommendation(BaseModel):
    """Meal recommendation with reasoning"""
    meal: Meal
    relevance_score: float = Field(ge=0.0, le=1.0)
    reasoning: str
    matches_preferences: List[str]


class RecommendationRequest(BaseModel):
    """Request for meal recommendations"""
    user_id: str
    preferences: Optional[Dict[str, Any]] = None
    dietary_restrictions: List[DietaryTag] = []
    calorie_target: Optional[int] = None
    meal_category: Optional[MealCategory] = None
    exclude_ingredients: List[str] = []
    max_results: int = Field(default=5, ge=1, le=20)


class RecommendationResponse(BaseModel):
    """Response with meal recommendations"""
    recommendations: List[MealRecommendation]
    total_found: int
    query_understanding: str
