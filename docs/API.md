# Pulse Fitness API Documentation

## Overview

The Pulse Fitness API is a RESTful service built with FastAPI that provides comprehensive fitness tracking, social features, and ML-powered recommendations. The API supports both metric and imperial units, with automatic conversion for ML processing.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.pulsefitness.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

1. **Register**: `POST /register`
2. **Login**: `POST /login` (returns JWT token)

## API Endpoints

### Authentication

#### `POST /register`
Register a new user account.

**Request Body:**
```json
{
  "username": "fitness_user",
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "fitness_user",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### `POST /login`
Authenticate and get JWT token.

**Request Body:**
```json
{
  "username": "fitness_user",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### `GET /me`
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "fitness_user",
  "email": "user@example.com",
  "full_name": "John Doe",
  "fitness_goal": "strength",
  "experience_level": "intermediate",
  "unit_system": "IMPERIAL",
  "height_unit": "INCHES",
  "weight_unit": "LBS"
}
```

### User Management

#### `GET /users/profile`
Get current user's profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "fitness_user",
  "email": "user@example.com",
  "full_name": "John Doe",
  "fitness_goal": "strength",
  "experience_level": "intermediate",
  "unit_system": "IMPERIAL",
  "height": 70.0,
  "weight": 150.0
}
```

#### `PUT /users/profile`
Update current user's profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Smith",
  "fitness_goal": "muscle_gain",
  "experience_level": "advanced"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "fitness_user",
  "full_name": "John Smith",
  "fitness_goal": "muscle_gain",
  "experience_level": "advanced"
}
```

#### `GET /users/stats`
Get current user's fitness statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": 1,
  "total_workouts": 25,
  "total_weight_lifted": 15000.0,
  "total_cardio_distance": 150.5,
  "total_calories_burned": 12500.0,
  "personal_records": {
    "barbell_squat": {"weight": 225.0, "date": "2024-01-15"},
    "deadlift": {"weight": 315.0, "date": "2024-01-20"}
  }
}
```

#### `GET /users/{user_id}`
Get public profile of another user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 2,
  "username": "fitness_buddy",
  "full_name": "Jane Doe",
  "fitness_goal": "endurance",
  "experience_level": "beginner"
}
```

#### `GET /users/search/{username}`
Search users by username.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "username": "fitness_buddy",
    "full_name": "Jane Doe"
  }
]
```

### Workout Management

#### `POST /workouts/`
Create a new workout.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Upper Body Strength",
  "description": "Focus on chest, shoulders, and arms",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "exercises": [
    {
      "exercise_id": 1,
      "order": 1,
      "sets": 3,
      "reps": "8-12",
      "weight": "135",
      "rest_time": 90
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "Upper Body Strength",
  "description": "Focus on chest, shoulders, and arms",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "status": "PLANNED",
  "exercises": [...]
}
```

#### `GET /workouts/`
Get user's workouts with optional filters.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (optional): Filter workouts from this date
- `end_date` (optional): Filter workouts until this date
- `status` (optional): Filter by status (PLANNED, IN_PROGRESS, COMPLETED, CANCELLED)
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 50, max: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Upper Body Strength",
    "scheduled_date": "2024-01-20T14:00:00Z",
    "status": "COMPLETED",
    "total_duration": 75,
    "calories_burned": 450.0
  }
]
```

#### `GET /workouts/stats`
Get workout statistics for the user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `days` (optional): Number of days to analyze (default: 30, max: 365)

**Response:** `200 OK`
```json
{
  "total_workouts": 25,
  "completed_workouts": 22,
  "total_duration": 1650,
  "total_calories_burned": 12500.0,
  "average_duration": 66.0,
  "favorite_exercises": ["Barbell Squat", "Deadlift", "Bench Press"]
}
```

#### `GET /workouts/upcoming`
Get upcoming scheduled workouts.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `days` (optional): Number of days ahead to look (default: 7, max: 30)

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "name": "Lower Body Power",
    "scheduled_date": "2024-01-22T16:00:00Z",
    "status": "PLANNED"
  }
]
```

#### `GET /workouts/{workout_id}`
Get a specific workout.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Upper Body Strength",
  "description": "Focus on chest, shoulders, and arms",
  "scheduled_date": "2024-01-20T14:00:00Z",
  "started_at": "2024-01-20T14:05:00Z",
  "completed_at": "2024-01-20T15:20:00Z",
  "status": "COMPLETED",
  "total_duration": 75,
  "calories_burned": 450.0,
  "exercises": [
    {
      "id": 1,
      "exercise_id": 1,
      "name": "Barbell Bench Press",
      "sets": 3,
      "reps": "8-12",
      "weight": "135",
      "actual_reps": "10,8,6",
      "actual_weight": "135,135,135"
    }
  ]
}
```

