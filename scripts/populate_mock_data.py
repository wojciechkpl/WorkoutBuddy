#!/usr/bin/env python3
"""
Mock Data Population Script for WorkoutBuddy AI Services Testing

This script populates the database with realistic mock data for testing
the AI services notebook. All accounts are clearly marked as test accounts.

Usage:
    python scripts/populate_mock_data.py
"""

import hashlib
import os
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://wojciechkowalinski@localhost/workoutbuddy"
)
engine = create_engine(DATABASE_URL)


# Create a mock user class that matches the database schema
class DatabaseUser:
    def __init__(self, user_data):
        self.id = user_data.get("id")
        self.username = user_data.get("username")
        self.email = user_data.get("email")
        self.full_name = user_data.get("full_name")
        self.fitness_goal = user_data.get("fitness_goal", "general")
        self.experience_level = user_data.get("experience_level", "beginner")
        self.height = user_data.get("height")
        self.weight = user_data.get("weight")
        self.age = user_data.get("age")
        self.is_active = user_data.get("is_active", True)
        self.is_verified = user_data.get("is_verified", True)
        # For compatibility with AI services
        self.first_name = self.full_name.split()[0] if self.full_name else "User"
        self.last_name = (
            " ".join(self.full_name.split()[1:])
            if self.full_name and len(self.full_name.split()) > 1
            else ""
        )


def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_mock_users():
    """Create mock users with clear test annotations"""

    mock_users = [
        {
            "username": "test_alice_fitness",
            "email": "test.alice@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "Alice Johnson",
            "fitness_goal": "ENDURANCE",
            "experience_level": "INTERMEDIATE",
            "height": 165.0,
            "weight": 60.0,
            "age": 34,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=30),
            "updated_at": datetime.now() - timedelta(days=1),
        },
        {
            "username": "test_bob_strength",
            "email": "test.bob@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "Bob Smith",
            "fitness_goal": "STRENGTH",
            "experience_level": "ADVANCED",
            "height": 180.0,
            "weight": 85.0,
            "age": 36,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=45),
            "updated_at": datetime.now() - timedelta(days=2),
        },
        {
            "username": "test_carol_flexibility",
            "email": "test.carol@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "Carol Davis",
            "fitness_goal": "GENERAL_FITNESS",
            "experience_level": "BEGINNER",
            "height": 160.0,
            "weight": 55.0,
            "age": 29,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=20),
            "updated_at": datetime.now() - timedelta(days=1),
        },
        {
            "username": "test_david_cardio",
            "email": "test.david@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "David Wilson",
            "fitness_goal": "ENDURANCE",
            "experience_level": "INTERMEDIATE",
            "height": 175.0,
            "weight": 70.0,
            "age": 32,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=60),
            "updated_at": datetime.now() - timedelta(days=3),
        },
        {
            "username": "test_emma_wellness",
            "email": "test.emma@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "Emma Brown",
            "fitness_goal": "GENERAL_FITNESS",
            "experience_level": "BEGINNER",
            "height": 168.0,
            "weight": 62.0,
            "age": 31,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=15),
            "updated_at": datetime.now() - timedelta(days=1),
        },
        {
            "username": "test_frank_muscle",
            "email": "test.frank@workoutbuddy.test",
            "hashed_password": hash_password("testpass123"),
            "full_name": "Frank Miller",
            "fitness_goal": "MUSCLE_GAIN",
            "experience_level": "ADVANCED",
            "height": 185.0,
            "weight": 90.0,
            "age": 39,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now() - timedelta(days=90),
            "updated_at": datetime.now() - timedelta(days=5),
        },
    ]

    with engine.connect() as conn:
        for user in mock_users:
            # Check if user already exists
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"), user
            )
            if result.fetchone():
                print(f"User {user['email']} already exists, skipping...")
                continue

            # Insert user
            result = conn.execute(
                text(
                    """
                INSERT INTO users (
                    username, email, hashed_password, full_name,
                    fitness_goal, experience_level, height, weight, age,
                    is_active, is_verified, created_at, updated_at
                ) VALUES (
                    :username, :email, :hashed_password, :full_name,
                    :fitness_goal, :experience_level, :height, :weight, :age,
                    :is_active, :is_verified, :created_at, :updated_at
                ) RETURNING id
            """
                ),
                user,
            )

            user_id = result.fetchone()[0]
            print(f"✅ Created test user: {user['full_name']} (ID: {user_id})")

            # Create user goals
            create_user_goals(conn, user_id, user["fitness_goal"])

            # Create user stats
            create_user_stats(conn, user_id, user["fitness_goal"])

            # Create workouts
            create_user_workouts(
                conn, user_id, user["fitness_goal"], user["experience_level"]
            )

    print(f"\n🎉 Created {len(mock_users)} test users with complete profiles!")


