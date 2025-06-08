from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext

from .core import models, schemas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# User CRUD Operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID with optimized query"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create new user with community preferences"""
    hashed_password = hash_password(user.password)

    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        year_of_birth=user.year_of_birth,
        height_ft=user.height_ft,
        height_in=user.height_in,
        weight_lb=user.weight_lb,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        goal_type=user.goal_type,
        goal_date=user.goal_date,
        # Community accountability features
        wants_accountability_partner=user.wants_accountability_partner,
        accountability_preference=user.accountability_preference,
        motivation_style=user.motivation_style,
        time_zone=user.time_zone,
        preferred_check_in_frequency=user.preferred_check_in_frequency,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user_id: int, update_data: Dict[str, Any]
) -> Optional[models.User]:
    """Update user with new data"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    user.last_active = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def get_users_wanting_partners(db: Session, limit: int = 50) -> List[models.User]:
    """Get users who want accountability partners"""
    return (
        db.query(models.User)
        .filter(models.User.wants_accountability_partner == True)
        .limit(limit)
        .all()
    )


# Goal CRUD Operations
def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int) -> models.Goal:
    """Create goal with community features"""
    db_goal = models.Goal(**goal.dict(), owner_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goal(db: Session, goal_id: int) -> Optional[models.Goal]:
    """Get goal by ID"""
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()


def get_goals(db: Session, user_id: int) -> List[models.Goal]:
    """Get all goals for a user"""
    return db.query(models.Goal).filter(models.Goal.owner_id == user_id).all()


def get_public_goals(
    db: Session, limit: int = 20, offset: int = 0
) -> List[models.Goal]:
    """Get public goals for community feed"""
    return (
        db.query(models.Goal)
        .filter(models.Goal.is_public == True)
        .order_by(desc(models.Goal.target_date))
        .offset(offset)
        .limit(limit)
        .all()
    )


def update_goal_community_support(db: Session, goal_id: int) -> Optional[models.Goal]:
    """Increment community support count for a goal"""
    goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if goal:
        goal.community_support_count += 1
        db.commit()
        db.refresh(goal)
    return goal


# Community Connection CRUD Operations
def create_community_connection(
    db: Session, connection: schemas.CommunityConnectionCreate, requester_id: int
) -> models.CommunityConnection:
    """Create accountability partnership request"""
    db_connection = models.CommunityConnection(
        requester_id=requester_id,
        partner_id=connection.partner_id,
        connection_type=connection.connection_type,
        goal_compatibility=connection.goal_compatibility,
        schedule_compatibility=connection.schedule_compatibility,
        personality_compatibility=connection.personality_compatibility,
        status=models.CommunityConnectionStatus.PENDING,
    )

    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection


def get_community_connection(
    db: Session, connection_id: int
) -> Optional[models.CommunityConnection]:
    """Get community connection by ID"""
    return (
        db.query(models.CommunityConnection)
        .filter(models.CommunityConnection.id == connection_id)
        .first()
    )


def get_user_connections(db: Session, user_id: int) -> List[models.CommunityConnection]:
    """Get all connections for a user (both sent and received)"""
    return (
        db.query(models.CommunityConnection)
        .filter(
            or_(
                models.CommunityConnection.requester_id == user_id,
                models.CommunityConnection.partner_id == user_id,
            )
        )
        .all()
    )


def get_active_partnerships(
    db: Session, user_id: int
) -> List[models.CommunityConnection]:
    """Get active accountability partnerships for a user"""
    return (
        db.query(models.CommunityConnection)
        .filter(
            or_(
                models.CommunityConnection.requester_id == user_id,
                models.CommunityConnection.partner_id == user_id,
            ),
            models.CommunityConnection.status
            == models.CommunityConnectionStatus.ACTIVE,
        )
        .all()
    )


def update_connection_status(
    db: Session, connection_id: int, status: schemas.CommunityConnectionStatus
) -> Optional[models.CommunityConnection]:
    """Update connection status (accept/reject partnership)"""
    connection = (
        db.query(models.CommunityConnection)
        .filter(models.CommunityConnection.id == connection_id)
        .first()
    )

    if connection:
        connection.status = status
        if status == models.CommunityConnectionStatus.ACTIVE:
            connection.started_at = datetime.utcnow()
        elif status in [
            models.CommunityConnectionStatus.COMPLETED,
            models.CommunityConnectionStatus.PAUSED,
        ]:
            connection.ended_at = datetime.utcnow()

        db.commit()
        db.refresh(connection)

    return connection


def update_connection_metrics(
    db: Session, connection_id: int, metrics: Dict[str, float]
) -> Optional[models.CommunityConnection]:
    """Update partnership success metrics"""
    connection = (
        db.query(models.CommunityConnection)
        .filter(models.CommunityConnection.id == connection_id)
        .first()
    )

    if connection:
        for key, value in metrics.items():
            if hasattr(connection, key):
                setattr(connection, key, value)

        db.commit()
        db.refresh(connection)

    return connection


# Check-in CRUD Operations
def create_accountability_check_in(
    db: Session, check_in: schemas.AccountabilityCheckInCreate, user_id: int
) -> models.AccountabilityCheckIn:
    """Create accountability check-in"""
    db_check_in = models.AccountabilityCheckIn(
        user_id=user_id,
        connection_id=check_in.connection_id,
        workout_completed=check_in.workout_completed,
        energy_level=check_in.energy_level,
        motivation_level=check_in.motivation_level,
        notes=check_in.notes,
        challenges_faced=check_in.challenges_faced,
    )

    db.add(db_check_in)
    db.commit()
    db.refresh(db_check_in)

    # Update connection check-in count
    connection = (
        db.query(models.CommunityConnection)
        .filter(models.CommunityConnection.id == check_in.connection_id)
        .first()
    )
    if connection:
        connection.total_check_ins += 1
        db.commit()

    return db_check_in


def create_partner_response(
    db: Session, response: schemas.PartnerResponseCreate, check_in_id: int
) -> Optional[models.AccountabilityCheckIn]:
    """Respond to partner's check-in"""
    check_in = (
        db.query(models.AccountabilityCheckIn)
        .filter(models.AccountabilityCheckIn.id == check_in_id)
        .first()
    )

    if check_in:
        check_in.partner_responded = True
        check_in.partner_response = response.response
        check_in.encouragement_sent = response.encouragement_sent
        check_in.response_time_hours = (
            datetime.utcnow() - check_in.check_in_date
        ).total_seconds() / 3600

        db.commit()
        db.refresh(check_in)

    return check_in


def get_user_check_ins(
    db: Session, user_id: int, limit: int = 20, days: int = 30
) -> List[models.AccountabilityCheckIn]:
    """Get recent check-ins for a user"""
    since_date = datetime.utcnow() - timedelta(days=days)

    return (
        db.query(models.AccountabilityCheckIn)
        .filter(
            models.AccountabilityCheckIn.user_id == user_id,
            models.AccountabilityCheckIn.check_in_date >= since_date,
        )
        .order_by(desc(models.AccountabilityCheckIn.check_in_date))
        .limit(limit)
        .all()
    )


def get_pending_partner_responses(
    db: Session, user_id: int
) -> List[models.AccountabilityCheckIn]:
    """Get check-ins that need partner responses"""
    # Get user's partnerships
    partnerships = get_active_partnerships(db, user_id)
    connection_ids = [p.id for p in partnerships]

    if not connection_ids:
        return []

    # Find check-ins from partners that need responses
    return (
        db.query(models.AccountabilityCheckIn)
        .filter(
            models.AccountabilityCheckIn.connection_id.in_(connection_ids),
            models.AccountabilityCheckIn.user_id != user_id,
            models.AccountabilityCheckIn.partner_responded == False,
            models.AccountabilityCheckIn.check_in_date
            >= datetime.utcnow() - timedelta(days=7),
        )
        .order_by(desc(models.AccountabilityCheckIn.check_in_date))
        .all()
    )


# Goal Check-in CRUD Operations
def create_goal_check_in(
    db: Session, check_in: schemas.GoalCheckInCreate, user_id: int
) -> models.GoalCheckIn:
    """Create goal progress check-in"""
    db_check_in = models.GoalCheckIn(
        goal_id=check_in.goal_id,
        user_id=user_id,
        progress_percentage=check_in.progress_percentage,
        is_on_track=check_in.is_on_track,
        confidence_level=check_in.confidence_level,
        notes=check_in.notes,
    )

    db.add(db_check_in)
    db.commit()
    db.refresh(db_check_in)
    return db_check_in


def get_goal_check_ins(db: Session, goal_id: int) -> List[models.GoalCheckIn]:
    """Get all check-ins for a goal"""
    return (
        db.query(models.GoalCheckIn)
        .filter(models.GoalCheckIn.goal_id == goal_id)
        .order_by(desc(models.GoalCheckIn.check_in_date))
        .all()
    )


# Progress Update CRUD Operations
def create_progress_update(
    db: Session, update: schemas.ProgressUpdateCreate, user_id: int
) -> models.ProgressUpdate:
    """Create shareable progress update"""
    db_update = models.ProgressUpdate(
        goal_id=update.goal_id,
        user_id=user_id,
        update_text=update.update_text,
        milestone_achieved=update.milestone_achieved,
        progress_percentage=update.progress_percentage,
    )

    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update


