"""
Portable App Injector Module
"""

import logging
import shutil
from pathlib import Path
from typing import Optional
import tempfile
import subprocess

logger = logging.getLogger(__name__)


class PortableAppManager:
    """Portable applications manager"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_port_'))

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

    def create_portable_apps_folder(self):
        """Create portable apps folder"""
        portable_dir = self.mount_point / "PortableApps"
        portable_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created portable apps folder: {portable_dir}")
        return portable_dir

    def add_portable_app(self, app_name: str, source_path: Optional[Path] = None):
        """Add portable application"""
        portable_dir = self.create_portable_apps_folder()
        app_dir = portable_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        if source_path and source_path.exists():
            shutil.copytree(source_path, app_dir, dirs_exist_ok=True)

        logger.info(f"Added portable app: {app_name}")
