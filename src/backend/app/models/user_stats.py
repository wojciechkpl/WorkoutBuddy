# backend/app/models/user_stats.py
"""
UserStats model for tracking user progress
"""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class WeightUnit(enum.Enum):
    KG = "KG"
    LBS = "LBS"


class DistanceUnit(enum.Enum):
    KM = "KM"
    MILES = "MILES"
    METERS = "METERS"


class UserStats(Base):
    """User statistics and personal records with unit support"""

    __tablename__ = "user_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)

    # Body measurements (stored in user's preferred units)
    weight = Column(Float)  # stored in weight_unit
    body_fat_percentage = Column(Float)
    muscle_mass = Column(Float)  # stored in weight_unit

    # Performance stats
    total_workouts = Column(Integer, default=0)
    total_weight_lifted = Column(Float, default=0)  # stored in weight_unit
    total_cardio_distance = Column(Float, default=0)  # stored in distance_unit
    total_calories_burned = Column(Float, default=0)

    # Unit tracking
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    distance_unit = Column(Enum(DistanceUnit), default=DistanceUnit.KM)

    # Personal records (JSON string)
    personal_records = Column(Text)  # {"bench_press": 100, "squat": 150, ...}

    # Relationships
    user = relationship("User", back_populates="user_stats")

    def get_weight_kg(self) -> float:
        """Get weight in kilograms (metric)"""
        if self.weight is None:
            return None

        if self.weight_unit == WeightUnit.KG:
            return self.weight
        elif self.weight_unit == WeightUnit.LBS:
            return self.weight * 0.45359237
        return self.weight

    def get_muscle_mass_kg(self) -> float:
        """Get muscle mass in kilograms (metric)"""
        if self.muscle_mass is None:
            return None

        if self.weight_unit == WeightUnit.KG:
            return self.muscle_mass
        elif self.weight_unit == WeightUnit.LBS:
            return self.muscle_mass * 0.45359237
        return self.muscle_mass

    def get_total_weight_lifted_kg(self) -> float:
        """Get total weight lifted in kilograms (metric)"""
        if self.total_weight_lifted is None:
            return 0.0

        if self.weight_unit == WeightUnit.KG:
            return self.total_weight_lifted
        elif self.weight_unit == WeightUnit.LBS:
            return self.total_weight_lifted * 0.45359237
        return self.total_weight_lifted

    def get_total_cardio_distance_km(self) -> float:
        """Get total cardio distance in kilometers (metric)"""
        if self.total_cardio_distance is None:
            return 0.0

        if self.distance_unit == DistanceUnit.KM:
            return self.total_cardio_distance
        elif self.distance_unit == DistanceUnit.MILES:
            return self.total_cardio_distance * 1.609344
        elif self.distance_unit == DistanceUnit.METERS:
            return self.total_cardio_distance / 1000.0
        return self.total_cardio_distance

    def set_weight_kg(self, weight_kg: float):
        """Set weight from kilograms"""
        if self.weight_unit == WeightUnit.KG:
            self.weight = weight_kg
        elif self.weight_unit == WeightUnit.LBS:
            self.weight = weight_kg * 2.20462262

    def set_muscle_mass_kg(self, muscle_mass_kg: float):
        """Set muscle mass from kilograms"""
        if self.weight_unit == WeightUnit.KG:
            self.muscle_mass = muscle_mass_kg
        elif self.weight_unit == WeightUnit.LBS:
            self.muscle_mass = muscle_mass_kg * 2.20462262

    def set_total_weight_lifted_kg(self, total_kg: float):
        """Set total weight lifted from kilograms"""
        if self.weight_unit == WeightUnit.KG:
            self.total_weight_lifted = total_kg
        elif self.weight_unit == WeightUnit.LBS:
            self.total_weight_lifted = total_kg * 2.20462262

    def set_total_cardio_distance_km(self, distance_km: float):
        """Set total cardio distance from kilometers"""
        if self.distance_unit == DistanceUnit.KM:
            self.total_cardio_distance = distance_km
        elif self.distance_unit == DistanceUnit.MILES:
            self.total_cardio_distance = distance_km / 1.609344
        elif self.distance_unit == DistanceUnit.METERS:
            self.total_cardio_distance = distance_km * 1000.0

    def __repr__(self):
        return f"<UserStats(user_id={self.user_id}, date='{self.date}')>"
