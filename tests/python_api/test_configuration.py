#!/usr/bin/env python3
"""
Comprehensive Configuration Test Suite for WorkoutBuddy

Tests the hybrid configuration approach:
- API keys from environment variables
- Other settings from config files
- Service auto-enablement
- Module imports and compatibility
"""

import os
import sys
import traceback
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Also set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = str(project_root)


class ConfigurationTestSuite:
    """Test suite for WorkoutBuddy configuration system"""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        try:
            print(f"🧪 Testing: {test_name}")
            test_func()
            print(f"✅ PASSED: {test_name}")
            self.tests_passed += 1
            self.test_results.append((test_name, "PASSED", None))
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"   Error: {str(e)}")
            self.tests_failed += 1
            self.test_results.append((test_name, "FAILED", str(e)))

    def test_environment_variables(self):
        """Test that required environment variables are loaded"""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        posthog_key = os.getenv("POSTHOG_API_KEY")

        assert anthropic_key is not None, "ANTHROPIC_API_KEY not found in environment"
        assert posthog_key is not None, "POSTHOG_API_KEY not found in environment"
        assert anthropic_key != "your-anthropic-api-key-here", (
            "ANTHROPIC_API_KEY is placeholder value"
        )
        assert len(anthropic_key) > 10, "ANTHROPIC_API_KEY appears to be invalid"
        assert posthog_key.startswith("phc_"), (
            "POSTHOG_API_KEY should start with 'phc_'"
        )

    def test_config_loading(self):
        """Test that configuration loads successfully"""
        from ml_backend.app.config import backend_config, load_config

        # Test global config instance
        assert backend_config is not None, "Global backend_config not initialized"

        # Test fresh config loading
        fresh_config = load_config()
        assert fresh_config is not None, "Fresh config loading failed"

        # Test config structure
        assert hasattr(backend_config, "database"), "Config missing database section"
        assert hasattr(backend_config, "app"), "Config missing app section"
        assert hasattr(backend_config, "ai"), "Config missing ai section"
        assert hasattr(backend_config, "analytics"), "Config missing analytics section"

    def test_api_keys_configuration(self):
        """Test that API keys are properly configured"""
        from ml_backend.app.config import backend_config

        # Test AI configuration
        assert backend_config.ai.anthropic_api_key is not None, (
            "Anthropic API key not loaded"
        )
        assert backend_config.ai.enabled == True, (
            "AI service should be enabled when API key is present"
        )

        # Test Analytics configuration
        assert backend_config.analytics.posthog_api_key is not None, (
            "PostHog API key not loaded"
        )
        assert backend_config.analytics.enabled == True, (
            "Analytics should be enabled when API key is present"
        )

    def test_database_configuration(self):
        """Test database configuration and connectivity"""
        from ml_backend.app.config import backend_config
        from sqlalchemy import create_engine, text

        # Test database URL is configured
        db_url = backend_config.database.url
        assert db_url is not None, "Database URL not configured"
        assert len(db_url) > 0, "Database URL is empty"

        # Test database connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1, "Database connection test failed"

    def test_core_imports(self):
        """Test that all core modules can be imported"""
        # Test config import
        from ml_backend.app.config import backend_config

        assert backend_config is not None

        # Test database models
        from ml_backend.app.core.models import Base, User

        assert Base is not None
        assert User is not None

        # Test schemas
        from ml_backend.app.core.schemas import (
            WorkoutPlanRequest,
            CommunityMatchRequest,
        )

        assert WorkoutPlanRequest is not None
        assert CommunityMatchRequest is not None

    def test_ml_service_import(self):
        """Test ML service and related imports"""
        from ml_backend.app.core.model import MLService, community_analytics

        assert MLService is not None, "MLService class not importable"
        assert community_analytics is not None, "community_analytics not available"

        # Test MLService initialization
        ml_service = MLService()
        assert ml_service is not None, "MLService initialization failed"
        assert hasattr(ml_service, "load_models"), (
            "MLService missing load_models method"
        )

    def test_api_endpoints_import(self):
        """Test API endpoints and FastAPI app"""
        from ml_backend.app.api.endpoints import router
        from ml_backend.app.main import app

        assert router is not None, "API router not importable"
        assert app is not None, "FastAPI app not importable"

    def test_configuration_values(self):
        """Test specific configuration values"""
        from ml_backend.app.config import backend_config

        # Test database URL format
        db_url = backend_config.database.url
        assert "postgresql://" in db_url or "sqlite://" in db_url, (
            "Invalid database URL format"
        )

        # Test app configuration
        assert backend_config.app.api_host == "0.0.0.0", "API host should be 0.0.0.0"
        assert backend_config.app.api_port == 8000, "API port should be 8000"

        # Test AI configuration
        assert backend_config.ai.model_name == "claude-3-haiku-20240307", (
            "AI model name incorrect"
        )
        assert backend_config.ai.max_tokens == 500, "AI max tokens incorrect"
        assert backend_config.ai.temperature == 0.7, "AI temperature incorrect"

        # Test ML configuration
        assert hasattr(backend_config.ml, "model_path"), "ML config missing model_path"
        assert backend_config.ml.similarity_algorithm == "cosine", (
            "ML similarity algorithm incorrect"
        )

    def test_hybrid_configuration_approach(self):
        """Test that the hybrid configuration approach works correctly"""
        from ml_backend.app.config import backend_config
        import os

        # API keys should come from environment
        env_anthropic = os.getenv("ANTHROPIC_API_KEY")
        config_anthropic = backend_config.ai.anthropic_api_key
        assert env_anthropic == config_anthropic, (
            "Anthropic API key not loaded from environment"
        )

        env_posthog = os.getenv("POSTHOG_API_KEY")
        config_posthog = backend_config.analytics.posthog_api_key
        assert env_posthog == config_posthog, (
            "PostHog API key not loaded from environment"
        )

        # Other settings should come from config files (hardcoded defaults)
        assert backend_config.app.secret_key == "your-secret-key", (
            "Secret key should be hardcoded default"
        )
        assert backend_config.analytics.posthog_host == "https://app.posthog.com", (
            "PostHog host should be hardcoded"
        )

    def run_all_tests(self):
        """Run all configuration tests"""
        print("🏋️ WorkoutBuddy Configuration Test Suite")
        print("=" * 60)
        print("Testing hybrid configuration approach:")
        print("  • API keys from environment variables")
        print("  • Other settings from config files")
        print("=" * 60)

        # Run all tests
        self.run_test("Environment Variables Loading", self.test_environment_variables)
        self.run_test("Configuration Loading", self.test_config_loading)
        self.run_test("API Keys Configuration", self.test_api_keys_configuration)
        self.run_test("Database Configuration", self.test_database_configuration)
        self.run_test("Core Module Imports", self.test_core_imports)
        self.run_test("ML Service Import", self.test_ml_service_import)
        self.run_test("API Endpoints Import", self.test_api_endpoints_import)
        self.run_test("Configuration Values", self.test_configuration_values)
        self.run_test(
            "Hybrid Configuration Approach", self.test_hybrid_configuration_approach
        )

        # Print summary
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"📊 Total Tests: {self.tests_passed + self.tests_failed}")

        if self.tests_failed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, status, error in self.test_results:
                if status == "FAILED":
                    print(f"   • {test_name}: {error}")

        success_rate = (
            self.tests_passed / (self.tests_passed + self.tests_failed)
        ) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")

        if self.tests_failed == 0:
            print("\n🎉 ALL TESTS PASSED! Configuration is working correctly.")
            return True
        else:
            print(
                f"\n⚠️  {self.tests_failed} test(s) failed. Please check the configuration."
            )
            return False


def main():
    """Main test runner"""
    test_suite = ConfigurationTestSuite()
    success = test_suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
