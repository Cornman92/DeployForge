"""Windows Update package integration."""

import logging
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from deployforge.core.exceptions import OperationError


logger = logging.getLogger(__name__)


@dataclass
class UpdatePackage:
    """Represents a Windows Update package."""
    kb_number: str
    file_path: Path
    package_type: str  # msu, cab, esd
    description: str = ""


class UpdateIntegrator:
    """Integrate Windows Update packages into offline images."""

    def __init__(self, mount_point: Path):
        """
        Initialize update integrator.

        Args:
            mount_point: Path to mounted Windows image
        """
        self.mount_point = Path(mount_point)
        self.is_windows = platform.system() == 'Windows'

    def apply_update(
        self,
        update_path: Path,
        update_type: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Apply a single update to the image.

        Args:
            update_path: Path to update file (.msu, .cab, etc.)
            update_type: Type of update (auto, msu, cab, esd)

        Returns:
            Dictionary with application results

        Raises:
            OperationError: If update fails
        """
        update_path = Path(update_path)

        if not update_path.exists():
            raise OperationError(f"Update file not found: {update_path}")

        # Auto-detect update type
        if update_type == 'auto':
            update_type = update_path.suffix[1:].lower()

        logger.info(f"Applying update {update_path.name} (type: {update_type})")

        if update_type == 'msu':
            return self._apply_msu(update_path)
        elif update_type == 'cab':
            return self._apply_cab(update_path)
        else:
            raise OperationError(f"Unsupported update type: {update_type}")

    def _apply_msu(self, msu_path: Path) -> Dict[str, Any]:
        """Apply an MSU update using DISM."""
        if not self.is_windows:
            raise OperationError("MSU application requires Windows and DISM")

        cmd = [
            'dism',
            '/Image:' + str(self.mount_point),
            '/Add-Package',
            '/PackagePath:' + str(msu_path),
        ]

        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"DISM MSU application failed: {result.stderr}")

        return {
            'package': str(msu_path),
            'type': 'msu',
            'status': 'success'
        }

    def _apply_cab(self, cab_path: Path) -> Dict[str, Any]:
        """Apply a CAB update using DISM."""
        if not self.is_windows:
            raise OperationError("CAB application requires Windows and DISM")

        cmd = [
            'dism',
            '/Image:' + str(self.mount_point),
            '/Add-Package',
            '/PackagePath:' + str(cab_path),
        ]

        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"DISM CAB application failed: {result.stderr}")

        return {
            'package': str(cab_path),
            'type': 'cab',
            'status': 'success'
        }

    def apply_updates_batch(
        self,
        updates: List[UpdatePackage]
    ) -> Dict[str, Any]:
        """
        Apply multiple updates in batch.

        Args:
            updates: List of UpdatePackage objects

        Returns:
            Dictionary with batch results
        """
        results = {
            'total': len(updates),
            'successful': 0,
            'failed': 0,
            'details': []
        }

        for update in updates:
            try:
                result = self.apply_update(update.file_path, update.package_type)
                results['successful'] += 1
                results['details'].append(result)

                logger.info(f"Successfully applied {update.kb_number}")

            except Exception as e:
                logger.error(f"Failed to apply {update.kb_number}: {e}")
                results['failed'] += 1
                results['details'].append({
                    'package': str(update.file_path),
                    'kb': update.kb_number,
                    'status': 'failed',
                    'error': str(e)
                })

        return results

    def cleanup_superseded(self) -> None:
        """
        Clean up superseded components.

        Reduces image size by removing superseded updates.
        """
        if not self.is_windows:
            raise OperationError("Cleanup requires Windows and DISM")

        cmd = [
            'dism',
            '/Image:' + str(self.mount_point),
            '/Cleanup-Image',
            '/StartComponentCleanup',
            '/ResetBase',
        ]

        logger.info("Cleaning up superseded components...")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"Component cleanup failed: {result.stderr}")

        logger.info("Component cleanup completed")

    def get_packages(self) -> List[Dict[str, Any]]:
        """
        Get list of installed packages.

        Returns:
            List of package information dictionaries
        """
        if not self.is_windows:
            raise OperationError("Package listing requires Windows and DISM")

        cmd = [
            'dism',
            '/Image:' + str(self.mount_point),
            '/Get-Packages',
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"Package listing failed: {result.stderr}")

        # Parse DISM output (simplified)
        packages = []
        # TODO: Parse DISM output format properly
        packages.append({'raw_output': result.stdout})

        return packages
