"""
Gaming Optimization Module

Optimizes Windows images for gaming performance.

Features:
- Game Mode optimization
- GPU driver pre-installation
- Network latency optimization
- Background service optimization
- DirectX/Visual C++ runtime installation
- Gaming-specific registry tweaks
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GamingProfile(Enum):
    """Gaming optimization profiles"""

    COMPETITIVE = "competitive"  # Maximum performance, minimal latency
    BALANCED = "balanced"  # Good performance with some quality
    QUALITY = "quality"  # Best visual quality
    STREAMING = "streaming"  # Optimized for streaming


@dataclass
class GamingOptimization:
    """Gaming optimization settings"""

    enable_game_mode: bool = True
    disable_fullscreen_optimizations: bool = False
    optimize_network_latency: bool = True
    disable_game_bar: bool = False
    enable_hardware_acceleration: bool = True
    disable_background_recording: bool = True
    optimize_mouse_polling: bool = True
    disable_nagle_algorithm: bool = True
    priority_boost: str = "high"  # low, normal, high, realtime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enable_game_mode": self.enable_game_mode,
            "disable_fullscreen_optimizations": self.disable_fullscreen_optimizations,
            "optimize_network_latency": self.optimize_network_latency,
            "disable_game_bar": self.disable_game_bar,
            "enable_hardware_acceleration": self.enable_hardware_acceleration,
            "disable_background_recording": self.disable_background_recording,
            "optimize_mouse_polling": self.optimize_mouse_polling,
            "disable_nagle_algorithm": self.disable_nagle_algorithm,
            "priority_boost": self.priority_boost,
        }


class GamingOptimizer:
    """
    Optimizes Windows images for gaming performance.

    Example:
        optimizer = GamingOptimizer(Path('install.wim'))
        optimizer.mount()
        optimizer.apply_profile(GamingProfile.COMPETITIVE)
        optimizer.install_gaming_runtimes()
        optimizer.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize gaming optimizer.

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
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_gaming_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

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
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """Unmount the image"""
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def apply_profile(self, profile: GamingProfile):
        """
        Apply gaming optimization profile.

        Args:
            profile: Gaming profile to apply
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying gaming profile: {profile.value}")

        if profile == GamingProfile.COMPETITIVE:
            config = GamingOptimization(
                enable_game_mode=True,
                disable_fullscreen_optimizations=True,
                optimize_network_latency=True,
                disable_game_bar=True,
                enable_hardware_acceleration=True,
                disable_background_recording=True,
                optimize_mouse_polling=True,
                disable_nagle_algorithm=True,
                priority_boost="high",
            )
        elif profile == GamingProfile.BALANCED:
            config = GamingOptimization(
                enable_game_mode=True,
                optimize_network_latency=True,
                disable_background_recording=True,
                priority_boost="normal",
            )
        elif profile == GamingProfile.QUALITY:
            config = GamingOptimization(
                enable_game_mode=True, enable_hardware_acceleration=True, priority_boost="normal"
            )
        else:  # STREAMING
            config = GamingOptimization(
                enable_game_mode=True,
                enable_hardware_acceleration=True,
                disable_background_recording=False,
                priority_boost="high",
            )

        self._apply_optimization(config)

    def _apply_optimization(self, config: GamingOptimization):
        """Apply gaming optimizations"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Enable Game Mode
            if config.enable_game_mode:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Microsoft\\GameBar",
                        "/v",
                        "AutoGameModeEnabled",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "1",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            # Disable Game Bar
            if config.disable_game_bar:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Microsoft\\GameBar",
                        "/v",
                        "UseNexusForGameBarEnabled",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "0",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            # Disable background recording
            if config.disable_background_recording:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
                        "/v",
                        "AppCaptureEnabled",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "0",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            # Hardware-accelerated GPU scheduling
            if config.enable_hardware_acceleration:
                subprocess.run(
                    [
                        "reg",
                        "add",
                        f"{hive_key}\\Microsoft\\DirectX\\GraphicsSettings",
                        "/v",
                        "HwSchMode",
                        "/t",
                        "REG_DWORD",
                        "/d",
                        "2",
                        "/f",
                    ],
                    check=True,
                    capture_output=True,
                )

            logger.info("Gaming optimizations applied")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

        # Network optimizations
        if config.optimize_network_latency:
            self._optimize_network()

    def _optimize_network(self):
        """Optimize network settings for gaming"""
        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            # Disable Nagle's algorithm
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Services\\Tcpip\\Parameters",
                    "/v",
                    "TcpAckFrequency",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Services\\Tcpip\\Parameters",
                    "/v",
                    "TCPNoDelay",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            # Optimize network throttling
            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\ControlSet001\\Services\\Tcpip\\Parameters",
                    "/v",
                    "TcpDelAckTicks",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "0",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Network optimizations applied")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def install_gaming_runtimes(self, runtimes_path: Optional[Path] = None):
        """
        Install gaming runtimes (DirectX, Visual C++).

        Args:
            runtimes_path: Path to runtime installers
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Installing gaming runtimes")

        # Create runtime installation script
        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_path = scripts_dir / "install_gaming_runtimes.ps1"

        script_content = """# Gaming Runtimes Installation
