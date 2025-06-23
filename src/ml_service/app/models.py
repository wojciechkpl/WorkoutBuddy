"""
Data models for ML Service

All ML models use metric units internally for consistency and accuracy.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model for ML service with metric units"""

    id: int
    username: str
    email: str
    fitness_goal: Optional[str] = None
    experience_level: Optional[str] = None
    height_cm: Optional[float] = None  # Always in centimeters
    weight_kg: Optional[float] = None  # Always in kilograms
    unit_system: Optional[str] = "METRIC"  # User's preferred unit system
    height_unit: Optional[str] = "CM"  # User's height unit preference
    weight_unit: Optional[str] = "KG"  # User's weight unit preference
    created_at: Optional[datetime] = None

    def get_height_cm(self) -> Optional[float]:
        """Get height in centimeters (metric)"""
        return self.height_cm

    def get_weight_kg(self) -> Optional[float]:
        """Get weight in kilograms (metric)"""
        return self.weight_kg

    def set_height_cm(self, height_cm: float):
        """Set height in centimeters"""
        self.height_cm = height_cm

    def set_weight_kg(self, weight_kg: float):
        """Set weight in kilograms"""
        self.weight_kg = weight_kg


@dataclass
class Workout:
    """Workout model for ML service"""

    id: int
    user_id: int
    name: str
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class WorkoutExercise:
    """Workout exercise model for ML service with metric units"""

    id: int
    workout_id: int
    exercise_id: int
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None  # Always in kilograms
    duration_seconds: Optional[int] = None
    distance_meters: Optional[float] = None  # Always in meters
    speed_kmh: Optional[float] = None  # Always in km/h
    rest_seconds: Optional[int] = None
    order_index: Optional[int] = None
    weight_unit: Optional[str] = "KG"  # Original unit for reference
    distance_unit: Optional[str] = "METERS"  # Original unit for reference

    def get_weight_kg(self) -> Optional[float]:
        """Get weight in kilograms (metric)"""
        return self.weight_kg

    def get_distance_meters(self) -> Optional[float]:
        """Get distance in meters (metric)"""
        return self.distance_meters

    def get_speed_kmh(self) -> Optional[float]:
        """Get speed in kilometers per hour (metric)"""
        return self.speed_kmh

    def set_weight_kg(self, weight_kg: float):
        """Set weight in kilograms"""
        self.weight_kg = weight_kg

    def set_distance_meters(self, distance_meters: float):
        """Set distance in meters"""
        self.distance_meters = distance_meters

    def set_speed_kmh(self, speed_kmh: float):
        """Set speed in kilometers per hour"""
        self.speed_kmh = speed_kmh


@dataclass
class UserStats:
    """User statistics model for ML service with metric units"""

    user_id: int
    total_workouts: int = 0
    total_exercises: int = 0
    avg_workout_duration: float = 0.0
    favorite_muscle_groups: list[str] = None
    experience_level: str = "beginner"

    # Metric measurements
    weight_kg: Optional[float] = None  # Always in kilograms
    muscle_mass_kg: Optional[float] = None  # Always in kilograms
    total_weight_lifted_kg: float = 0.0  # Always in kilograms
    total_cardio_distance_km: float = 0.0  # Always in kilometers

    def __post_init__(self):
        if self.favorite_muscle_groups is None:
            self.favorite_muscle_groups = []

    def get_weight_kg(self) -> Optional[float]:
        """Get weight in kilograms (metric)"""
        return self.weight_kg

    def get_muscle_mass_kg(self) -> Optional[float]:
        """Get muscle mass in kilograms (metric)"""
        return self.muscle_mass_kg

    def get_total_weight_lifted_kg(self) -> float:
        """Get total weight lifted in kilograms (metric)"""
        return self.total_weight_lifted_kg

    def get_total_cardio_distance_km(self) -> float:
        """Get total cardio distance in kilometers (metric)"""
        return self.total_cardio_distance_km

    def set_weight_kg(self, weight_kg: float):
        """Set weight in kilograms"""
        self.weight_kg = weight_kg

    def set_muscle_mass_kg(self, muscle_mass_kg: float):
        """Set muscle mass in kilograms"""
        self.muscle_mass_kg = muscle_mass_kg

    def set_total_weight_lifted_kg(self, total_kg: float):
        """Set total weight lifted in kilograms"""
        self.total_weight_lifted_kg = total_kg

    def set_total_cardio_distance_km(self, distance_km: float):
        """Set total cardio distance in kilometers"""
        self.total_cardio_distance_km = distance_km
