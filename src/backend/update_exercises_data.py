#!/usr/bin/env python3
"""
Script to update existing exercises with required fields before migration
"""

from app.database import get_db
from app.models.exercise import Exercise, MuscleGroup, Equipment, ExerciseType

def update_exercises_data():
    """Update existing exercises with required fields"""
    db = next(get_db())
    
    try:
        # Update existing exercises with required fields
        exercises_data = [
            {
                'name': 'Push-ups',
                'primary_muscle': MuscleGroup.CHEST,
                'equipment': Equipment.BODYWEIGHT,
                'exercise_type': ExerciseType.STRENGTH,
                'difficulty': 1,
                'is_distance_based': False,
                'is_time_based': False,
                'mets': 4.0
            },
            {
                'name': 'Squats',
                'primary_muscle': MuscleGroup.LEGS,
                'equipment': Equipment.BODYWEIGHT,
                'exercise_type': ExerciseType.STRENGTH,
                'difficulty': 1,
                'is_distance_based': False,
                'is_time_based': False,
                'mets': 5.0
            },
            {
                'name': 'Pull-ups',
                'primary_muscle': MuscleGroup.BACK,
                'equipment': Equipment.BODYWEIGHT,
                'exercise_type': ExerciseType.STRENGTH,
                'difficulty': 3,
                'is_distance_based': False,
                'is_time_based': False,
                'mets': 6.0
            },
            {
                'name': 'Deadlift',
                'primary_muscle': MuscleGroup.BACK,
                'equipment': Equipment.BARBELL,
                'exercise_type': ExerciseType.STRENGTH,
                'difficulty': 3,
                'is_distance_based': False,
                'is_time_based': False,
                'mets': 3.0
            },
            {
                'name': 'Bench Press',
                'primary_muscle': MuscleGroup.CHEST,
                'equipment': Equipment.BARBELL,
                'exercise_type': ExerciseType.STRENGTH,
                'difficulty': 2,
                'is_distance_based': False,
                'is_time_based': False,
                'mets': 3.0
            }
        ]
        
        for exercise_data in exercises_data:
            exercise = db.query(Exercise).filter(Exercise.name == exercise_data['name']).first()
            if exercise:
                exercise.primary_muscle = exercise_data['primary_muscle']
                exercise.equipment = exercise_data['equipment']
                exercise.exercise_type = exercise_data['exercise_type']
                exercise.difficulty = exercise_data['difficulty']
                exercise.is_distance_based = exercise_data['is_distance_based']
                exercise.is_time_based = exercise_data['is_time_based']
                exercise.mets = exercise_data['mets']
                print(f"Updated exercise: {exercise.name}")
        
        db.commit()
        print("All exercises updated successfully!")
        
    except Exception as e:
        print(f"Error updating exercises: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_exercises_data() 