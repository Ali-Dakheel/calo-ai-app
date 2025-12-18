"""
Prompts package initialization
"""
from app.prompts.agent_prompts import *

__all__ = [
    "PREFERENCE_LEARNER_SYSTEM",
    "MEAL_RECOMMENDER_SYSTEM",
    "FEEDBACK_ANALYZER_SYSTEM",
    "KITCHEN_ROUTER_SYSTEM",
    "CONVERSATION_ROUTER_SYSTEM",
    "get_meal_recommendation_prompt",
    "get_feedback_analysis_prompt",
    "get_kitchen_routing_prompt",
    "get_routing_prompt"
]
