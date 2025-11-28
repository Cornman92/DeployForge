"""
Windows Feature Toggle Manager Module

Comprehensive management of Windows optional features.

Features:
- WSL2 (Windows Subsystem for Linux 2)
- Hyper-V virtualization
- Windows Sandbox
- Windows Containers
- .NET Framework versions
- Internet Information Services (IIS)
- Windows Media Player
- Telnet Client/Server
- TFTP Client
- PowerShell features
- Virtual Machine Platform
- Developer Mode enablement
- Feature presets and collections
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class FeaturePreset(Enum):
    """Predefined feature collections"""

    DEVELOPER = "developer"  # WSL2, Hyper-V, Sandbox, VM Platform
    VIRTUALIZATION = "virtualization"  # Hyper-V, VM Platform, Containers
    WEB_SERVER = "web_server"  # IIS, .NET features
    MINIMAL = "minimal"  # Disable non-essential features
    ENTERPRISE = "enterprise"  # Full enterprise feature set


@dataclass
class FeatureSet:
    """Collection of related Windows features"""

    name: str
    features: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    description: str = ""

    def all_features(self) -> List[str]:
        """Get all features including dependencies"""
        return list(set(self.features + self.dependencies))


class WindowsFeatures:
    """
    Windows feature name constants for common features.

    These are the actual feature names used by DISM.
    """

    # Virtualization
    WSL = "Microsoft-Windows-Subsystem-Linux"
    VIRTUAL_MACHINE_PLATFORM = "VirtualMachinePlatform"
    HYPERV = "Microsoft-Hyper-V-All"
    HYPERV_TOOLS = "Microsoft-Hyper-V-Tools-All"
    HYPERV_PLATFORM = "Microsoft-Hyper-V"
    CONTAINERS = "Containers"
    WINDOWS_SANDBOX = "Containers-DisposableClientVM"

    # Development
    NET_FRAMEWORK_35 = "NetFx3"
    NET_FRAMEWORK_45 = "NetFx4-AdvSrvs"
    NET_FRAMEWORK_CORE = "NetFx4Extended-ASPNET45"

    # Web Server (IIS)
    IIS = "IIS-WebServer"
    IIS_MANAGEMENT_CONSOLE = "IIS-ManagementConsole"
    IIS_ASP_NET = "IIS-ASPNET"
    IIS_ASP_NET45 = "IIS-ASPNET45"

    # Network
    TELNET_CLIENT = "TelnetClient"
    TELNET_SERVER = "TelnetServer"
    TFTP_CLIENT = "TFTP"
    SMB1 = "SMB1Protocol"
    SMB_DIRECT = "SmbDirect"

    # Media
    MEDIA_PLAYER = "WindowsMediaPlayer"
    MEDIA_FEATURES = "MediaPlayback"

    # Printing
    PRINTING = "Printing-PrintToPDFServices-Features"
    PRINTING_XPS = "Printing-XPSServices-Features"

    # PowerShell
    POWERSHELL_ISE = "MicrosoftWindowsPowerShellISE"
    POWERSHELL_V2 = "MicrosoftWindowsPowerShellV2"

    # Legacy
    LEGACY_COMPONENTS = "LegacyComponents"
    DIRECT_PLAY = "DirectPlay"


class FeatureManager:
    """
    Comprehensive Windows optional features manager.

    Example:
        manager = FeatureManager(Path('install.wim'))
        manager.mount()
        manager.enable_wsl2()  # Easy WSL2 enablement
        manager.enable_hyperv()
        manager.enable_sandbox()
        manager.apply_developer_preset()
        manager.unmount(save_changes=True)
    """

    # Feature collections for common scenarios
    FEATURE_PRESETS = {
        FeaturePreset.DEVELOPER: FeatureSet(
            name="Developer",
            features=[
                WindowsFeatures.WSL,
                WindowsFeatures.VIRTUAL_MACHINE_PLATFORM,
                WindowsFeatures.HYPERV,
                WindowsFeatures.WINDOWS_SANDBOX,
                WindowsFeatures.CONTAINERS,
                WindowsFeatures.NET_FRAMEWORK_45,
            ],
            description="Full development environment with WSL2, Hyper-V, and Sandbox",
        ),
        FeaturePreset.VIRTUALIZATION: FeatureSet(
            name="Virtualization",
            features=[
                WindowsFeatures.HYPERV,
                WindowsFeatures.HYPERV_TOOLS,
                WindowsFeatures.VIRTUAL_MACHINE_PLATFORM,
                WindowsFeatures.CONTAINERS,
            ],
            description="Complete virtualization stack",
        ),
        FeaturePreset.WEB_SERVER: FeatureSet(
            name="Web Server",
            features=[
                WindowsFeatures.IIS,
                WindowsFeatures.IIS_MANAGEMENT_CONSOLE,
                WindowsFeatures.IIS_ASP_NET45,
                WindowsFeatures.NET_FRAMEWORK_45,
            ],
            description="IIS web server with ASP.NET support",
        ),
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize feature manager.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the image for modification"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_feat_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

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
        logger.info(f"Feature manager mounted at {mount_point}")
        return mount_point

    def unmount(self, save_changes: bool = True):
        """Unmount the image"""
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        commit_flag = "/Commit" if save_changes else "/Discard"
        subprocess.run(
            ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
            check=True,
            capture_output=True,
        )
        self._mounted = False
        logger.info("Feature manager unmounted")

    def enable(self, *features: str) -> bool:
        """
        Enable Windows features.

        Args:
            features: One or more feature names to enable

        Returns:
            True if all features enabled successfully
        """
        success = True
        for feature in features:
            try:
                subprocess.run(
                    [
                        "dism",
                        f"/Image:{self.mount_point}",
                        "/Enable-Feature",
                        f"/FeatureName:{feature}",
                        "/All",  # Enable all dependencies
                        "/NoRestart",
                    ],
                    check=True,
                    capture_output=True,
                )

                logger.info(f"Enabled feature: {feature}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to enable {feature}: {e.stderr.decode()}")
                success = False

        return success

    def disable(self, *features: str) -> bool:
        """
        Disable Windows features.

        Args:
            features: One or more feature names to disable

        Returns:
            True if all features disabled successfully
        """
        success = True
        for feature in features:
            try:
                subprocess.run(
                    [
                        "dism",
                        f"/Image:{self.mount_point}",
                        "/Disable-Feature",
                        f"/FeatureName:{feature}",
                        "/NoRestart",
                    ],
                    check=True,
                    capture_output=True,
                )

                logger.info(f"Disabled feature: {feature}")

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to disable {feature}: {e.stderr.decode()}")
                success = False

        return success

    def apply_preset(self, preset: FeaturePreset) -> bool:
        """
        Apply a predefined feature preset.

        Args:
            preset: FeaturePreset to apply

        Returns:
            True if all features applied successfully
        """
        feature_set = self.FEATURE_PRESETS.get(preset)
        if not feature_set:
            logger.error(f"Unknown preset: {preset}")
            return False

        logger.info(f"Applying {feature_set.name} preset: {feature_set.description}")
        return self.enable(*feature_set.all_features())

    # Convenience methods for common features
    def enable_wsl2(self) -> bool:
        """Enable Windows Subsystem for Linux 2"""
        logger.info("Enabling WSL2...")
        return self.enable(WindowsFeatures.WSL, WindowsFeatures.VIRTUAL_MACHINE_PLATFORM)

    def enable_hyperv(self) -> bool:
        """Enable Hyper-V virtualization"""
        logger.info("Enabling Hyper-V...")
        return self.enable(WindowsFeatures.HYPERV, WindowsFeatures.HYPERV_TOOLS)

    def enable_sandbox(self) -> bool:
        """Enable Windows Sandbox"""
        logger.info("Enabling Windows Sandbox...")
        return self.enable(WindowsFeatures.CONTAINERS, WindowsFeatures.WINDOWS_SANDBOX)

    def enable_containers(self) -> bool:
        """Enable Windows Containers"""
        logger.info("Enabling Windows Containers...")
        return self.enable(WindowsFeatures.CONTAINERS)

    def enable_iis(self) -> bool:
        """Enable IIS Web Server with ASP.NET"""
        logger.info("Enabling IIS Web Server...")
        return self.enable(
            WindowsFeatures.IIS,
            WindowsFeatures.IIS_MANAGEMENT_CONSOLE,
            WindowsFeatures.IIS_ASP_NET45,
        )

    def enable_dotnet_35(self) -> bool:
        """Enable .NET Framework 3.5"""
        logger.info("Enabling .NET Framework 3.5...")
        return self.enable(WindowsFeatures.NET_FRAMEWORK_35)

    def enable_dotnet_45(self) -> bool:
        """Enable .NET Framework 4.5+"""
        logger.info("Enabling .NET Framework 4.5...")
        return self.enable(WindowsFeatures.NET_FRAMEWORK_45)

    def disable_smb1(self) -> bool:
        """Disable SMB1 for security"""
        logger.info("Disabling SMB1 for security...")
        return self.disable(WindowsFeatures.SMB1)

    def disable_media_player(self) -> bool:
        """Disable Windows Media Player"""
        logger.info("Disabling Windows Media Player...")
        return self.disable(WindowsFeatures.MEDIA_PLAYER)

    def apply_developer_preset(self) -> bool:
        """Apply developer feature preset (WSL2, Hyper-V, Sandbox)"""
        return self.apply_preset(FeaturePreset.DEVELOPER)

    def apply_virtualization_preset(self) -> bool:
        """Apply virtualization feature preset"""
        return self.apply_preset(FeaturePreset.VIRTUALIZATION)

    def apply_web_server_preset(self) -> bool:
        """Apply web server feature preset"""
        return self.apply_preset(FeaturePreset.WEB_SERVER)

    def list_available_features(self) -> List[str]:
        """
        List all available features in the image.

        Returns:
            List of feature names
        """
        try:
            result = subprocess.run(
                ["dism", f"/Image:{self.mount_point}", "/Get-Features", "/Format:List"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Parse feature names from output
            features = []
            for line in result.stdout.split("\n"):
                if line.strip().startswith("Feature Name :"):
                    feature = line.split(":", 1)[1].strip()
                    features.append(feature)

            return features

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list features: {e.stderr}")
            return []

    def get_feature_state(self, feature_name: str) -> Optional[str]:
        """
        Get the state of a specific feature.

        Args:
            feature_name: Name of the feature

        Returns:
            Feature state (Enabled, Disabled, etc.) or None if not found
        """
        try:
            result = subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Get-FeatureInfo",
                    f"/FeatureName:{feature_name}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # Parse state from output
            for line in result.stdout.split("\n"):
                if line.strip().startswith("State :"):
                    return line.split(":", 1)[1].strip()

            return None

        except subprocess.CalledProcessError:
            return None


def configure_features(image_path: Path, enable: List[str] = None, disable: List[str] = None):
    """
    Quick feature configuration.

    Args:
        image_path: Path to image file
        enable: List of features to enable
        disable: List of features to disable
    """
    fm = FeatureManager(image_path)
    fm.mount()

    if enable:
        fm.enable(*enable)

    if disable:
        fm.disable(*disable)

    fm.unmount(save_changes=True)
    logger.info("Features configured")


def enable_developer_features(image_path: Path):
    """
    Quick developer feature enablement (WSL2, Hyper-V, Sandbox).

    Args:
        image_path: Path to image file
    """
    fm = FeatureManager(image_path)
    fm.mount()
    fm.apply_developer_preset()
    fm.unmount(save_changes=True)
    logger.info("Developer features enabled")
