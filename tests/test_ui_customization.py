"""
Unit Tests for UI Customization Module

Tests for ui_customization.py covering UICustomizer class,
profiles, configurations, and all customization methods.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from deployforge.ui_customization import (
    UICustomizer,
    UIProfile,
    ThemeMode,
    TaskbarAlignment,
    ExplorerView,
    UICustomizationConfig,
    customize_ui
)


class TestUICustomizationConfig:
    """Test UICustomizationConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = UICustomizationConfig()

        assert config.windows10_context_menu is True
        assert config.taskbar_alignment == TaskbarAlignment.LEFT
        assert config.theme_mode == ThemeMode.DARK
        assert config.show_file_extensions is True

    def test_to_dict(self):
        """Test configuration serialization"""
        config = UICustomizationConfig()
        config_dict = config.to_dict()

        assert 'context_menu' in config_dict
        assert 'taskbar' in config_dict
        assert 'explorer' in config_dict
        assert 'theme' in config_dict

        assert config_dict['theme']['mode'] == 'dark'
        assert config_dict['taskbar']['alignment'] == 'left'

    def test_custom_config(self):
        """Test custom configuration"""
        config = UICustomizationConfig()
        config.theme_mode = ThemeMode.LIGHT
        config.taskbar_alignment = TaskbarAlignment.CENTER
        config.show_hidden_files = True

        config_dict = config.to_dict()

        assert config_dict['theme']['mode'] == 'light'
        assert config_dict['taskbar']['alignment'] == 'center'
        assert config_dict['explorer']['hidden_files'] is True


