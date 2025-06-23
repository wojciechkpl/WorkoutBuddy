import 'package:dio/dio.dart';
import 'package:pulse_fitness/config/app_config.dart';
import 'package:pulse_fitness/services/storage_service.dart';

class AuthService {
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
        print('Auth Service Error: ${error.message}');
        handler.next(error);
      },
    ));
  }

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _dio.post(AppConfig.loginEndpoint, data: {
      'username': username,
      'password': password,
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
    String fullName
  ) async {
    final response = await _dio.post(AppConfig.registerEndpoint, data: {
      'username': username,
      'email': email,
      'password': password,
      'full_name': fullName,
    });
    return response.data;
  }

  static Future<Map<String, dynamic>> getUserProfile() async {
    final response = await _dio.get(AppConfig.userProfileEndpoint);
    return response.data;
  }

  static Future<Map<String, dynamic>> updateUserProfile(Map<String, dynamic> updates) async {
    final response = await _dio.put(AppConfig.updateProfileEndpoint, data: updates);
    return response.data;
  }

  static Future<void> logout() async {
    await StorageService.clearToken();
    await StorageService.clearUserData();
  }
}
