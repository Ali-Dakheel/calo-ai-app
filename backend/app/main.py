"""
Calo AI Nutrition Advisor - FastAPI Main Application
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import chat, recommendations, kitchen, analytics
from app.services.rag_service import initialize_rag_engine, meal_collection
from app.services.llm_service import check_ollama_health
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    # Startup: Initialize RAG engine with meal data
    logger.info("Initializing Calo AI Advisor...")
    await initialize_rag_engine()
    logger.info("RAG Engine initialized successfully")

    yield

    # Shutdown: Cleanup if needed
    logger.info("Shutting down Calo AI Advisor...")


app = FastAPI(
    title="Calo AI Nutrition Advisor",
    description="Intelligent meal recommendation and feedback analysis system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Calo AI Nutrition Advisor",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with real service verification"""
    # Check Ollama LLM service
    ollama_healthy = await check_ollama_health()

    # Check RAG service (ChromaDB collection)
    rag_healthy = meal_collection is not None

    # Determine overall status
    all_healthy = ollama_healthy and rag_healthy
    status = "healthy" if all_healthy else "degraded"

    return {
        "status": status,
        "services": {
            "api": "operational",
            "llm": "operational" if ollama_healthy else "unavailable",
            "rag": "operational" if rag_healthy else "unavailable"
        }
    }


# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(kitchen.router, prefix="/api/v1/kitchen", tags=["Kitchen"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )
