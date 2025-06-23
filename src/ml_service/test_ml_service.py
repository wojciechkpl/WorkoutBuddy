"""
Test script for the new stateless ML service
"""


import requests

# Test data
test_users_data = [
    {
        "id": 1,
        "age": 25,
        "height": 175,
        "weight": 70,
        "fitness_goal": "muscle_gain",
        "experience_level": "intermediate",
    },
    {
        "id": 2,
        "age": 30,
        "height": 180,
        "weight": 80,
        "fitness_goal": "strength",
        "experience_level": "advanced",
    },
    {
        "id": 3,
        "age": 22,
        "height": 165,
        "weight": 55,
        "fitness_goal": "weight_loss",
        "experience_level": "beginner",
    },
]

test_interactions_data = [
    {"user_id": 1, "exercise_id": 1, "rating": 4.5},
    {"user_id": 1, "exercise_id": 2, "rating": 3.0},
    {"user_id": 2, "exercise_id": 1, "rating": 5.0},
    {"user_id": 2, "exercise_id": 3, "rating": 4.0},
    {"user_id": 3, "exercise_id": 2, "rating": 2.5},
    {"user_id": 3, "exercise_id": 4, "rating": 3.5},
]

test_exercise_ids = [1, 2, 3, 4, 5]


def test_ml_service():
    """Test the ML service endpoints"""
    base_url = "http://localhost:8000"

    print("Testing ML Service...")

    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # Test model status
    try:
        response = requests.get(f"{base_url}/models/status")
        print(f"Model status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Model status failed: {e}")

    # Test training user similarity model
    try:
        training_data = {
            "users_data": test_users_data,
            "interactions_data": test_interactions_data,
            "exercise_ids": test_exercise_ids,
        }
        response = requests.post(
            f"{base_url}/train/user-similarity", json=training_data
        )
        print(f"Train user similarity: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Train user similarity failed: {e}")

    # Test training exercise recommender
    try:
        training_data = {
            "users_data": test_users_data,
            "interactions_data": test_interactions_data,
            "exercise_ids": test_exercise_ids,
        }
        response = requests.post(
            f"{base_url}/train/exercise-recommender", json=training_data
        )
        print(f"Train exercise recommender: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Train exercise recommender failed: {e}")

    # Test getting similar users
    try:
        user_features = [
            25.0,
            175.0,
            70.0,
            1.0,
            1.0,
        ]  # Age, height, weight, goal, level
        request_data = {
            "user_features": user_features,
            "user_id": 1,
            "n_recommendations": 2,
        }
        response = requests.post(
            f"{base_url}/recommendations/similar-users", json=request_data
        )
        print(f"Similar users: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Similar users failed: {e}")

    # Test getting exercise recommendations
    try:
        user_interactions = [1.0, 1.0, 0.0, 0.0, 0.0]  # User has done exercises 1 and 2
        request_data = {
            "user_id": 1,
            "user_interactions": user_interactions,
            "n_recommendations": 3,
        }
        response = requests.post(
            f"{base_url}/recommendations/exercises", json=request_data
        )
        print(f"Exercise recommendations: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Exercise recommendations failed: {e}")

    # Test saving models
    try:
        response = requests.post(f"{base_url}/models/save")
        print(f"Save models: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Save models failed: {e}")


if __name__ == "__main__":
    test_ml_service()
