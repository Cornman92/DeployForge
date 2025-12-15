"""
Modern UI Customization Module

Comprehensive Windows 11/10 UI customization with profiles for taskbar, start menu,
context menus, File Explorer, themes, and visual effects.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class UIProfile(Enum):
    """Predefined UI customization profiles"""

    MODERN = "modern"  # Windows 11 modern UI with enhancements
    CLASSIC = "classic"  # Windows 10-style UI
    MINIMAL = "minimal"  # Clean, distraction-free interface
    GAMING = "gaming"  # Optimized for gaming (performance-focused UI)
    PRODUCTIVITY = "productivity"  # Professional workspace layout
    DEVELOPER = "developer"  # Developer-friendly customizations


class ThemeMode(Enum):
    """System theme modes"""

    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class TaskbarAlignment(Enum):
    """Taskbar icon alignment"""

    LEFT = "left"
    CENTER = "center"


class ExplorerView(Enum):
    """Default File Explorer view"""

    THIS_PC = "this_pc"
    QUICK_ACCESS = "quick_access"


@dataclass
class UICustomizationConfig:
    """Configuration for UI customizations"""

    # Context Menu
    windows10_context_menu: bool = True
    compact_context_menu: bool = False

    # Taskbar
    taskbar_alignment: TaskbarAlignment = TaskbarAlignment.LEFT
    show_task_view: bool = True
    show_widgets: bool = False
    show_chat: bool = False
    show_search: bool = True
    combine_taskbar_buttons: bool = True
    taskbar_size: str = "medium"  # small, medium, large

    # Start Menu
    show_recommended: bool = False
    show_recently_added: bool = True
    more_pins: bool = True
    start_menu_folders: List[str] = field(default_factory=lambda: ["Settings", "File Explorer"])

    # File Explorer
    show_file_extensions: bool = True
    show_hidden_files: bool = False
    show_full_path: bool = True
    explorer_default_view: ExplorerView = ExplorerView.THIS_PC
    disable_quick_access_history: bool = True
    compact_view: bool = False

    # Theme & Visual
    theme_mode: ThemeMode = ThemeMode.DARK
    transparency_effects: bool = True
    animations: bool = True
    accent_color_on_title_bars: bool = True

    # Performance & Visual Effects
    disable_animations: bool = False
    disable_transparency: bool = False
    disable_shadows: bool = False
    visual_effects_best_performance: bool = False

    # Desktop
    show_desktop_icons: bool = True
    show_recycle_bin: bool = True
    show_this_pc: bool = True
    show_user_files: bool = False

    # Advanced
    remove_edge_recommendations: bool = True
    disable_lockscreen_tips: bool = True
    disable_windows_spotlight: bool = True
    classic_alt_tab: bool = False
    snap_layouts: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "context_menu": {
                "windows10_style": self.windows10_context_menu,
                "compact": self.compact_context_menu,
            },
            "taskbar": {
                "alignment": self.taskbar_alignment.value,
                "task_view": self.show_task_view,
                "widgets": self.show_widgets,
                "chat": self.show_chat,
                "search": self.show_search,
                "combine_buttons": self.combine_taskbar_buttons,
                "size": self.taskbar_size,
            },
            "start_menu": {
                "recommended": self.show_recommended,
                "recently_added": self.show_recently_added,
                "more_pins": self.more_pins,
                "folders": self.start_menu_folders,
            },
            "explorer": {
                "file_extensions": self.show_file_extensions,
                "hidden_files": self.show_hidden_files,
                "full_path": self.show_full_path,
                "default_view": self.explorer_default_view.value,
                "disable_quick_access_history": self.disable_quick_access_history,
                "compact_view": self.compact_view,
            },
            "theme": {
                "mode": self.theme_mode.value,
                "transparency": self.transparency_effects,
                "animations": self.animations,
                "accent_on_title_bars": self.accent_color_on_title_bars,
            },
            "performance": {
                "disable_animations": self.disable_animations,
                "disable_transparency": self.disable_transparency,
                "disable_shadows": self.disable_shadows,
                "best_performance": self.visual_effects_best_performance,
            },
            "desktop": {
                "show_icons": self.show_desktop_icons,
                "recycle_bin": self.show_recycle_bin,
                "this_pc": self.show_this_pc,
                "user_files": self.show_user_files,
            },
            "advanced": {
                "remove_edge_recommendations": self.remove_edge_recommendations,
                "disable_lockscreen_tips": self.disable_lockscreen_tips,
                "disable_windows_spotlight": self.disable_windows_spotlight,
                "classic_alt_tab": self.classic_alt_tab,
                "snap_layouts": self.snap_layouts,
            },
        }


class UICustomizer:
    """Modern UI customization manager"""

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize UI customizer

        Args:
            image_path: Path to Windows image (WIM/ESD)
            index: Image index to customize
        """
        self.image_path = Path(image_path)
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = UICustomizationConfig()

        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")

    def mount(
        self,
        mount_point: Optional[Path] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """Mount Windows image"""
        if progress_callback:
            progress_callback("Mounting image for UI customization...")

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_ui_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        try:
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
            self._mounted = True
            logger.info(f"Image mounted at {mount_point}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e}")
            raise

        return mount_point

    def unmount(
        self, save_changes: bool = True, progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Unmount Windows image"""
        if not self._mounted:
            raise RuntimeError("Image is not mounted")

        if progress_callback:
            progress_callback("Unmounting image...")

        commit_flag = "/Commit" if save_changes else "/Discard"

        try:
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )
            self._mounted = False
            logger.info("Image unmounted successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e}")
            raise

    def apply_profile(
        self, profile: UIProfile, progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Apply predefined UI profile"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        if progress_callback:
            progress_callback(f"Applying UI profile: {profile.value}")

        if profile == UIProfile.MODERN:
            # Windows 11 modern with enhancements
            self.config.windows10_context_menu = False
            self.config.taskbar_alignment = TaskbarAlignment.CENTER
            self.config.show_widgets = True
            self.config.show_recommended = True
            self.config.theme_mode = ThemeMode.DARK
            self.config.transparency_effects = True
            self.config.animations = True
            self.config.snap_layouts = True

        elif profile == UIProfile.CLASSIC:
            # Windows 10-style
            self.config.windows10_context_menu = True
            self.config.taskbar_alignment = TaskbarAlignment.LEFT
            self.config.show_widgets = False
            self.config.show_chat = False
            self.config.theme_mode = ThemeMode.LIGHT
            self.config.classic_alt_tab = True

        elif profile == UIProfile.MINIMAL:
            # Clean interface
            self.config.windows10_context_menu = True
            self.config.compact_context_menu = True
            self.config.show_widgets = False
            self.config.show_chat = False
            self.config.show_task_view = False
            self.config.show_recommended = False
            self.config.disable_animations = True
            self.config.disable_transparency = True

        elif profile == UIProfile.GAMING:
            # Performance-focused
            self.config.windows10_context_menu = True
            self.config.theme_mode = ThemeMode.DARK
            self.config.disable_animations = True
            self.config.disable_transparency = True
            self.config.visual_effects_best_performance = True
            self.config.show_widgets = False
            self.config.show_chat = False

        elif profile == UIProfile.PRODUCTIVITY:
            # Professional workspace
            self.config.taskbar_alignment = TaskbarAlignment.LEFT
            self.config.show_file_extensions = True
            self.config.show_full_path = True
            self.config.explorer_default_view = ExplorerView.THIS_PC
            self.config.snap_layouts = True
            self.config.theme_mode = ThemeMode.DARK

        elif profile == UIProfile.DEVELOPER:
            # Developer-friendly
            self.config.windows10_context_menu = True
            self.config.show_file_extensions = True
            self.config.show_hidden_files = True
            self.config.show_full_path = True
            self.config.theme_mode = ThemeMode.DARK
            self.config.compact_view = True

        # Apply all settings
        self._apply_context_menu()
        self._apply_taskbar_settings()
        self._apply_start_menu_settings()
        self._apply_explorer_settings()
        self._apply_theme_settings()
        self._apply_performance_settings()
        self._apply_desktop_settings()
        self._apply_advanced_settings()

        logger.info(f"Applied UI profile: {profile.value}")

    def _apply_context_menu(self):
        """Apply context menu customizations"""
        if self.config.windows10_context_menu:
            self.restore_windows10_context_menu()

    def _apply_taskbar_settings(self):
        """Apply taskbar customizations"""
        self.configure_taskbar(
            alignment=self.config.taskbar_alignment,
            show_widgets=self.config.show_widgets,
            show_chat=self.config.show_chat,
        )

    def _apply_start_menu_settings(self):
        """Apply Start Menu customizations"""
        self.configure_start_menu(
            show_recommended=self.config.show_recommended, more_pins=self.config.more_pins
        )

    def _apply_explorer_settings(self):
        """Apply File Explorer customizations"""
        self.customize_file_explorer(
            show_extensions=self.config.show_file_extensions,
            show_hidden=self.config.show_hidden_files,
            show_full_path=self.config.show_full_path,
        )

    def _apply_theme_settings(self):
        """Apply theme customizations"""
        self.configure_theme(theme_mode=self.config.theme_mode)

    def _apply_performance_settings(self):
        """Apply performance-related visual settings"""
        if self.config.visual_effects_best_performance:
            self.optimize_visual_effects()

    def _apply_desktop_settings(self):
        """Apply desktop icon settings"""
        self.configure_desktop_icons(
            show_this_pc=self.config.show_this_pc,
            show_recycle_bin=self.config.show_recycle_bin,
            show_user_files=self.config.show_user_files
        )

    def _apply_advanced_settings(self):
        """Apply advanced UI settings"""
        if self.config.disable_lockscreen_tips or self.config.disable_windows_spotlight:
            self.disable_lockscreen_features()

    def restore_windows10_context_menu(self):
        """Restore Windows 10 style context menu"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Disable Windows 11 context menu
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Classes\\CLSID\\{{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}}\\InprocServer32",
                    "/ve",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Windows 10 context menu restored")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_taskbar(
        self,
        alignment: TaskbarAlignment = TaskbarAlignment.LEFT,
        show_widgets: bool = False,
        show_chat: bool = False,
    ):
        """Configure taskbar settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Taskbar alignment (0=left, 1=center)
            align_value = "1" if alignment == TaskbarAlignment.CENTER else "0"
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
                    align_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Widgets button
            widgets_value = "1" if show_widgets else "0"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "TaskbarDa",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    widgets_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Chat button
            chat_value = "1" if show_chat else "0"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "TaskbarMn",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    chat_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(
                f"Taskbar configured: alignment={alignment.value}, widgets={show_widgets}, chat={show_chat}"
            )

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_start_menu(self, show_recommended: bool = False, more_pins: bool = True):
        """Configure Start Menu layout"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Show recommended section
            rec_value = "1" if show_recommended else "0"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "Start_ShowRecommendations",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    rec_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # More pins, less recommendations
            if more_pins:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                        "/v",
                        "Start_Layout",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            logger.info(
                f"Start Menu configured: recommended={show_recommended}, more_pins={more_pins}"
            )

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def customize_file_explorer(
        self, show_extensions: bool = True, show_hidden: bool = False, show_full_path: bool = True
    ):
        """Customize File Explorer settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Show file extensions
            ext_value = "0" if show_extensions else "1"  # 0=show, 1=hide
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "HideFileExt",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    ext_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Show hidden files
            hidden_value = "1" if show_hidden else "2"  # 1=show, 2=hide
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                    "/v",
                    "Hidden",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    hidden_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Show full path in title bar
            if show_full_path:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CabinetState",
                        "/v",
                        "FullPath",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            # Default to This PC instead of Quick Access
            if self.config.explorer_default_view == ExplorerView.THIS_PC:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                        "/v",
                        "LaunchTo",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            logger.info(
                f"File Explorer customized: extensions={show_extensions}, hidden={show_hidden}"
            )

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_theme(self, theme_mode: ThemeMode = ThemeMode.DARK):
        """Configure system theme"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Dark/light mode
            if theme_mode == ThemeMode.DARK:
                # Apps dark mode
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
                        "0",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

                # System dark mode
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
                        "0",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            elif theme_mode == ThemeMode.LIGHT:
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
                        "1",
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
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            # Transparency effects
            trans_value = "1" if self.config.transparency_effects else "0"
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                    "/v",
                    "EnableTransparency",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    trans_value,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"Theme configured: mode={theme_mode.value}")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def optimize_visual_effects(self):
        """Optimize visual effects for best performance"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Disable animations
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Control Panel\\Desktop\\WindowMetrics",
                    "/v",
                    "MinAnimate",
                    "/t",
                    "REG_SZ",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Visual effects for best performance
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects",
                    "/v",
                    "VisualFXSetting",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "2",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Visual effects optimized for performance")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_lockscreen_features(self):
        """Disable lockscreen tips and spotlight"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Disable lockscreen tips
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager",
                    "/v",
                    "SubscribedContent-338387Enabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Disable Windows Spotlight
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager",
                    "/v",
                    "RotatingLockScreenEnabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Lockscreen features disabled")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_desktop_icons(
        self,
        show_this_pc: bool = True,
        show_recycle_bin: bool = True,
        show_user_files: bool = False,
    ):
        """Configure desktop icons"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Desktop icons: this_pc={show_this_pc}, recycle_bin={show_recycle_bin}")
        
        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"
        
        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )
            
            # This PC {20D04FE0-3AEA-1069-A2D8-08002B30309D}
            this_pc_val = "0" if show_this_pc else "1" # 0 = Show, 1 = Hide
            subprocess.run([
                "reg", "add",
                f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
                "/v", "{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
                "/t", "REG_DWORD", "/d", this_pc_val, "/f"
            ], check=True, capture_output=True)
            
            # Recycle Bin {645FF040-5081-101B-9F08-00AA002F954E}
            recycle_val = "0" if show_recycle_bin else "1"
            subprocess.run([
                "reg", "add",
                f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
                "/v", "{645FF040-5081-101B-9F08-00AA002F954E}",
                "/t", "REG_DWORD", "/d", recycle_val, "/f"
            ], check=True, capture_output=True)
            
            # User Files {59031a47-3f72-44a7-89c5-5595fe6b30ee}
            user_val = "0" if show_user_files else "1"
            subprocess.run([
                "reg", "add",
                f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel",
                "/v", "{59031a47-3f72-44a7-89c5-5595fe6b30ee}",
                "/t", "REG_DWORD", "/d", user_val, "/f"
            ], check=True, capture_output=True)
            
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)


def customize_ui(
    image_path: Path,
    profile: UIProfile = UIProfile.MODERN,
    progress_callback: Optional[Callable[[str], None]] = None,
):
    """
    Quick UI customization with profile

    Example:
        >>> from pathlib import Path
        >>> customize_ui(Path("install.wim"), UIProfile.GAMING)
    """
    ui = UICustomizer(image_path)
    ui.mount(progress_callback=progress_callback)
    ui.apply_profile(profile, progress_callback=progress_callback)
    ui.unmount(save_changes=True, progress_callback=progress_callback)
    logger.info("UI customization complete")
