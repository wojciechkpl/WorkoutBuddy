# WorkoutBuddy Architecture & Dependencies Diagram

## Overview

This document provides a holistic view of the WorkoutBuddy application architecture, showing the relationships between different components, services, and the dual unit system implementation.

## System Architecture

```mermaid
graph TB
    %% External Users
    User[👤 User] --> Mobile[Mobile App]
    User --> Web[Web Interface]

    %% Frontend Layer
    subgraph "Frontend Layer"
        Mobile --> MobileAPI[Mobile API Client]
        Web --> WebAPI[Web API Client]
    end

    %% API Gateway Layer
    subgraph "API Gateway Layer"
        Nginx[Nginx Reverse Proxy]
        MobileAPI --> Nginx
        WebAPI --> Nginx
    end

    %% Backend Services
    subgraph "Backend Services"
        subgraph "Main Backend (FastAPI)"
            MainAPI[Main API Server]
            AuthService[Authentication Service]
            UserService[User Management Service]
            WorkoutService[Workout Service]
            ExerciseService[Exercise Service]
            StatsService[Statistics Service]
        end

        subgraph "ML Service (FastAPI)"
            MLAPI[ML API Server]
            UserSimilarityModel[User Similarity Model]
            ExerciseRecommender[Exercise Recommender]
            AIServices[AI Services]
        end
    end

    %% Database Layer
    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL Database)]

        subgraph "Database Views"
            UsersMetric[users_metric View]
            UserStatsMetric[user_stats_metric View]
            WorkoutExercisesMetric[workout_exercises_metric View]
        end

        subgraph "Unit Conversion Functions"
            LbsToKg[lbs_to_kg()]
            KgToLbs[kg_to_lbs()]
            InchesToCm[inches_to_cm()]
            CmToInches[cm_to_inches()]
            MilesToKm[miles_to_km()]
            KmToMiles[km_to_miles()]
        end
    end

    %% Data Flow
    Nginx --> MainAPI
    Nginx --> MLAPI

    MainAPI --> AuthService
    MainAPI --> UserService
    MainAPI --> WorkoutService
    MainAPI --> ExerciseService
    MainAPI --> StatsService

    MLAPI --> UserSimilarityModel
    MLAPI --> ExerciseRecommender
    MLAPI --> AIServices

    %% Database Connections
    MainAPI --> PostgreSQL
    MLAPI --> PostgreSQL

    %% Unit System Integration
    UserService --> UnitConverter[Unit Conversion Utils]
    WorkoutService --> UnitConverter
    StatsService --> UnitConverter

    UserSimilarityModel --> UsersMetric
    UserSimilarityModel --> UserStatsMetric
    ExerciseRecommender --> WorkoutExercisesMetric
```

## Component Dependencies

```mermaid
graph LR
    %% Core Models
    subgraph "Core Models"
        UserModel[User Model]
        UserStatsModel[UserStats Model]
        WorkoutModel[Workout Model]
        WorkoutExerciseModel[WorkoutExercise Model]
        ExerciseModel[Exercise Model]
    end

    %% Unit System
    subgraph "Unit System"
        UnitConverter[UnitConverter]
        UnitPreferences[UnitPreferences]
        UnitEnums[Unit Enums]
    end

    %% Schemas
    subgraph "API Schemas"
        UserSchemas[User Schemas]
        WorkoutSchemas[Workout Schemas]
        ExerciseSchemas[Exercise Schemas]
        MetricSchemas[Metric Schemas]
    end

    %% ML Models
    subgraph "ML Models"
        UserSimilarityModel[UserSimilarityModel]
        ExerciseRecommender[ExerciseRecommender]
        MLDataModels[ML Data Models]
    end

    %% Services
    subgraph "Services"
        UserService[User Service]
        WorkoutService[Workout Service]
        StatsService[Stats Service]
        MLService[ML Service]
    end

    %% Dependencies
    UserModel --> UnitConverter
    UserStatsModel --> UnitConverter
    WorkoutExerciseModel --> UnitConverter

    UserSchemas --> UnitEnums
    WorkoutSchemas --> UnitEnums
    MetricSchemas --> UnitConverter

    UserSimilarityModel --> MLDataModels
    ExerciseRecommender --> MLDataModels
    MLDataModels --> UnitConverter

    UserService --> UserModel
    UserService --> UserSchemas
    WorkoutService --> WorkoutModel
    WorkoutService --> WorkoutSchemas
    StatsService --> UserStatsModel
    MLService --> UserSimilarityModel
    MLService --> ExerciseRecommender
```

