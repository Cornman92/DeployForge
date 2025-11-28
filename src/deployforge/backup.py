"""
Backup Integration Module

Comprehensive Windows backup configuration including File History, System Image Backup,
Volume Shadow Copy, System Restore, and recovery environment setup.
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class BackupProfile(Enum):
    """Predefined backup configuration profiles"""

    AGGRESSIVE = "aggressive"  # Maximum protection with frequent backups
    MODERATE = "moderate"  # Balanced backup strategy
    MINIMAL = "minimal"  # Essential backups only
    CLOUD_ONLY = "cloud_only"  # Cloud-focused backup strategy
    ENTERPRISE = "enterprise"  # Enterprise-grade backup configuration


class BackupType(Enum):
    """Types of backup operations"""

    FILE_HISTORY = "file_history"
    SYSTEM_IMAGE = "system_image"
    SYSTEM_RESTORE = "system_restore"
    VSS = "volume_shadow_copy"
    RECOVERY = "recovery_environment"


class RecoveryMode(Enum):
    """Recovery environment modes"""

    FULL = "full"  # Complete recovery environment
    MINIMAL = "minimal"  # Minimal recovery tools
    CUSTOM = "custom"  # Custom recovery configuration


@dataclass
class BackupConfig:
    """Configuration for backup systems"""

    # File History
    enable_file_history: bool = True
    file_history_frequency: int = 60  # minutes
    file_history_retention: int = 90  # days
    file_history_versions: int = 20  # number of versions to keep

    # System Restore
    enable_system_restore: bool = True
    system_restore_disk_usage: int = 10  # percentage of disk
    create_restore_point_on_install: bool = True
    create_restore_point_on_boot: bool = True

    # Volume Shadow Copy (VSS)
    enable_vss: bool = True
    vss_max_storage: int = 10  # percentage of volume
    vss_schedule: str = "daily"  # daily, weekly, monthly

    # System Image Backup
    enable_system_image: bool = False
    system_image_schedule: str = "weekly"  # daily, weekly, monthly
    system_image_retention: int = 4  # number of images to keep

    # Recovery Environment
    enable_recovery_environment: bool = True
    recovery_mode: RecoveryMode = RecoveryMode.FULL
    include_startup_repair: bool = True
    include_system_restore: bool = True
    include_command_prompt: bool = True
    include_system_image_recovery: bool = True

    # Cloud Backup Integration
    enable_onedrive_backup: bool = False
    backup_desktop: bool = True
    backup_documents: bool = True
    backup_pictures: bool = True

    # Advanced Options
    create_bootable_recovery: bool = True
    backup_script_path: Optional[Path] = None
    backup_destination: Optional[Path] = None
    compression_enabled: bool = True
    encryption_enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "file_history": {
                "enabled": self.enable_file_history,
                "frequency_minutes": self.file_history_frequency,
                "retention_days": self.file_history_retention,
                "versions": self.file_history_versions,
            },
            "system_restore": {
                "enabled": self.enable_system_restore,
                "disk_usage_percent": self.system_restore_disk_usage,
                "restore_point_on_install": self.create_restore_point_on_install,
                "restore_point_on_boot": self.create_restore_point_on_boot,
            },
            "vss": {
                "enabled": self.enable_vss,
                "max_storage_percent": self.vss_max_storage,
                "schedule": self.vss_schedule,
            },
            "system_image": {
                "enabled": self.enable_system_image,
                "schedule": self.system_image_schedule,
                "retention": self.system_image_retention,
            },
            "recovery": {
                "enabled": self.enable_recovery_environment,
                "mode": self.recovery_mode.value,
                "startup_repair": self.include_startup_repair,
                "system_restore": self.include_system_restore,
                "command_prompt": self.include_command_prompt,
                "image_recovery": self.include_system_image_recovery,
            },
            "cloud": {
                "onedrive_backup": self.enable_onedrive_backup,
                "desktop": self.backup_desktop,
                "documents": self.backup_documents,
                "pictures": self.backup_pictures,
            },
            "advanced": {
                "bootable_recovery": self.create_bootable_recovery,
                "compression": self.compression_enabled,
                "encryption": self.encryption_enabled,
            },
        }


class BackupIntegrator:
    """Comprehensive backup integration manager"""

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize backup integrator

        Args:
            image_path: Path to Windows image (WIM/ESD)
            index: Image index to configure
        """
        self.image_path = Path(image_path)
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = BackupConfig()

        if not self.image_path.exists():
            raise FileNotFoundError(f"Image not found: {self.image_path}")

    def mount(
        self,
        mount_point: Optional[Path] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Path:
        """Mount Windows image"""
        if progress_callback:
            progress_callback("Mounting image for backup configuration...")

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_backup_"))

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
        self, profile: BackupProfile, progress_callback: Optional[Callable[[str], None]] = None
    ):
        """Apply predefined backup profile"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        if progress_callback:
            progress_callback(f"Applying backup profile: {profile.value}")

        if profile == BackupProfile.AGGRESSIVE:
            # Maximum protection
            self.config.enable_file_history = True
            self.config.file_history_frequency = 30  # Every 30 minutes
            self.config.file_history_retention = 180  # 6 months
            self.config.file_history_versions = 50
            self.config.enable_system_restore = True
            self.config.system_restore_disk_usage = 15
            self.config.create_restore_point_on_install = True
            self.config.create_restore_point_on_boot = True
            self.config.enable_vss = True
            self.config.vss_max_storage = 15
            self.config.vss_schedule = "daily"
            self.config.enable_system_image = True
            self.config.system_image_schedule = "weekly"
            self.config.enable_recovery_environment = True
            self.config.recovery_mode = RecoveryMode.FULL

        elif profile == BackupProfile.MODERATE:
            # Balanced approach
            self.config.enable_file_history = True
            self.config.file_history_frequency = 60  # Hourly
            self.config.file_history_retention = 90  # 3 months
            self.config.enable_system_restore = True
            self.config.system_restore_disk_usage = 10
            self.config.create_restore_point_on_install = True
            self.config.enable_vss = True
            self.config.vss_max_storage = 10
            self.config.enable_recovery_environment = True
            self.config.recovery_mode = RecoveryMode.FULL

        elif profile == BackupProfile.MINIMAL:
            # Essential only
            self.config.enable_file_history = False
            self.config.enable_system_restore = True
            self.config.system_restore_disk_usage = 5
            self.config.create_restore_point_on_install = True
            self.config.enable_vss = True
            self.config.vss_max_storage = 5
            self.config.enable_recovery_environment = True
            self.config.recovery_mode = RecoveryMode.MINIMAL

        elif profile == BackupProfile.CLOUD_ONLY:
            # Cloud-focused
            self.config.enable_file_history = False
            self.config.enable_onedrive_backup = True
            self.config.backup_desktop = True
            self.config.backup_documents = True
            self.config.backup_pictures = True
            self.config.enable_system_restore = True
            self.config.system_restore_disk_usage = 5
            self.config.enable_recovery_environment = True

        elif profile == BackupProfile.ENTERPRISE:
            # Enterprise-grade
            self.config.enable_file_history = True
            self.config.file_history_frequency = 60
            self.config.enable_system_restore = True
            self.config.system_restore_disk_usage = 10
            self.config.enable_vss = True
            self.config.vss_schedule = "daily"
            self.config.enable_system_image = True
            self.config.system_image_schedule = "weekly"
            self.config.enable_recovery_environment = True
            self.config.recovery_mode = RecoveryMode.FULL
            self.config.encryption_enabled = True

        # Apply all backup configurations
        if self.config.enable_system_restore:
            self.configure_system_restore()

        if self.config.enable_vss:
            self.configure_vss()

        if self.config.create_restore_point_on_boot:
            self.create_restore_point_on_boot()

        if self.config.enable_recovery_environment:
            self.configure_recovery_environment()

        if self.config.enable_file_history:
            self.configure_file_history_defaults()

        logger.info(f"Applied backup profile: {profile.value}")

    def configure_system_restore(self):
        """Configure System Restore settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable System Restore
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore",
                    "/v",
                    "DisableSR",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Set disk usage
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore",
                    "/v",
                    "DiskPercent",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    str(self.config.system_restore_disk_usage),
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(
                f"System Restore configured: {self.config.system_restore_disk_usage}% disk usage"
            )

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_vss(self):
        """Configure Volume Shadow Copy Service"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable VSS
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Services\\VSS",
                    "/v",
                    "Start",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "2",
                    "/f",  # Automatic
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"VSS configured: {self.config.vss_schedule} schedule")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def create_restore_point_on_boot(self):
        """Create restore point on first boot"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Create initial restore point
