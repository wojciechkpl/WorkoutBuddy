# backend/app/services/workout_service.py
"""
Workout service utilities
"""

import csv
import logging
import os
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import Exercise, User, UserStats, Workout, WorkoutExercise

logger = logging.getLogger(__name__)


class WorkoutService:
    """Service for workout-related operations"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_workout_metrics(self, workout: Workout):
        """Calculate and update workout metrics"""
        if not workout.started_at or not workout.completed_at:
            return

        # Calculate duration
        duration = (workout.completed_at - workout.started_at).total_seconds() / 60
        workout.total_duration = int(duration)

        # Calculate total volume and calories
        total_volume = 0
        total_calories = 0
        total_distance = 0

        for we in workout.exercises:
            exercise = we.exercise

            # Volume for strength exercises
            if we.actual_weight and we.actual_reps:
                weights = [float(w) for w in we.actual_weight.split(",") if w]
                reps = [int(r) for r in we.actual_reps.split(",") if r]

                if weights and reps:
                    # Calculate volume per set and sum
                    for i in range(min(len(weights), len(reps))):
                        total_volume += weights[i] * reps[i]

            # Calories calculation
            if exercise.mets and we.duration:
                # MET formula: calories = METs * weight_kg * hours
                calories = (
                    exercise.mets * (workout.user.weight or 70) * (we.duration / 60)
                )
                total_calories += calories
            elif we.sets and we.actual_reps:
                # Rough estimate for strength training
                total_reps = sum([int(r) for r in we.actual_reps.split(",") if r])
                calories = total_reps * 0.5 * (exercise.difficulty or 3)
                total_calories += calories

            # Distance for cardio
            if we.distance:
                total_distance += we.distance

        workout.total_volume = total_volume
        workout.calories_burned = total_calories
        workout.total_distance = total_distance

    def update_user_stats(self, user: User, workout: Workout):
        """Update user statistics after workout completion"""
        # Get or create today's stats
        today = datetime.utcnow().date()
        stats = (
            self.db.query(UserStats)
            .filter(UserStats.user_id == user.id, func.date(UserStats.date) == today)
            .first()
        )

        if not stats:
            stats = UserStats(user_id=user.id, date=datetime.utcnow())
            self.db.add(stats)

        # Update stats
        stats.total_workouts += 1
        stats.total_weight_lifted += workout.total_volume or 0
        stats.total_cardio_distance += workout.total_distance or 0
        stats.total_calories_burned += workout.calories_burned or 0

        # Update personal records
        self._update_personal_records(stats, workout)

    def _update_personal_records(self, stats: UserStats, workout: Workout):
        """Update personal records from workout"""
        import json

        prs = json.loads(stats.personal_records) if stats.personal_records else {}

        for we in workout.exercises:
            exercise_name = we.exercise.name

            # Check for weight PR
            if we.actual_weight:
                weights = [float(w) for w in we.actual_weight.split(",") if w]
                if weights:
                    max_weight = max(weights)
                    current_pr = prs.get(f"{exercise_name}_weight", 0)
                    if max_weight > current_pr:
                        prs[f"{exercise_name}_weight"] = max_weight

            # Check for reps PR
            if we.actual_reps:
                reps = [int(r) for r in we.actual_reps.split(",") if r]
                if reps:
                    max_reps = max(reps)
                    current_pr = prs.get(f"{exercise_name}_reps", 0)
                    if max_reps > current_pr:
                        prs[f"{exercise_name}_reps"] = max_reps

        stats.personal_records = json.dumps(prs)

    def get_user_stats(self, user: User, days: int) -> dict:
        """Get comprehensive user statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get workouts in date range
        workouts = (
            self.db.query(Workout)
            .filter(Workout.user_id == user.id, Workout.completed_at >= cutoff_date)
            .all()
        )

        completed_workouts = [w for w in workouts if w.status == "completed"]

        # Calculate stats
        total_duration = sum(w.total_duration or 0 for w in completed_workouts)
        total_calories = sum(w.calories_burned or 0 for w in completed_workouts)
        total_volume = sum(w.total_volume or 0 for w in completed_workouts)
        total_distance = sum(w.total_distance or 0 for w in completed_workouts)

        # Get favorite exercises
        exercise_counts = (
            self.db.query(
                Exercise.name,
                Exercise.primary_muscle,
                func.count(WorkoutExercise.id).label("count"),
            )
            .select_from(WorkoutExercise)
            .join(Exercise)
            .join(Workout)
            .filter(Workout.user_id == user.id, Workout.completed_at >= cutoff_date)
            .group_by(Exercise.id)
            .order_by(func.count(WorkoutExercise.id).desc())
            .limit(5)
            .all()
        )

        favorite_exercises = [
            {"name": name, "muscle_group": muscle.value, "count": count}
            for name, muscle, count in exercise_counts
        ]

        # Calculate muscle group distribution
        muscle_distribution = (
            self.db.query(
                Exercise.primary_muscle, func.count(WorkoutExercise.id).label("count")
            )
            .select_from(WorkoutExercise)
            .join(Exercise)
            .join(Workout)
            .filter(Workout.user_id == user.id, Workout.completed_at >= cutoff_date)
            .group_by(Exercise.primary_muscle)
            .all()
        )

        muscle_group_distribution = {
            muscle.value: count for muscle, count in muscle_distribution
        }

        return {
            "total_workouts": len(workouts),
            "completed_workouts": len(completed_workouts),
            "total_duration": total_duration,
            "total_calories": total_calories,
            "total_volume": total_volume,
            "total_distance": total_distance,
            "favorite_exercises": favorite_exercises,
            "muscle_group_distribution": muscle_group_distribution,
        }


def import_exercise_database():
    """Import exercises from CSV file"""
    csv_path = os.path.join(settings.DATA_PATH, "exercises.csv")

    if not os.path.exists(csv_path):
        logger.warning(f"Exercise CSV not found at {csv_path}")
        return

    db = SessionLocal()

    try:
        # Check if exercises already exist
        if db.query(Exercise).count() > 0:
            logger.info("Exercises already imported")
            return

        with open(csv_path, encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                exercise = Exercise(
                    name=row.get("name", ""),
                    description=row.get("description", ""),
                    primary_muscle=row.get("primary_muscle", "full_body"),
                    secondary_muscles=row.get("secondary_muscles", ""),
                    equipment=row.get("equipment", "none"),
                    exercise_type=row.get("exercise_type", "strength"),
                    difficulty=int(row.get("difficulty", 3)),
                    instructions=row.get("instructions", ""),
                    tips=row.get("tips", ""),
                    video_url=row.get("video_url", ""),
                    is_distance_based=row.get("is_distance_based", "").lower()
                    == "true",
                    is_time_based=row.get("is_time_based", "").lower() == "true",
                    mets=float(row.get("mets", 4.0)),
                )
                db.add(exercise)

            db.commit()
            logger.info("Exercises imported successfully")

    except Exception as e:
        logger.error(f"Error importing exercises: {e}")
        db.rollback()
    finally:
        db.close()
