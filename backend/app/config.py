"""
Application configuration and settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "Calo AI Nutrition Advisor"
    app_version: str = "1.0.0"
    debug: bool = True

    # CORS Settings
    cors_origins: List[str] = ["http://localhost:3000"]

    # Ollama Settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: int = 120

    # ChromaDB Settings
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "calo_meals"

    # Agent Settings
    max_conversation_history: int = 10
    temperature: float = 0.7
    max_tokens: int = 1000

    # RAG Settings
    rag_top_k: int = 5
    similarity_threshold: float = 0.7

    # Streaming Settings
    stream_chunk_size: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
