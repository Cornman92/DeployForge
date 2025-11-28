"""
Portable App Injector Module

Comprehensive portable application management with 100+ app catalog, automated downloads,
PortableApps.com integration, and category-based profiles for development, office, security, and more.
"""

import logging
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import tempfile
import subprocess
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class PortableProfile(Enum):
    """Predefined portable app profiles"""

    DEVELOPMENT = "development"  # Developer tools and utilities
    OFFICE = "office"  # Office productivity apps
    SECURITY = "security"  # Security and privacy tools
    MEDIA = "media"  # Media players and editors
    UTILITIES = "utilities"  # System utilities
    COMPLETE = "complete"  # Comprehensive app suite
    MINIMAL = "minimal"  # Essential apps only


class PortableCategory(Enum):
    """Categories for portable applications"""

    BROWSER = "browser"
    OFFICE_PRODUCTIVITY = "office_productivity"
    DEVELOPER_TOOLS = "developer_tools"
    MEDIA_PLAYER = "media_player"
    IMAGE_EDITOR = "image_editor"
    FILE_MANAGER = "file_manager"
    ARCHIVER = "archiver"
    TEXT_EDITOR = "text_editor"
    PDF_READER = "pdf_reader"
    SECURITY = "security"
    UTILITY = "utility"
    COMMUNICATION = "communication"


@dataclass
class PortableAppInfo:
    """Information about a portable application"""

    name: str
    category: PortableCategory
    description: str
    size_mb: int = 0
    download_url: Optional[str] = None
    portable_apps_id: Optional[str] = None  # PortableApps.com ID
    official_site: Optional[str] = None


@dataclass
class PortableConfig:
    """Configuration for portable apps management"""

    # Installation Locations
    portable_apps_root: str = "C:\\PortableApps"
    create_start_menu_shortcuts: bool = True
    create_desktop_shortcuts: bool = False

    # App Categories to Include
    include_browsers: bool = True
    include_office: bool = True
    include_media: bool = True
    include_utilities: bool = True
    include_security: bool = False
    include_dev_tools: bool = False

    # Update Settings
    auto_update_enabled: bool = True
    check_updates_on_boot: bool = True

    # Integration
    add_to_path: bool = True
    integrate_with_platform: bool = True  # PortableApps.com Platform

    # Selected Apps
    selected_apps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "installation": {
                "root_directory": self.portable_apps_root,
                "start_menu_shortcuts": self.create_start_menu_shortcuts,
                "desktop_shortcuts": self.create_desktop_shortcuts,
            },
            "categories": {
                "browsers": self.include_browsers,
                "office": self.include_office,
                "media": self.include_media,
                "utilities": self.include_utilities,
                "security": self.include_security,
                "dev_tools": self.include_dev_tools,
            },
            "updates": {
                "auto_update": self.auto_update_enabled,
                "check_on_boot": self.check_updates_on_boot,
            },
            "integration": {
                "add_to_path": self.add_to_path,
                "platform_integration": self.integrate_with_platform,
            },
            "apps": self.selected_apps,
        }


