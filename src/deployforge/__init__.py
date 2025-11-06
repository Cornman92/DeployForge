"""
DeployForge - Windows Deployment Suite
Customize, personalize and optimize Windows images and packages.
"""

__version__ = "0.1.0"
__author__ = "DeployForge Team"
__description__ = "Windows Deployment Suite for image customization"

from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import (
    DeployForgeError,
    ImageNotFoundError,
    UnsupportedFormatError,
    MountError,
)

__all__ = [
    "ImageManager",
    "DeployForgeError",
    "ImageNotFoundError",
    "UnsupportedFormatError",
    "MountError",
]
