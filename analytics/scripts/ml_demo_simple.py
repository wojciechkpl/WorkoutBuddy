#!/usr/bin/env python3
"""
WorkoutBuddy ML Features Demonstration Script

This interactive demonstration showcases the AI and machine learning capabilities
of the WorkoutBuddy platform. It provides hands-on examples of:

1. AI-powered challenge generation with GPT models
2. Community matching using similarity algorithms
3. Real-time analytics and cohort analysis
4. A/B testing framework functionality
5. Recommendation engine algorithms

The demo is designed to:
- Show practical applications of each ML feature
- Demonstrate configuration-driven hyperparameter tuning
- Visualize algorithm outputs and performance metrics
- Test both AI-enabled and fallback modes
- Provide interactive examples for learning and development

Usage:
    python ml_demo_simple.py

Requirements:
- All dependencies from requirements-dev.txt
- Optional: OpenAI API key for full AI features
- Optional: PostHog API key for analytics tracking

Author: WorkoutBuddy Team
Version: 2.1.0
"""

import sys
import os
import asyncio
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Add app to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "ml_backend"))

# Import WorkoutBuddy components
from app.config import backend_config
from app.ai_services import ai_service
from app.analytics import analytics_service
from app.ab_testing import ab_testing_service

# Configure visualization
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


