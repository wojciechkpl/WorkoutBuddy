#!/usr/bin/env python3
"""
Quick database analysis script for WorkoutBuddy
Run this for a fast overview of your database without opening Jupyter
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from collections import Counter

# Add app directory to path
sys.path.append("app")


def main():
    print("🏋️ WorkoutBuddy Database Quick Analysis")
    print("=" * 50)

    # Database connection
    try:
        from app.config import backend_config

        DATABASE_URL = backend_config.database.url
    except ImportError:
        DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workoutbuddy.db")

    engine = create_engine(DATABASE_URL)

    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Load exercise data
    try:
        exercises_df = pd.read_sql("SELECT * FROM exercises", engine)
        print(f"\n📊 Found {len(exercises_df)} exercises in database")
    except Exception as e:
        print(f"❌ Error loading exercises: {e}")
        return

    # Basic statistics
    print(f"\n📈 Basic Statistics:")
    print(f"   • Total exercises: {len(exercises_df)}")
    print(f"   • Unique muscle groups: {exercises_df['main_muscle_group'].nunique()}")
    print(f"   • Equipment types: {exercises_df['equipment'].nunique()}")
    print(f"   • Difficulty levels: {exercises_df['difficulty'].nunique()}")

    # Top muscle groups
    print(f"\n🎯 Top 5 Muscle Groups:")
    muscle_groups = exercises_df["main_muscle_group"].value_counts().head(5)
    for muscle, count in muscle_groups.items():
        print(f"   • {muscle}: {count} exercises")

    # Equipment distribution
    print(f"\n🛠️ Top 5 Equipment Types:")
    equipment = exercises_df["equipment"].value_counts().head(5)
    for equip, count in equipment.items():
        print(f"   • {equip}: {count} exercises")

    # Difficulty distribution
    print(f"\n🏆 Difficulty Distribution:")
    difficulty = exercises_df["difficulty"].value_counts()
    for diff, count in difficulty.items():
        percentage = (count / len(exercises_df)) * 100
        print(f"   • {diff}: {count} exercises ({percentage:.1f}%)")

    # Data quality check
    print(f"\n🔍 Data Quality:")
    missing_data = exercises_df.isnull().sum()
    if missing_data.sum() == 0:
        print("   ✅ No missing values found")
    else:
        print("   ⚠️ Missing values detected:")
        for col, missing in missing_data[missing_data > 0].items():
            print(f"      • {col}: {missing} missing")

    # Check for duplicates
    duplicates = exercises_df.duplicated(subset=["name"]).sum()
    if duplicates == 0:
        print("   ✅ No duplicate exercise names")
    else:
        print(f"   ⚠️ {duplicates} duplicate exercise names found")

    # Sample exercises by category
    print(f"\n🏋️ Sample Exercises:")

    # Beginner exercises
    beginner = exercises_df[exercises_df["difficulty"] == "Beginner"]["name"].head(3)
    if not beginner.empty:
        print(f"   Beginner: {', '.join(beginner.tolist())}")

    # Dumbbell exercises
    dumbbell = exercises_df[
        exercises_df["equipment"].str.contains("Dumbbells", na=False)
    ]["name"].head(3)
    if not dumbbell.empty:
        print(f"   Dumbbell: {', '.join(dumbbell.tolist())}")

    # Chest exercises
    chest = exercises_df[
        exercises_df["main_muscle_group"].str.contains("Chest", na=False)
    ]["name"].head(3)
    if not chest.empty:
        print(f"   Chest: {', '.join(chest.tolist())}")

    # Check other tables
    print(f"\n👥 Other Tables:")
    try:
        users_count = pd.read_sql("SELECT COUNT(*) as count FROM users", engine)[
            "count"
        ].iloc[0]
        print(f"   • Users: {users_count}")
    except:
        print("   • Users: Table not accessible")

    try:
        goals_count = pd.read_sql("SELECT COUNT(*) as count FROM goals", engine)[
            "count"
        ].iloc[0]
        print(f"   • Goals: {goals_count}")
    except:
        print("   • Goals: Table not accessible")

    print(f"\n🚀 Next Steps:")
    print(f"   • Run 'uv run python start_jupyter.py' for detailed analysis")
    print(f"   • Open workoutbuddy_exploration.ipynb for interactive visualizations")
    print(f"   • Use the exercise data for ML model training")

    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