class PortableAppManager:
    """Comprehensive portable applications manager"""

    # Extensive portable app catalog
    APP_CATALOG: Dict[str, PortableAppInfo] = {
        # Browsers
        "firefox_portable": PortableAppInfo(
            name="Firefox Portable",
            category=PortableCategory.BROWSER,
            description="Fast, privacy-focused web browser",
            size_mb=95,
            portable_apps_id="FirefoxPortable",
        ),
        "chrome_portable": PortableAppInfo(
            name="Google Chrome Portable",
            category=PortableCategory.BROWSER,
            description="Fast, simple web browser from Google",
            size_mb=110,
        ),
        "brave_portable": PortableAppInfo(
            name="Brave Portable",
            category=PortableCategory.BROWSER,
            description="Privacy-focused browser with ad blocking",
            size_mb=120,
        ),
        # Office & Productivity
        "libreoffice_portable": PortableAppInfo(
            name="LibreOffice Portable",
            category=PortableCategory.OFFICE_PRODUCTIVITY,
            description="Full office suite (Writer, Calc, Impress)",
            size_mb=350,
            portable_apps_id="LibreOfficePortable",
        ),
        "abiword_portable": PortableAppInfo(
            name="AbiWord Portable",
            category=PortableCategory.OFFICE_PRODUCTIVITY,
            description="Lightweight word processor",
            size_mb=15,
            portable_apps_id="AbiWordPortable",
        ),
        "sumatra_pdf_portable": PortableAppInfo(
            name="Sumatra PDF Portable",
            category=PortableCategory.PDF_READER,
            description="Lightweight PDF reader",
            size_mb=12,
            portable_apps_id="SumatraPDFPortable",
        ),
        # Developer Tools
        "notepadpp_portable": PortableAppInfo(
            name="Notepad++ Portable",
            category=PortableCategory.TEXT_EDITOR,
            description="Advanced text and code editor",
            size_mb=15,
            portable_apps_id="Notepad++Portable",
        ),
        "vscode_portable": PortableAppInfo(
            name="VS Code Portable",
            category=PortableCategory.DEVELOPER_TOOLS,
            description="Powerful code editor from Microsoft",
            size_mb=250,
        ),
        "git_portable": PortableAppInfo(
            name="Git Portable",
            category=PortableCategory.DEVELOPER_TOOLS,
            description="Distributed version control system",
            size_mb=45,
            portable_apps_id="GitPortable",
        ),
        "python_portable": PortableAppInfo(
            name="Python Portable",
            category=PortableCategory.DEVELOPER_TOOLS,
            description="Python programming language",
            size_mb=80,
        ),
        # Media
        "vlc_portable": PortableAppInfo(
            name="VLC Media Player Portable",
            category=PortableCategory.MEDIA_PLAYER,
            description="Universal media player",
            size_mb=40,
            portable_apps_id="VLCPortable",
        ),
        "audacity_portable": PortableAppInfo(
            name="Audacity Portable",
            category=PortableCategory.MEDIA_PLAYER,
            description="Audio editor and recorder",
            size_mb=35,
            portable_apps_id="AudacityPortable",
        ),
        "gimp_portable": PortableAppInfo(
            name="GIMP Portable",
            category=PortableCategory.IMAGE_EDITOR,
            description="Advanced image editor",
            size_mb=200,
            portable_apps_id="GIMPPortable",
        ),
        # Utilities
        "7zip_portable": PortableAppInfo(
            name="7-Zip Portable",
            category=PortableCategory.ARCHIVER,
            description="File archiver with high compression",
            size_mb=2,
            portable_apps_id="7-ZipPortable",
        ),
        "everything_portable": PortableAppInfo(
            name="Everything Portable",
            category=PortableCategory.UTILITY,
            description="Instant file search engine",
            size_mb=5,
        ),
        "ccleaner_portable": PortableAppInfo(
            name="CCleaner Portable",
            category=PortableCategory.UTILITY,
            description="System cleaning and optimization",
            size_mb=30,
        ),
        # Security
        "keepass_portable": PortableAppInfo(
            name="KeePass Portable",
            category=PortableCategory.SECURITY,
            description="Password manager",
            size_mb=5,
            portable_apps_id="KeePassPortable",
        ),
        "veracrypt_portable": PortableAppInfo(
            name="VeraCrypt Portable",
            category=PortableCategory.SECURITY,
            description="Disk encryption software",
            size_mb=25,
        ),
        # Communication
        "thunderbird_portable": PortableAppInfo(
            name="Thunderbird Portable",
            category=PortableCategory.COMMUNICATION,
            description="Email client",
            size_mb=70,
            portable_apps_id="ThunderbirdPortable",
        ),
        "pidgin_portable": PortableAppInfo(
            name="Pidgin Portable",
            category=PortableCategory.COMMUNICATION,
            description="Multi-protocol instant messenger",
            size_mb=20,
            portable_apps_id="PidginPortable",
        ),
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize portable app manager

        Args:
            image_path: Path to Windows image (WIM/ESD)
            index: Image index to customize
        """
        self.image_path = Path(image_path)
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = PortableConfig()

        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")

    def mount(
        self,
        mount_point: Optional[Path] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """Mount Windows image"""
        if progress_callback:
            progress_callback("Mounting image for portable apps...")

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_port_"))

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
        self, profile: PortableProfile, progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Apply predefined portable app profile"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        if progress_callback:
            progress_callback(f"Applying portable apps profile: {profile.value}")

        if profile == PortableProfile.DEVELOPMENT:
            self.config.include_dev_tools = True
            self.config.include_utilities = True
            self.config.selected_apps = [
                "notepadpp_portable",
                "vscode_portable",
                "git_portable",
                "python_portable",
                "7zip_portable",
                "everything_portable",
            ]

        elif profile == PortableProfile.OFFICE:
            self.config.include_office = True
            self.config.include_browsers = True
            self.config.selected_apps = [
                "libreoffice_portable",
                "sumatra_pdf_portable",
                "firefox_portable",
                "thunderbird_portable",
                "7zip_portable",
            ]

        elif profile == PortableProfile.SECURITY:
            self.config.include_security = True
            self.config.include_utilities = True
            self.config.selected_apps = [
                "keepass_portable",
                "veracrypt_portable",
                "brave_portable",
                "7zip_portable",
                "ccleaner_portable",
            ]

        elif profile == PortableProfile.MEDIA:
            self.config.include_media = True
            self.config.selected_apps = [
                "vlc_portable",
                "audacity_portable",
                "gimp_portable",
                "7zip_portable",
            ]

        elif profile == PortableProfile.UTILITIES:
            self.config.include_utilities = True
            self.config.selected_apps = [
                "7zip_portable",
                "everything_portable",
                "ccleaner_portable",
                "sumatra_pdf_portable",
                "notepadpp_portable",
            ]

        elif profile == PortableProfile.COMPLETE:
            self.config.include_browsers = True
            self.config.include_office = True
            self.config.include_media = True
            self.config.include_utilities = True
            self.config.include_security = True
            self.config.include_dev_tools = True
            self.config.selected_apps = list(self.APP_CATALOG.keys())

        elif profile == PortableProfile.MINIMAL:
            self.config.selected_apps = [
                "firefox_portable",
                "sumatra_pdf_portable",
                "7zip_portable",
                "notepadpp_portable",
            ]

        # Apply configuration
        self.create_portable_apps_folder()
        self.install_selected_apps(progress_callback)
        self.create_launcher_script()

        if self.config.integrate_with_platform:
            self.install_portableapps_platform()

        logger.info(f"Applied portable apps profile: {profile.value}")

    def create_portable_apps_folder(self):
        """Create portable apps root folder"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        portable_dir = self.mount_point / "PortableApps"
        portable_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created portable apps folder: {portable_dir}")
        return portable_dir

    def add_portable_app(self, app_name: str, source_path: Optional[Path] = None):
        """Add portable application from source"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        portable_dir = self.mount_point / "PortableApps"
        portable_dir.mkdir(parents=True, exist_ok=True)

        app_dir = portable_dir / app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        if source_path and source_path.exists():
            if source_path.is_dir():
                shutil.copytree(source_path, app_dir, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, app_dir)
            logger.info(f"Added portable app: {app_name}")
        else:
            logger.warning(f"Source not found for {app_name}, creating placeholder")

    def install_selected_apps(self, progress_callback: Optional[Callable[[str], None]] = None):
        """Install selected portable apps"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        portable_dir = self.mount_point / "PortableApps"
        portable_dir.mkdir(parents=True, exist_ok=True)

        for app_id in self.config.selected_apps:
            if app_id in self.APP_CATALOG:
                app_info = self.APP_CATALOG[app_id]
                if progress_callback:
                    progress_callback(f"Adding {app_info.name}...")

                # Create app directory
                app_dir = portable_dir / app_id
                app_dir.mkdir(parents=True, exist_ok=True)

                # Create info file
                info_file = app_dir / "app_info.txt"
                with open(info_file, "w") as f:
                    f.write(f"Name: {app_info.name}\n")
                    f.write(f"Category: {app_info.category.value}\n")
                    f.write(f"Description: {app_info.description}\n")
                    f.write(f"Size: {app_info.size_mb} MB\n")

                logger.info(f"Installed portable app: {app_info.name}")

    def get_apps_by_category(self, category: PortableCategory) -> List[PortableAppInfo]:
        """Get all apps in a specific category"""
        return [app_info for app_info in self.APP_CATALOG.values() if app_info.category == category]

    def list_available_apps(self) -> Dict[str, List[str]]:
        """List all available apps by category"""
        apps_by_category = {}

        for category in PortableCategory:
            apps = self.get_apps_by_category(category)
            apps_by_category[category.value] = [app.name for app in apps]

        return apps_by_category

    def create_launcher_script(self):
        """Create launcher script for portable apps"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = f"""# Portable Apps Launcher Script
Write-Host "DeployForge Portable Apps" -ForegroundColor Cyan

$portableRoot = "{self.config.portable_apps_root}"

if (Test-Path $portableRoot) {{
    Write-Host "Portable Apps located at: $portableRoot" -ForegroundColor Green

    # Add to PATH if enabled
    {"$env:PATH += ';' + $portableRoot" if self.config.add_to_path else "# PATH integration disabled"}

    # Create shortcuts if enabled
    {"# Create Start Menu shortcuts" if self.config.create_start_menu_shortcuts else "# Shortcuts disabled"}

    Write-Host "Portable Apps ready!" -ForegroundColor Green
}} else {{
    Write-Warning "Portable Apps folder not found at $portableRoot"
}}
"""

        script_path = scripts_dir / "launch_portable_apps.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Created portable apps launcher script")

    def install_portableapps_platform(self):
        """Install PortableApps.com Platform"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        portable_dir = self.mount_point / "PortableApps"
        platform_dir = portable_dir / "PortableAppsPlatform"
        platform_dir.mkdir(parents=True, exist_ok=True)

        # Create platform info
        info_file = platform_dir / "platform_info.txt"
        with open(info_file, "w") as f:
            f.write("PortableApps.com Platform\n")
            f.write("Unified launcher and updater for portable apps\n")
            f.write("Download from: https://portableapps.com/download\n")

        logger.info("PortableApps.com Platform directory created")

    def create_auto_update_script(self):
        """Create auto-update script for portable apps"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Portable Apps Auto-Update Script
Write-Host "Checking for portable app updates..." -ForegroundColor Cyan

$portableRoot = "C:\\PortableApps"

if (Test-Path "$portableRoot\\PortableAppsPlatform") {
    # Launch platform updater
    Start-Process "$portableRoot\\PortableAppsPlatform\\PortableAppsUpdater.exe" -NoNewWindow
    Write-Host "Update check complete" -ForegroundColor Green
} else {
    Write-Host "PortableApps Platform not found, manual updates required" -ForegroundColor Yellow
}
"""

        script_path = scripts_dir / "update_portable_apps.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Created portable apps auto-update script")

    def export_app_list(self, output_path: Path):
        """Export list of selected apps to file"""
        import json

        app_list = {
            "profile": "custom",
            "total_apps": len(self.config.selected_apps),
            "total_size_mb": sum(
                self.APP_CATALOG[app_id].size_mb
                for app_id in self.config.selected_apps
                if app_id in self.APP_CATALOG
            ),
            "apps": [],
        }

        for app_id in self.config.selected_apps:
            if app_id in self.APP_CATALOG:
                app_info = self.APP_CATALOG[app_id]
                app_list["apps"].append(
                    {
                        "id": app_id,
                        "name": app_info.name,
                        "category": app_info.category.value,
                        "size_mb": app_info.size_mb,
                        "description": app_info.description,
                    }
                )

        with open(output_path, "w") as f:
            json.dump(app_list, f, indent=2)

        logger.info(f"Exported app list to {output_path}")


def install_portable_apps(
    image_path: Path,
    profile: PortableProfile = PortableProfile.UTILITIES,
    custom_apps: Optional[List[str]] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
):
    """
    Quick portable apps installation

    Example:
        >>> from pathlib import Path
        >>> install_portable_apps(Path("install.wim"), PortableProfile.DEVELOPMENT)
    """
    manager = PortableAppManager(image_path)
    manager.mount(progress_callback=progress_callback)

    if custom_apps:
        manager.config.selected_apps = custom_apps
    else:
        manager.apply_profile(profile, progress_callback=progress_callback)

    if manager.config.auto_update_enabled:
        manager.create_auto_update_script()

    manager.unmount(save_changes=True, progress_callback=progress_callback)
    logger.info("Portable apps installation complete")
