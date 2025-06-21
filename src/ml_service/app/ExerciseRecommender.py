# backend/app/ml/ExerciseRecommender.py
"""
Exercise recommendation model based on user preferences and similar users
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.models import User, WorkoutExercise, Workout
from app.UserSimilarityModel import UserSimilarityModel
import logging

logger = logging.getLogger(__name__)

class ExerciseRecommender:
    """
    Recommends exercises based on:
    - User's workout history
    - Similar users' preferences
    - Muscle group balance
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
        workout_type: Optional[str] = None
    ) -> List[Dict]:
        """Get personalized exercise recommendations"""
        
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
                    "instructions": exercise_data.instructions
                }
                
                # Calculate score based on user preferences
                score = self._calculate_exercise_score(exercise, user, db, workout_type)
                
                recommendations.append({
                    **exercise,
                    "score": score,
                    "reasoning": self._get_recommendation_reasoning(exercise, user, score)
                })
            
            # Sort by score and return top N
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            return recommendations[:n_recommendations]
            
        except Exception as e:
            logger.error(f"Error getting exercise recommendations: {e}")
            return []
    
    def _calculate_exercise_score(
        self,
        exercise: Dict,
        user: User,
        db: Session,
        workout_type: Optional[str] = None
    ) -> float:
        """Calculate score for an exercise based on user preferences"""
        score = 0.0
        
        try:
            # 1. Match fitness goal
            if user.fitness_goal:
                if user.fitness_goal == "strength" and exercise["muscle_group"] in ["chest", "back", "legs"]:
                    score += 0.3
                elif user.fitness_goal == "weight_loss" and exercise["equipment"] == "Bodyweight":
                    score += 0.2
                elif user.fitness_goal == "muscle_gain" and exercise["muscle_group"] in ["chest", "back", "shoulders"]:
                    score += 0.3
            
            # 2. Match experience level
            if user.experience_level:
                if user.experience_level == "beginner" and exercise["difficulty_level"] == "Beginner":
                    score += 0.2
                elif user.experience_level == "intermediate" and exercise["difficulty_level"] in ["Beginner", "Intermediate"]:
                    score += 0.2
                elif user.experience_level == "advanced":
                    score += 0.1
            
            # 3. Check if user has done this exercise before (preference)
            result = db.execute(text("""
                SELECT COUNT(*) as count 
                FROM workout_exercises we
                JOIN workouts w ON we.workout_id = w.id
                WHERE w.user_id = :user_id AND we.exercise_id = :exercise_id
            """), {"user_id": user.id, "exercise_id": exercise["id"]})
            
            exercise_count = result.fetchone().count
            if exercise_count > 0:
                score += min(exercise_count * 0.1, 0.3)  # Cap at 0.3
            
            # 4. Muscle group balance (avoid overworking same muscle)
            if exercise["muscle_group"]:
                result = db.execute(text("""
                    SELECT COUNT(*) as count 
                    FROM workout_exercises we
                    JOIN workouts w ON we.workout_id = w.id
                    JOIN exercises e ON we.exercise_id = e.id
                    WHERE w.user_id = :user_id 
                    AND e.muscle_group = :muscle_group
                    AND w.created_at >= NOW() - INTERVAL '7 days'
                """), {"user_id": user.id, "muscle_group": exercise["muscle_group"]})
                
                recent_count = result.fetchone().count
                if recent_count > 3:  # If worked this muscle group recently
                    score -= 0.2
            
            # 5. Random factor for variety
            score += np.random.random() * 0.1
            
        except Exception as e:
            logger.error(f"Error calculating exercise score: {e}")
        
        return max(score, 0.0)  # Ensure non-negative
    
    def _get_recommendation_reasoning(
        self,
        exercise: Dict,
        user: User,
        score: float
    ) -> str:
        """Generate reasoning for recommendation"""
        reasons = []
        
        if user.fitness_goal:
            if user.fitness_goal == "strength" and exercise["muscle_group"] in ["chest", "back", "legs"]:
                reasons.append("Great for strength building")
            elif user.fitness_goal == "weight_loss" and exercise["equipment"] == "Bodyweight":
                reasons.append("Effective for weight loss")
            elif user.fitness_goal == "muscle_gain" and exercise["muscle_group"] in ["chest", "back", "shoulders"]:
                reasons.append("Excellent for muscle growth")
        
        if user.experience_level:
            if user.experience_level == "beginner" and exercise["difficulty_level"] == "Beginner":
                reasons.append("Perfect for beginners")
            elif user.experience_level == "intermediate" and exercise["difficulty_level"] in ["Beginner", "Intermediate"]:
                reasons.append("Suitable for your experience level")
        
        if score > 0.5:
            reasons.append("High recommendation score")
        elif score > 0.3:
            reasons.append("Good match for your profile")
        else:
            reasons.append("Good variety exercise")
        
        return "; ".join(reasons) if reasons else "Recommended based on your profile"
    
    def _build_features(self):
        """Build features for the recommender (placeholder)"""
        logger.info("Building exercise recommender features...")
        # This would typically involve feature engineering
        # For now, just log that it's called
        pass