#!/usr/bin/env python3
"""
Script to import exercises from exercise_table_ext.csv into the database
"""

import csv
import json
import logging
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.database import Base, SessionLocal, engine
from app.models.exercise import Equipment, Exercise, ExerciseType, MuscleGroup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def map_muscle_group(muscle_str):
    """Map muscle group string to enum value"""
    muscle_mapping = {
        "chest": MuscleGroup.CHEST,
        "back": MuscleGroup.BACK,
        "shoulders": MuscleGroup.SHOULDERS,
        "biceps": MuscleGroup.BICEPS,
        "triceps": MuscleGroup.TRICEPS,
        "legs": MuscleGroup.LEGS,
        "glutes": MuscleGroup.GLUTES,
        "core": MuscleGroup.CORE,
        "cardio": MuscleGroup.CARDIO,
        "full_body": MuscleGroup.FULL_BODY,
        "quadriceps": MuscleGroup.LEGS,
        "hamstrings": MuscleGroup.LEGS,
        "calves": MuscleGroup.LEGS,
        "lats": MuscleGroup.BACK,
        "rhomboids": MuscleGroup.BACK,
        "traps": MuscleGroup.BACK,
        "forearms": MuscleGroup.BICEPS,
        "adductors": MuscleGroup.LEGS,
        "abductors": MuscleGroup.LEGS,
        "hip flexors": MuscleGroup.LEGS,
        "lower back": MuscleGroup.BACK,
        "upper chest": MuscleGroup.CHEST,
        "lower chest": MuscleGroup.CHEST,
        "front delts": MuscleGroup.SHOULDERS,
        "rear delts": MuscleGroup.SHOULDERS,
        "obliques": MuscleGroup.CORE,
        "lower abs": MuscleGroup.CORE,
        "upper abs": MuscleGroup.CORE,
        "grip": MuscleGroup.BICEPS,
        "power": MuscleGroup.FULL_BODY,
        "balance": MuscleGroup.CORE,
        "stability": MuscleGroup.CORE,
        "flexibility": MuscleGroup.CORE,
        "lateral movement": MuscleGroup.LEGS,
        "unilateral strength": MuscleGroup.LEGS,
        "reactive strength": MuscleGroup.LEGS,
        "anti-lateral flexion": MuscleGroup.CORE,
        "anti-extension": MuscleGroup.CORE,
        "serratus": MuscleGroup.CORE,
        "erector spinae": MuscleGroup.BACK,
        "trapezius": MuscleGroup.BACK,
        "brachialis": MuscleGroup.BICEPS,
        "brachioradialis": MuscleGroup.BICEPS,
        "gastrocnemius": MuscleGroup.LEGS,
        "deltoid anterior": MuscleGroup.SHOULDERS,
        "deltoid lateral": MuscleGroup.SHOULDERS,
        "deltoid posterior": MuscleGroup.SHOULDERS,
        "pectoral sternal": MuscleGroup.CHEST,
        "pectoral clavicular": MuscleGroup.CHEST,
        "latissimus dorsi": MuscleGroup.BACK,
        "rectus abdominis": MuscleGroup.CORE,
        "gluteus": MuscleGroup.GLUTES,
        "trapezius upper": MuscleGroup.BACK,
        "trapezius middle": MuscleGroup.BACK,
        "trapezius lower": MuscleGroup.BACK,
    }

    # Clean the muscle string
    muscle_str = muscle_str.lower().strip()

    # Try exact match first
    if muscle_str in muscle_mapping:
        return muscle_mapping[muscle_str]

    # Try partial matches
    for key, value in muscle_mapping.items():
        if key in muscle_str or muscle_str in key:
            return value

    # Default to full body if no match
    logger.warning(f"Unknown muscle group: {muscle_str}, defaulting to FULL_BODY")
    return MuscleGroup.FULL_BODY


