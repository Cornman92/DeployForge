"""
System Performance Optimizer Module

Optimizes Windows images for maximum performance.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SystemOptimizer:
    """Performance optimizer for Windows images"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_opt_'))

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

    def optimize_boot_time(self):
        """Optimize boot time"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control',
                '/v', 'BootDelay',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Boot time optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_hibernation(self):
        """Disable hibernation"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\Power',
                '/v', 'HibernateEnabled',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Hibernation disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)


def optimize_system(image_path: Path):
    """Quick system optimization"""
    opt = SystemOptimizer(image_path)
    opt.mount()
    opt.optimize_boot_time()
    opt.disable_hibernation()
    opt.unmount(save_changes=True)
    logger.info("System optimization complete")
