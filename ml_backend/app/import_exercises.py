#!/usr/bin/env python3

import os
import sys
import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import config directly
from config import backend_config

# Create engine and base directly
DATABASE_URL = backend_config.database.url
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# Define Exercise model directly
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    main_muscle_group = Column(String)
    equipment = Column(String)
    difficulty = Column(String)
    form_cues = Column(String)
    visual_reference = Column(String)


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_csv_file(file_path):
    """Parse the CSV file and extract exercise data"""
    exercises = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row_num, row in enumerate(
                csv_reader, start=2
            ):  # Start at 2 because of header
                try:
                    # Skip section headers and empty rows
                    exercise_name = row.get("Exercise Name", "").strip()
                    if (
                        not exercise_name
                        or exercise_name.startswith("**")
                        or exercise_name == ""
                    ):
                        continue

                    exercise = {
                        "name": exercise_name,
                        "description": row.get("Short Description", "").strip(),
                        "main_muscle_group": row.get("Main Muscle Group", "").strip(),
                        "equipment": row.get("Equipment Required", "").strip(),
                        "difficulty": row.get("Difficulty Level", "").strip(),
                        "form_cues": row.get("Key Form Cues", "").strip(),
                        "visual_reference": row.get("Visual Reference", "").strip(),
                    }

                    # Skip empty rows
                    if exercise["name"] and exercise["name"] != "-":
                        exercises.append(exercise)

                except Exception as e:
                    logger.warning(f"Error parsing row {row_num}: {e}")
                    continue

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []

    return exercises


def import_exercises():
    """Import exercises from CSV file into database"""

    # Find the CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(current_dir, "../../data/exercise_table_ext.csv")

    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        return False

    logger.info(f"Reading exercises from: {csv_file}")

    # Parse the CSV file
    exercises_data = parse_csv_file(csv_file)

    if not exercises_data:
        logger.error("No exercises found in CSV file")
        return False

    logger.info(f"Found {len(exercises_data)} exercises to import")

    # Create database session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        # Try to clear existing exercises (graceful handling of permissions)
        try:
            existing_count = session.query(Exercise).count()
            if existing_count > 0:
                session.query(Exercise).delete()
                logger.info(f"Cleared {existing_count} existing exercises")
            else:
                logger.info("No existing exercises to clear")
        except Exception as permission_error:
            logger.warning(
                f"Could not clear existing exercises (permission issue): {permission_error}"
            )
            logger.info("Will attempt to insert new exercises only...")

        # Import new exercises
        imported_count = 0
        skipped_count = 0

        for exercise_data in exercises_data:
            try:
                # Check if exercise already exists (by name)
                existing = (
                    session.query(Exercise)
                    .filter(Exercise.name == exercise_data["name"])
                    .first()
                )
                if existing:
                    skipped_count += 1
                    continue

                exercise = Exercise(
                    name=exercise_data["name"],
                    description=exercise_data["description"],
                    main_muscle_group=exercise_data["main_muscle_group"],
                    equipment=exercise_data["equipment"],
                    difficulty=exercise_data["difficulty"],
                    form_cues=exercise_data["form_cues"],
                    visual_reference=exercise_data["visual_reference"],
                )
                session.add(exercise)
                imported_count += 1

            except Exception as e:
                logger.warning(
                    f"Error importing exercise '{exercise_data['name']}': {e}"
                )
                continue

        # Commit all changes
        session.commit()

        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} duplicate exercises")
        logger.info(f"Successfully imported {imported_count} new exercises")

        # Final count
        total_exercises = session.query(Exercise).count()
        logger.info(f"Total exercises in database: {total_exercises}")

        return True

    except Exception as e:
        logger.error(f"Database error: {e}")
        session.rollback()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    success = import_exercises()
    if success:
        logger.info("Exercise import completed successfully!")
        sys.exit(0)
    else:
        logger.error("Exercise import failed!")
        sys.exit(1)