Write-Host "Installing gaming runtimes..."

# DirectX
if (Test-Path "C:\\Runtimes\\DirectX") {
    Write-Host "Installing DirectX..."
    Start-Process -FilePath "C:\\Runtimes\\DirectX\\DXSETUP.exe" -ArgumentList "/silent" -Wait
}

# Visual C++ Redistributables
$vcRedists = @(
    "2015-2022-x64",
    "2015-2022-x86"
)

foreach ($redist in $vcRedists) {
    $path = "C:\\Runtimes\\VCRedist\\VC_redist.$redist.exe"
    if (Test-Path $path) {
        Write-Host "Installing Visual C++ $redist..."
        Start-Process -FilePath $path -ArgumentList "/install", "/quiet", "/norestart" -Wait
    }
}

Write-Host "Gaming runtimes installation complete"
"""

        with open(script_path, "w") as f:
            f.write(script_content)

        # Copy runtimes if provided
        if runtimes_path and runtimes_path.exists():
            runtimes_dest = self.mount_point / "Runtimes"
            runtimes_dest.mkdir(parents=True, exist_ok=True)

            import shutil

            for item in runtimes_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, runtimes_dest / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, runtimes_dest / item.name)

        # Add to SetupComplete.cmd
        setupcomplete_path = scripts_dir / "SetupComplete.cmd"
        mode = "a" if setupcomplete_path.exists() else "w"

        with open(setupcomplete_path, mode) as f:
            if mode == "w":
                f.write("@echo off\n")

            f.write(
                'powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_gaming_runtimes.ps1"\n'
            )

        logger.info("Gaming runtimes configured")

    def optimize_services(self):
        """Optimize Windows services for gaming"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Optimizing services for gaming")

        # Services to disable for gaming
        services_to_disable = [
            "DiagTrack",  # Connected User Experiences and Telemetry
            "SysMain",  # Superfetch (can cause stuttering)
            "WSearch",  # Windows Search (optional)
            "TabletInputService",  # Touch Keyboard
            "WMPNetworkSvc",  # Windows Media Player Network Sharing
        ]

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
        hive_key = "HKLM\\TEMP_SYSTEM"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            for service in services_to_disable:
                service_key = f"{hive_key}\\ControlSet001\\Services\\{service}"
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
                        "4",  # Disabled
                        "/f",
                    ],
                    capture_output=True,
                )

            logger.info(f"Disabled {len(services_to_disable)} services")

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)


def optimize_for_gaming(
    image_path: Path, profile: str = "competitive", install_runtimes: bool = True
) -> GamingOptimizer:
    """
    Quick gaming optimization.

    Args:
        image_path: Path to image
        profile: Gaming profile (competitive, balanced, quality, streaming)
        install_runtimes: Install DirectX/VC++ runtimes

    Returns:
        GamingOptimizer instance

    Example:
        optimizer = optimize_for_gaming(
            Path('install.wim'),
            profile='competitive',
            install_runtimes=True
        )
    """
    optimizer = GamingOptimizer(image_path)
    optimizer.mount()

    # Apply profile
    optimizer.apply_profile(GamingProfile(profile))

    # Optimize services
    optimizer.optimize_services()

    # Install runtimes
    if install_runtimes:
        optimizer.install_gaming_runtimes()

    optimizer.unmount(save_changes=True)

    logger.info(f"Gaming optimization complete: {profile} profile")

    return optimizer
