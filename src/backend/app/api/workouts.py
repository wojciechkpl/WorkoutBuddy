# backend/app/api/workouts.py
"""
Workout management endpoints
"""

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models import User, Workout, WorkoutExercise, WorkoutStatus
from app.schemas.workout import (
    WorkoutCreate,
    WorkoutExerciseUpdate,
    WorkoutResponse,
    WorkoutStats,
    WorkoutUpdate,
)
from app.services.workout_service import WorkoutService

router = APIRouter()


# Test data endpoints (no authentication required)
@router.get("/test/sample", response_model=list[WorkoutResponse])
async def get_test_workouts() -> list[dict]:
    """
    Get sample workout data for testing (no authentication required)
    """
    return [
        {
            "id": 1,
            "name": "Upper Body Strength",
            "description": "Focus on chest, back, and shoulders",
            "scheduled_date": datetime.now().date(),
            "status": "planned",
            "started_at": None,
            "completed_at": None,
            "total_duration": None,
            "calories_burned": None,
            "total_volume": None,
            "total_distance": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": 1,
            "exercises": [
                {
                    "id": 1,
                    "exercise_id": 1,
                    "workout_id": 1,
                    "sets": 3,
                    "reps": "10-12",
                    "weight": "135.0",
                    "duration": None,
                    "distance": None,
                    "speed": None,
                    "incline": None,
                    "rest_time": 90,
                    "actual_reps": None,
                    "actual_weight": None,
                    "notes": "Focus on form",
                    "order": 1,
                    "weight_unit": "LBS",
                    "distance_unit": None,
                    "exercise": {
                        "id": 1,
                        "name": "Bench Press",
                        "description": "Classic chest pressing exercise",
                        "primary_muscle": "chest",
                        "secondary_muscles": [],
                        "equipment": "barbell",
                        "exercise_type": "strength",
                        "difficulty": 3,
                        "instructions": "Lie on bench, lower bar to chest, press back up",
                        "tips": None,
                        "video_url": None,
                        "is_distance_based": False,
                        "is_time_based": False,
                        "mets": 4.0,
                    },
                },
                {
                    "id": 2,
                    "exercise_id": 3,
                    "workout_id": 1,
                    "sets": 3,
                    "reps": "8-10",
                    "weight": None,
                    "duration": None,
                    "distance": None,
                    "speed": None,
                    "incline": None,
                    "rest_time": 120,
                    "actual_reps": None,
                    "actual_weight": None,
                    "notes": "Full range of motion",
                    "order": 2,
                    "weight_unit": None,
                    "distance_unit": None,
                    "exercise": {
                        "id": 3,
                        "name": "Pull-ups",
                        "description": "Upper body pulling exercise",
                        "primary_muscle": "back",
                        "secondary_muscles": [],
                        "equipment": "other",
                        "exercise_type": "strength",
                        "difficulty": 3,
                        "instructions": "Hang from bar, pull body up until chin over bar, lower with control",
                        "tips": None,
                        "video_url": None,
                        "is_distance_based": False,
                        "is_time_based": False,
                        "mets": 4.0,
                    },
                },
            ],
        },
        {
            "id": 2,
            "name": "Lower Body Power",
            "description": "Build strength in legs and glutes",
            "scheduled_date": (datetime.now() + timedelta(days=1)).date(),
            "status": "planned",
            "started_at": None,
            "completed_at": None,
            "total_duration": None,
            "calories_burned": None,
            "total_volume": None,
            "total_distance": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": 1,
            "exercises": [
                {
                    "id": 3,
                    "exercise_id": 2,
                    "workout_id": 2,
                    "sets": 4,
                    "reps": "12-15",
                    "weight": None,
                    "duration": None,
                    "distance": None,
                    "speed": None,
                    "incline": None,
                    "rest_time": 60,
                    "actual_reps": None,
                    "actual_weight": None,
                    "notes": "Go deep, keep chest up",
                    "order": 1,
                    "weight_unit": None,
                    "distance_unit": None,
                    "exercise": {
                        "id": 2,
                        "name": "Squats",
                        "description": "Fundamental lower body exercise",
                        "primary_muscle": "legs",
                        "secondary_muscles": [],
                        "equipment": "bodyweight",
                        "exercise_type": "strength",
                        "difficulty": 3,
                        "instructions": "Stand with feet shoulder-width apart, lower hips back and down, return to standing",
                        "tips": None,
                        "video_url": None,
                        "is_distance_based": False,
                        "is_time_based": False,
                        "mets": 4.0,
                    },
                },
                {
                    "id": 4,
                    "exercise_id": 4,
                    "workout_id": 2,
                    "sets": 3,
                    "reps": "8-10",
                    "weight": "225.0",
                    "duration": None,
                    "distance": None,
                    "speed": None,
                    "incline": None,
                    "rest_time": 180,
                    "actual_reps": None,
                    "actual_weight": None,
                    "notes": "Keep back straight",
                    "order": 2,
                    "weight_unit": "LBS",
                    "distance_unit": None,
                    "exercise": {
                        "id": 4,
                        "name": "Deadlift",
                        "description": "Compound posterior chain exercise",
                        "primary_muscle": "back",
                        "secondary_muscles": [],
                        "equipment": "barbell",
                        "exercise_type": "strength",
                        "difficulty": 3,
                        "instructions": "Stand with feet hip-width, grip bar, lift by extending hips and knees",
                        "tips": None,
                        "video_url": None,
                        "is_distance_based": False,
                        "is_time_based": False,
                        "mets": 4.0,
                    },
                },
            ],
        },
    ]


