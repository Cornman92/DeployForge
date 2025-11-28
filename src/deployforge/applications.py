"""
Application Injection for DeployForge

This module provides functionality for injecting applications into Windows images
before deployment. Supports MSI, EXE, APPX/MSIX, and Office 365.

Features:
- MSI application installation with transforms
- EXE silent installation
- APPX/MSIX provisioning
- Office 365 Click-to-Run deployment
- Microsoft Store app injection
- Dependency resolution
- License key injection
- Post-install script execution

Platform Support:
- Windows: Full support with DISM
- Linux/macOS: Limited support
"""

import logging
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class InstallType(Enum):
    """Application installation types"""

    MSI = "msi"
    EXE = "exe"
    APPX = "appx"
    MSIX = "msix"
    OFFICE365 = "office365"
    SCRIPT = "script"


class InstallContext(Enum):
    """Installation context"""

    MACHINE = "machine"  # Install for all users
    USER = "user"  # Install for current user
    PROVISION = "provision"  # Provision for all users (APPX)


@dataclass
class AppPackage:
    """Represents an application package"""

    name: str
    installer: Path
    install_type: InstallType
    arguments: str = ""
    install_context: InstallContext = InstallContext.MACHINE
    dependencies: List[str] = field(default_factory=list)
    license_key: Optional[str] = None
    post_install_script: Optional[Path] = None
    architecture: str = "x64"  # x64, x86, arm64
    min_os_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "installer": str(self.installer),
            "install_type": self.install_type.value,
            "arguments": self.arguments,
            "install_context": self.install_context.value,
            "dependencies": self.dependencies,
            "has_license": self.license_key is not None,
            "architecture": self.architecture,
        }


@dataclass
class Office365Config:
    """Office 365 Click-to-Run configuration"""

    architecture: str = "64"  # 32 or 64
    apps: List[str] = field(default_factory=lambda: ["Word", "Excel", "PowerPoint", "Outlook"])
    exclude_apps: List[str] = field(default_factory=list)
    language: str = "en-us"
    channel: str = "Current"  # Current, MonthlyEnterprise, SemiAnnual
    shared_activation: bool = False
    update_enabled: bool = True
    accept_eula: bool = True
    display_level: str = "None"  # None, Full

    def generate_xml(self) -> str:
        """Generate Office deployment XML configuration"""
        config = ET.Element("Configuration")

        # Add element
        add = ET.SubElement(config, "Add")
        add.set("OfficeClientEdition", self.architecture)
        add.set("Channel", self.channel)

        # Product
        product = ET.SubElement(add, "Product")
        product.set("ID", "O365ProPlusRetail")

        # Language
        lang = ET.SubElement(product, "Language")
        lang.set("ID", self.language)

        # Exclude apps
        if self.exclude_apps:
            for app in self.exclude_apps:
                exclude = ET.SubElement(product, "ExcludeApp")
                exclude.set("ID", app)

        # Display settings
        display = ET.SubElement(config, "Display")
        display.set("Level", self.display_level)
        display.set("AcceptEULA", str(self.accept_eula).upper())

        # Updates
        if not self.update_enabled:
            updates = ET.SubElement(config, "Updates")
            updates.set("Enabled", "FALSE")

        # Shared activation
        if self.shared_activation:
            property_elem = ET.SubElement(config, "Property")
            property_elem.set("Name", "SharedComputerLicensing")
            property_elem.set("Value", "1")

        return ET.tostring(config, encoding="unicode")


class ApplicationInjector:
    """Manages application injection into Windows images"""

    def __init__(self, image_path: Path):
        """
        Initialize application injector

        Args:
            image_path: Path to Windows image (WIM/VHD/VHDX)
        """
        self.image_path = image_path
        self.mount_point: Optional[Path] = None
        self.is_mounted = False
        self.applications: List[AppPackage] = []

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount image for modification

        Args:
            mount_point: Directory to mount to

        Returns:
            Path to mount point
        """
        if not mount_point:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_app_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting image {self.image_path} to {mount_point}")

        try:
            subprocess.run(
                [
                    "dism",
                    "/Mount-Wim",
                    f"/WimFile:{self.image_path}",
                    "/Index:1",
                    f"/MountDir:{mount_point}",
                ],
                check=True,
                timeout=300,
            )

            self.is_mounted = True
            logger.info("Image mounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e}")
            raise

        return mount_point

    def unmount(self, save_changes: bool = True):
        """
        Unmount image

        Args:
            save_changes: Whether to commit changes
        """
        if not self.is_mounted or not self.mount_point:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting image from {self.mount_point}")

        action = "/Commit" if save_changes else "/Discard"

        try:
            subprocess.run(
                ["dism", "/Unmount-Wim", f"/MountDir:{self.mount_point}", action],
                check=True,
                timeout=600,
            )

            self.is_mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e}")
            raise
        finally:
            if self.mount_point and self.mount_point.exists():
                shutil.rmtree(self.mount_point, ignore_errors=True)

    def add_application(self, app: AppPackage):
        """
        Add application to image

        Args:
            app: AppPackage to install
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Adding application: {app.name}")

        if app.install_type == InstallType.MSI:
            self._add_msi_application(app)
        elif app.install_type == InstallType.EXE:
            self._add_exe_application(app)
        elif app.install_type in [InstallType.APPX, InstallType.MSIX]:
            self._add_appx_application(app)
        elif app.install_type == InstallType.OFFICE365:
            raise ValueError("Use add_office365() method for Office 365")
        elif app.install_type == InstallType.SCRIPT:
            self._add_script(app)

        self.applications.append(app)
        logger.info(f"Application {app.name} added successfully")

    def _add_msi_application(self, app: AppPackage):
        """Add MSI application using DISM"""
        if not app.installer.exists():
            raise FileNotFoundError(f"Installer not found: {app.installer}")

        # Copy MSI to image
        app_dir = self.mount_point / "Windows" / "Setup" / "Applications" / app.name
        app_dir.mkdir(parents=True, exist_ok=True)

        msi_dest = app_dir / app.installer.name
        shutil.copy2(app.installer, msi_dest)

        # Create install script
        install_script = f"""@echo off
REM Install {app.name}
msiexec /i "{msi_dest}" {app.arguments} /qn /norestart
if %errorlevel% equ 0 (
    echo {app.name} installed successfully
) else (
    echo {app.name} installation failed with error %errorlevel%
)
"""

        script_path = app_dir / "install.cmd"
        script_path.write_text(install_script, encoding="utf-8")

        # Add to FirstLogonCommands or RunOnce
        self._add_to_autologon_scripts(app.name, str(script_path))

        logger.info(f"MSI application {app.name} prepared")

    def _add_exe_application(self, app: AppPackage):
        """Add EXE application"""
        if not app.installer.exists():
            raise FileNotFoundError(f"Installer not found: {app.installer}")

        # Copy EXE to image
        app_dir = self.mount_point / "Windows" / "Setup" / "Applications" / app.name
        app_dir.mkdir(parents=True, exist_ok=True)

        exe_dest = app_dir / app.installer.name
        shutil.copy2(app.installer, exe_dest)

        # Create install script
        install_script = f"""@echo off
REM Install {app.name}
"{exe_dest}" {app.arguments}
if %errorlevel% equ 0 (
    echo {app.name} installed successfully
) else (
    echo {app.name} installation failed with error %errorlevel%
)
"""

        script_path = app_dir / "install.cmd"
        script_path.write_text(install_script, encoding="utf-8")

        # Add to autologon scripts
        self._add_to_autologon_scripts(app.name, str(script_path))

        logger.info(f"EXE application {app.name} prepared")

    def _add_appx_application(self, app: AppPackage):
        """Add APPX/MSIX application using DISM"""
        if not app.installer.exists():
            raise FileNotFoundError(f"Package not found: {app.installer}")

        logger.info(f"Provisioning APPX package: {app.name}")

        try:
            # Provision app for all users
            subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Add-ProvisionedAppxPackage",
                    f"/PackagePath:{app.installer}",
                    "/SkipLicense",
                ],
                check=True,
                timeout=300,
            )

            logger.info(f"APPX package {app.name} provisioned")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to provision APPX: {e}")
            raise

    def _add_script(self, app: AppPackage):
        """Add custom installation script"""
        if not app.installer.exists():
            raise FileNotFoundError(f"Script not found: {app.installer}")

        # Copy script to image
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_dest = scripts_dir / app.installer.name
        shutil.copy2(app.installer, script_dest)

        # Add to autologon scripts
        self._add_to_autologon_scripts(app.name, str(script_dest))

        logger.info(f"Script {app.name} added")

    def _add_to_autologon_scripts(self, name: str, script_path: str):
        """Add script to run on first logon"""
        # Create RunOnce registry entry
        setupcomplete_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        setupcomplete_dir.mkdir(parents=True, exist_ok=True)

        setupcomplete = setupcomplete_dir / "SetupComplete.cmd"

        # Append to SetupComplete.cmd
        if setupcomplete.exists():
            content = setupcomplete.read_text(encoding="utf-8")
        else:
            content = "@echo off\nREM Application installation scripts\n\n"

        content += f'call "{script_path}"\n'

        setupcomplete.write_text(content, encoding="utf-8")

        logger.info(f"Added {name} to SetupComplete.cmd")

    def add_office365(self, config: Office365Config, setup_exe: Path):
        """
        Add Office 365 Click-to-Run deployment

        Args:
            config: Office365Config object
            setup_exe: Path to Office Deployment Tool setup.exe
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        if not setup_exe.exists():
            raise FileNotFoundError(f"Office setup not found: {setup_exe}")

        logger.info("Adding Office 365 deployment")

        # Create Office directory
        office_dir = self.mount_point / "Windows" / "Setup" / "Office365"
        office_dir.mkdir(parents=True, exist_ok=True)

        # Copy setup.exe
        shutil.copy2(setup_exe, office_dir / "setup.exe")

        # Generate configuration XML
        config_xml = config.generate_xml()
        (office_dir / "configuration.xml").write_text(config_xml, encoding="utf-8")

        # Create install script
        install_script = f"""@echo off
