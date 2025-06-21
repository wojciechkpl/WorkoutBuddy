# backend/app/services/recommendation_engine.py
"""
Recommendation engine service - simplified version without ML dependencies
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import requests
from app.models import User, Exercise, Workout, WorkoutExercise
from app.schemas.exercise import ExerciseResponse
from app.config import settings

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Simplified recommendation engine"""
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
    
    def get_exercise_recommendations(
        self,
        muscle_groups: Optional[List[str]] = None,
        equipment: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get basic exercise recommendations based on filters"""
        
        query = self.db.query(Exercise)
        
        if muscle_groups:
            query = query.filter(Exercise.primary_muscle.in_(muscle_groups))
        
        if equipment:
            query = query.filter(Exercise.equipment.in_(equipment))
        
        exercises = query.limit(limit).all()
        
        return [
            {
                "id": ex.id,
                "name": ex.name,
                "description": ex.description,
                "primary_muscle": ex.primary_muscle.value if ex.primary_muscle else None,
                "equipment": ex.equipment.value if ex.equipment else None,
                "difficulty": ex.difficulty,
                "score": 0.5,  # Default score
                "reasoning": "Basic recommendation"
            }
            for ex in exercises
        ]
    
    def get_user_stats(self) -> Dict:
        """Get basic user statistics"""
        total_workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user.id,
            Workout.status == "completed"
        ).count()
        
        recent_workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user.id,
            Workout.completed_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return {
            "total_workouts": total_workouts,
            "recent_workouts": recent_workouts,
            "consistency_score": recent_workouts / 30 if recent_workouts > 0 else 0
        }