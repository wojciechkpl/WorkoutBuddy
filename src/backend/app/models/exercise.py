# backend/app/models/exercise.py
"""
Exercise model for exercise database
"""

from sqlalchemy import Column, Integer, String, Text, Enum, Float,Boolean
from sqlalchemy.orm import relationship
import enum
import json
from app.database import Base

class MuscleGroup(enum.Enum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    LEGS = "legs"
    GLUTES = "glutes"
    CORE = "core"
    CARDIO = "cardio"
    FULL_BODY = "full_body"

class Equipment(enum.Enum):
    NONE = "none"
    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    KETTLEBELL = "kettlebell"
    MACHINE = "machine"
    CABLE = "cable"
    BANDS = "bands"
    BODYWEIGHT = "bodyweight"
    CARDIO_MACHINE = "cardio_machine"
    OTHER = "other"

class ExerciseType(enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    PLYOMETRIC = "plyometric"

class Exercise(Base):
    """Exercise model with detailed information"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    primary_muscle = Column(Enum(MuscleGroup), nullable=False, index=True)
    secondary_muscles = Column(String)  # JSON string of muscle groups
    equipment = Column(Enum(Equipment), nullable=False, index=True)
    exercise_type = Column(Enum(ExerciseType), nullable=False)
    difficulty = Column(Integer)  # 1-5
    instructions = Column(Text)
    tips = Column(Text)
    video_url = Column(String)
    
    # For cardio exercises
    is_distance_based = Column(Boolean, default=False)
    is_time_based = Column(Boolean, default=False)
    
    # METs (Metabolic Equivalent of Task) for calorie calculation
    mets = Column(Float, default=4.0)
    
    # Relationships
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")

    @property
    def secondary_muscles_list(self):
        if self.secondary_muscles:
            try:
                return json.loads(self.secondary_muscles)
            except Exception:
                return []
        return []

    @secondary_muscles_list.setter
    def secondary_muscles_list(self, value):
        if isinstance(value, list):
            self.secondary_muscles = json.dumps(value)
        elif isinstance(value, str):
            self.secondary_muscles = value
        else:
            self.secondary_muscles = json.dumps([])

    def __repr__(self):
        return f"<Exercise(name='{self.name}', type='{self.exercise_type}')>"