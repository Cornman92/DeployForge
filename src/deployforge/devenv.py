"""
Developer Environment Builder Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class DeveloperEnvironment:
    """Developer environment builder"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_dev_'))

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

    def install_toolchain(self, toolchain: str, version: str = 'latest'):
        """Install development toolchain"""
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = f"# Install {toolchain}\n"
        script += f"winget install --id {toolchain} --version {version} --silent\n"

        script_path = scripts_dir / f"install_{toolchain}.ps1"
        with open(script_path, 'w') as f:
            f.write(script)

        logger.info(f"Configured toolchain: {toolchain}")

    def enable_developer_mode(self):
        """Enable Windows developer mode"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\AppModelUnlock',
                '/v', 'AllowDevelopmentWithoutDevLicense',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Developer mode enabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)


def setup_dev_environment(image_path: Path, toolchains: List[str] = None):
    """Quick dev environment setup"""
    dev = DeveloperEnvironment(image_path)
    dev.mount()

    for toolchain in (toolchains or ['Python.Python.3.12', 'OpenJS.NodeJS']):
        dev.install_toolchain(toolchain)

    dev.enable_developer_mode()
    dev.unmount(save_changes=True)

    logger.info("Developer environment configured")
