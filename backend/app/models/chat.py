"""
Chat-related Pydantic models and schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request from user"""
    message: str = Field(..., min_length=1, max_length=1000)
    user_id: str = Field(..., description="User identifier")
    conversation_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response from agent"""
    message: str
    conversation_id: str
    agent_used: str
    recommendations: Optional[List[str]] = None
    requires_kitchen_action: bool = False
    confidence: float = Field(ge=0.0, le=1.0)


class ConversationHistory(BaseModel):
    """Conversation history"""
    conversation_id: str
    user_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


class StreamingChunk(BaseModel):
    """Streaming response chunk"""
    chunk: str
    is_final: bool = False
    metadata: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    """Chat message response for API"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history endpoint"""
    conversation_id: str
    message_count: int
    messages: List[ChatMessageResponse]


class DeleteConversationResponse(BaseModel):
    """Response model for delete conversation endpoint"""
    message: str
