# backend/app/schemas/workout.py
"""
Pydantic schemas for Workout operations
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models import WorkoutStatus
from app.schemas.exercise import ExerciseResponse

class WorkoutExerciseBase(BaseModel):
    """Base workout exercise schema"""
    exercise_id: int
    order: int
    sets: Optional[int] = None
    reps: Optional[str] = None
    weight: Optional[str] = None
    duration: Optional[int] = None
    distance: Optional[float] = None
    speed: Optional[float] = None
    incline: Optional[float] = None
    rest_time: Optional[int] = None
    notes: Optional[str] = None

class WorkoutExerciseCreate(WorkoutExerciseBase):
    """Schema for creating workout exercises"""
    pass

class WorkoutExerciseUpdate(BaseModel):
    """Schema for updating workout exercises"""
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None
    notes: Optional[str] = None

class WorkoutExerciseResponse(WorkoutExerciseBase):
    """Schema for workout exercise responses"""
    id: int
    workout_id: int
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None
    exercise: "ExerciseResponse"
    
    class Config:
        from_attributes = True

class WorkoutBase(BaseModel):
    """Base workout schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: datetime

class WorkoutCreate(WorkoutBase):
    """Schema for creating workouts"""
    exercises: List[WorkoutExerciseCreate] = []

class WorkoutUpdate(BaseModel):
    """Schema for updating workouts"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[WorkoutStatus] = None
    notes: Optional[str] = None

class WorkoutResponse(WorkoutBase):
    """Schema for workout responses"""
    id: int
    user_id: int
    status: WorkoutStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None
    calories_burned: Optional[float] = None
    total_volume: Optional[float] = None
    total_distance: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    exercises: List[WorkoutExerciseResponse] = []
    
    class Config:
        from_attributes = True

class WorkoutStats(BaseModel):
    """Schema for workout statistics"""
    total_workouts: int
    completed_workouts: int
    total_duration: int
    total_calories: float
    total_volume: float
    total_distance: float
    favorite_exercises: List[dict]
    muscle_group_distribution: dict