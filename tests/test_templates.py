"""Tests for template system."""

import pytest
import json
from pathlib import Path
from deployforge.templates import (
    TemplateManager,
    CustomizationTemplate,
    FileOperation,
    RegistryTweak
)


def test_template_creation(sample_template):
    """Test template creation."""
    assert sample_template.name == "Test Template"
    assert sample_template.version == "1.0"
    assert len(sample_template.files) == 1
    assert len(sample_template.registry) == 1


def test_template_manager_save_json(temp_dir, sample_template):
    """Test saving template as JSON."""
    manager = TemplateManager(temp_dir)
    output_path = temp_dir / "test_template.json"

    manager.save_template(sample_template, output_path)

    assert output_path.exists()

    with open(output_path) as f:
        data = json.load(f)

    assert data["name"] == "Test Template"
    assert data["version"] == "1.0"


def test_template_manager_load_json(temp_dir, sample_template):
    """Test loading template from JSON."""
    manager = TemplateManager(temp_dir)
    output_path = temp_dir / "test_template.json"

    # Save first
    manager.save_template(sample_template, output_path)

    # Load
    loaded_template = manager.load_template(output_path)

    assert loaded_template.name == sample_template.name
    assert loaded_template.version == sample_template.version
    assert len(loaded_template.files) == len(sample_template.files)


def test_template_validation_valid(sample_template):
    """Test validating a valid template."""
    manager = TemplateManager(Path("/tmp"))

    is_valid = manager.validate_template(sample_template)
    assert is_valid


def test_template_validation_invalid():
    """Test validating an invalid template."""
    manager = TemplateManager(Path("/tmp"))

    # Template with invalid action
    template = CustomizationTemplate(name="Invalid", version="1.0")
    template.files.append(FileOperation(
        action="invalid_action",
        destination="/test"
    ))

    with pytest.raises(Exception):
        manager.validate_template(template)


def test_file_operation():
    """Test file operation creation."""
    op = FileOperation(
        action="add",
        source="/source/file.txt",
        destination="/dest/file.txt"
    )

    assert op.action == "add"
    assert op.source == "/source/file.txt"
    assert op.destination == "/dest/file.txt"


def test_registry_tweak():
    """Test registry tweak creation."""
    tweak = RegistryTweak(
        hive="HKLM\\SOFTWARE",
        path="Test\\Path",
        name="TestValue",
        data="123",
        type="REG_DWORD"
    )

    assert tweak.hive == "HKLM\\SOFTWARE"
    assert tweak.type == "REG_DWORD"
