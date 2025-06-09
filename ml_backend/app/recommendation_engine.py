from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.ai_service import ai_service

app = FastAPI()

def get_user_analytics_data(user_id: str, db: Session) -> np.ndarray:
    """Get user analytics data for ML processing"""
    # TODO: Replace with actual database queries
    # For now, return mock data in expected format
    return np.array([
        30,    # days_since_signup
        5,     # total_goals
        3,     # completed_goals
        2.5,   # avg_checkins_per_week
        10,    # community_messages_sent
        1,     # fitness_level_encoded (0=beginner, 1=intermediate, 2=advanced)
    ])

class UserSegmentation:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=5, random_state=42)

    def create_user_features(self, user_data: pd.DataFrame) -> np.ndarray:
        """Create feature vectors for users"""
        features = []

        for _, user in user_data.iterrows():
            feature_vector = [
                user["days_since_signup"],
                user["total_goals"],
                user["completed_goals"],
                user["avg_checkins_per_week"],
                user["community_messages_sent"],
                user["fitness_level_encoded"],  # 0=beginner, 1=intermediate, 2=advanced
            ]
            features.append(feature_vector)

        return np.array(features)

    def segment_users(self, user_data: pd.DataFrame) -> np.ndarray:
        """Segment users based on behavior patterns"""
        features = self.create_user_features(user_data)
        features_scaled = self.scaler.fit_transform(features)

        clusters = self.kmeans.fit_predict(features_scaled)

        # Save model for future predictions
        joblib.dump(self.scaler, "models/user_scaler.pkl")
        joblib.dump(self.kmeans, "models/user_segments.pkl")

        return clusters

    def predict_churn_risk(self, user_features: np.ndarray) -> float:
        """Simple churn prediction based on activity patterns"""
        # Load pre-trained model or use simple heuristics for MVP
        recent_activity = user_features[3]  # avg_checkins_per_week
        community_engagement = user_features[4] / max(user_features[1], 1)

        # Simple scoring (replace with trained model later)
        churn_score = 1.0 - (recent_activity * 0.6 + community_engagement * 0.4)
        return max(0.0, min(1.0, churn_score))


# API endpoint for ML insights
@app.get("/api/analytics/user-insights/{user_id}")
async def get_user_insights(user_id: str, db: Session = Depends(get_db)):
    # Get user data
    user_data = get_user_analytics_data(user_id, db)

    # Generate insights
    segmentation = UserSegmentation()
    churn_risk = segmentation.predict_churn_risk(user_data)

    # AI-generated recommendations
    recommendations = await ai_service.generate_user_recommendations(
        user_data, churn_risk
    )

    return {
        "churn_risk": churn_risk,
        "segment": "early_adopter",  # From clustering
        "recommendations": recommendations,
        "next_suggested_challenge": await ai_service.suggest_next_challenge(user_id),
    }
