"""
Browser & Software Bundling Module
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class BrowserBundler:
    """Browser and software bundler"""

    BROWSERS = {
        'chrome': 'Google.Chrome',
        'firefox': 'Mozilla.Firefox',
        'edge': 'Microsoft.Edge',
        'brave': 'BraveSoftware.BraveBrowser'
    }

    COMMON_SOFTWARE = {
        '7zip': '7zip.7zip',
        'vlc': 'VideoLAN.VLC',
        'notepad++': 'Notepad++.Notepad++',
        'vscode': 'Microsoft.VisualStudioCode',
        'spotify': 'Spotify.Spotify',
        'discord': 'Discord.Discord'
    }

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_browser_'))

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

    def install_browser(self, browser: str, **kwargs):
        """Install browser"""
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        if browser in self.BROWSERS:
            script = f"winget install --id {self.BROWSERS[browser]} --silent\n"

            script_path = scripts_dir / f"install_{browser}.ps1"
            with open(script_path, 'w') as f:
                f.write(script)

            logger.info(f"Configured browser: {browser}")

    def bundle_common_software(self, apps: List[str]):
        """Bundle common software"""
        for app in apps:
            if app in self.COMMON_SOFTWARE:
                self.install_browser(app)


def install_browsers(image_path: Path, browsers: List[str] = None):
    """Quick browser installation"""
    bundler = BrowserBundler(image_path)
    bundler.mount()

    for browser in (browsers or ['firefox', 'chrome']):
        bundler.install_browser(browser)

    bundler.unmount(save_changes=True)
    logger.info("Browsers configured")
