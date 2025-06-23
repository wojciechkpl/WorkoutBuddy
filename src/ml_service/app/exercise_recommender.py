# backend/app/ml/ExerciseRecommender.py
"""
Exercise recommendation model based on user preferences and similar users

This model uses metric units internally for all calculations to ensure consistency.
"""

import logging
from typing import Optional

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import User
from app.user_similarity_model import UserSimilarityModel

logger = logging.getLogger(__name__)


class ExerciseRecommender:
    """
    Recommends exercises based on:
    - User's workout history
    - Similar users' preferences
    - Muscle group balance

    All calculations use metric units for consistency.
    """

    def __init__(self):
        self.user_similarity_model = None

    @classmethod
    def load_or_initialize(cls):
        """Load or initialize the recommender"""
        instance = cls()
        instance.user_similarity_model = UserSimilarityModel()
        return instance

    def get_recommendations(
        self,
        user: User,
        db: Session,
        n_recommendations: int = 10,
        workout_type: Optional[str] = None,
    ) -> list[dict]:
        """Get personalized exercise recommendations using metric data"""

        try:
            # Get all exercises
            result = db.execute(text("SELECT * FROM exercises"))
            exercises_data = result.fetchall()

            if not exercises_data:
                return []

            recommendations = []

            for exercise_data in exercises_data:
                # Create exercise dict
                exercise = {
                    "id": exercise_data.id,
                    "name": exercise_data.name,
                    "description": exercise_data.description,
                    "muscle_group": exercise_data.muscle_group,
                    "equipment": exercise_data.equipment,
                    "difficulty_level": exercise_data.difficulty_level,
                    "instructions": exercise_data.instructions,
                }

                # Calculate score based on user preferences
                score = self._calculate_exercise_score(exercise, user, db, workout_type)

                recommendations.append(
                    {
                        **exercise,
                        "score": score,
                        "reasoning": self._get_recommendation_reasoning(
                            exercise, user, score
                        ),
                    }
                )

            # Sort by score and return top N
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            return recommendations[:n_recommendations]

        except Exception as e:
            logger.error(f"Error getting exercise recommendations: {e}")
            return []

    def _calculate_exercise_score(
        self,
        exercise: dict,
        user: User,
        db: Session,
        workout_type: Optional[str] = None,
    ) -> float:
        """Calculate score for an exercise based on user preferences using metric data"""
        score = 0.0

        try:
            # 1. Match fitness goal
            if user.fitness_goal:
                if user.fitness_goal == "strength" and exercise["muscle_group"] in [
                    "chest",
                    "back",
                    "legs",
                ]:
                    score += 0.3
                elif (
                    user.fitness_goal == "weight_loss"
                    and exercise["equipment"] == "Bodyweight"
                ):
                    score += 0.2
                elif user.fitness_goal == "muscle_gain" and exercise[
                    "muscle_group"
                ] in ["chest", "back", "shoulders"]:
                    score += 0.3

            # 2. Match experience level
            if user.experience_level:
                if (
                    user.experience_level == "beginner"
                    and exercise["difficulty_level"] == "Beginner"
                ):
                    score += 0.2
                elif user.experience_level == "intermediate" and exercise[
                    "difficulty_level"
                ] in ["Beginner", "Intermediate"]:
                    score += 0.2
                elif user.experience_level == "advanced":
                    score += 0.1

            # 3. Check if user has done this exercise before (preference)
            # Use metric view for consistency
            try:
                result = db.execute(
                    text(
                        """
                    SELECT COUNT(*) as count
                    FROM workout_exercises_metric we
                    JOIN workouts w ON we.workout_id = w.id
                    WHERE w.user_id = :user_id AND we.exercise_id = :exercise_id
                """
                    ),
                    {"user_id": user.id, "exercise_id": exercise["id"]},
                )
            except Exception as e:
                logger.warning(
                    f"Error using metric view, falling back to regular table: {e}"
                )
                result = db.execute(
                    text(
                        """
                    SELECT COUNT(*) as count
                    FROM workout_exercises we
                    JOIN workouts w ON we.workout_id = w.id
                    WHERE w.user_id = :user_id AND we.exercise_id = :exercise_id
                """
                    ),
                    {"user_id": user.id, "exercise_id": exercise["id"]},
                )

            exercise_count = result.fetchone().count
            if exercise_count > 0:
                score += min(exercise_count * 0.1, 0.3)  # Cap at 0.3

            # 4. Muscle group balance (avoid overworking same muscle)
            if exercise["muscle_group"]:
                try:
                    result = db.execute(
                        text(
                            """
                        SELECT COUNT(*) as count
                        FROM workout_exercises_metric we
                        JOIN workouts w ON we.workout_id = w.id
                        JOIN exercises e ON we.exercise_id = e.id
                        WHERE w.user_id = :user_id
                        AND e.muscle_group = :muscle_group
                        AND w.created_at >= NOW() - INTERVAL '7 days'
                    """
                        ),
                        {"user_id": user.id, "muscle_group": exercise["muscle_group"]},
                    )
                except Exception as e:
                    logger.warning(
                        f"Error using metric view for muscle balance, falling back: {e}"
                    )
                    result = db.execute(
                        text(
                            """
                        SELECT COUNT(*) as count
                        FROM workout_exercises we
                        JOIN workouts w ON we.workout_id = w.id
                        JOIN exercises e ON we.exercise_id = e.id
                        WHERE w.user_id = :user_id
                        AND e.muscle_group = :muscle_group
                        AND w.created_at >= NOW() - INTERVAL '7 days'
                    """
                        ),
                        {"user_id": user.id, "muscle_group": exercise["muscle_group"]},
                    )

                recent_count = result.fetchone().count
                if recent_count > 3:  # If worked this muscle group recently
                    score -= 0.2

            # 5. Consider user's physical metrics (using metric units)
            if hasattr(user, "get_height_cm") and hasattr(user, "get_weight_kg"):
                height_cm = user.get_height_cm()
                weight_kg = user.get_weight_kg()

                if height_cm and weight_kg:
                    # Adjust score based on user's physical characteristics
                    # For example, heavier users might prefer certain exercises
                    if weight_kg > 80 and exercise["equipment"] == "Bodyweight":
                        score += 0.1  # Bodyweight exercises good for heavier users

                    # Height considerations for certain exercises
                    if height_cm > 180 and exercise["muscle_group"] == "legs":
                        score += 0.05  # Taller users might benefit from leg exercises

            # 6. Random factor for variety
            score += np.random.random() * 0.1

        except Exception as e:
            logger.error(f"Error calculating exercise score: {e}")

        return max(score, 0.0)  # Ensure non-negative

    def _get_recommendation_reasoning(
        self, exercise: dict, user: User, score: float
    ) -> str:
        """Generate reasoning for recommendation"""
        reasons = []

        if user.fitness_goal:
            if user.fitness_goal == "strength" and exercise["muscle_group"] in [
                "chest",
                "back",
                "legs",
            ]:
                reasons.append("Great for strength building")
            elif (
                user.fitness_goal == "weight_loss"
                and exercise["equipment"] == "Bodyweight"
            ):
                reasons.append("Effective for weight loss")
            elif user.fitness_goal == "muscle_gain" and exercise["muscle_group"] in [
                "chest",
                "back",
                "shoulders",
            ]:
                reasons.append("Excellent for muscle growth")

        if user.experience_level:
            if (
                user.experience_level == "beginner"
                and exercise["difficulty_level"] == "Beginner"
            ):
                reasons.append("Perfect for beginners")
            elif user.experience_level == "intermediate" and exercise[
                "difficulty_level"
            ] in ["Beginner", "Intermediate"]:
                reasons.append("Suitable for your experience level")

        # Add physical characteristics reasoning
        if hasattr(user, "get_height_cm") and hasattr(user, "get_weight_kg"):
            height_cm = user.get_height_cm()
            weight_kg = user.get_weight_kg()

            if height_cm and weight_kg:
                if weight_kg > 80 and exercise["equipment"] == "Bodyweight":
                    reasons.append("Good for your body weight")
                if height_cm > 180 and exercise["muscle_group"] == "legs":
                    reasons.append("Beneficial for your height")

        if score > 0.5:
            reasons.append("High recommendation score")
        elif score > 0.3:
            reasons.append("Good match for your profile")
        else:
            reasons.append("Good variety exercise")

        return "; ".join(reasons) if reasons else "Recommended based on your profile"

    def _build_features(self):
        """Build features for the recommender using metric data"""
        logger.info("Building exercise recommender features with metric units...")
        # This would typically involve feature engineering with metric units
        # For now, just log that it's called
        pass
