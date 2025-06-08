"""
Test suite for WorkoutBuddy ML Backend API endpoints
"""

import pytest
import requests
import json
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_ID = 1


class TestMLPredictionAPI:
    """Test class for ML prediction endpoints"""

    def test_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "WorkoutBuddy" in data["message"]

    def test_workout_plan_prediction(self):
        """Test personalized workout plan generation"""
        payload = {
            "user_id": TEST_USER_ID,
            "duration_weeks": 4,
            "workout_days_per_week": 3,
            "session_duration_minutes": 45,
            "equipment_available": ["bodyweight", "dumbbells"],
            "fitness_goals": ["muscle_gain", "strength"],
        }

        response = requests.post(f"{API_BASE_URL}/predict/workout-plan", json=payload)

        # Should return 200 or 404 (if user doesn't exist)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert "plan_id" in data
            assert "exercises" in data
            assert "weekly_schedule" in data
            assert data["duration_weeks"] == 4

    def test_community_matches(self):
        """Test community matching algorithm"""
        payload = {
            "user_id": TEST_USER_ID,
            "max_matches": 5,
            "location_radius_km": 10,
            "compatibility_threshold": 0.7,
        }

        response = requests.post(
            f"{API_BASE_URL}/predict/community-matches", json=payload
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 5

            if data:  # If matches found
                match = data[0]
                assert "user_id" in match
                assert "compatibility_score" in match
                assert "match_reasons" in match

    def test_exercise_recommendations(self):
        """Test exercise recommendation system"""
        payload = {
            "user_id": TEST_USER_ID,
            "muscle_groups": ["chest", "shoulders"],
            "equipment_available": ["bodyweight"],
            "difficulty_level": "intermediate",
            "max_recommendations": 10,
        }

        response = requests.post(
            f"{API_BASE_URL}/predict/exercise-recommendations", json=payload
        )

        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 10

            if data:  # If recommendations found
                exercise = data[0]
                assert "exercise_id" in exercise
                assert "name" in exercise
                assert "recommendation_score" in exercise
                assert "muscle_groups" in exercise

    def test_invalid_user_id(self):
        """Test API behavior with invalid user ID"""
        payload = {
            "user_id": 99999,  # Non-existent user
            "duration_weeks": 4,
        }

        response = requests.post(f"{API_BASE_URL}/predict/workout-plan", json=payload)

        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]

    def test_malformed_request(self):
        """Test API behavior with malformed requests"""
        # Missing required fields
        payload = {}

        response = requests.post(f"{API_BASE_URL}/predict/workout-plan", json=payload)

        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    # Run basic tests
    test_api = TestMLPredictionAPI()

    print("🧪 Running ML Backend API Tests")
    print("=" * 40)

    try:
        test_api.test_health_check()
        print("✅ Health check test passed")
    except Exception as e:
        print(f"❌ Health check test failed: {e}")

    try:
        test_api.test_invalid_user_id()
        print("✅ Invalid user ID test passed")
    except Exception as e:
        print(f"❌ Invalid user ID test failed: {e}")

    try:
        test_api.test_malformed_request()
        print("✅ Malformed request test passed")
    except Exception as e:
        print(f"❌ Malformed request test failed: {e}")

    print("\n🎉 Basic tests completed!")
