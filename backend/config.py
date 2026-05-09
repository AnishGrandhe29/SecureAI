"""
Application configuration — all settings loaded from environment variables.
Uses pydantic-settings BaseSettings for type-safe config with .env file support.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # === Required (no defaults) ===
    GEMINI_API_KEY: str
    SECRET_KEY: str

    # === Database ===
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/insights.db"

    # === Redis ===
    REDIS_URL: str = "redis://redis:6379"

    # === ChromaDB ===
    CHROMA_PATH: str = "./chroma_db"

    # === Application ===
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8

    # === JWT ===
    JWT_ALGORITHM: str = "HS256"

    # === Gemini ===
    GEMINI_MODEL: str = "gemini-1.5-pro"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