#### `PUT /workouts/{workout_id}`
Update a workout.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Workout Name",
  "status": "IN_PROGRESS"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Updated Workout Name",
  "status": "IN_PROGRESS",
  "started_at": "2024-01-20T14:05:00Z"
}
```

#### `POST /workouts/{workout_id}/start`
Start a workout.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "IN_PROGRESS",
  "started_at": "2024-01-20T14:05:00Z"
}
```

#### `POST /workouts/{workout_id}/complete`
Complete a workout.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "notes": "Great workout! Felt strong today."
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "status": "COMPLETED",
  "completed_at": "2024-01-20T15:20:00Z",
  "total_duration": 75,
  "calories_burned": 450.0
}
```

#### `PUT /workouts/{workout_id}/exercises/{exercise_id}`
Update a specific exercise in a workout.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "actual_reps": "10,8,6",
  "actual_weight": "135,135,135",
  "notes": "Felt heavy on the last set"
}
```

**Response:** `200 OK`
```json
{
  "message": "Exercise updated successfully"
}
```

#### `DELETE /workouts/{workout_id}`
Delete a workout.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Workout deleted successfully"
}
```

### Exercise Management

#### `GET /exercises/`
Get exercises with optional filters.

**Query Parameters:**
- `muscle_group` (optional): Filter by primary muscle group
- `equipment` (optional): Filter by equipment type
- `exercise_type` (optional): Filter by exercise type
- `difficulty_min` (optional): Minimum difficulty (1-5)
- `difficulty_max` (optional): Maximum difficulty (1-5)
- `search` (optional): Search in name and description
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 50, max: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Barbell Bench Press",
    "description": "Compound chest exercise",
    "primary_muscle": "CHEST",
    "secondary_muscles": ["TRICEPS", "SHOULDERS"],
    "equipment": "BARBELL",
    "exercise_type": "STRENGTH",
    "difficulty": 3,
    "instructions": "Lie on bench, lower bar to chest...",
    "video_url": "https://example.com/video1"
  }
]
```

#### `GET /exercises/muscle-groups`
Get all available muscle groups.

**Response:** `200 OK`
```json
[
  "LEGS", "CORE", "BACK", "SHOULDERS", 
  "FULL_BODY", "CHEST", "TRICEPS", "BICEPS", "GLUTES"
]
```

#### `GET /exercises/equipment`
Get all available equipment types.

**Response:** `200 OK`
```json
[
  "NONE", "DUMBBELL", "BARBELL", "OTHER", 
  "CABLE", "KETTLEBELL", "MACHINE", "BANDS"
]
```

#### `GET /exercises/{exercise_id}`
Get a specific exercise.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Barbell Bench Press",
  "description": "Compound chest exercise",
  "primary_muscle": "CHEST",
  "secondary_muscles": ["TRICEPS", "SHOULDERS"],
  "equipment": "BARBELL",
  "exercise_type": "STRENGTH",
  "difficulty": 3,
  "instructions": "Lie on bench, lower bar to chest...",
  "tips": "Keep your feet flat on the ground...",
  "video_url": "https://example.com/video1"
}
```

#### `POST /exercises/`
Create a new exercise (authenticated).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Custom Exercise",
  "description": "A custom exercise",
  "primary_muscle": "CHEST",
  "secondary_muscles": ["TRICEPS"],
  "equipment": "DUMBBELL",
  "exercise_type": "STRENGTH",
  "difficulty": 2,
  "instructions": "Step-by-step instructions...",
  "tips": "Helpful tips..."
}
```

**Response:** `201 Created`
```json
{
  "id": 158,
  "name": "Custom Exercise",
  "description": "A custom exercise",
  "primary_muscle": "CHEST",
  "secondary_muscles": ["TRICEPS"],
  "equipment": "DUMBBELL",
  "exercise_type": "STRENGTH",
  "difficulty": 2
}
```

