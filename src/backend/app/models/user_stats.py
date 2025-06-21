# backend/app/models/user_stats.py
"""
UserStats model for tracking user progress
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserStats(Base):
    """User statistics and personal records"""
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Body measurements
    weight = Column(Float)  # in kg
    body_fat_percentage = Column(Float)
    muscle_mass = Column(Float)  # in kg
    
    # Performance stats
    total_workouts = Column(Integer, default=0)
    total_weight_lifted = Column(Float, default=0)  # in kg
    total_cardio_distance = Column(Float, default=0)  # in km
    total_calories_burned = Column(Float, default=0)
    
    # Personal records (JSON string)
    personal_records = Column(Text)  # {"bench_press": 100, "squat": 150, ...}
    
    # Relationships
    user = relationship("User", back_populates="user_stats")
    
    def __repr__(self):
        return f"<UserStats(user_id={self.user_id}, date='{self.date}')>"