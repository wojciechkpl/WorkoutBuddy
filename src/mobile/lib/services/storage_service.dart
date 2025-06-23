// mobile/lib/services/storage_service.dart
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  static const String _settingsKey = 'app_settings';

  static Future<void> init() async {
    await SharedPreferences.getInstance();
  }

  // Token management
  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  // User data management
  static Future<void> saveUserData(Map<String, dynamic> userData) async {
    final prefs = await SharedPreferences.getInstance();
    final userString = userData.toString(); // Simple serialization
    await prefs.setString(_userKey, userString);
  }

  static Future<Map<String, dynamic>?> getUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userString = prefs.getString(_userKey);
    if (userString != null) {
      // Simple deserialization - in production, use proper JSON serialization
      return {'user_data': userString};
    }
    return null;
  }

  static Future<void> clearUserData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
  }

  // Settings management
  static Future<void> saveSettings(Map<String, dynamic> settings) async {
    final prefs = await SharedPreferences.getInstance();
    for (final entry in settings.entries) {
      if (entry.value is String) {
        await prefs.setString('${_settingsKey}_${entry.key}', entry.value as String);
      } else if (entry.value is int) {
        await prefs.setInt('${_settingsKey}_${entry.key}', entry.value as int);
      } else if (entry.value is bool) {
        await prefs.setBool('${_settingsKey}_${entry.key}', entry.value as bool);
      } else if (entry.value is double) {
        await prefs.setDouble('${_settingsKey}_${entry.key}', entry.value as double);
      }
    }
  }

  static Future<Map<String, dynamic>> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys();
    final settings = <String, dynamic>{};

    for (final key in keys) {
      if (key.startsWith(_settingsKey)) {
        final settingKey = key.substring(_settingsKey.length + 1);
        settings[settingKey] = prefs.get(key);
      }
    }

    return settings;
  }

  // Clear all data
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
