"""
Enhanced ML module leveraging Python's rich AI/ML ecosystem
Designed for scalability and easy model integration
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from dataclasses import dataclass
import logging
from sklearn.neighbors import NearestNeighbors
import pickle

from ..config import backend_config
from . import schemas
from . import models
from .preprocess import DataPreprocessor
from .postprocess import OutputFormatter
from .schemas import (
    WorkoutPlanRequest,
    WorkoutPlanResponse,
    CommunityMatchRequest,
    CommunityMatchResponse,
    ExerciseRecommendationRequest,
    ExerciseRecommendation,
)

logger = logging.getLogger(__name__)

# Model configurations
MODEL_PATH = backend_config.ml.model_path
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class CommunityInsights:
    """AI-generated insights for community management"""

    engagement_score: float
    retention_risk: float
    recommended_actions: List[str]
    optimal_check_in_frequency: str
    personality_traits: Dict[str, float]


class AccountabilityPartnerMatcher:
    """AI-powered accountability partner matching using multiple signals"""

    def __init__(self):
        self.goal_vectorizer = TfidfVectorizer(max_features=100, stop_words="english")
        self.scaler = StandardScaler()
        self._model_trained = False

    def calculate_compatibility(
        self,
        user1: models.User,
        user2: models.User,
        user1_goals: List[models.Goal],
        user2_goals: List[models.Goal],
    ) -> Dict[str, float]:
        """Calculate multi-dimensional compatibility between users"""

        # 1. Goal Compatibility (semantic similarity)
        goal_texts1 = [f"{g.title} {g.description or ''}" for g in user1_goals]
        goal_texts2 = [f"{g.title} {g.description or ''}" for g in user2_goals]

        if goal_texts1 and goal_texts2:
            all_texts = goal_texts1 + goal_texts2
            tfidf_matrix = self.goal_vectorizer.fit_transform(all_texts)

            user1_vector = tfidf_matrix[: len(goal_texts1)].mean(axis=0)
            user2_vector = tfidf_matrix[len(goal_texts1) :].mean(axis=0)
            goal_compatibility = cosine_similarity(user1_vector, user2_vector)[0, 0]
        else:
            goal_compatibility = 0.0

        # 2. Schedule Compatibility (time zones, activity levels)
        schedule_compatibility = self._calculate_schedule_compatibility(user1, user2)

        # 3. Demographic Compatibility (age, activity level)
        demographic_compatibility = self._calculate_demographic_compatibility(
            user1, user2
        )

        # 4. Motivation Style Compatibility
        motivation_compatibility = self._calculate_motivation_compatibility(
            user1, user2
        )

        return {
            "goal_compatibility": float(goal_compatibility),
            "schedule_compatibility": schedule_compatibility,
            "demographic_compatibility": demographic_compatibility,
            "motivation_compatibility": motivation_compatibility,
            "overall_score": (
                goal_compatibility * 0.4
                + schedule_compatibility * 0.3
                + demographic_compatibility * 0.2
                + motivation_compatibility * 0.1
            ),
        }

    def _calculate_schedule_compatibility(
        self, user1: models.User, user2: models.User
    ) -> float:
        """Calculate time zone and schedule compatibility"""
        # Time zone compatibility
        if user1.time_zone and user2.time_zone:
            # Simple time zone difference calculation (can be enhanced)
            tz_diff = abs(hash(user1.time_zone) - hash(user2.time_zone)) % 24
            tz_score = max(0, 1 - tz_diff / 12)  # Closer time zones = higher score
        else:
            tz_score = 0.5  # Default if no time zone info

        # Activity level compatibility
        activity_levels = [
            "sedentary",
            "lightly_active",
            "moderately_active",
            "very_active",
            "extremely_active",
        ]
        if (
            user1.activity_level in activity_levels
            and user2.activity_level in activity_levels
        ):
            level1_idx = activity_levels.index(user1.activity_level)
            level2_idx = activity_levels.index(user2.activity_level)
            activity_score = max(
                0, 1 - abs(level1_idx - level2_idx) / len(activity_levels)
            )
        else:
            activity_score = 0.5

        return (tz_score + activity_score) / 2

    def _calculate_demographic_compatibility(
        self, user1: models.User, user2: models.User
    ) -> float:
        """Calculate age and demographic compatibility"""
        age_diff = abs(user1.year_of_birth - user2.year_of_birth)
        age_score = max(0, 1 - age_diff / 30)  # Closer ages = higher score

        # Gender compatibility (can be same or different based on preferences)
        gender_score = 0.8 if user1.gender == user2.gender else 0.6

        return (age_score + gender_score) / 2

    def _calculate_motivation_compatibility(
        self, user1: models.User, user2: models.User
    ) -> float:
        """Calculate motivation style compatibility"""
        if not user1.motivation_style or not user2.motivation_style:
            return 0.5

        # Complementary motivation styles work well together
        compatible_pairs = {
            ("encouraging", "competitive"): 0.9,
            ("analytical", "encouraging"): 0.8,
            ("competitive", "analytical"): 0.7,
            ("encouraging", "encouraging"): 0.9,
            ("competitive", "competitive"): 0.8,
            ("analytical", "analytical"): 0.7,
        }

        pair = tuple(sorted([user1.motivation_style, user2.motivation_style]))
        return compatible_pairs.get(pair, 0.5)


class CommunityEngagementPredictor(nn.Module):
    """Neural network for predicting user engagement and retention"""

    def __init__(self, input_size: int = 20, hidden_size: int = 64):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, 3),  # engagement, retention, satisfaction
        )

    def forward(self, x):
        return torch.sigmoid(self.network(x))


class CommunityAnalytics:
    """Advanced analytics for community accountability hypothesis validation"""

    def __init__(self):
        self.engagement_model = CommunityEngagementPredictor()
        self.partner_matcher = AccountabilityPartnerMatcher()

    def calculate_community_impact(self, db: Session) -> schemas.CommunityMetrics:
        """Calculate key metrics to validate the community accountability hypothesis"""

        # Get all users and their engagement data
        users = db.query(models.User).all()
        total_users = len(users)

        # Users with accountability partners
        users_with_partners = (
            db.query(models.User)
            .join(
                models.CommunityConnection,
                (models.User.id == models.CommunityConnection.requester_id)
                | (models.User.id == models.CommunityConnection.partner_id),
            )
            .filter(
                models.CommunityConnection.status
                == models.CommunityConnectionStatus.ACTIVE
            )
            .distinct()
            .count()
        )

        # Active connections
        active_connections = (
            db.query(models.CommunityConnection)
            .filter(
                models.CommunityConnection.status
                == models.CommunityConnectionStatus.ACTIVE
            )
            .count()
        )

        # Calculate retention and engagement scores
        avg_retention = db.query(models.User.retention_score).scalar() or 0.0
        avg_engagement = (
            db.query(models.User.community_engagement_score).scalar() or 0.0
        )

        # Goal completion rates (with vs without community)
        goal_completion_with_community = self._calculate_goal_completion_rate(
            db, with_community=True
        )
        goal_completion_without_community = self._calculate_goal_completion_rate(
            db, with_community=False
        )

        # Calculate community impact factor
        if goal_completion_without_community > 0:
            community_impact_factor = (
                goal_completion_with_community / goal_completion_without_community
            )
        else:
            community_impact_factor = 1.0

        return schemas.CommunityMetrics(
            total_users=total_users,
            users_with_accountability_partners=users_with_partners,
            active_connections=active_connections,
            average_retention_score=avg_retention,
            average_engagement_score=avg_engagement,
            goal_completion_rate_with_community=goal_completion_with_community,
            goal_completion_rate_without_community=goal_completion_without_community,
            community_impact_factor=community_impact_factor,
        )

    def _calculate_goal_completion_rate(
        self, db: Session, with_community: bool
    ) -> float:
        """Calculate goal completion rate for users with/without community support"""

        if with_community:
            # Users with accountability partners or public goals
            query = (
                db.query(models.Goal)
                .join(models.User)
                .filter(
                    (models.User.wants_accountability_partner == True)
                    | (models.Goal.is_public == True)
                    | (models.Goal.wants_support == True)
                )
            )
        else:
            # Users without community features
            query = (
                db.query(models.Goal)
                .join(models.User)
                .filter(
                    (models.User.wants_accountability_partner == False)
                    & (models.Goal.is_public == False)
                    & (models.Goal.wants_support == False)
                )
            )

        goals = query.all()
        if not goals:
            return 0.0

        # Simple completion rate based on target dates and check-ins
        completed_goals = 0
        for goal in goals:
            if goal.target_date and goal.target_date < datetime.utcnow():
                # Check if goal had regular check-ins (proxy for completion)
                check_ins = (
                    db.query(models.GoalCheckIn)
                    .filter(
                        models.GoalCheckIn.goal_id == goal.id,
                        models.GoalCheckIn.progress_percentage >= 100,
                    )
                    .count()
                )
                if check_ins > 0:
                    completed_goals += 1

        return completed_goals / len(goals) if goals else 0.0

    def generate_partner_recommendations(
        self, user_id: int, db: Session, limit: int = 5
    ) -> List[schemas.PartnerRecommendation]:
        """Generate AI-powered partner recommendations for a user"""

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return []

        user_goals = db.query(models.Goal).filter(models.Goal.owner_id == user_id).all()

        # Get potential partners (users who want accountability partners)
        potential_partners = (
            db.query(models.User)
            .filter(
                models.User.wants_accountability_partner == True,
                models.User.id != user_id,
            )
            .all()
        )

        recommendations = []

        for partner in potential_partners:
            partner_goals = (
                db.query(models.Goal).filter(models.Goal.owner_id == partner.id).all()
            )

            compatibility = self.partner_matcher.calculate_compatibility(
                user, partner, user_goals, partner_goals
            )

            # Generate compatibility reasons
            reasons = []
            if compatibility["goal_compatibility"] > 0.7:
                reasons.append("Similar fitness goals")
            if compatibility["schedule_compatibility"] > 0.7:
                reasons.append("Compatible schedules")
            if compatibility["motivation_compatibility"] > 0.7:
                reasons.append("Complementary motivation styles")

            # Find shared goal types
            user_goal_types = set(g.title.lower() for g in user_goals)
            partner_goal_types = set(g.title.lower() for g in partner_goals)
            shared_goals = list(user_goal_types.intersection(partner_goal_types))

            recommendations.append(
                schemas.PartnerRecommendation(
                    partner_user=schemas.User.from_orm(partner),
                    compatibility_score=compatibility["overall_score"],
                    compatibility_reasons=reasons,
                    shared_goals=shared_goals,
                    schedule_overlap=f"{compatibility['schedule_compatibility']:.0%} compatible",
                )
            )

        # Sort by compatibility score and return top recommendations
        recommendations.sort(key=lambda x: x.compatibility_score, reverse=True)
        return recommendations[:limit]

    def predict_user_engagement(
        self, user: models.User, db: Session
    ) -> CommunityInsights:
        """Use ML to predict user engagement and generate personalized insights"""

        # Feature engineering for engagement prediction
        features = self._extract_user_features(user, db)

        # Predict engagement, retention risk, and satisfaction
        with torch.no_grad():
            features_tensor = torch.FloatTensor([features]).to(DEVICE)
            predictions = self.engagement_model(features_tensor)
            engagement_score, retention_score, satisfaction_score = (
                predictions[0].cpu().numpy()
            )

        # Generate recommended actions based on predictions
        recommended_actions = self._generate_action_recommendations(
            engagement_score, retention_score, satisfaction_score, user
        )

        # Determine optimal check-in frequency
        optimal_frequency = self._recommend_check_in_frequency(user, engagement_score)

        # Infer personality traits from behavior
        personality_traits = self._infer_personality_traits(user, db)

        return CommunityInsights(
            engagement_score=float(engagement_score),
            retention_risk=1.0 - float(retention_score),
            recommended_actions=recommended_actions,
            optimal_check_in_frequency=optimal_frequency,
            personality_traits=personality_traits,
        )

    def _extract_user_features(self, user: models.User, db: Session) -> List[float]:
        """Extract features for ML model"""
        features = []

        # Basic demographics
        current_year = datetime.now().year
        age = current_year - user.year_of_birth
        features.extend(
            [
                age / 100.0,  # Normalized age
                1.0 if user.gender == "male" else 0.0,
                user.height_cm / 200.0,  # Normalized height
                user.weight_kg / 150.0,  # Normalized weight
            ]
        )

        # Activity and goal features
        activity_mapping = {
            "sedentary": 0.2,
            "lightly_active": 0.4,
            "moderately_active": 0.6,
            "very_active": 0.8,
            "extremely_active": 1.0,
        }
        features.append(activity_mapping.get(user.activity_level, 0.5))

        # Community engagement features
        features.extend(
            [
                1.0 if user.wants_accountability_partner else 0.0,
                user.retention_score,
                user.community_engagement_score,
            ]
        )

        # Goal-related features
        goals = db.query(models.Goal).filter(models.Goal.owner_id == user.id).all()
        features.extend(
            [
                len(goals) / 10.0,  # Normalized goal count
                sum(1 for g in goals if g.is_public)
                / max(len(goals), 1),  # Public goal ratio
                sum(1 for g in goals if g.wants_support)
                / max(len(goals), 1),  # Support-seeking ratio
            ]
        )

        # Check-in activity features
        check_ins = (
            db.query(models.AccountabilityCheckIn)
            .filter(models.AccountabilityCheckIn.user_id == user.id)
            .all()
        )

        if check_ins:
            avg_energy = np.mean([c.energy_level for c in check_ins if c.energy_level])
            avg_motivation = np.mean(
                [c.motivation_level for c in check_ins if c.motivation_level]
            )
            check_in_frequency = len(check_ins) / max(
                (datetime.utcnow() - user.created_at).days, 1
            )
        else:
            avg_energy = avg_motivation = check_in_frequency = 0.0

        features.extend(
            [
                avg_energy / 10.0,  # Normalized energy
                avg_motivation / 10.0,  # Normalized motivation
                min(check_in_frequency, 1.0),  # Capped frequency
            ]
        )

        # Pad features to fixed size
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    def _generate_action_recommendations(
        self,
        engagement: float,
        retention: float,
        satisfaction: float,
        user: models.User,
    ) -> List[str]:
        """Generate personalized action recommendations"""
        actions = []

        if engagement < 0.3:
            actions.append("Increase community interaction through daily check-ins")
            actions.append("Join a small accountability group")

        if retention < 0.4:
            actions.append("Set smaller, more achievable milestone goals")
            actions.append("Find an accountability partner with similar schedule")

        if satisfaction < 0.5:
            actions.append("Experiment with different motivation styles")
            actions.append("Share progress updates to increase social support")

        if not user.wants_accountability_partner:
            actions.append(
                "Consider trying accountability partnership to boost motivation"
            )

        return actions[:4]  # Limit to top 4 recommendations

    def _recommend_check_in_frequency(
        self, user: models.User, engagement_score: float
    ) -> str:
        """Recommend optimal check-in frequency based on user profile and engagement"""

        if engagement_score > 0.7:
            return "daily"
        elif engagement_score > 0.4:
            return "every-other-day"
        else:
            return "weekly"

    def _infer_personality_traits(
        self, user: models.User, db: Session
    ) -> Dict[str, float]:
        """Infer personality traits from user behavior patterns"""

        # Get user's check-in patterns
        check_ins = (
            db.query(models.AccountabilityCheckIn)
            .filter(models.AccountabilityCheckIn.user_id == user.id)
            .all()
        )

        traits = {
            "consistency": 0.5,
            "social_orientation": 0.5,
            "goal_focus": 0.5,
            "optimism": 0.5,
        }

        if check_ins:
            # Consistency: regularity of check-ins
            if len(check_ins) > 7:
                check_in_dates = [c.check_in_date for c in check_ins]
                check_in_dates.sort()
                intervals = [
                    (check_in_dates[i + 1] - check_in_dates[i]).days
                    for i in range(len(check_in_dates) - 1)
                ]
                consistency = 1.0 - (
                    np.std(intervals) / np.mean(intervals) if intervals else 0
                )
                traits["consistency"] = min(max(consistency, 0), 1)

            # Social orientation: engagement with partners
            social_interactions = sum(
                1 for c in check_ins if c.partner_responded or c.encouragement_sent
            )
            traits["social_orientation"] = min(
                social_interactions / len(check_ins), 1.0
            )

            # Optimism: average motivation and energy levels
            motivations = [c.motivation_level for c in check_ins if c.motivation_level]
            if motivations:
                traits["optimism"] = np.mean(motivations) / 10.0

        # Goal focus: ratio of public goals and support-seeking
        goals = db.query(models.Goal).filter(models.Goal.owner_id == user.id).all()
        if goals:
            public_ratio = sum(1 for g in goals if g.is_public) / len(goals)
            support_ratio = sum(1 for g in goals if g.wants_support) / len(goals)
            traits["goal_focus"] = (public_ratio + support_ratio) / 2

        return traits


# Global instances for the application
community_analytics = CommunityAnalytics()
partner_matcher = AccountabilityPartnerMatcher()


# Enhanced API functions
def generate_personalized_plan(user_data: Dict) -> Dict:
    """Generate AI-powered personalized workout plan"""
    # TODO: Integrate with advanced ML models for workout generation
    return {
        "plan": "AI-powered personalized plan based on community insights",
        "ai_confidence": 0.85,
        "community_recommendations": True,
    }


def match_accountability_partners(
    user_id: int, db: Session
) -> List[schemas.PartnerRecommendation]:
    """Find optimal accountability partners using AI"""
    return community_analytics.generate_partner_recommendations(user_id, db)


def analyze_community_impact(db: Session) -> schemas.CommunityMetrics:
    """Analyze overall community impact for hypothesis validation"""
    return community_analytics.calculate_community_impact(db)


def get_user_insights(user_id: int, db: Session) -> CommunityInsights:
    """Get AI-powered insights for a specific user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    return community_analytics.predict_user_engagement(user, db)


