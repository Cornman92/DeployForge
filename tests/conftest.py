"""
Pytest Configuration and Shared Fixtures

Provides common fixtures for all tests including mocked DISM operations,
temporary files, and test data.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch


# =============================================================================
# Path Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files"""
    return tmp_path


@pytest.fixture
def test_image_path(tmp_path):
    """Provide a temporary test image file path"""
    image_path = tmp_path / "test_image.wim"
    image_path.write_text("Mock WIM file content")
    return image_path


@pytest.fixture
def test_mount_point(tmp_path):
    """Provide a temporary mount point directory"""
    mount_point = tmp_path / "mount"
    mount_point.mkdir(parents=True, exist_ok=True)

    # Create realistic Windows mount structure
    (mount_point / "Windows").mkdir()
    (mount_point / "Windows" / "System32").mkdir()
    (mount_point / "Windows" / "System32" / "config").mkdir()
    (mount_point / "Windows" / "Setup").mkdir()
    (mount_point / "Windows" / "Setup" / "Scripts").mkdir()
    (mount_point / "Users").mkdir()
    (mount_point / "Users" / "Default").mkdir()

    # Create registry hive files
    (mount_point / "Windows" / "System32" / "config" / "SOFTWARE").write_text("MOCK_HIVE")
    (mount_point / "Windows" / "System32" / "config" / "SYSTEM").write_text("MOCK_HIVE")
    (mount_point / "Users" / "Default" / "NTUSER.DAT").write_text("MOCK_HIVE")

    return mount_point


# =============================================================================
# DISM Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for DISM operations"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Operation completed successfully",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def progress_callback():
    """Provide a mock progress callback function"""
    callback = Mock()
    return callback
