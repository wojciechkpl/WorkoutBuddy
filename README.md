# Pulse Fitness - Modular Microservices Architecture (2024)

A modern fitness application built with a modular, microservices architecture using Docker containers and integrated ML services.

---

## 🏗️ Modular Architecture Overview

- **Backend API** (FastAPI, src/backend): Core business logic, user/social/workout/safety endpoints, DI, config, and monitoring
- **ML Service** (FastAPI, src/ml_service): ML recommendations, moderation, analytics, stateless, versioned
- **Mobile/Web** (Flutter, src/mobile): User interface, multiplatform, Dockerized for web
- **Database** (PostgreSQL): Data persistence, metric/imperial support, test data separation
- **Redis**: Caching, session storage
- **Nginx** (optional): Reverse proxy, load balancer

---

## 🐳 Docker & Compose Usage

- All services are containerized and orchestrated via `docker-compose.yml`
- **Build & Run (dev/prod):**
  ```bash
  # Start all services
  docker-compose up --build -d
  # Stop all
  docker-compose down
  ```
- **Healthchecks:** All containers expose `/health` endpoints and are checked by Docker Compose
- **Volumes:** Data (Postgres, Redis) and ML models are persisted via named volumes
- **Environment:** All config/secrets via env vars (see `.envrc`)

---

## 🧩 Service Boundaries & Extensibility

- **Backend**: Modular DI, config, and service registration. Add new services in `app/services/`, register in DI.
- **ML Service**: Add new models or endpoints in `ml_service/app/`.
- **Mobile**: Add new screens/providers in `mobile/lib/`.
- **Infra**: Add new containers/services in `docker-compose.yml`.

---

## 🩺 Healthchecks & Monitoring
- All services expose `/health` endpoints
- Docker Compose and K8s configs use these for orchestration
- Monitoring hooks in backend for ML, DB, and cache health

---

## 🧪 Testing & Synthetic Data
- Full test suite: `pytest -v` (see `src/backend/tests/`)
- Synthetic test data covers all user journey flows, including safety, privacy, ML feedback, accountability, and community
- Test data is separated by annotation for easy cleanup

---

## 🛠️ Troubleshooting
- **ModuleNotFoundError: No module named 'app'**: Ensure you use the correct working directory and PYTHONPATH in Docker/Compose. The backend expects `/app` as the root in the container.
- **Port conflicts**: Make sure ports 8000 (backend), 8001 (ML), 5432 (db), 6379 (redis) are free or adjust in `docker-compose.yml`.
- **Database migrations**: Use Alembic or manual SQL for schema changes. See `src/backend/alembic/`.

---

## 📂 Project Structure (2024)

```
project-root/
  backend/              # FastAPI backend
    app/
      api/              # API endpoints
      core/             # DI, config, bootstrap
      models/           # SQLAlchemy models
      repositories/     # Data access
      schemas/          # Pydantic schemas
      services/         # Business logic, ML, external
      utils/            # Utilities
    tests/              # Unit/integration tests
    Dockerfile
  ml_service/           # ML microservice
    app/
    models/
    data/
    Dockerfile
  mobile/               # Flutter app
    lib/
    Dockerfile
  docs/                 # Architecture, DB, user journey, units
  docker-compose.yml
  ...
```

---

## For more, see `/docs` for detailed architecture, DB, and user journey diagrams.

## 🗄️ Database Schema

The application uses PostgreSQL with the following schema design:

