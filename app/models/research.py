from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.core.config import MODEL_NAME


class ResearchRequest(BaseModel):
    """Request model for research endpoint."""
    query: str = Field(..., description="The research query to investigate")
    model_name: str = Field(default=MODEL_NAME, description="The model to use for research")
    stream: bool = Field(default=False, description="Whether to stream the response")


class ResearchResponse(BaseModel):
    """Response model for research endpoint."""
    message: Dict[str, str] = Field(..., description="The research response message")
    model: str = Field(..., description="The model used for research")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")


class StreamingChunk(BaseModel):
    """Model for streaming research chunks."""
    content: str = Field(..., description="The content of this chunk")
    done: bool = Field(..., description="Whether this is the final chunk")
    model: str = Field(..., description="The model used for this chunk") 