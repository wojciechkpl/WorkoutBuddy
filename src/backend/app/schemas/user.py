# backend/app/schemas/user.py
"""
Pydantic schemas for User operations with unit support
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for user updates with unit preferences"""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    height: Optional[float] = Field(
        None, gt=0
    )  # Stored in user's preferred height_unit
    weight: Optional[float] = Field(
        None, gt=0
    )  # Stored in user's preferred weight_unit
    unit_system: Optional[str] = Field(None, regex="^(METRIC|IMPERIAL)$")
    height_unit: Optional[str] = Field(None, regex="^(CM|INCHES|FEET_INCHES)$")
    weight_unit: Optional[str] = Field(None, regex="^(KG|LBS)$")

    @validator("height")
    def validate_height(cls, v, values):
        """Validate height based on unit"""
        if v is not None:
            height_unit = values.get("height_unit", "CM")
            if height_unit == "CM" and (v < 50 or v > 300):
                raise ValueError("Height in cm must be between 50 and 300")
            elif height_unit == "INCHES" and (v < 20 or v > 120):
                raise ValueError("Height in inches must be between 20 and 120")
            elif height_unit == "FEET_INCHES" and (v < 24 or v > 144):
                raise ValueError("Height in total inches must be between 24 and 144")
        return v

    @validator("weight")
    def validate_weight(cls, v, values):
        """Validate weight based on unit"""
        if v is not None:
            weight_unit = values.get("weight_unit", "KG")
            if weight_unit == "KG" and (v < 20 or v > 300):
                raise ValueError("Weight in kg must be between 20 and 300")
            elif weight_unit == "LBS" and (v < 44 or v > 660):
                raise ValueError("Weight in lbs must be between 44 and 660")
        return v


class UserResponse(UserBase):
    """Schema for user responses with unit preferences"""

    id: int
    full_name: Optional[str] = None
    bio: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None  # In user's preferred height_unit
    weight: Optional[float] = None  # In user's preferred weight_unit
    unit_system: Optional[str] = None
    height_unit: Optional[str] = None
    weight_unit: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserMetricResponse(UserBase):
    """Schema for user responses with metric units (for algorithms)"""

    id: int
    full_name: Optional[str] = None
    bio: Optional[str] = None
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None  # Always in centimeters
    weight_kg: Optional[float] = None  # Always in kilograms
    unit_system: Optional[str] = None
    height_unit: Optional[str] = None
    weight_unit: Optional[str] = None
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
    """Schema for user statistics with unit support"""

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


class UserStatsMetricResponse(BaseModel):
    """Schema for user statistics with metric units (for algorithms)"""

    id: int
    user_id: int
    weight_kg: Optional[float] = None  # Always in kilograms
    muscle_mass_kg: Optional[float] = None  # Always in kilograms
    total_weight_lifted_kg: float = 0.0  # Always in kilograms
    total_cardio_distance_km: float = 0.0  # Always in kilometers
    total_calories_burned: float = 0.0
    weight_unit: Optional[str] = None  # Original unit for reference
    distance_unit: Optional[str] = None  # Original unit for reference

    class Config:
        from_attributes = True


class UnitPreferences(BaseModel):
    """Schema for user unit preferences"""

    unit_system: str = Field(..., regex="^(METRIC|IMPERIAL)$")
    height_unit: str = Field(..., regex="^(CM|INCHES|FEET_INCHES)$")
    weight_unit: str = Field(..., regex="^(KG|LBS)$")

    @validator("height_unit")
    def validate_height_unit(cls, v, values):
        """Validate height unit matches unit system"""
        unit_system = values.get("unit_system")
        if unit_system == "METRIC" and v not in ["CM"]:
            raise ValueError("Metric system should use CM for height")
        elif unit_system == "IMPERIAL" and v not in ["INCHES", "FEET_INCHES"]:
            raise ValueError(
                "Imperial system should use INCHES or FEET_INCHES for height"
            )
        return v

    @validator("weight_unit")
    def validate_weight_unit(cls, v, values):
        """Validate weight unit matches unit system"""
        unit_system = values.get("unit_system")
        if unit_system == "METRIC" and v != "KG":
            raise ValueError("Metric system should use KG for weight")
        elif unit_system == "IMPERIAL" and v != "LBS":
            raise ValueError("Imperial system should use LBS for weight")
        return v
