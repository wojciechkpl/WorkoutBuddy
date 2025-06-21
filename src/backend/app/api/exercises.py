# backend/app/api/exercises.py
"""
Exercise management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import json

from app.database import get_db
from app.models import Exercise, User
from app.schemas.exercise import ExerciseResponse, ExerciseFilter, ExerciseCreate, ExerciseUpdate
from app.api.auth import get_current_user

router = APIRouter()

def exercise_to_response(exercise):
    data = {c.name: getattr(exercise, c.name) for c in exercise.__table__.columns}
    data["secondary_muscles"] = exercise.secondary_muscles_list
    return data

@router.get("/", response_model=List[ExerciseResponse])
async def get_exercises(
    muscle_group: Optional[str] = Query(None),
    equipment: Optional[str] = Query(None),
    exercise_type: Optional[str] = Query(None),
    difficulty_min: Optional[int] = Query(None, ge=1, le=5),
    difficulty_max: Optional[int] = Query(None, ge=1, le=5),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Get exercises with optional filters (public endpoint)
    """
    query = db.query(Exercise)
    
    # Apply filters
    if muscle_group:
        query = query.filter(Exercise.primary_muscle == muscle_group)
    
    if equipment:
        query = query.filter(Exercise.equipment == equipment)
    
    if exercise_type:
        query = query.filter(Exercise.exercise_type == exercise_type)
    
    if difficulty_min:
        query = query.filter(Exercise.difficulty >= difficulty_min)
    
    if difficulty_max:
        query = query.filter(Exercise.difficulty <= difficulty_max)
    
    if search:
        query = query.filter(
            or_(
                Exercise.name.ilike(f"%{search}%"),
                Exercise.description.ilike(f"%{search}%")
            )
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    exercises = query.offset(skip).limit(limit).all()
    
    return [exercise_to_response(e) for e in exercises]

@router.get("/muscle-groups", response_model=List[str])
async def get_muscle_groups() -> List[str]:
    """
    Get all available muscle groups (public endpoint)
    """
    from app.models import MuscleGroup
    return [mg.value for mg in MuscleGroup]

@router.get("/equipment", response_model=List[str])
async def get_equipment_types() -> List[str]:
    """
    Get all available equipment types (public endpoint)
    """
    from app.models import Equipment
    return [eq.value for eq in Equipment]

@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get a specific exercise by ID (public endpoint)
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    
    return exercise_to_response(exercise)

@router.post("/", response_model=ExerciseResponse, status_code=201)
async def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a new exercise (authenticated endpoint)
    """
    # Check if exercise with same name already exists
    existing_exercise = db.query(Exercise).filter(
        Exercise.name == exercise_data.name
    ).first()
    
    if existing_exercise:
        raise HTTPException(
            status_code=400,
            detail="Exercise with this name already exists"
        )
    
    exercise = Exercise(**exercise_data.dict(exclude={"secondary_muscles"}))
    if exercise_data.secondary_muscles:
        exercise.secondary_muscles = json.dumps(exercise_data.secondary_muscles)
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    
    return exercise_to_response(exercise)

@router.put("/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    exercise_id: int,
    exercise_update: ExerciseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Update an exercise (authenticated endpoint)
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    
    # Update fields
    update_data = exercise_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "secondary_muscles" and value is not None:
            setattr(exercise, "secondary_muscles", json.dumps(value))
        else:
            setattr(exercise, field, value)
    
    db.commit()
    db.refresh(exercise)
    
    return exercise_to_response(exercise)

@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an exercise (authenticated endpoint)
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    db.delete(exercise)
    db.commit()
    return Response(status_code=204)

@router.get("/{exercise_id}/history")
async def get_exercise_history(
    exercise_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get user's history with a specific exercise (authenticated endpoint)
    """
    from app.models import WorkoutExercise, Workout
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(WorkoutExercise).join(Workout).filter(
        and_(
            WorkoutExercise.exercise_id == exercise_id,
            Workout.user_id == current_user.id,
            Workout.completed_at >= cutoff_date,
            Workout.status == "completed"
        )
    ).order_by(Workout.completed_at.desc()).all()
    
    # Calculate personal records
    max_weight = 0
    max_reps = 0
    total_volume = 0
    
    history_data = []
    for record in history:
        if record.actual_weight:
            weights = [float(w) for w in record.actual_weight.split(",") if w]
            if weights:
                max_weight = max(max_weight, max(weights))
        
        if record.actual_reps:
            reps = [int(r) for r in record.actual_reps.split(",") if r]
            if reps:
                max_reps = max(max_reps, max(reps))
                total_volume += sum(reps) * (sum(weights) / len(weights) if weights else 0)
        
        history_data.append({
            "date": record.workout.completed_at,
            "sets": record.sets,
            "reps": record.actual_reps or record.reps,
            "weight": record.actual_weight or record.weight,
            "notes": record.notes
        })
    
    return {
        "exercise_id": exercise_id,
        "total_sessions": len(history),
        "personal_records": {
            "max_weight": max_weight,
            "max_reps": max_reps,
            "total_volume": total_volume
        },
        "history": history_data
    }
