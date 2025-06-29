# backend/app/models/challenge.py
"""
Challenge model
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.schemas.challenge import ChallengeType, ChallengeStatus


class Challenge(Base):
    """Challenge model"""

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    challenge_type = Column(Enum(ChallengeType), nullable=False)
    target_value = Column(Float, nullable=False)
    target_unit = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reward_points = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False)
    status = Column(Enum(ChallengeStatus), default=ChallengeStatus.ACTIVE)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="created_challenges")
