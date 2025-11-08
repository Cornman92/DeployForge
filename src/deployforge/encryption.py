"""
BitLocker & Encryption Management Module

Provides BitLocker configuration and encryption management for Windows images.

Features:
- BitLocker pre-configuration
- TPM settings
- Encryption method selection
- Recovery key escrow to AD
- Recovery password management
- FIPS compliance mode
- Network unlock configuration
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import secrets

logger = logging.getLogger(__name__)


class EncryptionMethod(Enum):
    """BitLocker encryption methods"""
    AES_128_CBC = "aes128"
    AES_256_CBC = "aes256"
    XTS_AES_128 = "xts-aes128"
    XTS_AES_256 = "xts-aes256"


class RecoveryKeyType(Enum):
    """Recovery key types"""
    PASSWORD = "password"
    NUMERICAL_PASSWORD = "numerical"
    EXTERNAL_KEY = "external"


@dataclass
class BitLockerConfig:
    """
    BitLocker configuration settings.
    """
    enabled: bool = True
    encryption_method: EncryptionMethod = EncryptionMethod.XTS_AES_256
    require_tpm: bool = True
    tpm_and_pin: bool = False
    tpm_and_startup_key: bool = False
    save_recovery_key_to_ad: bool = False
    recovery_key_type: RecoveryKeyType = RecoveryKeyType.NUMERICAL_PASSWORD
    fips_compliance: bool = False
    hardware_encryption: bool = False
    used_space_only: bool = True  # Encrypt only used space
    network_unlock: bool = False
    min_pin_length: int = 6

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'enabled': self.enabled,
            'encryption_method': self.encryption_method.value,
            'require_tpm': self.require_tpm,
            'tpm_and_pin': self.tpm_and_pin,
            'tpm_and_startup_key': self.tpm_and_startup_key,
            'save_recovery_key_to_ad': self.save_recovery_key_to_ad,
            'recovery_key_type': self.recovery_key_type.value,
            'fips_compliance': self.fips_compliance,
            'hardware_encryption': self.hardware_encryption,
            'used_space_only': self.used_space_only,
            'network_unlock': self.network_unlock,
            'min_pin_length': self.min_pin_length
        }


class BitLockerManager:
    """
    Manages BitLocker encryption configuration in Windows images.

    Example:
        bitlocker = BitLockerManager(Path('install.wim'))
        bitlocker.mount()

        config = BitLockerConfig(
            encryption_method=EncryptionMethod.XTS_AES_256,
            require_tpm=True,
            save_recovery_key_to_ad=True
        )

        bitlocker.configure_bitlocker(config)
        bitlocker.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize BitLocker manager.

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
        """
        Mount the image.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to mount point
        """
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_bitlocker_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            if self.image_path.suffix.lower() == '.wim':
                subprocess.run(
                    ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
                     f'/Index:{self.index}', f'/MountDir:{mount_point}'],
                    check=True,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ['dism', '/Mount-Image', f'/ImageFile:{self.image_path}',
                     f'/Index:{self.index}', f'/MountDir:{mount_point}'],
                    check=True,
                    capture_output=True
                )

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """
        Unmount the image.

        Args:
            save_changes: Whether to commit changes
        """
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = '/Commit' if save_changes else '/Discard'
            subprocess.run(
                ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
                check=True,
                capture_output=True
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def configure_bitlocker(self, config: BitLockerConfig):
        """
        Configure BitLocker settings.

        Args:
            config: BitLocker configuration
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Configuring BitLocker settings")

        # Configure via registry and group policy
        self._configure_encryption_method(config.encryption_method)

        if config.require_tpm:
            self._configure_tpm(config)

        if config.save_recovery_key_to_ad:
            self._configure_ad_backup()

        if config.fips_compliance:
            self._enable_fips_mode()

        if config.network_unlock:
            self._configure_network_unlock()

        if config.used_space_only:
            self._configure_used_space_encryption()

        # Save configuration manifest
        self._save_config_manifest(config)

        logger.info("BitLocker configuration applied")

    def _configure_encryption_method(self, method: EncryptionMethod):
        """Configure encryption algorithm"""
        # Map to registry value
        method_map = {
            EncryptionMethod.AES_128_CBC: 1,
            EncryptionMethod.AES_256_CBC: 2,
            EncryptionMethod.XTS_AES_128: 6,
            EncryptionMethod.XTS_AES_256: 7
        }

        method_value = method_map[method]

        # Load SOFTWARE hive
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Set encryption method
            policy_key = f"{hive_key}\\Policies\\Microsoft\\FVE"

            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'EncryptionMethodWithXtsOs',
                '/t', 'REG_DWORD',
                '/d', str(method_value),
                '/f'
            ], check=True, capture_output=True)

            logger.info(f"Set encryption method to {method.value}")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def _configure_tpm(self, config: BitLockerConfig):
        """Configure TPM settings"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            policy_key = f"{hive_key}\\Policies\\Microsoft\\FVE"

            # Require TPM
            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'UseTPM',
                '/t', 'REG_DWORD',
                '/d', '1' if config.require_tpm else '0',
                '/f'
            ], check=True, capture_output=True)

            # TPM + PIN
            if config.tpm_and_pin:
                subprocess.run([
                    'reg', 'add', policy_key,
                    '/v', 'UseTPMPIN',
                    '/t', 'REG_DWORD',
                    '/d', '1',
                    '/f'
                ], check=True, capture_output=True)

                # Minimum PIN length
                subprocess.run([
                    'reg', 'add', policy_key,
                    '/v', 'MinimumPIN',
                    '/t', 'REG_DWORD',
                    '/d', str(config.min_pin_length),
                    '/f'
                ], check=True, capture_output=True)

            # TPM + Startup Key
            if config.tpm_and_startup_key:
                subprocess.run([
                    'reg', 'add', policy_key,
                    '/v', 'UseTPMKey',
                    '/t', 'REG_DWORD',
                    '/d', '1',
                    '/f'
                ], check=True, capture_output=True)

            logger.info("TPM configuration applied")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def _configure_ad_backup(self):
        """Configure Active Directory backup for recovery keys"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            policy_key = f"{hive_key}\\Policies\\Microsoft\\FVE"

            # Enable AD backup
            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'OSActiveDirectoryBackup',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            # Require backup before enabling BitLocker
            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'OSRequireActiveDirectoryBackup',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("AD backup configuration applied")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def _enable_fips_mode(self):
        """Enable FIPS compliance mode"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            policy_key = f"{hive_key}\\ControlSet001\\Control\\Lsa\\FipsAlgorithmPolicy"

            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'Enabled',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("FIPS mode enabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def _configure_network_unlock(self):
        """Configure network unlock"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            policy_key = f"{hive_key}\\Policies\\Microsoft\\FVE"

            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'OSManageNKP',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Network unlock configured")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def _configure_used_space_encryption(self):
        """Configure used space only encryption"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            policy_key = f"{hive_key}\\Policies\\Microsoft\\FVE"

            subprocess.run([
                'reg', 'add', policy_key,
                '/v', 'EncryptionType',
                '/t', 'REG_DWORD',
                '/d', '1',  # 1 = Used space only, 0 = Full disk
                '/f'
            ], check=True, capture_output=True)

            logger.info("Used space encryption configured")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def generate_recovery_password(self) -> str:
        """
        Generate BitLocker numerical recovery password.

        Returns:
            48-digit recovery password
        """
        # Generate 48-digit numerical password (8 groups of 6 digits)
        groups = []
        for _ in range(8):
            group = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            groups.append(group)

        password = '-'.join(groups)

        logger.info("Generated recovery password")

        return password

    def _save_config_manifest(self, config: BitLockerConfig):
        """Save BitLocker configuration manifest"""
        manifest_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = manifest_dir / "bitlocker_config.json"

        with open(manifest_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)

        logger.info(f"Saved configuration manifest to {manifest_path}")


def configure_enterprise_bitlocker(
    image_path: Path,
    encryption_method: str = "xts-aes256",
    require_tpm: bool = True,
    save_to_ad: bool = True,
    fips_compliance: bool = False
) -> BitLockerManager:
    """
    Configure BitLocker with enterprise settings.

    Args:
        image_path: Path to WIM/VHDX image
        encryption_method: Encryption algorithm
        require_tpm: Require TPM
        save_to_ad: Save recovery keys to AD
        fips_compliance: Enable FIPS mode

    Returns:
        BitLockerManager instance

    Example:
        bitlocker = configure_enterprise_bitlocker(
            image_path=Path('install.wim'),
            encryption_method='xts-aes256',
            require_tpm=True,
            save_to_ad=True
        )
    """
    manager = BitLockerManager(image_path)
    manager.mount()

    config = BitLockerConfig(
        enabled=True,
        encryption_method=EncryptionMethod(encryption_method),
        require_tpm=require_tpm,
        save_recovery_key_to_ad=save_to_ad,
        fips_compliance=fips_compliance,
        used_space_only=True
    )

    manager.configure_bitlocker(config)
    manager.unmount(save_changes=True)

    logger.info("Enterprise BitLocker configuration complete")

    return manager


def create_bitlocker_deployment_script(
    output_path: Path,
    config: BitLockerConfig,
    recovery_password: Optional[str] = None
):
    """
    Create PowerShell script for BitLocker deployment.

    Args:
        output_path: Path to save script
        config: BitLocker configuration
        recovery_password: Optional recovery password
    """
    script = """# BitLocker Deployment Script
# Generated by DeployForge

Write-Host "Configuring BitLocker..."

# Check TPM status
$tpm = Get-Tpm
if (-not $tpm.TpmPresent) {
    Write-Error "TPM not present"
    exit 1
}

if (-not $tpm.TpmReady) {
    Write-Host "Initializing TPM..."
    Initialize-Tpm -AllowClear -AllowPhysicalPresence
}

"""

    if config.require_tpm:
        script += """
# Enable BitLocker with TPM
"""
        if config.tpm_and_pin:
            script += """$pin = Read-Host -AsSecureString "Enter BitLocker PIN"
Enable-BitLocker -MountPoint "C:" -EncryptionMethod {encryption_method} -TpmAndPinProtector -Pin $pin
"""
        else:
            script += """Enable-BitLocker -MountPoint "C:" -EncryptionMethod {encryption_method} -TpmProtector
"""

    if recovery_password:
        script += f"""
# Add recovery password
$recoveryPassword = "{recovery_password}"
Add-BitLockerKeyProtector -MountPoint "C:" -RecoveryPasswordProtector -RecoveryPassword $recoveryPassword
"""

    if config.save_recovery_key_to_ad:
        script += """
# Backup recovery key to AD
Backup-BitLockerKeyProtector -MountPoint "C:" -KeyProtectorId (Get-BitLockerVolume -MountPoint "C:").KeyProtector[0].KeyProtectorId
"""

    script += """
Write-Host "BitLocker configuration complete"
"""

    # Replace placeholders
    script = script.replace("{encryption_method}", config.encryption_method.value.replace('-', ''))

    with open(output_path, 'w') as f:
        f.write(script)

    logger.info(f"BitLocker deployment script created: {output_path}")
