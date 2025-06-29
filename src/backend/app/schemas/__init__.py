# backend/app/schemas/__init__.py
"""
Schemas package initialization
"""

from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from app.schemas.workout import WorkoutCreate, WorkoutUpdate, WorkoutResponse
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseResponse
from app.schemas.recommendation import (
    WorkoutPlanRequest,
    ExerciseRecommendation,
    WorkoutPlanExercise,
    WorkoutPlanResponse,
    ProgressInsights,
)
from app.schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeType,
    ChallengeStatus,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "WorkoutCreate",
    "WorkoutUpdate",
    "WorkoutResponse",
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseResponse",
    "WorkoutPlanRequest",
    "ExerciseRecommendation",
    "WorkoutPlanExercise",
    "WorkoutPlanResponse",
    "ProgressInsights",
    "ChallengeCreate",
    "ChallengeUpdate",
    "ChallengeResponse",
    "ChallengeType",
    "ChallengeStatus",
]
