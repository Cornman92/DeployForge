"""Main image manager for coordinating image operations."""

from pathlib import Path
from typing import Optional, Dict, Any
import logging

from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.exceptions import UnsupportedFormatError


logger = logging.getLogger(__name__)


class ImageManager:
    """
    Main entry point for managing Windows deployment images.

    Automatically detects image format and delegates to appropriate handler.
    """

    # Map of file extensions to handler classes
    _handlers: Dict[str, type] = {}

    @classmethod
    def register_handler(cls, extension: str, handler_class: type) -> None:
        """
        Register a handler for a specific file extension.

        Args:
            extension: File extension (e.g., '.iso', '.wim')
            handler_class: Handler class to use for this extension
        """
        cls._handlers[extension.lower()] = handler_class
        logger.debug(f"Registered handler {handler_class.__name__} for {extension}")

    @classmethod
    def get_handler(cls, image_path: Path) -> BaseImageHandler:
        """
        Get the appropriate handler for an image file.

        Args:
            image_path: Path to the image file

        Returns:
            Handler instance for the image

        Raises:
            UnsupportedFormatError: If the image format is not supported
        """
        image_path = Path(image_path)
        extension = image_path.suffix.lower()

        handler_class = cls._handlers.get(extension)
        if not handler_class:
            supported = ", ".join(cls._handlers.keys())
            raise UnsupportedFormatError(
                f"Unsupported image format: {extension}. " f"Supported formats: {supported}"
            )

        logger.info(f"Using {handler_class.__name__} for {image_path.name}")
        return handler_class(image_path)

    @classmethod
    def supported_formats(cls) -> list:
        """
        Get list of supported image formats.

        Returns:
            List of supported file extensions
        """
        return list(cls._handlers.keys())

    def __init__(self, image_path: Path):
        """
        Initialize the image manager.

        Args:
            image_path: Path to the image file
        """
        self.image_path = Path(image_path)
        self.handler = self.get_handler(self.image_path)

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the image."""
        return self.handler.mount(mount_point)

    def unmount(self, save_changes: bool = False) -> None:
        """Unmount the image."""
        self.handler.unmount(save_changes)

    def list_files(self, path: str = "/") -> list:
        """List files in the image."""
        return self.handler.list_files(path)

    def add_file(self, source: Path, destination: str) -> None:
        """Add a file to the image."""
        self.handler.add_file(source, destination)

    def remove_file(self, path: str) -> None:
        """Remove a file from the image."""
        self.handler.remove_file(path)

    def extract_file(self, source: str, destination: Path) -> None:
        """Extract a file from the image."""
        self.handler.extract_file(source, destination)

    def get_info(self) -> Dict[str, Any]:
        """Get image information."""
        return self.handler.get_info()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        return self.handler.__exit__(exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ImageManager(image_path={self.image_path}, handler={self.handler.__class__.__name__})"
        )
