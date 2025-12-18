"""
Services package initialization
"""
from app.services.llm_service import (
    generate_completion,
    generate_streaming_completion,
    generate_structured_output,
    embed_text,
    check_ollama_health
)
from app.services.rag_service import (
    initialize_rag_engine,
    search_meals,
    get_meal_by_id,
    get_contextual_meals
)
from app.services.agent_service import (
    process_message,
    route_conversation
)
from app.services.meal_service import (
    get_all_meals,
    get_meal_details,
    filter_meals_by_criteria,
    get_popular_meals,
    generate_meal_plan
)

__all__ = [
    # LLM Service
    "generate_completion",
    "generate_streaming_completion",
    "generate_structured_output",
    "embed_text",
    "check_ollama_health",
    # RAG Service
    "initialize_rag_engine",
    "search_meals",
    "get_meal_by_id",
    "get_contextual_meals",
    # Agent Service
    "process_message",
    "route_conversation",
    # Meal Service
    "get_all_meals",
    "get_meal_details",
    "filter_meals_by_criteria",
    "get_popular_meals",
    "generate_meal_plan",
]
