# Database Documentation (2024)

This document provides detailed information about the WorkoutBuddy database schema, including new tables for safety, privacy, ML feedback, accountability check-ins, and community connections. Synthetic test data covers all flows and is annotated for separation.

## 📋 Table Overview

| Table | Purpose | Records | Key Features |
|-------|---------|---------|--------------|
| `users` | User accounts and profiles | 0+ | Authentication, fitness goals, experience levels |
| `user_goals` | User fitness goals and targets | 0+ | Goal tracking, progress monitoring |
| `user_stats` | User fitness statistics over time | 0+ | Progress tracking, metrics history |
| `workouts` | Workout sessions and plans | 0+ | Workout scheduling, completion tracking |
| `workout_exercises` | Exercises within workouts | 0+ | Exercise parameters, performance tracking |
| `exercises` | Exercise library | 157 | Comprehensive exercise database |
| `friendships` | Social connections | 0+ | User relationships, social features |
| `safety_reports` | User safety reports | 0+ | Report generation, user safety monitoring |
| `user_blocks` | User block list | 0+ | Blocked user list, user safety feature |
| `privacy_settings` | User privacy preferences | 0+ | User privacy settings, data protection |
| `ml_feedback` | User feedback on ML recommendations | 0+ | Feedback on ML-generated recommendations |
| `accountability_checkins` | Accountability check-ins | 0+ | Check-ins for accountability, progress tracking |
| `community_groups` | Community groups | 0+ | Group creation, community management |
| `community_memberships` | Group memberships | 0+ | Membership in community groups |
| `community_connections` | Community connections | 0+ | Connections between users in community groups |

## 🗂️ Detailed Table Schemas

### Users Table

**Purpose**: Store user account information and fitness profiles

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    username VARCHAR NOT NULL UNIQUE,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    age INTEGER,
    height DOUBLE PRECISION, -- in cm
    weight DOUBLE PRECISION, -- in kg
    fitness_goal USER_DEFINED, -- enum
    experience_level USER_DEFINED, -- enum
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Features**:
- Unique email and username constraints
- Fitness goal and experience level enums
- Height/weight tracking for fitness calculations
- Account verification and activation status

### User Goals Table

**Purpose**: Track user fitness goals and progress

```sql
CREATE TABLE user_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    goal_type VARCHAR NOT NULL, -- e.g., 'weight_loss', 'strength_gain'
    target_value DOUBLE PRECISION NOT NULL,
    current_value DOUBLE PRECISION,
    target_date TIMESTAMP,
    is_achieved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    achieved_at TIMESTAMP
);
```

**Goal Types**:
- `weight_loss` - Target weight in kg
- `strength_gain` - Target weight for specific exercises
- `endurance` - Target duration or distance
- `muscle_gain` - Target muscle mass percentage
- `body_fat_loss` - Target body fat percentage

### User Stats Table

**Purpose**: Track user fitness metrics over time

```sql
CREATE TABLE user_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weight DOUBLE PRECISION, -- in kg
    body_fat_percentage DOUBLE PRECISION,
    muscle_mass DOUBLE PRECISION, -- in kg
    total_workouts INTEGER DEFAULT 0,
    total_weight_lifted DOUBLE PRECISION DEFAULT 0, -- in kg
    total_cardio_distance DOUBLE PRECISION DEFAULT 0, -- in km
    total_calories_burned DOUBLE PRECISION DEFAULT 0,
    personal_records TEXT -- JSON format
);
```

**Personal Records Format**:
```json
{
    "barbell_squat": {"weight": 100, "date": "2024-01-15"},
    "deadlift": {"weight": 150, "date": "2024-01-20"},
    "5k_run": {"time": "25:30", "date": "2024-01-10"}
}
```

### Workouts Table

**Purpose**: Store workout sessions and plans

