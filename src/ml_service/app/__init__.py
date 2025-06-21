# backend/app/ml/__init__.py
"""
ML package initialization
"""

from app.UserSimilarityModel import UserSimilarityModel
from app.ExerciseRecommender import ExerciseRecommender

__all__ = ["UserSimilarityModel", "ExerciseRecommender"]