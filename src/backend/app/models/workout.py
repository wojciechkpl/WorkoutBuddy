# backend/app/models/workout.py
"""
Workout model for workout sessions
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class WorkoutStatus(enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class Workout(Base):
    """Workout session model"""
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(Enum(WorkoutStatus), default=WorkoutStatus.PLANNED)
    
    # Workout metrics
    total_duration = Column(Integer)  # in minutes
    calories_burned = Column(Float)
    total_volume = Column(Float)  # total weight moved for strength workouts
    total_distance = Column(Float)  # for cardio workouts in km
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workout(name='{self.name}', status='{self.status}')>"