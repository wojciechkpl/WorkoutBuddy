import posthog
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass
import pandas as pd

from .core import models

logger = logging.getLogger(__name__)


@dataclass
class CohortMetrics:
    cohort_name: str
    total_users: int
    goal_completion_rate: float
    avg_engagement_score: float
    retention_rate: float
    days_to_first_goal: Optional[float]
    community_impact_factor: float


@dataclass
class EventMetrics:
    event_name: str
    count: int
    unique_users: int
    avg_properties: Dict[str, Any]
    conversion_rate: Optional[float] = None


class AnalyticsService:
    def __init__(self):
        self.posthog_key = os.getenv("POSTHOG_API_KEY")
        self.enabled = bool(self.posthog_key)

        if self.enabled:
            posthog.api_key = self.posthog_key
            posthog.host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
            logger.info("PostHog analytics initialized")
        else:
            logger.warning(
                "PostHog API key not found. Analytics will be logged locally only."
            )

    def track_event(
        self, user_id: str, event_name: str, properties: Dict[str, Any] = None
    ):
        """Track user events with PostHog"""
        properties = properties or {}
        properties.update(
            {"timestamp": datetime.utcnow().isoformat(), "source": "workoutbuddy_api"}
        )

        if self.enabled:
            try:
                posthog.capture(user_id, event_name, properties)
            except Exception as e:
                logger.error(f"PostHog tracking failed: {e}")

        # Always log locally for debugging
        logger.info(
            f"Event tracked: {event_name} for user {user_id} with properties {properties}"
        )

    def identify_user(self, user_id: str, user_properties: Dict[str, Any]):
        """Identify user with their properties"""
        if self.enabled:
            try:
                posthog.identify(user_id, user_properties)
            except Exception as e:
                logger.error(f"PostHog user identification failed: {e}")

        logger.info(f"User identified: {user_id} with properties {user_properties}")

    def track_user_registration(self, user: models.User):
        """Track user registration with key properties"""
        properties = {
            "goal_type": user.goal_type,
            "activity_level": user.activity_level,
            "age": datetime.now().year - user.year_of_birth,
            "wants_accountability": getattr(
                user, "wants_accountability_partner", False
            ),
            "registration_date": user.created_at.isoformat(),
        }

        self.identify_user(str(user.id), properties)
        self.track_event(str(user.id), "user_registered", properties)

    def track_challenge_generation(
        self, user_id: str, challenge_data: Dict, ai_generated: bool = False
    ):
        """Track challenge generation events"""
        properties = {
            "challenge_type": challenge_data.get("goal_type", "unknown"),
            "difficulty": challenge_data.get("difficulty", 0),
            "ai_generated": ai_generated,
            "equipment_needed": len(challenge_data.get("equipment_needed", [])),
            "duration": challenge_data.get("duration", "unknown"),
        }

        self.track_event(user_id, "challenge_generated", properties)

    def track_challenge_completion(
        self, user_id: str, challenge_data: Dict, completed: bool
    ):
        """Track challenge completion"""
        properties = {
            "completed": completed,
            "challenge_type": challenge_data.get("goal_type", "unknown"),
            "difficulty": challenge_data.get("difficulty", 0),
            "completion_time": datetime.utcnow().isoformat(),
        }

        event_name = "challenge_completed" if completed else "challenge_abandoned"
        self.track_event(user_id, event_name, properties)

    def track_community_interaction(
        self, user_id: str, interaction_type: str, target_user_id: str = None
    ):
        """Track community interactions"""
        properties = {
            "interaction_type": interaction_type,  # "match_request", "encouragement_sent", "message", etc.
            "target_user_id": target_user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.track_event(user_id, "community_interaction", properties)

    def track_goal_progress(
        self, user_id: str, goal_id: str, progress_percentage: float
    ):
        """Track goal progress updates"""
        properties = {
            "goal_id": goal_id,
            "progress_percentage": progress_percentage,
            "milestone": self._get_milestone(progress_percentage),
        }

        self.track_event(user_id, "goal_progress_updated", properties)

        # Track milestone achievements
        if progress_percentage in [25, 50, 75, 100]:
            self.track_event(
                user_id, f"milestone_{int(progress_percentage)}_achieved", properties
            )

    def analyze_cohorts(self, db: Session) -> List[CohortMetrics]:
        """Analyze user cohorts for retention and engagement"""
        try:
            # Define cohorts based on registration week
            cohorts = []

            # Weekly cohorts for the last 8 weeks
            for week_offset in range(8):
                start_date = datetime.utcnow() - timedelta(weeks=week_offset + 1)
                end_date = datetime.utcnow() - timedelta(weeks=week_offset)

                cohort_users = (
                    db.query(models.User)
                    .filter(
                        models.User.created_at >= start_date,
                        models.User.created_at < end_date,
                    )
                    .all()
                )

                if cohort_users:
                    metrics = self._calculate_cohort_metrics(cohort_users, db)
                    cohort_name = f"Week {start_date.strftime('%Y-%W')}"

                    cohorts.append(
                        CohortMetrics(
                            cohort_name=cohort_name,
                            total_users=len(cohort_users),
                            goal_completion_rate=metrics["goal_completion_rate"],
                            avg_engagement_score=metrics["avg_engagement_score"],
                            retention_rate=metrics["retention_rate"],
                            days_to_first_goal=metrics["days_to_first_goal"],
                            community_impact_factor=metrics["community_impact_factor"],
                        )
                    )

            return cohorts

        except Exception as e:
            logger.error(f"Cohort analysis failed: {e}")
            return []

    def get_event_metrics(self, db: Session, days: int = 7) -> List[EventMetrics]:
        """Get event metrics from database (simplified version without PostHog queries)"""
        # This would typically query PostHog's API, but we'll simulate with database data
        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Simulate event metrics based on database activity
            metrics = []

            # User registrations
            new_users = (
                db.query(models.User)
                .filter(models.User.created_at >= start_date)
                .count()
            )

            metrics.append(
                EventMetrics(
                    event_name="user_registered",
                    count=new_users,
                    unique_users=new_users,
                    avg_properties={},
                )
            )

            # Goal creations
            new_goals = (
                db.query(models.Goal)
                .filter(models.Goal.target_date >= start_date)
                .count()
            )

            metrics.append(
                EventMetrics(
                    event_name="goal_created",
                    count=new_goals,
                    unique_users=new_goals,  # Simplified assumption
                    avg_properties={},
                )
            )

            return metrics

        except Exception as e:
            logger.error(f"Event metrics calculation failed: {e}")
            return []

    def _calculate_cohort_metrics(
        self, users: List[models.User], db: Session
    ) -> Dict[str, float]:
        """Calculate metrics for a user cohort"""
        if not users:
            return self._empty_metrics()

        total_users = len(users)
        user_ids = [user.id for user in users]

        # Goal completion rate
        completed_goals = 0
        total_goals = 0
        days_to_completion = []

        for user_id in user_ids:
            user_goals = (
                db.query(models.Goal).filter(models.Goal.owner_id == user_id).all()
            )
            total_goals += len(user_goals)

            for goal in user_goals:
                if goal.target_date and goal.target_date < datetime.utcnow():
                    # Check if goal was completed (simplified check)
                    completed_goals += 1

                    # Calculate days to completion
                    if goal.target_date:
                        days = (
                            (goal.target_date - goal.created_at).days
                            if hasattr(goal, "created_at")
                            else 30
                        )
                        days_to_completion.append(days)

        goal_completion_rate = completed_goals / total_goals if total_goals > 0 else 0

        # Average engagement score
        engagement_scores = [
            getattr(user, "community_engagement_score", 0) for user in users
        ]
        avg_engagement = (
            sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        )

        # Retention rate (users active in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users = sum(
            1
            for user in users
            if getattr(user, "last_active", user.created_at) >= week_ago
        )
        retention_rate = active_users / total_users

        # Community impact factor (users with accountability partners perform better)
        with_community = [
            user
            for user in users
            if getattr(user, "wants_accountability_partner", False)
        ]
        without_community = [
            user
            for user in users
            if not getattr(user, "wants_accountability_partner", False)
        ]

        community_impact_factor = 1.0
        if with_community and without_community:
            with_score = sum(
                getattr(user, "community_engagement_score", 0)
                for user in with_community
            ) / len(with_community)
            without_score = sum(
                getattr(user, "community_engagement_score", 0)
                for user in without_community
            ) / len(without_community)
            community_impact_factor = (
                with_score / without_score if without_score > 0 else 1.0
            )

        return {
            "goal_completion_rate": goal_completion_rate,
            "avg_engagement_score": avg_engagement,
            "retention_rate": retention_rate,
            "days_to_first_goal": sum(days_to_completion) / len(days_to_completion)
            if days_to_completion
            else None,
            "community_impact_factor": community_impact_factor,
        }

    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics for cohorts with no users"""
        return {
            "goal_completion_rate": 0.0,
            "avg_engagement_score": 0.0,
            "retention_rate": 0.0,
            "days_to_first_goal": None,
            "community_impact_factor": 1.0,
        }

    def _get_milestone(self, progress: float) -> str:
        """Get milestone name based on progress percentage"""
        if progress >= 100:
            return "completed"
        elif progress >= 75:
            return "almost_there"
        elif progress >= 50:
            return "halfway"
        elif progress >= 25:
            return "getting_started"
        else:
            return "just_started"


# Global analytics service instance
analytics_service = AnalyticsService()
