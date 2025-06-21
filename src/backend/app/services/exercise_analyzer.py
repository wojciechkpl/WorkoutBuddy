# backend/app/services/exercise_analyzer.py
"""
Exercise analysis service for recovery and recommendations
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

from app.models import User, Workout, WorkoutExercise, Exercise

class ExerciseAnalyzer:
    """Analyze exercise patterns and recovery needs"""
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
    
    def get_next_workout_suggestion(self) -> Dict:
        """Suggest next workout based on recovery and balance"""
        
        # Get recent workouts
        recent_workouts = self.db.query(Workout).filter(
            Workout.user_id == self.user.id,
            Workout.completed_at >= datetime.utcnow() - timedelta(days=7)
        ).order_by(Workout.completed_at.desc()).all()
        
        if not recent_workouts:
            return {
                "suggestion": "Start with a full-body workout",
                "muscle_groups": ["chest", "back", "legs"],
                "reasoning": "No recent workout history found"
            }
        
        # Analyze muscle group recovery
        muscle_last_worked = self._get_muscle_recovery_status(recent_workouts)
        
        # Find muscles that need work
        ready_muscles = []
        for muscle, last_worked in muscle_last_worked.items():
            days_since = (datetime.utcnow() - last_worked).days
            
            # Recovery time based on muscle group
            recovery_days = {
                "legs": 3,
                "back": 2,
                "chest": 2,
                "shoulders": 2,
                "biceps": 1,
                "triceps": 1,
                "core": 1
            }
            
            if days_since >= recovery_days.get(muscle, 2):
                ready_muscles.append(muscle)
        
        # Generate suggestion
        if not ready_muscles:
            return {
                "suggestion": "Light cardio or active recovery day",
                "muscle_groups": [],
                "reasoning": "All muscle groups are still recovering"
            }
        
        # Prioritize larger muscle groups
        priority_order = ["legs", "back", "chest", "shoulders", "biceps", "triceps", "core"]
        suggested_muscles = sorted(
            ready_muscles,
            key=lambda x: priority_order.index(x) if x in priority_order else 999
        )[:3]
        
        return {
            "suggestion": f"Focus on {', '.join(suggested_muscles)}",
            "muscle_groups": suggested_muscles,
            "reasoning": "These muscle groups have had adequate recovery time"
        }
    
    def _get_muscle_recovery_status(self, workouts: List[Workout]) -> Dict:
        """Get last worked date for each muscle group"""
        muscle_dates = defaultdict(lambda: datetime.min)
        
        for workout in workouts:
            for we in workout.exercises:
                muscle = we.exercise.primary_muscle.value
                if workout.completed_at > muscle_dates[muscle]:
                    muscle_dates[muscle] = workout.completed_at
        
        return dict(muscle_dates)