def create_user_goals(conn, user_id, fitness_goal):
    """Create mock goals for a user"""

    goal_templates = {
        "ENDURANCE": [
            ("5K Run Time", 25),
            ("Cardio Sessions/Week", 3),
            ("VO2 Max", 45),
        ],
        "STRENGTH": [
            ("Bench Press (kg)", 80),
            ("Squat (kg)", 120),
            ("Deadlift (kg)", 140),
        ],
        "GENERAL_FITNESS": [
            ("Weekly Workouts", 4),
            ("Flexibility Score", 7),
            ("Energy Level", 8),
        ],
        "MUSCLE_GAIN": [
            ("Muscle Mass (kg)", 5),
            ("Bench Press (kg)", 90),
            ("Body Fat (%)", 15),
        ],
        "WEIGHT_LOSS": [("Weight (kg)", 70), ("Body Fat (%)", 18), ("BMI", 22)],
        "ATHLETIC_PERFORMANCE": [
            ("Sprint Time (s)", 12),
            ("Vertical Jump (cm)", 60),
            ("Agility Score", 9),
        ],
    }

    goals = goal_templates.get(fitness_goal, [("General Fitness", 1)])

    for i, (goal_type, target_value) in enumerate(goals):
        current_value = target_value * random.uniform(0.5, 0.9)
        is_achieved = current_value >= target_value
        goal = {
            "user_id": user_id,
            "goal_type": f"[TEST] {goal_type}",
            "target_value": target_value,
            "current_value": current_value,
            "target_date": (datetime.now() + timedelta(days=90)),
            "is_achieved": is_achieved,
            "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
            "achieved_at": datetime.now() if is_achieved else None,
        }

        conn.execute(
            text(
                """
            INSERT INTO user_goals (
                user_id, goal_type, target_value, current_value, target_date, is_achieved, created_at, achieved_at
            ) VALUES (
                :user_id, :goal_type, :target_value, :current_value, :target_date, :is_achieved, :created_at, :achieved_at
            )
        """
            ),
            goal,
        )

    print(f"   📋 Created {len(goals)} test goals for user {user_id}")


def create_user_stats(conn, user_id, fitness_goal):
    """Create mock user statistics"""
    # Generate realistic stats based on fitness goal
    if fitness_goal == "ENDURANCE":
        weight = random.uniform(55, 75)
        body_fat = random.uniform(15, 22)
        muscle_mass = random.uniform(20, 30)
        total_cardio_distance = random.uniform(30, 120)  # km
        total_weight_lifted = random.uniform(1000, 3000)  # kg
    elif fitness_goal == "STRENGTH":
        weight = random.uniform(70, 100)
        body_fat = random.uniform(12, 18)
        muscle_mass = random.uniform(30, 40)
        total_cardio_distance = random.uniform(5, 20)
        total_weight_lifted = random.uniform(5000, 20000)
    elif fitness_goal == "MUSCLE_GAIN":
        weight = random.uniform(75, 110)
        body_fat = random.uniform(10, 18)
        muscle_mass = random.uniform(35, 45)
        total_cardio_distance = random.uniform(5, 15)
        total_weight_lifted = random.uniform(8000, 25000)
    else:
        weight = random.uniform(55, 80)
        body_fat = random.uniform(18, 25)
        muscle_mass = random.uniform(18, 28)
        total_cardio_distance = random.uniform(10, 40)
        total_weight_lifted = random.uniform(1000, 5000)

    stats = {
        "user_id": user_id,
        "date": datetime.now() - timedelta(days=random.randint(0, 7)),
        "weight": weight,
        "body_fat_percentage": body_fat,
        "muscle_mass": muscle_mass,
        "total_workouts": random.randint(5, 50),
        "total_weight_lifted": total_weight_lifted,
        "total_cardio_distance": total_cardio_distance,
        "total_calories_burned": random.randint(1000, 8000),
        "personal_records": "[TEST] Bench 100kg, 5K Run 24min",
    }

    conn.execute(
        text(
            """
        INSERT INTO user_stats (
            user_id, date, weight, body_fat_percentage, muscle_mass, total_workouts,
            total_weight_lifted, total_cardio_distance, total_calories_burned, personal_records
        ) VALUES (
            :user_id, :date, :weight, :body_fat_percentage, :muscle_mass, :total_workouts,
            :total_weight_lifted, :total_cardio_distance, :total_calories_burned, :personal_records
        )
    """
        ),
        stats,
    )

    print(f"   📊 Created test stats for user {user_id}")


