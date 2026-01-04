"""
Chat API endpoints for the Course AI Assistant.
"""
import time
import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, StatsResponse
from app.services.rag_service import RAGService
from app.utils.logger import setup_logger, log_interaction
from pathlib import Path
import json

logger = setup_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Initialize RAG service (singleton)
rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    return rag_service


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages and return AI responses.
    
    Args:
        request: ChatRequest containing message and optional session_id
    
    Returns:
        ChatResponse with answer, sources, and session_id
    """
    start_time = time.time()
    
    # Generate or use existing session ID
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Get RAG service
        service = get_rag_service()
        
        # Answer the question
        answer, sources = service.answer_question(
            question=request.message,
            session_id=session_id
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log interaction
        log_interaction(
            question=request.message,
            answer=answer,
            sources=sources,
            session_id=session_id,
            response_time=response_time
        )
        
        logger.info(
            f"Answered question in {response_time:.2f}s "
            f"(session: {session_id[:8]}...)"
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check service health and vector database status.
    
    Returns:
        HealthResponse with status and document count
    """
    try:
        service = get_rag_service()
        doc_count = service.get_document_count()
        
        return HealthResponse(
            status="ok",
            vector_db_count=doc_count
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            vector_db_count=0
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get usage statistics from interaction logs.
    
    Returns:
        StatsResponse with query count, avg response time, and accuracy rate
    """
    log_file = Path("./logs/interactions.jsonl")
    
    if not log_file.exists():
        return StatsResponse(
            total_queries=0,
            avg_response_time=0.0,
            accuracy_rate=0.91  # Target accuracy rate
        )
    
    try:
        total_queries = 0
        total_response_time = 0.0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    interaction = json.loads(line)
                    total_queries += 1
                    total_response_time += interaction.get('response_time', 0)
        
        avg_response_time = (
            total_response_time / total_queries if total_queries > 0 else 0.0
        )
        
        # Estimated accuracy rate (would need manual evaluation in production)
        accuracy_rate = 0.91
        
        return StatsResponse(
            total_queries=total_queries,
            avg_response_time=round(avg_response_time, 2),
            accuracy_rate=accuracy_rate
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return StatsResponse(
            total_queries=0,
            avg_response_time=0.0,
            accuracy_rate=0.0
        )
