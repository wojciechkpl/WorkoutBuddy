// mobile/lib/models/workout.dart
import 'exercise.dart';

class Workout {
  final int id;
  final String name;
  final String description;
  final String status;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final int? totalDuration;
  final double? totalVolume;
  final double? caloriesBurned;
  final double? totalDistance;
  final List<WorkoutExercise> exercises;
  final DateTime createdAt;
  final DateTime updatedAt;

  Workout({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    this.startedAt,
    this.completedAt,
    this.totalDuration,
    this.totalVolume,
    this.caloriesBurned,
    this.totalDistance,
    required this.exercises,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Workout.fromJson(Map<String, dynamic> json) {
    return Workout(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      status: json['status'] ?? 'planned',
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'])
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
      totalDuration: json['total_duration'],
      totalVolume: json['total_volume']?.toDouble(),
      caloriesBurned: json['calories_burned']?.toDouble(),
      totalDistance: json['total_distance']?.toDouble(),
      exercises: json['exercises'] != null
          ? (json['exercises'] as List)
              .map((e) => WorkoutExercise.fromJson(e))
              .toList()
          : [],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'status': status,
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'total_duration': totalDuration,
      'total_volume': totalVolume,
      'calories_burned': caloriesBurned,
      'total_distance': totalDistance,
      'exercises': exercises.map((e) => e.toJson()).toList(),
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class WorkoutExercise {
  final int id;
  final Exercise exercise;
  final int order;
  final int? sets;
  final String? reps;
  final String? weight;
  final int? duration;
  final double? distance;
  final double? speed;
  final double? incline;
  final int? restTime;
  final String? actualReps;
  final String? actualWeight;
  final String? notes;

  WorkoutExercise({
    required this.id,
    required this.exercise,
    required this.order,
    this.sets,
    this.reps,
    this.weight,
    this.duration,
    this.distance,
    this.speed,
    this.incline,
    this.restTime,
    this.actualReps,
    this.actualWeight,
    this.notes,
  });

  factory WorkoutExercise.fromJson(Map<String, dynamic> json) {
    return WorkoutExercise(
      id: json['id'],
      exercise: Exercise.fromJson(json['exercise']),
      order: json['order'],
      sets: json['sets'],
      reps: json['reps'],
      weight: json['weight'],
      duration: json['duration'],
      distance: json['distance']?.toDouble(),
      speed: json['speed']?.toDouble(),
      incline: json['incline']?.toDouble(),
      restTime: json['rest_time'],
      actualReps: json['actual_reps'],
      actualWeight: json['actual_weight'],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'exercise': exercise.toJson(),
      'order': order,
      'sets': sets,
      'reps': reps,
      'weight': weight,
      'duration': duration,
      'distance': distance,
      'speed': speed,
      'incline': incline,
      'rest_time': restTime,
      'actual_reps': actualReps,
      'actual_weight': actualWeight,
      'notes': notes,
    };
  }
}
