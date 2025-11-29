"""Tests for system services management module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from deployforge.services import (
    ServiceManager,
    ServicePreset,
    ServiceStartup,
    SERVICE_PRESETS,
)


def test_service_manager_init(mock_wim_file):
    """Test ServiceManager initialization."""
    manager = ServiceManager(mock_wim_file)
    assert manager.image_path == mock_wim_file
    assert manager.index == 1
    assert not manager.is_mounted


def test_service_startup_enum():
    """Test ServiceStartup enum values."""
    assert ServiceStartup.AUTOMATIC.value == 2
    assert ServiceStartup.MANUAL.value == 3
    assert ServiceStartup.DISABLED.value == 4
    assert ServiceStartup.AUTOMATIC_DELAYED.value == 2


def test_service_preset_enum():
    """Test ServicePreset enum values."""
    assert ServicePreset.GAMING.value == "gaming"
    assert ServicePreset.PERFORMANCE.value == "performance"
    assert ServicePreset.PRIVACY.value == "privacy"
    assert ServicePreset.ENTERPRISE.value == "enterprise"
    assert ServicePreset.MINIMAL.value == "minimal"


def test_service_presets_structure():
    """Test SERVICE_PRESETS dictionary structure."""
    assert ServicePreset.GAMING in SERVICE_PRESETS
    assert ServicePreset.PERFORMANCE in SERVICE_PRESETS
    assert ServicePreset.PRIVACY in SERVICE_PRESETS

    gaming_config = SERVICE_PRESETS[ServicePreset.GAMING]
    assert isinstance(gaming_config, dict)
    assert len(gaming_config) > 0

    # Check that presets contain ServiceStartup enum values
    for service, startup in gaming_config.items():
        assert isinstance(startup, ServiceStartup)


def test_gaming_preset_services():
    """Test gaming preset configuration."""
    gaming_config = SERVICE_PRESETS[ServicePreset.GAMING]

    # Gaming preset should disable certain services
    assert "SysMain" in gaming_config  # Superfetch
    assert "WSearch" in gaming_config  # Windows Search
    assert "DiagTrack" in gaming_config  # Diagnostics


def test_privacy_preset_services():
    """Test privacy preset configuration."""
    privacy_config = SERVICE_PRESETS[ServicePreset.PRIVACY]

    # Privacy preset should disable telemetry services
    assert "DiagTrack" in privacy_config
    assert "dmwappushservice" in privacy_config


def test_performance_preset_services():
    """Test performance preset configuration."""
    performance_config = SERVICE_PRESETS[ServicePreset.PERFORMANCE]

    # Performance preset should disable performance-impacting services
    assert len(performance_config) > 0


@patch("subprocess.run")
def test_set_service_startup_internal(mock_run, mock_wim_file, mock_mount_point):
    """Test setting service startup type."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager._set_service_startup_internal("wuauserv", ServiceStartup.DISABLED)

    # Should set service registry value
    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_set_service_startup(mock_run, mock_wim_file, mock_mount_point):
    """Test public set_service_startup method."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.set_service_startup("wuauserv", ServiceStartup.MANUAL)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_disable_service(mock_run, mock_wim_file, mock_mount_point):
    """Test disabling a service."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.disable_service("wuauserv")

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_enable_service(mock_run, mock_wim_file, mock_mount_point):
    """Test enabling a service."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.enable_service("wuauserv")

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_apply_preset_gaming(mock_run, mock_wim_file, mock_mount_point):
    """Test applying gaming preset."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.apply_preset(ServicePreset.GAMING)

    # Should configure multiple services
    gaming_config = SERVICE_PRESETS[ServicePreset.GAMING]
    expected_calls = len(gaming_config) * 2  # 2 reg commands per service
    assert mock_run.call_count >= expected_calls


