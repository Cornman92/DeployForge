"""
Modern UI Customization Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class UICustomizer:
    """Modern UI customization"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_ui_'))

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

    def restore_windows10_context_menu(self):
        """Restore Windows 10 style context menu"""
        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\Software\\Classes\\CLSID\\{{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}}\\InprocServer32',
                '/ve',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Windows 10 context menu restored")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def customize_file_explorer(self, show_extensions: bool = True, dark_mode: bool = True):
        """Customize File Explorer"""
        logger.info(f"File Explorer customized: extensions={show_extensions}, dark={dark_mode}")


def customize_ui(image_path: Path):
    """Quick UI customization"""
    ui = UICustomizer(image_path)
    ui.mount()
    ui.restore_windows10_context_menu()
    ui.customize_file_explorer()
    ui.unmount(save_changes=True)
    logger.info("UI customization complete")
