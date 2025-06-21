"""
ML Service Client for Backend
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class MLServiceClient:
    """Client for communicating with ML Service"""
    
    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.timeout = 30.0
    
    async def get_exercise_recommendations(
        self, 
        user_id: int, 
        n_recommendations: int = 10,
        workout_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get exercise recommendations from ML service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/recommendations/exercises",
                    params={
                        "user_id": user_id,
                        "n_recommendations": n_recommendations,
                        "workout_type": workout_type
                    }
                )
                response.raise_for_status()
                return response.json()["recommendations"]
        except Exception as e:
            logger.error(f"Error getting exercise recommendations: {e}")
            return []
    
    async def get_similar_users(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get similar users from ML service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/similar-users/{user_id}",
                    params={"limit": limit}
                )
                response.raise_for_status()
                return response.json()["similar_users"]
        except Exception as e:
            logger.error(f"Error getting similar users: {e}")
            return []
    
    async def train_models(self) -> bool:
        """Trigger model training in ML service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/models/train")
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check ML service health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"ML service health check failed: {e}")
            return False

# Create global instance
ml_client = MLServiceClient() 