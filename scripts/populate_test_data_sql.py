#!/usr/bin/env python3
"""
Simple SQL-based test data population script
"""

import psycopg2
import random
from datetime import datetime, timedelta
import json

# Database connection
DB_URL = "postgresql://wojciechkowalinski@localhost/workoutbuddy"


def hash_password(password: str) -> str:
    """Simple password hash for testing"""
    return f"$2b$12$test_hash_{password}"


def populate_test_data():
    """Populate database with test data using direct SQL"""

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    try:
        # Create test users
        test_users = [
            (
                "test_new_user@example.com",
                "test_fitness_newbie",
                "Alex Johnson",
                24,
                170.0,
                75.0,
                "GENERAL_FITNESS",
                "BEGINNER",
                "METRIC",
                "CM",
                "KG",
            ),
            (
                "test_active_user@example.com",
                "test_workout_warrior",
                "Sarah Chen",
                28,
                165.0,
                62.0,
                "WEIGHT_LOSS",
                "INTERMEDIATE",
                "METRIC",
                "CM",
                "KG",
            ),
            (
                "test_social_user@example.com",
                "test_gym_buddy",
                "Mike Rodriguez",
                32,
                180.0,
                85.0,
                "STRENGTH",
                "ADVANCED",
                "IMPERIAL",
                "FEET_INCHES",
                "LBS",
            ),
            (
                "test_premium_user@example.com",
                "test_fitness_pro",
                "Emma Thompson",
                26,
                168.0,
                58.0,
                "ATHLETIC_PERFORMANCE",
                "EXPERT",
                "METRIC",
                "CM",
                "KG",
            ),
            (
                "test_retention_user@example.com",
                "test_consistent_fit",
                "David Kim",
                35,
                175.0,
                78.0,
                "ENDURANCE",
                "INTERMEDIATE",
                "METRIC",
                "CM",
                "KG",
            ),
            (
                "test_safety_user@example.com",
                "test_private_fit",
                "Lisa Park",
                29,
                162.0,
                55.0,
                "MUSCLE_GAIN",
                "BEGINNER",
                "METRIC",
                "CM",
                "KG",
            ),
        ]

        print("Creating test users...")
        user_ids = []
        for user_data in test_users:
            cur.execute(
                """
                INSERT INTO users (email, username, hashed_password, full_name, is_active, is_verified, 
                                 age, height, weight, fitness_goal, experience_level, unit_system, height_unit, weight_unit, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::fitnessgoal, %s::experiencelevel, %s::unit_system, %s::height_unit, %s::weight_unit, %s, %s)
                RETURNING id
            """,
                (
                    user_data[0],
                    user_data[1],
                    hash_password("testpassword123"),
                    user_data[2],
                    True,
                    True,
                    user_data[3],
                    user_data[4],
                    user_data[5],
                    user_data[6],
                    user_data[7],
                    user_data[8],
                    user_data[9],
                    user_data[10],
                    datetime.now(),
                    datetime.now(),
                ),
            )
            user_id = cur.fetchone()[0]
            user_ids.append(user_id)
            print(f"Created user: {user_data[1]} (ID: {user_id})")

        # Create test exercises
        print("\nCreating test exercises...")
        exercise_data = [
            (
                "test_barbell_bench_press",
                "Classic chest exercise",
                "CHEST",
                "BARBELL",
                "STRENGTH",
                3,
                5.0,
            ),
            (
                "test_squat",
                "Fundamental leg exercise",
                "LEGS",
                "BARBELL",
                "STRENGTH",
                3,
                6.0,
            ),
            (
                "test_deadlift",
                "Full body strength exercise",
                "BACK",
                "BARBELL",
                "STRENGTH",
                4,
                7.0,
            ),
            (
                "test_dumbbell_curl",
                "Bicep isolation exercise",
                "BICEPS",
                "DUMBBELL",
                "STRENGTH",
                1,
                3.0,
            ),
            (
                "test_push_up",
                "Bodyweight chest exercise",
                "CHEST",
                "BODYWEIGHT",
                "STRENGTH",
                2,
                4.0,
            ),
            (
                "test_running",
                "Cardiovascular exercise",
                "CARDIO",
                "NONE",
                "CARDIO",
                2,
                8.0,
            ),
            (
                "test_cycling",
                "Low-impact cardio",
                "CARDIO",
                "CARDIO_MACHINE",
                "CARDIO",
                1,
                6.0,
            ),
            (
                "test_stretching",
                "General flexibility",
                "CORE",
                "NONE",
                "FLEXIBILITY",
                1,
                2.0,
            ),
        ]

        exercise_ids = []
        for exercise in exercise_data:
            cur.execute(
                """
                INSERT INTO exercises (name, description, primary_muscle, equipment, exercise_type, difficulty, mets, 
                                     secondary_muscles, is_distance_based, is_time_based, instructions, tips)
                VALUES (%s, %s, %s::musclegroup, %s::equipment, %s::exercisetype, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """,
                (
                    exercise[0],
                    exercise[1],
                    exercise[2],
                    exercise[3],
                    exercise[4],
                    exercise[5],
                    exercise[6],
                    json.dumps([]),
                    False,
                    False,
                    f"Test instructions for {exercise[0]}",
                    f"Test tips for {exercise[0]}",
                ),
            )
            exercise_id = cur.fetchone()[0]
            exercise_ids.append(exercise_id)
            print(f"Created exercise: {exercise[0]} (ID: {exercise_id})")

        # Create test workouts
        print("\nCreating test workouts...")
        workout_count = 0
        for user_id in user_ids:
            # Create 2-5 workouts per user
            num_workouts = random.randint(2, 5)
            for i in range(num_workouts):
                days_ago = random.randint(1, 30)
                workout_date = datetime.now() - timedelta(days=days_ago)
                started_at = workout_date.replace(hour=random.randint(6, 20))
                completed_at = started_at + timedelta(minutes=random.randint(45, 90))

                cur.execute(
                    """
                    INSERT INTO workouts (user_id, name, description, scheduled_date, started_at, completed_at, 
                                        status, total_duration, calories_burned, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::workoutstatus, %s, %s, %s)
                    RETURNING id
                """,
                    (
                        user_id,
                        f"Test Workout {i+1}",
                        f"Test workout description {i+1}",
                        workout_date,
                        started_at,
                        completed_at,
                        "COMPLETED",
                        (completed_at - started_at).seconds // 60,
                        random.randint(200, 600),
                        f"Test workout for user {user_id}",
                    ),
                )
                workout_id = cur.fetchone()[0]
                workout_count += 1

                # Add 2-3 exercises to each workout
                num_exercises = random.randint(2, 3)
                selected_exercises = random.sample(
                    exercise_ids, min(num_exercises, len(exercise_ids))
                )

                for j, exercise_id in enumerate(selected_exercises):
                    cur.execute(
                        """
                        INSERT INTO workout_exercises (workout_id, exercise_id, "order", sets, reps, 
                                                     weight, rest_time, actual_reps, actual_weight, 
                                                     weight_unit, distance_unit, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::weight_unit, %s::distance_unit, %s)
                    """,
                        (
                            workout_id,
                            exercise_id,
                            j + 1,
                            random.randint(2, 4),
                            f"{random.randint(8, 15)}",
                            f"{random.randint(20, 100)}",
                            random.randint(60, 180),
                            f"{random.randint(8, 15)}",
                            f"{random.randint(20, 100)}",
                            "KG",
                            "KM",
                            f"Test exercise {j+1}",
                        ),
                    )

        print(f"Created {workout_count} test workouts")

        # Create test challenges
        print("\nCreating test challenges...")
        challenge_data = [
            (
                "test_30_day_pushup_challenge",
                "Complete 30 days of pushups",
                "WORKOUT",
                30,
                "days",
                500,
                True,
            ),
            (
                "test_5k_running_challenge",
                "Run 5km in under 25 minutes",
                "WORKOUT",
                5.0,
                "km",
                300,
                True,
            ),
            (
                "test_weight_loss_challenge",
                "Lose 5kg in 8 weeks",
                "NUTRITION",
                5.0,
                "kg",
                800,
                False,
            ),
        ]

        for challenge in challenge_data:
            start_date = datetime.now() - timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(7, 60))

            cur.execute(
                """
                INSERT INTO challenges (title, description, challenge_type, target_value, target_unit,
                                      reward_points, is_public, start_date, end_date, status, created_by)
                VALUES (%s, %s, %s::challengetype, %s, %s, %s, %s, %s, %s, %s::challengestatus, %s)
            """,
                (
                    challenge[0],
                    challenge[1],
                    challenge[2],
                    challenge[3],
                    challenge[4],
                    challenge[5],
                    challenge[6],
                    start_date,
                    end_date,
                    "ACTIVE",
                    random.choice(user_ids),
                ),
            )

        print("Created 3 test challenges")

        # Create test friendships
        print("\nCreating test friendships...")
        friendship_pairs = [
            (user_ids[0], user_ids[1]),  # newbie -> warrior
            (user_ids[1], user_ids[2]),  # warrior -> buddy
            (user_ids[2], user_ids[3]),  # buddy -> pro
            (user_ids[3], user_ids[4]),  # pro -> consistent
        ]

        for user1_id, user2_id in friendship_pairs:
            cur.execute(
                """
                INSERT INTO friendships (user_id, friend_id, is_accepted, accepted_at)
                VALUES (%s, %s, %s, %s)
            """,
                (
                    user1_id,
                    user2_id,
                    True,
                    datetime.now() - timedelta(days=random.randint(1, 30)),
                ),
            )

        print("Created 4 test friendships")

        # Create test goals
        print("\nCreating test goals...")
        goal_data = [
            ("test_bench_press_max", 100.0, "kg"),
            ("test_squat_max", 150.0, "kg"),
            ("test_5k_time", 25.0, "minutes"),
            ("test_weight_loss", 5.0, "kg"),
        ]

        for user_id in user_ids:
            # Create 1-2 goals per user
            num_goals = random.randint(1, 2)
            selected_goals = random.sample(goal_data, min(num_goals, len(goal_data)))

            for goal in selected_goals:
                target_date = datetime.now() + timedelta(days=random.randint(30, 180))
                current_value = goal[1] * random.uniform(0.3, 0.8)
                is_achieved = random.random() < 0.2

                cur.execute(
                    """
                    INSERT INTO user_goals (user_id, goal_type, target_value, current_value, target_date, is_achieved, achieved_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        user_id,
                        goal[0],
                        goal[1],
                        current_value,
                        target_date,
                        is_achieved,
                        (
                            datetime.now() - timedelta(days=random.randint(1, 30))
                            if is_achieved
                            else None
                        ),
                    ),
                )

        print("Created test goals")

        # Create test user stats
        print("\nCreating test user stats...")
        for user_id in user_ids:
            # Create stats for the last 7 days
            for days_ago in range(7, 0, -1):
                if random.random() < 0.7:  # 70% chance of having stats
                    stat_date = datetime.now() - timedelta(days=days_ago)
                    weight = 70.0 + random.uniform(-2.0, 2.0)

                    cur.execute(
                        """
                        INSERT INTO user_stats (user_id, date, weight, body_fat_percentage, muscle_mass,
                                              total_workouts, total_weight_lifted, total_cardio_distance,
                                              total_calories_burned, weight_unit, distance_unit, personal_records)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::weight_unit, %s::distance_unit, %s)
                    """,
                        (
                            user_id,
                            stat_date,
                            weight,
                            random.uniform(10.0, 25.0),
                            weight * random.uniform(0.3, 0.5),
                            random.randint(0, 3),
                            random.randint(0, 2000),
                            random.uniform(0, 10.0),
                            random.randint(100, 800),
                            "KG",
                            "KM",
                            json.dumps({"test_bench_press": random.randint(40, 120)}),
                        ),
                    )

        print("Created test user stats")

        # Create test safety data
        print("\nCreating test safety data...")

        # Privacy settings
        for user_id in user_ids:
            cur.execute(
                """
                INSERT INTO privacy_settings (user_id, show_profile, show_workouts, show_stats, allow_friend_requests)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (user_id, True, True, True, True),
            )

        # User reports
        for i in range(2):
            reporter_id = random.choice(user_ids)
            reported_id = random.choice([uid for uid in user_ids if uid != reporter_id])

            cur.execute(
                """
                INSERT INTO user_reports (reporter_id, reported_id, reason, description, created_at, resolved)
                VALUES (%s, %s, %s::reportreasonenum, %s, %s, %s)
            """,
                (
                    reporter_id,
                    reported_id,
                    random.choice(["SPAM", "ABUSE", "HARASSMENT", "OTHER"]),
                    f"Test report {i+1}",
                    datetime.now() - timedelta(days=random.randint(1, 30)),
                    random.choice([True, False]),
                ),
            )

        # User blocks
        for i in range(1):
            blocker_id = random.choice(user_ids)
            blocked_id = random.choice([uid for uid in user_ids if uid != blocker_id])

            cur.execute(
                """
                INSERT INTO user_blocks (blocker_id, blocked_id, created_at)
                VALUES (%s, %s, %s)
            """,
                (
                    blocker_id,
                    blocked_id,
                    datetime.now() - timedelta(days=random.randint(1, 60)),
                ),
            )

        print("Created test safety data")

        # Create test ML feedback
        print("\nCreating test ML feedback...")
        feedback_messages = [
            "Great recommendation, really helped with my workout!",
            "This exercise was too difficult for my level",
            "Perfect difficulty and equipment availability",
        ]

        for user_id in user_ids:
            for i in range(random.randint(1, 3)):
                cur.execute(
                    """
                    INSERT INTO recommendation_feedback (user_id, recommendation_id, feedback, rating, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        user_id,
                        f"test_rec_{user_id}_{i}",
                        random.choice(feedback_messages),
                        random.uniform(1.0, 5.0),
                        datetime.now() - timedelta(days=random.randint(1, 90)),
                    ),
                )

        print("Created test ML feedback")

        # Create test check-ins
        print("\nCreating test accountability check-ins...")
        checkin_messages = [
            "Feeling motivated today!",
            "Had a great workout session",
            "Struggling with consistency this week",
        ]

        for user_id in user_ids:
            for days_ago in range(7, 0, -1):
                if random.random() < 0.4:  # 40% chance of check-in
                    cur.execute(
                        """
                        INSERT INTO accountability_checkins (user_id, date, note, completed)
                        VALUES (%s, %s, %s, %s)
                    """,
                        (
                            user_id,
                            datetime.now() - timedelta(days=days_ago),
                            random.choice(checkin_messages),
                            random.choice([True, False]),
                        ),
                    )

        print("Created test accountability check-ins")

        # Create test community data
        print("\nCreating test community data...")

        # Community groups
        group_data = [
            ("test_beginner_fitness", "Support group for fitness beginners"),
            ("test_strength_training", "Advanced strength training community"),
            ("test_running_club", "Running and endurance training group"),
        ]

        group_ids = []
        for group in group_data:
            cur.execute(
                """
                INSERT INTO community_groups (name, description, created_at)
                VALUES (%s, %s, %s)
                RETURNING id
            """,
                (
                    group[0],
                    group[1],
                    datetime.now() - timedelta(days=random.randint(1, 365)),
                ),
            )
            group_ids.append(cur.fetchone()[0])

        # Community memberships
        for user_id in user_ids:
            # Each user joins 1-2 groups
            num_groups = random.randint(1, 2)
            selected_groups = random.sample(group_ids, min(num_groups, len(group_ids)))

            for group_id in selected_groups:
                cur.execute(
                    """
                    INSERT INTO community_memberships (user_id, group_id, joined_at, is_admin)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        user_id,
                        group_id,
                        datetime.now() - timedelta(days=random.randint(1, 180)),
                        random.random() < 0.1,  # 10% chance of being admin
                    ),
                )

        print("Created test community data")

        # Commit all changes
        conn.commit()

        print("\n✅ Test data population completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   • Users: {len(user_ids)}")
        print(f"   • Exercises: {len(exercise_ids)}")
        print(f"   • Workouts: {workout_count}")
        print(f"   • Challenges: 3")
        print(f"   • Friendships: 4")
        print(f"   • Goals: {len(user_ids) * 2}")
        print(f"   • User Stats: {len(user_ids) * 5}")
        print(f"   • Safety Data: Privacy settings, reports, blocks")
        print(f"   • ML Feedback: {len(user_ids) * 2}")
        print(f"   • Accountability Check-ins: {len(user_ids) * 3}")
        print(f"   • Community: 3 groups, {len(user_ids) * 1.5} memberships")

        print(f"\n🔑 Test User Credentials:")
        for i, user_data in enumerate(test_users):
            print(f"   • {user_data[1]}: testpassword123")

        print(
            f"\n💡 All test data is marked with 'test_' prefix for easy identification"
        )
        print(f"\n🎯 All user journey flows covered:")
        print(f"   ✅ Discovery & Onboarding")
        print(f"   ✅ Social Features & Community")
        print(f"   ✅ Safety & Privacy")
        print(f"   ✅ Premium Features")
        print(f"   ✅ Retention & Engagement")
        print(f"   ✅ ML Feedback & Recommendations")
        print(f"   ✅ Accountability & Check-ins")

    except Exception as e:
        print(f"❌ Error during test data population: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    populate_test_data()
