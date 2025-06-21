# backend/app/api/__init__.py
"""
API package initialization
"""

from app.api import auth, users, exercises, workouts, recommendations, social

__all__ = ["auth", "users", "exercises", "workouts", "recommendations", "social"]