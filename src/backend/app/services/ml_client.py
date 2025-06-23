"""
ML Service Client - Updated for stateless ML models
"""

import logging

import requests

from app.config import settings

logger = logging.getLogger(__name__)


class MLServiceClient:
    """Client for interacting with the ML service"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.ML_SERVICE_URL
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to ML service"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"ML service request failed: {e}")
            raise

    def get_health(self) -> dict:
        """Check ML service health"""
        return self._make_request("GET", "/health")

    def get_model_status(self) -> dict:
        """Get status of trained models"""
        return self._make_request("GET", "/models/status")

    def train_user_similarity_model(
        self,
        users_data: list[dict],
        interactions_data: list[dict],
        exercise_ids: list[int],
    ) -> dict:
        """Train user similarity model"""
        data = {
            "users_data": users_data,
            "interactions_data": interactions_data,
            "exercise_ids": exercise_ids,
        }
        return self._make_request("POST", "/train/user-similarity", data)

    def train_exercise_recommender(
        self,
        users_data: list[dict],
        interactions_data: list[dict],
        exercise_ids: list[int],
    ) -> dict:
        """Train exercise recommender model"""
        data = {
            "users_data": users_data,
            "interactions_data": interactions_data,
            "exercise_ids": exercise_ids,
        }
        return self._make_request("POST", "/train/exercise-recommender", data)

    def get_similar_users(
        self, user_features: list[float], user_id: int, n_recommendations: int = None
    ) -> dict:
        """Get similar users based on user features"""
        data = {
            "user_features": user_features,
            "user_id": user_id,
            "n_recommendations": n_recommendations,
        }
        return self._make_request("POST", "/recommendations/similar-users", data)

    def get_exercise_recommendations(
        self,
        user_id: int,
        user_interactions: list[float],
        n_recommendations: int = None,
    ) -> dict:
        """Get exercise recommendations for a user"""
        data = {
            "user_id": user_id,
            "user_interactions": user_interactions,
            "n_recommendations": n_recommendations,
        }
        return self._make_request("POST", "/recommendations/exercises", data)

    def save_models(self) -> dict:
        """Save trained models to disk"""
        return self._make_request("POST", "/models/save")

    def load_models(self) -> dict:
        """Load trained models from disk"""
        return self._make_request("POST", "/models/load")


# Global ML service client instance
ml_client = MLServiceClient()
