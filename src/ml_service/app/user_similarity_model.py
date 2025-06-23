# backend/app/ml/user_similarity.py
"""
User similarity model for finding similar users based on goals and workout patterns

This model uses metric units internally for all calculations to ensure consistency.
"""

import logging
import os

import joblib
import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)


class UserSimilarityModel:
    """
    ML model for finding similar users based on:
    - Fitness goals
    - Experience level
    - Workout patterns

    All calculations use metric units for consistency.
    """

    MODEL_PATH = os.path.join(settings.ML_MODEL_PATH, "user_similarity_model.pkl")

    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=5)
        self.user_features = {}

    def extract_user_features(self, user: User, db: Session) -> np.ndarray:
        """Extract feature vector for a user using metric units"""
        features = []

        # Basic profile features (always in metric units)
        # Use the metric conversion methods to ensure we get metric values
        height_cm = (
            user.get_height_cm() if hasattr(user, "get_height_cm") else user.height_cm
        )
        weight_kg = (
            user.get_weight_kg() if hasattr(user, "get_weight_kg") else user.weight_kg
        )

        features.extend(
            [
                height_cm or 170.0,  # Default height in cm
                weight_kg or 70.0,  # Default weight in kg
                1 if user.fitness_goal == "weight_loss" else 0,
                1 if user.fitness_goal == "muscle_gain" else 0,
                1 if user.fitness_goal == "strength" else 0,
                1 if user.fitness_goal == "endurance" else 0,
                1 if user.experience_level == "beginner" else 0,
                1 if user.experience_level == "intermediate" else 0,
                1 if user.experience_level == "advanced" else 0,
            ]
        )

        # Workout pattern features - using metric views for consistency
        try:
            # Get workout count
            result = db.execute(
                text(
                    """
                SELECT COUNT(*) as workout_count
                FROM workouts
                WHERE user_id = :user_id
            """
                ),
                {"user_id": user.id},
            )
            workout_count = result.fetchone().workout_count
            features.append(workout_count)

            # Get average workout duration (in minutes)
            result = db.execute(
                text(
                    """
                SELECT AVG(total_duration) as avg_duration
                FROM workouts
                WHERE user_id = :user_id AND total_duration IS NOT NULL
            """
                ),
                {"user_id": user.id},
            )
            avg_duration = result.fetchone().avg_duration or 0
            features.append(avg_duration)

            # Get total weight lifted (in kg from metric view)
            result = db.execute(
                text(
                    """
                SELECT COALESCE(SUM(total_weight_lifted_kg), 0) as total_weight
                FROM user_stats_metric
                WHERE user_id = :user_id
            """
                ),
                {"user_id": user.id},
            )
            total_weight_lifted = result.fetchone().total_weight or 0
            features.append(total_weight_lifted)

            # Get total cardio distance (in km from metric view)
            result = db.execute(
                text(
                    """
                SELECT COALESCE(SUM(total_cardio_distance_km), 0) as total_distance
                FROM user_stats_metric
                WHERE user_id = :user_id
            """
                ),
                {"user_id": user.id},
            )
            total_cardio_distance = result.fetchone().total_distance or 0
            features.append(total_cardio_distance)

        except Exception as e:
            logger.error(f"Error getting workout features: {e}")
            features.extend([0, 0, 0, 0])

        return np.array(features)

    def train(self, db: Session = None):
        """Train the similarity model using metric data"""
        logger.info("Training user similarity model with metric units...")

        if not db:
            logger.warning("No database session provided for training")
            return

        # Get all users from metric view to ensure consistent units
        try:
            result = db.execute(text("SELECT * FROM users_metric"))
            users_data = result.fetchall()
        except Exception as e:
            logger.error(f"Error getting users from metric view: {e}")
            # Fallback to regular users table
            try:
                result = db.execute(text("SELECT * FROM users"))
                users_data = result.fetchall()
            except Exception as e2:
                logger.error(f"Error getting users from regular table: {e2}")
                return

        if len(users_data) < 3:
            logger.warning("Not enough users to train similarity model")
            return

        # Extract features for all users
        feature_matrix = []
        user_ids = []

        for user_data in users_data:
            try:
                # Create User object from database row
                # Use metric values from the view or convert if using regular table
                user = User(
                    id=user_data.id,
                    username=user_data.username,
                    email=user_data.email,
                    fitness_goal=getattr(user_data, "fitness_goal", None),
                    experience_level=getattr(user_data, "experience_level", None),
                    height_cm=getattr(
                        user_data, "height_cm", None
                    ),  # Already in cm from metric view
                    weight_kg=getattr(
                        user_data, "weight_kg", None
                    ),  # Already in kg from metric view
                )

                features = self.extract_user_features(user, db)
                feature_matrix.append(features)
                user_ids.append(user.id)
                self.user_features[user.id] = features
            except Exception as e:
                logger.error(f"Error extracting features for user {user_data.id}: {e}")

        if len(feature_matrix) < 3:
            logger.warning("Not enough valid user features")
            return

        # Fit scaler
        feature_matrix = np.array(feature_matrix)
        self.scaler.fit(feature_matrix)

        # Save model
        self.save_model()
        logger.info(
            f"User similarity model trained with {len(users_data)} users using metric units"
        )

    def find_similar_users(self, user: User, db: Session, limit: int = 5) -> list[dict]:
        """Find similar users using metric units"""
        try:
            user_features = self.extract_user_features(user, db)
            user_features_scaled = self.scaler.transform([user_features])

            # Get all other users from metric view
            try:
                result = db.execute(
                    text("SELECT * FROM users_metric WHERE id != :user_id"),
                    {"user_id": user.id},
                )
                other_users_data = result.fetchall()
            except Exception as e:
                logger.warning(
                    f"Error getting users from metric view, falling back to regular table: {e}"
                )
                result = db.execute(
                    text("SELECT * FROM users WHERE id != :user_id"),
                    {"user_id": user.id},
                )
                other_users_data = result.fetchall()

            similarities = []

            for other_user_data in other_users_data:
                try:
                    other_user = User(
                        id=other_user_data.id,
                        username=other_user_data.username,
                        email=other_user_data.email,
                        fitness_goal=getattr(other_user_data, "fitness_goal", None),
                        experience_level=getattr(
                            other_user_data, "experience_level", None
                        ),
                        height_cm=getattr(
                            other_user_data, "height_cm", None
                        ),  # Already in cm from metric view
                        weight_kg=getattr(
                            other_user_data, "weight_kg", None
                        ),  # Already in kg from metric view
                    )

                    other_features = self.extract_user_features(other_user, db)
                    other_features_scaled = self.scaler.transform([other_features])

                    # Calculate cosine similarity
                    similarity = cosine_similarity(
                        user_features_scaled, other_features_scaled
                    )[0][0]
                    similarities.append(
                        {
                            "user_id": other_user.id,
                            "username": other_user.username,
                            "similarity_score": float(similarity),
                            "fitness_goal": other_user.fitness_goal,
                            "experience_level": other_user.experience_level,
                        }
                    )
                except Exception as e:
                    logger.error(
                        f"Error calculating similarity for user {other_user_data.id}: {e}"
                    )

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similarities[:limit]

        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []

    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
            joblib.dump(
                {
                    "scaler": self.scaler,
                    "pca": self.pca,
                    "user_features": self.user_features,
                },
                self.MODEL_PATH,
            )
            logger.info(f"User similarity model saved to {self.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.MODEL_PATH):
                model_data = joblib.load(self.MODEL_PATH)
                self.scaler = model_data["scaler"]
                self.pca = model_data["pca"]
                self.user_features = model_data["user_features"]
                logger.info(f"User similarity model loaded from {self.MODEL_PATH}")
                return True
            else:
                logger.warning(f"Model file not found: {self.MODEL_PATH}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
