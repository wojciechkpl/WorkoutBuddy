import 'package:flutter/foundation.dart';
import 'package:pulse_fitness/services/api_service.dart';

class WorkoutProvider with ChangeNotifier {
  List<Map<String, dynamic>> _workouts = [];
  List<Map<String, dynamic>> _exercises = [];
  bool _isLoading = false;

  List<Map<String, dynamic>> get workouts => _workouts;
  List<Map<String, dynamic>> get exercises => _exercises;
  bool get isLoading => _isLoading;

  Future<void> loadWorkouts() async {
    try {
      _isLoading = true;
      notifyListeners();

      _workouts = await ApiService.getWorkouts();
    } catch (e) {
      print('Error loading workouts: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadExercises({
    String? muscleGroup,
    String? equipment,
    int limit = 20,
  }) async {
    try {
      _isLoading = true;
      notifyListeners();

      _exercises = await ApiService.getExercises(
        muscleGroup: muscleGroup,
        equipment: equipment,
        limit: limit,
      );
    } catch (e) {
      print('Error loading exercises: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createWorkout(Map<String, dynamic> workout) async {
    try {
      _isLoading = true;
      notifyListeners();

      final newWorkout = await ApiService.createWorkout(workout);
      _workouts.add(newWorkout);
      
      return true;
    } catch (e) {
      print('Error creating workout: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateWorkout(int id, Map<String, dynamic> workout) async {
    try {
      _isLoading = true;
      notifyListeners();

      final updatedWorkout = await ApiService.updateWorkout(id, workout);
      final index = _workouts.indexWhere((w) => w['id'] == id);
      if (index != -1) {
        _workouts[index] = updatedWorkout;
      }
      
      return true;
    } catch (e) {
      print('Error updating workout: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<List<Map<String, dynamic>>> getExerciseRecommendations({
    int nRecommendations = 10,
    String? workoutType,
  }) async {
    try {
      return await ApiService.getExerciseRecommendations(
        nRecommendations: nRecommendations,
        workoutType: workoutType,
      );
    } catch (e) {
      print('Error getting exercise recommendations: $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> generateWorkoutPlan(Map<String, dynamic> request) async {
    try {
      return await ApiService.generateWorkoutPlan(request);
    } catch (e) {
      print('Error generating workout plan: $e');
      return null;
    }
  }
} 