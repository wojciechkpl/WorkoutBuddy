# backend/app/api/recommendations.py
"""
Recommendations API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.schemas.recommendation import ExerciseRecommendation, WorkoutPlanRequest, WorkoutPlanResponse
from app.api.auth import get_current_user
from app.services.recommendation_engine import RecommendationEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/exercises", response_model=List[ExerciseRecommendation])
async def get_exercise_recommendations(
    n_recommendations: int = 10,
    workout_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized exercise recommendations"""
    try:
        engine = RecommendationEngine()
        recommendations = engine.get_exercise_recommendations(
            current_user, db, n_recommendations, workout_type
        )
        
        logger.info(f"Generated {len(recommendations)} exercise recommendations for user {current_user.username}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating exercise recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )

@router.post("/workout-plan", response_model=WorkoutPlanResponse)
async def generate_workout_plan(
    request: WorkoutPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized workout plan"""
    try:
        engine = RecommendationEngine()
        workout_plan = engine.generate_workout_plan(
            current_user, db, request
        )
        
        logger.info(f"Generated workout plan for user {current_user.username}")
        return workout_plan
        
    except Exception as e:
        logger.error(f"Error generating workout plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate workout plan"
        )

@router.get("/similar-users")
async def get_similar_users(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find similar users based on fitness goals and workout patterns"""
    try:
        from app.ml.UserSimilarityModel import UserSimilarityModel
        
        model = UserSimilarityModel()
        similar_users = model.find_similar_users(current_user, db, n_similar=limit)
        
        # Get user details for similar users
        user_details = []
        for user_id, similarity_score in similar_users:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user_details.append({
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "fitness_goal": user.fitness_goal,
                    "experience_level": user.experience_level,
                    "similarity_score": similarity_score
                })
        
        logger.info(f"Found {len(user_details)} similar users for {current_user.username}")
        return {
            "similar_users": user_details,
            "total_found": len(user_details)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar users"
        )

@router.get("/progress-insights")
async def get_progress_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized progress insights and recommendations"""
    try:
        engine = RecommendationEngine()
        insights = engine.get_progress_insights(current_user, db)
        
        logger.info(f"Generated progress insights for user {current_user.username}")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating progress insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate progress insights"
        )