```mermaid
erDiagram
    users {
        integer id PK
        varchar email UK
        varchar username UK
        varchar hashed_password
        varchar full_name
        boolean is_active
        boolean is_verified
        integer age
        double_precision height
        double_precision weight
        enum fitness_goal
        enum experience_level
        timestamp created_at
        timestamp updated_at
    }

    user_goals {
        integer id PK
        integer user_id FK
        varchar goal_type
        double_precision target_value
        double_precision current_value
        timestamp target_date
        boolean is_achieved
        timestamp created_at
        timestamp achieved_at
    }

    user_stats {
        integer id PK
        integer user_id FK
        timestamp date
        double_precision weight
        double_precision body_fat_percentage
        double_precision muscle_mass
        integer total_workouts
        double_precision total_weight_lifted
        double_precision total_cardio_distance
        double_precision total_calories_burned
        text personal_records
    }

    workouts {
        integer id PK
        integer user_id FK
        varchar name
        text description
        timestamp scheduled_date
        timestamp started_at
        timestamp completed_at
        enum status
        integer total_duration
        double_precision calories_burned
        double_precision total_volume
        double_precision total_distance
        text notes
        timestamp created_at
        timestamp updated_at
    }

    workout_exercises {
        integer id PK
        integer workout_id FK
        integer exercise_id FK
        integer order
        integer sets
        varchar reps
        varchar weight
        integer duration
        double_precision distance
        double_precision speed
        double_precision incline
        integer rest_time
        varchar actual_reps
        varchar actual_weight
        text notes
    }

    exercises {
        integer id PK
        varchar name
        text description
        enum primary_muscle
        varchar secondary_muscles
        enum equipment
        enum exercise_type
        integer difficulty
        text instructions
        text tips
        varchar video_url
        boolean is_distance_based
        boolean is_time_based
        double_precision mets
    }

    friendships {
        integer id PK
        integer user_id FK
        integer friend_id FK
        boolean is_accepted
        timestamp created_at
        timestamp accepted_at
    }

    %% Relationships
    users ||--o{ user_goals : "has"
    users ||--o{ user_stats : "tracks"
    users ||--o{ workouts : "creates"
    users ||--o{ friendships : "initiates"
    users ||--o{ friendships : "receives"
    workouts ||--o{ workout_exercises : "contains"
    exercises ||--o{ workout_exercises : "used_in"
```

### 📊 Database Statistics

- **Total Tables**: 7
- **Total Exercises**: 157
- **Primary Muscle Groups**: 9 (LEGS, CORE, BACK, SHOULDERS, FULL_BODY, CHEST, TRICEPS, BICEPS, GLUTES)
- **Equipment Types**: 8 (NONE, DUMBBELL, BARBELL, OTHER, CABLE, KETTLEBELL, MACHINE, BANDS)

### 🔗 Key Relationships

1. **User Management**: Users can have multiple goals, stats, and workouts
2. **Workout Tracking**: Workouts contain multiple exercises with specific parameters
3. **Social Features**: Users can form friendships with other users
4. **Progress Tracking**: User stats track fitness progress over time
5. **Exercise Library**: Comprehensive exercise database with detailed metadata

### 🎯 Data Enums

**Fitness Goals**: `strength`, `endurance`, `weight_loss`, `muscle_gain`, `general_fitness`
**Experience Levels**: `beginner`, `intermediate`, `advanced`
**Primary Muscles**: `LEGS`, `CORE`, `BACK`, `SHOULDERS`, `FULL_BODY`, `CHEST`, `TRICEPS`, `BICEPS`, `GLUTES`
**Equipment**: `NONE`, `DUMBBELL`, `BARBELL`, `OTHER`, `CABLE`, `KETTLEBELL`, `MACHINE`, `BANDS`
**Exercise Types**: `STRENGTH`, `CARDIO`, `FLEXIBILITY`, `BALANCE`
**Workout Status**: `scheduled`, `in_progress`, `completed`, `cancelled`

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for easier management)

### Environment Setup

1. **Load environment variables**
   ```bash
   # If using direnv
   direnv allow

   # Or manually source the file
   source .envrc
   ```

2. **Start all services**
   ```bash
   make up
   # or
   docker-compose up -d
   ```

3. **Check service status**
   ```bash
   make status
   # or
   docker-compose ps
   ```

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - ML Service: http://localhost/ml
   - API Documentation: http://localhost/api/docs

## 📁 Project Structure

```
WorkoutBuddy/
├── docker-compose.yml          # Main Docker Compose configuration
├── nginx.conf                  # Nginx reverse proxy configuration
├── Makefile                    # Management commands
├── .envrc                      # Environment variables
├── README.md                   # This file
└── src/
    ├── backend/                # Backend API service
    │   ├── app/
    │   ├── tests/              # Backend unit tests
    │   ├── Dockerfile
    │   ├── Requirements.txt
    │   ├── pytest.ini
    │   └── init.sql
    ├── ml_service/             # ML Service
    │   ├── app/
    │   ├── tests/              # ML service unit tests
    │   ├── models/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── pytest.ini
    │   └── main.py
    └── mobile/                 # Flutter frontend
        ├── lib/
        ├── Dockerfile
        ├── nginx.conf
        └── pubspec.yaml
```

## 🔧 Service Details

### Backend API Service
- **Port**: 8000
- **Technology**: FastAPI, SQLAlchemy, PostgreSQL
- **Features**: User management, workout tracking, social features
- **Health Check**: `GET /health`

