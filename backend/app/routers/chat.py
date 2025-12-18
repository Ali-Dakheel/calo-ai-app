"""
Chat Router - Handles conversational interactions
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from app.models.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ConversationHistoryResponse,
    DeleteConversationResponse,
)
from app.services.agent_service import process_message, conversations
from app.services.llm_service import check_ollama_health
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message and get a response from the AI agent
    
    Args:
        request: Chat request with message and user info
        
    Returns:
        Chat response with agent's reply
    """
    # Validate Ollama is running
    if not await check_ollama_health():
        raise HTTPException(
            status_code=503,
            detail="LLM service is unavailable. Please ensure Ollama is running."
        )
    
    # Validate request
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    try:
        # Process message through agent system
        result = await process_message(
            message=request.message,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            agent_used=result["agent_used"],
            recommendations=result.get("recommendations"),
            requires_kitchen_action=result.get("requires_kitchen_action", False),
            confidence=result["confidence"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response for better UX
    
    Args:
        request: Chat request
        
    Returns:
        Streaming response
    """
    # Validate Ollama
    if not await check_ollama_health():
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable"
        )
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # For now, use non-streaming and simulate streaming
            # In production, implement true streaming with agent service
            result = await process_message(
                message=request.message,
                user_id=request.user_id,
                conversation_id=request.conversation_id
            )
            
            # Simulate streaming by chunking response
            response_text = result["message"]
            chunk_size = settings.stream_chunk_size
            
            words = response_text.split()
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                yield f"data: {chunk}\n\n"
            
            # Send final metadata
            yield f"data: [DONE]\n\n"
        
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )


@router.get("/history/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str) -> ConversationHistoryResponse:
    """
    Get conversation history

    Args:
        conversation_id: Conversation identifier

    Returns:
        List of messages in conversation
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = conversations[conversation_id]

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        message_count=len(history),
        messages=[
            ChatMessageResponse(
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in history
        ]
    )


@router.delete("/history/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(conversation_id: str) -> DeleteConversationResponse:
    """
    Delete a conversation

    Args:
        conversation_id: Conversation to delete

    Returns:
        Success message
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    del conversations[conversation_id]

    return DeleteConversationResponse(message="Conversation deleted successfully")
