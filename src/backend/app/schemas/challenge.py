# backend/app/schemas/challenge.py
"""
Challenge schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ChallengeType(str, Enum):
    """Types of challenges"""

    WORKOUT = "workout"
    NUTRITION = "nutrition"
    SOCIAL = "social"
    CUSTOM = "custom"


class ChallengeStatus(str, Enum):
    """Challenge status"""

    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChallengeCreate(BaseModel):
    """Schema for creating a challenge"""

    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    challenge_type: ChallengeType
    target_value: float = Field(..., gt=0)
    target_unit: str = Field(..., min_length=1, max_length=20)
    start_date: datetime
    end_date: datetime
    reward_points: Optional[int] = Field(None, ge=0)
    is_public: bool = False


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge"""

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    challenge_type: Optional[ChallengeType] = None
    target_value: Optional[float] = Field(None, gt=0)
    target_unit: Optional[str] = Field(None, min_length=1, max_length=20)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    reward_points: Optional[int] = Field(None, ge=0)
    is_public: Optional[bool] = None


class ChallengeResponse(BaseModel):
    """Schema for challenge response"""

    id: int
    title: str
    description: Optional[str]
    challenge_type: ChallengeType
    target_value: float
    target_unit: str
    start_date: datetime
    end_date: datetime
    reward_points: Optional[int]
    is_public: bool
    status: ChallengeStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