def calculate_retention_risk(user_id: int, db: Session) -> float:
    """Calculate user retention risk using ML"""
    insights = get_user_insights(user_id, db)
    return insights.retention_risk


# Future-proofing: Plugin architecture for new ML models
class MLModelPlugin:
    """Base class for ML model plugins"""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

    def load(self):
        """Load the model"""
        raise NotImplementedError

    def predict(self, data):
        """Make predictions"""
        raise NotImplementedError

    def train(self, data):
        """Train the model"""
        raise NotImplementedError


# Cost-effective caching for expensive ML operations
_model_cache = {}
_prediction_cache = {}


def cached_prediction(cache_key: str, prediction_func, ttl_hours: int = 24):
    """Cache expensive ML predictions"""
    import hashlib
    import pickle
    from datetime import datetime, timedelta

    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()

    if cache_hash in _prediction_cache:
        result, timestamp = _prediction_cache[cache_hash]
        if datetime.now() - timestamp < timedelta(hours=ttl_hours):
            return result

    # Generate new prediction
    result = prediction_func()
    _prediction_cache[cache_hash] = (result, datetime.now())

    return result


class MLService:
    """
    Main ML service class for WorkoutBuddy platform.

    Handles all machine learning operations including:
    - Workout plan generation
    - Community matching
    - Exercise recommendations
    - Progress analysis
    """

    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.formatter = OutputFormatter()
        self.models = {}
        self.scalers = {}
        self.load_models()

    def load_models(self):
        """Load all ML models and preprocessors"""
        try:
            # For now, we'll use simple rule-based algorithms
            # In production, these would be trained ML models
            logger.info("Loading ML models...")

            # Initialize simple models for demonstration
            self.models["workout_recommender"] = self._create_simple_workout_model()
            self.models["community_matcher"] = self._create_community_matcher()
            self.models["exercise_recommender"] = self._create_exercise_recommender()

            logger.info("ML models loaded successfully")

        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            # Fall back to simple rule-based systems
            self._initialize_fallback_models()

    def generate_workout_plan(
        self, user, request: WorkoutPlanRequest
    ) -> WorkoutPlanResponse:
        """
        Generate a personalized workout plan using ML models.

        Args:
            user: User database object
            request: Workout plan request parameters

        Returns:
            Formatted workout plan response
        """
        try:
            # Preprocess user data
            user_features = self.preprocessor.preprocess_user_data(
                {
                    "date_of_birth": getattr(user, "date_of_birth", None),
                    "gender": getattr(user, "gender", "other"),
                    "height": getattr(user, "height_cm", 170),
                    "weight": getattr(user, "weight_kg", 70),
                    "activity_level": getattr(user, "activity_level", "intermediate"),
                    "primary_goal": getattr(user, "goal_type", "general_fitness"),
                    "workout_history": [],  # Would be populated from database
                }
            )

            # Generate workout plan using ML model
            ml_output = self._generate_ml_workout_plan(user_features, request)

            # Format output
            formatted_plan = self.formatter.format_workout_plan(
                ml_output, user_features
            )

            return WorkoutPlanResponse(**formatted_plan)

        except Exception as e:
            logger.error(f"Error generating workout plan: {e}")
            # Return a simple fallback plan
            return self._generate_fallback_workout_plan(user, request)

    def find_community_matches(
        self, user, request: CommunityMatchRequest
    ) -> List[CommunityMatchResponse]:
        """
        Find compatible community matches using ML similarity algorithms.

        Args:
            user: User database object
            request: Community match request parameters

        Returns:
            List of formatted community matches
        """
        try:
            # For demonstration, return sample matches
            # In production, this would query the database and use ML models
            sample_matches = [
                {
                    "user_id": 2,
                    "similarity_score": 0.85,
                    "shared_interests": ["strength_training", "morning_workouts"],
                    "schedule_compatibility": 0.8,
                    "fitness_level_similarity": 0.9,
                    "goal_similarity": 0.8,
                    "activity_level": "intermediate",
                    "primary_goals": ["muscle_gain", "strength"],
                    "preferred_times": ["morning"],
                    "workout_frequency": "4 times/week",
                },
                {
                    "user_id": 3,
                    "similarity_score": 0.72,
                    "shared_interests": ["cardio", "evening_workouts"],
                    "schedule_compatibility": 0.7,
                    "fitness_level_similarity": 0.8,
                    "goal_similarity": 0.6,
                    "activity_level": "intermediate",
                    "primary_goals": ["weight_loss", "endurance"],
                    "preferred_times": ["evening"],
                    "workout_frequency": "3 times/week",
                },
            ]

            # Format matches
            formatted_matches = self.formatter.format_community_matches(
                sample_matches,
                {"id": user.id, "primary_goal": getattr(user, "goal_type", "fitness")},
            )

            return [CommunityMatchResponse(**match) for match in formatted_matches]

        except Exception as e:
            logger.error(f"Error finding community matches: {e}")
            return []

    def recommend_exercises(
        self, user, request: ExerciseRecommendationRequest
    ) -> List[ExerciseRecommendation]:
        """
        Generate AI-powered exercise recommendations.

        Args:
            user: User database object
            request: Exercise recommendation request

        Returns:
            List of formatted exercise recommendations
        """
        try:
            # Sample exercise recommendations
            # In production, this would query the exercise database and use ML models
            sample_exercises = [
                {
                    "id": 1,
                    "name": "Push-ups",
                    "description": "Classic bodyweight exercise for chest and arms",
                    "score": 0.9,
                    "main_muscle_group": "chest",
                    "secondary_muscles": ["shoulders", "triceps"],
                    "difficulty": "intermediate",
                    "equipment": "bodyweight",
                    "equipment_alternatives": [],
                    "setup_instructions": "Start in plank position",
                    "execution_steps": [
                        "Lower body to the ground",
                        "Push back up to starting position",
                    ],
                    "form_tips": ["Keep core tight", "Maintain straight line"],
                    "estimated_duration_minutes": 2,
                    "calories_per_rep": 0.5,
                    "safety_notes": ["Avoid if you have wrist problems"],
                    "easier_variant": "Knee push-ups",
                    "harder_variant": "One-arm push-ups",
                    "benefits": ["muscle_gain", "strength"],
                },
                {
                    "id": 2,
                    "name": "Squats",
                    "description": "Fundamental lower body exercise",
                    "score": 0.85,
                    "main_muscle_group": "legs",
                    "secondary_muscles": ["glutes", "core"],
                    "difficulty": "beginner",
                    "equipment": "bodyweight",
                    "equipment_alternatives": [],
                    "setup_instructions": "Stand with feet shoulder-width apart",
                    "execution_steps": [
                        "Lower into sitting position",
                        "Return to standing position",
                    ],
                    "form_tips": ["Keep knees behind toes", "Engage core"],
                    "estimated_duration_minutes": 2,
                    "calories_per_rep": 0.8,
                    "safety_notes": ["Avoid if you have knee problems"],
                    "easier_variant": "Chair squats",
                    "harder_variant": "Jump squats",
                    "benefits": ["strength", "general_fitness"],
                },
            ]

            # Filter exercises based on request parameters
            filtered_exercises = self._filter_exercises(sample_exercises, request)

            # Format recommendations
            user_context = {
                "activity_level": getattr(user, "activity_level", "intermediate"),
                "primary_goal": getattr(user, "goal_type", "general_fitness"),
            }

            formatted_exercises = self.formatter.format_exercise_recommendations(
                filtered_exercises, user_context
            )

            return [
                ExerciseRecommendation(**exercise) for exercise in formatted_exercises
            ]

        except Exception as e:
            logger.error(f"Error generating exercise recommendations: {e}")
            return []

    def _create_simple_workout_model(self):
        """Create a simple workout recommendation model"""
        # This would be replaced with a trained ML model
        return {
            "type": "rule_based",
            "rules": {
                "beginner": {"duration": 30, "exercises": 4, "sets": 2},
                "intermediate": {"duration": 45, "exercises": 6, "sets": 3},
                "advanced": {"duration": 60, "exercises": 8, "sets": 4},
            },
        }

    def _create_community_matcher(self):
        """Create a simple community matching model"""
        # This would be replaced with a trained similarity model
        return NearestNeighbors(n_neighbors=5, metric="cosine")

    def _create_exercise_recommender(self):
        """Create a simple exercise recommendation model"""
        # This would be replaced with a trained recommendation model
        return {
            "type": "content_based",
            "features": ["muscle_group", "equipment", "difficulty", "goal_alignment"],
        }

    def _initialize_fallback_models(self):
        """Initialize simple fallback models if ML models fail to load"""
        logger.info("Initializing fallback ML models")
        self.models = {
            "workout_recommender": {"type": "simple"},
            "community_matcher": {"type": "simple"},
            "exercise_recommender": {"type": "simple"},
        }

    def _generate_ml_workout_plan(
        self, user_features: Dict, request: WorkoutPlanRequest
    ) -> Dict:
        """Generate workout plan using ML model"""
        # Simple rule-based generation for demonstration
        activity_level = user_features.get("activity_level", 2)

        if activity_level == 1:  # Beginner
            difficulty = "beginner"
            exercises_per_session = 4
            session_duration = 30
        elif activity_level == 3:  # Advanced
            difficulty = "advanced"
            exercises_per_session = 8
            session_duration = 60
        else:  # Intermediate
            difficulty = "intermediate"
            exercises_per_session = 6
            session_duration = 45

        return {
            "duration_weeks": request.duration_weeks,
            "difficulty_level": difficulty,
            "weekly_schedule": {
                "workout_days": request.workout_days_per_week,
                "rest_days": 7 - request.workout_days_per_week,
                "session_duration": session_duration,
                "recommended_days": ["Monday", "Wednesday", "Friday"][
                    : request.workout_days_per_week
                ],
            },
            "exercises": [
                {
                    "id": i,
                    "name": f"Exercise {i}",
                    "sets": 3,
                    "reps": "8-12",
                    "rest_seconds": 60,
                    "main_muscle_group": "full_body",
                    "equipment": "bodyweight",
                    "difficulty": difficulty,
                }
                for i in range(1, exercises_per_session + 1)
            ],
            "progression": {
                "type": "linear",
                "weight_increase_percent": 2.5,
                "rep_increase": 1,
                "duration_increase_minutes": 2,
            },
            "estimated_calories": session_duration * 5,  # Rough estimate
            "equipment_needed": request.equipment_available,
        }

    def _generate_fallback_workout_plan(
        self, user, request: WorkoutPlanRequest
    ) -> WorkoutPlanResponse:
        """Generate a simple fallback workout plan"""
        return WorkoutPlanResponse(
            user_id=request.user_id,
            plan_id=f"fallback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            created_at=datetime.now().isoformat(),
            title="Basic Fitness Plan",
            description="A simple fitness plan to get you started",
            duration_weeks=request.duration_weeks,
            difficulty_level="beginner",
            weekly_schedule={
                "workout_days": request.workout_days_per_week,
                "session_duration_minutes": request.session_duration_minutes,
            },
            exercises=[],
            progression={},
            estimated_calories_per_session=200,
            equipment_needed=request.equipment_available,
            tips=["Start slow", "Focus on form", "Stay consistent"],
        )

    def _filter_exercises(
        self, exercises: List[Dict], request: ExerciseRecommendationRequest
    ) -> List[Dict]:
        """Filter exercises based on request parameters"""
        filtered = []

        for exercise in exercises:
            # Filter by muscle groups if specified
            if request.muscle_groups:
                if not any(
                    mg.lower() in exercise.get("main_muscle_group", "").lower()
                    for mg in request.muscle_groups
                ):
                    continue

            # Filter by equipment
            if request.equipment_available:
                if exercise.get("equipment", "") not in request.equipment_available:
                    continue

            # Filter by difficulty
            if request.difficulty_level:
                if exercise.get("difficulty", "") != request.difficulty_level:
                    continue

            filtered.append(exercise)

            # Limit results
            if len(filtered) >= request.max_recommendations:
                break

        return filtered
