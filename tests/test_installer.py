"""Tests for application installer module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from deployforge.installer import (
    ApplicationInstaller,
    InstallMethod,
    InstallStatus,
    InstallProgress,
    InstallResult,
)
from deployforge.app_catalog import get_app, GAMING_APPS


def test_application_installer_init(mock_wim_file):
    """Test ApplicationInstaller initialization."""
    installer = ApplicationInstaller(mock_wim_file)
    assert installer.image_path == mock_wim_file
    assert installer.index == 1
    assert not installer.is_mounted


def test_install_method_priority():
    """Test InstallMethod enum priority order."""
    methods = list(InstallMethod)
    assert methods[0] == InstallMethod.WINGET
    assert methods[1] == InstallMethod.CHOCOLATEY
    assert methods[2] == InstallMethod.DIRECT_DOWNLOAD


def test_install_progress_dataclass():
    """Test InstallProgress dataclass."""
    progress = InstallProgress(
        app_id="steam",
        app_name="Steam",
        status=InstallStatus.IN_PROGRESS,
        progress_percent=50,
        current_step="Downloading installer",
        total_steps=3,
        current_step_index=1,
        method=InstallMethod.WINGET,
    )

    assert progress.app_id == "steam"
    assert progress.progress_percent == 50
    assert progress.method == InstallMethod.WINGET


def test_install_result_dataclass():
    """Test InstallResult dataclass."""
    result = InstallResult(
        app_id="steam",
        app_name="Steam",
        success=True,
        method=InstallMethod.WINGET,
    )

    assert result.success
    assert result.method == InstallMethod.WINGET
    assert result.error is None


@patch("subprocess.run")
def test_install_via_winget_success(mock_run, mock_wim_file):
    """Test successful installation via WinGet."""
    installer = ApplicationInstaller(mock_wim_file)

    # Mock successful WinGet installation
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

    app = get_app("steam")
    result = installer._install_via_winget(app, progress_callback=None)

    assert result is True
    mock_run.assert_called_once()

    # Verify WinGet command
    call_args = mock_run.call_args[0][0]
    assert "winget" in call_args
    assert "install" in call_args
    assert app.winget_id in call_args


@patch("subprocess.run")
def test_install_via_winget_failure(mock_run, mock_wim_file):
    """Test failed installation via WinGet."""
    installer = ApplicationInstaller(mock_wim_file)

    # Mock failed WinGet installation
    mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")

    app = get_app("steam")
    result = installer._install_via_winget(app, progress_callback=None)

    assert result is False


@patch("subprocess.run")
def test_install_via_chocolatey_success(mock_run, mock_wim_file):
    """Test successful installation via Chocolatey."""
    installer = ApplicationInstaller(mock_wim_file)

    # Mock successful Chocolatey installation
    mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

    app = get_app("discord")
    result = installer._install_via_chocolatey(app, progress_callback=None)

    assert result is True

    # Verify Chocolatey command
    call_args = mock_run.call_args[0][0]
    assert "choco" in call_args
    assert "install" in call_args
    assert app.chocolatey_id in call_args


@patch("deployforge.installer.ApplicationInstaller._download_file")
@patch("subprocess.run")
def test_install_via_download_success(mock_run, mock_download, mock_wim_file, temp_dir):
    """Test successful installation via direct download."""
    installer = ApplicationInstaller(mock_wim_file)

    # Mock download and installation
    installer_path = temp_dir / "installer.exe"
    installer_path.write_bytes(b"MOCK_INSTALLER")
    mock_download.return_value = installer_path
    mock_run.return_value = Mock(returncode=0)

    app = get_app("steam")
    result = installer._install_via_download(app, progress_callback=None)

    assert result is True
    mock_download.assert_called_once()
    mock_run.assert_called_once()


def test_install_application_with_winget_success(mock_wim_file):
    """Test install_application with WinGet fallback."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=True):
        with patch.object(installer, "mount"):
            with patch.object(installer, "unmount"):
                result = installer.install_application("steam")

    assert result.success
    assert result.app_id == "steam"
    assert result.method == InstallMethod.WINGET


def test_install_application_with_chocolatey_fallback(mock_wim_file):
    """Test install_application falls back to Chocolatey when WinGet fails."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=False):
        with patch.object(installer, "_install_via_chocolatey", return_value=True):
            with patch.object(installer, "mount"):
                with patch.object(installer, "unmount"):
                    result = installer.install_application("steam")

    assert result.success
    assert result.method == InstallMethod.CHOCOLATEY


def test_install_application_with_download_fallback(mock_wim_file):
    """Test install_application falls back to direct download."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=False):
        with patch.object(installer, "_install_via_chocolatey", return_value=False):
            with patch.object(installer, "_install_via_download", return_value=True):
                with patch.object(installer, "mount"):
                    with patch.object(installer, "unmount"):
                        result = installer.install_application("steam")

    assert result.success
    assert result.method == InstallMethod.DIRECT_DOWNLOAD


def test_install_application_all_methods_fail(mock_wim_file):
    """Test install_application when all methods fail."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=False):
        with patch.object(installer, "_install_via_chocolatey", return_value=False):
            with patch.object(installer, "_install_via_download", return_value=False):
                with patch.object(installer, "mount"):
                    with patch.object(installer, "unmount"):
                        result = installer.install_application("steam")

    assert not result.success
    assert "All installation methods failed" in result.error


def test_install_applications_multiple(mock_wim_file):
    """Test installing multiple applications."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=True):
        with patch.object(installer, "mount"):
            with patch.object(installer, "unmount"):
                results = installer.install_applications(["steam", "discord"])

    assert len(results) == 2
    assert "steam" in results
    assert "discord" in results
    assert results["steam"].success
    assert results["discord"].success


def test_install_applications_parallel(mock_wim_file):
    """Test parallel installation of applications."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "_install_via_winget", return_value=True):
        with patch.object(installer, "mount"):
            with patch.object(installer, "unmount"):
                results = installer.install_applications(
                    ["steam", "discord", "chrome"], parallel=True, max_workers=2
                )

    assert len(results) == 3
    assert all(result.success for result in results.values())


def test_progress_callback(mock_wim_file):
    """Test progress callback functionality."""
    installer = ApplicationInstaller(mock_wim_file)
    progress_updates = []

    def callback(progress: InstallProgress):
        progress_updates.append(progress)

    with patch.object(installer, "_install_via_winget", return_value=True):
        with patch.object(installer, "mount"):
            with patch.object(installer, "unmount"):
                installer.install_application("steam", progress_callback=callback)

    # Should have received progress updates
    assert len(progress_updates) > 0


def test_unknown_app_id(mock_wim_file):
    """Test installation with unknown app ID."""
    installer = ApplicationInstaller(mock_wim_file)

    with patch.object(installer, "mount"):
        with patch.object(installer, "unmount"):
            result = installer.install_application("nonexistent_app")

    assert not result.success
    assert "Unknown application" in result.error


def test_get_app_catalog():
    """Test retrieving application from catalog."""
    app = get_app("steam")

    assert app.id == "steam"
    assert app.name == "Steam"
    assert app.winget_id is not None
    assert app.category == "Gaming"


def test_gaming_apps_catalog():
    """Test gaming apps catalog structure."""
    assert "steam" in GAMING_APPS
    assert "discord" in GAMING_APPS
    assert "epic-games" in GAMING_APPS

    steam = GAMING_APPS["steam"]
    assert steam.winget_id == "Valve.Steam"
    assert steam.chocolatey_id == "steam"
