"""
User goals and progress tracking
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class UserGoal(Base):
    """User fitness goals"""

    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(
        String, nullable=False
    )  # e.g., "bench_press_max", "5k_time", "weight"
    target_value = Column(Float, nullable=False)
    current_value = Column(Float)
    target_date = Column(DateTime)
    is_achieved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    achieved_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<UserGoal(type='{self.goal_type}', target={self.target_value})>"
