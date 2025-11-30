"""Driver injection workflows for Windows images."""

import logging
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional
import zipfile
import tarfile
import shutil

from deployforge.core.exceptions import OperationError, ValidationError


logger = logging.getLogger(__name__)


class DriverInjector:
    """
    Inject drivers into Windows images.

    Supports driver packages in various formats and automated injection.
    """

    def __init__(self, mount_point: Path):
        """
        Initialize driver injector.

        Args:
            mount_point: Path to mounted Windows image
        """
        self.mount_point = Path(mount_point)
        self.is_windows = platform.system() == "Windows"
        self.driver_store = self.mount_point / "Windows" / "System32" / "DriverStore"

    def extract_driver_package(self, package_path: Path, extract_dir: Path) -> Path:
        """
        Extract a driver package if it's an archive.

        Args:
            package_path: Path to driver package
            extract_dir: Directory to extract to

        Returns:
            Path to extracted drivers

        Raises:
            ValidationError: If package format is unsupported
        """
        package_path = Path(package_path)
        extract_dir = Path(extract_dir)
        extract_dir.mkdir(parents=True, exist_ok=True)

        # If it's already a directory, return it
        if package_path.is_dir():
            return package_path

        # Extract based on file type
        if package_path.suffix.lower() in [".zip"]:
            with zipfile.ZipFile(package_path, "r") as zf:
                zf.extractall(extract_dir)

        elif package_path.suffix.lower() in [".tar", ".gz", ".bz2", ".xz"]:
            with tarfile.open(package_path, "r:*") as tf:
                tf.extractall(extract_dir)

        elif package_path.suffix.lower() in [".cab"]:
            if self.is_windows:
                cmd = ["expand", str(package_path), "-F:*", str(extract_dir)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise OperationError(f"Failed to extract CAB: {result.stderr}")
            else:
                raise OperationError("CAB extraction requires Windows")

        elif package_path.suffix.lower() in [".exe"]:
            # Some driver packages are self-extracting
            raise ValidationError("Self-extracting EXE files must be manually extracted first")

        else:
            raise ValidationError(f"Unsupported driver package format: {package_path.suffix}")

        logger.info(f"Extracted driver package to {extract_dir}")
        return extract_dir

    def find_inf_files(self, driver_dir: Path) -> List[Path]:
        """
        Find all INF files in a driver directory.

        Args:
            driver_dir: Directory to search

        Returns:
            List of INF file paths
        """
        driver_dir = Path(driver_dir)
        inf_files = list(driver_dir.rglob("*.inf"))

        logger.info(f"Found {len(inf_files)} INF files in {driver_dir}")
        return inf_files

    def validate_driver_package(self, driver_dir: Path) -> bool:
        """
        Validate a driver package.

        Args:
            driver_dir: Driver directory to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        inf_files = self.find_inf_files(driver_dir)

        if not inf_files:
            raise ValidationError(f"No INF files found in {driver_dir}")

        # Check for suspicious files (basic security check)
        suspicious_extensions = [".exe", ".com", ".bat", ".cmd", ".ps1", ".vbs", ".js"]
        for ext in suspicious_extensions:
            suspicious_files = list(driver_dir.rglob(f"*{ext}"))
            if suspicious_files:
                logger.warning(
                    f"Found {len(suspicious_files)} {ext} files in driver package. "
                    "Review for security before injection."
                )

        return True

    def inject_drivers(
        self, driver_paths: List[Path], force_unsigned: bool = False, recurse: bool = True
    ) -> Dict[str, Any]:
        """
        Inject drivers into the image.

        Args:
            driver_paths: List of driver directory or package paths
            force_unsigned: Allow unsigned drivers
            recurse: Recursively search for INF files

        Returns:
            Dictionary with injection results

        Raises:
            OperationError: If injection fails
        """
        if not self.is_windows:
            raise OperationError("Driver injection requires Windows and DISM")

        results = {"total": len(driver_paths), "successful": 0, "failed": 0, "details": []}

        for driver_path in driver_paths:
            try:
                driver_path = Path(driver_path)
                logger.info(f"Injecting drivers from {driver_path}")

                # Extract if it's an archive
                if driver_path.is_file():
                    extract_dir = Path(tempfile.mkdtemp(prefix="deployforge_drivers_"))
                    driver_dir = self.extract_driver_package(driver_path, extract_dir)
                else:
                    driver_dir = driver_path

                # Validate
                self.validate_driver_package(driver_dir)

                # Inject using DISM
                self._inject_with_dism(driver_dir, force_unsigned, recurse)

                results["successful"] += 1
                results["details"].append({"path": str(driver_path), "status": "success"})

                logger.info(f"Successfully injected drivers from {driver_path}")

                # Cleanup temporary extraction
                if driver_path.is_file() and extract_dir.exists():
                    shutil.rmtree(extract_dir)

            except Exception as e:
                logger.error(f"Failed to inject drivers from {driver_path}: {e}")
                results["failed"] += 1
                results["details"].append(
                    {"path": str(driver_path), "status": "failed", "error": str(e)}
                )

        return results

    def _inject_with_dism(self, driver_dir: Path, force_unsigned: bool, recurse: bool) -> None:
        """Inject drivers using DISM."""
        cmd = [
            "dism",
            "/Image:" + str(self.mount_point),
            "/Add-Driver",
            "/Driver:" + str(driver_dir),
        ]

        if recurse:
            cmd.append("/Recurse")

        if force_unsigned:
            cmd.append("/ForceUnsigned")

        logger.debug(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"DISM driver injection failed: {result.stderr}")

    def list_drivers(self) -> List[Dict[str, Any]]:
        """
        List drivers currently in the image.

        Returns:
            List of driver information dictionaries
        """
        if not self.is_windows:
            raise OperationError("Listing drivers requires Windows and DISM")

        cmd = [
            "dism",
            "/Image:" + str(self.mount_point),
            "/Get-Drivers",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"DISM get drivers failed: {result.stderr}")

        # Parse DISM output (simplified)
        drivers = []
        # TODO: Parse DISM output format
        # For now, return raw output
        drivers.append({"raw_output": result.stdout})

        return drivers

    def remove_driver(self, driver_inf: str) -> None:
        """
        Remove a driver from the image.

        Args:
            driver_inf: Published name of the driver (e.g., oem0.inf)

        Raises:
            OperationError: If removal fails
        """
        if not self.is_windows:
            raise OperationError("Driver removal requires Windows and DISM")

        cmd = [
            "dism",
            "/Image:" + str(self.mount_point),
            "/Remove-Driver",
            "/Driver:" + driver_inf,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise OperationError(f"DISM driver removal failed: {result.stderr}")

        logger.info(f"Removed driver {driver_inf}")
