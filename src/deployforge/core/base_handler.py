"""Base handler class for all image format handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


class BaseImageHandler(ABC):
    """Abstract base class for image format handlers."""

    def __init__(self, image_path: Path):
        """
        Initialize the handler.

        Args:
            image_path: Path to the image file
        """
        self.image_path = Path(image_path)
        self.is_mounted = False
        self.mount_point: Optional[Path] = None
        self._validate_image()

    def _validate_image(self) -> None:
        """Validate that the image file exists and is valid."""
        if not self.image_path.exists():
            from deployforge.core.exceptions import ImageNotFoundError

            raise ImageNotFoundError(f"Image file not found: {self.image_path}")

    @abstractmethod
    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount the image.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to the mount point

        Raises:
            MountError: If mounting fails
        """
        pass

    @abstractmethod
    def unmount(self, save_changes: bool = False) -> None:
        """
        Unmount the image.

        Args:
            save_changes: Whether to save changes made to the image

        Raises:
            MountError: If unmounting fails
        """
        pass

    @abstractmethod
    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in the image.

        Args:
            path: Path within the image to list

        Returns:
            List of file information dictionaries
        """
        pass

    @abstractmethod
    def add_file(self, source: Path, destination: str) -> None:
        """
        Add a file to the image.

        Args:
            source: Path to the source file on the host
            destination: Destination path within the image
        """
        pass

    @abstractmethod
    def remove_file(self, path: str) -> None:
        """
        Remove a file from the image.

        Args:
            path: Path to the file within the image
        """
        pass

    @abstractmethod
    def extract_file(self, source: str, destination: Path) -> None:
        """
        Extract a file from the image.

        Args:
            source: Path to the file within the image
            destination: Destination path on the host
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the image.

        Returns:
            Dictionary containing image metadata
        """
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.is_mounted:
            self.unmount(save_changes=False)
        return False

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(image_path={self.image_path})"
