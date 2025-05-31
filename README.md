# WorkoutBuddy

**A cross-platform fitness app that transforms personal health goals into social community experiences.**

WorkoutBuddy combines personalized goal-setting with powerful social accountability features, using AI to create customized workout plans and match users with compatible fitness partners.

## ✨ Key Features

- **🎯 Personalized Goal Setting** - Set ambitious fitness targets (marathons, weekly workouts, yoga practice)
- **🤖 AI-Powered Personalization** - Custom workout plans based on available time, equipment, and fitness level
- **👥 Smart Teammate Matching** - Connect with like-minded individuals for motivation and accountability
- **📊 Comprehensive Progress Tracking** - Detailed history of achievements and fitness journey
- **🔗 Social Sharing** - Share accomplishments with friends and family
- **💡 Intelligent Recommendations** - Data-driven suggestions for weights, reps, and training loads
- **🔄 Recovery Optimization** - Smart recommendations for rest and recovery
- **🏃‍♀️ Multi-Sport Support** - Running, strength training, yoga, and walking
- **📱 Cross-Platform** - Works on iOS, Android, and Web

## High-Level Architecture

```
+-------------------+         REST API         +-------------------+         SQL/ML         +-------------------+
|    Flutter App    | <---------------------> |     FastAPI       | <-------------------> |   PostgreSQL DB   |
|  (iOS/Android/Web)|                         |   (Python, ML)    |   (SQLAlchemy ORM)   |   + ML Models     |
+-------------------+                         +-------------------+                      +-------------------+
         |                                             |                                         
         | 1. User interacts with UI                   |                                         
         |-------------------------------------------->|                                         
         |                                             |                                         
         | 2. FastAPI handles requests,                |                                         
         |    authentication, business logic           |                                         
         |-------------------------------------------->|                                         
         |                                             |                                         
         | 3. FastAPI queries DB, runs ML models       |                                         
         |<--------------------------------------------|                                         
         |                                             |                                         
         | 4. Results returned to user                 |                                         
         |<--------------------------------------------|                                         
```

### **Components**

- **Frontend (Flutter)**
  - Cross-platform mobile/web app
  - Handles user registration, login, goal setting, social features, progress tracking, and displays AI recommendations
  - Communicates with backend via REST API

- **Backend (FastAPI)**
  - Handles authentication, user management, goal tracking, social features, and ML endpoints
  - Uses SQLAlchemy ORM and Alembic for database migrations
  - Machine Learning: PyTorch and scikit-learn for personalized plans, recommendations, and teammate matching

- **Database (PostgreSQL)**
  - Stores users, goals, progress, social connections, and exercises
  - Exercises imported from `data/exercise_table_extended.md`

- **Machine Learning**
  - PyTorch and scikit-learn models for:
    - Personalized workout plans
    - Teammate matching
    - Intelligent recommendations

## 🚀 How to Run (Development)

### Quick Start Backend (Step-by-Step)

Follow these detailed steps to get the backend server running:

#### **Step 1: Verify Prerequisites**

**Check Python version:**
```sh
python3 --version  # Should be 3.8 or higher
```

**Check if PostgreSQL is installed:**
```sh
postgres --version
# If not installed: brew install postgresql
```

**Install uv (Python package manager):**
```sh
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv

# Verify installation
uv --version
```

#### **Step 2: Setup PostgreSQL Database**

**Start PostgreSQL service:**
```sh
# Start PostgreSQL
brew services start postgresql

# Verify it's running
brew services list | grep postgresql
# Should show "started" status
```

**Create database and user:**
```sh
# Create the database
createdb workoutbuddy

# (Optional) Create a dedicated user
psql postgres -c "CREATE USER workoutbuddy_user WITH PASSWORD 'your_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE workoutbuddy TO workoutbuddy_user;"

# Verify database exists
psql -l | grep workoutbuddy
```

#### **Step 3: Configure Application**

**Navigate to project root and update config:**
```sh
cd /path/to/WorkoutBuddy  # Navigate to your project root
```

**Edit `config.yaml`** and update the database URL:
```yaml
backend:
  database:
    # For default postgres user:
    url: "postgresql://postgres@localhost/workoutbuddy"
    
    # Or for custom user:
    url: "postgresql://workoutbuddy_user:your_password@localhost/workoutbuddy"
```

#### **Step 4: Setup Backend Dependencies**

