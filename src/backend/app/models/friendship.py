# backend/app/models/friendship.py
"""
Friendship model for social features
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Friendship(Base):
    """Friendship model for social connections"""
    __tablename__ = "friendships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="sent_friendships")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="received_friendships")
    
    # Ensure unique friendships
    __table_args__ = (
        UniqueConstraint('user_id', 'friend_id', name='_user_friend_uc'),
    )
    
    def __repr__(self):
        return f"<Friendship(user_id={self.user_id}, friend_id={self.friend_id}, accepted={self.is_accepted})>"