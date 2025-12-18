"""
Calo AI Nutrition Advisor - FastAPI Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import chat, recommendations, kitchen, analytics
from app.services.rag_service import initialize_rag_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events"""
    # Startup: Initialize RAG engine with meal data
    print("🚀 Initializing Calo AI Advisor...")
    await initialize_rag_engine()
    print("✅ RAG Engine initialized successfully")
    
    yield
    
    # Shutdown: Cleanup if needed
    print("👋 Shutting down Calo AI Advisor...")


app = FastAPI(
    title="Calo AI Nutrition Advisor",
    description="Intelligent meal recommendation and feedback analysis system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "llm": "operational",
            "rag": "operational"
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