try {
    Enable-ComputerRestore -Drive "C:\\"
    Checkpoint-Computer -Description "Initial Setup - DeployForge" -RestorePointType "MODIFY_SETTINGS"
    Write-Host "Restore point created successfully"
} catch {
    Write-Warning "Failed to create restore point: $_"
}
"""

        script_path = scripts_dir / "create_restore_point.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Restore point creation script configured")

    def configure_file_history(self, backup_path: Path):
        """Configure File History with specific backup location"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        if not backup_path:
            logger.warning("No backup path specified for File History")
            return

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = f"""# Configure File History
try {{
    # Enable File History
    fhmanagew.exe -enable

    # Set backup location
    fhmanagew.exe -configure -target "{backup_path}"

    # Set frequency (in minutes)
    fhmanagew.exe -configure -frequency {self.config.file_history_frequency}

    Write-Host "File History configured successfully"
}} catch {{
    Write-Warning "Failed to configure File History: $_"
}}
"""

        script_path = scripts_dir / "configure_file_history.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info(f"File History configured: {backup_path}")

    def configure_file_history_defaults(self):
        """Configure File History default settings"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable File History
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\FileHistory",
                    "/v",
                    "Disabled",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("File History defaults configured")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_recovery_environment(self):
        """Configure Windows Recovery Environment"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        # Create recovery configuration script
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Configure Recovery Environment
try {
    # Enable Windows Recovery Environment
    reagentc /enable

    # Set recovery options
    reagentc /setreimage /path "C:\\Recovery\\WindowsRE"

    Write-Host "Recovery environment configured successfully"
} catch {
    Write-Warning "Failed to configure recovery environment: $_"
}
"""

        script_path = scripts_dir / "configure_recovery.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info(f"Recovery environment configured: {self.config.recovery_mode.value}")

    def configure_onedrive_backup(self):
        """Configure OneDrive folder backup"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable OneDrive folder backup
            if self.config.enable_onedrive_backup:
                folders = []
                if self.config.backup_desktop:
                    folders.append("Desktop")
                if self.config.backup_documents:
                    folders.append("Documents")
                if self.config.backup_pictures:
                    folders.append("Pictures")

                for folder in folders:
                    subprocess.run(
                        [
                            "reg",
                            "add",
                            f"{hive_key}\\Software\\Microsoft\\OneDrive\\Accounts\\Business1",
                            "/v",
                            f"{folder}FolderBackup",
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
                f"OneDrive backup configured for: {', '.join(folders) if folders else 'none'}"
            )

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def create_backup_schedule(self, backup_type: BackupType, schedule: str = "weekly"):
        """Create scheduled task for backup operations"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Map backup types to commands
        backup_commands = {
            BackupType.SYSTEM_IMAGE: "wbadmin start backup -backupTarget:E: -include:C: -quiet",
            BackupType.FILE_HISTORY: "fhmanagew.exe -backup now",
            BackupType.SYSTEM_RESTORE: "Checkpoint-Computer -Description 'Scheduled Backup' -RestorePointType MODIFY_SETTINGS",
        }

        if backup_type not in backup_commands:
            logger.warning(f"Unsupported backup type: {backup_type}")
            return

        # Create scheduled task script
        task_name = f"DeployForge_{backup_type.value}"
        command = backup_commands[backup_type]

        script = f"""# Create backup scheduled task
$trigger = New-ScheduledTaskTrigger -Weekly -At 2AM -DaysOfWeek Sunday
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command {command}"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "{task_name}" -Trigger $trigger -Action $action -Settings $settings -Description "DeployForge {backup_type.value} backup"
"""

        script_path = scripts_dir / f"schedule_{backup_type.value}.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info(f"Backup schedule created: {backup_type.value} - {schedule}")

    def enable_backup_compression(self):
        """Enable backup compression to save space"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable backup compression
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\WindowsBackup",
                    "/v",
                    "CompressBackup",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Backup compression enabled")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def configure_startup_recovery(self):
        """Configure advanced startup recovery options"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "BCD-Template"

        # Configure boot options for easier recovery access
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Configure startup recovery
try {
    # Enable F8 boot menu
    bcdedit /set {default} bootmenupolicy legacy

    # Set recovery options
    bcdedit /set {default} recoveryenabled yes

    Write-Host "Startup recovery configured"
} catch {
    Write-Warning "Failed to configure startup recovery: $_"
}
"""

        script_path = scripts_dir / "configure_startup_recovery.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Startup recovery options configured")

    def create_backup_verification_script(self):
        """Create script to verify backup configuration on first boot"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = """# Backup Configuration Verification
