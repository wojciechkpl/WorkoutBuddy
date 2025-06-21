/// Provides authentication state and logic for the Pulse Fitness app.
/// 
/// Handles login, registration, logout, and user profile loading.

import 'package:flutter/foundation.dart';
import 'package:pulse_fitness/services/auth_service.dart';
import 'package:pulse_fitness/services/storage_service.dart';

/// Manages authentication state and user profile.
class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  bool _isLoading = true;
  String? _token;
  Map<String, dynamic>? _user;

  /// Whether the user is authenticated.
  bool get isAuthenticated => _isAuthenticated;
  /// Whether authentication state is loading.
  bool get isLoading => _isLoading;
  /// The current JWT token, if any.
  String? get token => _token;
  /// The current user profile, if loaded.
  Map<String, dynamic>? get user => _user;

  /// Initializes the provider and attempts to load the user profile from storage.
  AuthProvider() {
    _initializeAuth();
  }

  /// Loads the token from storage and user profile if available.
  Future<void> _initializeAuth() async {
    try {
      _token = await StorageService.getToken();
      if (_token != null) {
        await _loadUserProfile();
      }
    } catch (e) {
      print('Error initializing auth: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Attempts to log in with the given username and password.
  /// Returns true if successful.
  Future<bool> login(String username, String password) async {
    try {
      _isLoading = true;
      notifyListeners();

      final response = await AuthService.login(username, password);
      _token = response['access_token'];
      await StorageService.saveToken(_token!);
      
      await _loadUserProfile();
      _isAuthenticated = true;
      
      return true;
    } catch (e) {
      print('Login error: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Registers a new user and returns true if successful.
  Future<bool> register(String username, String email, String password, String fullName) async {
    try {
      _isLoading = true;
      notifyListeners();

      await AuthService.register(username, email, password, fullName);
      return true;
    } catch (e) {
      print('Registration error: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Loads the user profile from the backend.
  Future<void> _loadUserProfile() async {
    try {
      _user = await AuthService.getUserProfile();
    } catch (e) {
      print('Error loading user profile: $e');
      await logout();
    }
  }

  /// Logs out the user and clears all authentication state.
  Future<void> logout() async {
    _isAuthenticated = false;
    _token = null;
    _user = null;
    await AuthService.logout();
    notifyListeners();
  }

  /// Updates the user profile with the given fields.
  Future<void> updateProfile(Map<String, dynamic> updates) async {
    try {
      _user = await AuthService.updateUserProfile(updates);
      notifyListeners();
    } catch (e) {
      print('Error updating profile: $e');
      rethrow;
    }
  }
} 