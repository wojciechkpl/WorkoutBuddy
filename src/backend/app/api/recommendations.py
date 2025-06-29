# backend/app/api/recommendations.py
"""
Recommendations API - Updated for stateless ML models
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exercise, User
from app.services.data_service import DataService
from app.services.ml_client import ml_client
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/exercises/{user_id}")
async def get_exercise_recommendations(
    user_id: int, n_recommendations: int = 10, db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    """Get exercise recommendations for a user"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's interaction vector
        data_service = DataService(db)
        user_interactions = data_service.get_user_interaction_vector(user_id)

        # Get recommendations from ML service
        response = ml_client.get_exercise_recommendations(
            user_id=user_id,
            user_interactions=user_interactions,
            n_recommendations=n_recommendations,
        )

        # Get exercise details for recommendations
        recommendations = response.get("recommendations", [])
        exercise_ids = [rec["exercise_id"] for rec in recommendations]

        exercises = db.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
        exercise_map = {ex.id: ex for ex in exercises}

        # Format response
        result = []
        for rec in recommendations:
            exercise_id = rec["exercise_id"]
            if exercise_id in exercise_map:
                exercise = exercise_map[exercise_id]
                result.append(
                    {
                        "exercise_id": exercise_id,
                        "name": exercise.name,
                        "primary_muscle": (
                            exercise.primary_muscle.value
                            if exercise.primary_muscle
                            else None
                        ),
                        "equipment": (
                            exercise.equipment.value if exercise.equipment else None
                        ),
                        "difficulty": exercise.difficulty,
                        "predicted_rating": rec["predicted_rating"],
                    }
                )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting recommendations: {e!s}"
        )


@router.get("/similar-users/{user_id}")
async def get_similar_users(
    user_id: int, n_recommendations: int = 5, db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    """Get similar users based on user features"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's feature vector
        data_service = DataService(db)
        user_features = data_service.get_user_features(user_id)

        if not user_features:
            raise HTTPException(
                status_code=400, detail="Unable to extract user features"
            )

        # Get similar users from ML service
        response = ml_client.get_similar_users(
            user_features=user_features,
            user_id=user_id,
            n_recommendations=n_recommendations,
        )

        # Get user details for similar users
        similar_users = response.get("similar_users", [])
        similar_user_ids = [user_info["user_id"] for user_info in similar_users]

        users = db.query(User).filter(User.id.in_(similar_user_ids)).all()
        user_map = {user.id: user for user in users}

        # Format response
        result = []
        for user_info in similar_users:
            similar_user_id = user_info["user_id"]
            if similar_user_id in user_map:
                similar_user = user_map[similar_user_id]
                result.append(
                    {
                        "user_id": similar_user_id,
                        "username": similar_user.username,
                        "fitness_goal": (
                            similar_user.fitness_goal.value
                            if similar_user.fitness_goal
                            else None
                        ),
                        "experience_level": (
                            similar_user.experience_level.value
                            if similar_user.experience_level
                            else None
                        ),
                        "similarity_score": user_info["similarity_score"],
                    }
                )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting similar users: {e!s}"
        )


@router.post("/train-models")
async def train_ml_models(db: Session = Depends(get_db)) -> dict[str, str]:
    """Train ML models with current data"""
    try:
        # Get all data for training
        data_service = DataService(db)
        users_data, interactions_data, exercise_ids = data_service.get_all_data_for_ml()

        if not users_data or not exercise_ids:
            raise HTTPException(
                status_code=400, detail="Insufficient data for training"
            )

        # Train user similarity model
        ml_client.train_user_similarity_model(
            users_data=users_data,
            interactions_data=interactions_data,
            exercise_ids=exercise_ids,
        )

        # Train exercise recommender model
        ml_client.train_exercise_recommender(
            users_data=users_data,
            interactions_data=interactions_data,
            exercise_ids=exercise_ids,
        )

        return {"message": "ML models trained successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {e!s}")


@router.get("/ml-status")
async def get_ml_service_status() -> dict[str, Any]:
    """Get ML service status and model information"""
    try:
        status = ml_client.get_model_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ML status: {e!s}")


@router.post("/save-models")
async def save_ml_models() -> dict[str, str]:
    """Save trained ML models to disk"""
    try:
        ml_client.save_models()
        return {"message": "Models saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving models: {e!s}")


@router.post("/load-models")
async def load_ml_models() -> dict[str, str]:
    """Load trained ML models from disk"""
    try:
        ml_client.load_models()
        return {"message": "Models loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading models: {e!s}")


@router.get("/onboarding")
def get_onboarding_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Get personalized recommendations for onboarding"""
    return {
        "message": "Personalized recommendations",
        "recommendations": [
            "Complete your first workout",
            "Join a fitness community",
            "Set up accountability partnerships"
        ],
        "challenges": [
            {"id": 1, "name": "7-Day Starter Challenge", "description": "Complete a workout every day for a week."},
            {"id": 2, "name": "Community Joiner", "description": "Join your first community group."}
        ],
        "communities": [
            {"id": 1, "name": "Beginners United", "description": "A welcoming group for new members."},
            {"id": 2, "name": "Strength Seekers", "description": "For those focused on strength training."}
        ],
        "friends_suggestions": [
            {"id": 1, "username": "fit_jane", "mutual_friends": 3},
            {"id": 2, "username": "workout_mike", "mutual_friends": 2}
        ]
    }
