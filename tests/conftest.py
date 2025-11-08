"""Pytest configuration and fixtures."""

import pytest
import tempfile
import zipfile
from pathlib import Path
import json


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_iso_file(temp_dir):
    """Create a mock ISO file."""
    iso_path = temp_dir / "test.iso"
    # Create an empty file for testing
    iso_path.write_bytes(b"ISO_MOCK_DATA" * 100)
    return iso_path


@pytest.fixture
def mock_wim_file(temp_dir):
    """Create a mock WIM file."""
    wim_path = temp_dir / "test.wim"
    wim_path.write_bytes(b"WIM_MOCK_DATA" * 100)
    return wim_path


@pytest.fixture
def mock_ppkg_file(temp_dir):
    """Create a mock PPKG file (ZIP)."""
    ppkg_path = temp_dir / "test.ppkg"

    with zipfile.ZipFile(ppkg_path, 'w') as zf:
        # Add customizations.xml
        customizations = """<?xml version="1.0" encoding="utf-8"?>
<WindowsCustomizations>
    <PackageConfig xmlns="urn:schemas-Microsoft-com:Windows-ICD-Package-Config.v1.0">
        <ID>{12345678-1234-1234-1234-123456789012}</ID>
        <Name>Test Package</Name>
        <Version>1.0</Version>
    </PackageConfig>
</WindowsCustomizations>"""
        zf.writestr('customizations.xml', customizations)
        zf.writestr('test.txt', 'Test content')

    return ppkg_path


@pytest.fixture
def mock_vhd_file(temp_dir):
    """Create a mock VHD file."""
    vhd_path = temp_dir / "test.vhd"
    vhd_path.write_bytes(b"VHD_MOCK_DATA" * 100)
    return vhd_path


@pytest.fixture
def sample_template():
    """Create a sample template for testing."""
    from deployforge.templates import CustomizationTemplate, FileOperation, RegistryTweak

    template = CustomizationTemplate(
        name="Test Template",
        version="1.0",
        description="Template for testing",
        author="Test Suite"
    )

    template.files.append(FileOperation(
        action="add",
        source="/test/source.txt",
        destination="/test/dest.txt"
    ))

    template.registry.append(RegistryTweak(
        hive="HKLM\\SOFTWARE",
        path="Test\\Path",
        name="TestValue",
        data="123",
        type="REG_DWORD"
    ))

    return template


@pytest.fixture
def mock_mount_point(temp_dir):
    """Create a mock mount point with directory structure."""
    mount_point = temp_dir / "mount"
    mount_point.mkdir()

    # Create Windows-like directory structure
    windows_dir = mount_point / "Windows"
    system32_dir = windows_dir / "System32"
    config_dir = system32_dir / "config"

    config_dir.mkdir(parents=True)

    # Create mock registry hives
    (config_dir / "SOFTWARE").write_bytes(b"MOCK_SOFTWARE_HIVE")
    (config_dir / "SYSTEM").write_bytes(b"MOCK_SYSTEM_HIVE")

    # Create some test files
    (mount_point / "test.txt").write_text("Test content")
    (windows_dir / "notepad.exe").write_bytes(b"MOCK_EXE")

    return mount_point


@pytest.fixture
def cache_dir(temp_dir):
    """Create a cache directory."""
    cache = temp_dir / "cache"
    cache.mkdir()
    return cache


@pytest.fixture
def audit_log_path(temp_dir):
    """Create an audit log path."""
    return temp_dir / "audit.jsonl"
