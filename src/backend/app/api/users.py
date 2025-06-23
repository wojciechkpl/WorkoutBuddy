# backend/app/api/users.py
"""
Users API endpoints
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.user_stats import UserStats
from app.schemas.user import UserResponse, UserStatsResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


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
