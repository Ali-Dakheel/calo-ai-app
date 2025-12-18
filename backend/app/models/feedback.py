"""
Feedback-related Pydantic models and schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class FeedbackCategory(str, Enum):
    """Feedback category"""
    TASTE = "taste"
    PORTION = "portion"
    DELIVERY = "delivery"
    PACKAGING = "packaging"
    NUTRITION = "nutrition"
    PRICE = "price"
    VARIETY = "variety"
    CUSTOM_REQUEST = "custom_request"


class CustomerFeedback(BaseModel):
    """Customer feedback model"""
    id: str
    user_id: str
    meal_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    comment: str
    sentiment: SentimentType
    categories: List[FeedbackCategory]
    timestamp: datetime = Field(default_factory=datetime.now)


class FeedbackAnalysis(BaseModel):
    """Analysis result of customer feedback"""
    feedback_id: str
    sentiment: SentimentType
    sentiment_score: float = Field(ge=0.0, le=1.0)
    key_themes: List[str]
    actionable_insights: List[str]
    requires_attention: bool
    suggested_response: Optional[str] = None


class KitchenRequest(BaseModel):
    """Special request routed to kitchen"""
    request_id: str
    user_id: str
    original_message: str
    request_type: str
    details: Dict[str, Any]
    priority: int = Field(ge=1, le=5, default=3)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class AnalyticsSummary(BaseModel):
    """Analytics summary"""
    total_feedback: int
    average_rating: float
    sentiment_breakdown: Dict[SentimentType, int]
    top_complaints: List[str]
    top_praises: List[str]
    popular_meals: List[str]
    action_items: List[str]
    time_period: str
