# backend/app/api/workouts.py
"""
Workout management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
import logging

from app.database import get_db
from app.models import User, Workout, WorkoutExercise, Exercise, WorkoutStatus
from app.schemas.workout import (
    WorkoutCreate, WorkoutUpdate, WorkoutResponse,
    WorkoutExerciseUpdate, WorkoutStats
)
from app.api.auth import get_current_user
from app.services.workout_service import WorkoutService

router = APIRouter()

@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Workout:
    """
    Create a new workout with exercises
    """
    # Create workout
    workout = Workout(
        user_id=current_user.id,
        name=workout_data.name,
        description=workout_data.description,
        scheduled_date=workout_data.scheduled_date,
        status=WorkoutStatus.PLANNED
    )
    
    db.add(workout)
    db.flush()  # Get workout ID without committing
    
    # Add exercises
    for exercise_data in workout_data.exercises:
        workout_exercise = WorkoutExercise(
            workout_id=workout.id,
            **exercise_data.dict()
        )
        db.add(workout_exercise)
    
    db.commit()
    db.refresh(workout)
    
    return workout

@router.get("/", response_model=List[WorkoutResponse])
async def get_workouts(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[WorkoutStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Workout]:
    """
    Get user's workouts with optional filters
    """
    query = db.query(Workout).filter(Workout.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Workout.scheduled_date >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(Workout.scheduled_date <= datetime.combine(end_date, datetime.max.time()))
    
    if status:
        query = query.filter(Workout.status == status)
    
    workouts = query.order_by(Workout.scheduled_date.desc()).offset(skip).limit(limit).all()
    
    return workouts

@router.get("/stats", response_model=WorkoutStats)
async def get_workout_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkoutStats:
    """
    Get workout statistics for the user
    """
    service = WorkoutService(db)
    return service.get_user_stats(current_user, days)

@router.get("/upcoming")
async def get_upcoming_workouts(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[WorkoutResponse]:
    """
    Get upcoming scheduled workouts
    """
    end_date = datetime.utcnow() + timedelta(days=days)
    
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id,
        Workout.scheduled_date >= datetime.utcnow(),
        Workout.scheduled_date <= end_date,
        Workout.status == WorkoutStatus.PLANNED
    ).order_by(Workout.scheduled_date).all()
    
    return workouts

@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Workout:
    """
    Get a specific workout
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    return workout

@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Workout:
    """
    Update a workout
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    # Update fields
    update_data = workout_update.dict(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        if update_data["status"] == WorkoutStatus.IN_PROGRESS and not workout.started_at:
            workout.started_at = datetime.utcnow()
        elif update_data["status"] == WorkoutStatus.COMPLETED and not workout.completed_at:
            workout.completed_at = datetime.utcnow()
            # Calculate workout metrics
            service = WorkoutService(db)
            service.calculate_workout_metrics(workout)
    
    for field, value in update_data.items():
        setattr(workout, field, value)
    
    db.commit()
    db.refresh(workout)
    
    return workout

@router.post("/{workout_id}/start")
async def start_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkoutResponse:
    """
    Start a workout session
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    if workout.status != WorkoutStatus.PLANNED:
        raise HTTPException(
            status_code=400,
            detail="Workout already started or completed"
        )
    
    workout.status = WorkoutStatus.IN_PROGRESS
    workout.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(workout)
    
    return workout

@router.post("/{workout_id}/complete")
async def complete_workout(
    workout_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkoutResponse:
    """
    Complete a workout session
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    if workout.status == WorkoutStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Workout already completed"
        )
    
    workout.status = WorkoutStatus.COMPLETED
    workout.completed_at = datetime.utcnow()
    
    if notes:
        workout.notes = notes
    
    # Calculate workout metrics
    service = WorkoutService(db)
    service.calculate_workout_metrics(workout)
    
    # Update user stats
    service.update_user_stats(current_user, workout)
    
    db.commit()
    db.refresh(workout)
    
    return workout

@router.put("/{workout_id}/exercises/{exercise_id}")
async def update_workout_exercise(
    workout_id: int,
    exercise_id: int,
    exercise_update: WorkoutExerciseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Update exercise performance data during workout
    """
    # Verify workout ownership
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    # Find workout exercise
    workout_exercise = db.query(WorkoutExercise).filter(
        WorkoutExercise.workout_id == workout_id,
        WorkoutExercise.id == exercise_id
    ).first()
    
    if not workout_exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found in workout"
        )
    
    # Update fields
    update_data = exercise_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout_exercise, field, value)
    
    db.commit()
    
    return {"message": "Exercise updated successfully"}

@router.delete("/{workout_id}")
async def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a workout
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()
    
    if not workout:
        raise HTTPException(
            status_code=404,
            detail="Workout not found"
        )
    
    db.delete(workout)
    db.commit()
    
    return {"message": "Workout deleted successfully"}