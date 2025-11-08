"""VHD/VHDX (Virtual Hard Disk) handler."""

import os
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.exceptions import MountError, OperationError


logger = logging.getLogger(__name__)


class VHDHandler(BaseImageHandler):
    """
    Handler for VHD/VHDX (Virtual Hard Disk) files.

    Uses:
    - Windows: DISM and Mount-DiskImage
    - Linux: qemu-nbd or guestfs
    - macOS: qemu-nbd
    """

    def __init__(self, image_path: Path):
        """Initialize the VHD handler."""
        super().__init__(image_path)
        self.is_windows = platform.system() == 'Windows'
        self._temp_dir = None
        self.partition = 1  # Default partition to mount

    def _check_qemu_nbd(self) -> bool:
        """Check if qemu-nbd is available."""
        try:
            result = subprocess.run(
                ['qemu-nbd', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_guestfs(self) -> bool:
        """Check if libguestfs tools are available."""
        try:
            result = subprocess.run(
                ['guestmount', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def mount(self, mount_point: Optional[Path] = None, partition: int = 1) -> Path:
        """
        Mount the VHD/VHDX.

        Args:
            mount_point: Optional custom mount point
            partition: Partition number to mount (default: 1)

        Returns:
            Path to the mount point
        """
        if self.is_mounted:
            logger.warning("Image is already mounted")
            return self.mount_point

        self.partition = partition

        try:
            # Create mount point
            if mount_point is None:
                self._temp_dir = tempfile.mkdtemp(prefix="deployforge_vhd_")
                self.mount_point = Path(self._temp_dir)
            else:
                self.mount_point = Path(mount_point)
                self.mount_point.mkdir(parents=True, exist_ok=True)

            # Mount using platform-specific method
            if self.is_windows:
                self._mount_windows()
            elif self._check_guestfs():
                self._mount_guestfs()
            elif self._check_qemu_nbd():
                self._mount_qemu_nbd()
            else:
                raise MountError(
                    "No VHD mounting tool available. "
                    "Install DISM (Windows), libguestfs, or qemu-nbd (Linux/Mac)"
                )

            self.is_mounted = True
            logger.info(f"Mounted VHD at {self.mount_point}")
            return self.mount_point

        except Exception as e:
            if self._temp_dir:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            raise MountError(f"Failed to mount VHD: {e}")

    def _mount_windows(self) -> None:
        """Mount VHD using Windows PowerShell."""
        # Mount the VHD
        ps_script = f"""
        $vhd = Mount-DiskImage -ImagePath '{self.image_path}' -PassThru
        $disk = $vhd | Get-DiskImage | Get-Disk
        $partition = Get-Partition -DiskNumber $disk.Number | Select-Object -Index {self.partition - 1}
        $volume = $partition | Get-Volume
        Write-Output $partition.DriveLetter
        """

        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise MountError(f"Failed to mount VHD: {result.stderr}")

        drive_letter = result.stdout.strip()
        # Note: On Windows, we can't easily mount to a custom path,
        # so we use the assigned drive letter
        logger.info(f"VHD mounted to drive {drive_letter}:")

    def _mount_guestfs(self) -> None:
        """Mount VHD using libguestfs (Linux)."""
        cmd = [
            'guestmount',
            '-a', str(self.image_path),
            '-m', f'/dev/sda{self.partition}',
            '--ro',  # Read-only by default
            str(self.mount_point)
        ]

        logger.debug(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise MountError(f"guestmount failed: {result.stderr}")

    def _mount_qemu_nbd(self) -> None:
        """Mount VHD using qemu-nbd (Linux/Mac)."""
        # Load nbd module
        try:
            subprocess.run(['sudo', 'modprobe', 'nbd', 'max_part=8'], check=False)
        except Exception:
            pass

        # Connect VHD to NBD device
        nbd_device = '/dev/nbd0'
        cmd = ['sudo', 'qemu-nbd', '--connect', nbd_device, str(self.image_path)]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise MountError(f"qemu-nbd connect failed: {result.stderr}")

        # Mount the partition
        partition_device = f"{nbd_device}p{self.partition}"
        mount_cmd = ['sudo', 'mount', '-o', 'ro', partition_device, str(self.mount_point)]

        result = subprocess.run(mount_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Disconnect nbd on failure
            subprocess.run(['sudo', 'qemu-nbd', '--disconnect', nbd_device], check=False)
            raise MountError(f"mount failed: {result.stderr}")

    def unmount(self, save_changes: bool = False) -> None:
        """
        Unmount the VHD.

        Args:
            save_changes: Whether to commit changes (if mounted read-write)
        """
        if not self.is_mounted:
            logger.warning("Image is not mounted")
            return

        try:
            if self.is_windows:
                self._unmount_windows()
            elif self._check_guestfs():
                self._unmount_guestfs()
            elif self._check_qemu_nbd():
                self._unmount_qemu_nbd()

            # Clean up temporary directory
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None

            self.is_mounted = False
            self.mount_point = None
            logger.info("Unmounted VHD")

        except Exception as e:
            raise MountError(f"Failed to unmount VHD: {e}")

    def _unmount_windows(self) -> None:
        """Unmount VHD using Windows PowerShell."""
        ps_script = f"Dismount-DiskImage -ImagePath '{self.image_path}'"
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise MountError(f"Failed to unmount VHD: {result.stderr}")

    def _unmount_guestfs(self) -> None:
        """Unmount using guestfs."""
        cmd = ['fusermount', '-u', str(self.mount_point)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            # Try guestunmount
            cmd = ['guestunmount', str(self.mount_point)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise MountError(f"guestunmount failed: {result.stderr}")

    def _unmount_qemu_nbd(self) -> None:
        """Unmount using qemu-nbd."""
        # Unmount filesystem
        subprocess.run(['sudo', 'umount', str(self.mount_point)], check=False)

        # Disconnect NBD
        nbd_device = '/dev/nbd0'
        subprocess.run(['sudo', 'qemu-nbd', '--disconnect', nbd_device], check=False)

    def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List files in the VHD."""
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

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
        """Add a file to the VHD."""
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            source = Path(source)
            if not source.exists():
                raise OperationError(f"Source file not found: {source}")

            dest_path = self.mount_point / destination.lstrip('/')
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source, dest_path)
            logger.info(f"Added {source} to VHD at {destination}")

        except Exception as e:
            raise OperationError(f"Failed to add file: {e}")

    def remove_file(self, path: str) -> None:
        """Remove a file from the VHD."""
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

        try:
            target_path = self.mount_point / path.lstrip('/')
            if target_path.is_file():
                target_path.unlink()
            elif target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                raise OperationError(f"Path not found: {path}")

            logger.info(f"Removed {path} from VHD")

        except Exception as e:
            raise OperationError(f"Failed to remove file: {e}")

    def extract_file(self, source: str, destination: Path) -> None:
        """Extract a file from the VHD."""
        if not self.is_mounted:
            raise MountError("Image must be mounted first")

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
        """Get information about the VHD."""
        info = {
            'path': str(self.image_path),
            'format': 'VHDX' if self.image_path.suffix.lower() == '.vhdx' else 'VHD',
            'size': self.image_path.stat().st_size,
            'mounted': self.is_mounted,
            'partition': self.partition,
        }

        return info

    def __repr__(self) -> str:
        """String representation."""
        format_type = 'VHDX' if self.image_path.suffix.lower() == '.vhdx' else 'VHD'
        return f"{format_type}Handler(image_path={self.image_path})"
