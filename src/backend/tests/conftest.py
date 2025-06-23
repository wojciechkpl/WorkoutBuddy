"""
Pytest configuration and fixtures for backend tests
"""

import json
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, get_db
from app.main import app
from app.models import Equipment, Exercise, ExerciseType, MuscleGroup

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for each test"""
    connection = test_db.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    # Add sample exercises
    sample_exercises = [
        Exercise(
            name="Push-ups",
            description="Classic bodyweight exercise for chest",
            primary_muscle=MuscleGroup.CHEST,
            secondary_muscles=json.dumps(["Triceps", "Shoulders"]),
            equipment=Equipment.BODYWEIGHT,
            exercise_type=ExerciseType.STRENGTH,
            difficulty=1,
            instructions="Start in plank position...",
            tips="Keep your core tight",
            video_url="https://example.com/pushups",
            is_distance_based=False,
            is_time_based=False,
            mets=4.0,
        ),
        Exercise(
            name="Squats",
            description="Lower body strength exercise",
            primary_muscle=MuscleGroup.LEGS,
            secondary_muscles=json.dumps(["Glutes", "Core"]),
            equipment=Equipment.BODYWEIGHT,
            exercise_type=ExerciseType.STRENGTH,
            difficulty=1,
            instructions="Stand with feet shoulder-width apart...",
            tips="Keep your back straight",
            video_url="https://example.com/squats",
            is_distance_based=False,
            is_time_based=False,
            mets=5.0,
        ),
        Exercise(
            name="Pull-ups",
            description="Upper body pulling exercise",
            primary_muscle=MuscleGroup.BACK,
            secondary_muscles=json.dumps(["Biceps", "Shoulders"]),
            equipment=Equipment.BODYWEIGHT,
            exercise_type=ExerciseType.STRENGTH,
            difficulty=3,
            instructions="Hang from a pull-up bar...",
            tips="Pull your shoulder blades together",
            video_url="https://example.com/pullups",
            is_distance_based=False,
            is_time_based=False,
            mets=6.0,
        ),
        Exercise(
            name="Running",
            description="Cardiovascular exercise",
            primary_muscle=MuscleGroup.LEGS,
            secondary_muscles=json.dumps(["Core"]),
            equipment=Equipment.NONE,
            exercise_type=ExerciseType.CARDIO,
            difficulty=2,
            instructions="Start with a warm-up...",
            tips="Maintain good posture",
            video_url="https://example.com/running",
            is_distance_based=True,
            is_time_based=True,
            mets=8.0,
        ),
        Exercise(
            name="Bench Press",
            description="Compound chest exercise",
            primary_muscle=MuscleGroup.CHEST,
            secondary_muscles=json.dumps(["Triceps", "Shoulders"]),
            equipment=Equipment.BARBELL,
            exercise_type=ExerciseType.STRENGTH,
            difficulty=2,
            instructions="Lie on bench with barbell...",
            tips="Keep your feet flat on the ground",
            video_url="https://example.com/benchpress",
            is_distance_based=False,
            is_time_based=False,
            mets=3.0,
        ),
    ]

    for exercise in sample_exercises:
        session.add(exercise)

    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Create test client with overridden database dependency"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "fitness_goal": "strength",
        "experience_level": "beginner",
    }


@pytest.fixture
def test_exercise_data():
    """Sample exercise data for testing"""
    return {
        "name": "Push-ups",
        "description": "Classic bodyweight exercise",
        "primary_muscle": "chest",
        "secondary_muscles": ["Triceps", "Shoulders"],
        "equipment": "bodyweight",
        "exercise_type": "strength",
        "difficulty": 1,
        "instructions": "Start in plank position...",
        "tips": "Keep your core tight",
        "video_url": "https://example.com/pushups",
        "is_distance_based": False,
        "is_time_based": False,
        "mets": 4.0,
    }
