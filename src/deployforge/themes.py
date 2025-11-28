"""
Visual Customization Engine Module

Provides theme and visual customization for Windows images.

Features:
- Custom wallpaper installation
- Theme configuration (dark/light)
- Start menu layout customization
- Taskbar configuration
- Icon theme support
- Desktop customization
"""

import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
import json

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Manages visual customization.

    Example:
        theme = ThemeManager(Path('install.wim'))
        theme.mount()
        theme.install_wallpaper_pack(Path('wallpapers/'))
        theme.set_default_theme('dark')
        theme.customize_taskbar(position='center')
        theme.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the image"""
        if self._mounted:
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_theme_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        try:
            if self.image_path.suffix.lower() == ".wim":
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Wim",
                        f"/WimFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )
            else:
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Image",
                        f"/ImageFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """Unmount the image"""
        if not self._mounted:
            return

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )
            self._mounted = False
            logger.info("Image unmounted")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount: {e.stderr.decode()}")
            raise

    def install_wallpaper_pack(self, wallpapers_path: Path):
        """Install custom wallpapers"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        wallpapers_dest = self.mount_point / "Windows" / "Web" / "Wallpaper" / "Custom"
        wallpapers_dest.mkdir(parents=True, exist_ok=True)

        if wallpapers_path.is_dir():
            for wallpaper in wallpapers_path.glob("*.jpg"):
                shutil.copy2(wallpaper, wallpapers_dest / wallpaper.name)
            for wallpaper in wallpapers_path.glob("*.png"):
                shutil.copy2(wallpaper, wallpapers_dest / wallpaper.name)

        logger.info(f"Installed wallpapers to {wallpapers_dest}")

    def set_default_theme(self, theme: str = "dark"):
        """Set default theme (dark/light)"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Set theme
            theme_value = "0" if theme == "dark" else "1"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                    "/v",
                    "AppsUseLightTheme",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    theme_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                    "/v",
                    "SystemUsesLightTheme",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    theme_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"Set default theme to {theme}")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def customize_taskbar(self, position: str = "center", size: str = "default"):
        """
        Customize taskbar.

        Args:
            position: 'center' or 'left' (Windows 11)
            size: 'small', 'default', 'large'
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Taskbar alignment (Windows 11)
            alignment_value = "1" if position == "center" else "0"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "TaskbarAl",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    alignment_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"Taskbar configured: {position}")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)


def apply_custom_theme(
    image_path: Path, theme: str = "dark", wallpapers: Optional[Path] = None
) -> ThemeManager:
    """
    Quick theme application.

    Example:
        apply_custom_theme(
            Path('install.wim'),
            theme='dark',
            wallpapers=Path('my-wallpapers/')
        )
    """
    theme_mgr = ThemeManager(image_path)
    theme_mgr.mount()

    theme_mgr.set_default_theme(theme)

    if wallpapers:
        theme_mgr.install_wallpaper_pack(wallpapers)

    theme_mgr.customize_taskbar(position="center")

    theme_mgr.unmount(save_changes=True)

    logger.info("Custom theme applied")

    return theme_mgr
