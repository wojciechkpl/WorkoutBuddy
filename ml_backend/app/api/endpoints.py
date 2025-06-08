"""
WorkoutBuddy ML Backend API Endpoints

This module contains all the API routes for serving ML models and handling
workout-related predictions and recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add the app directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ..core.model import MLService
from ..core.schemas import *
from ..database import SessionLocal
from .. import crud

# Initialize router and ML service
router = APIRouter()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize ML service (will be shared across requests)
ml_service = MLService()


@router.get("/")
async def health_check():
    """Health check endpoint for ML prediction service"""
    return {
        "message": "WorkoutBuddy ML Backend API",
        "status": "active",
        "ml_service": "operational",
        "available_endpoints": [
            "/predict/workout-plan",
            "/predict/community-matches",
            "/predict/exercise-recommendations",
        ],
    }


@router.post("/workout-plan", response_model=WorkoutPlanResponse)
async def get_personalized_workout_plan(
    request: WorkoutPlanRequest, db: Session = Depends(get_db)
):
    """Generate personalized workout plan using ML models"""
    try:
        # Get user data
        user = crud.get_user(db, user_id=request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate workout plan using ML
        workout_plan = ml_service.generate_workout_plan(user, request)
        return workout_plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Workout plan generation failed: {str(e)}"
        )


@router.post("/community-matches", response_model=List[CommunityMatchResponse])
async def get_community_matches(
    request: CommunityMatchRequest, db: Session = Depends(get_db)
):
    """Find compatible workout buddies using ML similarity algorithms"""
    try:
        user = crud.get_user(db, user_id=request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        matches = ml_service.find_community_matches(user, request)
        return matches

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Community matching failed: {str(e)}"
        )


@router.post("/exercise-recommendations", response_model=List[ExerciseRecommendation])
async def get_exercise_recommendations(
    request: ExerciseRecommendationRequest, db: Session = Depends(get_db)
):
    """Get AI-powered exercise recommendations"""
    try:
        user = crud.get_user(db, user_id=request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        recommendations = ml_service.recommend_exercises(user, request)
        return recommendations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Exercise recommendations failed: {str(e)}"
        )


@router.get("/model-status")
async def get_model_status():
    """Get status of loaded ML models"""
    try:
        return {
            "ml_service_status": "operational",
            "models_loaded": list(ml_service.models.keys()),
            "preprocessor_ready": ml_service.preprocessor is not None,
            "formatter_ready": ml_service.formatter is not None,
            "last_updated": "2024-01-01T00:00:00Z",  # Would be actual timestamp
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Model status check failed: {str(e)}"
        )


@router.post("/batch-recommendations")
async def get_batch_recommendations(
    user_ids: List[int],
    request_params: ExerciseRecommendationRequest,
    db: Session = Depends(get_db),
):
    """Get exercise recommendations for multiple users (batch processing)"""
    try:
        batch_results = {}

        for user_id in user_ids:
            user = crud.get_user(db, user_id=user_id)
            if user:
                # Create individual request for each user
                individual_request = ExerciseRecommendationRequest(
                    user_id=user_id,
                    muscle_groups=request_params.muscle_groups,
                    equipment_available=request_params.equipment_available,
                    difficulty_level=request_params.difficulty_level,
                    max_recommendations=request_params.max_recommendations,
                )

                recommendations = ml_service.recommend_exercises(
                    user, individual_request
                )
                batch_results[user_id] = [rec.dict() for rec in recommendations]
            else:
                batch_results[user_id] = {"error": "User not found"}

        return {
            "batch_results": batch_results,
            "processed_users": len(batch_results),
            "successful_predictions": len(
                [r for r in batch_results.values() if "error" not in r]
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch processing failed: {str(e)}"
        )


# Include all the existing routes from main.py
# This will be populated by extracting routes from the original main.py
