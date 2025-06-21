"""
Data models for ML Service
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class User:
    """User model for ML service"""
    id: int
    username: str
    email: str
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    created_at: Optional[datetime] = None

@dataclass
class Workout:
    """Workout model for ML service"""
    id: int
    user_id: int
    name: str
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class WorkoutExercise:
    """Workout exercise model for ML service"""
    id: int
    workout_id: int
    exercise_id: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = None
    order_index: Optional[int] = None

@dataclass
class UserStats:
    """User statistics model for ML service"""
    user_id: int
    total_workouts: int = 0
    total_exercises: int = 0
    avg_workout_duration: float = 0.0
    favorite_muscle_groups: List[str] = None
    experience_level: str = "beginner"
    
    def __post_init__(self):
        if self.favorite_muscle_groups is None:
            self.favorite_muscle_groups = [] 