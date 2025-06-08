# 🏋️ WorkoutBuddy - AI-Powered Fitness Platform

**WorkoutBuddy** is an intelligent fitness platform that combines machine learning with social features to create personalized workout experiences. The platform uses AI to generate custom workout plans, match users with compatible workout partners, and provide intelligent exercise recommendations.

## 🏗️ Repository Structure

```
WorkoutBuddy/
├── ml_backend/                 # Python ML models and FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── api/
│   │   │   └── endpoints.py   # API routes for ML model serving
│   │   ├── core/
│   │   │   ├── model.py       # ML model loading & inference
│   │   │   ├── preprocess.py  # Input data transformation
│   │   │   ├── postprocess.py # Output formatting
│   │   │   ├── models.py      # Database models
│   │   │   └── schemas.py     # Pydantic schemas
│   │   ├── services/          # Business logic services
│   │   ├── alembic/           # Database migrations
│   │   └── data/              # Exercise data and seed files
│   ├── models/                # Trained ML models
│   ├── requirements.txt
│   └── Dockerfile
├── flutter_app/               # Flutter mobile/web application (future)
├── deploy/                    # Deployment configurations
│   ├── docker-compose.yml     # Local development environment
│   ├── start_dev.sh          # Development startup script
│   └── cloud/                # Cloud deployment configs
├── docs/                      # Documentation and analysis
│   ├── notebooks/            # Jupyter notebooks for ML experiments
│   └── reports/              # Analysis reports
├── tests/                     # Test suites
│   ├── python_api/           # Backend API tests
│   └── flutter_e2e/          # End-to-end tests (future)
└── README.md
```

## 🚀 Features

- **🤖 AI-Powered Workout Plans**: Personalized workout generation using machine learning
- **👥 Smart Community Matching**: Find compatible workout partners using similarity algorithms
- **📊 Intelligent Exercise Recommendations**: AI-driven exercise suggestions based on goals and preferences
- **📈 Progress Analytics**: Track and analyze fitness progress with ML insights
- **🎯 A/B Testing Framework**: Built-in experimentation for feature optimization
- **🔄 Real-time Adaptations**: Dynamic workout adjustments based on performance

## 🛠️ Technology Stack

### Backend (ML & API)
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Primary database for user data and analytics
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management
- **Scikit-learn & PyTorch**: Machine learning frameworks
- **Anthropic Claude**: AI-powered content generation
- **PostHog**: Analytics and user behavior tracking
- **Redis**: Caching and session management

### Infrastructure
- **Docker**: Containerization for consistent environments
- **Docker Compose**: Local development orchestration
- **Railway**: Cloud deployment platform
- **Jupyter**: ML experimentation and analysis

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL (if running without Docker)

