#!/usr/bin/env python3
"""
Exercise data import script for Pulse Fitness application.

This script imports exercise data from CSV files into the database
with proper mapping and validation.
"""

import csv
import json
import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.database import SessionLocal
from app.models.exercise import Equipment, Exercise, ExerciseType, MuscleGroup

from .config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ExerciseImportError(Exception):
    """Custom exception for exercise import errors."""

    pass


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class ExerciseMapper:
    """Maps CSV data to Exercise model fields."""

    @staticmethod
    def map_muscle_group(muscle_str: str) -> MuscleGroup:
        """Map muscle group string to enum value."""
        if not muscle_str:
            return MuscleGroup.FULL_BODY

        muscle_str = muscle_str.lower().strip()

        # Get mapped value from config
        mapped_value = config.muscle_group_mapping.get(muscle_str)
        if mapped_value:
            try:
                return MuscleGroup(mapped_value)
            except ValueError:
                pass

        # Try partial matches
        for key, value in config.muscle_group_mapping.items():
            if key in muscle_str or muscle_str in key:
                try:
                    return MuscleGroup(value)
                except ValueError:
                    continue

        logger.warning(f"Unknown muscle group: {muscle_str}, defaulting to FULL_BODY")
        return MuscleGroup.FULL_BODY

    @staticmethod
    def map_equipment(equipment_str: str) -> Equipment:
        """Map equipment string to enum value."""
        if not equipment_str:
            return Equipment.NONE

        equipment_str = equipment_str.lower().strip()

        # Get mapped value from config
        mapped_value = config.equipment_mapping.get(equipment_str)
        if mapped_value:
            try:
                return Equipment(mapped_value)
            except ValueError:
                pass

        # Try partial matches
        for key, value in config.equipment_mapping.items():
            if key in equipment_str or equipment_str in key:
                try:
                    return Equipment(value)
                except ValueError:
                    continue

        logger.warning(f"Unknown equipment: {equipment_str}, defaulting to OTHER")
        return Equipment.OTHER

    @staticmethod
    def map_exercise_type(exercise_name: str, description: str) -> ExerciseType:
        """Map exercise type based on name and description."""
        exercise_name_lower = exercise_name.lower()
        description_lower = description.lower()

        # Check each exercise type
        for exercise_type_str, keywords in config.exercise_type_keywords.items():
            if any(
                keyword in exercise_name_lower or keyword in description_lower
                for keyword in keywords
            ):
                try:
                    return ExerciseType(exercise_type_str)
                except ValueError:
                    continue

        # Default to strength
        return ExerciseType.STRENGTH

    @staticmethod
    def map_difficulty(difficulty_str: str) -> int:
        """Map difficulty string to integer."""
        if not difficulty_str:
            return 3

        difficulty_str = difficulty_str.lower().strip()

        if difficulty_str in config.difficulty_mapping:
            return config.difficulty_mapping[difficulty_str]

        # Try to parse as integer
        try:
            return int(difficulty_str)
        except ValueError:
            logger.warning(f"Unknown difficulty: {difficulty_str}, defaulting to 3")
            return 3

    @staticmethod
    def parse_list_string(list_str: str) -> list[str]:
        """Parse list from string format like '[item1, item2]'."""
        if not list_str or list_str.strip() == "":
            return []

        # Remove brackets and split by comma
        list_str = list_str.strip("[]")
        items = [item.strip() for item in list_str.split(",")]

        # Filter out empty strings
        return [item for item in items if item]

    @staticmethod
    def calculate_mets(exercise_type: ExerciseType, difficulty: int) -> float:
        """Calculate METs based on exercise type and difficulty."""
        base = config.base_mets.get(exercise_type.value, 4.0)
        return base * (difficulty / 3.0)


class ExerciseValidator:
    """Validates exercise data before import."""

    @staticmethod
    def validate_exercise_data(row: dict[str, str]) -> tuple[bool, list[str]]:
        """Validate exercise data from CSV row."""
        errors = []

        # Check required fields
        if not row.get("Exercise Name", "").strip():
            errors.append("Exercise name is required")

        if not row.get("Short Description", "").strip():
            errors.append("Short description is required")

        # Check field lengths
        if len(row.get("Exercise Name", "")) > 100:
            errors.append("Exercise name too long (max 100 characters)")

        # Check difficulty level
        difficulty = row.get("Difficulty Level", "").lower().strip()
        if difficulty and difficulty not in config.difficulty_mapping:
            try:
                int(difficulty)
            except ValueError:
                errors.append("Invalid difficulty level")

        return len(errors) == 0, errors