## Data Flow with Unit System

```mermaid
flowchart TD
    %% User Input
    UserInput[User Input<br/>Imperial/Metric] --> InputValidation[Input Validation<br/>Unit-specific ranges]

    %% Backend Processing
    InputValidation --> UnitConversion[Unit Conversion<br/>To Metric for Processing]
    UnitConversion --> BusinessLogic[Business Logic<br/>Always Metric Units]

    %% Database Storage
    BusinessLogic --> DBStorage[Database Storage<br/>User's Preferred Units]
    DBStorage --> MetricViews[Metric Views<br/>Automatic Conversion]

    %% ML Processing
    MetricViews --> MLProcessing[ML Processing<br/>Metric Units Only]
    MLProcessing --> MLResults[ML Results<br/>Metric Units]

    %% Output
    MLResults --> OutputConversion[Output Conversion<br/>To User's Preferred Units]
    OutputConversion --> UserDisplay[User Display<br/>Imperial/Metric]

    %% Unit System Components
    subgraph "Unit System Components"
        UnitConverter[UnitConverter<br/>Conversion Functions]
        UnitPreferences[UnitPreferences<br/>User Preferences]
        UnitValidation[Unit Validation<br/>Range Checking]
    end

    InputValidation --> UnitValidation
    UnitConversion --> UnitConverter
    OutputConversion --> UnitConverter
    UnitConversion --> UnitPreferences
    OutputConversion --> UnitPreferences
```

## Database Schema with Unit Support

```mermaid
erDiagram
    USERS {
        int id PK
        string email
        string username
        string hashed_password
        string full_name
        boolean is_active
        boolean is_verified
        int age
        float height "stored in height_unit"
        float weight "stored in weight_unit"
        enum fitness_goal
        enum experience_level
        enum unit_system "METRIC/IMPERIAL"
        enum height_unit "CM/INCHES/FEET_INCHES"
        enum weight_unit "KG/LBS"
        datetime created_at
        datetime updated_at
    }

    USER_STATS {
        int id PK
        int user_id FK
        datetime date
        float weight "stored in weight_unit"
        float body_fat_percentage
        float muscle_mass "stored in weight_unit"
        int total_workouts
        float total_weight_lifted "stored in weight_unit"
        float total_cardio_distance "stored in distance_unit"
        float total_calories_burned
        enum weight_unit "KG/LBS"
        enum distance_unit "KM/MILES/METERS"
        text personal_records
    }

    WORKOUTS {
        int id PK
        int user_id FK
        string name
        text description
        datetime scheduled_date
        datetime started_at
        datetime completed_at
        enum status
        int total_duration "minutes"
        float calories_burned
        float total_volume "stored in user's weight_unit"
        float total_distance "stored in user's distance_unit"
        text notes
        datetime created_at
        datetime updated_at
    }

    WORKOUT_EXERCISES {
        int id PK
        int workout_id FK
        int exercise_id FK
        int order
        int sets
        string reps
        string weight "stored in weight_unit"
        int duration "minutes"
        float distance "stored in distance_unit"
        float speed "stored in distance_unit per hour"
        float incline
        int rest_time "seconds"
        string actual_reps
        string actual_weight
        text notes
        enum weight_unit "KG/LBS"
        enum distance_unit "KM/MILES/METERS"
    }

    EXERCISES {
        int id PK
        string name
        text description
        string muscle_group
        string equipment
        string difficulty_level
        text instructions
        datetime created_at
        datetime updated_at
    }

    %% Metric Views
    USERS_METRIC {
        int id
        string email
        string username
        string full_name
        boolean is_active
        boolean is_verified
        int age
        float height_cm "always in cm"
        float weight_kg "always in kg"
        enum fitness_goal
        enum experience_level
        enum unit_system
        enum height_unit
        enum weight_unit
        datetime created_at
        datetime updated_at
    }

    USER_STATS_METRIC {
        int id
        int user_id
        datetime date
        float weight_kg "always in kg"
        float body_fat_percentage
        float muscle_mass_kg "always in kg"
        int total_workouts
        float total_weight_lifted_kg "always in kg"
        float total_cardio_distance_km "always in km"
        float total_calories_burned
        enum weight_unit
        enum distance_unit
        text personal_records
    }

    WORKOUT_EXERCISES_METRIC {
        int id
        int workout_id
        int exercise_id
        int order
        int sets
        string reps
        string weight_kg "always in kg"
        int duration
        float distance_meters "always in meters"
        float speed_kmh "always in km/h"
        float incline
        int rest_time
        string actual_reps
        string actual_weight
        text notes
        enum weight_unit
        enum distance_unit
    }

    %% Relationships
    USERS ||--o{ USER_STATS : "has"
    USERS ||--o{ WORKOUTS : "creates"
    WORKOUTS ||--o{ WORKOUT_EXERCISES : "contains"
    EXERCISES ||--o{ WORKOUT_EXERCISES : "used_in"

    %% Metric View Relationships
    USERS ||--|| USERS_METRIC : "metric_view"
    USER_STATS ||--|| USER_STATS_METRIC : "metric_view"
    WORKOUT_EXERCISES ||--|| WORKOUT_EXERCISES_METRIC : "metric_view"
```

