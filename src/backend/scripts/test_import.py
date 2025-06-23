#!/usr/bin/env python3
"""
Test script for the refactored exercise importer.
"""

import logging
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from app.models.exercise import Equipment, MuscleGroup

from .config import config
from .exercise_importer import ExerciseImporter, ExerciseMapper, ExerciseValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mapper():
    """Test the ExerciseMapper class."""
    logger.info("Testing ExerciseMapper...")

    mapper = ExerciseMapper()

    # Test muscle group mapping
    assert mapper.map_muscle_group("chest") == MuscleGroup.CHEST
    assert mapper.map_muscle_group("quadriceps") == MuscleGroup.LEGS
    assert mapper.map_muscle_group("unknown") == MuscleGroup.FULL_BODY

    # Test equipment mapping
    assert mapper.map_equipment("barbell") == Equipment.BARBELL
    assert mapper.map_equipment("dumbbells") == Equipment.DUMBBELL
    assert mapper.map_equipment("unknown") == Equipment.OTHER

    # Test difficulty mapping
    assert mapper.map_difficulty("beginner") == 1
    assert mapper.map_difficulty("intermediate") == 3
    assert mapper.map_difficulty("advanced") == 5
    assert mapper.map_difficulty("2") == 2

    # Test list parsing
    assert mapper.parse_list_string("[chest, triceps]") == ["chest", "triceps"]
    assert mapper.parse_list_string("") == []

    logger.info("ExerciseMapper tests passed!")


def test_validator():
    """Test the ExerciseValidator class."""
    logger.info("Testing ExerciseValidator...")

    validator = ExerciseValidator()

    # Test valid data
    valid_row = {
        "Exercise Name": "Push-ups",
        "Short Description": "Classic bodyweight exercise",
        "Difficulty Level": "beginner",
    }
    is_valid, errors = validator.validate_exercise_data(valid_row)
    assert is_valid
    assert len(errors) == 0

    # Test invalid data
    invalid_row = {
        "Exercise Name": "",
        "Short Description": "",
        "Difficulty Level": "invalid",
    }
    is_valid, errors = validator.validate_exercise_data(invalid_row)
    assert not is_valid
    assert len(errors) > 0

    logger.info("ExerciseValidator tests passed!")


def test_importer_creation():
    """Test creating the ExerciseImporter."""
    logger.info("Testing ExerciseImporter creation...")

    # Test with default path
    importer = ExerciseImporter()
    assert importer.csv_path == config.data_dir / config.exercise_csv
    assert not importer.force_import

    # Test with custom path
    custom_path = Path("/tmp/test.csv")
    importer = ExerciseImporter(csv_path=custom_path, force_import=True)
    assert importer.csv_path == custom_path
    assert importer.force_import

    logger.info("ExerciseImporter creation tests passed!")


def main():
    """Run all tests."""
    logger.info("Running tests for refactored exercise importer...")

    try:
        test_mapper()
        test_validator()
        test_importer_creation()

        logger.info("All tests passed!")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
