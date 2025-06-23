"""
ML Service API endpoints
"""

import logging
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.exercise_recommender import ExerciseRecommender
from app.user_similarity_model import UserSimilarityModel

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pulse Fitness ML Service",
    description="ML-powered recommendations and analytics for Pulse Fitness",
    version=settings.SERVICE_VERSION,
)

# Initialize ML models
user_similarity_model = None
exercise_recommender = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global user_similarity_model, exercise_recommender

    try:
        # Initialize database connection
        init_db()

        # Initialize ML models
        user_similarity_model = UserSimilarityModel()
        exercise_recommender = ExerciseRecommender.load_or_initialize()

        logger.info("ML Service started successfully")
    except Exception as e:
        logger.error(f"Error starting ML Service: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


@app.post("/recommendations/exercises")
async def get_exercise_recommendations(
    user_id: int,
    n_recommendations: int = 10,
    workout_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get personalized exercise recommendations"""
    try:
        if exercise_recommender is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML service not ready",
            )

        # Get user from database
        from sqlalchemy import text

        result = db.execute(
            text("SELECT * FROM users WHERE id = :user_id"), {"user_id": user_id}
        )
        user_data = result.fetchone()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Create user object for ML model
        from app.models import User

        user = User(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            fitness_goal=getattr(user_data, "fitness_goal", None),
            experience_level=getattr(user_data, "experience_level", None),
            height_cm=getattr(user_data, "height_cm", None),
            weight_kg=getattr(user_data, "weight_kg", None),
        )

        recommendations = exercise_recommender.get_recommendations(
            user, db, n_recommendations, workout_type
        )

        return {"recommendations": recommendations}

    except Exception as e:
        logger.error(f"Error getting exercise recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations",
        )


@app.get("/similar-users/{user_id}")
async def get_similar_users(
    user_id: int, limit: int = 5, db: Session = Depends(get_db)
):
    """Find similar users"""
    try:
        if user_similarity_model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML service not ready",
            )

        # Get user from database
        from sqlalchemy import text

        result = db.execute(
            text("SELECT * FROM users WHERE id = :user_id"), {"user_id": user_id}
        )
        user_data = result.fetchone()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Create user object for ML model
        from app.models import User

        user = User(
            id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            fitness_goal=getattr(user_data, "fitness_goal", None),
            experience_level=getattr(user_data, "experience_level", None),
            height_cm=getattr(user_data, "height_cm", None),
            weight_kg=getattr(user_data, "weight_kg", None),
        )

        similar_users = user_similarity_model.find_similar_users(user, db, limit)

        return {"similar_users": similar_users}

    except Exception as e:
        logger.error(f"Error finding similar users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar users",
        )


@app.post("/models/train")
async def train_models():
    """Trigger model training"""
    try:
        # Train user similarity model
        if user_similarity_model:
            user_similarity_model.train()

        # Train exercise recommender
        if exercise_recommender:
            exercise_recommender._build_features()

        return {"message": "Models trained successfully"}

    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to train models",
        )
