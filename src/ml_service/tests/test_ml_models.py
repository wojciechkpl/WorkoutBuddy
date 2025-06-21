"""
Unit tests for ML models
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.UserSimilarityModel import UserSimilarityModel
from app.ExerciseRecommender import ExerciseRecommender
from app.models import User

class TestUserSimilarityModel:
    """Test cases for UserSimilarityModel"""
    
    def test_init(self):
        """Test model initialization"""
        model = UserSimilarityModel()
        assert model.scaler is not None
        assert model.pca is not None
        assert model.user_features == {}
    
    def test_extract_user_features(self, db_session):
        """Test feature extraction"""
        model = UserSimilarityModel()
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175,
            weight_kg=70.0
        )
        
        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(workout_count=5, avg_duration=45.0)
        
        features = model.extract_user_features(user, mock_db)
        
        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        assert features[0] == 175  # height_cm
        assert features[1] == 70.0  # weight_kg
    
    def test_find_similar_users(self, db_session):
        """Test finding similar users"""
        model = UserSimilarityModel()
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175,
            weight_kg=70.0
        )
        
        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(workout_count=5, avg_duration=45.0)
        
        # Mock other users
        other_user_data = Mock()
        other_user_data.id = 2
        other_user_data.username = "otheruser"
        other_user_data.email = "other@example.com"
        other_user_data.fitness_goal = "strength"
        other_user_data.experience_level = "intermediate"
        other_user_data.height_cm = 180
        other_user_data.weight_kg = 75.0
        
        mock_db.execute.return_value.fetchall.return_value = [other_user_data]
        
        similar_users = model.find_similar_users(user, mock_db, limit=5)
        
        assert isinstance(similar_users, list)
        assert len(similar_users) > 0
        assert "user_id" in similar_users[0]
        assert "similarity_score" in similar_users[0]
    
    def test_train_model(self, db_session):
        """Test model training"""
        model = UserSimilarityModel()
        
        # Mock database session
        mock_db = Mock()
        user_data = Mock()
        user_data.id = 1
        user_data.username = "testuser"
        user_data.email = "test@example.com"
        user_data.fitness_goal = "strength"
        user_data.experience_level = "beginner"
        user_data.height_cm = 175
        user_data.weight_kg = 70.0
        
        mock_db.execute.return_value.fetchall.return_value = [user_data]
        mock_db.execute.return_value.fetchone.return_value = Mock(workout_count=5, avg_duration=45.0)
        
        # Test training
        model.train(mock_db)
        
        # Verify scaler was fitted
        assert hasattr(model.scaler, 'mean_')

class TestExerciseRecommender:
    """Test cases for ExerciseRecommender"""
    
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
        """Test getting exercise recommendations"""
        recommender = ExerciseRecommender.load_or_initialize()
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175,
            weight_kg=70.0
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
        
        recommendations = recommender.get_recommendations(user, mock_db, n_recommendations=5)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "id" in recommendations[0]
        assert "name" in recommendations[0]
        assert "score" in recommendations[0]
    
    def test_calculate_exercise_score(self, db_session):
        """Test exercise score calculation"""
        recommender = ExerciseRecommender.load_or_initialize()
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175,
            weight_kg=70.0
        )
        
        exercise = {
            "id": 1,
            "name": "Push-ups",
            "muscle_group": "Chest",
            "equipment": "Bodyweight",
            "difficulty_level": "Beginner"
        }
        
        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value.fetchone.return_value = Mock(count=0)
        
        score = recommender._calculate_exercise_score(exercise, user, mock_db)
        
        assert isinstance(score, float)
        assert score >= 0.0
    
    def test_get_recommendation_reasoning(self, db_session):
        """Test recommendation reasoning generation"""
        recommender = ExerciseRecommender.load_or_initialize()
        
        # Create test user
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            fitness_goal="strength",
            experience_level="beginner",
            height_cm=175,
            weight_kg=70.0
        )
        
        exercise = {
            "id": 1,
            "name": "Push-ups",
            "muscle_group": "Chest",
            "equipment": "Bodyweight",
            "difficulty_level": "Beginner"
        }
        
        reasoning = recommender._get_recommendation_reasoning(exercise, user, 0.8)
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0 