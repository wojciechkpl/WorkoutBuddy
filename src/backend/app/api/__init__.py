# backend/app/api/__init__.py
"""
API package initialization
"""

from app.api import auth, exercises, recommendations, social, users, workouts

__all__ = ["auth", "users", "exercises", "workouts", "recommendations", "social"]
