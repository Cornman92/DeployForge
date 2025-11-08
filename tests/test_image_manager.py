"""Tests for ImageManager."""

import pytest
from pathlib import Path
from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import UnsupportedFormatError, ImageNotFoundError


def test_supported_formats():
    """Test that supported formats are registered."""
    formats = ImageManager.supported_formats()
    assert '.iso' in formats
    assert '.wim' in formats
    assert '.esd' in formats
    assert '.ppkg' in formats


def test_unsupported_format():
    """Test that unsupported formats raise an error."""
    with pytest.raises(UnsupportedFormatError):
        ImageManager(Path('test.unknown'))


def test_nonexistent_file():
    """Test that nonexistent files raise an error."""
    with pytest.raises(ImageNotFoundError):
        ImageManager(Path('nonexistent.iso'))