Write-Host "DeployForge Backup Configuration Verification" -ForegroundColor Cyan

# Check System Restore
$srStatus = (Get-ComputerRestorePoint -ErrorAction SilentlyContinue)
if ($srStatus) {
    Write-Host "[OK] System Restore is enabled" -ForegroundColor Green
} else {
    Write-Host "[WARNING] System Restore is not configured" -ForegroundColor Yellow
}

# Check VSS
$vssStatus = Get-Service -Name VSS
if ($vssStatus.Status -eq "Running") {
    Write-Host "[OK] Volume Shadow Copy Service is running" -ForegroundColor Green
} else {
    Write-Host "[WARNING] VSS is not running" -ForegroundColor Yellow
}

# Check Recovery Environment
$recoveryStatus = reagentc /info
if ($recoveryStatus -match "Enabled") {
    Write-Host "[OK] Windows Recovery Environment is enabled" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Recovery Environment is not enabled" -ForegroundColor Yellow
}

Write-Host "`nBackup verification complete" -ForegroundColor Cyan
"""

        script_path = scripts_dir / "verify_backup_config.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Backup verification script created")


def configure_backup(
    image_path: Path,
    profile: BackupProfile = BackupProfile.MODERATE,
    backup_path: Optional[Path] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
):
    """
    Quick backup configuration with profile

    Example:
        >>> from pathlib import Path
        >>> configure_backup(Path("install.wim"), BackupProfile.AGGRESSIVE)
    """
    backup = BackupIntegrator(image_path)
    backup.mount(progress_callback=progress_callback)
    backup.apply_profile(profile, progress_callback=progress_callback)

    if backup_path:
        backup.configure_file_history(backup_path)

    if backup.config.compression_enabled:
        backup.enable_backup_compression()

    backup.create_backup_verification_script()
    backup.unmount(save_changes=True, progress_callback=progress_callback)

    logger.info("Backup configuration complete")
