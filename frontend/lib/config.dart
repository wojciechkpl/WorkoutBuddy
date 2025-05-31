import 'package:flutter/services.dart' show rootBundle;
import 'package:yaml/yaml.dart';

class AppConfig {
  final String apiBaseUrl;
  final String environment;
  final Map featureFlags;

  AppConfig({required this.apiBaseUrl, required this.environment, required this.featureFlags});

  static Future<AppConfig> load() async {
    final yamlString = await rootBundle.loadString('assets/config.yaml');
    final yamlMap = loadYaml(yamlString);
    final frontend = yamlMap['frontend'];
    return AppConfig(
      apiBaseUrl: frontend['api_base_url'],
      environment: frontend['environment'],
      featureFlags: Map.from(frontend['feature_flags'] ?? {}),
    );
  }
} 