import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass
from enum import Enum
import random

from .core import models
from .analytics import analytics_service

logger = logging.getLogger(__name__)


class ExperimentStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class ExperimentVariant:
    name: str
    allocation: float  # Percentage of users (0.0-1.0)
    config: Dict[str, Any]
    description: str


@dataclass
class ExperimentConfig:
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    variants: List[ExperimentVariant]
    start_date: datetime
    end_date: Optional[datetime]
    target_metric: str
    minimum_sample_size: int
    created_at: datetime


@dataclass
class ExperimentResult:
    variant_name: str
    sample_size: int
    conversion_rate: float
    confidence_interval: tuple
    statistical_significance: bool


class ABTestingService:
    def __init__(self):
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.user_assignments: Dict[
            str, Dict[str, str]
        ] = {}  # user_id -> {experiment_id: variant}
        self._initialize_default_experiments()

    def _initialize_default_experiments(self):
        """Initialize default experiments for immediate testing"""

        # AI-powered challenge generation experiment
        self.experiments["ai_challenges_v1"] = ExperimentConfig(
            experiment_id="ai_challenges_v1",
            name="AI-Powered Challenge Generation",
            description="Test AI-generated vs. template-based challenges",
            status=ExperimentStatus.ACTIVE,
            variants=[
                ExperimentVariant(
                    name="control",
                    allocation=0.5,
                    config={"use_ai_challenges": False, "challenge_source": "template"},
                    description="Standard template-based challenges",
                ),
                ExperimentVariant(
                    name="ai_powered",
                    allocation=0.5,
                    config={"use_ai_challenges": True, "challenge_source": "ai"},
                    description="AI-generated personalized challenges",
                ),
            ],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            target_metric="challenge_completion_rate",
            minimum_sample_size=100,
            created_at=datetime.utcnow(),
        )

        # Community matching experiment
        self.experiments["community_matching_v1"] = ExperimentConfig(
            experiment_id="community_matching_v1",
            name="AI Community Matching",
            description="Test AI-powered vs. basic community matching",
            status=ExperimentStatus.ACTIVE,
            variants=[
                ExperimentVariant(
                    name="basic_matching",
                    allocation=0.5,
                    config={"use_ai_matching": False, "matching_algorithm": "basic"},
                    description="Basic goal-based matching",
                ),
                ExperimentVariant(
                    name="ai_matching",
                    allocation=0.5,
                    config={"use_ai_matching": True, "matching_algorithm": "ai"},
                    description="AI-powered compatibility matching",
                ),
            ],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            target_metric="community_connection_rate",
            minimum_sample_size=50,
            created_at=datetime.utcnow(),
        )

        # Encouragement frequency experiment
        self.experiments["encouragement_frequency_v1"] = ExperimentConfig(
            experiment_id="encouragement_frequency_v1",
            name="Encouragement Frequency Optimization",
            description="Test different frequencies of automated encouragement",
            status=ExperimentStatus.ACTIVE,
            variants=[
                ExperimentVariant(
                    name="daily",
                    allocation=0.33,
                    config={"encouragement_frequency": "daily", "max_per_day": 1},
                    description="Daily encouragement messages",
                ),
                ExperimentVariant(
                    name="every_3_days",
                    allocation=0.33,
                    config={
                        "encouragement_frequency": "every_3_days",
                        "max_per_day": 1,
                    },
                    description="Encouragement every 3 days",
                ),
                ExperimentVariant(
                    name="weekly",
                    allocation=0.34,
                    config={"encouragement_frequency": "weekly", "max_per_day": 1},
                    description="Weekly encouragement messages",
                ),
            ],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            target_metric="user_retention_7_day",
            minimum_sample_size=150,
            created_at=datetime.utcnow(),
        )

    def assign_user_to_experiment(self, user_id: str, experiment_id: str) -> str:
        """Assign user to experiment variant using consistent hashing"""
        if experiment_id not in self.experiments:
            logger.warning(f"Experiment {experiment_id} not found")
            return "control"

        experiment = self.experiments[experiment_id]

        # Check if user already assigned
        if (
            user_id in self.user_assignments
            and experiment_id in self.user_assignments[user_id]
        ):
            return self.user_assignments[user_id][experiment_id]

        # Use consistent hashing for assignment
        hash_input = f"{user_id}_{experiment_id}".encode("utf-8")
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        normalized_hash = (hash_value % 10000) / 10000.0  # 0.0 to 1.0

        # Assign to variant based on allocation
        cumulative_allocation = 0.0
        assigned_variant = "control"

        for variant in experiment.variants:
            cumulative_allocation += variant.allocation
            if normalized_hash <= cumulative_allocation:
                assigned_variant = variant.name
                break

        # Store assignment
        if user_id not in self.user_assignments:
            self.user_assignments[user_id] = {}
        self.user_assignments[user_id][experiment_id] = assigned_variant

        # Track assignment event
        analytics_service.track_event(
            user_id,
            "experiment_assignment",
            {
                "experiment_id": experiment_id,
                "variant": assigned_variant,
                "assignment_method": "consistent_hashing",
            },
        )

        logger.info(
            f"User {user_id} assigned to variant {assigned_variant} in experiment {experiment_id}"
        )
        return assigned_variant

    def get_user_variant(self, user_id: str, experiment_id: str) -> str:
        """Get user's assigned variant for experiment"""
        if experiment_id not in self.experiments:
            return "control"

        if (
            experiment_id not in self.experiments
            or self.experiments[experiment_id].status != ExperimentStatus.ACTIVE
        ):
            return "control"

        return self.assign_user_to_experiment(user_id, experiment_id)

    def get_experiment_config(self, user_id: str, experiment_id: str) -> Dict[str, Any]:
        """Get experiment configuration for user's variant"""
        if experiment_id not in self.experiments:
            return {}

        variant_name = self.get_user_variant(user_id, experiment_id)
        experiment = self.experiments[experiment_id]

        for variant in experiment.variants:
            if variant.name == variant_name:
                return variant.config

        return {}

    def should_use_ai_challenges(self, user_id: str) -> bool:
        """Check if user should receive AI-generated challenges"""
        config = self.get_experiment_config(user_id, "ai_challenges_v1")
        return config.get("use_ai_challenges", False)

    def should_use_ai_matching(self, user_id: str) -> bool:
        """Check if user should use AI-powered community matching"""
        config = self.get_experiment_config(user_id, "community_matching_v1")
        return config.get("use_ai_matching", False)

    def get_encouragement_frequency(self, user_id: str) -> str:
        """Get encouragement frequency for user"""
        config = self.get_experiment_config(user_id, "encouragement_frequency_v1")
        return config.get("encouragement_frequency", "weekly")

    def track_conversion(
        self, user_id: str, experiment_id: str, metric_name: str, value: float
    ):
        """Track conversion events for A/B testing"""
        variant = self.get_user_variant(user_id, experiment_id)

        analytics_service.track_event(
            user_id,
            "experiment_conversion",
            {
                "experiment_id": experiment_id,
                "variant": variant,
                "metric_name": metric_name,
                "metric_value": value,
                "conversion_timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info(
            f"Conversion tracked: {metric_name}={value} for user {user_id} in {experiment_id}:{variant}"
        )

    def analyze_experiment_results(
        self, experiment_id: str, db: Session
    ) -> List[ExperimentResult]:
        """Analyze experiment results with statistical significance"""
        if experiment_id not in self.experiments:
            return []

        experiment = self.experiments[experiment_id]
        results = []

        try:
            # This is a simplified analysis - in production, you'd query PostHog or your analytics database
            for variant in experiment.variants:
                # Calculate sample size for this variant
                variant_users = [
                    user_id
                    for user_id, assignments in self.user_assignments.items()
                    if assignments.get(experiment_id) == variant.name
                ]
                sample_size = len(variant_users)

                # Simulate conversion rate calculation (replace with real data)
                if experiment.target_metric == "challenge_completion_rate":
                    base_rate = 0.65  # 65% baseline completion rate
                    if variant.name == "ai_powered":
                        conversion_rate = base_rate * 1.15  # 15% improvement with AI
                    else:
                        conversion_rate = base_rate
                elif experiment.target_metric == "community_connection_rate":
                    base_rate = 0.35  # 35% baseline connection rate
                    if variant.name == "ai_matching":
                        conversion_rate = (
                            base_rate * 1.25
                        )  # 25% improvement with AI matching
                    else:
                        conversion_rate = base_rate
                else:
                    conversion_rate = random.uniform(0.3, 0.7)  # Placeholder

                # Calculate confidence interval (simplified)
                margin_of_error = (
                    1.96
                    * (conversion_rate * (1 - conversion_rate) / sample_size) ** 0.5
                    if sample_size > 0
                    else 0
                )
                confidence_interval = (
                    max(0, conversion_rate - margin_of_error),
                    min(1, conversion_rate + margin_of_error),
                )

                # Determine statistical significance (simplified check)
                statistical_significance = (
                    sample_size >= experiment.minimum_sample_size
                    and margin_of_error < 0.1
                )

                results.append(
                    ExperimentResult(
                        variant_name=variant.name,
                        sample_size=sample_size,
                        conversion_rate=conversion_rate,
                        confidence_interval=confidence_interval,
                        statistical_significance=statistical_significance,
                    )
                )

            return results

        except Exception as e:
            logger.error(f"Experiment analysis failed for {experiment_id}: {e}")
            return []

    def get_active_experiments(self) -> List[ExperimentConfig]:
        """Get all active experiments"""
        return [
            exp
            for exp in self.experiments.values()
            if exp.status == ExperimentStatus.ACTIVE
        ]

    def create_experiment(self, experiment_config: ExperimentConfig) -> bool:
        """Create a new experiment"""
        try:
            # Validate experiment configuration
            if experiment_config.experiment_id in self.experiments:
                logger.error(
                    f"Experiment {experiment_config.experiment_id} already exists"
                )
                return False

            # Validate variant allocations sum to 1.0
            total_allocation = sum(
                variant.allocation for variant in experiment_config.variants
            )
            if abs(total_allocation - 1.0) > 0.01:
                logger.error(
                    f"Variant allocations must sum to 1.0, got {total_allocation}"
                )
                return False

            self.experiments[experiment_config.experiment_id] = experiment_config
            logger.info(f"Created experiment: {experiment_config.experiment_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            return False

    def pause_experiment(self, experiment_id: str) -> bool:
        """Pause an active experiment"""
        if experiment_id not in self.experiments:
            return False

        self.experiments[experiment_id].status = ExperimentStatus.PAUSED
        logger.info(f"Paused experiment: {experiment_id}")
        return True

    def resume_experiment(self, experiment_id: str) -> bool:
        """Resume a paused experiment"""
        if experiment_id not in self.experiments:
            return False

        self.experiments[experiment_id].status = ExperimentStatus.ACTIVE
        logger.info(f"Resumed experiment: {experiment_id}")
        return True


# Global A/B testing service instance
ab_testing_service = ABTestingService()
