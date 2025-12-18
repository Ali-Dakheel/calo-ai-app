"""
Multi-Agent Service - Orchestrates different AI agents
"""
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import uuid

from app.services.llm_service import generate_completion, generate_structured_output
from app.services.rag_service import search_meals, get_contextual_meals
from app.prompts.agent_prompts import (
    PREFERENCE_LEARNER_SYSTEM,
    MEAL_RECOMMENDER_SYSTEM,
    FEEDBACK_ANALYZER_SYSTEM,
    KITCHEN_ROUTER_SYSTEM,
    CONVERSATION_ROUTER_SYSTEM,
    get_meal_recommendation_prompt,
    get_feedback_analysis_prompt,
    get_kitchen_routing_prompt,
    get_routing_prompt
)
from app.models.chat import ChatMessage

# In-memory conversation storage (in production, use database)
conversations: Dict[str, List[ChatMessage]] = {}
user_contexts: Dict[str, Dict] = {}


async def route_conversation(
    message: str,
    conversation_history: List[ChatMessage]
) -> str:
    """
    Route conversation to appropriate agent
    
    Args:
        message: Current user message
        conversation_history: Previous messages
        
    Returns:
        Agent name to handle the message
    """
    # Convert history to simple format
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation_history[-5:]
    ]
    
    prompt = get_routing_prompt(message, history)
    
    try:
        response = await generate_completion(
            prompt=prompt,
            system_prompt=CONVERSATION_ROUTER_SYSTEM,
            temperature=0.3
        )
        
        # Extract agent name
        response = response.strip().upper()
        if "PREFERENCE" in response:
            return "PREFERENCE_LEARNER"
        elif "MEAL" in response or "RECOMMEND" in response:
            return "MEAL_RECOMMENDER"
        elif "FEEDBACK" in response:
            return "FEEDBACK_ANALYZER"
        elif "KITCHEN" in response:
            return "KITCHEN_ROUTER"
        else:
            # Default to preference learner for general queries
            return "PREFERENCE_LEARNER"
    except Exception as e:
        print(f"Routing error: {e}")
        return "PREFERENCE_LEARNER"


async def handle_preference_learning(
    message: str,
    user_id: str,
    conversation_history: List[ChatMessage]
) -> Dict:
    """Handle preference learning conversation"""
    
    # Build conversation context
    history_text = "\n".join([
        f"{msg.role}: {msg.content}"
        for msg in conversation_history[-5:]
    ])
    
    prompt = f"""Conversation so far:
{history_text}

User: {message}

Continue the conversation naturally. Ask ONE follow-up question to learn more about their preferences."""
    
    response = await generate_completion(
        prompt=prompt,
        system_prompt=PREFERENCE_LEARNER_SYSTEM,
        temperature=0.8
    )
    
    # Extract any mentioned preferences
    preferences = _extract_preferences_from_conversation(message, response)
    if preferences:
        _update_user_context(user_id, preferences)
    
    return {
        "message": response,
        "agent_used": "PREFERENCE_LEARNER",
        "confidence": 0.9,
        "extracted_preferences": preferences
    }


async def handle_meal_recommendation(
    message: str,
    user_id: str,
    conversation_history: List[ChatMessage]
) -> Dict:
    """Handle meal recommendation requests"""
    
    # Get user context
    user_context = user_contexts.get(user_id, {})
    
    # Search for relevant meals using RAG
    relevant_meals, context_explanation = await get_contextual_meals(
        user_query=message,
        user_preferences=user_context,
        top_k=5
    )
    
    if not relevant_meals:
        return {
            "message": "I couldn't find any meals matching your criteria right now. Could you tell me more about what you're looking for?",
            "agent_used": "MEAL_RECOMMENDER",
            "confidence": 0.5,
            "recommendations": []
        }
    
    # Generate recommendation with explanations
    prompt = get_meal_recommendation_prompt(message, relevant_meals, user_context)
    
    response = await generate_completion(
        prompt=prompt,
        system_prompt=MEAL_RECOMMENDER_SYSTEM,
        temperature=0.7
    )
    
    # Extract meal IDs from recommendations
    recommended_ids = [meal['id'] for meal in relevant_meals[:3]]
    
    return {
        "message": response,
        "agent_used": "MEAL_RECOMMENDER",
        "confidence": 0.95,
        "recommendations": recommended_ids,
        "context": context_explanation
    }


