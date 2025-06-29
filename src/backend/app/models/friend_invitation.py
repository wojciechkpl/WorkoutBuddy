from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class FriendInvitation(Base):
    __tablename__ = "friend_invitations"

    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invitee_email = Column(String, nullable=True)
    invitee_phone = Column(String, nullable=True)
    invitation_code = Column(String, unique=True, nullable=False)
    invitation_type = Column(String, nullable=False)
    personalized_message = Column(Text, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)

    inviter = relationship("User", foreign_keys=[inviter_id])

    def __repr__(self):
        return f"<FriendInvitation(inviter_id={self.inviter_id}, invitee_email={self.invitee_email}, code={self.invitation_code}, status={self.status})>" 