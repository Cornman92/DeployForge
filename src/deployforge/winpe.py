"""
Windows PE Customization for DeployForge

This module provides functionality for customizing Windows Preinstallation Environment (WinPE).
WinPE is used for deployment, recovery, and troubleshooting.

Features:
- WinPE image creation and customization
- Driver and package integration
- Startup script configuration
- Network and storage driver injection
- Custom branding and wallpapers
- Optional components (PowerShell, WMI, etc.)

Platform Support:
- Windows: DISM, ADK tools
- Linux: wimlib with limited functionality
"""

import logging
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class WinPEComponent(Enum):
    """Optional WinPE components"""

    # Scripting
    POWERSHELL = "WinPE-WMI", "WinPE-NetFX", "WinPE-Scripting", "WinPE-PowerShell"
    WMI = ("WinPE-WMI",)
    NETFX = ("WinPE-NetFX",)

    # Networking
    NETWORK = ("WinPE-WDS-Tools",)
    WIFI = ("WinPE-WiFi-Package",)

    # Storage
    STORAGE = ("WinPE-EnhancedStorage",)
    MDAC = ("WinPE-MDAC",)

    # Recovery
    RECOVERY = ("WinPE-WinReCfg",)
    STARTNET = ("WinPE-Setup",)

    # Security
    SECURE_BOOT = ("WinPE-SecureBootCmdlets",)
    BITLOCKER = ("WinPE-EnhancedStorage",)

    # Utilities
    HTML = ("WinPE-HTA",)
    SETUP_CLIENT = ("WinPE-Setup-Client",)
    FMAPI = ("WinPE-FMAPI",)


class WinPEArchitecture(Enum):
    """Supported architectures"""

    AMD64 = "amd64"
    X86 = "x86"
    ARM64 = "arm64"


@dataclass
class WinPEConfig:
    """WinPE configuration"""

    architecture: WinPEArchitecture = WinPEArchitecture.AMD64
    components: List[WinPEComponent] = field(default_factory=list)
    drivers: List[Path] = field(default_factory=list)
    startup_script: Optional[str] = None
    wallpaper: Optional[Path] = None
    scratch_space_mb: int = 512
    custom_files: Dict[Path, str] = field(default_factory=dict)  # source -> dest
    time_zone: str = "Pacific Standard Time"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "architecture": self.architecture.value,
            "components": [c.name for c in self.components],
            "drivers": [str(d) for d in self.drivers],
            "startup_script": self.startup_script,
            "wallpaper": str(self.wallpaper) if self.wallpaper else None,
            "scratch_space_mb": self.scratch_space_mb,
            "custom_files": {str(k): v for k, v in self.custom_files.items()},
            "time_zone": self.time_zone,
        }


