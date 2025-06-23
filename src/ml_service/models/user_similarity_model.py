"""
User Similarity Model - Stateless implementation
"""

import os
from typing import Any

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class UserSimilarityModel:
    """
    Stateless user similarity model that works with feature vectors
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.scaler = StandardScaler()
        self.user_features = None
        self.user_ids = None
        self.is_fitted = False

    def fit(self, user_features: np.ndarray, user_ids: list[int]) -> None:
        """
        Fit the model with user feature vectors

        Args:
            user_features: Array of shape (n_users, n_features)
            user_ids: List of user IDs corresponding to features
        """
        self.user_features = self.scaler.fit_transform(user_features)
        self.user_ids = user_ids
        self.is_fitted = True

    def find_similar_users(
        self, user_features: np.ndarray, user_id: int, n_recommendations: int = None
    ) -> list[tuple[int, float]]:
        """
        Find similar users based on feature vectors

        Args:
            user_features: Feature vector for the target user
            user_id: ID of the target user
            n_recommendations: Number of similar users to return

        Returns:
            List of tuples (user_id, similarity_score)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        if n_recommendations is None:
            n_recommendations = self.config.get("max_recommendations", 10)

        # Scale the input features
        user_features_scaled = self.scaler.transform(user_features.reshape(1, -1))

        # Calculate similarities
        similarities = cosine_similarity(user_features_scaled, self.user_features)[0]

        # Create pairs of (user_id, similarity)
        user_similarities = list(zip(self.user_ids, similarities))

        # Filter out the user themselves and below threshold
        threshold = self.config.get("min_similarity_threshold", 0.3)
        filtered_similarities = [
            (uid, sim)
            for uid, sim in user_similarities
            if uid != user_id and sim >= threshold
        ]

        # Sort by similarity and return top N
        filtered_similarities.sort(key=lambda x: x[1], reverse=True)
        return filtered_similarities[:n_recommendations]

    def get_user_similarity_matrix(self) -> np.ndarray:
        """
        Get the full user similarity matrix

        Returns:
            Similarity matrix of shape (n_users, n_users)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting similarity matrix")

        return cosine_similarity(self.user_features)

    def save_model(self, filepath: str) -> None:
        """Save the fitted model"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")

        model_data = {
            "scaler": self.scaler,
            "user_features": self.user_features,
            "user_ids": self.user_ids,
            "config": self.config,
        }
        joblib.dump(model_data, filepath)

    def load_model(self, filepath: str) -> None:
        """Load a fitted model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")

        model_data = joblib.load(filepath)
        self.scaler = model_data["scaler"]
        self.user_features = model_data["user_features"]
        self.user_ids = model_data["user_ids"]
        self.config = model_data["config"]
        self.is_fitted = True
