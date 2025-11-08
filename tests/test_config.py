"""Tests for configuration management."""

import pytest
from deployforge.config import Config


def test_default_config():
    """Test default configuration."""
    config = Config()
    assert config.get('mount.auto_cleanup') is True
    assert config.get('wim.default_index') == 1


def test_get_with_default():
    """Test getting config value with default."""
    config = Config()
    assert config.get('nonexistent.key', 'default_value') == 'default_value'


def test_set_config():
    """Test setting configuration value."""
    config = Config()
    config.set('mount.default_dir', '/tmp/test')
    assert config.get('mount.default_dir') == '/tmp/test'


def test_nested_config():
    """Test nested configuration access."""
    config = Config()
    config.set('custom.nested.value', 42)
    assert config.get('custom.nested.value') == 42
