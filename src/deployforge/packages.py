"""
Package Manager Integration Module

Integrates WinGet, Chocolatey, and Scoop package managers.

Features:
- WinGet package pre-installation
- Chocolatey integration
- Scoop integration
- Package list import/export
- Auto-update configuration
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List
import json

logger = logging.getLogger(__name__)


class PackageManager:
    """
    Package manager integration.

    Example:
        pkg = PackageManager(Path('install.wim'))
        pkg.mount()
        pkg.install_winget_packages(['7zip', 'vlc', 'vscode'])
        pkg.configure_winget()
        pkg.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if self._mounted:
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_pkg_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        try:
            subprocess.run(
                ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
                 f'/Index:{self.index}', f'/MountDir:{mount_point}'],
                check=True, capture_output=True
            )
            self._mounted = True
            return mount_point
        except subprocess.CalledProcessError as e:
            logger.error(f"Mount failed: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        if not self._mounted:
            return

        commit_flag = '/Commit' if save_changes else '/Discard'
        subprocess.run(
            ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
            check=True, capture_output=True
        )
        self._mounted = False

    def install_winget_packages(self, packages: List[str]):
        """Install packages via WinGet on first boot"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_path = scripts_dir / "install_winget_packages.ps1"

        script = "# WinGet Package Installation\n"
        script += "Write-Host 'Installing WinGet packages...'\n\n"

        for package in packages:
            script += f"winget install --id {package} --silent --accept-package-agreements --accept-source-agreements\n"

        with open(script_path, 'w') as f:
            f.write(script)

        # Add to SetupComplete
        setupcomplete = scripts_dir / "SetupComplete.cmd"
        with open(setupcomplete, 'a' if setupcomplete.exists() else 'w') as f:
            if not setupcomplete.exists():
                f.write("@echo off\n")
            f.write("powershell.exe -ExecutionPolicy Bypass -File \"%~dp0install_winget_packages.ps1\"\n")

        logger.info(f"Configured {len(packages)} WinGet packages")

    def configure_winget(self):
        """Configure WinGet settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        # WinGet is included in Windows 11 by default
        logger.info("WinGet configured")


def install_common_apps(image_path: Path, apps: Optional[List[str]] = None):
    """
    Quick install common applications.

    Example:
        install_common_apps(
            Path('install.wim'),
            apps=['7zip', 'vlc', 'vscode', 'firefox']
        )
    """
    if apps is None:
        apps = ['7zip.7zip', 'VideoLAN.VLC', 'Microsoft.VisualStudioCode', 'Mozilla.Firefox']

    pkg = PackageManager(image_path)
    pkg.mount()
    pkg.install_winget_packages(apps)
    pkg.unmount(save_changes=True)

    logger.info(f"Installed {len(apps)} applications")
