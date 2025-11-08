"""PPKG (Provisioning Package) handler."""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

try:
    import xmltodict
    XMLTODICT_AVAILABLE = True
except ImportError:
    XMLTODICT_AVAILABLE = False

from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.exceptions import MountError, OperationError


logger = logging.getLogger(__name__)


class PPKGHandler(BaseImageHandler):
    """
    Handler for PPKG (Provisioning Package) files.

    PPKG files are ZIP archives containing configuration files and
    resources for Windows device provisioning. They include:
    - customizations.xml: Configuration settings
    - Scripts and binaries
    - Certificates and profiles
    """

    def __init__(self, image_path: Path):
        """Initialize the PPKG handler."""
        super().__init__(image_path)
        self._temp_dir = None
        self._validate_ppkg()

    def _validate_ppkg(self) -> None:
        """Validate that the file is a valid PPKG (ZIP) file."""
        try:
            with zipfile.ZipFile(self.image_path, 'r') as zf:
                # Just check if it's a valid ZIP
                zf.testzip()
        except zipfile.BadZipFile:
            from deployforge.core.exceptions import ValidationError
            raise ValidationError(f"Invalid PPKG file: {self.image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount (extract) the PPKG.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to the mount point
        """
        if self.is_mounted:
            logger.warning("PPKG is already mounted")
            return self.mount_point

        try:
            # Create mount point
            if mount_point is None:
                self._temp_dir = tempfile.mkdtemp(prefix="deployforge_ppkg_")
                self.mount_point = Path(self._temp_dir)
            else:
                self.mount_point = Path(mount_point)
                self.mount_point.mkdir(parents=True, exist_ok=True)

            # Extract PPKG (ZIP) contents
            with zipfile.ZipFile(self.image_path, 'r') as zf:
                zf.extractall(self.mount_point)

            self.is_mounted = True
            logger.info(f"Mounted PPKG at {self.mount_point}")
            return self.mount_point

        except Exception as e:
            if self._temp_dir:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            raise MountError(f"Failed to mount PPKG: {e}")

    def unmount(self, save_changes: bool = False) -> None:
        """
        Unmount (repackage) the PPKG.

        Args:
            save_changes: Whether to save changes to a new PPKG
        """
        if not self.is_mounted:
            logger.warning("PPKG is not mounted")
            return

        try:
            if save_changes:
                # Create new PPKG with modifications
                new_ppkg_path = self.image_path.with_suffix('.ppkg.new')
                self._create_ppkg(self.mount_point, new_ppkg_path)
                logger.info(f"Saved modified PPKG to {new_ppkg_path}")

            # Clean up temporary directory
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None

            self.is_mounted = False
            self.mount_point = None
            logger.info("Unmounted PPKG")

        except Exception as e:
            raise MountError(f"Failed to unmount PPKG: {e}")

    def _create_ppkg(self, source_dir: Path, output_path: Path) -> None:
        """Create a PPKG (ZIP) from a directory."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(source_dir)
                    zf.write(file_path, arcname)

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in the PPKG.

        Args:
            path: Path within the PPKG to list

        Returns:
            List of file information dictionaries
        """
        if not self.is_mounted:
            raise MountError("PPKG must be mounted first")

        try:
            target_path = self.mount_point / path.lstrip('/')
            if not target_path.exists():
                return []

            files = []
            for item in target_path.iterdir():
                files.append({
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'path': str(item.relative_to(self.mount_point)),
                })
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def add_file(self, source: Path, destination: str) -> None:
        """
        Add a file to the PPKG.

        Args:
            source: Path to the source file
            destination: Destination path within the PPKG
        """
        if not self.is_mounted:
            raise MountError("PPKG must be mounted first")

        try:
            source = Path(source)
            if not source.exists():
                raise OperationError(f"Source file not found: {source}")

            dest_path = self.mount_point / destination.lstrip('/')
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source, dest_path)
            logger.info(f"Added {source} to PPKG at {destination}")

        except Exception as e:
            raise OperationError(f"Failed to add file: {e}")

    def remove_file(self, path: str) -> None:
        """
        Remove a file from the PPKG.

        Args:
            path: Path to the file within the PPKG
        """
        if not self.is_mounted:
            raise MountError("PPKG must be mounted first")

        try:
            target_path = self.mount_point / path.lstrip('/')
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                raise OperationError(f"Path not found: {path}")

            logger.info(f"Removed {path} from PPKG")

        except Exception as e:
            raise OperationError(f"Failed to remove file: {e}")

    def extract_file(self, source: str, destination: Path) -> None:
        """
        Extract a file from the PPKG.

        Args:
            source: Path to the file within the PPKG
            destination: Destination path on the host
        """
        if not self.is_mounted:
            raise MountError("PPKG must be mounted first")

        try:
            source_path = self.mount_point / source.lstrip('/')
            destination = Path(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)

            if source_path.is_file():
                shutil.copy2(source_path, destination)
            elif source_path.is_dir():
                shutil.copytree(source_path, destination, dirs_exist_ok=True)
            else:
                raise OperationError(f"Source not found: {source}")

            logger.info(f"Extracted {source} to {destination}")

        except Exception as e:
            raise OperationError(f"Failed to extract file: {e}")

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the PPKG.

        Returns:
            Dictionary containing PPKG metadata
        """
        info = {
            'path': str(self.image_path),
            'format': 'PPKG (Provisioning Package)',
            'size': self.image_path.stat().st_size,
            'mounted': self.is_mounted,
        }

        # Try to read metadata from the package
        try:
            with zipfile.ZipFile(self.image_path, 'r') as zf:
                info['files'] = len(zf.namelist())

                # Look for customizations.xml
                if 'customizations.xml' in zf.namelist():
                    info['has_customizations'] = True

                    if XMLTODICT_AVAILABLE and self.is_mounted:
                        customizations_path = self.mount_point / 'customizations.xml'
                        if customizations_path.exists():
                            with open(customizations_path, 'r', encoding='utf-8') as f:
                                info['customizations'] = xmltodict.parse(f.read())

        except Exception as e:
            logger.warning(f"Could not read PPKG metadata: {e}")

        return info

    def get_customizations(self) -> Optional[Dict[str, Any]]:
        """
        Get customizations from customizations.xml.

        Returns:
            Dictionary of customizations or None if not available
        """
        if not XMLTODICT_AVAILABLE:
            logger.warning("xmltodict not available, cannot parse customizations")
            return None

        if not self.is_mounted:
            raise MountError("PPKG must be mounted first")

        try:
            customizations_path = self.mount_point / 'customizations.xml'
            if not customizations_path.exists():
                logger.warning("customizations.xml not found in PPKG")
                return None

            with open(customizations_path, 'r', encoding='utf-8') as f:
                return xmltodict.parse(f.read())

        except Exception as e:
            logger.error(f"Failed to read customizations: {e}")
            return None

    def __repr__(self) -> str:
        """String representation."""
        return f"PPKGHandler(image_path={self.image_path})"
