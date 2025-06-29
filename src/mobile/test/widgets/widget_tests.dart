import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pulse_fitness/widgets/widgets.dart';

void main() {
  group('StoryWidget Tests', () {
    testWidgets('should display story with correct data', (WidgetTester tester) async {
      const story = StoryData(
        name: 'Test User',
        emoji: '👤',
        hasStory: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StoryWidget(story: story),
          ),
        ),
      );

      expect(find.text('Test User'), findsOneWidget);
      expect(find.text('👤'), findsOneWidget);
    });

    testWidgets('should show add button when hasStory is false', (WidgetTester tester) async {
      const story = StoryData(
        name: 'Test User',
        emoji: '👤',
        hasStory: false,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StoryWidget(story: story),
          ),
        ),
      );

      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('should not show add button when hasStory is true', (WidgetTester tester) async {
      const story = StoryData(
        name: 'Test User',
        emoji: '👤',
        hasStory: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StoryWidget(story: story),
          ),
        ),
      );

      expect(find.byIcon(Icons.add), findsNothing);
    });

    testWidgets('should call onTap when tapped', (WidgetTester tester) async {
      bool tapped = false;
      final story = StoryData(
        name: 'Test User',
        emoji: '👤',
        hasStory: true,
        onTap: () => tapped = true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: StoryWidget(story: story),
            ),
          ),
        ),
      );

      await tester.tap(find.byType(Container).first);
      expect(tapped, isTrue);
    });
  });

  group('StoriesRow Tests', () {
    testWidgets('should display multiple stories', (WidgetTester tester) async {
      final stories = [
        const StoryData(name: 'User 1', emoji: '👤', hasStory: true),
        const StoryData(name: 'User 2', emoji: '👤', hasStory: true),
        const StoryData(name: 'User 3', emoji: '👤', hasStory: false),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StoriesRow(stories: stories),
          ),
        ),
      );

      expect(find.text('User 1'), findsOneWidget);
      expect(find.text('User 2'), findsOneWidget);
      expect(find.text('User 3'), findsOneWidget);
    });

    testWidgets('should have correct height', (WidgetTester tester) async {
      final stories = [
        const StoryData(name: 'User 1', emoji: '👤', hasStory: true),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StoriesRow(stories: stories),
          ),
        ),
      );

      final sizedBox = tester.widget<SizedBox>(find.byType(SizedBox).first);
      expect(sizedBox.height, equals(90));
    });
  });

  group('CommunityCard Tests', () {
    testWidgets('should display community with correct data', (WidgetTester tester) async {
      const community = CommunityData(
        name: 'Test Community',
        members: '1.2k',
        active: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CommunityCard(community: community),
          ),
        ),
      );

      expect(find.text('Test Community'), findsOneWidget);
      expect(find.text('1.2k members'), findsOneWidget);
    });

    testWidgets('should show active indicator when active is true', (WidgetTester tester) async {
      const community = CommunityData(
        name: 'Test Community',
        members: '1.2k',
        active: true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CommunityCard(community: community),
          ),
        ),
      );

      expect(find.byType(Container), findsWidgets);
    });

    testWidgets('should call onTap when tapped', (WidgetTester tester) async {
      bool tapped = false;
      final community = CommunityData(
        name: 'Test Community',
        members: '1.2k',
        active: true,
        onTap: () => tapped = true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: CommunityCard(community: community),
            ),
          ),
        ),
      );

      await tester.tap(find.byType(GestureDetector), warnIfMissed: false);
      expect(tapped, isTrue);
    });
  });

  group('CommunitiesRow Tests', () {
    testWidgets('should display title when provided', (WidgetTester tester) async {
      final communities = [
        const CommunityData(name: 'Community 1', members: '1k', active: true),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CommunitiesRow(
              communities: communities,
              title: 'Test Title',
            ),
          ),
        ),
      );

      expect(find.text('Test Title'), findsOneWidget);
    });

    testWidgets('should display see all button when onSeeAll is provided', (WidgetTester tester) async {
      final communities = [
        const CommunityData(name: 'Community 1', members: '1k', active: true),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CommunitiesRow(
              communities: communities,
              title: 'Test Title',
              onSeeAll: () {},
            ),
          ),
        ),
      );

      expect(find.text('See all'), findsOneWidget);
    });
  });

  group('QuickStatCard Tests', () {
    testWidgets('should display stat with correct data', (WidgetTester tester) async {
      const stat = QuickStatData(
        label: 'Workouts',
        value: '12',
        unit: 'this week',
        icon: Icons.fitness_center,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickStatCard(stat: stat),
          ),
        ),
      );

      expect(find.text('Workouts'), findsOneWidget);
      expect(find.text('12'), findsOneWidget);
      expect(find.text('this week'), findsOneWidget);
      expect(find.byIcon(Icons.fitness_center), findsOneWidget);
    });

    testWidgets('should not display icon when not provided', (WidgetTester tester) async {
      const stat = QuickStatData(
        label: 'Workouts',
        value: '12',
        unit: 'this week',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickStatCard(stat: stat),
          ),
        ),
      );

      expect(find.byType(Icon), findsNothing);
    });

    testWidgets('should call onTap when tapped', (WidgetTester tester) async {
      bool tapped = false;
      final stat = QuickStatData(
        label: 'Workouts',
        value: '12',
        unit: 'this week',
        icon: Icons.fitness_center,
        onTap: () => tapped = true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: QuickStatCard(stat: stat),
            ),
          ),
        ),
      );

      await tester.tap(find.byType(GestureDetector), warnIfMissed: false);
      expect(tapped, isTrue);
    });
  });

  group('QuickStatsRow Tests', () {
    testWidgets('should display multiple stats', (WidgetTester tester) async {
      final stats = [
        const QuickStatData(label: 'Workouts', value: '12', unit: 'this week'),
        const QuickStatData(label: 'Calories', value: '2,450', unit: 'burned'),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickStatsRow(stats: stats),
          ),
        ),
      );

      expect(find.text('Workouts'), findsOneWidget);
      expect(find.text('Calories'), findsOneWidget);
    });

    testWidgets('should display title when provided', (WidgetTester tester) async {
      final stats = [
        const QuickStatData(label: 'Workouts', value: '12', unit: 'this week'),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickStatsRow(
              stats: stats,
              title: 'Test Title',
            ),
          ),
        ),
      );

      expect(find.text('Test Title'), findsOneWidget);
    });
  });

  group('FeedPost Tests', () {
    testWidgets('should display post with correct data', (WidgetTester tester) async {
      const post = FeedPostData(
        user: 'Test User',
        location: 'Test Location',
        content: 'Test content',
        activityIcon: '🏋️‍♀️',
        activity: 'Strength Training',
        duration: '45 min',
        likes: '23',
        time: '2 hours ago',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FeedPost(post: post),
          ),
        ),
      );

      expect(find.text('Test User'), findsOneWidget);
      expect(find.text('Test Location'), findsOneWidget);
      expect(find.text('Test content'), findsOneWidget);
      expect(find.text('🏋️‍♀️'), findsOneWidget);
      expect(find.text('Strength Training'), findsOneWidget);
      expect(find.text('45 min'), findsOneWidget);
      expect(find.text('23 likes'), findsOneWidget);
      expect(find.text('2 hours ago'), findsOneWidget);
    });

    testWidgets('should display challenge badge when provided', (WidgetTester tester) async {
      const post = FeedPostData(
        user: 'Test User',
        location: 'Test Location',
        content: 'Test content',
        challenge: 'Test Challenge',
        activityIcon: '🏋️‍♀️',
        activity: 'Strength Training',
        duration: '45 min',
        likes: '23',
        time: '2 hours ago',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FeedPost(post: post),
          ),
        ),
      );

      expect(find.text('Test Challenge'), findsOneWidget);
    });

    testWidgets('should display community badge when provided', (WidgetTester tester) async {
      const post = FeedPostData(
        user: 'Test User',
        location: 'Test Location',
        content: 'Test content',
        community: 'Test Community',
        activityIcon: '🏋️‍♀️',
        activity: 'Strength Training',
        duration: '45 min',
        likes: '23',
        time: '2 hours ago',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FeedPost(post: post),
          ),
        ),
      );

      expect(find.text('Test Community'), findsOneWidget);
    });

    testWidgets('should call onLike when like button is tapped', (WidgetTester tester) async {
      bool liked = false;
      final post = FeedPostData(
        user: 'Test User',
        location: 'Test Location',
        content: 'Test content',
        activityIcon: '🏋️‍♀️',
        activity: 'Strength Training',
        duration: '45 min',
        likes: '23',
        time: '2 hours ago',
        onLike: () => liked = true,
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FeedPost(post: post),
          ),
        ),
      );

      await tester.tap(find.byIcon(Icons.favorite_border));
      expect(liked, isTrue);
    });
  });

  group('FeedPostsList Tests', () {
    testWidgets('should display multiple posts', (WidgetTester tester) async {
      final posts = [
        const FeedPostData(
          user: 'User 1',
          location: 'Location 1',
          content: 'Content 1',
          activityIcon: '🏋️‍♀️',
          activity: 'Activity 1',
          duration: '30 min',
          likes: '10',
          time: '1 hour ago',
        ),
        const FeedPostData(
          user: 'User 2',
          location: 'Location 2',
          content: 'Content 2',
          activityIcon: '🏃‍♂️',
          activity: 'Activity 2',
          duration: '45 min',
          likes: '20',
          time: '2 hours ago',
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FeedPostsList(posts: posts),
          ),
        ),
      );

      expect(find.text('User 1'), findsOneWidget);
      expect(find.text('User 2'), findsOneWidget);
    });
  });
} 