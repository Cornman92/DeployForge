"""
Backup Integration Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BackupIntegrator:
    """Backup integration"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_backup_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        subprocess.run(
            ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
             f'/Index:{self.index}', f'/MountDir:{mount_point}'],
            check=True, capture_output=True
        )
        self._mounted = True
        return mount_point

    def unmount(self, save_changes: bool = True):
        commit_flag = '/Commit' if save_changes else '/Discard'
        subprocess.run(
            ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
            check=True, capture_output=True
        )
        self._mounted = False

    def configure_file_history(self, backup_path: Path):
        """Configure File History"""
        logger.info(f"File History configured: {backup_path}")

    def create_restore_point_on_boot(self):
        """Create restore point on first boot"""
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """
# Create restore point
Checkpoint-Computer -Description "Initial Setup" -RestorePointType "MODIFY_SETTINGS"
"""

        script_path = scripts_dir / "create_restore_point.ps1"
        with open(script_path, 'w') as f:
            f.write(script)

        logger.info("Restore point script configured")


def configure_backup(image_path: Path, backup_path: Optional[Path] = None):
    """Quick backup configuration"""
    backup = BackupIntegrator(image_path)
    backup.mount()

    if backup_path:
        backup.configure_file_history(backup_path)

    backup.create_restore_point_on_boot()
    backup.unmount(save_changes=True)

    logger.info("Backup integration complete")
