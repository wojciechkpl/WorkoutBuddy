class Exercise {
  final int id;
  final String name;
  final String description;
  final String primaryMuscle;
  final List<String> muscleGroups;
  final String equipment;
  final bool equipmentRequired;
  final int difficultyLevel;
  final String exerciseType;
  final double? mets;

  Exercise({
    required this.id,
    required this.name,
    required this.description,
    required this.primaryMuscle,
    required this.muscleGroups,
    required this.equipment,
    required this.equipmentRequired,
    required this.difficultyLevel,
    required this.exerciseType,
    this.mets,
  });

  factory Exercise.fromJson(Map<String, dynamic> json) {
    return Exercise(
      id: json['id'],
      name: json['name'],
      description: json['description'] ?? '',
      primaryMuscle: json['primary_muscle'] ?? '',
      muscleGroups: json['muscle_groups'] != null
          ? (json['muscle_groups'] as String).split(',').map((e) => e.trim()).toList()
          : [],
      equipment: json['equipment'] ?? '',
      equipmentRequired: json['equipment_required'] ?? false,
      difficultyLevel: json['difficulty_level'] ?? 1,
      exerciseType: json['exercise_type'] ?? 'strength',
      mets: json['mets']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'primary_muscle': primaryMuscle,
      'muscle_groups': muscleGroups.join(', '),
      'equipment': equipment,
      'equipment_required': equipmentRequired,
      'difficulty_level': difficultyLevel,
      'exercise_type': exerciseType,
      'mets': mets,
    };
  }
}
