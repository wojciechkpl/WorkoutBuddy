// mobile/lib/config/app_config.dart
class AppConfig {
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';
  static const String appName = 'Pulse Fitness';
  static const String appVersion = '1.0.0';

  // API endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String userProfileEndpoint = '/auth/me';
  static const String updateProfileEndpoint = '/users/profile';
  static const String exercisesEndpoint = '/exercises';
  static const String workoutsEndpoint = '/workouts';
  static const String recommendationsEndpoint = '/recommendations';
  static const String socialEndpoint = '/social';

  // Timeouts
  static const int connectionTimeout = 10000; // 10 seconds
  static const int receiveTimeout = 10000; // 10 seconds

  // Storage keys
  static const String tokenKey = 'auth_token';
  static const String userDataKey = 'user_data';
  static const String settingsKey = 'app_settings';
}
