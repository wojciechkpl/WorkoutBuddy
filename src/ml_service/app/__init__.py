# backend/app/ml/__init__.py
"""
ML package initialization
"""

from app.ai_services import (
    ChallengeResponse,
    CommunityMatchResponse,
    EncouragementResponse,
    ai_service,
)
from app.exercise_recommender import ExerciseRecommender
from app.user_similarity_model import UserSimilarityModel

__all__ = [
    "UserSimilarityModel",
    "ExerciseRecommender",
    "ai_service",
    "ChallengeResponse",
    "CommunityMatchResponse",
    "EncouragementResponse",
]
