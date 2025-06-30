# backend/app/main.py
"""
Pulse Fitness App - Main FastAPI Application
A social fitness application with ML-powered workout recommendations
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    exercises,
    recommendations,
    social,
    users,
    workouts,
    challenges,
    safety,
    privacy,
    community,
    accountability,
    subscriptions,
)
from app.config import settings
from app.database import Base, engine
from app.services.workout_service import import_exercise_database
from app.core.bootstrap import create_app, get_bootstrap
from app.core.config import get_config, get_logging_config

# Configure logging
logging_config = get_logging_config()
logging.basicConfig(
    level=getattr(logging, logging_config.level),
    format=logging_config.format,
    handlers=[
        (
            logging.StreamHandler()
            if logging_config.enable_console
            else logging.NullHandler()
        ),
        (
            logging.FileHandler(logging_config.file_path)
            if logging_config.enable_file and logging_config.file_path
            else logging.NullHandler()
        ),
    ],
)
logger = logging.getLogger(__name__)

# Global app instance
app = None


def set_global_app(application):
    global app
    app = application


async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    set_global_app(app)
    logger.info("Starting Pulse Fitness application")
    try:
        # Create and bootstrap the application
        application = await create_app()
        logger.info("Application started successfully")
        yield None  # Yield None instead of the application
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        logger.info("Shutting down Pulse Fitness application")
        if app:
            bootstrap = get_bootstrap()
            await bootstrap._cleanup()


async def create_application():
    """Create the FastAPI application with lifespan management"""
    global app

    if app is None:
        async with lifespan(app) as application:
            app = application

    return app


# Create FastAPI app instance
app = FastAPI(
    title="Pulse Fitness API",
    description="A social fitness app with ML-powered workout recommendations",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["Exercises"])
app.include_router(workouts.router, prefix="/api/v1/workouts", tags=["Workouts"])
app.include_router(
    recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"]
)
app.include_router(social.router, prefix="/api/v1/social", tags=["Social"])
app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["Challenges"])
app.include_router(safety.router, prefix="/api/v1/safety", tags=["Safety"])
app.include_router(privacy.router, prefix="/api/v1/privacy", tags=["Privacy"])
app.include_router(community.router, prefix="/api/v1/community", tags=["Community"])
app.include_router(
    accountability.router, prefix="/api/v1/accountability", tags=["Accountability"]
)
app.include_router(
    subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Pulse Fitness API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "pulse-fitness-api"}


# For development server
if __name__ == "__main__":
    import uvicorn

    config = get_config()

    logger.info(
        f"Starting development server on {config.get('host', '0.0.0.0')}:{config.get('port', 8000)}"
    )

    uvicorn.run(
        "app.main:app",
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8000),
        reload=config.is_development(),
        log_level=logging_config.level.lower(),
        access_log=True,
    )
