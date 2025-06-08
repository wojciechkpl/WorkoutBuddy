"""
Data Preprocessing Module for WorkoutBuddy ML Backend

This module handles all input data preprocessing and transformation
before feeding data to ML models.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class DataPreprocessor:
    """
    Main preprocessing class for transforming raw user data
    into ML-ready features.
    """

    def __init__(self):
        self.feature_scalers = {}
        self.encoders = {}

    def preprocess_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess user data for ML model input.

        Args:
            user_data: Raw user data from database

        Returns:
            Processed feature dictionary
        """
        features = {}

        # Demographic features
        features["age"] = self._calculate_age(user_data.get("date_of_birth"))
        features["gender"] = self._encode_gender(user_data.get("gender"))
        features["height"] = user_data.get("height", 0)
        features["weight"] = user_data.get("weight", 0)
        features["bmi"] = self._calculate_bmi(features["height"], features["weight"])

        # Activity level features
        features["activity_level"] = self._encode_activity_level(
            user_data.get("activity_level", "beginner")
        )

        # Goal features
        features["primary_goal"] = self._encode_fitness_goal(
            user_data.get("primary_goal")
        )

        # Historical workout features
        features["workout_frequency"] = self._calculate_workout_frequency(
            user_data.get("workout_history", [])
        )

        return features

    def preprocess_exercise_data(self, exercise_data: List[Dict]) -> pd.DataFrame:
        """
        Preprocess exercise data for recommendations.

        Args:
            exercise_data: List of exercise records

        Returns:
            Processed DataFrame with exercise features
        """
        df = pd.DataFrame(exercise_data)

        if df.empty:
            return df

        # Encode categorical features
        df["muscle_group_encoded"] = df["main_muscle_group"].apply(
            self._encode_muscle_group
        )
        df["equipment_encoded"] = df["equipment"].apply(self._encode_equipment)
        df["difficulty_encoded"] = df["difficulty"].apply(self._encode_difficulty)

        # Create exercise complexity score
        df["complexity_score"] = self._calculate_exercise_complexity(df)

        return df

    def preprocess_workout_history(self, workout_history: List[Dict]) -> Dict[str, Any]:
        """
        Extract features from user's workout history.

        Args:
            workout_history: List of historical workout records

        Returns:
            Aggregated workout features
        """
        if not workout_history:
            return self._get_default_history_features()

        df = pd.DataFrame(workout_history)

        # Time-based features
        features = {
            "total_workouts": len(df),
            "avg_workout_duration": df["duration"].mean() if "duration" in df else 0,
            "workout_consistency": self._calculate_consistency(df),
            "recent_activity_trend": self._calculate_recent_trend(df),
        }

        # Exercise preference features
        if "exercises" in df.columns:
            exercise_stats = self._analyze_exercise_preferences(df["exercises"])
            features.update(exercise_stats)

        return features

    def _calculate_age(self, date_of_birth: Optional[str]) -> int:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return 25  # Default age

        try:
            dob = datetime.fromisoformat(date_of_birth.replace("Z", "+00:00"))
            return int((datetime.now() - dob).days / 365.25)
        except:
            return 25

    def _encode_gender(self, gender: Optional[str]) -> int:
        """Encode gender as numeric value."""
        gender_map = {"male": 1, "female": 0, "other": 2}
        return gender_map.get(gender.lower() if gender else "other", 2)

    def _calculate_bmi(self, height: float, weight: float) -> float:
        """Calculate BMI from height (cm) and weight (kg)."""
        if height > 0 and weight > 0:
            height_m = height / 100
            return weight / (height_m**2)
        return 0.0

    def _encode_activity_level(self, level: str) -> int:
        """Encode activity level as numeric value."""
        level_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        return level_map.get(level.lower(), 1)

    def _encode_fitness_goal(self, goal: Optional[str]) -> int:
        """Encode fitness goal as numeric value."""
        goal_map = {
            "weight_loss": 1,
            "muscle_gain": 2,
            "strength": 3,
            "endurance": 4,
            "flexibility": 5,
            "general_fitness": 6,
        }
        return goal_map.get(goal.lower() if goal else "general_fitness", 6)

    def _calculate_workout_frequency(self, workout_history: List[Dict]) -> float:
        """Calculate average workout frequency per week."""
        if not workout_history:
            return 0.0

        # Calculate based on last 30 days
        recent_workouts = [
            w for w in workout_history if self._is_recent_workout(w.get("created_at"))
        ]

        return len(recent_workouts) / 4.0  # Per week average

    def _is_recent_workout(self, created_at: Optional[str]) -> bool:
        """Check if workout was in the last 30 days."""
        if not created_at:
            return False

        try:
            workout_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            return (datetime.now() - workout_date).days <= 30
        except:
            return False

    def _encode_muscle_group(self, muscle_group: str) -> int:
        """Encode muscle group as numeric value."""
        groups = [
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "cardio",
            "full_body",
        ]
        return (
            groups.index(muscle_group.lower()) if muscle_group.lower() in groups else 0
        )

    def _encode_equipment(self, equipment: str) -> int:
        """Encode equipment type as numeric value."""
        equipment_types = [
            "none",
            "dumbbells",
            "barbell",
            "resistance_bands",
            "kettlebell",
            "machine",
            "cable",
            "bodyweight",
        ]
        return (
            equipment_types.index(equipment.lower())
            if equipment.lower() in equipment_types
            else 0
        )

    def _encode_difficulty(self, difficulty: str) -> int:
        """Encode difficulty level as numeric value."""
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        return difficulty_map.get(difficulty.lower(), 2)

    def _calculate_exercise_complexity(self, df: pd.DataFrame) -> pd.Series:
        """Calculate exercise complexity score based on multiple factors."""
        # Simple complexity score based on difficulty and equipment
        complexity = df["difficulty_encoded"] * 0.6 + df["equipment_encoded"] * 0.4
        return complexity

    def _calculate_consistency(self, workout_df: pd.DataFrame) -> float:
        """Calculate workout consistency score (0-1)."""
        if len(workout_df) < 2:
            return 0.0

        # Calculate standard deviation of gaps between workouts
        workout_dates = pd.to_datetime(workout_df["created_at"], errors="coerce")
        workout_dates = workout_dates.dropna().sort_values()

        if len(workout_dates) < 2:
            return 0.0

        gaps = workout_dates.diff().dt.days.dropna()
        consistency = 1.0 / (1.0 + gaps.std())  # Lower std = higher consistency

        return min(consistency, 1.0)

    def _calculate_recent_trend(self, workout_df: pd.DataFrame) -> float:
        """Calculate recent workout activity trend."""
        if len(workout_df) < 2:
            return 0.0

        # Compare last 2 weeks vs previous 2 weeks
        now = datetime.now()
        last_2_weeks = workout_df[
            pd.to_datetime(workout_df["created_at"], errors="coerce")
            >= (now - timedelta(days=14))
        ]
        prev_2_weeks = workout_df[
            (
                pd.to_datetime(workout_df["created_at"], errors="coerce")
                >= (now - timedelta(days=28))
            )
            & (
                pd.to_datetime(workout_df["created_at"], errors="coerce")
                < (now - timedelta(days=14))
            )
        ]

        recent_count = len(last_2_weeks)
        prev_count = len(prev_2_weeks)

        if prev_count == 0:
            return 1.0 if recent_count > 0 else 0.0

        return recent_count / prev_count

    def _analyze_exercise_preferences(self, exercises_column) -> Dict[str, Any]:
        """Analyze user's exercise preferences from history."""
        # This would need to be implemented based on actual data structure
        return {
            "preferred_muscle_groups": [],
            "preferred_equipment": "bodyweight",
            "avg_exercise_difficulty": 2.0,
        }

    def _get_default_history_features(self) -> Dict[str, Any]:
        """Return default features for users with no workout history."""
        return {
            "total_workouts": 0,
            "avg_workout_duration": 30.0,
            "workout_consistency": 0.0,
            "recent_activity_trend": 0.0,
            "preferred_muscle_groups": [],
            "preferred_equipment": "bodyweight",
            "avg_exercise_difficulty": 1.0,
        }
