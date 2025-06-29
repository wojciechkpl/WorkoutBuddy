from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from app.database import Base


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommendation_id = Column(String, nullable=False)
    feedback = Column(Text)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
