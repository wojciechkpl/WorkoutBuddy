"""
WorkoutBuddy Configuration Management System

This module provides a comprehensive configuration management system for the WorkoutBuddy
AI-powered fitness platform. It handles:

- Environment-aware configuration loading (development vs production)
- Machine learning hyperparameters and model settings
- AI service configuration (Anthropic Claude models)
- Analytics and tracking settings (PostHog integration)
- A/B testing experiment parameters
- Database connection settings with Railway deployment support

The configuration system supports:
1. YAML-based config files for local development
2. Environment variables for production deployment
3. Railway cloud platform integration
4. Fallback defaults for all settings

Key Features:
- Type-safe configuration with dataclasses
- Environment variable override support
- Validation and error handling
- ML hyperparameter centralization
- Feature flag management

Author: WorkoutBuddy Team
Version: 2.1.0
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class DatabaseConfig:
    """
    Database connection configuration.

    Supports both SQLite (development) and PostgreSQL (production).
    Automatically detects Railway environment and configures accordingly.

    Attributes:
        url: Database connection URL (SQLite file path or PostgreSQL connection string)
    """

    url: str = "postgresql://wojciechkowalinski@localhost/workoutbuddy"


@dataclass
class AppConfig:
    """
    Core application configuration settings.

    Controls basic FastAPI server behavior and security settings.

    Attributes:
        secret_key: JWT signing key and general application secret
        api_host: Host interface to bind the server to
        api_port: Port number for the API server
    """

    secret_key: str = "your-secret-key"
    api_host: str = "0.0.0.0"
    api_port: int = 8000


@dataclass
class LoggingConfig:
    """
    Application logging configuration.

    Controls log verbosity and output formatting across the application.

    Attributes:
        level: Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """

    level: str = "INFO"


@dataclass
class AIConfig:
    """
    AI and Machine Learning service configuration.

    Manages Anthropic Claude integration and AI feature hyperparameters.
    All ML model settings are centralized here for easy tuning.

    Attributes:
        anthropic_api_key: Anthropic API authentication key
        enabled: Whether AI features are active (auto-detected from API key)
        model_name: Claude model to use (claude-3-haiku-20240307 recommended for cost efficiency)
        max_tokens: Maximum tokens per AI response
        temperature: Model creativity/randomness (0.0-1.0)
        challenge_creativity: How creative challenge generation should be
        challenge_difficulty_range: Min/max difficulty levels for challenges
        compatibility_threshold: Minimum similarity score for community matching
        max_matches: Maximum number of community matches to return
        encouragement_tone_variety: Variation in encouragement message tone
        personalization_weight: How much to personalize messages to user history
    """

    anthropic_api_key: Optional[str] = os.getenv(
        "ANTHROPIC_API_KEY"
    )  # Always load from environment variables
    enabled: bool = field(
        default_factory=lambda: bool(os.getenv("ANTHROPIC_API_KEY"))
    )  # Auto-enable when API key is present
    # Claude Model Configuration
    model_name: str = "claude-3-haiku-20240307"
    max_tokens: int = 500
    temperature: float = 0.7
    # Challenge Generation Hyperparameters
    challenge_creativity: float = 0.8
    challenge_difficulty_range: List[int] = field(default_factory=lambda: [1, 5])
    # Community Matching Hyperparameters
    compatibility_threshold: float = 0.7
    max_matches: int = 10
    # Encouragement Generation
    encouragement_tone_variety: float = 0.6
    personalization_weight: float = 0.8


@dataclass
class AnalyticsConfig:
    """
    Analytics and user tracking configuration.

    Manages PostHog integration for user behavior analytics and event tracking.

    Attributes:
        posthog_api_key: PostHog project API key
        posthog_host: PostHog instance URL (cloud or self-hosted)
        enabled: Whether analytics tracking is active
        batch_size: Number of events to batch before sending
        flush_interval: Seconds between automatic event flushes
        max_retries: Maximum retry attempts for failed analytics calls
    """

    posthog_api_key: Optional[str] = os.getenv("POSTHOG_API_KEY")
    posthog_host: str = "https://app.posthog.com"
    enabled: bool = field(default_factory=lambda: bool(os.getenv("POSTHOG_API_KEY")))
    # Event Tracking Configuration
    batch_size: int = 100
    flush_interval: int = 30  # seconds
    max_retries: int = 3


@dataclass
class ABTestingConfig:
    """
    A/B Testing experimentation framework configuration.

    Controls experiment setup, user assignment, and statistical analysis.

    Attributes:
        enabled: Whether A/B testing is active
        default_traffic_allocation: Default split for new experiments (0.0-1.0)
        minimum_sample_size: Minimum users required for statistical significance
        confidence_level: Statistical confidence level for results (0.0-1.0)
        hash_seed: Seed for consistent user assignment hashing
        active_experiments: List of currently running experiment IDs
    """

    enabled: bool = True
    # Experiment Configuration
    default_traffic_allocation: float = 0.5
    minimum_sample_size: int = 100
    confidence_level: float = 0.95
    # Hash Configuration for User Assignment
    hash_seed: str = "workoutbuddy-experiments"
    # Active Experiments
    active_experiments: List[str] = field(
        default_factory=lambda: [
            "ai_challenges_v1",
            "ai_community_matching_v1",
            "encouragement_frequency_v1",
        ]
    )


@dataclass
class MLConfig:
    """
    Machine Learning algorithms and hyperparameters configuration.

    Centralizes all ML model settings for community matching, recommendations,
    and analytics. This enables easy hyperparameter tuning without code changes.

    Attributes:
        model_path: Path to saved ML models
        similarity_algorithm: Algorithm for computing user similarity
        feature_weights: Importance weights for different user features
        recommendation_model: Type of recommendation algorithm to use
        n_recommendations: Number of recommendations to generate
        min_user_interactions: Minimum interactions required for recommendations
        cohort_window_days: Time window for cohort analysis
        retention_analysis_periods: Days to analyze for retention metrics
        anomaly_threshold: Standard deviations for anomaly detection
        min_data_points: Minimum data points required for analysis
    """

    # Model Storage
    model_path: str = "./models/model.pt"
    # Community Matching ML Parameters
    similarity_algorithm: str = "cosine"  # cosine, jaccard, euclidean
    feature_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "goal_type": 0.3,
            "activity_level": 0.2,
            "schedule_compatibility": 0.2,
            "engagement_score": 0.15,
            "location_proximity": 0.15,
        }
    )
    # Recommendation Engine
    recommendation_model: str = "collaborative_filtering"
    n_recommendations: int = 5
    min_user_interactions: int = 5
    # Cohort Analysis
    cohort_window_days: int = 30
    retention_analysis_periods: List[int] = field(
        default_factory=lambda: [7, 14, 30, 90]
    )
    # Anomaly Detection
    anomaly_threshold: float = 2.0  # Standard deviations
    min_data_points: int = 10


@dataclass
class BackendConfig:
    """
    Master configuration container for all WorkoutBuddy backend settings.

    Aggregates all configuration sections into a single, type-safe object
    that can be imported and used throughout the application.

    Attributes:
        database: Database connection settings
        app: Core application settings
        logging: Logging configuration
        ai: AI service and ML hyperparameters
        analytics: Analytics and tracking settings
        ab_testing: A/B testing experiment configuration
        ml: Machine learning algorithm settings
    """

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    app: AppConfig = field(default_factory=AppConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    analytics: AnalyticsConfig = field(default_factory=AnalyticsConfig)
    ab_testing: ABTestingConfig = field(default_factory=ABTestingConfig)
    ml: MLConfig = field(default_factory=MLConfig)


def load_config() -> BackendConfig:
    """
    Load and construct the complete application configuration.

    This function implements a sophisticated configuration loading strategy:
    1. Railway production environment (environment variables)
    2. Local development with config.yaml file
    3. Environment variable overrides
    4. Sensible defaults

    The loading order ensures that:
    - Production deployments work out-of-the-box on Railway
    - Local development is easy with YAML files
    - Sensitive values (API keys) are always from environment variables
    - Missing configurations don't break the application

    Returns:
        BackendConfig: Complete, validated configuration object

    Raises:
        Exception: Logs warnings for configuration issues but doesn't fail
    """

    # Railway Production Environment Configuration
    # ============================================
    # Railway provides specific environment variables that we can detect
    # to automatically configure the application for production deployment
    if os.getenv("RAILWAY_ENVIRONMENT"):
        # Construct PostgreSQL URL from Railway environment variables
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            # Railway PostgreSQL format - build URL from components
            db_host = os.getenv("PGHOST", "localhost")
            db_port = os.getenv("PGPORT", "5432")
            db_name = os.getenv("PGDATABASE", "workoutbuddy")
            db_user = os.getenv("PGUSER", "postgres")
            db_password = os.getenv("PGPASSWORD", "")
            database_url = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )

        # AI service configuration - auto-enable if API key is present
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        ai_enabled = bool(anthropic_api_key)

        # Analytics configuration - auto-enable if API key is present
        posthog_api_key = os.getenv("POSTHOG_API_KEY")
        analytics_enabled = bool(posthog_api_key)

        return BackendConfig(
            database=DatabaseConfig(url=database_url),
            app=AppConfig(
                secret_key=os.getenv("SECRET_KEY", "railway-secret-key"),
                api_host="0.0.0.0",
                api_port=int(os.getenv("PORT", 8000)),
            ),
            logging=LoggingConfig(level=os.getenv("LOG_LEVEL", "INFO")),
            ai=AIConfig(
                anthropic_api_key=anthropic_api_key,
                enabled=ai_enabled,
                model_name=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("AI_MAX_TOKENS", "500")),
            ),
            analytics=AnalyticsConfig(
                posthog_api_key=posthog_api_key,
                posthog_host=os.getenv("POSTHOG_HOST", "https://app.posthog.com"),
                enabled=analytics_enabled,
            ),
        )

    # Local Development Configuration
    # ===============================
    # For local development, try to load from config.yaml file
    # while still allowing environment variable overrides
    try:
        config_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../config.yaml")
        )
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)

            # Environment variables always take precedence over file config
            # This allows developers to override specific settings without
            # modifying the config file
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            posthog_api_key = os.getenv("POSTHOG_API_KEY")

            backend_data = config_data.get("backend", {})

            return BackendConfig(
                database=DatabaseConfig(
                    url=backend_data.get("database", {}).get(
                        "url", "sqlite:///./workoutbuddy.db"
                    )
                ),
                app=AppConfig(
                    secret_key=backend_data.get("app", {}).get(
                        "secret_key", "dev-secret-key"
                    ),
                    api_host=backend_data.get("app", {}).get("api_host", "0.0.0.0"),
                    api_port=backend_data.get("app", {}).get("api_port", 8000),
                ),
                logging=LoggingConfig(
                    level=backend_data.get("logging", {}).get("level", "INFO")
                ),
                ai=AIConfig(
                    anthropic_api_key=anthropic_api_key,
                    enabled=bool(anthropic_api_key),
                    **backend_data.get("ai", {}),
                ),
                analytics=AnalyticsConfig(
                    posthog_api_key=posthog_api_key,
                    enabled=bool(posthog_api_key),
                    **backend_data.get("analytics", {}),
                ),
                ab_testing=ABTestingConfig(**backend_data.get("ab_testing", {})),
                ml=MLConfig(**backend_data.get("ml", {})),
            )
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")

    # Fallback Default Configuration
    # ==============================
    # If no config file exists or Railway environment is not detected,
    # fall back to defaults with environment variable support
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    posthog_api_key = os.getenv("POSTHOG_API_KEY")

    return BackendConfig(
        ai=AIConfig(
            anthropic_api_key=anthropic_api_key, enabled=bool(anthropic_api_key)
        ),
        analytics=AnalyticsConfig(
            posthog_api_key=posthog_api_key,
            posthog_host=os.getenv("POSTHOG_HOST", "https://app.posthog.com"),
            enabled=bool(posthog_api_key),
        ),
    )


# Global configuration instance
# =============================
# This is the main configuration object that should be imported and used
# throughout the application. It's loaded once at startup for efficiency.
backend_config = load_config()
