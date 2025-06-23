"""
Unit tests for ML service API endpoints
"""

from unittest.mock import Mock, patch

from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_get_exercise_recommendations_success(client):
    """Test successful exercise recommendations with updated user schema"""
    # Mock user data
    user_data = Mock()
    user_data.id = 1
    user_data.username = "testuser"
    user_data.email = "test@example.com"
    user_data.fitness_goal = "STRENGTH"
    user_data.experience_level = "BEGINNER"
    user_data.height_cm = 175
    user_data.weight_kg = 70.0

    # Mock database session
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = user_data

    # Patch the recommender (update path if needed)
    with patch("app.api.exercise_recommender") as mock_recommender:
        mock_recommender.get_recommendations.return_value = [
            {
                "id": 1,
                "name": "Push-ups",
                "score": 0.8,
                "reasoning": "Great for strength building",
            }
        ]

        response = client.post(
            "/recommendations/exercises?user_id=1&n_recommendations=5"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        assert data["recommendations"][0]["name"] == "Push-ups"
        assert data["recommendations"][0]["score"] == 0.8


def test_get_exercise_recommendations_user_not_found(client):
    """Test exercise recommendations with non-existent user"""
    # Mock database session to return None (user not found)
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = None

    response = client.post("/recommendations/exercises?user_id=999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_get_exercise_recommendations_ml_service_not_ready(client):
    """Test exercise recommendations when ML service is not ready"""
    # Mock user data
    user_data = Mock()
    user_data.id = 1
    user_data.username = "testuser"
    user_data.email = "test@example.com"

    # Mock database session
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = user_data

    # Mock exercise recommender to be None
    with patch("app.api.exercise_recommender", None):
        response = client.post("/recommendations/exercises?user_id=1")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "ML service not ready" in response.json()["detail"]


def test_get_similar_users_success(client):
    """Test successful similar users endpoint"""
    # Mock user data
    user_data = Mock()
    user_data.id = 1
    user_data.username = "testuser"
    user_data.email = "test@example.com"
    user_data.fitness_goal = "STRENGTH"
    user_data.experience_level = "BEGINNER"
    user_data.height_cm = 175
    user_data.weight_kg = 70.0

    # Mock database session
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = user_data

    # Mock user similarity model
    with patch("app.api.user_similarity_model") as mock_model:
        mock_model.find_similar_users.return_value = [
            {
                "user_id": 2,
                "username": "similaruser",
                "similarity_score": 0.85,
                "fitness_goal": "STRENGTH",
                "experience_level": "INTERMEDIATE",
            }
        ]

        response = client.get("/similar-users/1?limit=5")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "similar_users" in data
        assert len(data["similar_users"]) > 0


def test_get_similar_users_user_not_found(client):
    """Test similar users with non-existent user"""
    # Mock database session to return None (user not found)
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = None

    response = client.get("/similar-users/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_get_similar_users_ml_service_not_ready(client):
    """Test similar users when ML service is not ready"""
    # Mock user data
    user_data = Mock()
    user_data.id = 1
    user_data.username = "testuser"
    user_data.email = "test@example.com"

    # Mock database session
    mock_db = Mock()
    mock_db.execute.return_value.fetchone.return_value = user_data

    # Mock user similarity model to be None
    with patch("app.api.user_similarity_model", None):
        response = client.get("/similar-users/1")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "ML service not ready" in response.json()["detail"]


def test_train_models_success(client):
    """Test successful model training"""
    # Mock ML models
    with patch("app.api.user_similarity_model") as mock_similarity, patch(
        "app.api.exercise_recommender"
    ) as mock_recommender:
        response = client.post("/models/train")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Models trained successfully"

        # Verify models were called
        mock_similarity.train.assert_called_once()
        mock_recommender._build_features.assert_called_once()


def test_train_models_ml_service_not_ready(client):
    """Test model training when ML service is not ready"""
    # Mock ML models to be None
    with patch("app.api.user_similarity_model", None), patch(
        "app.api.exercise_recommender", None
    ):
        response = client.post("/models/train")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Models trained successfully"
