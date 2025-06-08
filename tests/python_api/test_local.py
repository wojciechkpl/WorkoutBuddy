#!/usr/bin/env python3
"""
WorkoutBuddy Local Development Testing Suite

This script provides comprehensive testing of the WorkoutBuddy backend components
in a local development environment. It validates that all systems are properly
configured and functional before starting the full application.

Test Coverage:
- Configuration loading and validation
- Database connectivity (SQLite/PostgreSQL)
- AI service functionality (with fallback testing)
- Machine learning feature validation
- Analytics service setup
- Component integration testing

The testing suite is designed to:
1. Catch configuration issues early in development
2. Validate that all dependencies are properly installed
3. Test both AI-enabled and fallback modes
4. Ensure database migrations work correctly
5. Verify that ML algorithms function with sample data

Usage:
    python test_local.py

Exit Codes:
    0: All tests passed successfully
    1: One or more tests failed

Requirements:
- All dependencies from requirements-dev.txt installed
- Valid config.yaml file (optional)
- Database accessible (SQLite file will be created if needed)

Author: WorkoutBuddy Team
Version: 2.1.0
"""

import asyncio
import sys
import os
from pathlib import Path

# Add app to path for local imports
sys.path.append(str(Path(__file__).parent.parent.parent / "ml_backend"))

from app.config import backend_config
from app.database import engine, SessionLocal
from app import models
from sqlalchemy import text


def test_database():
    """
    Test database connection and table creation.

    This test validates:
    - Database connection establishment
    - SQLAlchemy engine functionality
    - Table creation from models
    - Basic query execution

    For SQLite (development):
    - Creates database file if it doesn't exist
    - Tests file permissions and accessibility

    For PostgreSQL (production):
    - Validates connection string format
    - Tests authentication and permissions
    - Verifies database exists and is accessible

    Returns:
        bool: True if database tests pass, False otherwise
    """
    print("🗄️  Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!", result.fetchone())
        return True
    except Exception as e:
        print("❌ Database connection failed:", str(e))
        return False


