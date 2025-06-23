// mobile/lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'package:pulse_fitness/config/app_config.dart';
import 'package:pulse_fitness/services/storage_service.dart';

class ApiService {
  static final Dio _dio = Dio(BaseOptions(
    baseUrl: AppConfig.apiBaseUrl,
    connectTimeout: Duration(milliseconds: AppConfig.connectionTimeout),
    receiveTimeout: Duration(milliseconds: AppConfig.receiveTimeout),
  ));

  static Future<void> init() async {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await StorageService.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        print('API Error: ${error.message}');
        handler.next(error);
      },
    ));
  }

  // Exercises
  static Future<List<Map<String, dynamic>>> getExercises({
    String? muscleGroup,
    String? equipment,
    int limit = 20,
  }) async {
    final response = await _dio.get('/exercises', queryParameters: {
      if (muscleGroup != null) 'muscle_group': muscleGroup,
      if (equipment != null) 'equipment': equipment,
      'limit': limit,
    });
    return List<Map<String, dynamic>>.from(response.data);
  }

  // Workouts
  static Future<List<Map<String, dynamic>>> getWorkouts() async {
    final response = await _dio.get('/workouts');
    return List<Map<String, dynamic>>.from(response.data);
  }

  static Future<Map<String, dynamic>> createWorkout(Map<String, dynamic> workout) async {
    final response = await _dio.post('/workouts', data: workout);
    return response.data;
  }

  static Future<Map<String, dynamic>> updateWorkout(int id, Map<String, dynamic> workout) async {
    final response = await _dio.put('/workouts/$id', data: workout);
    return response.data;
  }

  // Recommendations
  static Future<List<Map<String, dynamic>>> getExerciseRecommendations({
    int nRecommendations = 10,
    String? workoutType,
  }) async {
    final response = await _dio.post('/recommendations/exercises', data: {
      'n_recommendations': nRecommendations,
      if (workoutType != null) 'workout_type': workoutType,
    });
    return List<Map<String, dynamic>>.from(response.data);
  }

  static Future<Map<String, dynamic>> generateWorkoutPlan(Map<String, dynamic> request) async {
    final response = await _dio.post('/recommendations/workout-plan', data: request);
    return response.data;
  }

  // Social
  static Future<List<Map<String, dynamic>>> getFriends() async {
    final response = await _dio.get('/social/friends');
    return List<Map<String, dynamic>>.from(response.data);
  }

  static Future<List<Map<String, dynamic>>> getFriendRequests() async {
    final response = await _dio.get('/social/friends/requests');
    return List<Map<String, dynamic>>.from(response.data);
  }

  static Future<void> sendFriendRequest(String username) async {
    await _dio.post('/social/friends/request/$username');
  }

  static Future<void> acceptFriendRequest(int friendshipId) async {
    await _dio.put('/social/friends/accept/$friendshipId');
  }

  static Future<void> rejectFriendRequest(int friendshipId) async {
    await _dio.put('/social/friends/reject/$friendshipId');
  }
}