async def handle_feedback_analysis(
    message: str,
    user_id: str
) -> Dict:
    """Handle feedback analysis"""
    
    prompt = get_feedback_analysis_prompt(message)
    
    try:
        analysis = await generate_structured_output(
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
        
        # Generate response to customer
        if analysis.get("sentiment") == "negative":
            customer_response = f"Thank you for your feedback. {analysis.get('suggested_response', 'We take your concerns seriously and will work to improve.')}"
        else:
            customer_response = f"Thank you for your feedback! {analysis.get('suggested_response', 'We appreciate you taking the time to share your experience.')}"
        
        return {
            "message": customer_response,
            "agent_used": "FEEDBACK_ANALYZER",
            "confidence": 0.9,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Feedback analysis error: {e}")
        return {
            "message": "Thank you for your feedback! We've recorded your comments and will review them shortly.",
            "agent_used": "FEEDBACK_ANALYZER",
            "confidence": 0.7
        }


async def handle_kitchen_routing(
    message: str,
    user_id: str
) -> Dict:
    """Handle special kitchen requests"""
    
    prompt = get_kitchen_routing_prompt(message)
    
    try:
        routing_info = await generate_structured_output(
            prompt=prompt,
            system_prompt=KITCHEN_ROUTER_SYSTEM,
            output_schema={
                "requires_kitchen_action": "boolean",
                "request_type": "string",
                "details": "object",
                "summary": "string"
            }
        )
        
        if routing_info.get("requires_kitchen_action"):
            response = "I've forwarded your special request to our kitchen team. They'll review it and get back to you within 24 hours!"
            
            # Store request (in production, save to database)
            request_id = str(uuid.uuid4())
            # kitchen_requests[request_id] = {
            #     "user_id": user_id,
            #     "message": message,
            #     "routing_info": routing_info,
            #     "timestamp": datetime.now()
            # }
        else:
            response = "I can help you with that! Let me know what you'd like to change about your meals."
        
        return {
            "message": response,
            "agent_used": "KITCHEN_ROUTER",
            "confidence": 0.85,
            "requires_kitchen_action": routing_info.get("requires_kitchen_action", False),
            "routing_info": routing_info
        }
    except Exception as e:
        print(f"Kitchen routing error: {e}")
        return {
            "message": "I've noted your request and will make sure the kitchen team reviews it!",
            "agent_used": "KITCHEN_ROUTER",
            "confidence": 0.7,
            "requires_kitchen_action": True
        }


async def process_message(
    message: str,
    user_id: str,
    conversation_id: Optional[str] = None
) -> Dict:
    """
    Main entry point for processing user messages
    
    Args:
        message: User message
        user_id: User identifier
        conversation_id: Optional conversation ID
        
    Returns:
        Response dictionary with agent output
    """
    # Get or create conversation
    if not conversation_id:
        conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Add user message to history
    user_msg = ChatMessage(role="user", content=message)
    conversations[conversation_id].append(user_msg)
    
    # Route to appropriate agent
    agent = await route_conversation(message, conversations[conversation_id])
    
    # Handle with specific agent
    if agent == "PREFERENCE_LEARNER":
        result = await handle_preference_learning(
            message, user_id, conversations[conversation_id]
        )
    elif agent == "MEAL_RECOMMENDER":
        result = await handle_meal_recommendation(
            message, user_id, conversations[conversation_id]
        )
    elif agent == "FEEDBACK_ANALYZER":
        result = await handle_feedback_analysis(message, user_id)
    elif agent == "KITCHEN_ROUTER":
        result = await handle_kitchen_routing(message, user_id)
    else:
        result = await handle_preference_learning(
            message, user_id, conversations[conversation_id]
        )
    
    # Add assistant response to history
    assistant_msg = ChatMessage(role="assistant", content=result["message"])
    conversations[conversation_id].append(assistant_msg)
    
    # Add conversation_id to result
    result["conversation_id"] = conversation_id
    
    return result


def _extract_preferences_from_conversation(user_msg: str, assistant_msg: str) -> Dict:
    """Extract dietary preferences from conversation"""
    preferences = {}
    
    user_lower = user_msg.lower()
    
    # Extract dietary tags
    dietary_tags = []
    if "vegetarian" in user_lower:
        dietary_tags.append("vegetarian")
    if "vegan" in user_lower:
        dietary_tags.append("vegan")
    if "keto" in user_lower:
        dietary_tags.append("keto")
    if "gluten free" in user_lower or "gluten-free" in user_lower:
        dietary_tags.append("gluten_free")
    if "dairy free" in user_lower or "dairy-free" in user_lower:
        dietary_tags.append("dairy_free")
    if "halal" in user_lower:
        dietary_tags.append("halal")
    
    if dietary_tags:
        preferences["dietary_restrictions"] = dietary_tags
    
    # Extract calorie goals
    if "calorie" in user_lower:
        # Simple extraction - could be improved with regex
        words = user_lower.split()
        for i, word in enumerate(words):
            if word.isdigit() and int(word) > 200 and int(word) < 5000:
                preferences["calorie_target"] = int(word)
                break
    
    return preferences


def _update_user_context(user_id: str, new_preferences: Dict):
    """Update user context with new preferences"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    
    # Merge preferences
    for key, value in new_preferences.items():
        if key == "dietary_restrictions":
            existing = user_contexts[user_id].get(key, [])
            user_contexts[user_id][key] = list(set(existing + value))
        else:
            user_contexts[user_id][key] = value
