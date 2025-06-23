# backend/app/models/workout_exercise.py
"""
WorkoutExercise model for exercises within workouts
"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class WeightUnit(enum.Enum):
    KG = "KG"
    LBS = "LBS"


class DistanceUnit(enum.Enum):
    KM = "KM"
    MILES = "MILES"
    METERS = "METERS"


class WorkoutExercise(Base):
    """Exercise instance within a workout with unit support"""

    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Order in the workout

    # For strength exercises (stored in user's preferred units)
    sets = Column(Integer)
    reps = Column(String)  # Can be a range like "8-12" or specific like "10,8,6"
    weight = Column(String)  # Can be multiple weights for different sets "60,65,70"

    # For cardio exercises (stored in user's preferred units)
    duration = Column(Integer)  # in minutes
    distance = Column(Float)  # stored in distance_unit
    speed = Column(Float)  # stored in distance_unit per hour
    incline = Column(Float)  # percentage

    # General
    rest_time = Column(Integer)  # rest time after this exercise in seconds
    actual_reps = Column(String)  # What was actually performed
    actual_weight = Column(String)  # What weight was actually used
    notes = Column(Text)

    # Unit tracking
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    distance_unit = Column(Enum(DistanceUnit), default=DistanceUnit.METERS)

    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")

    def get_weight_kg(self) -> str:
        """Get weight in kilograms (metric)"""
        if not self.weight:
            return self.weight

        try:
            # Parse weight string (e.g., "60,65,70" or "100")
            weights = [float(w.strip()) for w in self.weight.split(",")]

            if self.weight_unit == WeightUnit.KG:
                return self.weight
            elif self.weight_unit == WeightUnit.LBS:
                converted_weights = [w * 0.45359237 for w in weights]
                return ",".join([f"{w:.2f}" for w in converted_weights])
        except (ValueError, AttributeError):
            pass

        return self.weight

    def get_distance_meters(self) -> float:
        """Get distance in meters (metric)"""
        if self.distance is None:
            return None

        if self.distance_unit == DistanceUnit.METERS:
            return self.distance
        elif self.distance_unit == DistanceUnit.KM:
            return self.distance * 1000.0
        elif self.distance_unit == DistanceUnit.MILES:
            return self.distance * 1609.344
        return self.distance

    def get_speed_kmh(self) -> float:
        """Get speed in kilometers per hour (metric)"""
        if self.speed is None:
            return None

        if self.distance_unit == DistanceUnit.KM:
            return self.speed
        elif self.distance_unit == DistanceUnit.MILES:
            return self.speed * 1.609344
        elif self.distance_unit == DistanceUnit.METERS:
            return self.speed * 3.6  # m/s to km/h
        return self.speed

    def set_weight_kg(self, weight_kg: str):
        """Set weight from kilograms"""
        if not weight_kg:
            self.weight = weight_kg
            return

        try:
            weights = [float(w.strip()) for w in weight_kg.split(",")]

            if self.weight_unit == WeightUnit.KG:
                self.weight = weight_kg
            elif self.weight_unit == WeightUnit.LBS:
                converted_weights = [w * 2.20462262 for w in weights]
                self.weight = ",".join([f"{w:.2f}" for w in converted_weights])
        except (ValueError, AttributeError):
            self.weight = weight_kg

    def set_distance_meters(self, distance_meters: float):
        """Set distance from meters"""
        if self.distance_unit == DistanceUnit.METERS:
            self.distance = distance_meters
        elif self.distance_unit == DistanceUnit.KM:
            self.distance = distance_meters / 1000.0
        elif self.distance_unit == DistanceUnit.MILES:
            self.distance = distance_meters / 1609.344

    def set_speed_kmh(self, speed_kmh: float):
        """Set speed from kilometers per hour"""
        if self.distance_unit == DistanceUnit.KM:
            self.speed = speed_kmh
        elif self.distance_unit == DistanceUnit.MILES:
            self.speed = speed_kmh / 1.609344
        elif self.distance_unit == DistanceUnit.METERS:
            self.speed = speed_kmh / 3.6  # km/h to m/s

    def __repr__(self):
        return f"<WorkoutExercise(workout_id={self.workout_id}, exercise_id={self.exercise_id})>"