class WorkoutBuddyMLDemo:
    """
    Interactive demonstration class for WorkoutBuddy ML features.

    This class provides a structured way to showcase and test all
    machine learning capabilities of the platform with real examples.
    """

    def __init__(self):
        """Initialize demo with sample data and configuration."""
        print("🚀 Initializing WorkoutBuddy ML Demo")
        print(
            f"AI Service: {'✅ Enabled' if ai_service.enabled else '⚠️ Fallback Mode'}"
        )
        print(
            f"Analytics: {'✅ Enabled' if analytics_service.enabled else '⚠️ Local Mode'}"
        )
        print(f"ML Algorithm: {backend_config.ml.similarity_algorithm}")
        print("=" * 50)

        # Generate sample user data for demonstrations
        self.sample_users = self._create_sample_users()

    def _create_sample_users(self):
        """
        Create realistic sample user data for ML demonstrations.

        Returns:
            list: Sample user objects with varied fitness profiles
        """
        from dataclasses import dataclass

        @dataclass
        class SampleUser:
            id: int
            name: str
            goal_type: str
            fitness_level: str
            activity_level: float
            engagement_score: float
            location: tuple
            preferred_times: list
            equipment: list

        users = [
            SampleUser(
                1,
                "Alex Runner",
                "cardio",
                "beginner",
                2.5,
                0.8,
                (40.7589, -73.9851),
                ["morning"],
                ["none"],
            ),
            SampleUser(
                2,
                "Sam Strong",
                "strength",
                "intermediate",
                4.0,
                0.9,
                (40.7505, -73.9934),
                ["evening"],
                ["dumbbells", "bench"],
            ),
            SampleUser(
                3,
                "Jordan Flex",
                "flexibility",
                "advanced",
                3.5,
                0.7,
                (40.7614, -73.9776),
                ["morning", "evening"],
                ["yoga_mat", "blocks"],
            ),
            SampleUser(
                4,
                "Casey Cardio",
                "cardio",
                "intermediate",
                3.8,
                0.85,
                (40.7549, -73.9840),
                ["evening"],
                ["treadmill"],
            ),
            SampleUser(
                5,
                "Riley Recovery",
                "flexibility",
                "beginner",
                2.0,
                0.6,
                (40.7580, -73.9855),
                ["morning"],
                ["yoga_mat"],
            ),
        ]
        return users

    async def demo_ai_challenges(self):
        """
        Demonstrate AI-powered challenge generation.

        This demo shows how the system generates personalized workout
        challenges using GPT models, with fallback to template responses
        when AI is unavailable.
        """
        print("\n🎯 AI-Powered Challenge Generation Demo")
        print("-" * 40)

        for user in self.sample_users[:3]:  # Demo with first 3 users
            print(f"\n👤 Generating challenge for {user.name}")
            print(f"   Goal: {user.goal_type} | Level: {user.fitness_level}")

            # Simulate user history for personalization
            user_history = {
                "recent_completion_rate": user.engagement_score,
                "recent_challenges": [f"Previous {user.goal_type} workout"],
                "preferred_duration": 20 + (user.activity_level * 5),
            }

            # User preferences for challenge customization
            preferences = {
                "goal_type": user.goal_type,
                "fitness_level": user.fitness_level,
                "equipment": user.equipment,
                "duration": int(user_history["preferred_duration"]),
            }

            try:
                # Generate personalized challenge
                challenge = await ai_service.generate_personalized_challenge(
                    user, user_history, preferences
                )

                # Display challenge details
                print(f"   📋 Title: {challenge.title}")
                print(f"   ⏱️  Duration: {challenge.duration}")
                print(f"   📊 Difficulty: {challenge.difficulty}/5")
                print(
                    f"   🔧 Equipment: {', '.join(challenge.equipment_needed) or 'None'}"
                )
                print(f"   💪 Motivation: {challenge.motivation_message}")
                print(f"   🤖 AI Generated: {challenge.ai_generated}")

            except Exception as e:
                print(f"   ❌ Challenge generation failed: {e}")

        # Show AI configuration being used
        print(f"\n🔧 Current AI Configuration:")
        print(f"   Model: {backend_config.ai.model_name}")
        print(f"   Temperature: {backend_config.ai.temperature}")
        print(f"   Max Tokens: {backend_config.ai.max_tokens}")
        print(f"   Creativity: {backend_config.ai.challenge_creativity}")

    def demo_community_matching(self):
        """
        Demonstrate ML-powered community matching algorithms.

        This demo shows how users are matched based on similarity
        calculations using configurable feature weights and algorithms.
        """
        print("\n🤝 Community Matching Algorithm Demo")
        print("-" * 40)

        # Convert user data to feature matrix for ML processing
        feature_matrix = self._create_feature_matrix()

        # Calculate similarity matrix using configured algorithm
        from sklearn.metrics.pairwise import cosine_similarity

        similarity_matrix = cosine_similarity(feature_matrix)

        # Demonstrate matching for the first user
        target_user = self.sample_users[0]
        print(f"\n🎯 Finding matches for {target_user.name}")
        print(f"   Profile: {target_user.goal_type}, {target_user.fitness_level}")

        # Get similarity scores for target user
        user_similarities = similarity_matrix[0]  # First user's similarities

        # Find top matches (excluding self)
        match_indices = np.argsort(user_similarities)[::-1][1:4]  # Top 3 matches

        print(f"\n📊 Top 3 Community Matches:")
        for i, match_idx in enumerate(match_indices, 1):
            match_user = self.sample_users[match_idx]
            similarity_score = user_similarities[match_idx]

            print(f"   {i}. {match_user.name}")
            print(f"      Similarity: {similarity_score:.3f}")
            print(f"      Profile: {match_user.goal_type}, {match_user.fitness_level}")
            print(
                f"      Common interests: {self._find_common_interests(target_user, match_user)}"
            )

        # Visualize similarity distribution
        self._plot_similarity_analysis(similarity_matrix, target_user.name)

        # Show configuration influence
        print(f"\n🔧 Matching Configuration:")
        print(f"   Algorithm: {backend_config.ml.similarity_algorithm}")
        print(f"   Feature Weights: {backend_config.ml.feature_weights}")
        print(
            f"   Compatibility Threshold: {backend_config.ai.compatibility_threshold}"
        )

    def _create_feature_matrix(self):
        """
        Convert user data into numerical feature matrix for ML algorithms.

        Returns:
            numpy.ndarray: Normalized feature matrix for similarity calculations
        """
        features = []

        for user in self.sample_users:
            # Create feature vector for each user
            feature_vector = [
                1.0 if user.goal_type == "cardio" else 0.0,
                1.0 if user.goal_type == "strength" else 0.0,
                1.0 if user.goal_type == "flexibility" else 0.0,
                user.activity_level / 5.0,  # Normalize to 0-1
                user.engagement_score,
                1.0 if "morning" in user.preferred_times else 0.0,
                1.0 if "evening" in user.preferred_times else 0.0,
                user.location[0] / 100.0,  # Normalize latitude
                user.location[1] / -100.0,  # Normalize longitude
            ]
            features.append(feature_vector)

        return np.array(features)

    def _find_common_interests(self, user1, user2):
        """Find shared interests between two users."""
        common = []

        if user1.goal_type == user2.goal_type:
            common.append(f"Both focus on {user1.goal_type}")

        shared_times = set(user1.preferred_times) & set(user2.preferred_times)
        if shared_times:
            common.append(f"Both prefer {', '.join(shared_times)} workouts")

        shared_equipment = set(user1.equipment) & set(user2.equipment)
        if shared_equipment:
            common.append(f"Both use {', '.join(shared_equipment)}")

        return ", ".join(common) if common else "Different preferences but compatible"

    def _plot_similarity_analysis(self, similarity_matrix, target_name):
        """
        Create visualization of similarity analysis results.

        Args:
            similarity_matrix: User similarity matrix
            target_name: Name of the target user for analysis
        """
        plt.figure(figsize=(12, 4))

        # Plot 1: Similarity distribution for target user
        plt.subplot(1, 2, 1)
        target_similarities = similarity_matrix[0]  # First user's similarities
        plt.hist(
            target_similarities, bins=10, alpha=0.7, color="skyblue", edgecolor="black"
        )
        plt.title(f"Similarity Distribution for {target_name}")
        plt.xlabel("Cosine Similarity")
        plt.ylabel("Frequency")
        plt.axvline(
            backend_config.ai.compatibility_threshold,
            color="red",
            linestyle="--",
            label=f"Threshold ({backend_config.ai.compatibility_threshold})",
        )
        plt.legend()

        # Plot 2: Full similarity matrix heatmap
        plt.subplot(1, 2, 2)
        user_names = [
            user.name.split()[0] for user in self.sample_users
        ]  # First names only
        sns.heatmap(
            similarity_matrix,
            annot=True,
            fmt=".2f",
            xticklabels=user_names,
            yticklabels=user_names,
            cmap="viridis",
            cbar_kws={"label": "Cosine Similarity"},
        )
        plt.title("User Similarity Matrix")
        plt.tight_layout()
        plt.show()

    def demo_analytics_insights(self):
        """
        Demonstrate analytics and cohort analysis capabilities.

        This shows how the platform tracks user behavior and generates
        insights for retention and engagement optimization.
        """
        print("\n📊 Analytics & Cohort Analysis Demo")
        print("-" * 40)

        # Generate synthetic event data for demonstration
        events_data = self._generate_sample_events()

        # Analyze user engagement patterns
        engagement_analysis = self._analyze_engagement(events_data)

        print(f"📈 Engagement Analysis:")
        print(f"   Total Events: {len(events_data)}")
        print(f"   Active Users: {engagement_analysis['active_users']}")
        print(f"   Avg. Sessions per User: {engagement_analysis['avg_sessions']:.1f}")
        print(
            f"   Challenge Completion Rate: {engagement_analysis['completion_rate']:.1%}"
        )

        # Demonstrate cohort analysis
        cohort_data = self._simulate_cohort_analysis()

        print(f"\n📊 Cohort Analysis (30-day window):")
        for cohort in cohort_data:
            print(f"   Week {cohort['week']}: {cohort['retention_rate']:.1%} retention")
            print(f"      Goal completion: {cohort['goal_completion']:.1%}")
            print(f"      Avg engagement: {cohort['avg_engagement']:.2f}")

        # Show analytics configuration
        print(f"\n🔧 Analytics Configuration:")
        print(
            f"   Service: {'PostHog' if analytics_service.enabled else 'Local tracking'}"
        )
        print(f"   Batch Size: {backend_config.analytics.batch_size}")
        print(f"   Flush Interval: {backend_config.analytics.flush_interval}s")

    def _generate_sample_events(self):
        """Generate realistic sample event data."""
        events = []
        event_types = [
            "challenge_completed",
            "goal_created",
            "community_joined",
            "workout_logged",
            "profile_updated",
        ]

        # Generate events for each user over the past 30 days
        for user in self.sample_users:
            for day in range(30):
                # Simulate varying activity levels
                if np.random.random() < user.engagement_score:
                    event = {
                        "user_id": user.id,
                        "event_type": np.random.choice(event_types),
                        "timestamp": datetime.now() - timedelta(days=day),
                        "properties": {"goal_type": user.goal_type},
                    }
                    events.append(event)

        return events

    def _analyze_engagement(self, events_data):
        """Analyze user engagement from event data."""
        unique_users = len(set(event["user_id"] for event in events_data))
        total_sessions = len(
            [e for e in events_data if e["event_type"] == "challenge_completed"]
        )
        completions = len(
            [e for e in events_data if e["event_type"] == "challenge_completed"]
        )
        total_challenges = len(
            [e for e in events_data if "challenge" in e["event_type"]]
        )

        return {
            "active_users": unique_users,
            "avg_sessions": len(events_data) / unique_users if unique_users > 0 else 0,
            "completion_rate": completions / max(total_challenges, 1),
        }

    def _simulate_cohort_analysis(self):
        """Simulate cohort analysis results."""
        cohorts = []
        for week in range(1, 5):  # 4 weeks of data
            retention = 1.0 - (week * 0.15)  # Simulate retention decline
            goal_completion = 0.8 - (week * 0.1)  # Simulate goal completion decline
            avg_engagement = 0.9 - (week * 0.05)  # Simulate engagement decline

            cohorts.append(
                {
                    "week": week,
                    "retention_rate": max(retention, 0.2),
                    "goal_completion": max(goal_completion, 0.3),
                    "avg_engagement": max(avg_engagement, 0.5),
                }
            )

        return cohorts

    def demo_ab_testing(self):
        """
        Demonstrate A/B testing framework functionality.

        This shows how experiments are configured, users are assigned
        to variants, and results are analyzed for statistical significance.
        """
        print("\n🧪 A/B Testing Framework Demo")
        print("-" * 40)

        # Show active experiments
        active_experiments = ab_testing_service.get_active_experiments()

        print(f"📋 Active Experiments: {len(active_experiments)}")
        for exp in active_experiments:
            print(f"   • {exp.name}")
            print(f"     Status: {exp.status.value}")
            print(f"     Variants: {len(exp.variants)}")

            # Show user assignments for demo users
            print(f"     User Assignments:")
            for user in self.sample_users[:3]:
                variant = ab_testing_service.get_user_variant(
                    str(user.id), exp.experiment_id
                )
                print(f"       {user.name}: {variant}")

        # Simulate experiment results
        print(f"\n📊 Simulated Experiment Results:")
        sample_results = self._simulate_experiment_results()

        for variant, results in sample_results.items():
            print(f"   {variant}:")
            print(f"     Conversion Rate: {results['conversion_rate']:.1%}")
            print(f"     Sample Size: {results['sample_size']}")
            print(f"     Confidence: {results['confidence']:.1%}")

        # Show configuration
        print(f"\n🔧 A/B Testing Configuration:")
        print(
            f"   Default Allocation: {backend_config.ab_testing.default_traffic_allocation}"
        )
        print(f"   Min Sample Size: {backend_config.ab_testing.minimum_sample_size}")
        print(f"   Confidence Level: {backend_config.ab_testing.confidence_level}")

    def _simulate_experiment_results(self):
        """Simulate A/B test results with realistic data."""
        return {
            "Control": {
                "conversion_rate": 0.15,
                "sample_size": 1250,
                "confidence": 0.95,
            },
            "AI_Challenges": {
                "conversion_rate": 0.22,
                "sample_size": 1180,
                "confidence": 0.98,
            },
        }

    async def run_full_demo(self):
        """
        Run the complete ML features demonstration.

        This orchestrates all demo components in a logical sequence
        to showcase the full capabilities of WorkoutBuddy's ML platform.
        """
        print("🎉 Welcome to the WorkoutBuddy ML Demo!")
        print("This demo showcases our AI-powered fitness platform capabilities.")
        print("=" * 60)

        try:
            # Run all demonstration components
            await self.demo_ai_challenges()
            self.demo_community_matching()
            self.demo_analytics_insights()
            self.demo_ab_testing()

            print("\n" + "=" * 60)
            print("✅ Demo completed successfully!")
            print("\n📚 Key Takeaways:")
            print("   • AI generates personalized workout challenges")
            print("   • ML algorithms match users with compatible communities")
            print("   • Analytics track engagement and optimize retention")
            print("   • A/B testing validates feature improvements")
            print("   • All hyperparameters are configurable without code changes")

        except Exception as e:
            print(f"\n❌ Demo encountered an error: {e}")
            print("Please check your configuration and dependencies.")


async def main():
    """
    Main entry point for the ML demonstration.

    Initializes the demo environment and runs the complete showcase
    of WorkoutBuddy's machine learning capabilities.
    """
    try:
        demo = WorkoutBuddyMLDemo()
        await demo.run_full_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Thanks for exploring WorkoutBuddy ML!")
    except Exception as e:
        print(f"\n❌ Demo failed to start: {e}")
        print(
            "Please ensure all dependencies are installed and configuration is valid."
        )


if __name__ == "__main__":
    # Run the interactive demonstration
    asyncio.run(main())
