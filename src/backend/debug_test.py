#!/usr/bin/env python3
"""
Debug script to test the personalized challenges endpoint
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from tests.conftest import create_test_user, get_test_token

# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
Base.metadata.create_all(bind=test_engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create test session
db_session = TestingSessionLocal()

# Override database dependency
app.dependency_overrides[get_db] = lambda: db_session

# Create test client
client = TestClient(app)

# Create test user and token
user = create_test_user(db_session, "user@test.com", "user")
token = get_test_token(user)

# Test the endpoint
response = client.get(
    "/api/v1/challenges/personalized",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body: {response.text}")

# Clean up
app.dependency_overrides.clear()
db_session.close() 