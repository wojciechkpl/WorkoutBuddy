"""
Configuration Management System for Pulse Fitness
Handles environment variables, configuration files, secret management, and feature flags
"""

import os
import json
import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import logging
from functools import lru_cache
import secrets
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment enumeration"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration"""

    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    migration_auto: bool = True


@dataclass
class RedisConfig:
    """Redis configuration"""

    url: str
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5


@dataclass
class SecurityConfig:
    """Security configuration"""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    cors_origins: List[str] = field(default_factory=list)
    cors_allow_credentials: bool = True


@dataclass
class MLConfig:
    """Machine Learning configuration"""

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    vector_db_url: Optional[str] = None
    vector_db_api_key: Optional[str] = None
    model_cache_dir: str = "./models"
    embedding_dimensions: int = 1536
    similarity_threshold: float = 0.7
    max_recommendations: int = 10
    batch_size: int = 32


@dataclass
class ExternalServicesConfig:
    """External services configuration"""

    email_service_url: Optional[str] = None
    email_service_api_key: Optional[str] = None
    push_notification_url: Optional[str] = None
    push_notification_api_key: Optional[str] = None
    file_storage_url: Optional[str] = None
    file_storage_api_key: Optional[str] = None
    sms_service_url: Optional[str] = None
    sms_service_api_key: Optional[str] = None


