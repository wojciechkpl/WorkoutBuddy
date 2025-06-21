// mobile/lib/models/exercise.dart
class Exercise {
  final int id;
  final String name;
  final String? description;
  final String primaryMuscle;
  final List<String>? secondaryMuscles;
  final String equipment;
  final String exerciseType;
  final int difficulty;
  final String? instructions;
  final String? tips;
  final String? videoUrl;
  final bool isDistanceBased;
  final bool isTimeBased;
  final double mets;

  Exercise({
    required this.id,
    required this.name,
    this.description,
    required this.primaryMuscle,
    this.secondaryMuscles,
    required this.equipment,
    required this.exerciseType,
    required this.difficulty,
    this.instructions,
    this.tips,
    this.videoUrl,
    required this.isDistanceBased,
    required this.isTimeBased,
    required this.mets,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      primaryMuscle: json['primary_muscle'],
      secondaryMuscles: json['secondary_muscles'] != null
          ? List<String>.from(json['secondary_muscles'])
          : null,
      equipment: json['equipment'],
      exerciseType: json['exercise_type'],
      difficulty: json['difficulty'],
      instructions: json['instructions'],
      tips: json['tips'],
      videoUrl: json['video_url'],
      isDistanceBased: json['is_distance_based'],
      isTimeBased: json['is_time_based'],
      mets: json['mets'].toDouble(),
    );
  }
}
