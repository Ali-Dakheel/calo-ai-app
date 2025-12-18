"""
Analytics Router - Feedback analysis and insights
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.models.feedback import (
    CustomerFeedback,
    FeedbackAnalysis,
    AnalyticsSummary,
    SentimentType,
    FeedbackCategory
)
from app.services.llm_service import generate_structured_output
from app.prompts.agent_prompts import get_feedback_analysis_prompt, FEEDBACK_ANALYZER_SYSTEM
from app.services.seed_data import get_demo_feedbacks

router = APIRouter()

# In-memory storage for demo
feedbacks: dict[str, CustomerFeedback] = {}
analyses: dict[str, FeedbackAnalysis] = {}


def _load_seed_data():
    """Load demo data for presentation"""
    for feedback in get_demo_feedbacks():
        feedbacks[feedback.id] = feedback


# Load seed data on module import
_load_seed_data()


@router.post("/feedback")
async def submit_feedback(
    user_id: str,
    meal_id: Optional[str],
    rating: int,
    comment: str
):
    """
    Submit customer feedback
    
    Args:
        user_id: User identifier
        meal_id: Optional meal identifier
        rating: Rating from 1-5
        comment: Feedback comment
        
    Returns:
        Feedback submission confirmation
    """
    if not user_id or not comment:
        raise HTTPException(status_code=400, detail="User ID and comment are required")
    
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create feedback ID
    feedback_id = str(uuid.uuid4())
    
    # Analyze sentiment (simplified)
    sentiment = _quick_sentiment(rating, comment)
    
    # Categorize feedback
    categories = _categorize_feedback(comment)
    
    feedback = CustomerFeedback(
        id=feedback_id,
        user_id=user_id,
        meal_id=meal_id,
        rating=rating,
        comment=comment,
        sentiment=sentiment,
        categories=categories,
        timestamp=datetime.now()
    )
    
    feedbacks[feedback_id] = feedback
    
    # Trigger async analysis
    try:
        analysis = await _analyze_feedback(feedback)
        analyses[feedback_id] = analysis
    except Exception as e:
        print(f"Analysis error: {e}")
    
    return {
        "feedback_id": feedback_id,
        "status": "received",
        "message": "Thank you for your feedback!"
    }


@router.get("/feedback/{feedback_id}")
async def get_feedback(feedback_id: str):
    """Get specific feedback with analysis"""
    if feedback_id not in feedbacks:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    feedback = feedbacks[feedback_id]
    analysis = analyses.get(feedback_id)
    
    return {
        "feedback": feedback.model_dump(),
        "analysis": analysis.model_dump() if analysis else None
    }


@router.get("/feedback")
async def list_feedback(
    sentiment: Optional[SentimentType] = None,
    category: Optional[FeedbackCategory] = None,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(50, ge=1, le=200)
):
    """
    List feedback with filters
    
    Args:
        sentiment: Filter by sentiment
        category: Filter by category
        min_rating: Minimum rating
        limit: Maximum results
        
    Returns:
        List of feedback
    """
    results = list(feedbacks.values())
    
    # Apply filters
    if sentiment:
        results = [f for f in results if f.sentiment == sentiment]
    
    if category:
        results = [f for f in results if category in f.categories]
    
    if min_rating:
        results = [f for f in results if f.rating >= min_rating]
    
    # Sort by timestamp (most recent first)
    results.sort(key=lambda f: f.timestamp, reverse=True)
    
    return {
        "total": len(results),
        "feedback": [f.model_dump() for f in results[:limit]]
    }


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365),
    meal_id: Optional[str] = None
):
    """
    Get analytics summary
    
    Args:
        days: Number of days to analyze
        meal_id: Optional filter by specific meal
        
    Returns:
        Analytics summary with insights
    """
    # Filter feedback by date range
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_feedback = [
        f for f in feedbacks.values()
        if f.timestamp >= cutoff_date
    ]
    
    # Filter by meal if specified
    if meal_id:
        recent_feedback = [f for f in recent_feedback if f.meal_id == meal_id]
    
    if not recent_feedback:
        return {
            "message": "No feedback found for the specified period",
            "total_feedback": 0
        }
    
    # Calculate statistics
    total = len(recent_feedback)
    avg_rating = sum(f.rating for f in recent_feedback) / total
    
    # Sentiment breakdown
    sentiment_breakdown = {
        SentimentType.POSITIVE: len([f for f in recent_feedback if f.sentiment == SentimentType.POSITIVE]),
        SentimentType.NEUTRAL: len([f for f in recent_feedback if f.sentiment == SentimentType.NEUTRAL]),
        SentimentType.NEGATIVE: len([f for f in recent_feedback if f.sentiment == SentimentType.NEGATIVE])
    }
    
    # Find top complaints and praises
    negative_feedback = [f for f in recent_feedback if f.sentiment == SentimentType.NEGATIVE]
    positive_feedback = [f for f in recent_feedback if f.sentiment == SentimentType.POSITIVE]
    
    # Category analysis
    category_counts = {}
    for feedback in recent_feedback:
        for cat in feedback.categories:
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1
    
    top_complaints = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Generate action items
    action_items = _generate_action_items(recent_feedback, analyses)
    
    summary = AnalyticsSummary(
        total_feedback=total,
        average_rating=round(avg_rating, 2),
        sentiment_breakdown=sentiment_breakdown,
        top_complaints=[f"{cat.value}: {count}" for cat, count in top_complaints],
        top_praises=_extract_top_praises(positive_feedback),
        popular_meals=_get_popular_meals_from_feedback(recent_feedback),
        action_items=action_items,
        time_period=f"Last {days} days"
    )
    
    return summary.model_dump()


@router.get("/trends")
async def get_feedback_trends(days: int = Query(30, ge=7, le=365)):
    """
    Get feedback trends over time
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Trend data
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_feedback = [
        f for f in feedbacks.values()
        if f.timestamp >= cutoff_date
    ]
    
    # Group by day
    daily_stats = {}
    for feedback in recent_feedback:
        day = feedback.timestamp.date().isoformat()
        
        if day not in daily_stats:
            daily_stats[day] = {
                "count": 0,
                "total_rating": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0
            }
        
        stats = daily_stats[day]
        stats["count"] += 1
        stats["total_rating"] += feedback.rating
        
        if feedback.sentiment == SentimentType.POSITIVE:
            stats["positive"] += 1
        elif feedback.sentiment == SentimentType.NEUTRAL:
            stats["neutral"] += 1
        else:
            stats["negative"] += 1
    
    # Calculate averages
    trends = []
    for day, stats in sorted(daily_stats.items()):
        trends.append({
            "date": day,
            "count": stats["count"],
            "average_rating": round(stats["total_rating"] / stats["count"], 2),
            "sentiment_distribution": {
                "positive": stats["positive"],
                "neutral": stats["neutral"],
                "negative": stats["negative"]
            }
        })
    
    return {
        "period": f"Last {days} days",
        "trends": trends
    }


