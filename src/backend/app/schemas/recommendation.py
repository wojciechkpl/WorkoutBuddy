# backend/app/schemas/recommendation.py
"""
Pydantic schemas for Recommendations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class WorkoutPlanRequest(BaseModel):
    """Schema for workout plan requests"""
    available_time: int = Field(..., ge=15, le=180)  # minutes
    muscle_groups: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    workout_type: Optional[str] = None  # "strength", "cardio", "mixed"
    intensity: Optional[str] = Field("moderate", pattern="^(low|moderate|high)$")

class ExerciseRecommendation(BaseModel):
    """Schema for exercise recommendations"""
    exercise_id: int
    exercise_name: str
    exercise_type: str
    difficulty_level: int
    muscle_groups: Optional[str] = None
    equipment_required: bool
    score: float
    reason: str

class WorkoutPlanExercise(BaseModel):
    """Schema for exercises in workout plan"""
    exercise: ExerciseRecommendation
    sets: int
    reps: str
    rest_time: int
    notes: str

class WorkoutPlanResponse(BaseModel):
    """Schema for workout plan responses"""
    name: str
    description: str
    estimated_duration: int
    estimated_calories: float
    exercises: List[WorkoutPlanExercise]
    ai_insights: Optional[str] = None

class ProgressInsights(BaseModel):
    """Schema for progress insights"""
    strength_progress: Dict[str, float]
    muscle_balance: Dict[str, float]
    workout_consistency: float
    recommendations: List[str]
    achievement_badges: List[str]