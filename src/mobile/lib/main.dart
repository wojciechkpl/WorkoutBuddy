/// Entry point for the Pulse Fitness Flutter app.
/// 
/// Sets up providers and determines whether to show the login or home screen.

// mobile/lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:pulse_fitness/config/theme.dart';
import 'package:pulse_fitness/providers/auth_provider.dart';
import 'package:pulse_fitness/providers/workout_provider.dart';
import 'package:pulse_fitness/providers/social_provider.dart';
import 'package:pulse_fitness/screens/auth/login_screen.dart';
import 'package:pulse_fitness/screens/home/home_screen.dart';
import 'package:pulse_fitness/services/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await StorageService.init();
  runApp(const PulseFitnessApp());
}

/// The root widget for the Pulse Fitness app.
/// 
/// Provides authentication, workout, and social state to the widget tree.
class PulseFitnessApp extends StatelessWidget {
  const PulseFitnessApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => WorkoutProvider()),
        ChangeNotifierProvider(create: (_) => SocialProvider()),
      ],
      child: MaterialApp(
        title: 'Pulse Fitness',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        home: Consumer<AuthProvider>(
          builder: (context, authProvider, _) {
            if (authProvider.isLoading) {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
            return authProvider.isAuthenticated
                ? const HomeScreen()
                : const LoginScreen();
          },
        ),
      ),
    );
  }
}