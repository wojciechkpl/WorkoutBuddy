# backend/app/models/user.py
"""
User model for authentication and profile management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
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

class User(Base):
    """User model with fitness profile"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Fitness profile
    age = Column(Integer)
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    fitness_goal = Column(Enum(FitnessGoal))
    experience_level = Column(Enum(ExperienceLevel))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    user_stats = relationship("UserStats", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")
    sent_friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    received_friendships = relationship(
        "Friendship",
        foreign_keys="Friendship.friend_id",
        back_populates="friend",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"