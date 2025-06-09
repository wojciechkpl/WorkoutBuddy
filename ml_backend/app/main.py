from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import json
import os
import asyncio
from datetime import datetime, timedelta

from .core import models, schemas
from . import crud, database
from .config import backend_config
from .ai_services import ai_service
from .analytics import analytics_service, CohortMetrics, EventMetrics
from .ab_testing import ab_testing_service, ExperimentResult

# Import new ML components
from .api.endpoints import router as ml_router
from .core.model import MLService
from .core.schemas import *

# Configure logging
logging.basicConfig(level=getattr(logging, backend_config.logging.level))
logger = logging.getLogger(__name__)

# Initialize ML service
ml_service = MLService()

# Initialize FastAPI
app = FastAPI(
    title="WorkoutBuddy ML Backend API v3.0",
    description="AI-Powered Fitness Platform with Machine Learning Models",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Production-ready CORS configuration
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://workoutbuddy-frontend.railway.app",
]

# Add Railway environment origins
if os.getenv("RAILWAY_ENVIRONMENT"):
    railway_domain = os.getenv("RAILWAY_STATIC_URL")
    if railway_domain:
        allowed_origins.append(f"https://{railway_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Include ML API routes
app.include_router(ml_router, prefix="/predict", tags=["ML Predictions"])


# Dependency injection
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoints
@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "message": "WorkoutBuddy ML Backend API v3.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production"
        if os.getenv("RAILWAY_ENVIRONMENT")
        else "development",
        "features": {
            "ml_workout_plans": True,
            "community_matching": True,
            "exercise_recommendations": True,
            "ai_powered_challenges": ai_service.enabled,
            "real_time_analytics": analytics_service.enabled,
            "ab_testing": True,
        },
        "ml_service_status": "operational",
        "ai_status": "enabled" if ai_service.enabled else "fallback_mode",
        "analytics_status": "enabled" if analytics_service.enabled else "local_only",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    try:
        db.execute("SELECT 1")
        total_users = db.query(models.User).count()
        active_experiments = len(ab_testing_service.get_active_experiments())

        return {
            "status": "healthy",
            "database": "connected",
            "users": total_users,
            "active_experiments": active_experiments,
            "ml_service": "operational",
            "ai_service": "operational" if ai_service.enabled else "fallback",
            "analytics": "operational" if analytics_service.enabled else "local",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


# User Management with Analytics
@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register new user with analytics tracking"""
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = crud.create_user(db=db, user=user)

        # Track user registration
        analytics_service.track_user_registration(new_user)

        logger.info(f"New user registered: {new_user.id}")
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Goal Management
@app.post("/goals", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, user_id: int, db: Session = Depends(get_db)):
    """Create goal with analytics tracking"""
    new_goal = crud.create_goal(db=db, goal=goal, user_id=user_id)

    # Track goal creation
    analytics_service.track_event(
        str(user_id),
        "goal_created",
        {
            "goal_type": goal.goal_type if hasattr(goal, "goal_type") else "general",
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "description": goal.description[:100] if goal.description else None,
        },
    )

    return new_goal


@app.get("/goals/{goal_id}")
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """Get goal details"""
    goal = crud.get_goal(db, goal_id=goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


# Legacy AI-Powered Challenge Generation (kept for compatibility)
@app.post("/challenges/generate")
async def generate_challenge(
    user_id: str,
    goal_type: str = "cardio",
    preferences: Dict[str, Any] = None,
    db: Session = Depends(get_db),
):
    """Generate AI-powered personalized daily challenges"""
    try:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check A/B test assignment for AI challenges
        use_ai = ab_testing_service.should_use_ai_challenges(user_id)

        if use_ai and ai_service.enabled:
            # Generate AI-powered challenge
            user_history = {
                "recent_completion_rate": getattr(
                    user, "community_engagement_score", 0
                ),
                "recent_challenges": [],
            }

            challenge_response = await ai_service.generate_personalized_challenge(
                user, user_history, preferences
            )

            # Track AI challenge generation
            analytics_service.track_event(
                user_id,
                "ai_challenge_generated",
                {
                    "goal_type": goal_type,
                    "ai_generated": True,
                    "experiment_group": "ai_challenges",
                },
            )

            return challenge_response

        else:
            # Fallback to rule-based challenges
            fallback_challenge = {
                "challenge_text": f"Complete a 20-minute {goal_type} workout today!",
                "difficulty": "moderate",
                "estimated_duration": 20,
                "tips": ["Start with a 5-minute warm-up", "Stay hydrated"],
                "ai_generated": False,
                "experiment_group": "control_challenges",
            }

            # Track fallback challenge generation
            analytics_service.track_event(
                user_id,
                "challenge_generated",
                {
                    "goal_type": goal_type,
                    "ai_generated": False,
                    "experiment_group": "control_challenges",
                },
            )

            return fallback_challenge

    except Exception as e:
        logger.error(f"Challenge generation failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Challenge generation failed")


# Rest of the endpoints remain the same...
# (I'll keep the existing endpoints for backward compatibility)


# Analytics endpoints
@app.get("/analytics/cohorts")
def get_cohort_analysis(db: Session = Depends(get_db)) -> List[Dict]:
    """Get user cohort analysis for retention insights"""
    try:
        cohorts = analytics_service.get_cohort_analysis(db)
        return [cohort.dict() for cohort in cohorts]
    except Exception as e:
        logger.error(f"Cohort analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Cohort analysis failed")


@app.get("/analytics/events")
def get_event_metrics(days: int = 7, db: Session = Depends(get_db)) -> List[Dict]:
    """Get event metrics for the specified time period"""
    try:
        events = analytics_service.get_event_metrics(db, days)
        return [event.dict() for event in events]
    except Exception as e:
        logger.error(f"Event metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Event metrics failed")


# A/B Testing endpoints
@app.get("/experiments")
def get_active_experiments():
    """Get list of active A/B testing experiments"""
    return {
        "active_experiments": ab_testing_service.get_active_experiments(),
        "total_experiments": len(ab_testing_service.get_active_experiments()),
    }


@app.get("/experiments/{experiment_id}/results")
def get_experiment_results(experiment_id: str, db: Session = Depends(get_db)):
    """Get A/B testing experiment results"""
    try:
        results = ab_testing_service.get_experiment_results(experiment_id, db)
        return results.dict() if results else {"error": "Experiment not found"}
    except Exception as e:
        logger.error(f"Failed to get experiment results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get experiment results")


# Exception handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error tracking"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("WorkoutBuddy ML Backend API v3.0 starting up...")
    logger.info(f"Database URL: {backend_config.database.url}")
    logger.info(f"AI Service enabled: {ai_service.enabled}")
    logger.info(f"Analytics enabled: {analytics_service.enabled}")
    logger.info(f"ML Service initialized: {ml_service is not None}")
    logger.info("Startup complete!")
