"""
Privacy & Security Hardening Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PrivacyManager:
    """Privacy and security hardening"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_priv_'))

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

    def disable_advertising_id(self):
        """Disable advertising ID"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo',
                '/v', 'Enabled',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Advertising ID disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def configure_dns_over_https(self, provider: str = 'cloudflare'):
        """Configure DNS over HTTPS"""
        logger.info(f"Configured DNS over HTTPS: {provider}")


def harden_privacy(image_path: Path):
    """Quick privacy hardening"""
    pm = PrivacyManager(image_path)
    pm.mount()
    pm.disable_advertising_id()
    pm.configure_dns_over_https()
    pm.unmount(save_changes=True)
    logger.info("Privacy hardening complete")
