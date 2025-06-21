# backend/app/ml/user_similarity.py
"""
User similarity model for finding similar users based on goals and workout patterns
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import joblib
import os
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import User, Workout, WorkoutExercise, UserStats
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class UserSimilarityModel:
    """
    ML model for finding similar users based on:
    - Fitness goals
    - Experience level
    - Workout patterns
    """
    
    MODEL_PATH = os.path.join(settings.ML_MODEL_PATH, "user_similarity_model.pkl")
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=5)
        self.user_features = {}
        
    def extract_user_features(self, user: User, db: Session) -> np.ndarray:
        """Extract feature vector for a user"""
        features = []
        
        # Basic profile features
        features.extend([
            user.height_cm or 170,
            user.weight_kg or 70,
            1 if user.fitness_goal == "weight_loss" else 0,
            1 if user.fitness_goal == "muscle_gain" else 0,
            1 if user.fitness_goal == "strength" else 0,
            1 if user.fitness_goal == "endurance" else 0,
            1 if user.experience_level == "beginner" else 0,
            1 if user.experience_level == "intermediate" else 0,
            1 if user.experience_level == "advanced" else 0,
        ])
        
        # Workout pattern features - using raw SQL for simplicity
        try:
            # Get workout count
            result = db.execute(text("""
                SELECT COUNT(*) as workout_count 
                FROM workouts 
                WHERE user_id = :user_id
            """), {"user_id": user.id})
            workout_count = result.fetchone().workout_count
            features.append(workout_count)
            
            # Get average workout duration
            result = db.execute(text("""
                SELECT AVG(duration_minutes) as avg_duration 
                FROM workouts 
                WHERE user_id = :user_id AND duration_minutes IS NOT NULL
            """), {"user_id": user.id})
            avg_duration = result.fetchone().avg_duration or 0
            features.append(avg_duration)
            
        except Exception as e:
            logger.error(f"Error getting workout features: {e}")
            features.extend([0, 0])
        
        return np.array(features)
    
    def train(self, db: Session = None):
        """Train the similarity model"""
        logger.info("Training user similarity model...")
        
        if not db:
            logger.warning("No database session provided for training")
            return
        
        # Get all users
        try:
            result = db.execute(text("SELECT * FROM users"))
            users_data = result.fetchall()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
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
                user = User(
                    id=user_data.id,
                    username=user_data.username,
                    email=user_data.email,
                    fitness_goal=getattr(user_data, 'fitness_goal', None),
                    experience_level=getattr(user_data, 'experience_level', None),
                    height_cm=getattr(user_data, 'height_cm', None),
                    weight_kg=getattr(user_data, 'weight_kg', None)
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
        logger.info(f"User similarity model trained with {len(users_data)} users")
    
    def find_similar_users(
        self,
        user: User,
        db: Session,
        limit: int = 5
    ) -> List[Dict]:
        """Find similar users"""
        try:
            user_features = self.extract_user_features(user, db)
            user_features_scaled = self.scaler.transform([user_features])
            
            # Get all other users
            result = db.execute(text("SELECT * FROM users WHERE id != :user_id"), {"user_id": user.id})
            other_users_data = result.fetchall()
            
            similarities = []
            
            for other_user_data in other_users_data:
                try:
                    other_user = User(
                        id=other_user_data.id,
                        username=other_user_data.username,
                        email=other_user_data.email,
                        fitness_goal=getattr(other_user_data, 'fitness_goal', None),
                        experience_level=getattr(other_user_data, 'experience_level', None),
                        height_cm=getattr(other_user_data, 'height_cm', None),
                        weight_kg=getattr(other_user_data, 'weight_kg', None)
                    )
                    
                    other_features = self.extract_user_features(other_user, db)
                    other_features_scaled = self.scaler.transform([other_features])
                    
                    # Calculate cosine similarity
                    similarity = cosine_similarity(user_features_scaled, other_features_scaled)[0][0]
                    similarities.append({
                        "user_id": other_user.id,
                        "username": other_user.username,
                        "similarity_score": float(similarity),
                        "fitness_goal": other_user.fitness_goal,
                        "experience_level": other_user.experience_level
                    })
                except Exception as e:
                    logger.error(f"Error calculating similarity for user {other_user_data.id}: {e}")
            
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
            model_data = {
                'scaler': self.scaler,
                'pca': self.pca,
                'user_features': self.user_features
            }
            joblib.dump(model_data, self.MODEL_PATH)
            logger.info(f"Model saved to {self.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_data = joblib.load(self.MODEL_PATH)
            self.scaler = model_data['scaler']
            self.pca = model_data['pca']
            self.user_features = model_data['user_features']
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise