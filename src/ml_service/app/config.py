"""
Configuration settings for ML Service
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """ML Service settings"""

    # Service
    SERVICE_NAME: str = "ml-service"
    SERVICE_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: Optional[str] = (
        None  # "postgresql://wojciechkowalinski@localhost/workoutbuddy"
    )

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # ML Models
    ML_MODEL_PATH: str = "./models"
    MODEL_CACHE_SIZE: int = 100

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    # Backend API
    BACKEND_API_URL: str = "http://backend:8000"

    # External APIs
    ANTHROPIC_API_KEY: Optional[str] = None
    POSTHOG_API_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    # Model Training
    TRAINING_BATCH_SIZE: int = 32
    TRAINING_EPOCHS: int = 100
    MODEL_SAVE_INTERVAL: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
