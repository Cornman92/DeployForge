"""Unit Tests for Portable Apps Module"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from deployforge.portable import (
    PortableAppManager,
    PortableProfile,
    PortableCategory,
    PortableConfig,
    install_portable_apps
)


class TestPortableConfig:
    def test_default_config(self):
        config = PortableConfig()
        assert config.portable_apps_root == "C:\\PortableApps"
        assert config.auto_update_enabled is True

    def test_to_dict(self):
        config = PortableConfig()
        config_dict = config.to_dict()
        assert 'installation' in config_dict
        assert 'apps' in config_dict


class TestPortableAppManager:
    def test_initialization(self, test_image_path):
        manager = PortableAppManager(test_image_path)
        assert isinstance(manager.config, PortableConfig)

    def test_app_catalog_exists(self):
        manager = PortableAppManager(Path("test.wim"))
        assert len(manager.APP_CATALOG) > 0
        assert 'firefox_portable' in manager.APP_CATALOG

    def test_get_apps_by_category(self, test_image_path):
        manager = PortableAppManager(test_image_path)
        browsers = manager.get_apps_by_category(PortableCategory.BROWSER)
        assert len(browsers) > 0
