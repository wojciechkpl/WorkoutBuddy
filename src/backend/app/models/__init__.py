# backend/app/models/__init__.py
"""
Models package initialization
"""

from app.models.exercise import Equipment, Exercise, ExerciseType, MuscleGroup
from app.models.friendship import Friendship
from app.models.user import ExperienceLevel, FitnessGoal, User
from app.models.user_goal import UserGoal
from app.models.user_stats import UserStats
from app.models.workout import Workout, WorkoutStatus
from app.models.workout_exercise import WorkoutExercise

__all__ = [
    "User",
    "FitnessGoal",
    "ExperienceLevel",
    "Exercise",
    "MuscleGroup",
    "Equipment",
    "ExerciseType",
    "Workout",
    "WorkoutStatus",
    "WorkoutExercise",
    "UserStats",
    "Friendship",
    "UserGoal",
]
