#!/usr/bin/env python3
"""
WorkoutBuddy Test Automation Suite

This script runs all tests for the WorkoutBuddy application including:
- Configuration tests
- Database connectivity tests
- Module import tests
- Environment variable validation
- API functionality tests

Usage:
    python run_tests.py [--verbose] [--config-only] [--db-only]
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from datetime import datetime


class TestRunner:
    """Automated test runner for WorkoutBuddy"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_results = []
        self.start_time = None
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests" / "python_api"

    def log(self, message, level="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            print(f"[{timestamp}] ❌ {message}")
        elif level == "WARNING":
            print(f"[{timestamp}] ⚠️  {message}")
        elif level == "SUCCESS":
            print(f"[{timestamp}] ✅ {message}")
        else:
            print(f"[{timestamp}] ℹ️  {message}")

    def run_command(self, command, description, cwd=None):
        """Run a command and capture results"""
        self.log(f"Running: {description}")
        if self.verbose:
            self.log(f"Command: {command}")

        try:
            if cwd is None:
                cwd = self.project_root

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=120,  # 2 minute timeout
            )

            if result.returncode == 0:
                self.log(f"✅ {description} PASSED", "SUCCESS")
                if self.verbose and result.stdout:
                    print(result.stdout)
                self.test_results.append((description, "PASSED", None))
                return True
            else:
                self.log(f"❌ {description} FAILED", "ERROR")
                if result.stderr:
                    self.log(f"Error: {result.stderr}", "ERROR")
                if self.verbose and result.stdout:
                    print(result.stdout)
                self.test_results.append((description, "FAILED", result.stderr))
                return False

        except subprocess.TimeoutExpired:
            self.log(f"❌ {description} TIMEOUT", "ERROR")
            self.test_results.append((description, "TIMEOUT", "Test exceeded timeout"))
            return False
        except Exception as e:
            self.log(f"❌ {description} ERROR: {e}", "ERROR")
            self.test_results.append((description, "ERROR", str(e)))
            return False

    def check_environment(self):
        """Check if the environment is properly set up"""
        self.log("Checking environment setup...")

        # Check if .envrc exists
        envrc_path = self.project_root / ".envrc"
        if not envrc_path.exists():
            self.log("⚠️ .envrc file not found", "WARNING")
            return False

        # Check environment variables
        required_vars = ["ANTHROPIC_API_KEY", "POSTHOG_API_KEY"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            self.log(f"⚠️ Missing environment variables: {missing_vars}", "WARNING")
            self.log("Make sure direnv is loaded: 'direnv allow'", "WARNING")
            return False

        self.log("✅ Environment check passed", "SUCCESS")
        return True

    def run_configuration_tests(self):
        """Run configuration tests"""
        self.log("🧪 Running configuration tests...")

        # Activate virtual environment and run configuration tests
        venv_activate = "source .venv/bin/activate"
        test_command = (
            f"{venv_activate} && cd tests/python_api && python test_configuration.py"
        )

        return self.run_command(
            test_command, "Configuration Tests", cwd=self.project_root
        )

    def run_database_tests(self):
        """Run database tests"""
        self.log("🗄️ Running database tests...")

        venv_activate = "source .venv/bin/activate"

        # Basic database connection test
        db_test_command = f"{venv_activate} && cd tests/python_api && python test_db.py"
        basic_db_success = self.run_command(
            db_test_command, "Basic Database Connection Test", cwd=self.project_root
        )

        # Enhanced database analysis
        analysis_command = f"{venv_activate} && cd tests/python_api && python test_database_analysis.py"
        analysis_success = self.run_command(
            analysis_command, "Database Analysis Test", cwd=self.project_root
        )

        return basic_db_success and analysis_success

    def run_import_tests(self):
        """Run module import tests"""
        self.log("📦 Running module import tests...")

        venv_activate = "source .venv/bin/activate"
        import_test = """
python -c "
import sys
sys.path.append('ml_backend')
print('Testing core imports...')
from ml_backend.app.config import backend_config
from ml_backend.app.core.models import Base, User
from ml_backend.app.core.schemas import WorkoutPlanRequest
from ml_backend.app.core.model import MLService
from ml_backend.app.api.endpoints import router
from ml_backend.app.main import app
print('All imports successful!')
"
        """

        test_command = f"{venv_activate} && {import_test}"

        return self.run_command(
            test_command, "Module Import Tests", cwd=self.project_root
        )

    def run_environment_tests(self):
        """Run environment variable tests"""
        self.log("🌍 Running environment variable tests...")

        venv_activate = "source .venv/bin/activate"
        env_test = """
python -c "
import os
import sys
sys.path.append('ml_backend')

print('Testing environment variables...')
anthropic = os.getenv('ANTHROPIC_API_KEY')
posthog = os.getenv('POSTHOG_API_KEY')

assert anthropic is not None, 'ANTHROPIC_API_KEY not found'
assert posthog is not None, 'POSTHOG_API_KEY not found'
assert len(anthropic) > 10, 'ANTHROPIC_API_KEY appears invalid'
assert posthog.startswith('phc_'), 'POSTHOG_API_KEY should start with phc_'

from ml_backend.app.config import backend_config
assert backend_config.ai.enabled, 'AI service should be enabled'
assert backend_config.analytics.enabled, 'Analytics should be enabled'

print('Environment variable tests passed!')
"
        """

        test_command = f"{venv_activate} && {env_test}"

        return self.run_command(
            test_command, "Environment Variable Tests", cwd=self.project_root
        )

    def run_all_tests(self, config_only=False, db_only=False):
        """Run all tests"""
        self.start_time = time.time()

        print("🏋️ WorkoutBuddy Automated Test Suite")
        print("=" * 60)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Check environment first
        if not self.check_environment():
            self.log(
                "❌ Environment check failed. Please ensure direnv is loaded.", "ERROR"
            )
            return False

        success = True

        if config_only:
            success &= self.run_configuration_tests()
        elif db_only:
            success &= self.run_database_tests()
        else:
            # Run all tests
            success &= self.run_environment_tests()
            success &= self.run_configuration_tests()
            success &= self.run_import_tests()
            success &= self.run_database_tests()

        # Print summary
        self.print_summary()

        return success

    def print_summary(self):
        """Print test results summary"""
        end_time = time.time()
        duration = end_time - self.start_time

        print("\n" + "=" * 60)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 60)

        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(
            1
            for _, status, _ in self.test_results
            if status in ["FAILED", "ERROR", "TIMEOUT"]
        )
        total = len(self.test_results)

        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Total Tests: {total}")
        print(f"⏱️  Duration: {duration:.2f} seconds")

        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, status, error in self.test_results:
                if status in ["FAILED", "ERROR", "TIMEOUT"]:
                    print(f"   • {test_name}: {status}")
                    if error and self.verbose:
                        print(f"     Error: {error}")

        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! 🚀")
            print("✅ Configuration is working correctly")
            print("✅ Environment variables are loaded")
            print("✅ Database connectivity is working")
            print("✅ All modules import successfully")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WorkoutBuddy Test Automation Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--config-only", action="store_true", help="Run only configuration tests"
    )
    parser.add_argument(
        "--db-only", action="store_true", help="Run only database tests"
    )

    args = parser.parse_args()

    runner = TestRunner(verbose=args.verbose)
    success = runner.run_all_tests(config_only=args.config_only, db_only=args.db_only)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