### ML Service
- **Port**: 8001
- **Technology**: FastAPI, scikit-learn, PyTorch
- **Features**: Exercise recommendations, user similarity, analytics
- **Health Check**: `GET /health`

### Frontend
- **Port**: 8080 (internal), 80 (external)
- **Technology**: Flutter Web, Nginx
- **Features**: Responsive web interface

### Database
- **Port**: 5432
- **Technology**: PostgreSQL 15
- **Features**: ACID compliance, JSON support, full-text search

### Redis
- **Port**: 6379
- **Technology**: Redis 7
- **Features**: Caching, session storage, rate limiting

## 🛠️ Management Commands

### Using Makefile (Recommended)
```bash
make help          # Show all available commands
make build         # Build all Docker images
make up            # Start all services
make down          # Stop all services
make logs          # Show logs from all services
make clean         # Remove all containers and volumes
make restart       # Restart all services
make status        # Show service status
```

### Using Docker Compose Directly
```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # Follow logs
docker-compose ps                 # Show status
docker-compose restart            # Restart services
```

### Service-Specific Commands
```bash
make backend       # Show backend logs
make ml           # Show ML service logs
make frontend     # Show frontend logs
make db           # Show database logs
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run ML service tests only
make test-ml

# Run tests locally (without Docker)
make test-backend-local
make test-ml-local
```

### Test Coverage

Tests are configured to generate coverage reports:
- **Backend**: Minimum 70% coverage required
- **ML Service**: Minimum 70% coverage required
- **Reports**: Generated in HTML format in `htmlcov/` directory

### Test Structure

#### Backend Tests
- **Unit Tests**: `src/backend/tests/test_*.py`
- **Fixtures**: `src/backend/tests/conftest.py`
- **Coverage**: Tests all API endpoints, models, and services

#### ML Service Tests
- **Unit Tests**: `src/ml_service/tests/test_*.py`
- **Fixtures**: `src/ml_service/tests/conftest.py`
- **Coverage**: Tests ML models, API endpoints, and data processing

### Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## 🔍 Monitoring and Debugging

### Health Checks
```bash
make health       # Check all service health endpoints
```

### Database Management
```bash
make db-migrate   # Run database migrations
make db-rollback  # Rollback last migration
make db-reset     # Reset database (WARNING: deletes all data)
```

### ML Service Management
```bash
make ml-train     # Trigger model training
```

## 🔐 Environment Variables

The application uses `.envrc` for environment variable management:

```bash
# Database
export DATABASE_URL="postgresql://pulse:pulse123@localhost:5432/pulse_fitness"

# Redis
export REDIS_URL="redis://localhost:6379"

# API Keys
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export POSTHOG_API_KEY="your-posthog-api-key"

# Security
export SECRET_KEY="your-super-secret-key-here-change-this-in-production"

# Service URLs
export ML_SERVICE_URL="http://localhost:8001"
export BACKEND_API_URL="http://localhost:8000"

# Logging
export LOG_LEVEL="INFO"

# Development
export DEBUG="false"
```

**Important**: Replace placeholder values with your actual API keys and secrets.

## 📊 API Endpoints

### Backend API
- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /users/me` - Get current user
- `GET /workouts` - Get user workouts
- `POST /workouts` - Create workout
- `GET /exercises` - Get exercises

### ML Service
- `GET /health` - Health check
- `POST /recommendations/exercises` - Get exercise recommendations
- `GET /similar-users/{user_id}` - Find similar users
- `POST /models/train` - Train ML models

## 🚀 Deployment

### Development
```bash
make dev-build
make dev-up
```

### Production
```bash
make prod-build
make prod-up
```

## 🔧 Development

### Adding New Services
1. Create service directory in `src/`
2. Add Dockerfile for the service
3. Update `docker-compose.yml`
4. Add service to Makefile commands

### Database Migrations
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
make db-migrate
```

### Testing
```bash
# Run backend tests
docker-compose exec backend pytest

# Run ML service tests
docker-compose exec ml-service pytest
```

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80, 8000, 8001, 5432, 6379 are available
2. **Database connection**: Wait for database to be ready before starting other services
3. **ML model loading**: Check ML service logs for model initialization issues
4. **Environment variables**: Ensure `.envrc` is loaded or environment variables are set

### Logs
```bash
# View all logs
make logs

# View specific service logs
make backend
make ml
make frontend
```

### Reset Everything
```bash
make clean
make build
make up
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`make test`)
6. Test with Docker Compose
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
