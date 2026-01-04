"""
Data models and schemas for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User's question or message")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[str] = Field(..., description="Source documents used")
    session_id: str = Field(..., description="Session ID for this conversation")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    vector_db_count: int = Field(..., description="Number of documents in vector database")


class StatsResponse(BaseModel):
    """Response model for statistics endpoint."""
    total_queries: int = Field(..., description="Total number of queries processed")
    avg_response_time: float = Field(..., description="Average response time in seconds")
    accuracy_rate: float = Field(..., description="Estimated accuracy rate")