## Service Dependencies

```mermaid
graph TD
    %% API Layer
    subgraph "API Layer"
        MainAPI[Main API Server]
        MLAPI[ML API Server]
    end

    %% Service Layer
    subgraph "Service Layer"
        AuthService[Authentication Service]
        UserService[User Management Service]
        WorkoutService[Workout Service]
        ExerciseService[Exercise Service]
        StatsService[Statistics Service]
        MLService[ML Service]
    end

    %% Model Layer
    subgraph "Model Layer"
        UserModel[User Model]
        UserStatsModel[UserStats Model]
        WorkoutModel[Workout Model]
        WorkoutExerciseModel[WorkoutExercise Model]
        ExerciseModel[Exercise Model]
    end

    %% Utility Layer
    subgraph "Utility Layer"
        UnitConverter[Unit Converter]
        UnitPreferences[Unit Preferences]
        DatabaseUtils[Database Utils]
        ValidationUtils[Validation Utils]
    end

    %% ML Layer
    subgraph "ML Layer"
        UserSimilarityModel[User Similarity Model]
        ExerciseRecommender[Exercise Recommender]
        FeatureExtractor[Feature Extractor]
    end

    %% Database Layer
    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL)]
        MetricViews[Metric Views]
        ConversionFunctions[Conversion Functions]
    end

    %% Dependencies
    MainAPI --> AuthService
    MainAPI --> UserService
    MainAPI --> WorkoutService
    MainAPI --> ExerciseService
    MainAPI --> StatsService

    MLAPI --> MLService

    AuthService --> UserModel
    UserService --> UserModel
    UserService --> UnitConverter
    UserService --> UnitPreferences

    WorkoutService --> WorkoutModel
    WorkoutService --> WorkoutExerciseModel
    WorkoutService --> UnitConverter

    ExerciseService --> ExerciseModel

    StatsService --> UserStatsModel
    StatsService --> UnitConverter

    MLService --> UserSimilarityModel
    MLService --> ExerciseRecommender
    MLService --> FeatureExtractor

    %% Model Dependencies
    UserModel --> UnitConverter
    UserStatsModel --> UnitConverter
    WorkoutExerciseModel --> UnitConverter

    %% ML Dependencies
    UserSimilarityModel --> MetricViews
    ExerciseRecommender --> MetricViews
    FeatureExtractor --> UnitConverter

    %% Database Dependencies
    UserModel --> PostgreSQL
    UserStatsModel --> PostgreSQL
    WorkoutModel --> PostgreSQL
    WorkoutExerciseModel --> PostgreSQL
    ExerciseModel --> PostgreSQL

    MetricViews --> ConversionFunctions
```

## Unit System Integration Points