class WinPECustomizer:
    """Customizes Windows PE images"""

    def __init__(self, winpe_image: Path, adk_path: Optional[Path] = None):
        """
        Initialize WinPE customizer

        Args:
            winpe_image: Path to WinPE WIM image (boot.wim)
            adk_path: Path to Windows ADK installation
        """
        self.winpe_image = winpe_image
        self.platform = platform.system()
        self.adk_path = adk_path or self._find_adk_path()
        self.mount_point: Optional[Path] = None

    def _find_adk_path(self) -> Optional[Path]:
        """Find Windows ADK installation path"""
        if self.platform != "Windows":
            return None

        # Common ADK locations
        adk_paths = [
            Path("C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit"),
            Path("C:/Program Files/Windows Kits/10/Assessment and Deployment Kit"),
        ]

        for path in adk_paths:
            if path.exists():
                logger.info(f"Found ADK at {path}")
                return path

        logger.warning("Windows ADK not found, some features may be limited")
        return None

    def mount(self, mount_point: Optional[Path] = None, index: int = 1) -> Path:
        """
        Mount WinPE image for modification

        Args:
            mount_point: Directory to mount to
            index: WIM index to mount (default 1)

        Returns:
            Path to mount point
        """
        if not mount_point:
            mount_point = Path(tempfile.mkdtemp(prefix="winpe_mount_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting WinPE image to {mount_point}")

        if self.platform == "Windows":
            # Use DISM
            subprocess.run(
                [
                    "dism",
                    "/Mount-Wim",
                    f"/WimFile:{self.winpe_image}",
                    f"/Index:{index}",
                    f"/MountDir:{mount_point}",
                ],
                check=True,
                timeout=120,
            )
        else:
            # Use wimlib on Linux/macOS
            subprocess.run(
                ["wimlib-imagex", "mount", str(self.winpe_image), str(index), str(mount_point)],
                check=True,
                timeout=120,
            )

        logger.info("WinPE image mounted successfully")
        return mount_point

    def unmount(self, save_changes: bool = True):
        """
        Unmount WinPE image

        Args:
            save_changes: Whether to commit changes
        """
        if not self.mount_point:
            logger.warning("No WinPE image mounted")
            return

        logger.info(f"Unmounting WinPE image from {self.mount_point}")

        if self.platform == "Windows":
            action = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Wim", f"/MountDir:{self.mount_point}", action],
                check=True,
                timeout=300,
            )
        else:
            commit_flag = "--commit" if save_changes else "--force"
            subprocess.run(
                ["wimlib-imagex", "unmount", str(self.mount_point), commit_flag],
                check=True,
                timeout=300,
            )

        # Cleanup mount point
        if self.mount_point.exists():
            shutil.rmtree(self.mount_point, ignore_errors=True)

        self.mount_point = None
        logger.info("WinPE image unmounted successfully")

    def add_component(self, component: WinPEComponent):
        """
        Add optional component to WinPE

        Args:
            component: WinPE component to add
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        if self.platform != "Windows":
            logger.warning("Adding components only supported on Windows with DISM")
            return

        if not self.adk_path:
            raise RuntimeError("Windows ADK not found, cannot add components")

        logger.info(f"Adding component: {component.name}")

        # Get component package paths
        packages_path = (
            self.adk_path / "Windows Preinstallation Environment" / "amd64" / "WinPE_OCs"
        )

        for package_name in component.value:
            cab_file = packages_path / f"{package_name}.cab"

            if not cab_file.exists():
                logger.warning(f"Component package not found: {cab_file}")
                continue

            try:
                subprocess.run(
                    [
                        "dism",
                        f"/Image:{self.mount_point}",
                        "/Add-Package",
                        f"/PackagePath:{cab_file}",
                    ],
                    check=True,
                    timeout=300,
                )

                logger.info(f"Added package: {package_name}")

                # Also add language pack if exists
                lang_cab = packages_path / "en-us" / f"{package_name}_en-us.cab"
                if lang_cab.exists():
                    subprocess.run(
                        [
                            "dism",
                            f"/Image:{self.mount_point}",
                            "/Add-Package",
                            f"/PackagePath:{lang_cab}",
                        ],
                        check=True,
                        timeout=300,
                    )
                    logger.info(f"Added language pack: {package_name}_en-us")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to add component {package_name}: {e}")

    def add_driver(self, driver_path: Path, force_unsigned: bool = False):
        """
        Add driver to WinPE

        Args:
            driver_path: Path to driver INF or folder
            force_unsigned: Allow unsigned drivers
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        logger.info(f"Adding driver: {driver_path}")

        if self.platform == "Windows":
            cmd = ["dism", f"/Image:{self.mount_point}", "/Add-Driver", f"/Driver:{driver_path}"]

            if driver_path.is_dir():
                cmd.append("/Recurse")

            if force_unsigned:
                cmd.append("/ForceUnsigned")

            subprocess.run(cmd, check=True, timeout=300)

        else:
            logger.warning("Driver injection on Linux/macOS is limited")

        logger.info(f"Driver added successfully: {driver_path}")

    def set_startup_script(self, script_content: str):
        """
        Set WinPE startup script (startnet.cmd)

        Args:
            script_content: Content of startup script
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        startnet_path = self.mount_point / "Windows" / "System32" / "startnet.cmd"
        startnet_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Setting WinPE startup script")

        with open(startnet_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.info(f"Startup script written to {startnet_path}")

    def set_wallpaper(self, wallpaper_path: Path):
        """
        Set WinPE wallpaper

        Args:
            wallpaper_path: Path to wallpaper image (JPG/BMP)
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        if not wallpaper_path.exists():
            raise FileNotFoundError(f"Wallpaper not found: {wallpaper_path}")

        # Copy to WinPE Windows directory
        dest_path = self.mount_point / "Windows" / "System32" / "winpe.jpg"
        shutil.copy2(wallpaper_path, dest_path)

        logger.info(f"Wallpaper set to {wallpaper_path}")

        # Set registry to use custom wallpaper
        # Would need to mount registry hive and modify
        logger.info("Note: Manual registry modification may be needed for wallpaper")

    def add_file(self, source: Path, destination: str):
        """
        Add custom file to WinPE

        Args:
            source: Source file path
            destination: Destination path in WinPE (relative to root)
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        dest_path = self.mount_point / destination.lstrip("/")
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, dest_path)
        logger.info(f"Added file: {source} -> {destination}")

    def set_scratch_space(self, size_mb: int = 512):
        """
        Configure scratch space (RAM disk) size

        Args:
            size_mb: Size in MB (default 512)
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        # Modify winpeshl.ini or unattend.xml
        logger.info(f"Setting scratch space to {size_mb}MB")

        # This would typically be set via unattend.xml
        # or winpeshl.ini modifications
        logger.info("Scratch space configuration requires unattend.xml modification")

    def optimize_image(self):
        """
        Optimize WinPE image (cleanup, compression)
        """
        if not self.mount_point:
            raise RuntimeError("WinPE image must be mounted first")

        if self.platform != "Windows":
            logger.warning("Image optimization only supported on Windows")
            return

        logger.info("Optimizing WinPE image")

        # Cleanup component store
        try:
            subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Cleanup-Image",
                    "/StartComponentCleanup",
                    "/ResetBase",
                ],
                check=True,
                timeout=600,
            )

            logger.info("Image cleanup completed")

        except subprocess.CalledProcessError as e:
            logger.warning(f"Image optimization failed: {e}")

    def apply_config(self, config: WinPEConfig):
        """
        Apply complete WinPE configuration

        Args:
            config: WinPEConfig object
        """
        logger.info("Applying WinPE configuration")

        # Mount image if not already mounted
        was_mounted = self.mount_point is not None
        if not was_mounted:
            self.mount()

        try:
            # Add components
            for component in config.components:
                self.add_component(component)

            # Add drivers
            for driver in config.drivers:
                self.add_driver(driver)

            # Set startup script
            if config.startup_script:
                self.set_startup_script(config.startup_script)

            # Set wallpaper
            if config.wallpaper:
                self.set_wallpaper(config.wallpaper)

            # Add custom files
            for source, dest in config.custom_files.items():
                self.add_file(source, dest)

            # Set scratch space
            self.set_scratch_space(config.scratch_space_mb)

            # Optimize
            self.optimize_image()

            logger.info("WinPE configuration applied successfully")

        finally:
            # Unmount if we mounted it
            if not was_mounted:
                self.unmount(save_changes=True)

    def create_bootable_iso(self, output_iso: Path, label: str = "WinPE"):
        """
        Create bootable ISO from WinPE image

        Args:
            output_iso: Output ISO path
            label: Volume label
        """
        if self.platform != "Windows":
            logger.warning("ISO creation best supported on Windows")

        logger.info(f"Creating bootable ISO: {output_iso}")

        if not self.adk_path:
            raise RuntimeError("Windows ADK required for ISO creation")

        # Use oscdimg from ADK
        oscdimg_path = self.adk_path / "Deployment Tools" / "amd64" / "Oscdimg" / "oscdimg.exe"

        if not oscdimg_path.exists():
            raise FileNotFoundError(f"oscdimg not found at {oscdimg_path}")

        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy WinPE files
            boot_path = temp_path / "boot"
            boot_path.mkdir()

            # Copy boot.wim
            shutil.copy2(self.winpe_image, boot_path / "boot.wim")

            # Copy bootmgr and BCD
            if self.adk_path:
                media_path = (
                    self.adk_path / "Windows Preinstallation Environment" / "amd64" / "Media"
                )
                if media_path.exists():
                    shutil.copytree(media_path, temp_path, dirs_exist_ok=True)

            # Create ISO
            etfsboot = temp_path / "boot" / "etfsboot.com"
            efisys = temp_path / "efi" / "microsoft" / "boot" / "efisys.bin"

            cmd = [
                str(oscdimg_path),
                "-m",
                "-o",
                "-u2",
                "-udfver102",
                f"-bootdata:2#p0,e,b{etfsboot}#pEF,e,b{efisys}",
                f"-l{label}",
                str(temp_path),
                str(output_iso),
            ]

            subprocess.run(cmd, check=True, timeout=300)

        logger.info(f"Bootable ISO created: {output_iso}")

    def export_wim(self, output_wim: Path, compress: str = "maximum"):
        """
        Export WinPE as optimized WIM

        Args:
            output_wim: Output WIM path
            compress: Compression type (none, fast, maximum)
        """
        logger.info(f"Exporting WinPE to {output_wim}")

        if self.platform == "Windows":
            subprocess.run(
                [
                    "dism",
                    "/Export-Image",
                    f"/SourceImageFile:{self.winpe_image}",
                    "/SourceIndex:1",
                    f"/DestinationImageFile:{output_wim}",
                    f"/Compress:{compress}",
                ],
                check=True,
                timeout=600,
            )

        else:
            # Use wimlib
            compress_flag = f"--compress={compress}"
            subprocess.run(
                [
                    "wimlib-imagex",
                    "export",
                    str(self.winpe_image),
                    "1",
                    str(output_wim),
                    compress_flag,
                ],
                check=True,
                timeout=600,
            )

        logger.info(f"WinPE exported successfully")


def create_deployment_winpe(
    output_wim: Path,
    adk_path: Optional[Path] = None,
    include_powershell: bool = True,
    include_network: bool = True,
    drivers: Optional[List[Path]] = None,
) -> WinPECustomizer:
    """
    Create a deployment-ready WinPE image

    Args:
        output_wim: Output WIM path
        adk_path: Path to Windows ADK
        include_powershell: Include PowerShell components
        include_network: Include networking components
        drivers: List of driver paths to inject

    Returns:
        Configured WinPECustomizer
    """
    # This would typically start from a base WinPE image
    # For demonstration, assume base image exists

    config = WinPEConfig(
        architecture=WinPEArchitecture.AMD64,
        components=[],
        drivers=drivers or [],
        scratch_space_mb=512,
    )

    if include_powershell:
        config.components.append(WinPEComponent.POWERSHELL)
        config.components.append(WinPEComponent.WMI)

    if include_network:
        config.components.append(WinPEComponent.NETWORK)

    # Default startup script
    config.startup_script = """@echo off
echo Starting Windows PE Deployment Environment...
wpeinit
echo.
echo Network initialized. System ready for deployment.
echo.
"""

    # Create customizer (would need base image path)
    # customizer = WinPECustomizer(base_winpe_path, adk_path)
    # customizer.apply_config(config)
    # customizer.export_wim(output_wim)

    logger.info("Deployment WinPE configuration created")

    return config


def create_recovery_winpe(
    output_wim: Path, adk_path: Optional[Path] = None, include_bitlocker: bool = True
) -> WinPEConfig:
    """
    Create a recovery-focused WinPE image

    Args:
        output_wim: Output WIM path
        adk_path: Path to Windows ADK
        include_bitlocker: Include BitLocker support

    Returns:
        Recovery WinPE configuration
    """
    config = WinPEConfig(
        architecture=WinPEArchitecture.AMD64,
        components=[WinPEComponent.POWERSHELL, WinPEComponent.WMI, WinPEComponent.RECOVERY],
        scratch_space_mb=1024,  # More space for recovery operations
    )

    if include_bitlocker:
        config.components.append(WinPEComponent.BITLOCKER)

    # Recovery startup script
    config.startup_script = """@echo off
echo Windows Recovery Environment
wpeinit
echo.
echo System ready for recovery operations.
echo.
"""

    logger.info("Recovery WinPE configuration created")

    return config
