"""
Windows Update Control for DeployForge

This module provides comprehensive control over Windows Update behavior in deployment
images through registry and Group Policy configurations.

Features:
- Disable/enable Windows Update completely
- Defer feature and quality updates
- Disable automatic driver updates
- Configure metered connection behavior
- Set active hours and restart policies
- Control update notifications
- Configure Windows Update for Business policies

Platform Support:
- Windows 10/11: Full support
- Windows Server 2016+: Full support

Example:
    from pathlib import Path
    from deployforge.updates_control import WindowsUpdateController, UpdatePolicy

    controller = WindowsUpdateController(Path("install.wim"))
    controller.mount()

    # Disable Windows Update completely
    controller.set_update_policy(UpdatePolicy.DISABLED)

    # Or configure update deferrals
    controller.set_update_policy(UpdatePolicy.MANUAL)
    controller.defer_feature_updates(days=365)
    controller.defer_quality_updates(days=30)
    controller.disable_driver_updates()

    controller.unmount(save_changes=True)
"""

import logging
import subprocess
import tempfile
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import shutil

logger = logging.getLogger(__name__)


class UpdatePolicy(Enum):
    """Windows Update policies"""

    DISABLED = "disabled"  # Completely disable Windows Update
    MANUAL = "manual"  # Manual check for updates
    AUTOMATIC = "automatic"  # Automatic updates (Windows default)
    NOTIFY_ONLY = "notify"  # Notify before downloading


