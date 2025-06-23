"""
Configuration settings for database scripts.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScriptConfig:
    """Configuration for database scripts."""

    # Database settings
    batch_size: int = 50
    max_retries: int = 3
    retry_delay: float = 1.0

    # Import settings
    skip_existing: bool = True
    validate_data: bool = True
    log_level: str = "INFO"

    # File paths
    data_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent / "data"
    )
    exercise_csv: str = "exercise_table_ext.csv"

    # Mapping configurations
    muscle_group_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "chest": "chest",
            "back": "back",
            "shoulders": "shoulders",
            "biceps": "biceps",
            "triceps": "triceps",
            "legs": "legs",
            "glutes": "glutes",
            "core": "core",
            "cardio": "cardio",
            "full_body": "full_body",
            "quadriceps": "legs",
            "hamstrings": "legs",
            "calves": "legs",
            "lats": "back",
            "rhomboids": "back",
            "traps": "back",
            "forearms": "biceps",
            "adductors": "legs",
            "abductors": "legs",
            "hip flexors": "legs",
            "lower back": "back",
            "upper chest": "chest",
            "lower chest": "chest",
            "front delts": "shoulders",
            "rear delts": "shoulders",
            "obliques": "core",
            "lower abs": "core",
            "upper abs": "core",
            "grip": "biceps",
            "power": "full_body",
            "balance": "core",
            "stability": "core",
            "flexibility": "core",
            "lateral movement": "legs",
            "unilateral strength": "legs",
            "reactive strength": "legs",
            "anti-lateral flexion": "core",
            "anti-extension": "core",
            "serratus": "core",
            "erector spinae": "back",
            "trapezius": "back",
            "brachialis": "biceps",
            "brachioradialis": "biceps",
            "gastrocnemius": "legs",
            "deltoid anterior": "shoulders",
            "deltoid lateral": "shoulders",
            "deltoid posterior": "shoulders",
            "pectoral sternal": "chest",
            "pectoral clavicular": "chest",
            "latissimus dorsi": "back",
            "rectus abdominis": "core",
            "gluteus": "glutes",
            "trapezius upper": "back",
            "trapezius middle": "back",
            "trapezius lower": "back",
        }
    )

    equipment_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "none": "none",
            "barbell": "barbell",
            "dumbbell": "dumbbell",
            "dumbbells": "dumbbell",
            "kettlebell": "kettlebell",
            "machine": "machine",
            "cable": "cable",
            "cable machine": "cable",
            "bands": "bands",
            "resistance band": "bands",
            "resistance bands": "bands",
            "bodyweight": "bodyweight",
            "cardio machine": "cardio_machine",
            "other": "other",
            "pull-up bar": "other",
            "dip bars": "other",
            "bench": "other",
            "incline bench": "other",
            "decline bench": "other",
            "step": "other",
            "box": "other",
            "platform": "other",
            "medicine ball": "other",
            "stability ball": "other",
            "preacher bench": "other",
            "landmine": "other",
            "t-bar": "other",
            "squat rack": "other",
            "hack squat machine": "machine",
            "smith machine": "machine",
            "leg press machine": "machine",
            "leg curl machine": "machine",
            "leg extension machine": "machine",
            "calf raise machine": "machine",
            "assisted pull-up machine": "machine",
            "assisted dip machine": "machine",
        }
    )

    difficulty_mapping: dict[str, int] = field(
        default_factory=lambda: {
            "beginner": 1,
            "intermediate": 3,
            "advanced": 5,
        }
    )

    exercise_type_keywords: dict[str, list] = field(
        default_factory=lambda: {
            "cardio": [
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
            ],
            "plyometric": ["jump", "hop", "bound", "explosive", "plyometric"],
            "flexibility": ["stretch", "flexibility", "mobility", "yoga"],
            "balance": ["balance", "stability", "single leg", "one leg"],
        }
    )

    base_mets: dict[str, float] = field(
        default_factory=lambda: {
            "strength": 4.0,
            "cardio": 8.0,
            "flexibility": 2.5,
            "balance": 3.0,
            "plyometric": 6.0,
        }
    )


# Global configuration instance
config = ScriptConfig()
