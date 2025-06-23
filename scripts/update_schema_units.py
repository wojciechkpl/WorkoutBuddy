#!/usr/bin/env python3
"""
Database Schema Update for Dual Unit Support (Metric/Imperial)

This script updates the database schema to support both metric and imperial units
while ensuring all downstream algorithms use metric units internally.

Changes:
1. Add unit preference fields to users table
2. Add unit fields to user_stats table
3. Update workout_exercises to support both units
4. Add unit conversion utilities
5. Update all related models and services
"""

import os
import sys

from sqlalchemy import create_engine, text

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://wojciechkowalinski@localhost/workoutbuddy"
)
engine = create_engine(DATABASE_URL)


def create_unit_enums():
    """Create unit preference enums"""

    with engine.connect() as conn:
        # Create unit preference enum
        conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE unit_system AS ENUM ('METRIC', 'IMPERIAL');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Create weight unit enum
        conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE weight_unit AS ENUM ('KG', 'LBS');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Create height unit enum
        conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE height_unit AS ENUM ('CM', 'INCHES', 'FEET_INCHES');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        # Create distance unit enum
        conn.execute(
            text(
                """
            DO $$ BEGIN
                CREATE TYPE distance_unit AS ENUM ('KM', 'MILES', 'METERS');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """
            )
        )

        conn.commit()
        print("✅ Created unit enums")


def update_users_table():
    """Update users table to support unit preferences"""

    with engine.connect() as conn:
        # Add unit preference columns
        conn.execute(
            text(
                """
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS unit_system unit_system DEFAULT 'METRIC',
            ADD COLUMN IF NOT EXISTS height_unit height_unit DEFAULT 'CM',
            ADD COLUMN IF NOT EXISTS weight_unit weight_unit DEFAULT 'KG';
        """
            )
        )

        # Add comments for clarity
        conn.execute(
            text(
                """
            COMMENT ON COLUMN users.unit_system IS 'User preference for unit system (METRIC/IMPERIAL)';
            COMMENT ON COLUMN users.height_unit IS 'Unit for height measurements (CM/INCHES/FEET_INCHES)';
            COMMENT ON COLUMN users.weight_unit IS 'Unit for weight measurements (KG/LBS)';
        """
            )
        )

        conn.commit()
        print("✅ Updated users table with unit preferences")


def update_user_stats_table():
    """Update user_stats table to support unit tracking"""

    with engine.connect() as conn:
        # Add unit columns
        conn.execute(
            text(
                """
            ALTER TABLE user_stats
            ADD COLUMN IF NOT EXISTS weight_unit weight_unit DEFAULT 'KG',
            ADD COLUMN IF NOT EXISTS distance_unit distance_unit DEFAULT 'KM';
        """
            )
        )

        # Add comments
        conn.execute(
            text(
                """
            COMMENT ON COLUMN user_stats.weight_unit IS 'Unit for weight measurements in this record';
            COMMENT ON COLUMN user_stats.distance_unit IS 'Unit for distance measurements in this record';
        """
            )
        )

        conn.commit()
        print("✅ Updated user_stats table with unit tracking")


def update_workout_exercises_table():
    """Update workout_exercises table to support unit preferences"""

    with engine.connect() as conn:
        # Add unit columns
        conn.execute(
            text(
                """
            ALTER TABLE workout_exercises
            ADD COLUMN IF NOT EXISTS weight_unit weight_unit DEFAULT 'KG',
            ADD COLUMN IF NOT EXISTS distance_unit distance_unit DEFAULT 'METERS';
        """
            )
        )

        # Add comments
        conn.execute(
            text(
                """
            COMMENT ON COLUMN workout_exercises.weight_unit IS 'Unit for weight in this exercise';
            COMMENT ON COLUMN workout_exercises.distance_unit IS 'Unit for distance in this exercise';
        """
            )
        )

        conn.commit()
        print("✅ Updated workout_exercises table with unit support")