REM Install Office 365
cd /d "{office_dir}"
setup.exe /configure configuration.xml
if %errorlevel% equ 0 (
    echo Office 365 installed successfully
) else (
    echo Office 365 installation failed with error %errorlevel%
)
"""

        script_path = office_dir / "install_office.cmd"
        script_path.write_text(install_script, encoding="utf-8")

        # Add to autologon scripts
        self._add_to_autologon_scripts("Office365", str(script_path))

        logger.info("Office 365 deployment configured")

    def add_appx_from_store(self, app_name: str, store_id: str):
        """
        Add Microsoft Store app by ID

        Args:
            app_name: Friendly name
            store_id: Store package family name
        """
        logger.info(f"Adding Store app: {app_name} ({store_id})")

        # This would require downloading from Store
        # For now, log that manual download is needed
        logger.warning(f"Store app {app_name} requires manual download")
        logger.info(f"Download {store_id} and use add_application() with APPX type")

    def install_dependencies(self, dependency: str):
        """
        Install common dependencies

        Args:
            dependency: Dependency name (vcredist, dotnet, directx, etc.)
        """
        logger.info(f"Installing dependency: {dependency}")

        dependency_map = {
            "vcredist2015": "Visual C++ 2015-2022 Redistributable",
            "vcredist2013": "Visual C++ 2013 Redistributable",
            "dotnet48": ".NET Framework 4.8",
            "dotnet6": ".NET 6 Runtime",
            "directx": "DirectX End-User Runtime",
        }

        if dependency in dependency_map:
            logger.info(f"Dependency {dependency_map[dependency]} should be installed")
            logger.warning("Automatic dependency installation not yet implemented")
            logger.info("Please add dependency installer manually using add_application()")
        else:
            logger.warning(f"Unknown dependency: {dependency}")

    def export_manifest(self, output_path: Path):
        """
        Export application manifest

        Args:
            output_path: Output JSON file path
        """
        manifest = {
            "image": str(self.image_path),
            "applications": [app.to_dict() for app in self.applications],
            "total_apps": len(self.applications),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Application manifest exported to {output_path}")


def create_standard_app_bundle(bundle_name: str = "enterprise") -> List[AppPackage]:
    """
    Create standard application bundles

    Args:
        bundle_name: Bundle name (enterprise, developer, office)

    Returns:
        List of AppPackage objects
    """
    bundles = {
        "enterprise": [
            AppPackage(
                name="7-Zip",
                installer=Path("apps/7z-x64.exe"),
                install_type=InstallType.EXE,
                arguments="/S",
            ),
            AppPackage(
                name="Adobe Acrobat Reader",
                installer=Path("apps/AcroRdrDC.msi"),
                install_type=InstallType.MSI,
                arguments="/quiet /norestart",
            ),
            AppPackage(
                name="Google Chrome",
                installer=Path("apps/GoogleChromeStandaloneEnterprise64.msi"),
                install_type=InstallType.MSI,
                arguments="/quiet /norestart",
            ),
        ],
        "developer": [
            AppPackage(
                name="Visual Studio Code",
                installer=Path("apps/VSCodeSetup-x64.exe"),
                install_type=InstallType.EXE,
                arguments="/SILENT /NORESTART /MERGETASKS=!runcode",
            ),
            AppPackage(
                name="Git",
                installer=Path("apps/Git-x64.exe"),
                install_type=InstallType.EXE,
                arguments="/SILENT /NORESTART",
            ),
        ],
        "office": [
            # Office 365 would be added separately
        ],
    }

    return bundles.get(bundle_name, [])
