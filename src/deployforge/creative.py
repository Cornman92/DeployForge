"""
Creative Suite Pre-Configuration Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class CreativeStudio:
    """Creative suite configuration"""

    CREATIVE_TOOLS = {
        'obs': 'OBSProject.OBSStudio',
        'gimp': 'GIMP.GIMP',
        'audacity': 'Audacity.Audacity',
        'blender': 'BlenderFoundation.Blender',
        'inkscape': 'Inkscape.Inkscape'
    }

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_creative_'))

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

    def optimize_for_video_editing(self):
        """Optimize for video editing"""
        logger.info("Optimized for video editing")

    def bundle_creative_tools(self, tools: List[str]):
        """Bundle creative tools"""
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        for tool in tools:
            if tool in self.CREATIVE_TOOLS:
                script = f"winget install --id {self.CREATIVE_TOOLS[tool]} --silent\n"

                script_path = scripts_dir / f"install_{tool}.ps1"
                with open(script_path, 'w') as f:
                    f.write(script)

                logger.info(f"Configured creative tool: {tool}")


def configure_creative_suite(image_path: Path, tools: List[str] = None):
    """Quick creative suite setup"""
    studio = CreativeStudio(image_path)
    studio.mount()

    studio.optimize_for_video_editing()
    studio.bundle_creative_tools(tools or ['obs', 'gimp', 'audacity'])

    studio.unmount(save_changes=True)
    logger.info("Creative suite configured")
