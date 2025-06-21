// mobile/lib/models/user.dart
class User {
  final int id;
  final String email;
  final String username;
  final bool isActive;
  final bool isVerified;
  final int? age;
  final double? height;
  final double? weight;
  final String? fitnessGoal;
  final String? experienceLevel;
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.username,
    required this.isActive,
    required this.isVerified,
    this.age,
    this.height,
    this.weight,
    this.fitnessGoal,
    this.experienceLevel,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      username: json['username'],
      isActive: json['is_active'],
      isVerified: json['is_verified'],
      age: json['age'],
      height: json['height']?.toDouble(),
      weight: json['weight']?.toDouble(),
      fitnessGoal: json['fitness_goal'],
      experienceLevel: json['experience_level'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'username': username,
      'is_active': isActive,
      'is_verified': isVerified,
      'age': age,
      'height': height,
      'weight': weight,
      'fitness_goal': fitnessGoal,
      'experience_level': experienceLevel,
      'created_at': createdAt.toIso8601String(),
    };
  }
}