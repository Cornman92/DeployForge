"""
Gaming Launcher Pre-Installer Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class GamingLaunchers:
    """Gaming launcher installer"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_launch_'))

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

    def install(self, launcher: str, **kwargs):
        """Install gaming launcher"""
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        launcher_ids = {
            'steam': 'Valve.Steam',
            'epic-games': 'EpicGames.EpicGamesLauncher',
            'gog-galaxy': 'GOG.Galaxy',
            'xbox-app': 'Microsoft.GamingApp'
        }

        if launcher in launcher_ids:
            script = f"winget install --id {launcher_ids[launcher]} --silent\n"

            script_path = scripts_dir / f"install_{launcher}.ps1"
            with open(script_path, 'w') as f:
                f.write(script)

            logger.info(f"Configured launcher: {launcher}")


def install_gaming_launchers(image_path: Path, launchers: List[str] = None):
    """Quick launcher installation"""
    gl = GamingLaunchers(image_path)
    gl.mount()

    for launcher in (launchers or ['steam', 'epic-games']):
        gl.install(launcher)

    gl.unmount(save_changes=True)
    logger.info("Gaming launchers configured")
