#!/bin/bash

# WorkoutBuddy Development Environment Startup Script
# This script sets up and starts the complete development environment

set -e

echo "🏋️ WorkoutBuddy Development Environment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "Docker Compose is not installed. Please install it and try again."
    exit 1
fi

print_status "Starting WorkoutBuddy development environment..."

# Navigate to the deploy directory
cd "$(dirname "$0")"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p init-db
mkdir -p ../ml_backend/models
mkdir -p ../ml_backend/logs

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start services
print_status "Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
print_status "Waiting for services to be ready..."

# Wait for database
print_status "Waiting for database..."
timeout 60 bash -c 'until docker-compose exec db pg_isready -U admin -d workoutbuddy; do sleep 2; done'

if [ $? -eq 0 ]; then
    print_success "Database is ready!"
else
    print_error "Database failed to start within 60 seconds"
    exit 1
fi

# Wait for backend
print_status "Waiting for ML backend..."
timeout 60 bash -c 'until curl -f http://localhost:8000/ > /dev/null 2>&1; do sleep 2; done'

if [ $? -eq 0 ]; then
    print_success "ML Backend is ready!"
else
    print_error "ML Backend failed to start within 60 seconds"
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec ml_backend alembic upgrade head

if [ $? -eq 0 ]; then
    print_success "Database migrations completed!"
else
    print_warning "Database migrations failed or not available"
fi

# Import exercise data if available
if [ -f "../ml_backend/data/exercise_table_extended.md" ]; then
    print_status "Importing exercise data..."
    docker-compose exec ml_backend python -m app.import_exercises
    
    if [ $? -eq 0 ]; then
        print_success "Exercise data imported!"
    else
        print_warning "Exercise data import failed"
    fi
fi

echo ""
print_success "🎉 WorkoutBuddy development environment is ready!"
echo ""
echo "Available services:"
echo "  🌐 ML Backend API:    http://localhost:8000"
echo "  📊 API Documentation: http://localhost:8000/docs"
echo "  🗄️  Database:         localhost:5432 (admin/mypassword)"
echo "  🔴 Redis:             localhost:6379"
echo "  📔 Jupyter Lab:       http://localhost:8888"
echo ""
echo "Useful commands:"
echo "  View logs:           docker-compose logs -f"
echo "  Stop services:       docker-compose down"
echo "  Restart backend:     docker-compose restart ml_backend"
echo "  Database shell:      docker-compose exec db psql -U admin -d workoutbuddy"
echo "  Backend shell:       docker-compose exec ml_backend bash"
echo ""
print_status "Happy coding! 🚀" 