```sh
# Navigate to backend directory
cd backend

# Install all dependencies and create virtual environment
uv sync

# Verify installation worked
uv run python -c "import fastapi; print('FastAPI installed successfully')"
```

#### **Step 5: Setup Database Schema**

```sh
# Run database migrations to create tables
uv run alembic upgrade head

# Verify tables were created
psql workoutbuddy -c "\dt"
# Should show: users, goals, exercises tables
```

#### **Step 6: Import Exercise Data**

```sh
# Import exercises from the markdown file
uv run python -m app.import_exercises

# Verify exercises were imported
psql workoutbuddy -c "SELECT COUNT(*) FROM exercises;"
# Should show the number of imported exercises
```

#### **Step 7: Start the Backend Server**

```sh
# Start the FastAPI development server
uv run uvicorn app.main:app --reload

# Server will start on: http://127.0.0.1:8000
```

#### **Step 8: Verify Backend is Running**

**Test the API endpoints:**
```sh
# Test health check endpoint
curl http://127.0.0.1:8000/

# Should return: {"message": "WorkoutBuddy API is running!"}

# View API documentation
open http://127.0.0.1:8000/docs
# Opens interactive API documentation in browser
```

#### **Step 9: Test Core Functionality**

**Register a test user:**
```sh
curl -X POST "http://127.0.0.1:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123"
  }'
```

**Create a test goal:**
```sh
curl -X POST "http://127.0.0.1:8000/goals?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Daily Exercise",
    "description": "Exercise for 30 minutes daily",
    "target_date": "2024-12-31T00:00:00"
  }'
```

### **Common Backend Issues & Solutions**

**❌ "Connection refused" when starting server:**
```sh
# Check if port 8000 is already in use
lsof -i :8000

# Kill existing process if needed
kill -9 <PID>

# Or use a different port
uv run uvicorn app.main:app --reload --port 8001
```

**❌ "No module named 'app'" error:**
```sh
# Make sure you're in the backend directory
pwd  # Should end with /WorkoutBuddy/backend

# Verify uv virtual environment is activated
uv run python -c "import sys; print(sys.prefix)"
```

**❌ Database connection errors:**
```sh
# Test database connection manually
psql workoutbuddy -c "SELECT 1;"

# Check PostgreSQL is running
brew services list | grep postgresql

# Restart PostgreSQL if needed
brew services restart postgresql
```

**❌ "Alembic not found" or migration errors:**
```sh
# Ensure you're in backend directory with alembic.ini
ls alembic.ini  # Should exist

# Reset and re-run migrations
uv run alembic downgrade base
uv run alembic upgrade head
```

### **Environment Variables (Alternative Setup)**

Instead of editing `config.yaml`, you can use environment variables:

```sh
# Set database URL
export DATABASE_URL="postgresql://postgres@localhost/workoutbuddy"

# Set other optional variables
export WORKOUTBUDDY_SECRET_KEY="your-secret-key-here"
export WORKOUTBUDDY_DEBUG="true"

# Start server with environment variables
uv run uvicorn app.main:app --reload
```

---

### 1. **Prerequisites**
- Python 3.8+
- Flutter SDK
- PostgreSQL
- uv (Python package manager)

### 2. **Backend Setup**

#### a. Install uv (if not already installed)
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Or with Homebrew:
```sh
brew install uv
```

#### b. Install dependencies and set up project
```sh
cd backend
uv sync
```

#### c. Install and start PostgreSQL
- Install via Homebrew: `brew install postgresql`
- Start: `brew services start postgresql`
- Create database: `createdb workoutbuddy`

#### d. Configure database connection
- Edit `config.yaml` (project root) and set your PostgreSQL user and password in `backend.database.url`.

#### e. Run Alembic migrations
```sh
uv run alembic upgrade head
```

#### f. Import exercises
```sh
uv run python -m app.import_exercises
```

#### g. Run the FastAPI server
```sh
uv run uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

---

### 3. **Frontend Setup**

#### a. Install Flutter (if not already)
- [Flutter Install Guide](https://docs.flutter.dev/get-started/install)

#### b. Get dependencies
```sh
cd frontend
flutter pub get
```

#### c. Run the Flutter app
```sh
flutter run
```

---

## 🧪 Testing

### Backend Tests
```sh
cd backend
uv run pytest
```

### Frontend Tests
```sh
cd frontend
flutter test
```

---

## 🔧 Development Workflow

### Adding New Dependencies

**Backend:**
```sh
cd backend
uv add package-name              # Add runtime dependency
uv add --dev package-name        # Add development dependency
```

**Frontend:**
```sh
cd frontend
flutter pub add package_name
```

### Database Migrations
```sh
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

