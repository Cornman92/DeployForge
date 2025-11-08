"""
DeployForge - Enterprise Windows Deployment Suite
Complete automation solution with UEFI/GPT partitioning, WinPE customization,
answer files, and multi-language support.
"""

__version__ = "0.4.0"
__author__ = "DeployForge Team"
__description__ = "Enterprise Windows Deployment Suite for complete image automation"

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
