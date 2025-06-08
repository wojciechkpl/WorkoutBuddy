from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Boolean,
    Float,
    Enum,
)
from sqlalchemy.orm import relationship
from ..database import Base
import datetime
import enum


class AccountabilityType(enum.Enum):
    WORKOUT_PARTNER = "workout_partner"
    PROGRESS_CHECKER = "progress_checker"
    GOAL_SUPPORTER = "goal_supporter"
    COMMUNITY_GROUP = "community_group"


class CommunityConnectionStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


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

    # Crawl Phase: Community accountability features
    wants_accountability_partner = Column(Boolean, default=False)
    accountability_preference = Column(Enum(AccountabilityType), nullable=True)
    motivation_style = Column(
        String, nullable=True
    )  # "encouraging", "competitive", "analytical"
    time_zone = Column(String, nullable=True)
    preferred_check_in_frequency = Column(
        String, nullable=True
    )  # "daily", "weekly", "bi-weekly"

    # Feedback collection for hypothesis validation
    retention_score = Column(Float, default=0.0)  # Calculated metric
    community_engagement_score = Column(Float, default=0.0)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships for community features
    sent_connections = relationship(
        "CommunityConnection",
        foreign_keys="CommunityConnection.requester_id",
        back_populates="requester",
    )
    received_connections = relationship(
        "CommunityConnection",
        foreign_keys="CommunityConnection.partner_id",
        back_populates="partner",
    )
    check_ins = relationship("AccountabilityCheckIn", back_populates="user")
    feedback_responses = relationship("UserFeedback", back_populates="user")


class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    target_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="goals")

    # Crawl Phase: Community accountability for goals
    is_public = Column(Boolean, default=False)  # Allow community to see goal
    wants_support = Column(Boolean, default=False)  # User wants accountability
    success_probability = Column(Float, default=0.5)  # ML prediction
    community_support_count = Column(Integer, default=0)

    # Progress tracking for accountability
    check_ins = relationship("GoalCheckIn", back_populates="goal")
    progress_updates = relationship("ProgressUpdate", back_populates="goal")


class CommunityConnection(Base):
    """Connects users for accountability partnerships"""

    __tablename__ = "community_connections"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"))
    partner_id = Column(Integer, ForeignKey("users.id"))
    connection_type = Column(Enum(AccountabilityType))
    status = Column(
        Enum(CommunityConnectionStatus), default=CommunityConnectionStatus.PENDING
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Matching criteria
    goal_compatibility = Column(Float, default=0.0)  # How well goals align (0-1)
    schedule_compatibility = Column(Float, default=0.0)  # Time zone/availability match
    personality_compatibility = Column(Float, default=0.0)  # Communication style match

    # Success metrics for hypothesis validation
    total_check_ins = Column(Integer, default=0)
    mutual_success_rate = Column(Float, default=0.0)
    partnership_satisfaction = Column(Float, default=0.0)

    # Relationships
    requester = relationship(
        "User", foreign_keys=[requester_id], back_populates="sent_connections"
    )
    partner = relationship(
        "User", foreign_keys=[partner_id], back_populates="received_connections"
    )
    check_ins = relationship("AccountabilityCheckIn", back_populates="connection")


class AccountabilityCheckIn(Base):
    """Daily/weekly check-ins between accountability partners"""

    __tablename__ = "accountability_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    connection_id = Column(Integer, ForeignKey("community_connections.id"))
    check_in_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Check-in content
    workout_completed = Column(Boolean, default=False)
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    motivation_level = Column(Integer, nullable=True)  # 1-10 scale
    notes = Column(Text, nullable=True)
    challenges_faced = Column(Text, nullable=True)

    # Partner interaction
    partner_responded = Column(Boolean, default=False)
    partner_response = Column(Text, nullable=True)
    encouragement_sent = Column(Boolean, default=False)

    # Metrics for hypothesis validation
    response_time_hours = Column(Float, nullable=True)
    interaction_quality_score = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="check_ins")
    connection = relationship("CommunityConnection", back_populates="check_ins")


class GoalCheckIn(Base):
    """Progress check-ins for specific goals"""

    __tablename__ = "goal_check_ins"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    check_in_date = Column(DateTime, default=datetime.datetime.utcnow)

    progress_percentage = Column(Float, default=0.0)
    is_on_track = Column(Boolean, default=True)
    confidence_level = Column(Integer, nullable=True)  # 1-10 how confident they are
    notes = Column(Text, nullable=True)

    # Community impact metrics
    community_views = Column(Integer, default=0)
    community_encouragement_count = Column(Integer, default=0)

    goal = relationship("Goal", back_populates="check_ins")


class ProgressUpdate(Base):
    """Shareable progress updates for community motivation"""

    __tablename__ = "progress_updates"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    update_text = Column(Text)
    milestone_achieved = Column(String, nullable=True)
    progress_percentage = Column(Float, default=0.0)

    # Community engagement metrics
    views_count = Column(Integer, default=0)
    encouragement_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)

    goal = relationship("Goal", back_populates="progress_updates")


class UserFeedback(Base):
    """Collect feedback to validate community accountability hypothesis"""

    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Core hypothesis questions
    community_impact_rating = Column(
        Integer, nullable=True
    )  # 1-10: How much has community helped?
    accountability_effectiveness = Column(
        Integer, nullable=True
    )  # 1-10: How effective is accountability?
    motivation_improvement = Column(
        Integer, nullable=True
    )  # 1-10: Motivation increase?
    adherence_improvement = Column(
        Integer, nullable=True
    )  # 1-10: Better at sticking to goals?

    # Qualitative feedback
    most_helpful_feature = Column(String, nullable=True)
    biggest_challenge = Column(String, nullable=True)
    suggestions = Column(Text, nullable=True)
    would_recommend = Column(Boolean, nullable=True)

    # Retention indicators
    likelihood_to_continue = Column(Integer, nullable=True)  # 1-10
    primary_retention_driver = Column(String, nullable=True)

    user = relationship("User", back_populates="feedback_responses")


class CommunityGroup(Base):
    """Small groups for accountability (manual curation in Crawl phase)"""

    __tablename__ = "community_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Group settings
    max_members = Column(
        Integer, default=8
    )  # Keep groups small for strong accountability
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)  # Manual curation

    # Success metrics
    member_retention_rate = Column(Float, default=0.0)
    average_goal_completion_rate = Column(Float, default=0.0)
    average_engagement_score = Column(Float, default=0.0)

    # Relationships
    memberships = relationship("GroupMembership", back_populates="group")


class GroupMembership(Base):
    """Track user membership in community groups"""

    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("community_groups.id"))
    joined_at = Column(DateTime, default=datetime.datetime.utcnow)
    left_at = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    role = Column(String, default="member")  # "member", "moderator", "leader"

    # Engagement metrics
    check_ins_count = Column(Integer, default=0)
    encouragements_given = Column(Integer, default=0)
    encouragements_received = Column(Integer, default=0)

    group = relationship("CommunityGroup", back_populates="memberships")


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