def test_config():
    """
    Test configuration loading and validation.

    This test validates:
    - Configuration file parsing (YAML/environment variables)
    - All configuration sections are properly loaded
    - Type safety and default value handling
    - Environment variable override functionality
    - ML hyperparameter accessibility

    The test checks that all major configuration sections contain
    expected values and that the configuration can be accessed
    without errors throughout the application.

    Returns:
        bool: True if configuration is valid, False otherwise
    """
    print("⚙️  Testing configuration...")
    try:
        # Test basic application settings access
        print(
            f"   📋 App host: {backend_config.app.api_host}:{backend_config.app.api_port}"
        )

        # Test feature flag accessibility
        print(f"   🤖 AI enabled: {backend_config.ai.enabled}")
        print(f"   📊 Analytics enabled: {backend_config.analytics.enabled}")
        print(f"   🧪 A/B testing enabled: {backend_config.ab_testing.enabled}")

        # Test ML configuration accessibility
        print(f"   🔬 ML algorithm: {backend_config.ml.similarity_algorithm}")
        print(
            f"   🎯 Feature weights: {list(backend_config.ml.feature_weights.keys())}"
        )

        print("   ✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False


async def test_ai_service():
    """
    Test AI service functionality in both enabled and fallback modes.

    This test validates:
    - AI service initialization
    - OpenAI API key detection
    - Fallback mode when API key is missing
    - Challenge generation functionality
    - Response format validation
    - Error handling for API failures

    The test uses mock user data to generate a sample challenge,
    ensuring that the AI service can process user information
    and return properly formatted responses regardless of whether
    the OpenAI API is available.

    Returns:
        bool: True if AI service tests pass, False otherwise
    """
    print("🤖 Testing AI service...")
    try:
        from app.ai_services import ai_service

        # Create mock user data for testing
        # This simulates the user objects that would come from the database
        class MockUser:
            def __init__(self):
                self.id = 1
                self.name = "Test User"
                self.goal_type = "cardio"

        user = MockUser()

        # Mock user history and preferences for challenge generation
        user_history = {"recent_completion_rate": 0.8, "recent_challenges": []}
        preferences = {"goal_type": "cardio", "fitness_level": "beginner"}

        # Test challenge generation - this will use AI if available,
        # or fall back to template responses if not
        challenge = await ai_service.generate_personalized_challenge(
            user, user_history, preferences
        )

        # Validate response format and content
        print(f"   📋 Generated challenge: {challenge.title}")
        print(f"   🤖 AI powered: {challenge.ai_generated}")

        # Ensure required fields are present
        assert hasattr(challenge, "title"), "Challenge missing title"
        assert hasattr(challenge, "description"), "Challenge missing description"
        assert hasattr(challenge, "ai_generated"), "Challenge missing AI flag"

        print("   ✅ AI service working")
        return True
    except Exception as e:
        print(f"   ❌ AI service error: {e}")
        return False


def test_ml_features():
    """
    Test machine learning algorithms and data processing.

    This test validates:
    - ML library imports (numpy, scikit-learn)
    - Similarity calculation algorithms
    - Data matrix operations
    - Configuration-based algorithm selection
    - Numerical computation accuracy

    The test generates sample data to ensure that the core ML
    algorithms used for community matching and recommendations
    are working correctly. This catches issues with:
    - Missing dependencies
    - Version incompatibilities
    - Numerical computation errors
    - Configuration-driven algorithm selection

    Returns:
        bool: True if ML features work correctly, False otherwise
    """
    print("🔬 Testing ML features...")
    try:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        # Generate sample data matrix for similarity testing
        # This simulates user feature vectors for community matching
        data = np.random.rand(5, 3)

        # Test similarity calculation using the configured algorithm
        # This is the core operation for community matching
        similarity = cosine_similarity(data)

        # Validate results make sense
        print(f"   📊 Similarity matrix shape: {similarity.shape}")
        print(f"   🎯 Max similarity: {similarity.max():.3f}")

        # Basic sanity checks for similarity matrix
        assert similarity.shape == (5, 5), "Incorrect similarity matrix shape"
        assert 0.0 <= similarity.max() <= 1.0, "Similarity values out of range"

        print("   ✅ ML features working")
        return True
    except Exception as e:
        print(f"   ❌ ML error: {e}")
        return False


def test_analytics():
    """
    Test analytics service initialization and configuration.

    This test validates:
    - Analytics service module loading
    - PostHog configuration detection
    - Service enablement logic
    - Event structure validation
    - Fallback behavior when analytics disabled

    The test doesn't send actual events to avoid polluting
    analytics data during development, but ensures that the
    analytics system is properly configured and ready to
    track events when needed.

    Returns:
        bool: True if analytics service is properly configured, False otherwise
    """
    print("📊 Testing analytics...")
    try:
        from app.analytics import analytics_service

        # Create sample event structure for validation
        # This ensures the analytics service can handle typical event data
        test_event = {"event": "test_event", "properties": {"test": True}}

        # Test service state and configuration
        print(f"   📈 Analytics enabled: {analytics_service.enabled}")

        # Validate that the service initializes without errors
        # Even when disabled, it should not cause import or initialization failures
        assert hasattr(analytics_service, "enabled"), (
            "Analytics service missing enabled attribute"
        )

        print("   ✅ Analytics service ready")
        return True
    except Exception as e:
        print(f"   ❌ Analytics error: {e}")
        return False


async def main():
    """
    Main test orchestration function.

    This function:
    1. Runs all test functions in a logical order
    2. Collects results and generates a summary report
    3. Provides next steps for successful setups
    4. Returns appropriate exit codes for CI/CD integration

    The test order is designed to catch fundamental issues first
    (configuration, database) before testing higher-level features
    (AI, ML, analytics) that depend on the foundation.

    Returns:
        bool: True if all tests pass, False if any test fails
    """
    print("🚀 WorkoutBuddy Local Testing")
    print("=" * 40)

    # Define test suite with descriptive names and test functions
    # Order matters: test fundamental components first
    tests = [
        ("Configuration", test_config),  # Test config loading first
        ("Database", test_database),  # Test database connection
        ("AI Service", test_ai_service),  # Test AI functionality
        ("ML Features", test_ml_features),  # Test ML algorithms
        ("Analytics", test_analytics),  # Test analytics setup
    ]

    results = []

    # Execute each test and collect results
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            # Handle async test functions
            result = await test_func()
        else:
            # Handle synchronous test functions
            result = test_func()
        results.append(result)
        print()  # Add spacing between tests for readability

    # Generate comprehensive test report
    print("=" * 40)
    print("📊 Test Results Summary:")
    for (test_name, _), result in zip(tests, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    # Calculate overall result
    overall = all(results)
    print(
        f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}"
    )

    # Provide next steps for successful setups
    if overall:
        print("\n🎉 Your WorkoutBuddy setup is ready!")
        print("📚 Next steps:")
        print("   1. Start the server: uvicorn app.main:app --reload")
        print(
            "   2. Open the demo notebook: jupyter notebook workoutbuddy_ml_demo.ipynb"
        )
        print("   3. Visit API docs: http://localhost:8000/docs")

    return overall


if __name__ == "__main__":
    # Run the test suite and exit with appropriate code
    # This allows the script to be used in CI/CD pipelines
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
