#!/usr/bin/env python3
"""
Script to start Jupyter notebook with WorkoutBuddy database environment
"""

import os
import sys
import subprocess

# Ensure we can import from the app
sys.path.append("ml_backend/app")

try:
    from config import backend_config

    DATABASE_URL = backend_config.database.url
except ImportError:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workoutbuddy.db")


def main():
    # Set environment variables
    os.environ["DATABASE_URL"] = DATABASE_URL

    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ["PYTHONPATH"] = current_dir

    print("🚀 Starting Jupyter Notebook for WorkoutBuddy Database Exploration")
    print(f"📁 Working directory: {current_dir}")
    print(f"🔗 Database: {DATABASE_URL}")
    print("\n📊 Available notebooks:")
    print("- workoutbuddy_exploration.ipynb: Comprehensive database analysis")
    print("\n🌐 Jupyter will open in your browser at http://localhost:8888")
    print("💡 Use Ctrl+C to stop the server")
    print("-" * 60)

    try:
        # Start Jupyter notebook
        subprocess.run(
            [
                sys.executable,
                "-m",
                "jupyter",
                "notebook",
                "--ip=127.0.0.1",
                "--port=8888",
                "--no-browser",
                "--allow-root",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Jupyter notebook server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Jupyter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
