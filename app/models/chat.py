from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")


class StreamingChunk(BaseModel):
    """Streaming chunk model for partial responses."""
    content: str = Field(..., description="Partial content chunk for streaming")
    done: bool = Field(False, description="Whether this is the last chunk")
    model: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage] = Field(..., description="List of previous messages in the conversation")
    max_tokens: Optional[int] = Field(1000, description="Maximum number of tokens to generate")
    model_name: Optional[str] = Field(None, description="The name of the model to use (e.g., gpt-4, gpt-3.5-turbo)")
    stream: bool = Field(False, description="Whether to stream the response or not")


class ChatResponse(BaseModel):
    """Chat response model."""
    message: ChatMessage
    usage: Optional[dict] = None
    model: Optional[str] = None 