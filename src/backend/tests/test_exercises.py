"""
Unit tests for exercise endpoints
"""

import pytest
from fastapi import status
import uuid

def test_get_exercises(client):
    """Test getting all exercises (public endpoint)"""
    response = client.get("/api/v1/exercises")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Should have the sample exercises from init.sql
    assert len(data) >= 5

def test_get_exercises_with_filters(client):
    """Test getting exercises with filters (public endpoint)"""
    # Test muscle group filter
    response = client.get("/api/v1/exercises?muscle_group=Chest")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for exercise in data:
        assert exercise["muscle_group"] == "Chest"
    
    # Test equipment filter
    response = client.get("/api/v1/exercises?equipment=Bodyweight")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for exercise in data:
        assert exercise["equipment"] == "Bodyweight"

def test_get_exercise_by_id(client):
    """Test getting exercise by ID (public endpoint)"""
    # First get all exercises to get an ID
    response = client.get("/api/v1/exercises")
    exercises = response.json()
    
    if exercises:
        exercise_id = exercises[0]["id"]
        response = client.get(f"/api/v1/exercises/{exercise_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == exercise_id
        assert "name" in data
        assert "description" in data

def test_get_exercise_by_id_not_found(client):
    """Test getting non-existent exercise (public endpoint)"""
    response = client.get("/api/v1/exercises/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_exercise_authenticated(client, test_user_data, test_exercise_data):
    """Test creating exercise with authentication"""
    # Register and login user
    client.post("/api/v1/auth/register", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Create exercise with a unique name
    headers = {"Authorization": f"Bearer {token}"}
    unique_exercise = test_exercise_data.copy()
    unique_exercise["name"] = f"Push-ups-{uuid.uuid4()}"
    response = client.post("/api/v1/exercises", json=unique_exercise, headers=headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == unique_exercise["name"]
    assert data["primary_muscle"] == unique_exercise["primary_muscle"]

def test_create_exercise_unauthenticated(client, test_exercise_data):
    """Test creating exercise without authentication"""
    response = client.post("/api/v1/exercises", json=test_exercise_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_exercise_authenticated(client, test_user_data, test_exercise_data):
    """Test updating exercise with authentication"""
    # Register and login user
    client.post("/api/v1/auth/register", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Create exercise first with a unique name
    headers = {"Authorization": f"Bearer {token}"}
    unique_exercise = test_exercise_data.copy()
    unique_exercise["name"] = f"Push-ups-{uuid.uuid4()}"
    create_response = client.post("/api/v1/exercises", json=unique_exercise, headers=headers)
    exercise_id = create_response.json()["id"]
    
    # Update exercise
    update_data = unique_exercise.copy()
    update_data["name"] = "Updated Push-ups"
    response = client.put(f"/api/v1/exercises/{exercise_id}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Push-ups"

def test_delete_exercise_authenticated(client, test_user_data, test_exercise_data):
    """Test deleting exercise with authentication"""
    # Register and login user
    client.post("/api/v1/auth/register", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Create exercise first with a unique name
    headers = {"Authorization": f"Bearer {token}"}
    unique_exercise = test_exercise_data.copy()
    unique_exercise["name"] = f"Push-ups-{uuid.uuid4()}"
    create_response = client.post("/api/v1/exercises", json=unique_exercise, headers=headers)
    exercise_id = create_response.json()["id"]
    
    # Delete exercise
    response = client.delete(f"/api/v1/exercises/{exercise_id}", headers=headers)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify exercise is deleted
    get_response = client.get(f"/api/v1/exercises/{exercise_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND 