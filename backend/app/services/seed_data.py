"""Seed data for demo presentation"""
from datetime import datetime, timedelta
from app.models.feedback import (
    CustomerFeedback, KitchenRequest, SentimentType, FeedbackCategory
)


def get_demo_kitchen_requests() -> list[KitchenRequest]:
    """Generate demo kitchen requests for presentation"""
    now = datetime.now()
    return [
        KitchenRequest(
            request_id="kr-001",
            user_id="user_demo1",
            original_message="The grilled chicken was too salty yesterday",
            request_type="Quality Complaint",
            details={"meal": "Grilled Chicken", "issue": "overseasoned"},
            priority=4,
            status="pending",
            created_at=now - timedelta(hours=2)
        ),
        KitchenRequest(
            request_id="kr-002",
            user_id="user_demo2",
            original_message="Can I get extra protein in my meals?",
            request_type="Modification Request",
            details={"request": "extra protein", "preference": "chicken or beef"},
            priority=3,
            status="in_progress",
            created_at=now - timedelta(hours=5)
        ),
        KitchenRequest(
            request_id="kr-003",
            user_id="user_demo3",
            original_message="I'm severely allergic to nuts, please be careful",
            request_type="Allergy Alert",
            details={"allergen": "nuts", "severity": "severe"},
            priority=5,
            status="pending",
            created_at=now - timedelta(minutes=30)
        ),
        KitchenRequest(
            request_id="kr-004",
            user_id="user_demo4",
            original_message="The portion was too small for lunch",
            request_type="Portion Complaint",
            details={"meal": "Salmon Bowl", "issue": "portion size"},
            priority=3,
            status="completed",
            created_at=now - timedelta(days=1)
        ),
        KitchenRequest(
            request_id="kr-005",
            user_id="user_demo5",
            original_message="Please no onions in any of my meals",
            request_type="Dietary Preference",
            details={"exclude": "onions", "reason": "preference"},
            priority=2,
            status="in_progress",
            created_at=now - timedelta(hours=8)
        ),
    ]


def get_demo_feedbacks() -> list[CustomerFeedback]:
    """Generate demo customer feedback for presentation"""
    now = datetime.now()
    return [
        CustomerFeedback(
            id="fb-001",
            user_id="user_demo1",
            meal_id="meal_grilled_chicken",
            rating=5,
            comment="The grilled chicken was absolutely delicious! Fresh ingredients and perfect seasoning.",
            sentiment=SentimentType.POSITIVE,
            categories=[FeedbackCategory.TASTE],
            timestamp=now - timedelta(days=1)
        ),
        CustomerFeedback(
            id="fb-002",
            user_id="user_demo2",
            meal_id="meal_salmon_bowl",
            rating=4,
            comment="Great healthy option, love the protein content. Would order again!",
            sentiment=SentimentType.POSITIVE,
            categories=[FeedbackCategory.NUTRITION, FeedbackCategory.TASTE],
            timestamp=now - timedelta(days=2)
        ),
        CustomerFeedback(
            id="fb-003",
            user_id="user_demo3",
            meal_id="meal_vegan_wrap",
            rating=2,
            comment="Portion was too small for the price. Left me hungry.",
            sentiment=SentimentType.NEGATIVE,
            categories=[FeedbackCategory.PORTION, FeedbackCategory.PRICE],
            timestamp=now - timedelta(days=1)
        ),
        CustomerFeedback(
            id="fb-004",
            user_id="user_demo4",
            meal_id="meal_beef_steak",
            rating=5,
            comment="Best steak I've had in ages! Perfectly cooked and tasty.",
            sentiment=SentimentType.POSITIVE,
            categories=[FeedbackCategory.TASTE],
            timestamp=now - timedelta(days=3)
        ),
        CustomerFeedback(
            id="fb-005",
            user_id="user_demo5",
            meal_id="meal_chicken_salad",
            rating=3,
            comment="Decent meal but delivery was late. Food was cold.",
            sentiment=SentimentType.NEUTRAL,
            categories=[FeedbackCategory.DELIVERY],
            timestamp=now - timedelta(days=2)
        ),
        CustomerFeedback(
            id="fb-006",
            user_id="user_demo6",
            meal_id="meal_protein_bowl",
            rating=5,
            comment="Amazing variety of options! Love the healthy choices.",
            sentiment=SentimentType.POSITIVE,
            categories=[FeedbackCategory.VARIETY, FeedbackCategory.NUTRITION],
            timestamp=now - timedelta(days=1)
        ),
        CustomerFeedback(
            id="fb-007",
            user_id="user_demo7",
            meal_id="meal_grilled_chicken",
            rating=1,
            comment="Chicken was way too salty. Terrible experience.",
            sentiment=SentimentType.NEGATIVE,
            categories=[FeedbackCategory.TASTE],
            timestamp=now - timedelta(hours=12)
        ),
        CustomerFeedback(
            id="fb-008",
            user_id="user_demo8",
            meal_id="meal_salmon_bowl",
            rating=4,
            comment="Fresh and healthy! The salmon was delicious.",
            sentiment=SentimentType.POSITIVE,
            categories=[FeedbackCategory.TASTE, FeedbackCategory.NUTRITION],
            timestamp=now - timedelta(days=4)
        ),
    ]
