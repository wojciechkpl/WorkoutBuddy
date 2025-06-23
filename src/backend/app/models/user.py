# backend/app/models/user.py
"""
User model for authentication and profile management
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class FitnessGoal(enum.Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"
    ATHLETIC_PERFORMANCE = "athletic_performance"


class ExperienceLevel(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class UnitSystem(enum.Enum):
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"


class WeightUnit(enum.Enum):
    KG = "KG"
    LBS = "LBS"


class HeightUnit(enum.Enum):
    CM = "CM"
    INCHES = "INCHES"
    FEET_INCHES = "FEET_INCHES"


class User(Base):
    """User model with fitness profile and unit preferences"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Fitness profile (stored in user's preferred units)
    age = Column(Integer)
    height = Column(Float)  # stored in user's height_unit
    weight = Column(Float)  # stored in user's weight_unit
    fitness_goal = Column(Enum(FitnessGoal))
    experience_level = Column(Enum(ExperienceLevel))

    # Unit preferences
    unit_system = Column(Enum(UnitSystem), default=UnitSystem.METRIC)
    height_unit = Column(Enum(HeightUnit), default=HeightUnit.CM)
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workouts = relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    user_stats = relationship(
        "UserStats", back_populates="user", cascade="all, delete-orphan"
    )
    goals = relationship(
        "UserGoal", back_populates="user", cascade="all, delete-orphan"
    )
    sent_friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    received_friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.friend_id",
        back_populates="friend",
        cascade="all, delete-orphan",
    )

    def get_height_cm(self) -> float:
        """Get height in centimeters (metric)"""
        if self.height is None:
            return None

        if self.height_unit == HeightUnit.CM:
            return self.height
        elif self.height_unit == HeightUnit.INCHES:
            return self.height * 2.54
        elif self.height_unit == HeightUnit.FEET_INCHES:
            # Assuming height is stored as total inches (feet * 12 + inches)
            return self.height * 2.54
        return self.height

    def get_weight_kg(self) -> float:
        """Get weight in kilograms (metric)"""
        if self.weight is None:
            return None

        if self.weight_unit == WeightUnit.KG:
            return self.weight
        elif self.weight_unit == WeightUnit.LBS:
            return self.weight * 0.45359237
        return self.weight

    def set_height_cm(self, height_cm: float):
        """Set height from centimeters"""
        if self.height_unit == HeightUnit.CM:
            self.height = height_cm
        elif self.height_unit == HeightUnit.INCHES:
            self.height = height_cm / 2.54
        elif self.height_unit == HeightUnit.FEET_INCHES:
            self.height = height_cm / 2.54

    def set_weight_kg(self, weight_kg: float):
        """Set weight from kilograms"""
        if self.weight_unit == WeightUnit.KG:
            self.weight = weight_kg
        elif self.weight_unit == WeightUnit.LBS:
            self.weight = weight_kg * 2.20462262

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