def map_equipment(equipment_str):
    """Map equipment string to enum value"""
    equipment_mapping = {
        "none": Equipment.NONE,
        "barbell": Equipment.BARBELL,
        "dumbbell": Equipment.DUMBBELL,
        "dumbbells": Equipment.DUMBBELL,
        "kettlebell": Equipment.KETTLEBELL,
        "machine": Equipment.MACHINE,
        "cable": Equipment.CABLE,
        "cable machine": Equipment.CABLE,
        "bands": Equipment.BANDS,
        "resistance band": Equipment.BANDS,
        "resistance bands": Equipment.BANDS,
        "bodyweight": Equipment.BODYWEIGHT,
        "cardio machine": Equipment.CARDIO_MACHINE,
        "other": Equipment.OTHER,
        "pull-up bar": Equipment.OTHER,
        "dip bars": Equipment.OTHER,
        "bench": Equipment.OTHER,
        "incline bench": Equipment.OTHER,
        "decline bench": Equipment.OTHER,
        "step": Equipment.OTHER,
        "box": Equipment.OTHER,
        "platform": Equipment.OTHER,
        "medicine ball": Equipment.OTHER,
        "stability ball": Equipment.OTHER,
        "preacher bench": Equipment.OTHER,
        "landmine": Equipment.OTHER,
        "t-bar": Equipment.OTHER,
        "squat rack": Equipment.OTHER,
        "hack squat machine": Equipment.MACHINE,
        "smith machine": Equipment.MACHINE,
        "leg press machine": Equipment.MACHINE,
        "leg curl machine": Equipment.MACHINE,
        "leg extension machine": Equipment.MACHINE,
        "calf raise machine": Equipment.MACHINE,
        "assisted pull-up machine": Equipment.MACHINE,
        "assisted dip machine": Equipment.MACHINE,
    }

    # Clean the equipment string
    equipment_str = equipment_str.lower().strip()

    # Try exact match first
    if equipment_str in equipment_mapping:
        return equipment_mapping[equipment_str]

    # Try partial matches
    for key, value in equipment_mapping.items():
        if key in equipment_str or equipment_str in key:
            return value

    # Default to other if no match
    logger.warning(f"Unknown equipment: {equipment_str}, defaulting to OTHER")
    return Equipment.OTHER


def map_exercise_type(exercise_name, description):
    """Map exercise type based on name and description"""
    exercise_name_lower = exercise_name.lower()
    description_lower = description.lower()

    # Cardio exercises
    cardio_keywords = [
        "run",
        "jog",
        "walk",
        "bike",
        "cycle",
        "row",
        "elliptical",
        "treadmill",
        "stationary bike",
        "rowing machine",
    ]
    if any(
        keyword in exercise_name_lower or keyword in description_lower
        for keyword in cardio_keywords
    ):
        return ExerciseType.CARDIO

    # Plyometric exercises
    plyo_keywords = ["jump", "hop", "bound", "explosive", "plyometric"]
    if any(
        keyword in exercise_name_lower or keyword in description_lower
        for keyword in plyo_keywords
    ):
        return ExerciseType.PLYOMETRIC

    # Flexibility exercises
    flex_keywords = ["stretch", "flexibility", "mobility", "yoga"]
    if any(
        keyword in exercise_name_lower or keyword in description_lower
        for keyword in flex_keywords
    ):
        return ExerciseType.FLEXIBILITY

    # Balance exercises
    balance_keywords = ["balance", "stability", "single leg", "one leg"]
    if any(
        keyword in exercise_name_lower or keyword in description_lower
        for keyword in balance_keywords
    ):
        return ExerciseType.BALANCE

    # Default to strength
    return ExerciseType.STRENGTH


def map_difficulty(difficulty_str):
    """Map difficulty string to integer"""
    difficulty_mapping = {
        "beginner": 1,
        "intermediate": 3,
        "advanced": 5,
    }

    difficulty_str = difficulty_str.lower().strip()

    if difficulty_str in difficulty_mapping:
        return difficulty_mapping[difficulty_str]

    # Try to parse as integer
    try:
        return int(difficulty_str)
    except ValueError:
        # Default to intermediate
        logger.warning(f"Unknown difficulty: {difficulty_str}, defaulting to 3")
        return 3