def get_community_feed(
    db: Session, limit: int = 20, offset: int = 0, user_id: Optional[int] = None
) -> List[models.ProgressUpdate]:
    """Get community progress feed"""
    query = db.query(models.ProgressUpdate)

    # If user_id provided, prioritize updates from their connections
    if user_id:
        partnerships = get_active_partnerships(db, user_id)
        partner_ids = []
        for partnership in partnerships:
            if partnership.requester_id == user_id:
                partner_ids.append(partnership.partner_id)
            else:
                partner_ids.append(partnership.requester_id)

        # Show partner updates first, then public updates
        query = query.filter(
            or_(
                models.ProgressUpdate.user_id.in_(partner_ids),
                models.ProgressUpdate.goal_id.in_(
                    db.query(models.Goal.id).filter(models.Goal.is_public == True)
                ),
            )
        )

    return (
        query.order_by(desc(models.ProgressUpdate.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


def increment_progress_update_engagement(
    db: Session, update_id: int, engagement_type: str
) -> Optional[models.ProgressUpdate]:
    """Increment engagement metrics for progress update"""
    update = (
        db.query(models.ProgressUpdate)
        .filter(models.ProgressUpdate.id == update_id)
        .first()
    )

    if update:
        if engagement_type == "view":
            update.views_count += 1
        elif engagement_type == "encouragement":
            update.encouragement_count += 1
        elif engagement_type == "share":
            update.shares_count += 1

        db.commit()
        db.refresh(update)

    return update


# Feedback CRUD Operations
def create_user_feedback(
    db: Session, feedback: schemas.UserFeedbackCreate, user_id: int
) -> models.UserFeedback:
    """Create user feedback for hypothesis validation"""
    db_feedback = models.UserFeedback(
        user_id=user_id,
        community_impact_rating=feedback.community_impact_rating,
        accountability_effectiveness=feedback.accountability_effectiveness,
        motivation_improvement=feedback.motivation_improvement,
        adherence_improvement=feedback.adherence_improvement,
        most_helpful_feature=feedback.most_helpful_feature,
        biggest_challenge=feedback.biggest_challenge,
        suggestions=feedback.suggestions,
        would_recommend=feedback.would_recommend,
        likelihood_to_continue=feedback.likelihood_to_continue,
        primary_retention_driver=feedback.primary_retention_driver,
    )

    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_user_feedback_history(db: Session, user_id: int) -> List[models.UserFeedback]:
    """Get all feedback submissions for a user"""
    return (
        db.query(models.UserFeedback)
        .filter(models.UserFeedback.user_id == user_id)
        .order_by(desc(models.UserFeedback.created_at))
        .all()
    )


def get_aggregated_feedback_metrics(db: Session) -> Dict[str, Any]:
    """Get aggregated feedback metrics for analysis"""
    feedbacks = db.query(models.UserFeedback).all()

    if not feedbacks:
        return {"message": "No feedback data available"}

    metrics = {
        "total_responses": len(feedbacks),
        "avg_community_impact": 0,
        "avg_accountability_effectiveness": 0,
        "avg_motivation_improvement": 0,
        "avg_adherence_improvement": 0,
        "recommendation_rate": 0,
        "avg_likelihood_to_continue": 0,
        "retention_drivers": {},
        "helpful_features": {},
        "common_challenges": {},
    }

    # Calculate averages
    impact_ratings = [
        f.community_impact_rating for f in feedbacks if f.community_impact_rating
    ]
    if impact_ratings:
        metrics["avg_community_impact"] = sum(impact_ratings) / len(impact_ratings)

    accountability_ratings = [
        f.accountability_effectiveness
        for f in feedbacks
        if f.accountability_effectiveness
    ]
    if accountability_ratings:
        metrics["avg_accountability_effectiveness"] = sum(accountability_ratings) / len(
            accountability_ratings
        )

    motivation_ratings = [
        f.motivation_improvement for f in feedbacks if f.motivation_improvement
    ]
    if motivation_ratings:
        metrics["avg_motivation_improvement"] = sum(motivation_ratings) / len(
            motivation_ratings
        )

    adherence_ratings = [
        f.adherence_improvement for f in feedbacks if f.adherence_improvement
    ]
    if adherence_ratings:
        metrics["avg_adherence_improvement"] = sum(adherence_ratings) / len(
            adherence_ratings
        )

    likelihood_ratings = [
        f.likelihood_to_continue for f in feedbacks if f.likelihood_to_continue
    ]
    if likelihood_ratings:
        metrics["avg_likelihood_to_continue"] = sum(likelihood_ratings) / len(
            likelihood_ratings
        )

    # Calculate recommendation rate
    recommendations = [
        f.would_recommend for f in feedbacks if f.would_recommend is not None
    ]
    if recommendations:
        metrics["recommendation_rate"] = sum(recommendations) / len(recommendations)

    # Count categorical responses
    for feedback in feedbacks:
        if feedback.primary_retention_driver:
            metrics["retention_drivers"][feedback.primary_retention_driver] = (
                metrics["retention_drivers"].get(feedback.primary_retention_driver, 0)
                + 1
            )

        if feedback.most_helpful_feature:
            metrics["helpful_features"][feedback.most_helpful_feature] = (
                metrics["helpful_features"].get(feedback.most_helpful_feature, 0) + 1
            )

        if feedback.biggest_challenge:
            metrics["common_challenges"][feedback.biggest_challenge] = (
                metrics["common_challenges"].get(feedback.biggest_challenge, 0) + 1
            )

    return metrics


# Community Group CRUD Operations
def create_community_group(
    db: Session, group: schemas.CommunityGroupCreate
) -> models.CommunityGroup:
    """Create community group"""
    db_group = models.CommunityGroup(
        name=group.name,
        description=group.description,
        max_members=group.max_members,
        requires_approval=group.requires_approval,
    )

    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_community_groups(db: Session, limit: int = 20) -> List[models.CommunityGroup]:
    """Get available community groups"""
    return (
        db.query(models.CommunityGroup)
        .filter(models.CommunityGroup.is_active == True)
        .limit(limit)
        .all()
    )


def request_group_membership(
    db: Session, group_id: int, user_id: int
) -> models.GroupMembership:
    """Request to join community group"""
    # Check if user is already a member
    existing = (
        db.query(models.GroupMembership)
        .filter(
            models.GroupMembership.group_id == group_id,
            models.GroupMembership.user_id == user_id,
            models.GroupMembership.is_active == True,
        )
        .first()
    )

    if existing:
        return existing

    membership = models.GroupMembership(group_id=group_id, user_id=user_id)

    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def get_user_group_memberships(
    db: Session, user_id: int
) -> List[models.GroupMembership]:
    """Get user's group memberships"""
    return (
        db.query(models.GroupMembership)
        .filter(
            models.GroupMembership.user_id == user_id,
            models.GroupMembership.is_active == True,
        )
        .all()
    )


# Analytics and Reporting
def calculate_user_engagement_score(db: Session, user_id: int) -> float:
    """Calculate comprehensive user engagement score"""
    user = get_user(db, user_id)
    if not user:
        return 0.0

    score = 0.0

    # Check-in frequency (30%)
    recent_check_ins = get_user_check_ins(db, user_id, days=30)
    check_in_frequency = len(recent_check_ins) / 30  # Check-ins per day
    score += min(check_in_frequency * 10, 3.0)  # Max 3 points

    # Partnership activity (25%)
    partnerships = get_active_partnerships(db, user_id)
    if partnerships:
        score += 2.5

    # Community interaction (25%)
    pending_responses = get_pending_partner_responses(db, user_id)
    response_rate = 1.0 - (len(pending_responses) / max(len(recent_check_ins), 1))
    score += response_rate * 2.5

    # Goal setting and tracking (20%)
    goals = get_goals(db, user_id)
    public_goals = [g for g in goals if g.is_public or g.wants_support]
    if goals:
        goal_score = (len(public_goals) / len(goals)) * 2.0
        score += goal_score

    return min(score / 10.0, 1.0)  # Normalize to 0-1


def calculate_retention_risk(db: Session, user_id: int) -> float:
    """Calculate user retention risk"""
    user = get_user(db, user_id)
    if not user:
        return 1.0  # High risk if user doesn't exist

    risk_factors = 0.0

    # Days since last activity
    if user.last_active:
        days_inactive = (datetime.utcnow() - user.last_active).days
        if days_inactive > 7:
            risk_factors += 0.3
        if days_inactive > 14:
            risk_factors += 0.3
    else:
        risk_factors += 0.6

    # Low engagement score
    engagement = calculate_user_engagement_score(db, user_id)
    if engagement < 0.3:
        risk_factors += 0.4

    # No accountability partners
    partnerships = get_active_partnerships(db, user_id)
    if not partnerships:
        risk_factors += 0.2

    # No recent goals
    goals = get_goals(db, user_id)
    recent_goals = [
        g for g in goals if g.target_date and g.target_date > datetime.utcnow()
    ]
    if not recent_goals:
        risk_factors += 0.2

    return min(risk_factors, 1.0)
