# backend/app/models/__init__.py
"""
Models package initialization
"""

from app.models.user import User, FitnessGoal, ExperienceLevel
from app.models.exercise import Exercise, MuscleGroup, Equipment, ExerciseType
from app.models.workout import Workout, WorkoutStatus
from app.models.workout_exercise import WorkoutExercise
from app.models.user_stats import UserStats
from app.models.friendship import Friendship
from app.models.user_goal import UserGoal

__all__ = [
    "User", "FitnessGoal", "ExperienceLevel",
    "Exercise", "MuscleGroup", "Equipment", "ExerciseType",
    "Workout", "WorkoutStatus",
    "WorkoutExercise",
    "UserStats",
    "Friendship",
    "UserGoal"
]