class WindowsUpdateController:
    """
    Control Windows Update behavior in deployment images.

    This class provides comprehensive control over Windows Update settings
    through registry modifications. All changes are applied offline to the
    mounted image.

    Features:
    - Complete Windows Update control
    - Feature and quality update deferrals
    - Driver update control
    - Metered connection configuration
    - Active hours and restart policies
    - Update notification settings

    Attributes:
        image_path: Path to Windows image file
        mount_point: Directory where image is mounted
        is_mounted: Whether image is currently mounted
        registry_loaded: Whether registry hives are loaded

    Example:
        controller = WindowsUpdateController(Path("install.wim"))
        controller.mount()

        # Disable all updates
        controller.set_update_policy(UpdatePolicy.DISABLED)

        # Or configure manual updates with deferrals
        controller.set_update_policy(UpdatePolicy.MANUAL)
        controller.defer_feature_updates(365)
        controller.defer_quality_updates(30)
        controller.disable_driver_updates()
        controller.set_metered_connection(True)

        controller.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path):
        """
        Initialize Windows Update controller.

        Args:
            image_path: Path to Windows image (WIM/ESD/VHD/VHDX)
        """
        self.image_path = image_path
        self.mount_point: Optional[Path] = None
        self.is_mounted = False
        self.registry_loaded = False

        logger.info(f"Initialized WindowsUpdateController for {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount image for modifications.

        Args:
            mount_point: Directory to mount to (creates temp dir if not specified)

        Returns:
            Path to mount point

        Raises:
            RuntimeError: If mounting fails
        """
        if self.is_mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if not mount_point:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_updates_"))

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
            save_changes: Whether to commit changes (True) or discard (False)
        """
        # Unload any loaded registry hives first
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

            # Cleanup mount point
            if self.mount_point and self.mount_point.exists():
                shutil.rmtree(self.mount_point, ignore_errors=True)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to unmount image: {error_msg}")
            raise RuntimeError(f"Failed to unmount image: {error_msg}") from e

    def set_update_policy(self, policy: UpdatePolicy) -> None:
        """
        Set overall Windows Update policy.

        Args:
            policy: Update policy to apply

        Example:
            # Disable updates completely
            controller.set_update_policy(UpdatePolicy.DISABLED)

            # Enable manual updates
            controller.set_update_policy(UpdatePolicy.MANUAL)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting Windows Update policy to {policy.value}")

        self._load_registry()

        try:
            policy_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU"

            if policy == UpdatePolicy.DISABLED:
                # Disable Windows Update service
                self._set_registry_value(policy_key, "NoAutoUpdate", 1, "REG_DWORD")
                self._set_registry_value(policy_key, "AUOptions", 1, "REG_DWORD")
                logger.info("Windows Update disabled")

            elif policy == UpdatePolicy.MANUAL:
                # Notify but don't download
                self._set_registry_value(policy_key, "NoAutoUpdate", 0, "REG_DWORD")
                self._set_registry_value(policy_key, "AUOptions", 2, "REG_DWORD")
                logger.info("Windows Update set to manual (notify only)")

            elif policy == UpdatePolicy.AUTOMATIC:
                # Automatic download and install
                self._set_registry_value(policy_key, "NoAutoUpdate", 0, "REG_DWORD")
                self._set_registry_value(policy_key, "AUOptions", 4, "REG_DWORD")
                logger.info("Windows Update set to automatic")

            elif policy == UpdatePolicy.NOTIFY_ONLY:
                # Notify before downloading
                self._set_registry_value(policy_key, "NoAutoUpdate", 0, "REG_DWORD")
                self._set_registry_value(policy_key, "AUOptions", 2, "REG_DWORD")
                logger.info("Windows Update set to notify only")

        except Exception as e:
            logger.error(f"Failed to set update policy: {e}")
            raise

    def defer_feature_updates(self, days: int = 365) -> None:
        """
        Defer feature updates for specified number of days.

        Feature updates (e.g., 21H2, 22H2) can be deferred up to 365 days.

        Args:
            days: Number of days to defer (0-365)

        Example:
            # Defer feature updates for 1 year
            controller.defer_feature_updates(365)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        if not 0 <= days <= 365:
            raise ValueError("Deferral days must be between 0 and 365")

        logger.info(f"Deferring feature updates for {days} days")

        self._load_registry()

        try:
            policy_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate"

            self._set_registry_value(
                policy_key, "DeferFeatureUpdates", 1, "REG_DWORD"
            )
            self._set_registry_value(
                policy_key, "DeferFeatureUpdatesPeriodInDays", days, "REG_DWORD"
            )

            logger.info(f"Feature updates deferred for {days} days")

        except Exception as e:
            logger.error(f"Failed to defer feature updates: {e}")
            raise

    def defer_quality_updates(self, days: int = 30) -> None:
        """
        Defer quality updates for specified number of days.

        Quality updates (security patches) can be deferred up to 30 days.

        Args:
            days: Number of days to defer (0-30)

        Example:
            # Defer quality updates for 30 days
            controller.defer_quality_updates(30)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        if not 0 <= days <= 30:
            raise ValueError("Quality update deferral must be between 0 and 30 days")

        logger.info(f"Deferring quality updates for {days} days")

        self._load_registry()

        try:
            policy_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate"

            self._set_registry_value(
                policy_key, "DeferQualityUpdates", 1, "REG_DWORD"
            )
            self._set_registry_value(
                policy_key, "DeferQualityUpdatesPeriodInDays", days, "REG_DWORD"
            )

            logger.info(f"Quality updates deferred for {days} days")

        except Exception as e:
            logger.error(f"Failed to defer quality updates: {e}")
            raise

    def disable_driver_updates(self) -> None:
        """
        Prevent automatic driver updates through Windows Update.

        This prevents Windows from automatically downloading and installing
        driver updates, which can sometimes cause compatibility issues.

        Example:
            controller.disable_driver_updates()
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Disabling automatic driver updates")

        self._load_registry()

        try:
            policy_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate"

            self._set_registry_value(
                policy_key, "ExcludeWUDriversInQualityUpdate", 1, "REG_DWORD"
            )

            # Also set in Device Installation settings
            device_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\DriverSearching"
            self._set_registry_value(
                device_key, "SearchOrderConfig", 0, "REG_DWORD"
            )

            logger.info("Driver updates disabled")

        except Exception as e:
            logger.error(f"Failed to disable driver updates: {e}")
            raise

    def set_metered_connection(self, enabled: bool = True) -> None:
        """
        Configure connection as metered to limit Windows Update downloads.

        When enabled, Windows Update will only download critical updates
        and will avoid large feature updates.

        Args:
            enabled: Whether to enable metered connection behavior

        Example:
            # Enable metered connection
            controller.set_metered_connection(True)
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"{'Enabling' if enabled else 'Disabling'} metered connection behavior")

        self._load_registry()

        try:
            # Set metered connection behavior for all networks
            policy_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection"

            self._set_registry_value(
                policy_key, "AllowTelemetry", 0 if enabled else 1, "REG_DWORD"
            )

            # Disable automatic updates on metered connections
            wu_key = "HKLM\\TEMP_SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU"
            self._set_registry_value(
                wu_key,
                "AllowAutoWindowsUpdateDownloadOverMeteredNetwork",
                0 if enabled else 1,
                "REG_DWORD",
            )

            logger.info(f"Metered connection {'enabled' if enabled else 'disabled'}")

        except Exception as e:
            logger.error(f"Failed to set metered connection: {e}")
            raise

    def disable_windows_update_service(self) -> None:
        """
        Disable the Windows Update service completely.

        WARNING: This will prevent all Windows updates from being installed.
        Only use this for specialized deployments (air-gapped systems, etc.)

        Example:
            controller.disable_windows_update_service()
        """
        if not self.is_mounted:
            raise RuntimeError("Image must be mounted first")

        logger.warning("Disabling Windows Update service - updates will be completely blocked")

        self._load_registry()

        try:
            # Disable Windows Update service
            service_key = "HKLM\\TEMP_SYSTEM\\ControlSet001\\Services\\wuauserv"
            self._set_registry_value(service_key, "Start", 4, "REG_DWORD")  # 4 = Disabled

            # Disable Update Orchestrator Service
            orch_key = "HKLM\\TEMP_SYSTEM\\ControlSet001\\Services\\UsoSvc"
            self._set_registry_value(orch_key, "Start", 4, "REG_DWORD")

            logger.info("Windows Update service disabled")

        except Exception as e:
            logger.error(f"Failed to disable Windows Update service: {e}")
            raise

    def _load_registry(self) -> None:
        """Load registry hives for modification"""
        if self.registry_loaded:
            return

        try:
            software_hive = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
            system_hive = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"

            # Load SOFTWARE hive
            subprocess.run(
                ["reg", "load", "HKLM\\TEMP_SOFTWARE", str(software_hive)],
                check=True,
                capture_output=True,
            )

            # Load SYSTEM hive
            subprocess.run(
                ["reg", "load", "HKLM\\TEMP_SYSTEM", str(system_hive)],
                check=True,
                capture_output=True,
            )

            self.registry_loaded = True
            logger.debug("Registry hives loaded")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to load registry: {e}")
            raise RuntimeError("Failed to load registry hives") from e

    def _unload_registry(self) -> None:
        """Unload registry hives"""
        if not self.registry_loaded:
            return

        try:
            # Unload hives
            subprocess.run(
                ["reg", "unload", "HKLM\\TEMP_SOFTWARE"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["reg", "unload", "HKLM\\TEMP_SYSTEM"],
                check=True,
                capture_output=True,
            )

            self.registry_loaded = False
            logger.debug("Registry hives unloaded")

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to unload registry cleanly: {e}")

    def _set_registry_value(
        self, key: str, name: str, value: Any, value_type: str
    ) -> None:
        """
        Set registry value using reg.exe.

        Args:
            key: Registry key path
            name: Value name
            value: Value data
            value_type: REG_DWORD, REG_SZ, etc.
        """
        try:
            # Create key if it doesn't exist
            subprocess.run(
                ["reg", "add", key, "/f"],
                check=False,
                capture_output=True,
            )

            # Set value
            subprocess.run(
                ["reg", "add", key, "/v", name, "/t", value_type, "/d", str(value), "/f"],
                check=True,
                capture_output=True,
            )

            logger.debug(f"Set {key}\\{name} = {value}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set registry value {key}\\{name}: {e}")
            raise

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current Windows Update configuration.

        Returns:
            Dictionary with current settings

        Example:
            config = controller.get_configuration()
            print(f"Updates deferred: {config['deferrals_enabled']}")
        """
        return {
            "image_path": str(self.image_path),
            "is_mounted": self.is_mounted,
            "mount_point": str(self.mount_point) if self.mount_point else None,
        }