async def _analyze_feedback(feedback: CustomerFeedback) -> FeedbackAnalysis:
    """Analyze feedback using LLM"""
    try:
        prompt = get_feedback_analysis_prompt(feedback.comment)
        
        result = await generate_structured_output(
            prompt=prompt,
            system_prompt=FEEDBACK_ANALYZER_SYSTEM,
            output_schema={
                "sentiment": "string",
                "sentiment_score": "float",
                "key_themes": "array",
                "actionable_insights": "array",
                "requires_attention": "boolean",
                "suggested_response": "string"
            }
        )
        
        return FeedbackAnalysis(
            feedback_id=feedback.id,
            sentiment=SentimentType(result.get("sentiment", "neutral")),
            sentiment_score=result.get("sentiment_score", 0.5),
            key_themes=result.get("key_themes", []),
            actionable_insights=result.get("actionable_insights", []),
            requires_attention=result.get("requires_attention", False),
            suggested_response=result.get("suggested_response")
        )
    
    except Exception as e:
        print(f"Analysis error: {e}")
        # Return basic analysis
        return FeedbackAnalysis(
            feedback_id=feedback.id,
            sentiment=feedback.sentiment,
            sentiment_score=0.5,
            key_themes=[],
            actionable_insights=[],
            requires_attention=feedback.rating <= 2
        )


