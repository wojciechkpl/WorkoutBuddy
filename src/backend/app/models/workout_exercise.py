# backend/app/models/workout_exercise.py
"""
WorkoutExercise model for exercises within workouts
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class WorkoutExercise(Base):
    """Exercise instance within a workout"""
    __tablename__ = "workout_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Order in the workout
    
    # For strength exercises
    sets = Column(Integer)
    reps = Column(String)  # Can be a range like "8-12" or specific like "10,8,6"
    weight = Column(String)  # Can be multiple weights for different sets "60,65,70"
    
    # For cardio exercises
    duration = Column(Integer)  # in minutes
    distance = Column(Float)  # in km
    speed = Column(Float)  # in km/h
    incline = Column(Float)  # percentage
    
    # General
    rest_time = Column(Integer)  # rest time after this exercise in seconds
    actual_reps = Column(String)  # What was actually performed
    actual_weight = Column(String)  # What weight was actually used
    notes = Column(Text)
    
    # Relationships
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    
    def __repr__(self):
        return f"<WorkoutExercise(workout_id={self.workout_id}, exercise_id={self.exercise_id})>"
