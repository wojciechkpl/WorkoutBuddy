from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    goals = relationship("Goal", back_populates="owner")
    gender = Column(String, nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    height_ft = Column(Integer, nullable=False)
    height_in = Column(Integer, nullable=False)
    weight_lb = Column(Integer, nullable=False)
    height_cm = Column(Integer, nullable=False)
    weight_kg = Column(Integer, nullable=False)
    activity_level = Column(String, nullable=False)
    goal_type = Column(String, nullable=False)
    goal_date = Column(DateTime, nullable=False)


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    target_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="goals")

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    main_muscle_group = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    form_cues = Column(Text, nullable=True)
    visual_reference = Column(String, nullable=True)
