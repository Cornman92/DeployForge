"""
Debloating & Privacy Tools Module

Removes bloatware and applies privacy tweaks to Windows images.
NOTE: Xbox and OneDrive are preserved by default.

Features:
- Remove pre-installed bloatware apps
- Disable telemetry and diagnostic data
- Remove unnecessary Windows features
- Apply privacy-focused registry tweaks
- Disable tips, suggestions, and ads
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class DebloatLevel(Enum):
    """Debloating levels"""
    MINIMAL = "minimal"  # Remove only obvious bloat
    MODERATE = "moderate"  # Remove most unnecessary apps
    AGGRESSIVE = "aggressive"  # Remove everything non-essential


class DebloatManager:
    """
    Removes bloatware and applies privacy tweaks.

    Example:
        debloat = DebloatManager(Path('install.wim'))
        debloat.mount()
        debloat.remove_bloatware(level=DebloatLevel.MODERATE)
        debloat.disable_telemetry()
        debloat.apply_privacy_tweaks()
        debloat.unmount(save_changes=True)
    """

    # Apps to remove (Xbox and OneDrive excluded per user request)
    BLOATWARE_APPS = {
        'minimal': [
            'Microsoft.BingNews',
            'Microsoft.GetHelp',
            'Microsoft.Getstarted',
            'Microsoft.MicrosoftOfficeHub',
            'Microsoft.MicrosoftSolitaireCollection',
            'Microsoft.People',
            'Microsoft.WindowsFeedbackHub',
            'Microsoft.YourPhone',
            'Microsoft.549981C3F5F10',  # Cortana
            'MicrosoftCorporationII.QuickAssist',
        ],
        'moderate': [
            # Minimal apps plus:
            'Microsoft.BingWeather',
            'Microsoft.WindowsMaps',
            'Microsoft.ZuneMusic',
            'Microsoft.ZuneVideo',
            'Microsoft.WindowsSoundRecorder',
            'Microsoft.MixedReality.Portal',
            'Microsoft.SkypeApp',
            'Microsoft.Messaging',
            'Microsoft.Print3D',
            'Microsoft.3DBuilder',
        ],
        'aggressive': [
            # Moderate apps plus:
            'Microsoft.WindowsCamera',
            'Microsoft.ScreenSketch',
            'Microsoft.WindowsAlarms',
            'Microsoft.WindowsCalculator',
            'Microsoft.Paint',
            'Microsoft.MSPaint',
        ]
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize debloat manager.

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
        """Mount the image"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_debloat_'))

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
        """Unmount the image"""
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

    def remove_bloatware(self, level: DebloatLevel = DebloatLevel.MODERATE):
        """
        Remove bloatware applications.

        Args:
            level: Debloating level
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Removing bloatware: {level.value} level")

        # Build list of apps to remove
        apps_to_remove = self.BLOATWARE_APPS['minimal'].copy()

        if level in [DebloatLevel.MODERATE, DebloatLevel.AGGRESSIVE]:
            apps_to_remove.extend(self.BLOATWARE_APPS['moderate'])

        if level == DebloatLevel.AGGRESSIVE:
            apps_to_remove.extend(self.BLOATWARE_APPS['aggressive'])

        removed_count = 0

        for app in apps_to_remove:
            try:
                # Remove provisioned package
                result = subprocess.run([
                    'dism',
                    f'/Image:{self.mount_point}',
                    '/Remove-ProvisionedAppxPackage',
                    f'/PackageName:{app}'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    removed_count += 1
                    logger.info(f"Removed: {app}")

            except Exception as e:
                logger.debug(f"Could not remove {app}: {e}")

        logger.info(f"Removed {removed_count} bloatware apps")

    def disable_telemetry(self):
        """Disable Windows telemetry and diagnostic data"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Disabling telemetry")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable telemetry
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Policies\\Microsoft\\Windows\\DataCollection',
                '/v', 'AllowTelemetry',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            # Disable diagnostic data
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\Diagnostics\\DiagTrack',
                '/v', 'ShowedToastAtLevel',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            # Disable app diagnostics
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\Privacy',
                '/v', 'TailoredExperiencesWithDiagnosticDataEnabled',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Telemetry disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def apply_privacy_tweaks(self):
        """Apply privacy-focused registry tweaks"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying privacy tweaks")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            privacy_tweaks = [
                # Disable advertising ID
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo', 'Enabled', '0'),

                # Disable Windows tips
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'SubscribedContent-338389Enabled', '0'),

                # Disable suggested content
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'SubscribedContent-353694Enabled', '0'),

                # Disable app suggestions
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'SubscribedContent-353696Enabled', '0'),

                # Disable timeline suggestions
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'SubscribedContent-353698Enabled', '0'),

                # Disable lock screen tips
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'RotatingLockScreenOverlayEnabled', '0'),

                # Disable suggested apps in Start
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'SystemPaneSuggestionsEnabled', '0'),

                # Disable Windows Spotlight
                (f'{hive_key}\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                 'RotatingLockScreenEnabled', '0'),
            ]

            for key, value_name, value_data in privacy_tweaks:
                subprocess.run([
                    'reg', 'add', key,
                    '/v', value_name,
                    '/t', 'REG_DWORD',
                    '/d', value_data,
                    '/f'
                ], capture_output=True)

            logger.info(f"Applied {len(privacy_tweaks)} privacy tweaks")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_cortana(self):
        """Disable Cortana"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Disabling Cortana")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable Cortana
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Policies\\Microsoft\\Windows\\Windows Search',
                '/v', 'AllowCortana',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            # Disable web search in Start menu
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Policies\\Microsoft\\Windows\\Windows Search',
                '/v', 'DisableWebSearch',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Cortana disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_windows_update_delivery_optimization(self):
        """Disable Windows Update P2P delivery"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Disabling Windows Update delivery optimization")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable P2P updates
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Policies\\Microsoft\\Windows\\DeliveryOptimization',
                '/v', 'DODownloadMode',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Delivery optimization disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)


def debloat_windows(
    image_path: Path,
    level: str = "moderate",
    disable_telemetry: bool = True,
    disable_cortana: bool = True
) -> DebloatManager:
    """
    Quick debloat function.

    Args:
        image_path: Path to image
        level: Debloat level (minimal, moderate, aggressive)
        disable_telemetry: Disable telemetry
        disable_cortana: Disable Cortana

    Returns:
        DebloatManager instance

    Example:
        debloat_windows(
            Path('install.wim'),
            level='moderate',
            disable_telemetry=True,
            disable_cortana=True
        )
    """
    debloat = DebloatManager(image_path)
    debloat.mount()

    # Remove bloatware
    debloat.remove_bloatware(DebloatLevel(level))

    # Apply privacy tweaks
    debloat.apply_privacy_tweaks()

    if disable_telemetry:
        debloat.disable_telemetry()

    if disable_cortana:
        debloat.disable_cortana()

    # Disable delivery optimization
    debloat.disable_windows_update_delivery_optimization()

    debloat.unmount(save_changes=True)

    logger.info("Debloating complete")

    return debloat
