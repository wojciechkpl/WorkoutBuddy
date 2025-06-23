# backend/app/schemas/exercise.py
"""
Pydantic schemas for Exercise operations
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models import Equipment, ExerciseType, MuscleGroup


class ExerciseBase(BaseModel):
    """Base exercise schema"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    primary_muscle: MuscleGroup
    secondary_muscles: Optional[list[str]] = None
    equipment: Equipment
    exercise_type: ExerciseType
    difficulty: int = Field(..., ge=1, le=5)
    instructions: Optional[str] = None
    tips: Optional[str] = None
    video_url: Optional[str] = None
    is_distance_based: bool = False
    is_time_based: bool = False
    mets: float = Field(4.0, ge=1.0, le=20.0)


class ExerciseCreate(ExerciseBase):
    """Schema for creating exercises"""

    pass


class ExerciseUpdate(BaseModel):
    """Schema for updating exercises"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    primary_muscle: Optional[MuscleGroup] = None
    secondary_muscles: Optional[list[str]] = None
    equipment: Optional[Equipment] = None
    exercise_type: Optional[ExerciseType] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    instructions: Optional[str] = None
    tips: Optional[str] = None
    video_url: Optional[str] = None
    is_distance_based: Optional[bool] = None
    is_time_based: Optional[bool] = None
    mets: Optional[float] = Field(None, ge=1.0, le=20.0)


class ExerciseResponse(ExerciseBase):
    """Schema for exercise responses"""

    id: int

    class Config:
        from_attributes = True


class ExerciseFilter(BaseModel):
    """Schema for exercise filtering"""

    muscle_groups: Optional[list[MuscleGroup]] = None
    equipment: Optional[list[Equipment]] = None
    exercise_types: Optional[list[ExerciseType]] = None
    difficulty_min: Optional[int] = Field(None, ge=1, le=5)
    difficulty_max: Optional[int] = Field(None, ge=1, le=5)
    search: Optional[str] = None
