# backend/app/main.py
"""
Pulse Fitness App - Main FastAPI Application
A social fitness application with ML-powered workout recommendations
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.database import engine, Base
from app.api import auth, users, exercises, workouts, recommendations, social
from app.config import settings
from app.services.workout_service import import_exercise_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting up Pulse Fitness App...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Import exercise database if CSV exists
    try:
        import_exercise_database()
        logger.info("Exercise database imported successfully")
    except Exception as e:
        logger.warning(f"Could not import exercise database: {e}")
    
    # Note: ML models are now handled by the separate ML service
    logger.info("ML service is separate - models will be loaded there")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pulse Fitness App...")

# Create FastAPI app instance
app = FastAPI(
    title="Pulse Fitness API",
    description="A social fitness app with ML-powered workout recommendations",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(social.router, prefix="/api/v1/social", tags=["Social"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Pulse Fitness API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "pulse-fitness-api"
    }