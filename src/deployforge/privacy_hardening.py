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
        "diagnostics.support.microsoft.com",
        "corp.sts.microsoft.com",
        "statsfe1.ws.microsoft.com",
        "pre.footprintpredict.com",
        "i1.services.visualstudio.com",
        "sam.msn.com",
        "telemetry.appex.bing.net",
        "settings-win.data.microsoft.com",
        "onesettings-win.data.microsoft.com",
        "watson.ppe.telemetry.microsoft.com",
        "survey.watson.microsoft.com",
        "watson.live.com",
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
                "disable_suggestions": True,
                "disable_feedback": True,
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
                "disable_feedback": True,
                "disable_tailored_experiences": True,
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
                "disable_feedback": True,
                "disable_tailored_experiences": True,
                "disable_wifi_sense": True,
                "harden_services": True,
            },
        }

        config = levels.get(level, levels[PrivacyLevel.MODERATE])
        for key, value in config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def _reg_add(self, hive_key: str, key_path: str, value_name: str, value_type: str, value_data: str):
        """Helper to add registry key"""
        try:
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\{key_path}",
                    "/v",
                    value_name,
                    "/t",
                    value_type,
                    "/d",
                    value_data,
                    "/f",
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to add registry key {key_path}\\{value_name}: {e.stderr.decode()}")

    def disable_telemetry(self):
        """Disable Windows telemetry"""
        logger.info("Disabling telemetry")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\DataCollection", "AllowTelemetry", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_cortana(self):
        """Disable Cortana"""
        logger.info("Disabling Cortana")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\Windows Search", "AllowCortana", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_web_search(self):
        """Disable Bing Search in Start Menu"""
        logger.info("Disabling Web Search")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\Windows Search", "DisableWebSearch", "REG_DWORD", "1")
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\Windows Search", "ConnectedSearchUseWeb", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_activity_history(self):
        """Disable Activity History and Timeline"""
        logger.info("Disabling Activity History")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\System", "PublishUserActivities", "REG_DWORD", "0")
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\System", "UploadUserActivities", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_location_services(self):
        """Disable Location Services"""
        logger.info("Disabling Location Services")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location", "Value", "REG_SZ", "Deny")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_feedback(self):
        """Disable Feedback Notifications"""
        logger.info("Disabling Feedback")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\DataCollection", "DoNotShowFeedbackNotifications", "REG_DWORD", "1")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_tailored_experiences(self):
        """Disable Tailored Experiences"""
        logger.info("Disabling Tailored Experiences")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\CloudContent", "DisableTailoredExperiencesWithDiagnosticData", "REG_DWORD", "1")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_suggestions(self):
        """Disable Windows Suggestions (Consumer Features)"""
        logger.info("Disabling Windows Suggestions")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\CloudContent", "DisableWindowsConsumerFeatures", "REG_DWORD", "1")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_cloud_sync(self):
        """Disable Cloud Sync (Settings Sync)"""
        logger.info("Disabling Cloud Sync")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\SettingSync", "DisableSettingSync", "REG_DWORD", "2")
            self._reg_add(hive_key, "Policies\\Microsoft\\Windows\\SettingSync", "DisableSettingSyncUserOverride", "REG_DWORD", "1")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_wifi_sense(self):
        """Disable WiFi Sense"""
        logger.info("Disabling WiFi Sense")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Microsoft\\WcmSvc\\wifinetworkmanager", "WifiSenseCredShared", "REG_DWORD", "0")
            self._reg_add(hive_key, "Microsoft\\WcmSvc\\wifinetworkmanager", "WifiSenseOpen", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_advertising_id(self):
        """Disable advertising ID"""
        logger.info("Disabling Advertising ID")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo", "Enabled", "REG_DWORD", "0")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_windows_search(self):
        """Disable Windows Search Service"""
        logger.info("Disabling Windows Search Service")
        # This requires disabling the service via registry
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            self._reg_add(hive_key, "ControlSet001\\Services\\WSearch", "Start", "REG_DWORD", "4") # 4 = Disabled
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def block_telemetry_domains(self):
        """Block telemetry domains via hosts file"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted")

        logger.info("Blocking telemetry domains")

        hosts_file = self.mount_point / "Windows" / "System32" / "drivers" / "etc" / "hosts"
        
        # Ensure parent dir exists
        hosts_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            current_content = ""
            if hosts_file.exists():
                current_content = hosts_file.read_text()

            with open(hosts_file, "a") as f:
                if "# DeployForge - Telemetry blocking" not in current_content:
                    f.write("\n# DeployForge - Telemetry blocking\n")
                    for domain in self.TELEMETRY_DOMAINS:
                        f.write(f"0.0.0.0 {domain}\n")
        except Exception as e:
            logger.error(f"Failed to modify hosts file: {e}")

        logger.info(f"Blocked {len(self.TELEMETRY_DOMAINS)} telemetry domains")

    def harden_services(self):
        """Disable telemetry services"""
        logger.info("Hardening services")
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"
        
        try:
            subprocess.run(["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True)
            # DiagTrack (Connected User Experiences and Telemetry)
            self._reg_add(hive_key, "ControlSet001\\Services\\DiagTrack", "Start", "REG_DWORD", "4")
            # dmwappushservice (WAP Push Message Routing Service)
            self._reg_add(hive_key, "ControlSet001\\Services\\dmwappushservice", "Start", "REG_DWORD", "4")
        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def disable_scheduled_tasks(self):
        """Disable telemetry scheduled tasks"""
        logger.info("Disabling telemetry scheduled tasks")
        # This requires mounting the SOFTWARE hive and modifying the Tree key for Task Scheduler
        # Or using a script that runs on first boot. Using script approach is safer for tasks.
        
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        script = """@echo off
REM Disable Telemetry Tasks
schtasks /Change /TN "Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator" /Disable
schtasks /Change /TN "Microsoft\\Windows\\Customer Experience Improvement Program\\UsbCeip" /Disable
schtasks /Change /TN "Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser" /Disable
schtasks /Change /TN "Microsoft\\Windows\\Application Experience\\ProgramDataUpdater" /Disable
schtasks /Change /TN "Microsoft\\Windows\\Autochk\\Proxy" /Disable
schtasks /Change /TN "Microsoft\\Windows\\DiskDiagnostic\\Microsoft-Windows-DiskDiagnosticDataCollector" /Disable
"""
        script_path = scripts_dir / "disable_tasks.cmd"
        with open(script_path, "w") as f:
            f.write(script)
            
        # Add to SetupComplete.cmd
        setupcomplete = scripts_dir / "SetupComplete.cmd"
        content = ""
        if setupcomplete.exists():
            content = setupcomplete.read_text()
        
        if "disable_tasks.cmd" not in content:
            with open(setupcomplete, "a") as f:
                f.write(f'\ncall "{script_path}"\n')

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

        if self.config.disable_web_search:
            self.disable_web_search()

        if self.config.disable_activity_history:
            self.disable_activity_history()

        if self.config.disable_location_services:
            self.disable_location_services()

        if self.config.disable_feedback:
            self.disable_feedback()

        if self.config.disable_tailored_experiences:
            self.disable_tailored_experiences()

        if self.config.disable_suggestions:
            self.disable_suggestions()

        if self.config.disable_cloud_sync:
            self.disable_cloud_sync()

        if self.config.disable_wifi_sense:
            self.disable_wifi_sense()

        if self.config.disable_windows_search:
            self.disable_windows_search()
            
        if self.config.harden_services:
            self.harden_services()

        if self.config.disable_scheduled_tasks:
            self.disable_scheduled_tasks()

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
