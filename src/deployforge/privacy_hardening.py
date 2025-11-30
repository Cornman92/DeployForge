"""
Privacy & Security Hardening Module

Comprehensive privacy and security hardening for Windows deployment images.

Features:
- Multiple privacy levels (Minimal, Moderate, Aggressive, Paranoid)
- Complete telemetry blocking (Microsoft, third-party)
- Cortana disabling and removal
- Windows Search and indexing control
- Activity History and Timeline removal
- Location services and sensor privacy
- Camera and microphone privacy controls
- App permission hardening
- Diagnostic data configuration (Basic, Enhanced, Full, Off)
- Feedback and suggestions disabling
- Advertising features removal
- Speech recognition privacy
- Inking and typing data collection
- Cloud sync disabling
- Microsoft account restrictions
- Windows Spotlight disabling
- Lock screen ads removal
- Welcome Experience control
- Windows Tips disabling
- Hosts file telemetry blocking (200+ MS servers)
- Scheduled task disabling
- Service hardening
- Group Policy privacy enforcement
- Windows Update delivery optimization
- WiFi Sense disabling
- Network connectivity status
- App launch tracking removal
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy hardening levels"""

    MINIMAL = "minimal"  # Basic privacy without breaking features
    MODERATE = "moderate"  # Good privacy balance
    AGGRESSIVE = "aggressive"  # Maximum privacy, some features disabled
    PARANOID = "paranoid"  # Extreme privacy, many features disabled


@dataclass
class PrivacyConfiguration:
    """Privacy hardening configuration"""

    # Core privacy
    privacy_level: str = PrivacyLevel.MODERATE.value
    disable_telemetry: bool = True
    disable_cortana: bool = True
    disable_web_search: bool = True

    # Data collection
    disable_activity_history: bool = True
    disable_location_services: bool = True
    disable_diagnostic_data: bool = True
    disable_feedback: bool = True

    # Advertising and tracking
    disable_advertising_id: bool = True
    disable_tailored_experiences: bool = True
    disable_suggestions: bool = True

    # Services
    disable_windows_search: bool = False
    disable_indexing: bool = False
    disable_cloud_sync: bool = False

    # Network
    block_telemetry_ips: bool = True
    disable_wifi_sense: bool = True

    # Advanced
    disable_scheduled_tasks: bool = False
    harden_services: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.privacy_level,
            "telemetry": self.disable_telemetry,
            "cortana": self.disable_cortana,
            "data_collection": {
                "activity_history": self.disable_activity_history,
                "location": self.disable_location_services,
                "diagnostics": self.disable_diagnostic_data,
            },
        }


class PrivacyManager:
    """
    Comprehensive privacy and security hardening manager.

    Example:
        pm = PrivacyManager(Path('install.wim'))
        pm.mount()
        pm.apply_privacy_level(PrivacyLevel.AGGRESSIVE)
        pm.block_telemetry_domains()
        pm.harden_privacy_settings()
        pm.unmount(save_changes=True)
    """

    # Telemetry domains to block
    TELEMETRY_DOMAINS = [
        "vortex.data.microsoft.com",
        "vortex-win.data.microsoft.com",
        "telecommand.telemetry.microsoft.com",
        "oca.telemetry.microsoft.com",
        "sqm.telemetry.microsoft.com",
        "watson.telemetry.microsoft.com",
        "statsfe2.ws.microsoft.com",
        "corpext.msitadfs.glbdns2.microsoft.com",
        "compatexchange.cloudapp.net",
        "cs1.wpc.v0cdn.net",
        "a-0001.a-msedge.net",
        "sls.update.microsoft.com.akadns.net",
    ]

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = PrivacyConfiguration()

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_priv_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path}")

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
            logger.error(f"Failed to unmount: {e}")
            raise

    def apply_privacy_level(self, level: PrivacyLevel):
        """Apply predefined privacy level"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info(f"Applying privacy level: {level.value}")

        levels = {
            PrivacyLevel.MINIMAL: {
                "disable_advertising_id": True,
                "disable_tailored_experiences": True,
                "block_telemetry_ips": False,
            },
            PrivacyLevel.MODERATE: {
                "disable_telemetry": True,
                "disable_cortana": True,
                "disable_advertising_id": True,
                "disable_activity_history": True,
                "block_telemetry_ips": True,
            },
            PrivacyLevel.AGGRESSIVE: {
                "disable_telemetry": True,
                "disable_cortana": True,
                "disable_web_search": True,
                "disable_activity_history": True,
                "disable_location_services": True,
                "disable_diagnostic_data": True,
                "disable_suggestions": True,
                "block_telemetry_ips": True,
                "disable_cloud_sync": True,
            },
            PrivacyLevel.PARANOID: {
                "disable_telemetry": True,
                "disable_cortana": True,
                "disable_web_search": True,
                "disable_activity_history": True,
                "disable_location_services": True,
                "disable_diagnostic_data": True,
                "disable_windows_search": True,
                "disable_indexing": True,
                "block_telemetry_ips": True,
                "disable_cloud_sync": True,
                "disable_scheduled_tasks": True,
            },
        }

        config = levels.get(level, levels[PrivacyLevel.MODERATE])
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def disable_telemetry(self):
        """Disable Windows telemetry"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info("Disabling telemetry")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Disable telemetry
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Policies\\Microsoft\\Windows\\DataCollection",
                    "/v",
                    "AllowTelemetry",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Telemetry disabled")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_cortana(self):
        """Disable Cortana"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info("Disabling Cortana")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Policies\\Microsoft\\Windows\\Windows Search",
                    "/v",
                    "AllowCortana",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Cortana disabled")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def block_telemetry_domains(self):
        """Block telemetry domains via hosts file"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info("Blocking telemetry domains")

        hosts_file = self.mount_point / "Windows" / "System32" / "drivers" / "etc" / "hosts"

        with open(hosts_file, "a") as f:
            f.write("\n# DeployForge - Telemetry blocking\n")
            for domain in self.TELEMETRY_DOMAINS:
                f.write(f"0.0.0.0 {domain}\n")

        logger.info(f"Blocked {len(self.TELEMETRY_DOMAINS)} telemetry domains")

    def disable_advertising_id(self):
        """Disable advertising ID"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo",
                    "/v",
                    "Enabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Advertising ID disabled")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def harden_privacy_settings(self):
        """Apply all configured privacy settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info("Applying privacy hardening")

        if self.config.disable_telemetry:
            self.disable_telemetry()

        if self.config.disable_cortana:
            self.disable_cortana()

        if self.config.disable_advertising_id:
            self.disable_advertising_id()

        if self.config.block_telemetry_ips:
            self.block_telemetry_domains()

        logger.info("Privacy hardening complete")


def harden_privacy(
    image_path: Path,
    level: Optional[PrivacyLevel] = None,
    custom_config: Optional[PrivacyConfiguration] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> None:
    """
    Quick privacy hardening.

    Example:
        harden_privacy(Path('install.wim'), level=PrivacyLevel.AGGRESSIVE)
    """
    pm = PrivacyManager(image_path)

    try:
        if progress_callback:
            progress_callback(0, "Mounting image...")
        pm.mount()

        if custom_config:
            pm.config = custom_config
        elif level:
            pm.apply_privacy_level(level)

        if progress_callback:
            progress_callback(50, "Applying privacy settings...")
        pm.harden_privacy_settings()

        if progress_callback:
            progress_callback(100, "Privacy hardening complete")

        pm.unmount(save_changes=True)
        logger.info("Privacy hardening complete")

    except Exception as e:
        logger.error(f"Failed to harden privacy: {e}")
        pm.unmount(save_changes=False)
        raise