def parse_muscle_list(muscle_str):
    """Parse muscle list from string"""
    if not muscle_str or muscle_str.strip() == "":
        return []

    # Remove brackets and split by comma
    muscle_str = muscle_str.strip("[]")
    muscles = [m.strip() for m in muscle_str.split(",")]

    # Filter out empty strings
    muscles = [m for m in muscles if m]

    return muscles


def parse_equipment_list(equipment_str):
    """Parse equipment list from string"""
    if not equipment_str or equipment_str.strip() == "":
        return []

    # Remove brackets and split by comma
    equipment_str = equipment_str.strip("[]")
    equipment = [e.strip() for e in equipment_str.split(",")]

    # Filter out empty strings
    equipment = [e for e in equipment if e]

    return equipment


def import_exercises():
    """Import exercises from CSV file"""
    # Find the CSV file
    csv_path = Path(__file__).parent.parent.parent / "data" / "exercise_table_ext.csv"

    if not csv_path.exists():
        logger.error(f"CSV file not found at {csv_path}")
        return False

    db = SessionLocal()

    try:
        # Check if exercises already exist
        existing_count = db.query(Exercise).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing exercises. Skipping import.")
            return True

        logger.info(f"Importing exercises from {csv_path}")

        with open(csv_path, encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            imported_count = 0
            for row in csv_reader:
                try:
                    # Parse muscle groups
                    primary_muscles = parse_muscle_list(
                        row.get("Main Muscle Group [List]", "")
                    )
                    primary_muscle = (
                        map_muscle_group(primary_muscles[0])
                        if primary_muscles
                        else MuscleGroup.FULL_BODY
                    )

                    # Parse secondary muscles (all except primary)
                    secondary_muscles = (
                        primary_muscles[1:] if len(primary_muscles) > 1 else []
                    )

                    # Parse equipment
                    equipment_list = parse_equipment_list(
                        row.get("Equipment Required [List]", "")
                    )
                    equipment = (
                        map_equipment(equipment_list[0])
                        if equipment_list
                        else Equipment.NONE
                    )

                    # Map exercise type
                    exercise_type = map_exercise_type(
                        row.get("Exercise Name", ""), row.get("Short Description", "")
                    )

                    # Map difficulty
                    difficulty = map_difficulty(
                        row.get("Difficulty Level", "Intermediate")
                    )

                    # Determine if distance/time based
                    is_distance_based = (
                        "distance" in row.get("Short Description", "").lower()
                    )
                    is_time_based = "time" in row.get("Short Description", "").lower()

                    # Estimate METs based on exercise type and difficulty
                    base_mets = {
                        ExerciseType.STRENGTH: 4.0,
                        ExerciseType.CARDIO: 8.0,
                        ExerciseType.FLEXIBILITY: 2.5,
                        ExerciseType.BALANCE: 3.0,
                        ExerciseType.PLYOMETRIC: 6.0,
                    }
                    mets = base_mets.get(exercise_type, 4.0) * (difficulty / 3.0)

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

                    db.add(exercise)
                    imported_count += 1

                    if imported_count % 10 == 0:
                        logger.info(f"Imported {imported_count} exercises...")

                except Exception as e:
                    logger.error(
                        f"Error importing exercise {row.get('Exercise Name', 'Unknown')}: {e}"
                    )
                    continue

            db.commit()
            logger.info(f"Successfully imported {imported_count} exercises")
            return True

    except Exception as e:
        logger.error(f"Error importing exercises: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main function"""
    logger.info("Starting exercise import...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Import exercises
    success = import_exercises()

    if success:
        logger.info("Exercise import completed successfully")
    else:
        logger.error("Exercise import failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