```sql
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR NOT NULL,
    description TEXT,
    scheduled_date TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status USER_DEFINED DEFAULT 'scheduled', -- enum
    total_duration INTEGER, -- in minutes
    calories_burned DOUBLE PRECISION,
    total_volume DOUBLE PRECISION, -- total weight lifted
    total_distance DOUBLE PRECISION, -- for cardio workouts
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Status Values**:
- `scheduled` - Workout is planned but not started
- `in_progress` - Workout is currently being performed
- `completed` - Workout has been finished
- `cancelled` - Workout was cancelled

### Workout Exercises Table

**Purpose**: Link exercises to workouts with specific parameters

```sql
CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workouts(id),
    exercise_id INTEGER NOT NULL REFERENCES exercises(id),
    "order" INTEGER NOT NULL, -- exercise sequence
    sets INTEGER,
    reps VARCHAR, -- e.g., "8-12", "to failure"
    weight VARCHAR, -- e.g., "50kg", "bodyweight"
    duration INTEGER, -- in seconds for time-based exercises
    distance DOUBLE PRECISION, -- in meters for distance-based exercises
    speed DOUBLE PRECISION, -- in km/h for cardio
    incline DOUBLE PRECISION, -- in degrees for cardio
    rest_time INTEGER, -- in seconds
    actual_reps VARCHAR, -- what was actually performed
    actual_weight VARCHAR, -- what was actually lifted
    notes TEXT
);
```

**Key Features**:
- Flexible parameter storage (reps/weight as strings for variations)
- Support for both strength and cardio exercises
- Actual vs planned performance tracking
- Rest time and exercise ordering

### Exercises Table

**Purpose**: Comprehensive exercise library

```sql
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    primary_muscle USER_DEFINED NOT NULL, -- enum
    secondary_muscles VARCHAR, -- JSON array
    equipment USER_DEFINED NOT NULL, -- enum
    exercise_type USER_DEFINED NOT NULL, -- enum
    difficulty INTEGER CHECK (difficulty >= 1 AND difficulty <= 5),
    instructions TEXT,
    tips TEXT,
    video_url VARCHAR,
    is_distance_based BOOLEAN DEFAULT false,
    is_time_based BOOLEAN DEFAULT false,
    mets DOUBLE PRECISION -- Metabolic Equivalent of Task
);
```

**Primary Muscles**: `LEGS`, `CORE`, `BACK`, `SHOULDERS`, `FULL_BODY`, `CHEST`, `TRICEPS`, `BICEPS`, `GLUTES`

**Equipment Types**: `NONE`, `DUMBBELL`, `BARBELL`, `OTHER`, `CABLE`, `KETTLEBELL`, `MACHINE`, `BANDS`

**Exercise Types**: `STRENGTH`, `CARDIO`, `FLEXIBILITY`, `BALANCE`

### Friendships Table

**Purpose**: Manage social connections between users

```sql
CREATE TABLE friendships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    friend_id INTEGER NOT NULL REFERENCES users(id),
    is_accepted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP,
    CHECK (user_id != friend_id)
);
```

**Features**:
- Bidirectional friendship requests
- Acceptance tracking
- Prevents self-friendship

### Safety Reports Table

**Purpose**: Store user safety reports

```sql
CREATE TABLE safety_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    report_type VARCHAR NOT NULL, -- e.g., 'incident', 'safety_concern'
    description TEXT,
    status USER_DEFINED DEFAULT 'pending', -- enum
    resolved_at TIMESTAMP
);
```

**Status Values**:
- `pending` - Report is awaiting review
- `resolved` - Report has been reviewed and resolved

### User Blocks Table

**Purpose**: Store user block list

```sql
CREATE TABLE user_blocks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    blocked_user_id INTEGER NOT NULL REFERENCES users(id),
    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (user_id != blocked_user_id)
);
```

**Features**:
- Bidirectional blocking
- Prevents self-blocking

### Privacy Settings Table

**Purpose**: Store user privacy preferences

```sql
CREATE TABLE privacy_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    privacy_level USER_DEFINED NOT NULL, -- enum
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Privacy Levels**:
- `public` - User's data is visible to everyone
- `private` - User's data is only visible to friends
- `custom` - User's data is visible to a custom set of users

### ML Feedback Table

**Purpose**: Store user feedback on ML recommendations

```sql
CREATE TABLE ml_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback_type VARCHAR NOT NULL, -- e.g., 'like', 'dislike', 'suggestion'
    description TEXT,
    status USER_DEFINED DEFAULT 'pending', -- enum
    resolved_at TIMESTAMP
);
```