> **💡 Configuration Note**: WorkoutBuddy uses a hybrid approach where API keys are loaded from environment variables (for security) while other settings are in config files (for simplicity). See the [Environment Variables & API Keys](#-environment-variables--api-keys) section for setup.

### 1. Clone and Setup
```bash
git clone <repository-url>
cd WorkoutBuddy

# Set up your API keys (see Environment Variables section)
# Create .envrc file with your API keys
```

### 2. Start Development Environment
```bash
cd deploy
./start_dev.sh
```

This script will:
- Start PostgreSQL database
- Build and run the ML backend
- Set up Redis for caching
- Launch Jupyter Lab for ML development
- Run database migrations
- Import exercise data

### 3. Access Services
- **🌐 ML Backend API**: http://localhost:8000
- **📊 API Documentation**: http://localhost:8000/docs
- **🗄️ Database**: localhost:5432 (admin/mypassword)
- **🔴 Redis**: localhost:6379
- **📔 Jupyter Lab**: http://localhost:8888

## 🧪 API Usage Examples

### Health Check
```bash
curl http://localhost:8000/
```

### Generate Personalized Workout Plan
```bash
curl -X POST "http://localhost:8000/predict/workout-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "duration_weeks": 4,
    "workout_days_per_week": 3,
    "equipment_available": ["bodyweight", "dumbbells"],
    "fitness_goals": ["muscle_gain"]
  }'
```

### Find Community Matches
```bash
curl -X POST "http://localhost:8000/predict/community-matches" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "max_matches": 5,
    "compatibility_threshold": 0.7
  }'
```

### Get Exercise Recommendations
```bash
curl -X POST "http://localhost:8000/predict/exercise-recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "muscle_groups": ["chest", "shoulders"],
    "equipment_available": ["bodyweight"],
    "difficulty_level": "intermediate"
  }'
```

## 🧪 Testing

### Run API Tests
```bash
cd tests/python_api
python test_predict.py
```

### Run with pytest
```bash
cd tests/python_api
pytest test_predict.py -v
```

## 🔧 Development

### Local Development (without Docker)
```bash
cd ml_backend

# Install dependencies
pip install -r requirements.txt

# Set up API keys (create .envrc file with direnv)
# See "Environment Variables & API Keys" section below

# Set Python path
export PYTHONPATH="$(pwd)"

# Run migrations (database URL is configured in config.yaml)
alembic upgrade head

# Import exercise data
python -m app.import_exercises

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations
```bash
# Connect to database
docker-compose exec db psql -U admin -d workoutbuddy

# Run migrations
docker-compose exec ml_backend alembic upgrade head

# Create new migration
docker-compose exec ml_backend alembic revision --autogenerate -m "description"
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ml_backend
```

## 📊 ML Model Development

### Jupyter Notebooks
Access Jupyter Lab at http://localhost:8888 for:
- Data exploration and analysis
- Model training and evaluation
- Feature engineering experiments
- Performance monitoring

### Model Training Pipeline
1. **Data Preprocessing**: Transform raw user data into ML features
2. **Feature Engineering**: Create meaningful features for recommendations
3. **Model Training**: Train recommendation and matching algorithms
4. **Evaluation**: Validate model performance and accuracy
5. **Deployment**: Update production models with new versions

## 🌐 Deployment

### Railway (Production)
The application is configured for Railway deployment with automatic PostgreSQL provisioning.

### Environment Variables
Set these API keys in your production environment (other settings are in config files):
- `ANTHROPIC_API_KEY`: Anthropic API key for AI features  
- `POSTHOG_API_KEY`: PostHog analytics key

Optional overrides (if needed):
- `DATABASE_URL`: PostgreSQL connection string (overrides config.yaml)
- `SECRET_KEY`: Application secret for JWT signing (overrides config.yaml)

## 📈 Analytics & Monitoring

- **PostHog Integration**: User behavior tracking and analytics
- **A/B Testing Framework**: Built-in experimentation capabilities
- **Performance Monitoring**: API response times and error tracking
- **ML Model Metrics**: Recommendation accuracy and user satisfaction

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` directory
- Review API documentation at http://localhost:8000/docs

## 🔐 Environment Variables & API Keys

### Configuration Approach

WorkoutBuddy uses a **hybrid configuration approach**:
- **API Keys**: Always loaded from environment variables (for security)
- **Other Configuration**: Hardcoded in config files (for simplicity)

### Required Environment Variables (API Keys Only)

Create a `.envrc` file (for direnv) or set these environment variables:

```bash
# Required API Keys (always loaded from environment)
export ANTHROPIC_API_KEY=your-anthropic-api-key-here
export POSTHOG_API_KEY=your-posthog-api-key-here
```

### For Local Development with direnv

1. **Install direnv** (if not already installed):
```bash
# macOS
brew install direnv

# Ubuntu/Debian  
sudo apt install direnv

# Add to your shell profile (.zshrc, .bashrc)
eval "$(direnv hook zsh)"  # or bash
```

2. **Create .envrc file**:
```bash
# API Keys - loaded from environment variables for security
export ANTHROPIC_API_KEY=your-anthropic-api-key-here
export POSTHOG_API_KEY=your-posthog-api-key-here
```

3. **Allow direnv to load the environment**:
```bash
direnv allow
```

### Configuration Files

Other settings are configured in YAML files:
- **Database URL**: Set in `ml_backend/config.yaml` 
- **Server settings**: Host, port, logging level in config files
- **ML parameters**: Hyperparameters and model settings in YAML
- **A/B testing**: Experiment configuration in config files

**Example ml_backend/config.yaml**:
```yaml
backend:
  database:
    url: "postgresql://wojciechkowalinski@localhost/workoutbuddy"
  
  app:
    secret_key: "dev-secret-key-change-in-production"
    api_host: "0.0.0.0" 
    api_port: 8000
    
  # API keys are loaded from environment variables
  # Other settings configured here
```

### For Production Deployment

Set only the API keys as environment variables in your production environment:

**Railway**:
```bash
railway variables set ANTHROPIC_API_KEY=your-anthropic-key
railway variables set POSTHOG_API_KEY=your-posthog-key
```

**Docker**:
```bash
docker run -e ANTHROPIC_API_KEY=your-key -e POSTHOG_API_KEY=your-key ...
```

**Docker Compose**:
```yaml
environment:
  - ANTHROPIC_API_KEY=your-anthropic-key
  - POSTHOG_API_KEY=your-posthog-key
```

### Environment Variable Override (Optional)

While most configuration is in YAML files, you can still override any setting with environment variables if needed:

```bash
# Optional overrides (not required for normal operation)
export DATABASE_URL=postgresql://custom-db-url
export SECRET_KEY=custom-secret-key
export LOG_LEVEL=DEBUG
export API_PORT=3000
```

### ⚠️ Security Best Practices

1. **API Keys (REQUIRED from environment)**:
   - ✅ Always load from environment variables
   - ✅ Never commit to git repositories
   - ✅ Use different keys for different environments
   - ✅ Rotate keys regularly

2. **Configuration Files**:
   - ✅ Safe to commit to git (no secrets)
   - ✅ Easy to modify and track changes
   - ✅ Environment-specific config files supported

3. **NEVER** add API keys to:
   - Git repositories
   - Shell configuration files (.zshrc, .bashrc)
   - Docker images
   - Code files

4. **DO** use:
   - Environment variables for API keys
   - Config files for non-sensitive settings
   - Secret management services in production
   - `.envrc` with direnv for local development

---

**Happy coding! 🚀**