@dataclass
class FeatureFlags:
    """Feature flags configuration"""

    # Core Features
    enable_ml_recommendations: bool = True
    enable_social_features: bool = True
    enable_safety_moderation: bool = True

    # Communication Features
    enable_push_notifications: bool = True
    enable_email_notifications: bool = True
    enable_sms_notifications: bool = False

    # File and Media Features
    enable_file_upload: bool = True
    enable_image_processing: bool = True
    enable_video_upload: bool = False

    # Analytics and Monitoring
    enable_analytics: bool = True
    enable_debug_mode: bool = False
    enable_performance_monitoring: bool = True

    # Advanced Features
    enable_ai_coaching: bool = True
    enable_voice_commands: bool = False
    enable_ar_workouts: bool = False

    # Social Features
    enable_friend_system: bool = True
    enable_challenges: bool = True
    enable_leaderboards: bool = True
    enable_group_workouts: bool = True

    # Safety Features
    enable_content_moderation: bool = True
    enable_user_verification: bool = True
    enable_reporting_system: bool = True
    enable_blocking_system: bool = True

    # Premium Features
    enable_premium_workouts: bool = True
    enable_personal_training: bool = False
    enable_nutrition_tracking: bool = True
    enable_advanced_analytics: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration"""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = False


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""

    enable_health_checks: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 9090
    health_check_interval: int = 30
    performance_monitoring: bool = True


class ConfigurationManager:
    """Main configuration manager"""

    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._secrets: Dict[str, str] = {}
        self._feature_flags: FeatureFlags = FeatureFlags()
        self._environment: Environment = Environment.DEVELOPMENT
        self._encryption_key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None

        # Load configuration
        self._load_environment()
        self._load_config_files()
        self._load_secrets()
        self._setup_encryption()
        self._validate_configuration()

    def _load_environment(self):
        """Load environment variables"""
        self._environment = Environment(os.getenv("ENVIRONMENT", "development"))
        logger.info(f"Loaded environment: {self._environment.value}")

    def _load_config_files(self):
        """Load configuration from files"""
        # Look for config in multiple possible locations
        possible_config_dirs = [
            Path("config"),  # Current directory
            Path("src/backend/config"),  # Backend directory
            Path(__file__).parent.parent.parent / "config",  # Relative to this file
        ]

        config_dir = None
        for dir_path in possible_config_dirs:
            logger.info(
                f"Checking config directory: {dir_path} (exists: {dir_path.exists()})"
            )
            if dir_path.exists():
                config_dir = dir_path
                logger.info(f"Found config directory: {config_dir}")
                break

        if not config_dir:
            logger.warning("No config directory found, using defaults")
            return

        # Load base configuration
        base_config_path = config_dir / "config.yaml"
        logger.info(f"Loading base config from: {base_config_path}")
        if base_config_path.exists():
            with open(base_config_path, "r") as f:
                config_data = yaml.safe_load(f)
                logger.info(f"Loaded config data: {config_data}")
                self._config.update(config_data)
        else:
            logger.warning(f"Base config file not found: {base_config_path}")

        # Load environment-specific configuration
        env_config_path = config_dir / f"config.{self._environment.value}.yaml"
        logger.info(f"Loading env config from: {env_config_path}")
        if env_config_path.exists():
            with open(env_config_path, "r") as f:
                env_config = yaml.safe_load(f)
                logger.info(f"Loaded env config data: {env_config}")
                self._config.update(env_config)

        # Load feature flags
        feature_flags_path = config_dir / "feature_flags.yaml"
        if feature_flags_path.exists():
            with open(feature_flags_path, "r") as f:
                flags_data = yaml.safe_load(f)
                self._feature_flags = FeatureFlags(**flags_data)

        logger.info("Configuration files loaded")

    def _load_secrets(self):
        """Load secrets from environment and files"""
        # Load from environment variables
        secret_prefixes = ["SECRET_", "API_KEY_", "PASSWORD_", "TOKEN_"]
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in secret_prefixes):
                self._secrets[key] = value

        # Load from secrets file
        secrets_file = Path("config/secrets.yaml")
        if secrets_file.exists():
            with open(secrets_file, "r") as f:
                secrets_data = yaml.safe_load(f)
                if secrets_data:
                    self._secrets.update(secrets_data)

        logger.info(f"Loaded {len(self._secrets)} secrets")

    def _setup_encryption(self):
        """Setup encryption for sensitive data"""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if encryption_key:
            self._encryption_key = encryption_key.encode()
            self._fernet = Fernet(self._encryption_key)
        else:
            # Generate a new key for development
            if self._environment == Environment.DEVELOPMENT:
                self._encryption_key = Fernet.generate_key()
                self._fernet = Fernet(self._encryption_key)
                logger.warning("Generated new encryption key for development")

    def _validate_configuration(self):
        """Validate configuration"""
        required_keys = ["database_url", "redis_url", "secret_key"]

        for key in required_keys:
            if not self.get(key):
                raise ValueError(f"Required configuration key '{key}' not found")

        logger.info("Configuration validation passed")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Check environment variables first
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return env_value

        # Check configuration
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_secret(self, key: str, default: Any = None) -> Any:
        """Get secret value"""
        return self._secrets.get(key, default)

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        return DatabaseConfig(
            url=self.get("database_url"),
            pool_size=self.get("database.pool_size", 10),
            max_overflow=self.get("database.max_overflow", 20),
            pool_timeout=self.get("database.pool_timeout", 30),
            pool_recycle=self.get("database.pool_recycle", 3600),
            echo=self.get("database.echo", False),
            migration_auto=self.get("database.migration_auto", True),
        )

    def get_redis_config(self) -> RedisConfig:
        """Get Redis configuration"""
        redis_url = self.get("redis_url", "redis://localhost:6379/0")
        return RedisConfig(
            url=redis_url,
            host=self.get("redis.host", "localhost"),
            port=self.get("redis.port", 6379),
            db=self.get("redis.db", 0),
            password=self.get("redis.password"),
            ssl=self.get("redis.ssl", False),
            max_connections=self.get("redis.max_connections", 10),
            socket_timeout=self.get("redis.socket_timeout", 5),
            socket_connect_timeout=self.get("redis.socket_connect_timeout", 5),
        )

    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return SecurityConfig(
            secret_key=self.get_secret("SECRET_KEY") or self.get("secret_key"),
            algorithm=self.get("security.algorithm", "HS256"),
            access_token_expire_minutes=self.get(
                "security.access_token_expire_minutes", 30
            ),
            refresh_token_expire_days=self.get("security.refresh_token_expire_days", 7),
            password_min_length=self.get("security.password_min_length", 8),
            password_require_special=self.get(
                "security.password_require_special", True
            ),
            password_require_numbers=self.get(
                "security.password_require_numbers", True
            ),
            password_require_uppercase=self.get(
                "security.password_require_uppercase", True
            ),
            rate_limit_requests=self.get("security.rate_limit_requests", 100),
            rate_limit_window=self.get("security.rate_limit_window", 3600),
            cors_origins=self.get("security.cors_origins", []),
            cors_allow_credentials=self.get("security.cors_allow_credentials", True),
        )

    def get_ml_config(self) -> MLConfig:
        """Get ML configuration"""
        return MLConfig(
            openai_api_key=self.get_secret("OPENAI_API_KEY"),
            anthropic_api_key=self.get_secret("ANTHROPIC_API_KEY"),
            vector_db_url=self.get("ml.vector_db_url"),
            vector_db_api_key=self.get_secret("VECTOR_DB_API_KEY"),
            model_cache_dir=self.get("ml.model_cache_dir", "./models"),
            embedding_dimensions=self.get("ml.embedding_dimensions", 1536),
            similarity_threshold=self.get("ml.similarity_threshold", 0.7),
            max_recommendations=self.get("ml.max_recommendations", 10),
            batch_size=self.get("ml.batch_size", 32),
        )

    def get_external_services_config(self) -> ExternalServicesConfig:
        """Get external services configuration"""
        return ExternalServicesConfig(
            email_service_url=self.get("external.email_service_url"),
            email_service_api_key=self.get_secret("EMAIL_SERVICE_API_KEY"),
            push_notification_url=self.get("external.push_notification_url"),
            push_notification_api_key=self.get_secret("PUSH_NOTIFICATION_API_KEY"),
            file_storage_url=self.get("external.file_storage_url"),
            file_storage_api_key=self.get_secret("FILE_STORAGE_API_KEY"),
            sms_service_url=self.get("external.sms_service_url"),
            sms_service_api_key=self.get_secret("SMS_SERVICE_API_KEY"),
        )

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return LoggingConfig(
            level=self.get("logging.level", "INFO"),
            format=self.get(
                "logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            file_path=self.get("logging.file_path"),
            max_file_size=self.get("logging.max_file_size", 10 * 1024 * 1024),
            backup_count=self.get("logging.backup_count", 5),
            enable_console=self.get("logging.enable_console", True),
            enable_file=self.get("logging.enable_file", False),
        )

    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        return MonitoringConfig(
            enable_health_checks=self.get("monitoring.enable_health_checks", True),
            enable_metrics=self.get("monitoring.enable_metrics", True),
            enable_tracing=self.get("monitoring.enable_tracing", False),
            metrics_port=self.get("monitoring.metrics_port", 9090),
            health_check_interval=self.get("monitoring.health_check_interval", 30),
            performance_monitoring=self.get("monitoring.performance_monitoring", True),
        )

    def get_feature_flags(self) -> FeatureFlags:
        """Get feature flags"""
        return self._feature_flags

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return getattr(self._feature_flags, feature_name, False)

    def encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not self._fernet:
            raise ValueError("Encryption not configured")
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not self._fernet:
            raise ValueError("Encryption not configured")
        return self._fernet.decrypt(encrypted_value.encode()).decode()

    def get_environment(self) -> Environment:
        """Get current environment"""
        return self._environment

    def is_development(self) -> bool:
        """Check if running in development"""
        return self._environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self._environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self._environment == Environment.TESTING

    def reload(self):
        """Reload configuration"""
        self._config.clear()
        self._secrets.clear()
        self._load_config_files()
        self._load_secrets()
        self._validate_configuration()
        logger.info("Configuration reloaded")


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


@lru_cache()
def get_config() -> ConfigurationManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().get_database_config()


def get_redis_config() -> RedisConfig:
    """Get Redis configuration"""
    return get_config().get_redis_config()


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return get_config().get_security_config()


def get_ml_config() -> MLConfig:
    """Get ML configuration"""
    return get_config().get_ml_config()


def get_external_services_config() -> ExternalServicesConfig:
    """Get external services configuration"""
    return get_config().get_external_services_config()


def get_logging_config() -> LoggingConfig:
    """Get logging configuration"""
    return get_config().get_logging_config()


def get_monitoring_config() -> MonitoringConfig:
    """Get monitoring configuration"""
    return get_config().get_monitoring_config()


def get_feature_flags() -> FeatureFlags:
    """Get feature flags"""
    return get_config().get_feature_flags()


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return get_config().is_feature_enabled(feature_name)