**Status Values**:
- `pending` - Feedback is awaiting review
- `resolved` - Feedback has been reviewed and resolved

### Accountability Check-ins Table

**Purpose**: Track user accountability check-ins

```sql
CREATE TABLE accountability_checkins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    checkin_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status USER_DEFINED DEFAULT 'pending', -- enum
    notes TEXT
);
```

**Status Values**:
- `pending` - Check-in is awaiting completion
- `completed` - Check-in has been completed

### Community Groups Table

**Purpose**: Store community groups

```sql
CREATE TABLE community_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Community Memberships Table

**Purpose**: Store group memberships

```sql
CREATE TABLE community_memberships (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES community_groups(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (group_id != user_id)
);
```

**Features**:
- Bidirectional membership
- Prevents self-membership

### Community Connections Table

**Purpose**: Store community connections

```sql
CREATE TABLE community_connections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    connection_id INTEGER NOT NULL REFERENCES users(id),
    connection_type USER_DEFINED NOT NULL, -- enum
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (user_id != connection_id)
);
```

**Features**:
- Bidirectional connection
- Prevents self-connection

## 🔗 Relationships and Constraints

### Foreign Key Relationships

1. **user_goals.user_id** → **users.id**
   - Cascade delete: When user is deleted, their goals are deleted

2. **user_stats.user_id** → **users.id**
   - Cascade delete: When user is deleted, their stats are deleted

3. **workouts.user_id** → **users.id**
   - Cascade delete: When user is deleted, their workouts are deleted

4. **workout_exercises.workout_id** → **workouts.id**
   - Cascade delete: When workout is deleted, its exercises are deleted

5. **workout_exercises.exercise_id** → **exercises.id**
   - Restrict delete: Cannot delete exercises that are used in workouts

6. **friendships.user_id** → **users.id**
   - Cascade delete: When user is deleted, their friendships are deleted

7. **friendships.friend_id** → **users.id**
   - Cascade delete: When user is deleted, their friendships are deleted

8. **safety_reports.user_id** → **users.id**
   - Cascade delete: When user is deleted, their safety reports are deleted

9. **user_blocks.user_id** → **users.id**
   - Cascade delete: When user is deleted, their block list is deleted

10. **privacy_settings.user_id** → **users.id**
    - Cascade delete: When user is deleted, their privacy settings are deleted

11. **ml_feedback.user_id** → **users.id**
    - Cascade delete: When user is deleted, their ML feedback is deleted

12. **accountability_checkins.user_id** → **users.id**
    - Cascade delete: When user is deleted, their check-ins are deleted

13. **community_memberships.user_id** → **users.id**
    - Cascade delete: When user is deleted, their memberships are deleted

14. **community_connections.user_id** → **users.id**
    - Cascade delete: When user is deleted, their connections are deleted

15. **community_connections.connection_id** → **users.id**
    - Cascade delete: When user is deleted, their connections are deleted

### Unique Constraints

- `users.email` - Unique email addresses
- `users.username` - Unique usernames
- `friendships(user_id, friend_id)` - Unique friendship pairs
- `safety_reports(user_id, report_date)` - Unique report per user per date
- `user_blocks(user_id, blocked_user_id)` - Unique block per user per blocked user
- `privacy_settings(user_id)` - Unique privacy settings per user
- `ml_feedback(user_id, feedback_date)` - Unique feedback per user per date
- `community_memberships(group_id, user_id)` - Unique membership per group per user
- `community_connections(user_id, connection_id)` - Unique connection per user per connection

## 📊 Data Distribution

### Exercise Distribution by Muscle Group

| Muscle Group | Count | Percentage |
|--------------|-------|------------|
| LEGS | 46 | 29.3% |
| CORE | 21 | 13.4% |
| BACK | 19 | 12.1% |
| SHOULDERS | 18 | 11.5% |
| FULL_BODY | 17 | 10.8% |
| CHEST | 12 | 7.6% |
| TRICEPS | 9 | 5.7% |
| BICEPS | 9 | 5.7% |
| GLUTES | 6 | 3.8% |

### Exercise Distribution by Equipment

| Equipment | Count | Percentage |
|-----------|-------|------------|
| NONE | 36 | 22.9% |
| DUMBBELL | 33 | 21.0% |
| BARBELL | 31 | 19.7% |
| OTHER | 20 | 12.7% |
| CABLE | 14 | 8.9% |
| KETTLEBELL | 10 | 6.4% |
| MACHINE | 8 | 5.1% |
| BANDS | 5 | 3.2% |

## 🎯 Common Queries

### Get User's Recent Workouts

```sql
SELECT w.*, COUNT(we.id) as exercise_count
FROM workouts w
LEFT JOIN workout_exercises we ON w.id = we.workout_id
WHERE w.user_id = $1
GROUP BY w.id
ORDER BY w.scheduled_date DESC
LIMIT 10;
```

### Get Exercise Recommendations by Muscle Group

```sql
SELECT e.*, e.difficulty
FROM exercises e
WHERE e.primary_muscle = $1
  AND e.difficulty <= $2
  AND e.equipment = ANY($3)