def _quick_sentiment(rating: int, comment: str) -> SentimentType:
    """Quick sentiment classification"""
    comment_lower = comment.lower()
    
    # Positive indicators
    positive_words = ["great", "excellent", "amazing", "love", "best", "delicious", "perfect"]
    negative_words = ["bad", "terrible", "awful", "hate", "worst", "disgusting", "poor"]
    
    has_positive = any(word in comment_lower for word in positive_words)
    has_negative = any(word in comment_lower for word in negative_words)
    
    if rating >= 4 and (has_positive or not has_negative):
        return SentimentType.POSITIVE
    elif rating <= 2 or has_negative:
        return SentimentType.NEGATIVE
    else:
        return SentimentType.NEUTRAL


def _categorize_feedback(comment: str) -> List[FeedbackCategory]:
    """Categorize feedback based on keywords"""
    categories = []
    comment_lower = comment.lower()
    
    keywords = {
        FeedbackCategory.TASTE: ["taste", "flavor", "delicious", "bland", "spicy", "salty"],
        FeedbackCategory.PORTION: ["portion", "size", "small", "large", "hungry", "too much"],
        FeedbackCategory.DELIVERY: ["delivery", "late", "on time", "driver", "arrived"],
        FeedbackCategory.PACKAGING: ["packaging", "container", "leaked", "damaged", "box"],
        FeedbackCategory.NUTRITION: ["healthy", "calories", "protein", "carbs", "nutrition"],
        FeedbackCategory.PRICE: ["price", "expensive", "cheap", "value", "cost"],
        FeedbackCategory.VARIETY: ["variety", "options", "same", "different", "choices"]
    }
    
    for category, words in keywords.items():
        if any(word in comment_lower for word in words):
            categories.append(category)
    
    if not categories:
        categories.append(FeedbackCategory.CUSTOM_REQUEST)
    
    return categories


def _generate_action_items(
    feedback_list: List[CustomerFeedback],
    analyses_dict: dict
) -> List[str]:
    """Generate action items from feedback"""
    items = []
    
    # Check for recurring issues
    negative = [f for f in feedback_list if f.sentiment == SentimentType.NEGATIVE]
    
    if len(negative) > len(feedback_list) * 0.2:  # More than 20% negative
        items.append("High negative feedback rate - investigate quality issues")
    
    # Category-based actions
    all_categories = []
    for f in negative:
        all_categories.extend(f.categories)
    
    from collections import Counter
    common_issues = Counter(all_categories).most_common(3)
    
    for category, count in common_issues:
        if count >= 3:
            items.append(f"Multiple complaints about {category.value} - needs attention")
    
    return items[:5]  # Top 5 action items


def _extract_top_praises(positive_feedback: List[CustomerFeedback]) -> List[str]:
    """Extract common praises"""
    if not positive_feedback:
        return []
    
    # Simple keyword extraction
    praises = []
    for feedback in positive_feedback[:10]:
        comment = feedback.comment.lower()
        if "delicious" in comment or "tasty" in comment:
            praises.append("Great taste")
        if "healthy" in comment:
            praises.append("Healthy options")
        if "fresh" in comment:
            praises.append("Fresh ingredients")
    
    return list(set(praises))[:5]


def _get_popular_meals_from_feedback(feedback_list: List[CustomerFeedback]) -> List[str]:
    """Get most mentioned meals"""
    meal_ratings = {}
    
    for feedback in feedback_list:
        if feedback.meal_id and feedback.rating >= 4:
            if feedback.meal_id not in meal_ratings:
                meal_ratings[feedback.meal_id] = 0
            meal_ratings[feedback.meal_id] += 1
    
    popular = sorted(meal_ratings.items(), key=lambda x: x[1], reverse=True)
    return [meal_id for meal_id, _ in popular[:5]]