```mermaid
graph LR
    %% User Interface
    subgraph "User Interface"
        MobileApp[Mobile App]
        WebApp[Web App]
    end

    %% API Layer
    subgraph "API Layer"
        UserAPI[User API]
        WorkoutAPI[Workout API]
        StatsAPI[Stats API]
        MLAPI[ML API]
    end

    %% Unit System
    subgraph "Unit System"
        UnitConverter[Unit Converter]
        UnitPreferences[Unit Preferences]
        UnitValidation[Unit Validation]
    end

    %% Database
    subgraph "Database"
        UserTable[Users Table]
        StatsTable[User Stats Table]
        WorkoutTable[Workout Exercises Table]
        MetricViews[Metric Views]
    end

    %% ML Services
    subgraph "ML Services"
        UserSimilarity[User Similarity]
        ExerciseRec[Exercise Recommender]
    end

    %% Data Flow
    MobileApp --> UserAPI
    WebApp --> UserAPI
    MobileApp --> WorkoutAPI
    WebApp --> WorkoutAPI

    UserAPI --> UnitValidation
    WorkoutAPI --> UnitValidation
    StatsAPI --> UnitValidation

    UnitValidation --> UnitConverter
    UnitValidation --> UnitPreferences

    UserAPI --> UserTable
    WorkoutAPI --> WorkoutTable
    StatsAPI --> StatsTable

    UserSimilarity --> MetricViews
    ExerciseRec --> MetricViews

    MetricViews --> UnitConverter
```

## Key Features of the Architecture

### 1. **Dual Unit Support**
- **User Preferences**: Users can choose between metric and imperial units
- **Storage**: Data is stored in user's preferred units
- **Processing**: All algorithms use metric units internally
- **Display**: Results are converted back to user's preferred units

### 2. **Metric Views**
- **Automatic Conversion**: Database views automatically convert units to metric
- **Algorithm Access**: ML models access data through metric views
- **Performance**: Fast access to converted data without application-level conversion

### 3. **Unit Conversion Functions**
- **Database Level**: PostgreSQL functions for efficient conversion
- **Application Level**: Python utilities for conversion and formatting
- **Validation**: Unit-specific range validation

### 4. **Service Separation**
- **Main Backend**: Handles user management, workouts, and statistics
- **ML Service**: Handles recommendations and similarity calculations
- **Shared Models**: Common data models with unit support

### 5. **API Design**
- **Dual Schemas**: Regular schemas for user input/output, metric schemas for algorithms
- **Unit Validation**: Input validation based on unit type
- **Flexible Display**: Support for different unit preferences

## Benefits of This Architecture

1. **User Experience**: Users work in their preferred units
2. **Algorithm Consistency**: All ML algorithms use metric units
3. **Data Integrity**: Original units are preserved
4. **Performance**: Efficient unit conversion at database level
5. **Maintainability**: Clear separation of concerns
6. **Scalability**: Microservice architecture supports independent scaling
7. **Flexibility**: Easy to add new units or conversion factors

## Deployment Architecture

```mermaid
graph TB
    %% External
    Internet[Internet] --> LoadBalancer[Load Balancer]

    %% Infrastructure
    subgraph "Kubernetes Cluster"
        subgraph "Frontend"
            MobileService[Mobile Service]
            WebService[Web Service]
        end

        subgraph "Backend Services"
            MainBackend[Main Backend]
            MLService[ML Service]
        end

        subgraph "Data Layer"
            PostgreSQL[(PostgreSQL)]
            Redis[(Redis Cache)]
        end

        subgraph "Monitoring"
            Prometheus[Prometheus]
            Grafana[Grafana]
        end
    end

    %% Connections
    LoadBalancer --> MobileService
    LoadBalancer --> WebService
    LoadBalancer --> MainBackend
    LoadBalancer --> MLService

    MainBackend --> PostgreSQL
    MLService --> PostgreSQL
    MainBackend --> Redis
    MLService --> Redis

    Prometheus --> MainBackend
    Prometheus --> MLService
    Prometheus --> PostgreSQL
    Grafana --> Prometheus
```

This architecture provides a comprehensive view of how the dual unit system integrates with all components of the WorkoutBuddy application, ensuring consistency, performance, and user satisfaction.