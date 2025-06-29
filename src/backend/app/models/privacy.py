from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.database import Base


class PrivacySetting(Base):
    __tablename__ = "privacy_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    show_profile = Column(Boolean, default=True)
    show_workouts = Column(Boolean, default=True)
    show_stats = Column(Boolean, default=True)
    allow_friend_requests = Column(Boolean, default=True)
