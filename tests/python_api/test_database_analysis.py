#!/usr/bin/env python3
"""
Enhanced Database Analysis Test for WorkoutBuddy

Tests database connectivity, configuration loading, and provides
comprehensive analysis when database tables are available.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from collections import Counter

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Also set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = str(project_root)


class DatabaseAnalysisTest:
    """Enhanced database analysis and testing"""

    def __init__(self):
        self.engine = None
        self.database_url = None
        self.test_results = []

    def load_configuration(self):
        """Load and validate configuration"""
        try:
            from ml_backend.app.config import backend_config

            self.database_url = backend_config.database.url
            print(f"✅ Configuration loaded successfully")
            print(f"   Database URL: {self.database_url}")
            print(
                f"   AI Service: {'Enabled' if backend_config.ai.enabled else 'Disabled'}"
            )
            print(
                f"   Analytics: {'Enabled' if backend_config.analytics.enabled else 'Disabled'}"
            )
            return True
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
            # Fallback to environment variable
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///./workoutbuddy.db")
            print(f"⚠️  Using fallback database URL: {self.database_url}")
            return False

    def test_database_connection(self):
        """Test database connectivity"""
        try:
            self.engine = create_engine(self.database_url)
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                assert result[0] == 1
            print("✅ Database connection successful!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def analyze_database_schema(self):
        """Analyze database schema and available tables"""
        try:
            inspector = inspect(self.engine)
            table_names = inspector.get_table_names()

            if not table_names:
                print("ℹ️  No tables found in database (expected for new setup)")
                return []

            print(f"📊 Found {len(table_names)} tables:")
            for table in table_names:
                columns = inspector.get_columns(table)
                print(f"   • {table}: {len(columns)} columns")

            return table_names
        except Exception as e:
            print(f"⚠️  Schema analysis failed: {e}")
            return []

    def analyze_exercises_table(self):
        """Analyze exercises table if available"""
        try:
            exercises_df = pd.read_sql("SELECT * FROM exercises", self.engine)
            print(f"\n📈 Exercises Table Analysis:")
            print(f"   • Total exercises: {len(exercises_df)}")

            if len(exercises_df) > 0:
                # Basic statistics
                if "main_muscle_group" in exercises_df.columns:
                    unique_muscle_groups = exercises_df["main_muscle_group"].nunique()
                    print(f"   • Unique muscle groups: {unique_muscle_groups}")

                if "equipment" in exercises_df.columns:
                    equipment_types = exercises_df["equipment"].nunique()
                    print(f"   • Equipment types: {equipment_types}")

                if "difficulty" in exercises_df.columns:
                    difficulty_levels = exercises_df["difficulty"].nunique()
                    print(f"   • Difficulty levels: {difficulty_levels}")

                # Top categories
                if "main_muscle_group" in exercises_df.columns:
                    print(f"\n🎯 Top 5 Muscle Groups:")
                    muscle_groups = (
                        exercises_df["main_muscle_group"].value_counts().head(5)
                    )
                    for muscle, count in muscle_groups.items():
                        print(f"   • {muscle}: {count} exercises")

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
                if "name" in exercises_df.columns:
                    duplicates = exercises_df.duplicated(subset=["name"]).sum()
                    if duplicates == 0:
                        print("   ✅ No duplicate exercise names")
                    else:
                        print(f"   ⚠️ {duplicates} duplicate exercise names found")

            return True
        except Exception as e:
            print(f"ℹ️  Exercises table analysis: {e}")
            return False

    def analyze_other_tables(self):
        """Analyze other tables if available"""
        tables_to_check = ["users", "goals", "workouts", "user_profiles"]

        print(f"\n👥 Other Tables Analysis:")
        for table in tables_to_check:
            try:
                count_result = pd.read_sql(
                    f"SELECT COUNT(*) as count FROM {table}", self.engine
                )
                count = count_result["count"].iloc[0]
                print(f"   • {table.title()}: {count} records")
            except:
                print(f"   • {table.title()}: Table not available")

    def run_comprehensive_analysis(self):
        """Run comprehensive database analysis"""
        print("🏋️ WorkoutBuddy Database Analysis & Configuration Test")
        print("=" * 65)

        # Step 1: Load configuration
        config_success = self.load_configuration()

        # Step 2: Test database connection
        if not self.test_database_connection():
            print("\n❌ Cannot proceed without database connection")
            return False

        # Step 3: Analyze schema
        tables = self.analyze_database_schema()

        # Step 4: Analyze specific tables
        if "exercises" in tables:
            self.analyze_exercises_table()
        else:
            print("\nℹ️  Exercises table not found - this is normal for new setups")
            print("   Run database migrations and import data to populate tables")

        # Step 5: Analyze other tables
        if tables:
            self.analyze_other_tables()

        # Step 6: Provide recommendations
        print(f"\n🚀 Next Steps:")
        if not tables:
            print(f"   • Run database migrations: 'alembic upgrade head'")
            print(f"   • Import exercise data: 'python -m app.import_exercises'")
        print(f"   • Run 'uv run python start_jupyter.py' for detailed analysis")
        print(
            f"   • Open workoutbuddy_exploration.ipynb for interactive visualizations"
        )

        print(f"\n✅ Analysis complete!")
        return True


def main():
    """Main analysis runner"""
    analyzer = DatabaseAnalysisTest()
    success = analyzer.run_comprehensive_analysis()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
