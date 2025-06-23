"""
ML Service API - Stateless implementation
"""

from typing import Any, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .data.feature_processor import FeatureProcessor
from .models.exercise_recommender import ExerciseRecommender
from .models.user_similarity_model import UserSimilarityModel
from .utils.config_loader import ConfigLoader

app = FastAPI(title="ML Service", version="1.0.0")

# Load configuration
config_loader = ConfigLoader()
config = config_loader.load_config()

# Initialize models
user_similarity_model = UserSimilarityModel(
    config_loader.get_model_config("user_similarity")
)
exercise_recommender = ExerciseRecommender(
    config_loader.get_model_config("exercise_recommender")
)
feature_processor = FeatureProcessor(config)


# Pydantic models for API
class UserFeatures(BaseModel):
    user_id: int
    features: list[float]


class UserInteractionVector(BaseModel):
    user_id: int
    interaction_vector: list[float]


class TrainingData(BaseModel):
    users_data: list[dict[str, Any]]
    interactions_data: list[dict[str, Any]]
    exercise_ids: list[int]


class SimilarityRequest(BaseModel):
    user_features: list[float]
    user_id: int
    n_recommendations: Optional[int] = None


class RecommendationRequest(BaseModel):
    user_id: int
    user_interactions: list[float]
    n_recommendations: Optional[int] = None


@app.post("/train/user-similarity")
async def train_user_similarity_model(data: TrainingData):
    """Train the user similarity model with user features"""
    try:
        # Convert user data to feature vectors
        user_ids = [user["id"] for user in data.users_data]
        user_features = feature_processor.fit_user_features(data.users_data)

        # Train the model
        user_similarity_model.fit(user_features, user_ids)

        return {"message": "User similarity model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train/exercise-recommender")
async def train_exercise_recommender(data: TrainingData):
    """Train the exercise recommender model with interaction data"""
    try:
        # Get user IDs from interactions
        user_ids = list(
            set(interaction["user_id"] for interaction in data.interactions_data)
        )

        # Create interaction matrix
        interaction_matrix = feature_processor.create_interaction_matrix(
            data.interactions_data, user_ids, data.exercise_ids
        )

        # Train the model
        exercise_recommender.fit(interaction_matrix, user_ids, data.exercise_ids)

        return {"message": "Exercise recommender model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/similar-users")
async def get_similar_users(request: SimilarityRequest):
    """Get similar users based on user features"""
    try:
        if not user_similarity_model.is_fitted:
            raise HTTPException(
                status_code=400, detail="User similarity model not trained"
            )

        # Convert features to numpy array
        user_features = np.array(request.user_features)

        # Get similar users
        similar_users = user_similarity_model.find_similar_users(
            user_features, request.user_id, request.n_recommendations
        )

        return {
            "similar_users": [
                {"user_id": uid, "similarity_score": float(score)}
                for uid, score in similar_users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations/exercises")
async def get_exercise_recommendations(request: RecommendationRequest):
    """Get exercise recommendations for a user"""
    try:
        if not exercise_recommender.is_fitted:
            raise HTTPException(
                status_code=400, detail="Exercise recommender model not trained"
            )

        # Convert interaction vector to numpy array
        user_interactions = np.array(request.user_interactions)

        # Get recommendations
        recommendations = exercise_recommender.recommend_exercises(
            request.user_id, user_interactions, request.n_recommendations
        )

        return {
            "recommendations": [
                {"exercise_id": eid, "predicted_rating": float(rating)}
                for eid, rating in recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/status")
async def get_model_status():
    """Get the status of trained models"""
    return {
        "user_similarity_model": {
            "trained": user_similarity_model.is_fitted,
            "config": config_loader.get_model_config("user_similarity"),
        },
        "exercise_recommender": {
            "trained": exercise_recommender.is_fitted,
            "config": config_loader.get_model_config("exercise_recommender"),
        },
    }


@app.post("/models/save")
async def save_models():
    """Save trained models to disk"""
    try:
        persistence_config = config_loader.get_model_persistence_config()
        save_path = persistence_config.get("save_path", "/app/models")

        if user_similarity_model.is_fitted:
            user_similarity_model.save_model(f"{save_path}/user_similarity_model.pkl")

        if exercise_recommender.is_fitted:
            exercise_recommender.save_model(
                f"{save_path}/exercise_recommender_model.pkl"
            )

        return {"message": "Models saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/load")
async def load_models():
    """Load trained models from disk"""
    try:
        persistence_config = config_loader.get_model_persistence_config()
        load_path = persistence_config.get("load_path", "/app/models")

        # Try to load models
        try:
            user_similarity_model.load_model(f"{load_path}/user_similarity_model.pkl")
        except FileNotFoundError:
            pass  # Model not saved yet

        try:
            exercise_recommender.load_model(
                f"{load_path}/exercise_recommender_model.pkl"
            )
        except FileNotFoundError:
            pass  # Model not saved yet

        return {"message": "Models loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-service"}
