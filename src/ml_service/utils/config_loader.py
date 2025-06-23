"""
Configuration loader for ML service
"""

import os
from typing import Any

import yaml


class ConfigLoader:
    """Load and manage ML service configuration"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "ml_config.yaml"
            )
        self.config_path = config_path
        self._config = None

    def load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file"""
        if self._config is None:
            with open(self.config_path) as file:
                self._config = yaml.safe_load(file)
        return self._config

    def get_model_config(self, model_name: str) -> dict[str, Any]:
        """Get configuration for a specific model"""
        config = self.load_config()
        return config.get("models", {}).get(model_name, {})

    def get_feature_config(self, feature_type: str) -> list:
        """Get feature configuration"""
        config = self.load_config()
        return config.get("features", {}).get(feature_type, [])

    def get_data_processing_config(self) -> dict[str, Any]:
        """Get data processing configuration"""
        config = self.load_config()
        return config.get("data_processing", {})

    def get_model_persistence_config(self) -> dict[str, Any]:
        """Get model persistence configuration"""
        config = self.load_config()
        return config.get("model_persistence", {})