class TestUICustomizer:
    """Test UICustomizer class"""

    def test_initialization(self, test_image_path):
        """Test UICustomizer initialization"""
        customizer = UICustomizer(test_image_path)

        assert customizer.image_path == test_image_path
        assert customizer.index == 1
        assert customizer._mounted is False
        assert isinstance(customizer.config, UICustomizationConfig)

    def test_initialization_nonexistent_image(self):
        """Test initialization with nonexistent image"""
        with pytest.raises(FileNotFoundError):
            UICustomizer(Path("/nonexistent/image.wim"))

    @patch('subprocess.run')
    def test_mount(self, mock_run, test_image_path, test_mount_point):
        """Test mount operation"""
        customizer = UICustomizer(test_image_path)
        mock_run.return_value = Mock(returncode=0)

        mount_point = customizer.mount(test_mount_point)

        assert customizer._mounted is True
        assert customizer.mount_point == test_mount_point
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_unmount(self, mock_run, test_image_path, test_mount_point):
        """Test unmount operation"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.unmount(save_changes=True)

        assert customizer._mounted is False
        mock_run.assert_called_once()
        assert '/Commit' in str(mock_run.call_args)

    def test_unmount_not_mounted(self, test_image_path):
        """Test unmount when not mounted raises error"""
        customizer = UICustomizer(test_image_path)

        with pytest.raises(RuntimeError, match="not mounted"):
            customizer.unmount()

    @patch('subprocess.run')
    def test_apply_gaming_profile(self, mock_run, test_image_path, test_mount_point):
        """Test applying gaming UI profile"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.apply_profile(UIProfile.GAMING)

        assert customizer.config.theme_mode == ThemeMode.DARK
        assert customizer.config.disable_animations is True
        assert customizer.config.visual_effects_best_performance is True

    @patch('subprocess.run')
    def test_apply_developer_profile(self, mock_run, test_image_path, test_mount_point):
        """Test applying developer UI profile"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.apply_profile(UIProfile.DEVELOPER)

        assert customizer.config.show_file_extensions is True
        assert customizer.config.show_hidden_files is True
        assert customizer.config.theme_mode == ThemeMode.DARK

    def test_apply_profile_not_mounted(self, test_image_path):
        """Test applying profile when not mounted raises error"""
        customizer = UICustomizer(test_image_path)

        with pytest.raises(RuntimeError, match="must be mounted"):
            customizer.apply_profile(UIProfile.GAMING)


class TestUIProfiles:
    """Test UI profile enums"""

    def test_all_profiles_exist(self):
        """Test all expected profiles are defined"""
        expected_profiles = ['MODERN', 'CLASSIC', 'MINIMAL', 'GAMING', 'PRODUCTIVITY', 'DEVELOPER']

        for profile_name in expected_profiles:
            assert hasattr(UIProfile, profile_name)

    def test_profile_values(self):
        """Test profile enum values"""
        assert UIProfile.GAMING.value == 'gaming'
        assert UIProfile.DEVELOPER.value == 'developer'
        assert UIProfile.MODERN.value == 'modern'


class TestThemeModes:
    """Test theme mode enums"""

    def test_theme_modes_exist(self):
        """Test all theme modes are defined"""
        assert ThemeMode.DARK.value == 'dark'
        assert ThemeMode.LIGHT.value == 'light'
        assert ThemeMode.AUTO.value == 'auto'


class TestTaskbarAlignment:
    """Test taskbar alignment enum"""

    def test_alignment_values(self):
        """Test taskbar alignment values"""
        assert TaskbarAlignment.LEFT.value == 'left'
        assert TaskbarAlignment.CENTER.value == 'center'


@pytest.mark.integration
class TestCustomizeUIFunction:
    """Test the convenience customize_ui function"""

    @patch('deployforge.ui_customization.UICustomizer')
    def test_customize_ui_with_profile(self, mock_customizer_class):
        """Test customize_ui convenience function"""
        mock_customizer = Mock()
        mock_customizer_class.return_value = mock_customizer

        customize_ui(Path("test.wim"), UIProfile.GAMING)

        mock_customizer.mount.assert_called_once()
        mock_customizer.apply_profile.assert_called_once_with(
            UIProfile.GAMING,
            progress_callback=None
        )
        mock_customizer.unmount.assert_called_once_with(
            save_changes=True,
            progress_callback=None
        )


@pytest.mark.unit
class TestRegistryOperations:
    """Test registry modification methods"""

    @patch('subprocess.run')
    def test_restore_windows10_context_menu(self, mock_run, test_image_path, test_mount_point):
        """Test restoring Windows 10 context menu"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.restore_windows10_context_menu()

        # Should call reg load, reg add, reg unload
        assert mock_run.call_count >= 3

    @patch('subprocess.run')
    def test_configure_taskbar(self, mock_run, test_image_path, test_mount_point):
        """Test taskbar configuration"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.configure_taskbar(
            alignment=TaskbarAlignment.CENTER,
            show_widgets=True,
            show_chat=False
        )

        # Should configure registry settings
        assert mock_run.call_count > 0

    @patch('subprocess.run')
    def test_configure_theme(self, mock_run, test_image_path, test_mount_point):
        """Test theme configuration"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.configure_theme(ThemeMode.DARK)

        # Should set dark mode registry keys
        assert mock_run.call_count > 0


@pytest.mark.unit
class TestProgressCallbacks:
    """Test progress callback functionality"""

    @patch('subprocess.run')
    def test_mount_with_callback(self, mock_run, test_image_path, test_mount_point, progress_callback):
        """Test mount with progress callback"""
        customizer = UICustomizer(test_image_path)
        mock_run.return_value = Mock(returncode=0)

        customizer.mount(test_mount_point, progress_callback=progress_callback)

        progress_callback.assert_called_with("Mounting image for UI customization...")

    @patch('subprocess.run')
    def test_unmount_with_callback(self, mock_run, test_image_path, test_mount_point, progress_callback):
        """Test unmount with progress callback"""
        customizer = UICustomizer(test_image_path)
        customizer._mounted = True
        customizer.mount_point = test_mount_point
        mock_run.return_value = Mock(returncode=0)

        customizer.unmount(progress_callback=progress_callback)

        progress_callback.assert_called_with("Unmounting image...")
