"""Tests for Windows Update control module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from deployforge.updates_control import (
    WindowsUpdateController,
    UpdatePolicy,
)


def test_windows_update_controller_init(mock_wim_file):
    """Test WindowsUpdateController initialization."""
    controller = WindowsUpdateController(mock_wim_file)
    assert controller.image_path == mock_wim_file
    assert controller.index == 1
    assert not controller.is_mounted


def test_update_policy_enum():
    """Test UpdatePolicy enum values."""
    assert UpdatePolicy.DISABLED.value == "disabled"
    assert UpdatePolicy.MANUAL.value == "manual"
    assert UpdatePolicy.AUTOMATIC.value == "automatic"
    assert UpdatePolicy.NOTIFY_ONLY.value == "notify"


@patch("subprocess.run")
def test_set_registry_value(mock_run, mock_wim_file):
    """Test setting registry value."""
    controller = WindowsUpdateController(mock_wim_file)

    controller._set_registry_value("HKLM\\TEMP_SOFTWARE\\Test", "TestValue", 1, "REG_DWORD")

    # Should make two subprocess calls: reg add for key, reg add for value
    assert mock_run.call_count == 2


@patch("subprocess.run")
def test_load_registry(mock_run, mock_wim_file, mock_mount_point):
    """Test loading registry hives."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point

    controller._load_registry()

    # Should load both SOFTWARE and SYSTEM hives
    assert mock_run.call_count == 2

    # Verify reg load commands
    calls = mock_run.call_args_list
    assert "reg" in str(calls[0])
    assert "load" in str(calls[0])


@patch("subprocess.run")
def test_unload_registry(mock_run, mock_wim_file):
    """Test unloading registry hives."""
    controller = WindowsUpdateController(mock_wim_file)

    controller._unload_registry()

    # Should unload both SOFTWARE and SYSTEM hives
    assert mock_run.call_count == 2

    # Verify reg unload commands
    calls = mock_run.call_args_list
    assert "reg" in str(calls[0])
    assert "unload" in str(calls[0])


@patch("subprocess.run")
def test_set_update_policy_disabled(mock_run, mock_wim_file, mock_mount_point):
    """Test setting update policy to disabled."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.set_update_policy(UpdatePolicy.DISABLED)

    # Should set multiple registry values for disabled policy
    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_set_update_policy_manual(mock_run, mock_wim_file, mock_mount_point):
    """Test setting update policy to manual."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.set_update_policy(UpdatePolicy.MANUAL)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_set_update_policy_automatic(mock_run, mock_wim_file, mock_mount_point):
    """Test setting update policy to automatic."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.set_update_policy(UpdatePolicy.AUTOMATIC)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_defer_feature_updates(mock_run, mock_wim_file, mock_mount_point):
    """Test deferring feature updates."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.defer_feature_updates(days=365)

    # Should set defer registry values
    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_defer_feature_updates_invalid_days(mock_wim_file, mock_mount_point):
    """Test deferring feature updates with invalid days."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with pytest.raises(ValueError):
        controller.defer_feature_updates(days=400)  # Max is 365


@patch("subprocess.run")
def test_defer_quality_updates(mock_run, mock_wim_file, mock_mount_point):
    """Test deferring quality updates."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.defer_quality_updates(days=30)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_defer_quality_updates_invalid_days(mock_wim_file, mock_mount_point):
    """Test deferring quality updates with invalid days."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with pytest.raises(ValueError):
        controller.defer_quality_updates(days=40)  # Max is 30


@patch("subprocess.run")
def test_disable_driver_updates(mock_run, mock_wim_file, mock_mount_point):
    """Test disabling driver updates."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.disable_driver_updates()

    # Should set driver exclusion registry value
    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_set_metered_connection_enabled(mock_run, mock_wim_file, mock_mount_point):
    """Test enabling metered connection."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.set_metered_connection(enabled=True)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_set_metered_connection_disabled(mock_run, mock_wim_file, mock_mount_point):
    """Test disabling metered connection."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.set_metered_connection(enabled=False)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_disable_windows_update_service(mock_run, mock_wim_file, mock_mount_point):
    """Test disabling Windows Update service."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.disable_windows_update_service()

    # Should set service Start value to 4 (disabled)
    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_disable_automatic_restart(mock_run, mock_wim_file, mock_mount_point):
    """Test disabling automatic restart after updates."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.disable_automatic_restart()

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_pause_updates(mock_run, mock_wim_file, mock_mount_point):
    """Test pausing updates."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with patch.object(controller, "_load_registry"):
        with patch.object(controller, "_unload_registry"):
            controller.pause_updates(weeks=5)

    assert mock_run.call_count > 0


@patch("subprocess.run")
def test_pause_updates_invalid_weeks(mock_wim_file, mock_mount_point):
    """Test pausing updates with invalid weeks."""
    controller = WindowsUpdateController(mock_wim_file)
    controller.mount_point = mock_mount_point
    controller.is_mounted = True

    with pytest.raises(ValueError):
        controller.pause_updates(weeks=10)  # Max is 5


def test_mount_not_called_error(mock_wim_file):
    """Test error when modifying without mounting."""
    controller = WindowsUpdateController(mock_wim_file)

    with pytest.raises(RuntimeError):
        controller.set_update_policy(UpdatePolicy.DISABLED)


@patch("subprocess.run")
def test_full_workflow(mock_run, mock_wim_file, mock_mount_point):
    """Test complete workflow: mount, configure, unmount."""
    controller = WindowsUpdateController(mock_wim_file)

    with patch.object(controller, "mount"):
        with patch.object(controller, "_load_registry"):
            with patch.object(controller, "_unload_registry"):
                with patch.object(controller, "unmount"):
                    controller.mount()
                    controller.is_mounted = True
                    controller.mount_point = mock_mount_point

                    controller.set_update_policy(UpdatePolicy.DISABLED)
                    controller.defer_feature_updates(days=365)
                    controller.disable_driver_updates()

                    controller.unmount(save_changes=True)


def test_get_registry_tweak_summary(mock_wim_file):
    """Test getting summary of registry tweaks."""
    controller = WindowsUpdateController(mock_wim_file)

    summary = controller.get_tweak_summary()

    assert isinstance(summary, dict)
    assert "update_policy" in summary or len(summary) == 0  # Empty if not configured
