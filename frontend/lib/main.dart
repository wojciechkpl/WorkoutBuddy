import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final appConfig = await AppConfig.load();
  runApp(MyApp(appConfig: appConfig));
}

class MyApp extends StatelessWidget {
  final AppConfig appConfig;
  const MyApp({super.key, required this.appConfig});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WorkoutBuddy',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // TRY THIS: Try running your application with "flutter run". You'll see
        // the application has a purple toolbar. Then, without quitting the app,
        // try changing the seedColor in the colorScheme below to Colors.green
        // and then invoke "hot reload" (save your changes or press the "hot
        // reload" button in a Flutter-supported IDE, or press "r" if you used
        // the command line to start the app).
        //
        // Notice that the counter didn't reset back to zero; the application
        // state is not lost during the reload. To reset the state, use hot
        // restart instead.
        //
        // This works for code too, not just values: Most code changes can be
        // tested with just a hot reload.
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: HomeScreen(appConfig: appConfig),
    );
  }
}

class HomeScreen extends StatefulWidget {
  final AppConfig appConfig;
  const HomeScreen({super.key, required this.appConfig});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? apiResponse;
  bool loading = false;

  Future<void> fetchApiRoot() async {
    setState(() => loading = true);
    final url = Uri.parse('${widget.appConfig.apiBaseUrl}/');
    try {
      final response = await http.get(url);
      setState(() {
        apiResponse = response.body;
        loading = false;
      });
    } catch (e) {
      setState(() {
        apiResponse = 'Error: $e';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final enableSocial = widget.appConfig.featureFlags['enable_social'] == true;
    return Scaffold(
      appBar: AppBar(
        // TRY THIS: Try changing the color here to a specific color (to
        // Colors.amber, perhaps?) and trigger a hot reload to see the AppBar
        // change color while the other colors stay the same.
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        // Here we take the value from the MyHomePage object that was created by
        // the App.build method, and use it to set our appbar title.
        title: const Text('WorkoutBuddy'),
      ),
      body: Center(
        // Center is a layout widget. It takes a single child and positions it
        // in the middle of the parent.
        child: Column(
          // Column is also a layout widget. It takes a list of children and
          // arranges them vertically. By default, it sizes itself to fit its
          // children horizontally, and tries to be as tall as its parent.
          //
          // Column has various properties to control how it sizes itself and
          // how it positions its children. Here we use mainAxisAlignment to
          // center the children vertically; the main axis here is the vertical
          // axis because Columns are vertical (the cross axis would be
          // horizontal).
          //
          // TRY THIS: Invoke "debug painting" (choose the "Toggle Debug Paint"
          // action in the IDE, or press "p" in the console), to see the
          // wireframe for each widget.
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('API Base URL:'),
            Text(widget.appConfig.apiBaseUrl, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Text('Environment: ${widget.appConfig.environment}'),
            const SizedBox(height: 16),
            Text('Feature Flags:'),
            Text(widget.appConfig.featureFlags.toString()),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: fetchApiRoot,
              child: const Text('Fetch API Root'),
            ),
            if (loading) const CircularProgressIndicator(),
            if (apiResponse != null) ...[
              const SizedBox(height: 16),
              Text('API Response:'),
              Text(apiResponse!),
            ],
            const SizedBox(height: 32),
            if (enableSocial)
              const Text('🎉 Social features are enabled!'),
            if (!enableSocial)
              const Text('Social features are disabled.'),
          ],
        ),
      ),
    );
  }
}
