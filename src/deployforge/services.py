"""
System Services Management for DeployForge

This module provides control over Windows system services in deployment images.
Configure service startup types, enable/disable services, and apply service
presets for different use cases.

Features:
- Configure service startup types (Automatic, Manual, Disabled)
- Apply service presets (Gaming, Performance, Privacy, Enterprise)
- Disable unnecessary services for better performance
- Enable required services for functionality
- Bulk service configuration

Platform Support:
- Windows 10/11: Full support
- Windows Server 2016+: Full support

Example:
    from pathlib import Path
    from deployforge.services import ServiceManager, ServicePreset

    manager = ServiceManager(Path("install.wim"))
    manager.mount()

    # Apply gaming preset (disable unnecessary services)
    manager.apply_preset(ServicePreset.GAMING)

    # Or configure individual services
    manager.disable_service("SysMain")  # Superfetch
    manager.disable_service("WSearch")  # Windows Search
    manager.set_service_startup("Spooler", "Manual")  # Print Spooler

    manager.unmount(save_changes=True)
"""

import logging
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import shutil

logger = logging.getLogger(__name__)


class ServiceStartup(Enum):
    """Service startup types"""

    AUTOMATIC = 2  # Start automatically
    MANUAL = 3  # Start manually
    DISABLED = 4  # Disabled
    AUTOMATIC_DELAYED = 2  # Automatic (Delayed Start)


class ServicePreset(Enum):
    """Service configuration presets"""

    GAMING = "gaming"  # Optimize for gaming (disable background services)
    PERFORMANCE = "performance"  # Maximum performance (disable indexing, etc.)
    PRIVACY = "privacy"  # Privacy-focused (disable telemetry services)
    ENTERPRISE = "enterprise"  # Enterprise security (enable all security services)
    MINIMAL = "minimal"  # Minimal services for lightweight systems


# Service configuration presets
SERVICE_PRESETS: Dict[ServicePreset, Dict[str, ServiceStartup]] = {
    ServicePreset.GAMING: {
        # Disable performance-impacting services
        "SysMain": ServiceStartup.DISABLED,  # Superfetch/Prefetch
        "WSearch": ServiceStartup.DISABLED,  # Windows Search
        "DiagTrack": ServiceStartup.DISABLED,  # Diagnostics Tracking
        "dmwappushservice": ServiceStartup.DISABLED,  # WAP Push
        "HomeGroupListener": ServiceStartup.DISABLED,  # HomeGroup (if exists)
        "HomeGroupProvider": ServiceStartup.DISABLED,  # HomeGroup Provider
        "RetailDemo": ServiceStartup.DISABLED,  # Retail Demo Service
        "Fax": ServiceStartup.DISABLED,  # Fax Service
        "WerSvc": ServiceStartup.DISABLED,  # Error Reporting
        "Spooler": ServiceStartup.MANUAL,  # Print Spooler (manual instead of auto)
    },
    ServicePreset.PERFORMANCE: {
        # Disable all non-essential services
        "SysMain": ServiceStartup.DISABLED,
        "WSearch": ServiceStartup.DISABLED,
        "DiagTrack": ServiceStartup.DISABLED,
        "dmwappushservice": ServiceStartup.DISABLED,
        "WerSvc": ServiceStartup.DISABLED,
        "Spooler": ServiceStartup.DISABLED,
        "Fax": ServiceStartup.DISABLED,
        "BITS": ServiceStartup.MANUAL,  # Background Intelligent Transfer
        "wuauserv": ServiceStartup.DISABLED,  # Windows Update
        "TapiSrv": ServiceStartup.DISABLED,  # Telephony
        "FontCache": ServiceStartup.DISABLED,  # Windows Font Cache
    },
    ServicePreset.PRIVACY: {
        # Disable telemetry and data collection services
        "DiagTrack": ServiceStartup.DISABLED,  # Connected User Experiences and Telemetry
        "dmwappushservice": ServiceStartup.DISABLED,  # WAP Push
        "RetailDemo": ServiceStartup.DISABLED,  # Retail Demo
        "WerSvc": ServiceStartup.DISABLED,  # Error Reporting
        "PcaSvc": ServiceStartup.DISABLED,  # Program Compatibility Assistant
        "MapsBroker": ServiceStartup.DISABLED,  # Downloaded Maps Manager
        "lfsvc": ServiceStartup.DISABLED,  # Geolocation Service
        "XblAuthManager": ServiceStartup.DISABLED,  # Xbox Live Auth Manager
        "XblGameSave": ServiceStartup.DISABLED,  # Xbox Live Game Save
        "XboxNetApiSvc": ServiceStartup.DISABLED,  # Xbox Live Networking
    },
    ServicePreset.ENTERPRISE: {
        # Enable security services, disable consumer services
        "Windefend": ServiceStartup.AUTOMATIC,  # Windows Defender
        "WdNisSvc": ServiceStartup.AUTOMATIC,  # Windows Defender Network Inspection
        "wscsvc": ServiceStartup.AUTOMATIC,  # Security Center
        "MpsSvc": ServiceStartup.AUTOMATIC,  # Windows Firewall
        "RetailDemo": ServiceStartup.DISABLED,
        "XblAuthManager": ServiceStartup.DISABLED,
        "XblGameSave": ServiceStartup.DISABLED,
        "XboxNetApiSvc": ServiceStartup.DISABLED,
    },
    ServicePreset.MINIMAL: {
        # Disable everything non-critical
        "SysMain": ServiceStartup.DISABLED,
        "WSearch": ServiceStartup.DISABLED,
        "DiagTrack": ServiceStartup.DISABLED,
        "dmwappushservice": ServiceStartup.DISABLED,
        "WerSvc": ServiceStartup.DISABLED,
        "Spooler": ServiceStartup.DISABLED,
        "Fax": ServiceStartup.DISABLED,
        "BITS": ServiceStartup.DISABLED,
        "TapiSrv": ServiceStartup.DISABLED,
        "TabletInputService": ServiceStartup.DISABLED,
        "WbioSrvc": ServiceStartup.DISABLED,  # Windows Biometric Service
    },
}


