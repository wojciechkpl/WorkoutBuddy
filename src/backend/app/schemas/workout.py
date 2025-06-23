# backend/app/schemas/workout.py
"""
Pydantic schemas for Workout operations with unit support
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.models import WorkoutStatus
from app.schemas.exercise import ExerciseResponse


class WorkoutExerciseBase(BaseModel):
    """Base workout exercise schema with unit support"""

    exercise_id: int
    order: int
    sets: Optional[int] = None
    reps: Optional[str] = None
    weight: Optional[str] = None  # Stored in user's preferred weight_unit
    duration: Optional[int] = None  # in minutes
    distance: Optional[float] = None  # Stored in user's preferred distance_unit
    speed: Optional[float] = None  # Stored in user's preferred distance_unit per hour
    incline: Optional[float] = None  # percentage
    rest_time: Optional[int] = None  # in seconds
    notes: Optional[str] = None
    weight_unit: Optional[str] = Field(None, regex="^(KG|LBS)$")
    distance_unit: Optional[str] = Field(None, regex="^(KM|MILES|METERS)$")

    @validator("weight")
    def validate_weight(cls, v, values):
        """Validate weight based on unit"""
        if v is not None:
            weight_unit = values.get("weight_unit", "KG")
            try:
                # Parse weight string (e.g., "60,65,70" or "100")
                weights = [float(w.strip()) for w in v.split(",")]
                for weight in weights:
                    if weight_unit == "KG" and (weight < 0 or weight > 1000):
                        raise ValueError("Weight in kg must be between 0 and 1000")
                    elif weight_unit == "LBS" and (weight < 0 or weight > 2200):
                        raise ValueError("Weight in lbs must be between 0 and 2200")
            except (ValueError, AttributeError):
                raise ValueError("Invalid weight format")
        return v

    @validator("distance")
    def validate_distance(cls, v, values):
        """Validate distance based on unit"""
        if v is not None:
            distance_unit = values.get("distance_unit", "METERS")
            if distance_unit == "KM" and (v < 0 or v > 1000):
                raise ValueError("Distance in km must be between 0 and 1000")
            elif distance_unit == "MILES" and (v < 0 or v > 620):
                raise ValueError("Distance in miles must be between 0 and 620")
            elif distance_unit == "METERS" and (v < 0 or v > 1000000):
                raise ValueError("Distance in meters must be between 0 and 1000000")
        return v


class WorkoutExerciseCreate(WorkoutExerciseBase):
    """Schema for creating workout exercises"""

    pass


class WorkoutExerciseUpdate(BaseModel):
    """Schema for updating workout exercises"""

    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None  # Stored in user's preferred weight_unit
    notes: Optional[str] = None


class WorkoutExerciseResponse(WorkoutExerciseBase):
    """Schema for workout exercise responses"""

    id: int
    workout_id: int
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None  # Stored in user's preferred weight_unit
    exercise: "ExerciseResponse"

    class Config:
        from_attributes = True


class WorkoutExerciseMetricResponse(BaseModel):
    """Schema for workout exercise responses with metric units (for algorithms)"""

    id: int
    workout_id: int
    exercise_id: int
    order: int
    sets: Optional[int] = None
    reps: Optional[str] = None
    weight_kg: Optional[str] = None  # Always in kilograms
    duration: Optional[int] = None  # in minutes
    distance_meters: Optional[float] = None  # Always in meters
    speed_kmh: Optional[float] = None  # Always in km/h
    incline: Optional[float] = None  # percentage
    rest_time: Optional[int] = None  # in seconds
    actual_reps: Optional[str] = None
    actual_weight: Optional[str] = None  # Always in kilograms
    notes: Optional[str] = None
    weight_unit: Optional[str] = None  # Original unit for reference
    distance_unit: Optional[str] = None  # Original unit for reference

    class Config:
        from_attributes = True


class WorkoutBase(BaseModel):
    """Base workout schema"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: datetime


class WorkoutCreate(WorkoutBase):
    """Schema for creating workouts"""

    exercises: list[WorkoutExerciseCreate] = []


class WorkoutUpdate(BaseModel):
    """Schema for updating workouts"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    status: Optional[WorkoutStatus] = None
    notes: Optional[str] = None


class WorkoutResponse(WorkoutBase):
    """Schema for workout responses with unit support"""

    id: int
    user_id: int
    status: WorkoutStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None  # in minutes
    calories_burned: Optional[float] = None
    total_volume: Optional[float] = None  # Stored in user's preferred weight_unit
    total_distance: Optional[float] = None  # Stored in user's preferred distance_unit
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    exercises: list[WorkoutExerciseResponse] = []

    class Config:
        from_attributes = True


class WorkoutMetricResponse(WorkoutBase):
    """Schema for workout responses with metric units (for algorithms)"""

    id: int
    user_id: int
    status: WorkoutStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None  # in minutes
    calories_burned: Optional[float] = None
    total_volume_kg: Optional[float] = None  # Always in kilograms
    total_distance_km: Optional[float] = None  # Always in kilometers
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    exercises: list[WorkoutExerciseMetricResponse] = []

    class Config:
        from_attributes = True


class WorkoutStats(BaseModel):
    """Schema for workout statistics with unit support"""

    total_workouts: int
    completed_workouts: int
    total_duration: int  # in minutes
    total_calories: float
    total_volume: float  # Stored in user's preferred weight_unit
    total_distance: float  # Stored in user's preferred distance_unit
    favorite_exercises: list[dict]
    muscle_group_distribution: dict


class WorkoutStatsMetric(BaseModel):
    """Schema for workout statistics with metric units (for algorithms)"""

    total_workouts: int
    completed_workouts: int
    total_duration: int  # in minutes
    total_calories: float
    total_volume_kg: float  # Always in kilograms
    total_distance_km: float  # Always in kilometers
    favorite_exercises: list[dict]
    muscle_group_distribution: dict
