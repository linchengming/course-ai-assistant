"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.api.chat import router as chat_router
from app.config import get_settings
from app.utils.logger import setup_logger

# Setup logger
logger = setup_logger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Course AI Assistant",
    description="AI-powered course consultation assistant with RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Serve the chat interface."""
    static_file = Path(__file__).parent.parent / "static" / "index.html"
    if static_file.exists():
        return FileResponse(static_file)
    return {"message": "Course AI Assistant API", "docs": "/docs"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 50)
    logger.info("Course AI Assistant Starting...")
    logger.info(f"Host: {settings.app_host}:{settings.app_port}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Vector DB: {settings.vectordb_path}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Course AI Assistant Shutting Down...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
