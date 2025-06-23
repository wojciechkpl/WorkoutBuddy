"""
Unit tests for authentication endpoints
"""

from fastapi import status


def test_register_user_success(client, test_user_data):
    """Test successful user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "password" not in data  # Password should not be returned


def test_register_user_duplicate_username(client, test_user_data):
    """Test registration with duplicate username"""
    # Register first user
    client.post("/api/v1/auth/register", json=test_user_data)

    # Try to register with same username
    duplicate_data = test_user_data.copy()
    duplicate_data["email"] = "different@example.com"
    response = client.post("/api/v1/auth/register", json=duplicate_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username already registered" in response.json()["detail"]


def test_register_user_duplicate_email(client, test_user_data):
    """Test registration with duplicate email"""
    # Register first user
    client.post("/api/v1/auth/register", json=test_user_data)

    # Try to register with same email
    duplicate_data = test_user_data.copy()
    duplicate_data["username"] = "differentuser"
    response = client.post("/api/v1/auth/register", json=duplicate_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email already registered" in response.json()["detail"]


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user_data):
    """Test login with invalid credentials"""
    # Register user first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Try to login with wrong password
    login_data = {"username": test_user_data["username"], "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user(client, test_user_data):
    """Test getting current user with valid token"""
    # Register and login user
    client.post("/api/v1/auth/register", json=test_user_data)
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_no_token(client):
    """Test getting current user without token"""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