### Running in Different Environments
Update `config.yaml` for different environments (development, staging, production).

---

## 📁 Project Structure
```
WorkoutBuddy/
  backend/
    app/
      main.py               # FastAPI application
      models.py             # SQLAlchemy models
      schemas.py            # Pydantic schemas
      crud.py               # Database operations
      database.py           # Database configuration
      ml.py                 # Machine learning logic
      import_exercises.py   # Exercise data importer
      config.py             # Configuration loader
      alembic/              # Database migrations
      alembic.ini
    pyproject.toml          # Python dependencies (uv)
  data/
    exercise_table_extended.md  # Exercise database
  frontend/
    lib/
      main.dart             # Flutter main app
      config.dart           # Configuration loader
    assets/
      config.yaml           # Frontend config copy
    pubspec.yaml            # Flutter dependencies
  config.yaml               # Unified configuration
  README.md
```

---

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Check PostgreSQL is running: `brew services list | grep postgresql`
- Verify database exists: `psql -l | grep workoutbuddy`
- Check config.yaml has correct database credentials

**Frontend can't connect to backend:**
- Ensure backend is running on the correct port (check config.yaml)
- Update `frontend.api_base_url` in config.yaml if needed

**Import exercises fails:**
- Run migrations first: `uv run alembic upgrade head`
- Check database connection and permissions

**uv commands not working:**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart terminal after installation

---

## Notes
- Make sure your backend server is running before using the frontend app.
- Update API URLs in the Flutter app to point to your backend server if needed.
- For production, set up environment variables and secure your database credentials.

---

## Environment Variables

The backend uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string. Example:
  ```
  postgresql://myuser:mypassword@localhost/workoutbuddy
  ```
  If not set, defaults to the value in `backend/app/database.py`.

- (Optional) You can set other environment variables for production, such as secret keys, email configs, etc.

To set an environment variable temporarily:
```sh
export DATABASE_URL="postgresql://myuser:mypassword@localhost/workoutbuddy"
```

---

## API Usage Examples

### **Register a User**
```http
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "yourpassword"
}
```

### **Create a Goal**
```http
POST /goals?user_id=1
Content-Type: application/json

{
  "title": "Run a marathon",
  "description": "Complete a marathon in 2024",
  "target_date": "2024-12-31T00:00:00"
}
```

### **Get Personalized Plan (ML Endpoint)**
```http
POST /ml/personalized-plan?user_id=1
```

### **Get Root (Health Check)**
```http
GET /
```

---

## Config Usage Examples

The app uses a unified `config.yaml` file at the project root for both backend and frontend settings.

### **Backend Usage (Python)**

Access settings in your Python code:
```python
from .config import backend_config

# Database URL
db_url = backend_config.database.url

# ML model path
model_path = backend_config.ml.model_path

# App settings
secret_key = backend_config.app.secret_key
api_host = backend_config.app.api_host
api_port = backend_config.app.api_port

# Logging level
log_level = backend_config.logging.level
```

### **Frontend Usage (Dart/Flutter)**

Load and use config in your Flutter app:
```dart
import 'config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final appConfig = await AppConfig.load();
  runApp(MyApp(appConfig: appConfig));
}

// Use API base URL for requests
Future<void> fetchData() async {
  final url = Uri.parse('${appConfig.apiBaseUrl}/api/data');
  final response = await http.get(url);
  // Handle response...
}

// Toggle features based on flags
Widget buildSocialFeatures() {
  final enableSocial = appConfig.featureFlags['enable_social'] == true;
  if (enableSocial) {
    return SocialWidget();
  }
  return Container(); // Hide feature
}
```

### **Environment-Specific Configuration**

Update `config.yaml` for different environments:

**Development:**
```yaml
frontend:
  api_base_url: http://127.0.0.1:8000
  environment: development
```

**Production:**
```yaml
frontend:
  api_base_url: https://api.workoutbuddy.com
  environment: production
```

### **Feature Flags Example**

Enable/disable features without code changes:
```yaml
frontend:
  feature_flags:
    enable_social: true     # Show social features
    enable_ai: false        # Hide AI features
    enable_premium: true    # Show premium features
```

Then in your Flutter code:
```dart
if (appConfig.featureFlags['enable_ai'] == true) {
  // Show AI-powered recommendations
}
```