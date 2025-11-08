"""ISO image handler using pycdlib."""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import shutil

try:
    import pycdlib
    PYCDLIB_AVAILABLE = True
except ImportError:
    PYCDLIB_AVAILABLE = False

from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.exceptions import MountError, OperationError


logger = logging.getLogger(__name__)


class ISOHandler(BaseImageHandler):
    """Handler for ISO 9660 image files."""

    def __init__(self, image_path: Path):
        """Initialize the ISO handler."""
        if not PYCDLIB_AVAILABLE:
            raise ImportError(
                "pycdlib is required for ISO handling. "
                "Install it with: pip install pycdlib"
            )
        super().__init__(image_path)
        self.iso = None
        self._temp_dir = None

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount the ISO image.

        For ISO files, we create a temporary directory and extract files
        as needed, since pycdlib provides programmatic access.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to the mount point
        """
        if self.is_mounted:
            logger.warning("Image is already mounted")
            return self.mount_point

        try:
            # Create temporary directory if no mount point specified
            if mount_point is None:
                self._temp_dir = tempfile.mkdtemp(prefix="deployforge_iso_")
                self.mount_point = Path(self._temp_dir)
            else:
                self.mount_point = Path(mount_point)
                self.mount_point.mkdir(parents=True, exist_ok=True)

            # Open ISO
            self.iso = pycdlib.PyCdlib()
            self.iso.open(str(self.image_path))

            self.is_mounted = True
            logger.info(f"Mounted ISO at {self.mount_point}")
            return self.mount_point

        except Exception as e:
            if self._temp_dir:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            raise MountError(f"Failed to mount ISO: {e}")

    def unmount(self, save_changes: bool = False) -> None:
        """
        Unmount the ISO image.

        Args:
            save_changes: Whether to save changes to a new ISO
        """
        if not self.is_mounted:
            logger.warning("Image is not mounted")
            return

        try:
            if save_changes and self.iso:
                # Save changes to a new ISO
                backup_path = self.image_path.with_suffix('.iso.bak')
                new_iso_path = self.image_path.with_suffix('.iso.new')

                self.iso.write(str(new_iso_path))
                logger.info(f"Saved modified ISO to {new_iso_path}")

            if self.iso:
                self.iso.close()
                self.iso = None

            # Clean up temporary directory
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None

            self.is_mounted = False
            self.mount_point = None
            logger.info("Unmounted ISO")

        except Exception as e:
            raise MountError(f"Failed to unmount ISO: {e}")

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in the ISO.

        Args:
            path: Path within the ISO to list

        Returns:
            List of file information dictionaries
        """
        if not self.is_mounted or not self.iso:
            raise MountError("Image must be mounted first")

        try:
            files = []
            # Convert path to ISO 9660 format
            iso_path = path.replace('\\', '/').upper()
            if not iso_path.startswith('/'):
                iso_path = '/' + iso_path

            # List directory contents
            for child in self.iso.list_children(iso_path=iso_path):
                file_info = {
                    'name': child.file_identifier().decode('utf-8') if isinstance(child.file_identifier(), bytes) else child.file_identifier(),
                    'is_dir': child.is_dir(),
                    'size': child.get_data_length() if not child.is_dir() else 0,
                }
                files.append(file_info)

            return files

        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            return []

    def add_file(self, source: Path, destination: str) -> None:
        """
        Add a file to the ISO.

        Args:
            source: Path to the source file
            destination: Destination path within the ISO
        """
        if not self.is_mounted or not self.iso:
            raise MountError("Image must be mounted first")

        try:
            source = Path(source)
            if not source.exists():
                raise OperationError(f"Source file not found: {source}")

            # Convert destination to ISO 9660 format
            iso_dest = destination.replace('\\', '/').upper()

            # Add file to ISO
            with open(source, 'rb') as f:
                self.iso.add_fp(f, length=source.stat().st_size, iso_path=iso_dest)

            logger.info(f"Added {source} to ISO at {iso_dest}")

        except Exception as e:
            raise OperationError(f"Failed to add file: {e}")

    def remove_file(self, path: str) -> None:
        """
        Remove a file from the ISO.

        Args:
            path: Path to the file within the ISO
        """
        if not self.is_mounted or not self.iso:
            raise MountError("Image must be mounted first")

        try:
            # Convert path to ISO 9660 format
            iso_path = path.replace('\\', '/').upper()

            # Remove from ISO
            self.iso.rm_file(iso_path)
            logger.info(f"Removed {iso_path} from ISO")

        except Exception as e:
            raise OperationError(f"Failed to remove file: {e}")

    def extract_file(self, source: str, destination: Path) -> None:
        """
        Extract a file from the ISO.

        Args:
            source: Path to the file within the ISO
            destination: Destination path on the host
        """
        if not self.is_mounted or not self.iso:
            raise MountError("Image must be mounted first")

        try:
            destination = Path(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Convert source to ISO 9660 format
            iso_path = source.replace('\\', '/').upper()

            # Extract file
            self.iso.get_file_from_iso(str(destination), iso_path=iso_path)
            logger.info(f"Extracted {iso_path} to {destination}")

        except Exception as e:
            raise OperationError(f"Failed to extract file: {e}")

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the ISO.

        Returns:
            Dictionary containing ISO metadata
        """
        info = {
            'path': str(self.image_path),
            'format': 'ISO 9660',
            'size': self.image_path.stat().st_size,
            'mounted': self.is_mounted,
        }

        if self.is_mounted and self.iso:
            try:
                pvd = self.iso.pvd
                info.update({
                    'volume_identifier': pvd.volume_identifier.decode('utf-8').strip() if pvd.volume_identifier else '',
                    'system_identifier': pvd.system_identifier.decode('utf-8').strip() if pvd.system_identifier else '',
                    'volume_set_identifier': pvd.volume_set_identifier.decode('utf-8').strip() if pvd.volume_set_identifier else '',
                })
            except Exception as e:
                logger.warning(f"Could not read ISO metadata: {e}")

        return info
