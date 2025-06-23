# backend/app/config.py
"""
Configuration settings for Pulse Fitness App
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Pulse Fitness"

    # Database
    DATABASE_URL: str = "postgresql://pulse:pulse123@db:5432/pulse_fitness"

    # Security
    SECRET_KEY: str = "your-super-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # External APIs
    ANTHROPIC_API_KEY: Optional[str] = None
    POSTHOG_API_KEY: Optional[str] = None

    # ML Service
    ML_SERVICE_URL: str = "http://ml-service:8001"

    # ML Models (for backward compatibility)
    ML_MODEL_PATH: str = "/app/ml_models"
    MODEL_CACHE_SIZE: int = 100

    # Debug
    DEBUG: bool = False

    # Data
    DATA_PATH: str = "/app/data"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
