"""
Exercise Recommender Model - Stateless implementation
"""

import os
from typing import Any

import joblib
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF


class ExerciseRecommender:
    """
    Stateless exercise recommender using matrix factorization
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.model = None
        self.user_ids = None
        self.exercise_ids = None
        self.user_mapping = None
        self.exercise_mapping = None
        self.is_fitted = False

    def fit(
        self,
        interaction_matrix: csr_matrix,
        user_ids: list[int],
        exercise_ids: list[int],
    ) -> None:
        """
        Fit the model with user-exercise interaction matrix

        Args:
            interaction_matrix: Sparse matrix of shape (n_users, n_exercises)
            user_ids: List of user IDs corresponding to rows
            exercise_ids: List of exercise IDs corresponding to columns
        """
        self.user_ids = user_ids
        self.exercise_ids = exercise_ids

        # Create mappings for easy lookup
        self.user_mapping = {uid: idx for idx, uid in enumerate(user_ids)}
        self.exercise_mapping = {eid: idx for idx, eid in enumerate(exercise_ids)}

        # Initialize and fit NMF model
        n_factors = self.config.get("n_factors", 50)
        self.model = NMF(
            n_components=n_factors,
            max_iter=self.config.get("n_epochs", 20),
            alpha=self.config.get("regularization", 0.1),
            random_state=42,
        )

        # Fit the model
        self.model.fit(interaction_matrix)
        self.is_fitted = True

    def recommend_exercises(
        self, user_id: int, user_interactions: np.ndarray, n_recommendations: int = None
    ) -> list[tuple[int, float]]:
        """
        Recommend exercises for a user

        Args:
            user_id: ID of the target user
            user_interactions: Vector of user's interactions with exercises
            n_recommendations: Number of recommendations to return

        Returns:
            List of tuples (exercise_id, predicted_rating)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if n_recommendations is None:
            n_recommendations = self.config.get("max_recommendations", 20)

        # Get user index
        if user_id not in self.user_mapping:
            return []

        user_idx = self.user_mapping[user_id]

        # Predict ratings for all exercises
        predicted_ratings = self.model.transform(user_interactions.reshape(1, -1))
        predicted_ratings = predicted_ratings @ self.model.components_

        # Create exercise-rating pairs
        exercise_ratings = list(zip(self.exercise_ids, predicted_ratings[0]))

        # Filter out exercises the user has already interacted with
        # (assuming interactions > 0 means user has done the exercise)
        filtered_ratings = [
            (eid, rating)
            for eid, rating in exercise_ratings
            if user_interactions[self.exercise_mapping[eid]] == 0
        ]

        # Sort by predicted rating and return top N
        filtered_ratings.sort(key=lambda x: x[1], reverse=True)
        return filtered_ratings[:n_recommendations]

    def get_exercise_similarity_matrix(self) -> np.ndarray:
        """
        Get exercise similarity matrix based on learned factors

        Returns:
            Similarity matrix of shape (n_exercises, n_exercises)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting similarity matrix")

        # Use the learned exercise factors to compute similarities
        exercise_factors = self.model.components_.T  # Shape: (n_exercises, n_factors)
        similarities = np.dot(exercise_factors, exercise_factors.T)

        # Normalize
        norms = np.linalg.norm(exercise_factors, axis=1, keepdims=True)
        similarities = similarities / (norms * norms.T)

        return similarities

    def get_user_factors(self, user_id: int) -> np.ndarray:
        """
        Get learned user factors for a specific user

        Args:
            user_id: ID of the user

        Returns:
            User factor vector
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting user factors")

        if user_id not in self.user_mapping:
            raise ValueError(f"User {user_id} not found in training data")

        user_idx = self.user_mapping[user_id]
        return self.model.components_[:, user_idx]

    def save_model(self, filepath: str) -> None:
        """Save the fitted model"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")

        model_data = {
            "model": self.model,
            "user_ids": self.user_ids,
            "exercise_ids": self.exercise_ids,
            "user_mapping": self.user_mapping,
            "exercise_mapping": self.exercise_mapping,
            "config": self.config,
        }
        joblib.dump(model_data, filepath)

    def load_model(self, filepath: str) -> None:
        """Load a fitted model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        model_data = joblib.load(filepath)
        self.model = model_data["model"]
        self.user_ids = model_data["user_ids"]
        self.exercise_ids = model_data["exercise_ids"]
        self.user_mapping = model_data["user_mapping"]
        self.exercise_mapping = model_data["exercise_mapping"]
        self.config = model_data["config"]
        self.is_fitted = True
