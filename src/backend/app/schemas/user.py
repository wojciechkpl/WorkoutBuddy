# backend/app/schemas/user.py
"""
Pydantic schemas for User operations
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    full_name: Optional[str] = None
    bio: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str

class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    id: int
    user_id: int
    total_workouts: int
    total_exercises: int
    total_duration: int
    average_workout_duration: float
    favorite_exercise_type: Optional[str] = None
    strength_score: float
    cardio_score: float
    flexibility_score: float
    last_workout_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True