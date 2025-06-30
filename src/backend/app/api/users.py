# backend/app/api/users.py
"""
Users API endpoints
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.user_stats import UserStats
from app.schemas.user import UserResponse, UserStatsResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


# Test data endpoints (no authentication required)
@router.get("/test/profile", response_model=UserResponse)
async def get_test_user_profile():
    """
    Get sample user profile for testing (no authentication required)
    """
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "bio": "Fitness enthusiast working on strength and endurance",
        "date_of_birth": datetime(1990, 5, 15).date(),
        "gender": "male",
        "height": 175.0,
        "weight": 75.0,
        "height_unit": "cm",
        "weight_unit": "kg",
        "fitness_goal": "muscle_gain",
        "experience_level": "intermediate",
        "unit_system": "metric",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now() - timedelta(days=30),
        "updated_at": datetime.now(),
    }


@router.get("/test/stats", response_model=UserStatsResponse)
async def get_test_user_stats():
    """
    Get sample user statistics for testing (no authentication required)
    """
    return {
        "id": 1,
        "user_id": 1,
        "total_workouts": 45,
        "total_exercises": 12,
        "total_duration": 1935,  # 32 hours 15 minutes in minutes
        "average_workout_duration": 43.0,
        "favorite_exercise_type": "strength",
        "strength_score": 75.5,
        "cardio_score": 60.0,
        "flexibility_score": 45.0,
        "last_workout_date": datetime.now() - timedelta(days=1),
    }


@router.get("/test/recommendations")
async def get_test_recommendations():
    """
    Get sample workout recommendations for testing (no authentication required)
    """
    return {
        "recommendations": [
            {
                "id": 1,
                "name": "Upper Body Strength",
                "description": "Based on your recent chest focus",
                "difficulty": "intermediate",
                "estimated_duration": 45,
                "target_muscles": ["chest", "back", "shoulders"],
                "equipment_needed": ["barbell", "dumbbells"],
                "confidence_score": 0.85,
            },
            {
                "id": 2,
                "name": "Lower Body Power",
                "description": "Great for building leg strength",
                "difficulty": "intermediate",
                "estimated_duration": 50,
                "target_muscles": ["legs", "glutes"],
                "equipment_needed": ["barbell", "squat rack"],
                "confidence_score": 0.78,
            },
            {
                "id": 3,
                "name": "Cardio HIIT",
                "description": "High intensity interval training",
                "difficulty": "advanced",
                "estimated_duration": 30,
                "target_muscles": ["full_body"],
                "equipment_needed": ["bodyweight"],
                "confidence_score": 0.72,
            },
        ],
        "reasoning": "Based on your recent workout patterns and fitness goals",
    }


@router.get("/test/community")
async def get_test_community_data():
    """
    Get sample community data for testing (no authentication required)
    """
    return {
        "friends": [
            {
                "id": 2,
                "username": "fitness_friend",
                "full_name": "John Doe",
                "bio": "Loves running and strength training",
                "is_online": True,
                "last_workout": "2 hours ago",
                "workout_streak": 12,
            },
            {
                "id": 3,
                "username": "gym_buddy",
                "full_name": "Jane Smith",
                "bio": "Yoga instructor and fitness coach",
                "is_online": False,
                "last_workout": "1 day ago",
                "workout_streak": 8,
            },
        ],
        "challenges": [
            {
                "id": 1,
                "name": "30-Day Push-up Challenge",
                "description": "Complete 100 push-ups daily for 30 days",
                "participants": 45,
                "days_remaining": 15,
                "your_progress": 0.5,
            },
            {
                "id": 2,
                "name": "Weekly Mile Challenge",
                "description": "Run 10 miles this week",
                "participants": 23,
                "days_remaining": 3,
                "your_progress": 0.7,
            },
        ],
        "recent_activity": [
            {
                "user": "fitness_friend",
                "action": "completed a workout",
                "workout_name": "Upper Body Strength",
                "time_ago": "2 hours ago",
            },
            {
                "user": "gym_buddy",
                "action": "achieved a new PR",
                "workout_name": "Bench Press - 185 lbs",
                "time_ago": "1 day ago",
            },
        ],
    }


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile"""
    # Update only provided fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.fitness_goal is not None:
        current_user.fitness_goal = user_update.fitness_goal
    if user_update.experience_level is not None:
        current_user.experience_level = user_update.experience_level

    db.commit()
    db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.username}")
    return current_user


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's fitness statistics"""
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()

    if not stats:
        # Create default stats if none exist
        stats = UserStats(user_id=current_user.id)
        db.add(stats)
        db.commit()
        db.refresh(stats)

    return stats


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user by ID (public profile)"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.get("/search/{username}", response_model=list[UserResponse])
async def search_users(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search users by username"""
    users = (
        db.query(User)
        .filter(User.username.ilike(f"%{username}%"), User.id != current_user.id)
        .limit(10)
        .all()
    )

    return users


@router.post("/fitness-assessment")
def complete_fitness_assessment(
    assessment_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Complete fitness assessment for onboarding"""
    return {"message": "Fitness assessment completed"}


@router.post("/privacy-setup")
def privacy_setup(
    privacy_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Set privacy preferences for onboarding"""
    return {"message": "Privacy preferences set"}


@router.post("/goals")
def set_user_goals(
    goals_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stub: Set user goals for onboarding"""
    return {"message": "User goals set"}