@router.get("/test/stats", response_model=WorkoutStats)
async def get_test_workout_stats() -> WorkoutStats:
    """
    Get sample workout statistics for testing (no authentication required)
    """
    return WorkoutStats(
        total_workouts=12,
        completed_workouts=8,
        total_duration=390,  # 6 hours 30 minutes in minutes
        total_calories=2400,
        total_volume=15000.0,  # in user's preferred weight unit
        total_distance=125.5,  # in user's preferred distance unit
        favorite_exercises=[
            {"exercise_name": "Bench Press", "count": 15},
            {"exercise_name": "Squats", "count": 12},
            {"exercise_name": "Deadlift", "count": 10},
        ],
        muscle_group_distribution={
            "chest": 25,
            "back": 20,
            "legs": 30,
            "shoulders": 15,
            "arms": 10,
        },
    )


@router.get("/test/upcoming")
async def get_test_upcoming_workouts() -> list[WorkoutResponse]:
    """
    Get sample upcoming workouts for testing (no authentication required)
    """
    return [
        {
            "id": 3,
            "name": "Cardio Session",
            "description": "30 minutes of cardio",
            "scheduled_date": (datetime.now() + timedelta(days=2)).date(),
            "status": "planned",
            "started_at": None,
            "completed_at": None,
            "total_duration": None,
            "calories_burned": None,
            "total_volume": None,
            "total_distance": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": 1,
            "exercises": [],
        },
        {
            "id": 4,
            "name": "Full Body Circuit",
            "description": "High intensity circuit training",
            "scheduled_date": (datetime.now() + timedelta(days=3)).date(),
            "status": "planned",
            "started_at": None,
            "completed_at": None,
            "total_duration": None,
            "calories_burned": None,
            "total_volume": None,
            "total_distance": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "user_id": 1,
            "exercises": [],
        },
    ]


@router.post("/", response_model=WorkoutResponse)
async def create_workout(
    workout_data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
        status=WorkoutStatus.PLANNED,
    )

    db.add(workout)
    db.flush()  # Get workout ID without committing

    # Add exercises
    for exercise_data in workout_data.exercises:
        workout_exercise = WorkoutExercise(
            workout_id=workout.id, **exercise_data.dict()
        )
        db.add(workout_exercise)

    db.commit()
    db.refresh(workout)

    return workout


@router.get("/", response_model=list[WorkoutResponse])
async def get_workouts(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[WorkoutStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Workout]:
    """
    Get user's workouts with optional filters
    """
    query = db.query(Workout).filter(Workout.user_id == current_user.id)

    if start_date:
        query = query.filter(
            Workout.scheduled_date >= datetime.combine(start_date, datetime.min.time())
        )

    if end_date:
        query = query.filter(
            Workout.scheduled_date <= datetime.combine(end_date, datetime.max.time())
        )

    if status:
        query = query.filter(Workout.status == status)

    workouts = (
        query.order_by(Workout.scheduled_date.desc()).offset(skip).limit(limit).all()
    )

    return workouts


@router.get("/stats", response_model=WorkoutStats)
async def get_workout_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
) -> list[WorkoutResponse]:
    """
    Get upcoming scheduled workouts
    """
    end_date = datetime.utcnow() + timedelta(days=days)

    workouts = (
        db.query(Workout)
        .filter(
            Workout.user_id == current_user.id,
            Workout.scheduled_date >= datetime.utcnow(),
            Workout.scheduled_date <= end_date,
            Workout.status == WorkoutStatus.PLANNED,
        )
        .order_by(Workout.scheduled_date)
        .all()
    )

    return workouts


@router.get("/{workout_id}", response_model=WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workout:
    """
    Get a specific workout
    """
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
async def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workout:
    """
    Update a workout
    """
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Update fields
    update_data = workout_update.dict(exclude_unset=True)

    # Handle status changes
    if "status" in update_data:
        if (
            update_data["status"] == WorkoutStatus.IN_PROGRESS
            and not workout.started_at
        ):
            workout.started_at = datetime.utcnow()
        elif (
            update_data["status"] == WorkoutStatus.COMPLETED
            and not workout.completed_at
        ):
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
    db: Session = Depends(get_db),
) -> WorkoutResponse:
    """
    Start a workout session
    """
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout.status != WorkoutStatus.PLANNED:
        raise HTTPException(
            status_code=400, detail="Workout already started or completed"
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
    db: Session = Depends(get_db),
) -> WorkoutResponse:
    """
    Complete a workout session
    """
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    if workout.status == WorkoutStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Workout already completed")

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
    db: Session = Depends(get_db),
) -> dict:
    """
    Update exercise performance data during workout
    """
    # Verify workout ownership
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Find workout exercise
    workout_exercise = (
        db.query(WorkoutExercise)
        .filter(
            WorkoutExercise.workout_id == workout_id, WorkoutExercise.id == exercise_id
        )
        .first()
    )

    if not workout_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found in workout")

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
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete a workout
    """
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == current_user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()

    return {"message": "Workout deleted successfully"}