ORDER BY e.difficulty, e.name
LIMIT 10;
```

### Get User Progress Over Time

```sql
SELECT date, weight, body_fat_percentage, total_workouts
FROM user_stats
WHERE user_id = $1
  AND date >= $2
ORDER BY date;
```

### Get User's Personal Records

```sql
SELECT us.personal_records
FROM user_stats us
WHERE us.user_id = $1
ORDER BY us.date DESC
LIMIT 1;
```

## 🔧 Database Management

### Indexes

Recommended indexes for performance:

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Workout queries
CREATE INDEX idx_workouts_user_date ON workouts(user_id, scheduled_date);
CREATE INDEX idx_workouts_status ON workouts(status);

-- Exercise queries
CREATE INDEX idx_exercises_muscle ON exercises(primary_muscle);
CREATE INDEX idx_exercises_equipment ON exercises(equipment);
CREATE INDEX idx_exercises_difficulty ON exercises(difficulty);

-- Stats queries
CREATE INDEX idx_user_stats_user_date ON user_stats(user_id, date);

-- Friendship queries
CREATE INDEX idx_friendships_users ON friendships(user_id, friend_id);

-- Safety reports
CREATE INDEX idx_safety_reports_user_date ON safety_reports(user_id, report_date);

-- User blocks
CREATE INDEX idx_user_blocks_user_blocked ON user_blocks(user_id, blocked_user_id);

-- Privacy settings
CREATE INDEX idx_privacy_settings_user ON privacy_settings(user_id);

-- ML feedback
CREATE INDEX idx_ml_feedback_user_date ON ml_feedback(user_id, feedback_date);

-- Community groups
CREATE INDEX idx_community_groups_name ON community_groups(name);

-- Community memberships
CREATE INDEX idx_community_memberships_group ON community_memberships(group_id);

-- Community connections
CREATE INDEX idx_community_connections_user ON community_connections(user_id);
CREATE INDEX idx_community_connections_connection ON community_connections(connection_id);
```

### Maintenance

Regular maintenance tasks:

```sql
-- Update user stats
UPDATE user_stats
SET total_workouts = (
    SELECT COUNT(*)
    FROM workouts
    WHERE user_id = user_stats.user_id
      AND status = 'completed'
);

-- Clean up old stats (keep last 2 years)
DELETE FROM user_stats
WHERE date < CURRENT_DATE - INTERVAL '2 years';

-- Update workout completion times
UPDATE workouts
SET total_duration = EXTRACT(EPOCH FROM (completed_at - started_at)) / 60
WHERE completed_at IS NOT NULL AND started_at IS NOT NULL;
```

## 🚀 Performance Considerations

1. **Partitioning**: Consider partitioning `user_stats` by date for large datasets
2. **Archiving**: Archive old workout data to separate tables
3. **Caching**: Cache frequently accessed exercise data in Redis
4. **Connection Pooling**: Use connection pooling for better performance
5. **Read Replicas**: Consider read replicas for analytics queries

## 🔒 Security Considerations

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **SQL Injection**: Use parameterized queries only
3. **Row Level Security**: Consider implementing RLS for multi-tenant scenarios
4. **Data Encryption**: Encrypt sensitive user data at rest
5. **Audit Logging**: Log all data modifications for compliance

## Test Data Note

Synthetic test data is annotated with 'test' for easy separation and cleanup.