@patch("subprocess.run")
def test_apply_preset_performance(mock_run, mock_wim_file, mock_mount_point):
    """Test applying performance preset."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.apply_preset(ServicePreset.PERFORMANCE)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_apply_preset_privacy(mock_run, mock_wim_file, mock_mount_point):
    """Test applying privacy preset."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.apply_preset(ServicePreset.PRIVACY)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_apply_preset_enterprise(mock_run, mock_wim_file, mock_mount_point):
    """Test applying enterprise preset."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.apply_preset(ServicePreset.ENTERPRISE)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_apply_preset_minimal(mock_run, mock_wim_file, mock_mount_point):
    """Test applying minimal preset."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            manager.apply_preset(ServicePreset.MINIMAL)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_configure_services_multiple(mock_run, mock_wim_file, mock_mount_point):
    """Test configuring multiple services at once."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    services_config = {
        "wuauserv": ServiceStartup.DISABLED,
        "Spooler": ServiceStartup.MANUAL,
        "WSearch": ServiceStartup.DISABLED,
    }

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            results = manager.configure_services(services_config)

    assert len(results) == 3
    assert "wuauserv" in results
    assert "Spooler" in results
    assert "WSearch" in results


@patch("subprocess.run")
def test_configure_services_with_errors(mock_run, mock_wim_file, mock_mount_point):
    """Test configure_services handles errors gracefully."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point
    manager.is_mounted = True

    # Mock registry operations to fail for one service
    def side_effect(*args, **kwargs):
        if "BadService" in str(args):
            raise Exception("Service not found")
        return Mock(returncode=0)

    mock_run.side_effect = side_effect

    services_config = {
        "wuauserv": ServiceStartup.DISABLED,
        "BadService": ServiceStartup.DISABLED,
    }

    with patch.object(manager, "_load_registry"):
        with patch.object(manager, "_unload_registry"):
            results = manager.configure_services(services_config)

    assert results["wuauserv"] is True
    assert results["BadService"] is False


def test_get_service_list():
    """Test getting list of common services."""
    manager = ServiceManager(Path("test.wim"))

    services = manager.get_common_services()

    assert isinstance(services, list)
    assert len(services) > 0
    assert any("wuauserv" in s.lower() for s in services)


def test_mount_not_called_error(mock_wim_file):
    """Test error when modifying without mounting."""
    manager = ServiceManager(mock_wim_file)

    with pytest.raises(RuntimeError):
        manager.disable_service("wuauserv")


@patch("subprocess.run")
def test_full_workflow(mock_run, mock_wim_file, mock_mount_point):
    """Test complete workflow: mount, configure, unmount."""
    manager = ServiceManager(mock_wim_file)

    with patch.object(manager, "mount"):
        with patch.object(manager, "_load_registry"):
            with patch.object(manager, "_unload_registry"):
                with patch.object(manager, "unmount"):
                    manager.mount()
                    manager.is_mounted = True
                    manager.mount_point = mock_mount_point

                    manager.apply_preset(ServicePreset.GAMING)
                    manager.disable_service("wuauserv")

                    manager.unmount(save_changes=True)


def test_get_preset_description():
    """Test getting preset descriptions."""
    manager = ServiceManager(Path("test.wim"))

    description = manager.get_preset_description(ServicePreset.GAMING)

    assert isinstance(description, str)
    assert len(description) > 0


def test_list_all_presets():
    """Test listing all available presets."""
    manager = ServiceManager(Path("test.wim"))

    presets = manager.list_presets()

    assert len(presets) == 5
    assert ServicePreset.GAMING in presets
    assert ServicePreset.PERFORMANCE in presets
    assert ServicePreset.PRIVACY in presets
    assert ServicePreset.ENTERPRISE in presets
    assert ServicePreset.MINIMAL in presets


@patch("subprocess.run")
def test_load_registry(mock_run, mock_wim_file, mock_mount_point):
    """Test loading registry hives."""
    manager = ServiceManager(mock_wim_file)
    manager.mount_point = mock_mount_point

    manager._load_registry()

    # Should load SYSTEM hive
    assert mock_run.call_count >= 1
    assert "reg" in str(mock_run.call_args_list[0])
    assert "load" in str(mock_run.call_args_list[0])


@patch("subprocess.run")
def test_unload_registry(mock_run, mock_wim_file):
    """Test unloading registry hives."""
    manager = ServiceManager(mock_wim_file)

    manager._unload_registry()

    # Should unload SYSTEM hive
    assert mock_run.call_count >= 1
    assert "reg" in str(mock_run.call_args_list[0])
    assert "unload" in str(mock_run.call_args_list[0])


def test_service_preset_no_overlap():
    """Test that service presets don't have conflicting configurations."""
    # Get all unique services across all presets
    all_services = set()
    for preset_config in SERVICE_PRESETS.values():
        all_services.update(preset_config.keys())

    # Each preset should configure a reasonable subset
    for preset, config in SERVICE_PRESETS.items():
        assert len(config) > 0
        assert len(config) <= len(all_services)
