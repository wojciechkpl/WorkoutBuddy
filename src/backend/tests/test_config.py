import os
import pytest
from app.core.config import get_config, FeatureFlags, ConfigurationManager


def test_base_config_loads():
    config = get_config()
    print(f"Config object: {config}")
    print(f"Config _config: {config._config}")
    assert config.get("database_url")
    assert config.get("app.name") == "Pulse Fitness"


def test_feature_flags_load():
    config = get_config()
    flags = config.get_feature_flags()
    assert isinstance(flags, FeatureFlags)
    assert flags.enable_ml_recommendations is True
    assert hasattr(flags, "enable_sms_notifications")


def test_secret_management(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "supersecret")
    config = ConfigurationManager()
    assert config.get_secret("SECRET_KEY") == "supersecret"


def test_environment_switch(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    config = ConfigurationManager()
    assert config.get_environment().value == "development"
