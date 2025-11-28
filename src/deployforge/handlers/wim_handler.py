"""WIM (Windows Imaging Format) handler."""

import os
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
import json

from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.exceptions import MountError, OperationError, DISMError


logger = logging.getLogger(__name__)


class WIMHandler(BaseImageHandler):
    """
    Handler for WIM (Windows Imaging Format) files.

    Uses DISM on Windows or wimlib on Linux/Mac.
    """

    def __init__(self, image_path: Path):
        """Initialize the WIM handler."""
        super().__init__(image_path)
        self.is_windows = platform.system() == "Windows"
        self._temp_dir = None
        self.index = 1  # Default to first image index

    def _check_wimlib(self) -> bool:
        """Check if wimlib-imagex is available."""
        try:
            result = subprocess.run(
                ["wimlib-imagex", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_dism(self) -> bool:
        """Check if DISM is available (Windows only)."""
        if not self.is_windows:
            return False
        try:
            result = subprocess.run(["dism", "/?"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def mount(self, mount_point: Optional[Path] = None, index: int = 1) -> Path:
        """
        Mount the WIM image.

        Args:
            mount_point: Optional custom mount point
            index: Image index to mount (default: 1)

        Returns:
            Path to the mount point
        """
        if self.is_mounted:
            logger.warning("Image is already mounted")
            return self.mount_point

        self.index = index

        try:
            # Create mount point
            if mount_point is None:
                self._temp_dir = tempfile.mkdtemp(prefix="deployforge_wim_")
                self.mount_point = Path(self._temp_dir)
            else:
                self.mount_point = Path(mount_point)
                self.mount_point.mkdir(parents=True, exist_ok=True)

            # Try DISM first on Windows
            if self.is_windows and self._check_dism():
                self._mount_with_dism()
            # Try wimlib on Linux/Mac
            elif self._check_wimlib():
                self._mount_with_wimlib()
            else:
                raise MountError(
                    "No WIM mounting tool available. "
                    "Install DISM (Windows) or wimlib-imagex (Linux/Mac)"
                )

            self.is_mounted = True
            logger.info(f"Mounted WIM at {self.mount_point}")
            return self.mount_point

        except Exception as e:
            if self._temp_dir:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            raise MountError(f"Failed to mount WIM: {e}")

    def _mount_with_dism(self) -> None:
        """Mount WIM using DISM (Windows)."""
        cmd = [
            "dism",
            "/Mount-Wim",
            f"/WimFile:{self.image_path}",
            f"/Index:{self.index}",
            f"/MountDir:{self.mount_point}",
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise DISMError(f"DISM mount failed: {result.stderr}")

    def _mount_with_wimlib(self) -> None:
        """Mount WIM using wimlib-imagex (Linux/Mac)."""
        cmd = [
            "wimlib-imagex",
            "mount",
            str(self.image_path),
            str(self.index),
            str(self.mount_point),
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"wimlib mount failed: {result.stderr}")

    def unmount(self, save_changes: bool = False) -> None:
        """
        Unmount the WIM image.

        Args:
            save_changes: Whether to commit changes to the WIM
        """
        if not self.is_mounted:
            logger.warning("Image is not mounted")
            return

        try:
            # Unmount with DISM or wimlib
            if self.is_windows and self._check_dism():
                self._unmount_with_dism(save_changes)
            elif self._check_wimlib():
                self._unmount_with_wimlib(save_changes)

            # Clean up temporary directory
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None

            self.is_mounted = False
            self.mount_point = None
            logger.info("Unmounted WIM")

        except Exception as e:
            raise MountError(f"Failed to unmount WIM: {e}")

    def _unmount_with_dism(self, save_changes: bool) -> None:
        """Unmount WIM using DISM."""
        commit_flag = "/Commit" if save_changes else "/Discard"
        cmd = [
            "dism",
            "/Unmount-Wim",
            f"/MountDir:{self.mount_point}",
            commit_flag,
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise DISMError(f"DISM unmount failed: {result.stderr}")

    def _unmount_with_wimlib(self, save_changes: bool) -> None:
        """Unmount WIM using wimlib-imagex."""
        cmd = ["wimlib-imagex", "unmount", str(self.mount_point)]
        if save_changes:
            cmd.append("--commit")

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"wimlib unmount failed: {result.stderr}")

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in the WIM.

        Args:
            path: Path within the WIM to list

        Returns:
            List of file information dictionaries
        """
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            target_path = self.mount_point / path.lstrip("/")
            if not target_path.exists():
                return []

            files = []
            for item in target_path.iterdir():
                files.append(
                    {
                        "name": item.name,
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0,
                        "path": str(item.relative_to(self.mount_point)),
                    }
                )
            return files

        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def add_file(self, source: Path, destination: str) -> None:
        """
        Add a file to the WIM.

        Args:
            source: Path to the source file
            destination: Destination path within the WIM
        """
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            source = Path(source)
            if not source.exists():
                raise OperationError(f"Source file not found: {source}")

            dest_path = self.mount_point / destination.lstrip("/")
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source, dest_path)
            logger.info(f"Added {source} to WIM at {destination}")

        except Exception as e:
            raise OperationError(f"Failed to add file: {e}")

    def remove_file(self, path: str) -> None:
        """
        Remove a file from the WIM.

        Args:
            path: Path to the file within the WIM
        """
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            target_path = self.mount_point / path.lstrip("/")
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                raise OperationError(f"Path not found: {path}")

            logger.info(f"Removed {path} from WIM")

        except Exception as e:
            raise OperationError(f"Failed to remove file: {e}")

    def extract_file(self, source: str, destination: Path) -> None:
        """
        Extract a file from the WIM.

        Args:
            source: Path to the file within the WIM
            destination: Destination path on the host
        """
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            source_path = self.mount_point / source.lstrip("/")
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
        Get information about the WIM.

        Returns:
            Dictionary containing WIM metadata
        """
        info = {
            "path": str(self.image_path),
            "format": "WIM",
            "size": self.image_path.stat().st_size,
            "mounted": self.is_mounted,
            "index": self.index,
        }

        try:
            # Get image information using DISM or wimlib
            if self.is_windows and self._check_dism():
                info.update(self._get_info_dism())
            elif self._check_wimlib():
                info.update(self._get_info_wimlib())
        except Exception as e:
            logger.warning(f"Could not read WIM metadata: {e}")

        return info

    def _get_info_dism(self) -> Dict[str, Any]:
        """Get WIM info using DISM."""
        cmd = ["dism", "/Get-WimInfo", f"/WimFile:{self.image_path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Parse DISM output
            return {"dism_output": result.stdout}
        return {}

    def _get_info_wimlib(self) -> Dict[str, Any]:
        """Get WIM info using wimlib."""
        cmd = ["wimlib-imagex", "info", str(self.image_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return {"wimlib_output": result.stdout}
        return {}