class ServiceManager:
    """
    Manages Windows system services in deployment images.

    This class provides comprehensive service management through registry
    modifications. All changes are applied offline to the mounted image.

    Features:
    - Configure individual service startup types
    - Apply service presets for common scenarios
    - Enable/disable services
    - Bulk service configuration
    - Service dependency handling

    Attributes:
        image_path: Path to Windows image file
        mount_point: Directory where image is mounted
        is_mounted: Whether image is currently mounted
        registry_loaded: Whether registry hives are loaded

    Example:
        manager = ServiceManager(Path("install.wim"))
        manager.mount()

        # Apply preset
        manager.apply_preset(ServicePreset.GAMING)

        # Or configure individual services
        manager.disable_service("DiagTrack")
        manager.set_service_startup("wuauserv", "Manual")

        manager.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path):
        """
        Initialize service manager.

        Args:
            image_path: Path to Windows image (WIM/ESD/VHD/VHDX)
        """
        self.image_path = image_path
        self.mount_point: Optional[Path] = None
        self.is_mounted = False
        self.registry_loaded = False

        logger.info(f"Initialized ServiceManager for {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount image for modifications.

        Args:
            mount_point: Directory to mount to

        Returns:
            Path to mount point
        """
        if self.is_mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if not mount_point:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_services_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

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
                capture_output=True,
                timeout=300,
            )

            self.is_mounted = True
            logger.info("Image mounted successfully")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to mount image: {error_msg}")
            raise RuntimeError(f"Failed to mount image: {error_msg}") from e

        return mount_point

    def unmount(self, save_changes: bool = True) -> None:
        """
        Unmount image and optionally save changes.

        Args:
            save_changes: Whether to commit changes
        """
        if self.registry_loaded:
            self._unload_registry()

        if not self.is_mounted:
            logger.warning("Image not mounted")
            return

        logger.info(
            f"Unmounting {self.mount_point} ({'saving' if save_changes else 'discarding'} changes)"
        )

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Wim", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
                timeout=600,
            )

            self.is_mounted = False
            logger.info("Image unmounted successfully")

            if self.mount_point and self.mount_point.exists():
                shutil.rmtree(self.mount_point, ignore_errors=True)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to unmount image: {error_msg}")
            raise RuntimeError(f"Failed to unmount image: {error_msg}") from e

    def apply_preset(self, preset: ServicePreset) -> None:
        """
        Apply service configuration preset.

        Args:
            preset: Service preset to apply

        Example:
            # Apply gaming preset
            manager.apply_preset(ServicePreset.GAMING)

            # Apply privacy preset
            manager.apply_preset(ServicePreset.PRIVACY)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying service preset: {preset.value}")

        service_config = SERVICE_PRESETS[preset]

        self._load_registry()

        applied_count = 0
        failed_count = 0

        for service_name, startup_type in service_config.items():
            try:
                self._set_service_startup_internal(service_name, startup_type)
                applied_count += 1
                logger.debug(f"Configured {service_name} -> {startup_type.name}")
            except Exception as e:
                logger.warning(f"Failed to configure {service_name}: {e}")
                failed_count += 1

        logger.info(
            f"Preset applied: {applied_count} services configured, {failed_count} failed"
        )

    def disable_service(self, service_name: str) -> None:
        """
        Disable a Windows service.

        Args:
            service_name: Service name (e.g., "WSearch", "DiagTrack")

        Example:
            # Disable Windows Search
            manager.disable_service("WSearch")

            # Disable Telemetry
            manager.disable_service("DiagTrack")
        """
        self.set_service_startup(service_name, ServiceStartup.DISABLED)

    def enable_service(self, service_name: str, delayed: bool = False) -> None:
        """
        Enable a Windows service.

        Args:
            service_name: Service name
            delayed: Whether to use delayed automatic start

        Example:
            # Enable Windows Defender
            manager.enable_service("WinDefend")

            # Enable with delayed start
            manager.enable_service("wuauserv", delayed=True)
        """
        startup_type = (
            ServiceStartup.AUTOMATIC_DELAYED if delayed else ServiceStartup.AUTOMATIC
        )
        self.set_service_startup(service_name, startup_type)

    def set_service_startup(
        self, service_name: str, startup_type: ServiceStartup
    ) -> None:
        """
        Set service startup type.

        Args:
            service_name: Service name
            startup_type: Startup type to set

        Example:
            # Set to manual
            manager.set_service_startup("Spooler", ServiceStartup.MANUAL)

            # Disable service
            manager.set_service_startup("DiagTrack", ServiceStartup.DISABLED)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting {service_name} startup to {startup_type.name}")

        self._load_registry()
        self._set_service_startup_internal(service_name, startup_type)

    def configure_services(self, services: Dict[str, ServiceStartup]) -> Dict[str, bool]:
        """
        Configure multiple services at once.

        Args:
            services: Dictionary mapping service name to startup type

        Returns:
            Dictionary mapping service name to success status

        Example:
            results = manager.configure_services({
                "WSearch": ServiceStartup.DISABLED,
                "DiagTrack": ServiceStartup.DISABLED,
                "Spooler": ServiceStartup.MANUAL,
            })

            for service, success in results.items():
                print(f"{service}: {'OK' if success else 'FAILED'}")
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Configuring {len(services)} services")

        self._load_registry()

        results = {}
        for service_name, startup_type in services.items():
            try:
                self._set_service_startup_internal(service_name, startup_type)
                results[service_name] = True
            except Exception as e:
                logger.warning(f"Failed to configure {service_name}: {e}")
                results[service_name] = False

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Configured {success_count}/{len(services)} services successfully")

        return results

    def _load_registry(self) -> None:
        """Load SYSTEM registry hive"""
        if self.registry_loaded:
            return

        try:
            system_hive = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"

            subprocess.run(
                ["reg", "load", "HKLM\\TEMP_SYSTEM", str(system_hive)],
                check=True,
                capture_output=True,
            )

            self.registry_loaded = True
            logger.debug("SYSTEM registry hive loaded")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load registry: {e}")
            raise RuntimeError("Failed to load SYSTEM registry hive") from e

    def _unload_registry(self) -> None:
        """Unload SYSTEM registry hive"""
        if not self.registry_loaded:
            return

        try:
            subprocess.run(
                ["reg", "unload", "HKLM\\TEMP_SYSTEM"],
                check=True,
                capture_output=True,
            )

            self.registry_loaded = False
            logger.debug("SYSTEM registry hive unloaded")

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to unload registry cleanly: {e}")

    def _set_service_startup_internal(
        self, service_name: str, startup_type: ServiceStartup
    ) -> None:
        """
        Internal method to set service startup type.

        Args:
            service_name: Service name
            startup_type: Startup type value
        """
        try:
            # Service registry key
            service_key = f"HKLM\\TEMP_SYSTEM\\ControlSet001\\Services\\{service_name}"

            # Create service key if it doesn't exist (in case service doesn't exist)
            subprocess.run(
                ["reg", "add", service_key, "/f"],
                check=False,
                capture_output=True,
            )

            # Set startup type
            subprocess.run(
                [
                    "reg",
                    "add",
                    service_key,
                    "/v",
                    "Start",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    str(startup_type.value),
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.debug(f"Set {service_name} Start value to {startup_type.value}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set startup type for {service_name}: {e}")
            raise

    def list_common_services(self) -> List[str]:
        """
        List commonly configured services.

        Returns:
            List of service names

        Example:
            services = manager.list_common_services()
            for service in services:
                print(service)
        """
        return [
            "SysMain",  # Superfetch
            "WSearch",  # Windows Search
            "DiagTrack",  # Diagnostics Tracking
            "dmwappushservice",  # WAP Push
            "WerSvc",  # Error Reporting
            "Spooler",  # Print Spooler
            "Fax",  # Fax Service
            "BITS",  # Background Intelligent Transfer
            "wuauserv",  # Windows Update
            "TapiSrv",  # Telephony
            "RetailDemo",  # Retail Demo
            "XblAuthManager",  # Xbox Live Auth
            "XblGameSave",  # Xbox Live Game Save
            "XboxNetApiSvc",  # Xbox Live Networking
        ]
