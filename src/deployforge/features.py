"""
Windows Feature Toggle Manager Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class FeatureManager:
    """Windows optional features manager"""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_feat_'))

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

    def enable(self, *features: str):
        """Enable Windows features"""
        for feature in features:
            try:
                subprocess.run([
                    'dism',
                    f'/Image:{self.mount_point}',
                    '/Enable-Feature',
                    f'/FeatureName:{feature}',
                    '/All'
                ], check=True, capture_output=True)

                logger.info(f"Enabled feature: {feature}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to enable {feature}: {e.stderr.decode()}")

    def disable(self, *features: str):
        """Disable Windows features"""
        for feature in features:
            try:
                subprocess.run([
                    'dism',
                    f'/Image:{self.mount_point}',
                    '/Disable-Feature',
                    f'/FeatureName:{feature}'
                ], check=True, capture_output=True)

                logger.info(f"Disabled feature: {feature}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to disable {feature}: {e.stderr.decode()}")


def configure_features(image_path: Path, enable: List[str] = None, disable: List[str] = None):
    """Quick feature configuration"""
    fm = FeatureManager(image_path)
    fm.mount()

    if enable:
        fm.enable(*enable)

    if disable:
        fm.disable(*disable)

    fm.unmount(save_changes=True)
    logger.info("Features configured")
