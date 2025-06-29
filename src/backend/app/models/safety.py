from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ReportReasonEnum(str, enum.Enum):
    SPAM = "spam"
    ABUSE = "abuse"
    HARASSMENT = "harassment"
    OTHER = "other"


class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Enum(ReportReasonEnum), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)


class UserBlock(Base):
    __tablename__ = "user_blocks"
    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
