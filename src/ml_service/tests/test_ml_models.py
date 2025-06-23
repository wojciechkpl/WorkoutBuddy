"""
Unit tests for ML models with unit support

All tests use metric units internally for consistency.
"""

from unittest.mock import Mock

import numpy as np

from app.exercise_recommender import ExerciseRecommender
from app.models import User
from app.user_similarity_model import UserSimilarityModel


class TestUserSimilarityModel:
    """Test cases for UserSimilarityModel with metric units"""

    def test_init(self):
        """Test model initialization"""
        model = UserSimilarityModel()
        assert model.scaler is not None
        assert model.pca is not None
        assert model.user_features == {}

    def test_extract_user_features(self, db_session):
        """Test feature extraction with metric units"""
        model = UserSimilarityModel()

        # Create test user with metric units
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,  # Always in centimeters
            weight_kg=70.0,  # Always in kilograms
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        # Mock database session with metric data
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(
            workout_count=5, avg_duration=45.0, total_weight=500.0, total_distance=25.0
        )

        features = model.extract_user_features(user, mock_db)

        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        assert features[0] == 175.0  # height_cm
        assert features[1] == 70.0  # weight_kg

    def test_extract_user_features_imperial_conversion(self, db_session):
        """Test feature extraction with imperial to metric conversion"""
        model = UserSimilarityModel()

        # Create test user with imperial units
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,  # Will be converted from inches
            weight_kg=70.0,  # Will be converted from lbs
            unit_system="IMPERIAL",
            height_unit="INCHES",
            weight_unit="LBS",
        )

        # Mock the conversion methods
        def mock_get_height_cm():
            return 175.0  # Converted from inches to cm

        def mock_get_weight_kg():
            return 70.0  # Converted from lbs to kg

        user.get_height_cm = mock_get_height_cm
        user.get_weight_kg = mock_get_weight_kg

        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(
            workout_count=5, avg_duration=45.0, total_weight=500.0, total_distance=25.0
        )

        features = model.extract_user_features(user, mock_db)

        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        assert features[0] == 175.0  # height_cm (converted)
        assert features[1] == 70.0  # weight_kg (converted)

    def test_find_similar_users(self, db_session):
        """Test finding similar users with metric units"""
        model = UserSimilarityModel()

        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,
            weight_kg=70.0,
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        # Mock database session
        mock_db = Mock()

        # Mock workout data for feature extraction
        mock_db.execute.return_value.fetchone.return_value = Mock(
            workout_count=5, avg_duration=45.0, total_weight=500.0, total_distance=25.0
        )

        # Mock multiple users for training (need at least 3)
        user_data_1 = Mock()
        user_data_1.id = 1
        user_data_1.username = "testuser"
        user_data_1.email = "test@example.com"
        user_data_1.fitness_goal = "strength"
        user_data_1.experience_level = "beginner"
        user_data_1.height_cm = 175.0
        user_data_1.weight_kg = 70.0

        user_data_2 = Mock()
        user_data_2.id = 2
        user_data_2.username = "user2"
        user_data_2.email = "user2@example.com"
        user_data_2.fitness_goal = "muscle_gain"
        user_data_2.experience_level = "intermediate"
        user_data_2.height_cm = 180.0
        user_data_2.weight_kg = 75.0

        user_data_3 = Mock()
        user_data_3.id = 3
        user_data_3.username = "user3"
        user_data_3.email = "user3@example.com"
        user_data_3.fitness_goal = "endurance"
        user_data_3.experience_level = "advanced"
        user_data_3.height_cm = 170.0
        user_data_3.weight_kg = 65.0

        # Mock other users for similarity search
        other_user_data = Mock()
        other_user_data.id = 4
        other_user_data.username = "otheruser"
        other_user_data.email = "other@example.com"
        other_user_data.fitness_goal = "strength"
        other_user_data.experience_level = "intermediate"
        other_user_data.height_cm = 180.0  # Already in cm from metric view
        other_user_data.weight_kg = 75.0  # Already in kg from metric view

        # Set up mock responses
        mock_db.execute.return_value.fetchall.side_effect = [
            [user_data_1, user_data_2, user_data_3],  # For training
            [other_user_data],  # For similarity search
        ]

        # Train the model first
        model.train(mock_db)

        similar_users = model.find_similar_users(user, mock_db, limit=5)

        assert isinstance(similar_users, list)
        assert len(similar_users) > 0
        assert "user_id" in similar_users[0]
        assert "similarity_score" in similar_users[0]

    def test_train_model(self, db_session):
        """Test model training with metric data"""
        model = UserSimilarityModel()

        # Mock database session
        mock_db = Mock()

        # Create multiple users for training (need at least 3)
        user_data_1 = Mock()
        user_data_1.id = 1
        user_data_1.username = "testuser"
        user_data_1.email = "test@example.com"
        user_data_1.fitness_goal = "strength"
        user_data_1.experience_level = "beginner"
        user_data_1.height_cm = 175.0  # Already in cm from metric view
        user_data_1.weight_kg = 70.0  # Already in kg from metric view

        user_data_2 = Mock()
        user_data_2.id = 2
        user_data_2.username = "user2"
        user_data_2.email = "user2@example.com"
        user_data_2.fitness_goal = "muscle_gain"
        user_data_2.experience_level = "intermediate"
        user_data_2.height_cm = 180.0
        user_data_2.weight_kg = 75.0

        user_data_3 = Mock()
        user_data_3.id = 3
        user_data_3.username = "user3"
        user_data_3.email = "user3@example.com"
        user_data_3.fitness_goal = "endurance"
        user_data_3.experience_level = "advanced"
        user_data_3.height_cm = 170.0
        user_data_3.weight_kg = 65.0

        mock_db.execute.return_value.fetchall.return_value = [
            user_data_1,
            user_data_2,
            user_data_3,
        ]
        mock_db.execute.return_value.fetchone.return_value = Mock(
            workout_count=5, avg_duration=45.0, total_weight=500.0, total_distance=25.0
        )

        # Test training
        model.train(mock_db)

        # Verify scaler was fitted
        assert hasattr(model.scaler, "mean_")

    def test_train_model_insufficient_data(self, db_session):
        """Test model training with insufficient data"""
        model = UserSimilarityModel()

        # Mock database session with no users
        mock_db = Mock()
        mock_db.execute.return_value.fetchall.return_value = []

        # Test training with no data
        model.train(mock_db)

        # Verify scaler was not fitted
        assert not hasattr(model.scaler, "mean_")