def create_user_workouts(conn, user_id, fitness_goal, experience_level):
    """Create mock workouts for a user"""
    # Get some exercise IDs for this user's fitness goal
    exercise_query = """
        SELECT id FROM exercises
        WHERE primary_muscle IN ('FULL_BODY', 'CARDIO', 'CHEST', 'BACK', 'LEGS')
        ORDER BY RANDOM()
        LIMIT 10
    """
    exercises = conn.execute(text(exercise_query)).fetchall()
    exercise_ids = [ex[0] for ex in exercises]

    if not exercise_ids:
        print(f"   ⚠️ No exercises found for user {user_id}")
        return

    # Create 5-15 workouts over the last 30 days
    num_workouts = random.randint(5, 15)

    for i in range(num_workouts):
        # Random date within last 30 days
        workout_date = datetime.now() - timedelta(days=random.randint(0, 30))
        scheduled_date = workout_date
        started_at = workout_date.replace(
            hour=random.randint(6, 20), minute=random.randint(0, 59)
        )
        total_duration = random.randint(20, 90)  # minutes
        completed_at = started_at + timedelta(minutes=total_duration)
        status = random.choice(["PLANNED", "IN_PROGRESS", "COMPLETED", "SKIPPED"])
        calories_burned = random.randint(150, 500)
        total_volume = random.uniform(1000, 10000)
        total_distance = (
            random.uniform(1, 10) if fitness_goal in ["ENDURANCE", "CARDIO"] else 0.0
        )

        workout = {
            "user_id": user_id,
            "name": f"[TEST] {fitness_goal.title()} Workout #{i+1}",
            "description": f"Test workout for AI services demonstration - {fitness_goal} focus",
            "scheduled_date": scheduled_date,
            "started_at": started_at,
            "completed_at": completed_at,
            "status": status,
            "total_duration": total_duration,
            "calories_burned": calories_burned,
            "total_volume": total_volume,
            "total_distance": total_distance,
            "notes": f"Test workout session for user {user_id}",
            "created_at": started_at,
            "updated_at": completed_at,
        }

        result = conn.execute(
            text(
                """
            INSERT INTO workouts (
                user_id, name, description, scheduled_date, started_at, completed_at, status,
                total_duration, calories_burned, total_volume, total_distance, notes, created_at, updated_at
            ) VALUES (
                :user_id, :name, :description, :scheduled_date, :started_at, :completed_at, :status,
                :total_duration, :calories_burned, :total_volume, :total_distance, :notes, :created_at, :updated_at
            ) RETURNING id
        """
            ),
            workout,
        )

        workout_id = result.fetchone()[0]

        # Add 3-8 exercises to this workout
        num_exercises = random.randint(3, 8)
        selected_exercises = random.sample(
            exercise_ids, min(num_exercises, len(exercise_ids))
        )

        for j, exercise_id in enumerate(selected_exercises):
            workout_exercise = {
                "workout_id": workout_id,
                "exercise_id": exercise_id,
                "order": j + 1,
                "sets": random.randint(2, 4),
                "reps": str(random.randint(8, 15)),
                "weight": str(
                    random.uniform(5.0, 50.0)
                    if experience_level != "BEGINNER"
                    else random.uniform(2.0, 20.0)
                ),
                "duration": random.randint(30, 120),
                "distance": (
                    random.uniform(100, 1000)
                    if fitness_goal in ["ENDURANCE", "CARDIO"]
                    else None
                ),
                "speed": (
                    random.uniform(5.0, 15.0)
                    if fitness_goal in ["ENDURANCE", "CARDIO"]
                    else None
                ),
                "incline": (
                    random.uniform(0, 10)
                    if fitness_goal in ["ENDURANCE", "CARDIO"]
                    else None
                ),
                "rest_time": random.randint(30, 180),
                "actual_reps": str(random.randint(6, 12)),
                "actual_weight": str(
                    random.uniform(4.0, 45.0)
                    if experience_level != "BEGINNER"
                    else random.uniform(1.5, 18.0)
                ),
                "notes": f"Test exercise {j+1} in workout {workout_id}",
            }

            conn.execute(
                text(
                    """
                INSERT INTO workout_exercises (
                    workout_id, exercise_id, "order", sets, reps, weight, duration, distance, speed, incline, rest_time, actual_reps, actual_weight, notes
                ) VALUES (
                    :workout_id, :exercise_id, :order, :sets, :reps, :weight, :duration, :distance, :speed, :incline, :rest_time, :actual_reps, :actual_weight, :notes
                )
            """
                ),
                workout_exercise,
            )

        print(f"   💪 Created test workout {i+1}/{num_workouts} for user {user_id}")


