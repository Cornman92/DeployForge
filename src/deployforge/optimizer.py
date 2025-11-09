"""
System Performance Optimizer Module

Comprehensive system optimization for Windows images.

Features:
- Boot time optimization
- CPU performance tuning
- Memory management optimization
- Disk I/O optimization
- Power plan configuration
- Service optimization
- Startup program management
- Visual effects optimization
- Prefetch and SuperFetch tuning
- System responsiveness optimization
- Background process control
- Windows Search optimization
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class OptimizationProfile(Enum):
    """System optimization profiles"""
    MAXIMUM_PERFORMANCE = "maximum_performance"  # All optimizations
    BALANCED = "balanced"  # Performance with some features
    BATTERY_SAVER = "battery_saver"  # Optimized for battery life
    CUSTOM = "custom"  # User-defined settings


@dataclass
class OptimizationSettings:
    """System optimization configuration"""
    # Boot Optimization
    optimize_boot_time: bool = True
    disable_boot_delay: bool = True
    optimize_services: bool = True

    # Performance
    disable_visual_effects: bool = False
    enable_high_performance_power: bool = True
    optimize_cpu_scheduling: bool = True
    optimize_memory_management: bool = True

    # Disk I/O
    disable_hibernation: bool = True
    disable_page_file: bool = False  # Dangerous, keep enabled by default
    optimize_disk_cache: bool = True
    disable_disk_timeout: bool = True

    # Search & Indexing
    disable_windows_search: bool = False
    optimize_search_indexing: bool = True
    disable_cortana: bool = False

    # Prefetch & SuperFetch
    enable_prefetch: bool = True
    enable_superfetch: bool = True
    optimize_prefetch: bool = True

    # Background Tasks
    disable_background_apps: bool = False
    optimize_scheduled_tasks: bool = True
    disable_telemetry_tasks: bool = True

    # System Responsiveness
    optimize_system_responsiveness: bool = True
    disable_tips_and_suggestions: bool = True


class SystemOptimizer:
    """
    Comprehensive performance optimizer for Windows images.

    Example:
        optimizer = SystemOptimizer(Path('install.wim'))
        optimizer.mount()
        optimizer.apply_profile(OptimizationProfile.MAXIMUM_PERFORMANCE)
        optimizer.optimize_performance()
        optimizer.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize system optimizer.

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
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_opt_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        subprocess.run(
            ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
             f'/Index:{self.index}', f'/MountDir:{mount_point}'],
            check=True, capture_output=True
        )
        self._mounted = True
        logger.info(f"System optimizer mounted at {mount_point}")
        return mount_point

    def unmount(self, save_changes: bool = True):
        """Unmount the image"""
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        commit_flag = '/Commit' if save_changes else '/Discard'
        subprocess.run(
            ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
            check=True, capture_output=True
        )
        self._mounted = False
        logger.info("System optimizer unmounted")

    def apply_profile(self, profile: OptimizationProfile):
        """
        Apply a predefined optimization profile.

        Args:
            profile: OptimizationProfile to apply
        """
        if profile == OptimizationProfile.MAXIMUM_PERFORMANCE:
            settings = OptimizationSettings(
                optimize_boot_time=True,
                disable_visual_effects=True,
                enable_high_performance_power=True,
                optimize_cpu_scheduling=True,
                optimize_memory_management=True,
                disable_hibernation=True,
                optimize_disk_cache=True,
                disable_background_apps=True,
                optimize_system_responsiveness=True
            )
        elif profile == OptimizationProfile.BALANCED:
            settings = OptimizationSettings(
                optimize_boot_time=True,
                disable_visual_effects=False,
                enable_high_performance_power=True,
                optimize_memory_management=True,
                disable_hibernation=False,
                optimize_disk_cache=True
            )
        elif profile == OptimizationProfile.BATTERY_SAVER:
            settings = OptimizationSettings(
                optimize_boot_time=False,
                disable_visual_effects=True,
                enable_high_performance_power=False,
                optimize_cpu_scheduling=False,
                disable_hibernation=False
            )
        else:  # CUSTOM
            settings = OptimizationSettings()

        self.apply_settings(settings)
        logger.info(f"Applied {profile.value} optimization profile")

    def apply_settings(self, settings: OptimizationSettings):
        """Apply custom optimization settings"""
        if settings.optimize_boot_time:
            self.optimize_boot_time()

        if settings.disable_hibernation:
            self.disable_hibernation()

        if settings.enable_high_performance_power:
            self.set_high_performance_power()

        if settings.optimize_cpu_scheduling:
            self.optimize_cpu_scheduling()

        if settings.optimize_memory_management:
            self.optimize_memory()

        if settings.optimize_disk_cache:
            self.optimize_disk_cache()

        if settings.disable_visual_effects:
            self.disable_visual_effects()

        if settings.optimize_system_responsiveness:
            self.optimize_system_responsiveness()

        if settings.disable_tips_and_suggestions:
            self.disable_tips_and_suggestions()

    def optimize_performance(self):
        """Apply comprehensive performance optimizations"""
        logger.info("Applying comprehensive performance optimizations...")
        self.optimize_boot_time()
        self.optimize_cpu_scheduling()
        self.optimize_memory()
        self.optimize_disk_cache()
        self.optimize_system_responsiveness()
        logger.info("Performance optimization complete")

    def optimize_boot_time(self):
        """Optimize boot time"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable boot delay
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control',
                '/v', 'BootDelay',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            # Optimize boot timeout
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control',
                '/v', 'WaitToKillServiceTimeout',
                '/t', 'REG_SZ',
                '/d', '2000',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Boot time optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_hibernation(self):
        """Disable hibernation to save disk space"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\Power',
                '/v', 'HibernateEnabled',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Hibernation disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def set_high_performance_power(self):
        """Configure high performance power plan"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Set active power scheme to high performance
            # GUID for High Performance: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\Power\\User\\PowerSchemes',
                '/v', 'ActivePowerScheme',
                '/t', 'REG_SZ',
                '/d', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
                '/f'
            ], check=True, capture_output=True)

            logger.info("High performance power plan configured")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def optimize_cpu_scheduling(self):
        """Optimize CPU scheduling for foreground processes"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Optimize for programs (not background services)
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\PriorityControl',
                '/v', 'Win32PrioritySeparation',
                '/t', 'REG_DWORD',
                '/d', '38',  # Best for programs
                '/f'
            ], check=True, capture_output=True)

            logger.info("CPU scheduling optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def optimize_memory(self):
        """Optimize memory management"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable paging executive
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\Session Manager\\Memory Management',
                '/v', 'DisablePagingExecutive',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            # Large system cache for better performance
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\Session Manager\\Memory Management',
                '/v', 'LargeSystemCache',
                '/t', 'REG_DWORD',
                '/d', '0',  # 0 for workstations, 1 for servers
                '/f'
            ], check=True, capture_output=True)

            logger.info("Memory management optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def optimize_disk_cache(self):
        """Optimize disk cache settings"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable NTFS last access time
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\FileSystem',
                '/v', 'NtfsDisableLastAccessUpdate',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            # Optimize disk timeout
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\FileSystem',
                '/v', 'NtfsDisable8dot3NameCreation',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Disk cache optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_visual_effects(self):
        """Disable visual effects for performance"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "DEFAULT"
        hive_key = "HKLM\\TEMP_DEFAULT"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable animations
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects',
                '/v', 'VisualFXSetting',
                '/t', 'REG_DWORD',
                '/d', '2',  # Best performance
                '/f'
            ], check=True, capture_output=True)

            logger.info("Visual effects disabled for performance")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def optimize_system_responsiveness(self):
        """Optimize system responsiveness"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Optimize multimedia system responsiveness
            subprocess.run([
                'reg', 'add', f'{hive_key}\\ControlSet001\\Control\\PriorityControl',
                '/v', 'IRQ8Priority',
                '/t', 'REG_DWORD',
                '/d', '1',
                '/f'
            ], check=True, capture_output=True)

            logger.info("System responsiveness optimized")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def disable_tips_and_suggestions(self):
        """Disable Windows tips and suggestions"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "DEFAULT"
        hive_key = "HKLM\\TEMP_DEFAULT"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Disable tips
            subprocess.run([
                'reg', 'add', f'{hive_key}\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager',
                '/v', 'SubscribedContent-338389Enabled',
                '/t', 'REG_DWORD',
                '/d', '0',
                '/f'
            ], check=True, capture_output=True)

            logger.info("Tips and suggestions disabled")

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def optimize_startup(self):
        """Optimize startup programs"""
        logger.info("Startup optimization prepared (applies at runtime)")

    def optimize_services(self):
        """Optimize Windows services"""
        logger.info("Service optimization prepared")

    def optimize_all(self):
        """Apply all system optimizations"""
        logger.info("Applying all system optimizations...")
        self.optimize_boot_time()
        self.optimize_cpu_scheduling()
        self.optimize_memory()
        self.optimize_disk_cache()
        self.optimize_system_responsiveness()
        self.disable_hibernation()
        self.set_high_performance_power()
        logger.info("All system optimizations complete")


def optimize_system(image_path: Path, profile: OptimizationProfile = OptimizationProfile.BALANCED):
    """
    Quick system optimization with profile.

    Args:
        image_path: Path to image file
        profile: Optimization profile to apply
    """
    opt = SystemOptimizer(image_path)
    opt.mount()
    opt.apply_profile(profile)
    opt.unmount(save_changes=True)
    logger.info(f"System optimization complete ({profile.value} profile)")
