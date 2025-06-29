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
from app.models.challenge import Challenge
from app.models.safety import UserReport, UserBlock
from app.models.privacy import PrivacySetting
from app.models.ml_feedback import RecommendationFeedback
from app.models.checkin import AccountabilityCheckin
from app.models.community import CommunityGroup, CommunityMembership
from .friend_invitation import FriendInvitation

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
    "Challenge",
    "UserReport",
    "UserBlock",
    "PrivacySetting",
    "RecommendationFeedback",
    "AccountabilityCheckin",
    "CommunityGroup",
    "CommunityMembership",
]