class TestExerciseRecommender:
    """Test cases for ExerciseRecommender with metric units"""

    def test_init(self):
        """Test recommender initialization"""
        recommender = ExerciseRecommender()
        assert recommender.user_similarity_model is None

    def test_load_or_initialize(self):
        """Test loading or initializing recommender"""
        recommender = ExerciseRecommender.load_or_initialize()
        assert isinstance(recommender, ExerciseRecommender)
        assert recommender.user_similarity_model is not None

    def test_get_recommendations(self, db_session):
        """Test getting exercise recommendations with metric units"""
        recommender = ExerciseRecommender.load_or_initialize()

        # Create test user with metric units
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,
            weight_kg=70.0,
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        # Mock database session
        mock_db = Mock()
        exercise_data = Mock()
        exercise_data.id = 1
        exercise_data.name = "Push-ups"
        exercise_data.description = "Classic exercise"
        exercise_data.muscle_group = "Chest"
        exercise_data.equipment = "Bodyweight"
        exercise_data.difficulty_level = "Beginner"
        exercise_data.instructions = "Start in plank position"

        mock_db.execute.return_value.fetchall.return_value = [exercise_data]
        mock_db.execute.return_value.fetchone.return_value = Mock(count=0)

        recommendations = recommender.get_recommendations(
            user, mock_db, n_recommendations=5
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "id" in recommendations[0]
        assert "name" in recommendations[0]
        assert "score" in recommendations[0]

    def test_calculate_exercise_score(self, db_session):
        """Test exercise score calculation with metric units"""
        recommender = ExerciseRecommender.load_or_initialize()

        # Create test user with metric units
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,
            weight_kg=70.0,
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        exercise = {
            "id": 1,
            "name": "Push-ups",
            "muscle_group": "Chest",
            "equipment": "Bodyweight",
            "difficulty_level": "Beginner",
        }

        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(count=0)

        score = recommender._calculate_exercise_score(exercise, user, mock_db)

        assert isinstance(score, float)
        assert score >= 0.0

    def test_calculate_exercise_score_physical_metrics(self, db_session):
        """Test exercise score calculation considering physical metrics"""
        recommender = ExerciseRecommender.load_or_initialize()

        # Create test user with different physical characteristics
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=185.0,  # Taller user
            weight_kg=85.0,  # Heavier user
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        # Mock the conversion methods
        def mock_get_height_cm():
            return 185.0

        def mock_get_weight_kg():
            return 85.0

        user.get_height_cm = mock_get_height_cm
        user.get_weight_kg = mock_get_weight_kg

        exercise = {
            "id": 1,
            "name": "Push-ups",
            "muscle_group": "Chest",
            "equipment": "Bodyweight",
            "difficulty_level": "Beginner",
        }

        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(count=0)

        score = recommender._calculate_exercise_score(exercise, user, mock_db)

        assert isinstance(score, float)
        assert score >= 0.0
        # Should get bonus for bodyweight exercise with heavier user
        assert score > 0.0

    def test_get_recommendation_reasoning(self, db_session):
        """Test recommendation reasoning generation with metric units"""
        recommender = ExerciseRecommender.load_or_initialize()

        # Create test user with metric units
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175.0,
            weight_kg=70.0,
            unit_system="METRIC",
            height_unit="CM",
            weight_unit="KG",
        )

        exercise = {
            "id": 1,
            "name": "Push-ups",
            "muscle_group": "Chest",
            "equipment": "Bodyweight",
            "difficulty_level": "Beginner",
        }

        reasoning = recommender._get_recommendation_reasoning(exercise, user, 0.8)

        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