class ExerciseImporter:
    """Handles the import of exercise data from CSV files."""

    def __init__(self, csv_path: Optional[Path] = None, force_import: bool = False):
        self.csv_path = csv_path or (config.data_dir / config.exercise_csv)
        self.force_import = force_import
        self.mapper = ExerciseMapper()
        self.validator = ExerciseValidator()

    def validate_csv_file(self) -> bool:
        """Validate that the CSV file exists and is readable."""
        if not self.csv_path.exists():
            logger.error(f"CSV file not found at {self.csv_path}")
            return False

        if not self.csv_path.is_file():
            logger.error(f"Path is not a file: {self.csv_path}")
            return False

        return True

    def check_existing_exercises(self) -> int:
        """Check how many exercises already exist in the database."""
        with get_db_session() as session:
            return session.query(Exercise).count()

    def process_csv_row(self, row: dict[str, str]) -> Optional[Exercise]:
        """Process a single CSV row and return an Exercise object."""
        try:
            # Validate data
            if config.validate_data:
                is_valid, errors = self.validator.validate_exercise_data(row)
                if not is_valid:
                    logger.warning(
                        f"Validation errors for {row.get('Exercise Name', 'Unknown')}: {errors}"
                    )
                    return None

            # Parse muscle groups
            primary_muscles = self.mapper.parse_list_string(
                row.get("Main Muscle Group [List]", "")
            )
            primary_muscle = (
                self.mapper.map_muscle_group(primary_muscles[0])
                if primary_muscles
                else MuscleGroup.FULL_BODY
            )

            # Parse secondary muscles (all except primary)
            secondary_muscles = primary_muscles[1:] if len(primary_muscles) > 1 else []

            # Parse equipment
            equipment_list = self.mapper.parse_list_string(
                row.get("Equipment Required [List]", "")
            )
            equipment = (
                self.mapper.map_equipment(equipment_list[0])
                if equipment_list
                else Equipment.NONE
            )

            # Map exercise type
            exercise_type = self.mapper.map_exercise_type(
                row.get("Exercise Name", ""), row.get("Short Description", "")
            )

            # Map difficulty
            difficulty = self.mapper.map_difficulty(
                row.get("Difficulty Level", "Intermediate")
            )

            # Determine if distance/time based
            description_lower = row.get("Short Description", "").lower()
            is_distance_based = "distance" in description_lower
            is_time_based = "time" in description_lower

            # Calculate METs
            mets = self.mapper.calculate_mets(exercise_type, difficulty)

            # Create exercise object
            exercise = Exercise(
                name=row.get("Exercise Name", "").strip(),
                description=row.get("Short Description", "").strip(),
                primary_muscle=primary_muscle,
                secondary_muscles=json.dumps(secondary_muscles),
                equipment=equipment,
                exercise_type=exercise_type,
                difficulty=difficulty,
                instructions=row.get("Key Form Cues", "").strip(),
                tips="",  # Could be derived from form cues
                video_url=row.get("Visual Reference", "").strip(),
                is_distance_based=is_distance_based,
                is_time_based=is_time_based,
                mets=mets,
            )

            return exercise

        except Exception as e:
            logger.error(
                f"Error processing exercise {row.get('Exercise Name', 'Unknown')}: {e}"
            )
            return None

    def import_exercises(self) -> tuple[int, int]:
        """Import exercises from CSV file."""
        if not self.validate_csv_file():
            raise ExerciseImportError("CSV file validation failed")

        # Check existing exercises
        existing_count = self.check_existing_exercises()
        if existing_count > 0 and config.skip_existing and not self.force_import:
            logger.info(f"Found {existing_count} existing exercises. Skipping import.")
            return existing_count, 0

        logger.info(f"Importing exercises from {self.csv_path}")

        imported_count = 0
        error_count = 0

        with get_db_session() as session:
            try:
                with open(self.csv_path, encoding="utf-8") as file:
                    csv_reader = csv.DictReader(file)

                    for row in csv_reader:
                        exercise = self.process_csv_row(row)

                        if exercise:
                            session.add(exercise)
                            imported_count += 1

                            # Commit in batches
                            if imported_count % config.batch_size == 0:
                                session.commit()
                                logger.info(f"Imported {imported_count} exercises...")
                        else:
                            error_count += 1

                    # Commit remaining exercises
                    if imported_count % config.batch_size != 0:
                        session.commit()

                logger.info(f"Successfully imported {imported_count} exercises")
                if error_count > 0:
                    logger.warning(f"Failed to import {error_count} exercises")

                return imported_count, error_count

            except Exception as e:
                logger.error(f"Error during import: {e}")
                session.rollback()
                raise ExerciseImportError(f"Import failed: {e}")


def main(csv_path: Optional[str] = None, force_import: bool = False) -> None:
    """Main function to import exercises."""
    logger.info("Starting exercise import...")

    try:
        # Create importer and run import
        importer = ExerciseImporter(
            csv_path=Path(csv_path) if csv_path else None, force_import=force_import
        )
        imported_count, error_count = importer.import_exercises()

        logger.info(
            f"Import completed: {imported_count} imported, {error_count} errors"
        )

    except ExerciseImportError as e:
        logger.error(f"Exercise import error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import exercises from CSV")
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Path to CSV file (default: data/exercise_table_ext.csv)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force import even if exercises already exist",
    )

    args = parser.parse_args()
    main(csv_path=args.csv_path, force_import=args.force)
