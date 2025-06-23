"""
Feature processor for converting database data to ML-ready vectors
"""

from typing import Any

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler


class FeatureProcessor:
    """
    Converts database data to feature vectors for ML models
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_user_features(self, users_data: list[dict[str, Any]]) -> np.ndarray:
        """
        Convert user data to feature vectors

        Args:
            users_data: List of user dictionaries from database

        Returns:
            Feature matrix of shape (n_users, n_features)
        """
        df = pd.DataFrame(users_data)

        # Encode categorical features
        categorical_features = ["fitness_goal", "experience_level"]
        for feature in categorical_features:
            if feature in df.columns:
                le = LabelEncoder()
                df[f"{feature}_encoded"] = le.fit_transform(
                    df[feature].fillna("unknown")
                )
                self.label_encoders[feature] = le

        # Create feature matrix
        feature_columns = []

        # Age (normalize)
        if "age" in df.columns:
            feature_columns.append(df["age"].fillna(df["age"].mean()))

        # Height (normalize)
        if "height" in df.columns:
            feature_columns.append(df["height"].fillna(df["height"].mean()))

        # Weight (normalize)
        if "weight" in df.columns:
            feature_columns.append(df["weight"].fillna(df["weight"].mean()))

        # Encoded categorical features
        for feature in categorical_features:
            if f"{feature}_encoded" in df.columns:
                feature_columns.append(df[f"{feature}_encoded"])

        # Create feature matrix
        features = np.column_stack(feature_columns)

        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        self.is_fitted = True

        return features_scaled

    def transform_user_features(self, user_data: dict[str, Any]) -> np.ndarray:
        """
        Transform a single user's data to feature vector

        Args:
            user_data: User dictionary

        Returns:
            Feature vector
        """
        if not self.is_fitted:
            raise ValueError("Feature processor must be fitted first")

        # Convert to DataFrame for consistency
        df = pd.DataFrame([user_data])

        # Encode categorical features using fitted encoders
        categorical_features = ["fitness_goal", "experience_level"]
        for feature in categorical_features:
            if feature in df.columns and feature in self.label_encoders:
                df[f"{feature}_encoded"] = self.label_encoders[feature].transform(
                    df[feature].fillna("unknown")
                )

        # Create feature vector
        feature_columns = []

        # Age
        if "age" in df.columns:
            feature_columns.append(df["age"].fillna(df["age"].mean()))

        # Height
        if "height" in df.columns:
            feature_columns.append(df["height"].fillna(df["height"].mean()))

        # Weight
        if "weight" in df.columns:
            feature_columns.append(df["weight"].fillna(df["weight"].mean()))

        # Encoded categorical features
        for feature in categorical_features:
            if f"{feature}_encoded" in df.columns:
                feature_columns.append(df[f"{feature}_encoded"])

        # Create feature vector
        features = np.column_stack(feature_columns)

        # Scale features
        features_scaled = self.scaler.transform(features)

        return features_scaled.flatten()

    def create_interaction_matrix(
        self,
        interactions_data: list[dict[str, Any]],
        user_ids: list[int],
        exercise_ids: list[int],
    ) -> csr_matrix:
        """
        Create user-exercise interaction matrix

        Args:
            interactions_data: List of interaction dictionaries
            user_ids: List of user IDs
            exercise_ids: List of exercise IDs

        Returns:
            Sparse interaction matrix
        """
        # Create mappings
        user_mapping = {uid: idx for idx, uid in enumerate(user_ids)}
        exercise_mapping = {eid: idx for idx, eid in enumerate(exercise_ids)}

        # Create interaction matrix
        n_users = len(user_ids)
        n_exercises = len(exercise_ids)

        # Initialize matrix
        matrix = np.zeros((n_users, n_exercises))

        # Fill matrix with interactions
        for interaction in interactions_data:
            user_id = interaction.get("user_id")
            exercise_id = interaction.get("exercise_id")
            rating = interaction.get("rating", 1)  # Default to 1 if no rating

            if user_id in user_mapping and exercise_id in exercise_mapping:
                user_idx = user_mapping[user_id]
                exercise_idx = exercise_mapping[exercise_id]
                matrix[user_idx, exercise_idx] = rating

        return csr_matrix(matrix)

    def create_user_interaction_vector(
        self,
        user_id: int,
        interactions_data: list[dict[str, Any]],
        exercise_ids: list[int],
    ) -> np.ndarray:
        """
        Create interaction vector for a specific user

        Args:
            user_id: ID of the user
            interactions_data: List of interaction dictionaries
            exercise_ids: List of exercise IDs

        Returns:
            Interaction vector for the user
        """
        exercise_mapping = {eid: idx for idx, eid in enumerate(exercise_ids)}
        n_exercises = len(exercise_ids)

        # Initialize vector
        vector = np.zeros(n_exercises)

        # Fill vector with user's interactions
        for interaction in interactions_data:
            if interaction.get("user_id") == user_id:
                exercise_id = interaction.get("exercise_id")
                rating = interaction.get("rating", 1)

                if exercise_id in exercise_mapping:
                    exercise_idx = exercise_mapping[exercise_id]
                    vector[exercise_idx] = rating

        return vector