#### `PUT /exercises/{exercise_id}`
Update an exercise (authenticated).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "description": "Updated description",
  "difficulty": 3
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Barbell Bench Press",
  "description": "Updated description",
  "difficulty": 3
}
```

#### `DELETE /exercises/{exercise_id}`
Delete an exercise (authenticated).

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

#### `GET /exercises/{exercise_id}/history`
Get user's history with a specific exercise.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `days` (optional): Number of days to look back (default: 30, max: 365)

**Response:** `200 OK`
```json
{
  "exercise_id": 1,
  "exercise_name": "Barbell Bench Press",
  "total_workouts": 15,
  "total_sets": 45,
  "max_weight": 185.0,
  "progress_data": [
    {
      "date": "2024-01-15",
      "max_weight": 185.0,
      "total_volume": 5550.0
    }
  ]
}
```

### ML Recommendations

#### `GET /recommendations/exercises/{user_id}`
Get exercise recommendations for a user.

**Query Parameters:**
- `n_recommendations` (optional): Number of recommendations (default: 10)

**Response:** `200 OK`
```json
[
  {
    "exercise_id": 1,
    "name": "Barbell Bench Press",
    "primary_muscle": "CHEST",
    "equipment": "BARBELL",
    "difficulty": 3,
    "predicted_rating": 4.2
  }
]
```

#### `GET /recommendations/similar-users/{user_id}`
Get similar users based on user features.

**Query Parameters:**
- `n_recommendations` (optional): Number of recommendations (default: 5)

**Response:** `200 OK`
```json
[
  {
    "user_id": 2,
    "username": "fitness_buddy",
    "fitness_goal": "strength",
    "experience_level": "intermediate",
    "similarity_score": 0.85
  }
]
```

#### `POST /recommendations/train-models`
Train ML models with current data.

**Response:** `200 OK`
```json
{
  "message": "ML models trained successfully"
}
```

#### `GET /recommendations/ml-status`
Get ML service status and model information.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "models": {
    "user_similarity": "loaded",
    "exercise_recommender": "loaded"
  },
  "last_training": "2024-01-15T10:00:00Z"
}
```

### Social Features

#### `POST /social/friends/request/{username}`
Send a friend request to another user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Friend request sent successfully"
}
```

#### `PUT /social/friends/accept/{friendship_id}`
Accept a friend request.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Friend request accepted"
}
```

#### `PUT /social/friends/reject/{friendship_id}`
Reject a friend request.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Friend request rejected"
}
```

#### `GET /social/friends`
Get current user's friends.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "username": "fitness_buddy",
    "full_name": "Jane Doe",
    "fitness_goal": "endurance"
  }
]
```

#### `GET /social/friends/requests`
Get pending friend requests for current user.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "id": 3,
    "username": "new_friend",
    "full_name": "Bob Smith"
  }
]
```

### Challenges

#### `GET /challenges/`
Get all challenges.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "30-Day Push-up Challenge",
    "description": "Complete 100 push-ups daily for 30 days",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-30T23:59:59Z",
    "participants": 25
  }
]
```

#### `POST /challenges/`
Create a new challenge.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Squat Challenge",
  "description": "Complete 50 squats daily",
  "start_date": "2024-02-01T00:00:00Z",
  "end_date": "2024-02-28T23:59:59Z"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "Squat Challenge",
  "description": "Complete 50 squats daily",
  "start_date": "2024-02-01T00:00:00Z",
  "end_date": "2024-02-28T23:59:59Z",
  "created_by": 1
}
```

#### `GET /challenges/{challenge_id}`
Get a specific challenge.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "30-Day Push-up Challenge",
  "description": "Complete 100 push-ups daily for 30 days",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-30T23:59:59Z",
  "participants": 25,
  "leaderboard": [
    {
      "user_id": 1,
      "username": "fitness_user",
      "progress": 85
    }
  ]
}
```

#### `PUT /challenges/{challenge_id}`
Update a challenge.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "description": "Updated challenge description"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "30-Day Push-up Challenge",
  "description": "Updated challenge description"
}
```

#### `DELETE /challenges/{challenge_id}`
Delete a challenge.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "message": "Challenge deleted successfully"
}
```

## Error Responses

All endpoints may return the following error responses:

### `400 Bad Request`
```json
{
  "detail": "Validation error message"
}
```

### `401 Unauthorized`
```json
{
  "detail": "Could not validate credentials"
}
```

### `403 Forbidden`
```json
{
  "detail": "Insufficient permissions"
}
```

### `404 Not Found`
```json
{
  "detail": "Resource not found"
}
```

### `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### `500 Internal Server Error`
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Authentication endpoints**: 5 requests per minute
- **Other endpoints**: 100 requests per minute per user

When rate limited, you'll receive a `429 Too Many Requests` response.

## Unit System Support

The API supports both metric and imperial units:

- **User preferences**: Stored in user profile (`unit_system`, `height_unit`, `weight_unit`)
- **Input**: Accepts values in user's preferred units
- **Storage**: Converts to metric for ML processing, stores in user's units
- **Output**: Returns values in user's preferred units
- **ML**: All ML models use metric units internally

## Pagination

List endpoints support pagination with `skip` and `limit` parameters:

```json
{
  "data": [...],
  "total": 150,
  "skip": 0,
  "limit": 50,
  "has_more": true
}
```

## Health Check

#### `GET /health`
Check API health status.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

## SDKs and Libraries

- **Python**: Use `requests` or `httpx` for HTTP calls
- **JavaScript/TypeScript**: Use `fetch` or `axios`
- **Flutter**: Use `http` package
- **Postman**: Import OpenAPI spec from `/docs`

## OpenAPI Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json` 