def create_friendships():
    """Create mock friendships between test users"""

    with engine.connect() as conn:
        # Get all test user IDs
        result = conn.execute(
            text("SELECT id FROM users WHERE email LIKE '%@workoutbuddy.test'")
        )
        user_ids = [row[0] for row in result.fetchall()]

        if len(user_ids) < 2:
            print("⚠️ Need at least 2 test users to create friendships")
            return

        # Create some friendships
        friendships = [
            (user_ids[0], user_ids[1]),  # Alice - Bob
            (user_ids[0], user_ids[3]),  # Alice - David
            (user_ids[1], user_ids[5]),  # Bob - Frank
            (user_ids[2], user_ids[4]),  # Carol - Emma
            (user_ids[3], user_ids[4]),  # David - Emma
        ]

        for user1_id, user2_id in friendships:
            # Check if friendship already exists
            result = conn.execute(
                text(
                    """
                SELECT id FROM friendships
                WHERE (user_id = :user1 AND friend_id = :user2)
                   OR (user_id = :user2 AND friend_id = :user1)
            """
                ),
                {"user1": user1_id, "user2": user2_id},
            )

            if result.fetchone():
                continue

            friendship = {
                "user_id": user1_id,
                "friend_id": user2_id,
                "status": "accepted",
                "created_at": datetime.now() - timedelta(days=random.randint(1, 30)),
            }

            conn.execute(
                text(
                    """
                INSERT INTO friendships (user_id, friend_id, status, created_at)
                VALUES (:user_id, :friend_id, :status, :created_at)
            """
                ),
                friendship,
            )

            print(f"   🤝 Created friendship between users {user1_id} and {user2_id}")

    print(f"✅ Created {len(friendships)} test friendships!")


def main():
    """Main function to populate all mock data"""

    print("🚀 Starting mock data population for WorkoutBuddy AI Services testing...")
    print("=" * 70)

    try:
        # Create mock users with complete profiles
        print("\n1. Creating test users...")
        create_mock_users()

        # Create friendships
        print("\n2. Creating test friendships...")
        create_friendships()

        print("\n" + "=" * 70)
        print("🎉 Mock data population completed successfully!")
        print("\n📋 Test Accounts Created:")
        print("   • test_alice_fitness (Alice Johnson) - Cardio, Intermediate")
        print("   • test_bob_strength (Bob Smith) - Strength, Advanced")
        print("   • test_carol_flexibility (Carol Davis) - Flexibility, Beginner")
        print("   • test_david_cardio (David Wilson) - Cardio, Intermediate")
        print("   • test_emma_wellness (Emma Brown) - Wellness, Beginner")
        print("   • test_frank_muscle (Frank Miller) - Muscle Gain, Advanced")
        print("\n🔑 All test accounts use password: testpass123")
        print("📧 All emails end with @workoutbuddy.test")
        print("🏷️ All data is clearly marked with [TEST] prefix")
        print("\n✅ You can now run the ai_services_example.ipynb notebook!")

    except Exception as e:
        print(f"\n❌ Error populating mock data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
