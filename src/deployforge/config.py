"""Configuration management for DeployForge."""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for DeployForge."""

    DEFAULT_CONFIG = {
        'mount': {
            'default_dir': None,  # Use temp dir if None
            'auto_cleanup': True,
        },
        'logging': {
            'level': 'INFO',
            'file': None,
        },
        'wim': {
            'default_index': 1,
            'compression': 'maximum',  # none, fast, maximum, lzx, xpress
        },
        'iso': {
            'preserve_permissions': True,
        },
        'ppkg': {
            'validate_xml': True,
        },
    }

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load(config_path)

    def load(self, config_path: Path) -> None:
        """
        Load configuration from a YAML file.

        Args:
            config_path: Path to configuration file
        """
        if not YAML_AVAILABLE:
            logger.warning("PyYAML not available, using default configuration")
            return

        config_path = Path(config_path)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return

        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)

            if user_config:
                self._merge_config(user_config)

            logger.info(f"Loaded configuration from {config_path}")

        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")

    def save(self, config_path: Path) -> None:
        """
        Save configuration to a YAML file.

        Args:
            config_path: Path to save configuration
        """
        if not YAML_AVAILABLE:
            logger.error("PyYAML not available, cannot save configuration")
            return

        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)

            logger.info(f"Saved configuration to {config_path}")

        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")

    def _merge_config(self, user_config: Dict[str, Any]) -> None:
        """Merge user configuration with defaults."""
        def merge_dict(base: dict, updates: dict) -> None:
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        merge_dict(self.config, user_config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'mount.default_dir')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'mount.default_dir')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.

        Environment variables:
        - DEPLOYFORGE_CONFIG: Path to config file
        - DEPLOYFORGE_LOG_LEVEL: Logging level
        - DEPLOYFORGE_MOUNT_DIR: Default mount directory

        Returns:
            Config instance
        """
        config_path = os.environ.get('DEPLOYFORGE_CONFIG')
        config = cls(Path(config_path) if config_path else None)

        # Override with environment variables
        if log_level := os.environ.get('DEPLOYFORGE_LOG_LEVEL'):
            config.set('logging.level', log_level)

        if mount_dir := os.environ.get('DEPLOYFORGE_MOUNT_DIR'):
            config.set('mount.default_dir', mount_dir)

        return config

    def __repr__(self) -> str:
        """String representation."""
        return f"Config(config_path={self.config_path})"