def create_unit_conversion_functions():
    """Create PostgreSQL functions for unit conversions"""

    with engine.connect() as conn:
        # Weight conversion functions
        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION lbs_to_kg(lbs DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN lbs * 0.45359237;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION kg_to_lbs(kg DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN kg * 2.20462262;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        # Height conversion functions
        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION inches_to_cm(inches DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN inches * 2.54;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION cm_to_inches(cm DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN cm / 2.54;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        # Distance conversion functions
        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION miles_to_km(miles DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN miles * 1.609344;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION km_to_miles(km DOUBLE PRECISION)
            RETURNS DOUBLE PRECISION AS $$
            BEGIN
                RETURN km / 1.609344;
            END;
            $$ LANGUAGE plpgsql;
        """
            )
        )

        conn.commit()
        print("✅ Created unit conversion functions")


def create_views_for_metric_data():
    """Create views that always return metric data for algorithms"""

    with engine.connect() as conn:
        # View for users with metric units
        conn.execute(
            text(
                """
            CREATE OR REPLACE VIEW users_metric AS
            SELECT
                id,
                email,
                username,
                full_name,
                is_active,
                is_verified,
                age,
                CASE
                    WHEN height_unit = 'INCHES' THEN inches_to_cm(height)
                    WHEN height_unit = 'FEET_INCHES' THEN inches_to_cm(height * 12)
                    ELSE height
                END as height_cm,
                CASE
                    WHEN weight_unit = 'LBS' THEN lbs_to_kg(weight)
                    ELSE weight
                END as weight_kg,
                fitness_goal,
                experience_level,
                unit_system,
                height_unit,
                weight_unit,
                created_at,
                updated_at
            FROM users;
        """
            )
        )

        # View for user_stats with metric units
        conn.execute(
            text(
                """
            CREATE OR REPLACE VIEW user_stats_metric AS
            SELECT
                id,
                user_id,
                date,
                CASE
                    WHEN weight_unit = 'LBS' THEN lbs_to_kg(weight)
                    ELSE weight
                END as weight_kg,
                body_fat_percentage,
                muscle_mass,
                total_workouts,
                total_weight_lifted,
                CASE
                    WHEN distance_unit = 'MILES' THEN miles_to_km(total_cardio_distance)
                    ELSE total_cardio_distance
                END as total_cardio_distance_km,
                total_calories_burned,
                personal_records,
                weight_unit,
                distance_unit
            FROM user_stats;
        """
            )
        )

        # View for workout_exercises with metric units
        conn.execute(
            text(
                """
            CREATE OR REPLACE VIEW workout_exercises_metric AS
            SELECT
                id,
                workout_id,
                exercise_id,
                "order",
                sets,
                reps,
                CASE
                    WHEN weight_unit = 'LBS' THEN lbs_to_kg(CAST(weight AS DOUBLE PRECISION))
                    ELSE CAST(weight AS DOUBLE PRECISION)
                END as weight_kg,
                duration,
                CASE
                    WHEN distance_unit = 'MILES' THEN miles_to_km(distance)
                    ELSE distance
                END as distance_meters,
                speed,
                incline,
                rest_time,
                actual_reps,
                actual_weight,
                notes,
                weight_unit,
                distance_unit
            FROM workout_exercises;
        """
            )
        )

        conn.commit()
        print("✅ Created metric views for algorithms")


def main():
    """Main function to update schema for dual unit support"""

    print("🚀 Starting database schema update for dual unit support...")
    print("=" * 70)

    try:
        # Create unit enums
        print("\n1. Creating unit enums...")
        create_unit_enums()

        # Update tables
        print("\n2. Updating users table...")
        update_users_table()

        print("\n3. Updating user_stats table...")
        update_user_stats_table()

        print("\n4. Updating workout_exercises table...")
        update_workout_exercises_table()

        # Create conversion functions
        print("\n5. Creating unit conversion functions...")
        create_unit_conversion_functions()

        # Create metric views
        print("\n6. Creating metric views for algorithms...")
        create_views_for_metric_data()

        print("\n" + "=" * 70)
        print("🎉 Database schema updated successfully!")
        print("\n📋 Changes Made:")
        print("   ✅ Added unit_system, height_unit, weight_unit to users table")
        print("   ✅ Added weight_unit, distance_unit to user_stats table")
        print("   ✅ Added weight_unit, distance_unit to workout_exercises table")
        print("   ✅ Created unit conversion functions (lbs↔kg, inches↔cm, miles↔km)")
        print("   ✅ Created metric views for all algorithms")
        print("\n🔧 Usage:")
        print(
            "   • Use metric views (users_metric, user_stats_metric, etc.) for algorithms"
        )
        print(
            "   • Store user preferences in unit_system, height_unit, weight_unit fields"
        )
        print("   • Convert display units using the conversion functions")
        print("\n✅ All downstream algorithms will use metric units automatically!")

    except Exception as e:
        print(f"\n❌ Error updating schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
