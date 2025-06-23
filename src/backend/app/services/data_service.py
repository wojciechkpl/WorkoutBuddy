"""
Data Service for converting database data to ML-ready vectors
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models import Exercise, User, Workout, WorkoutExercise

logger = logging.getLogger(__name__)


class DataService:
    """Service for extracting and processing data for ML models"""

    def __init__(self, db: Session):
        self.db = db

    def get_users_data(self) -> list[dict[str, Any]]:
        """Extract user data for ML models"""
        users = self.db.query(User).all()

        users_data = []
        for user in users:
            user_data = {
                "id": user.id,
                "age": user.age,
                "height": user.height,
                "weight": user.weight,
                "fitness_goal": user.fitness_goal.value if user.fitness_goal else None,
                "experience_level": user.experience_level.value
                if user.experience_level
                else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            users_data.append(user_data)

        return users_data

    def get_exercises_data(self) -> list[dict[str, Any]]:
        """Extract exercise data for ML models"""
        exercises = self.db.query(Exercise).all()

        exercises_data = []
        for exercise in exercises:
            exercise_data = {
                "id": exercise.id,
                "name": exercise.name,
                "primary_muscle": exercise.primary_muscle.value
                if exercise.primary_muscle
                else None,
                "equipment": exercise.equipment.value if exercise.equipment else None,
                "exercise_type": exercise.exercise_type.value
                if exercise.exercise_type
                else None,
                "difficulty": exercise.difficulty,
                "mets": exercise.mets,
            }
            exercises_data.append(exercise_data)

        return exercises_data

    def get_user_exercise_interactions(self) -> list[dict[str, Any]]:
        """Extract user-exercise interactions for ML models"""
        # Get workout exercises with user information
        workout_exercises = (
            self.db.query(WorkoutExercise, Workout)
            .join(Workout)
            .filter(Workout.status == "completed")
            .all()
        )

        interactions = []
        for we, workout in workout_exercises:
            # Calculate a simple rating based on completion
            # In a real system, you might have actual ratings
            rating = 1.0  # Default rating for completed exercises

            interaction = {
                "user_id": workout.user_id,
                "exercise_id": we.exercise_id,
                "rating": rating,
                "workout_id": workout.id,
                "completed_at": workout.completed_at.isoformat()
                if workout.completed_at
                else None,
            }
            interactions.append(interaction)

        return interactions

    def get_user_interaction_vector(self, user_id: int) -> list[float]:
        """Get interaction vector for a specific user"""
        # Get all exercises
        exercises = self.db.query(Exercise).all()
        exercise_ids = [ex.id for ex in exercises]

        # Get user's interactions
        user_interactions = (
            self.db.query(WorkoutExercise, Workout)
            .join(Workout)
            .filter(Workout.user_id == user_id, Workout.status == "completed")
            .all()
        )

        # Create interaction vector
        interaction_vector = [0.0] * len(exercise_ids)
        exercise_id_to_idx = {eid: idx for idx, eid in enumerate(exercise_ids)}

        for we, workout in user_interactions:
            if we.exercise_id in exercise_id_to_idx:
                idx = exercise_id_to_idx[we.exercise_id]
                interaction_vector[idx] = 1.0  # User has done this exercise

        return interaction_vector

    def get_user_features(self, user_id: int) -> list[float]:
        """Get feature vector for a specific user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        # Create feature vector
        features = []

        # Age (normalized)
        features.append(float(user.age) if user.age else 30.0)

        # Height (normalized)
        features.append(float(user.height) if user.height else 170.0)

        # Weight (normalized)
        features.append(float(user.weight) if user.weight else 70.0)

        # Fitness goal (encoded)
        if user.fitness_goal:
            goal_mapping = {
                "weight_loss": 0,
                "muscle_gain": 1,
                "strength": 2,
                "endurance": 3,
                "general_fitness": 4,
                "athletic_performance": 5,
            }
            features.append(float(goal_mapping.get(user.fitness_goal.value, 0)))
        else:
            features.append(0.0)

        # Experience level (encoded)
        if user.experience_level:
            level_mapping = {
                "beginner": 0,
                "intermediate": 1,
                "advanced": 2,
                "expert": 3,
            }
            features.append(float(level_mapping.get(user.experience_level.value, 0)))
        else:
            features.append(0.0)

        return features

    def get_all_data_for_ml(self) -> tuple[list[dict], list[dict], list[int]]:
        """Get all data needed for ML model training"""
        users_data = self.get_users_data()
        interactions_data = self.get_user_exercise_interactions()
        exercise_ids = [ex["id"] for ex in self.get_exercises_data()]

        return users_data, interactions_data, exercise_ids
