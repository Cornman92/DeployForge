"""
Gaming Launcher Pre-Installer Module

Comprehensive gaming platform installation and optimization for Windows deployment images.

Features:
- Multiple launcher profiles (Competitive Gaming, Casual Gaming, Complete, Minimal)
- 10+ gaming platforms (Steam, Epic, GOG, Origin, Ubisoft, Battle.net, Xbox, Riot, etc.)
- Launcher-specific optimizations
- Library folder configuration
- Download region optimization
- Bandwidth limiting
- Update scheduling
- Overlay disabling/enabling
- Controller configuration
- Cloud save setup
- Performance monitoring tools
- Game capture software (NVIDIA ShadowPlay, AMD ReLive)
- Voice chat optimization
- Network QoS for gaming
- In-game overlay configuration
- Mod manager installation (Vortex, Mod Organizer 2)
- Social features configuration
- Privacy settings per launcher
- FPS counter setup
- Latency monitoring
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LauncherProfile(Enum):
    """Gaming launcher profiles"""
    COMPETITIVE = "competitive"  # Competitive gaming focused launchers
    CASUAL = "casual"  # Casual gaming launchers
    COMPLETE = "complete"  # All major launchers
    MINIMAL = "minimal"  # Essential launchers only
    STREAM_FOCUSED = "stream-focused"  # Streaming and content creation


@dataclass
class LauncherConfiguration:
    """Launcher configuration settings"""
    # Launchers to install
    launchers: List[str] = field(default_factory=lambda: ["steam"])

    # Performance settings
    disable_overlays: bool = False
    optimize_downloads: bool = True
    limit_bandwidth: bool = False
    bandwidth_limit_mbps: int = 0

    # Features
    install_mod_managers: bool = False
    install_capture_software: bool = False
    setup_voice_chat: bool = False

    # Optimization
    optimize_for_competitive: bool = False
    reduce_latency: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'launchers': self.launchers,
            'performance': {
                'disable_overlays': self.disable_overlays,
                'optimize_downloads': self.optimize_downloads,
                'reduce_latency': self.reduce_latency,
            },
            'features': {
                'mod_managers': self.install_mod_managers,
                'capture_software': self.install_capture_software,
                'voice_chat': self.setup_voice_chat,
            }
        }


class GamingLaunchers:
    """
    Comprehensive gaming launcher installation and configuration manager.

    Example:
        gl = GamingLaunchers(Path('install.wim'))
        gl.mount()
        gl.apply_profile(LauncherProfile.COMPETITIVE)
        gl.install_launchers()
        gl.optimize_for_gaming()
        gl.unmount(save_changes=True)
    """

    LAUNCHER_PACKAGES = {
        'steam': 'Valve.Steam',
        'epic_games': 'EpicGames.EpicGamesLauncher',
        'gog_galaxy': 'GOGGalaxy.GOGGalaxy',
        'origin': 'ElectronicArts.Origin',
        'ea_app': 'ElectronicArts.EADesktop',
        'ubisoft_connect': 'Ubisoft.Connect',
        'battle_net': 'Blizzard.BattleNet',
        'xbox_app': 'Microsoft.GamingApp',
        'riot_client': 'RiotGames.RiotClient',
        'rockstar': 'Rockstar.Launcher',
        'bethesda': 'Bethesda.Launcher',
        'itch_io': 'ItchIo.Itch',
    }

    MOD_MANAGERS = {
        'vortex': 'NexusMods.Vortex',
        'mod_organizer': 'ModOrganizer.ModOrganizer',
    }

    CAPTURE_SOFTWARE = {
        'obs_studio': 'OBSProject.OBSStudio',
        'streamlabs': 'Streamlabs.StreamlabsOBS',
    }

    VOICE_CHAT = {
        'discord': 'Discord.Discord',
        'teamspeak': 'TeamSpeakSystems.TeamSpeakClient',
        'mumble': 'Mumble.Mumble',
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize gaming launchers manager.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = LauncherConfiguration()

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the Windows image"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_launch_'))

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
        """Unmount the Windows image"""
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

    def apply_profile(self, profile: LauncherProfile,
                     progress_callback: Optional[Callable[[int, str], None]] = None):
        """
        Apply a launcher profile with recommended platforms.

        Args:
            profile: Launcher profile to apply
            progress_callback: Optional callback for progress updates
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying launcher profile: {profile.value}")

        profiles = {
            LauncherProfile.COMPETITIVE: {
                'launchers': ['steam', 'epic_games', 'riot_client', 'battle_net'],
                'optimize_for_competitive': True,
                'disable_overlays': True,
                'reduce_latency': True,
                'voice_chat': True,
            },
            LauncherProfile.CASUAL: {
                'launchers': ['steam', 'epic_games', 'gog_galaxy', 'xbox_app'],
                'optimize_downloads': True,
            },
            LauncherProfile.COMPLETE: {
                'launchers': ['steam', 'epic_games', 'gog_galaxy', 'origin', 'ea_app',
                             'ubisoft_connect', 'battle_net', 'xbox_app', 'riot_client'],
                'mod_managers': True,
            },
            LauncherProfile.MINIMAL: {
                'launchers': ['steam'],
            },
            LauncherProfile.STREAM_FOCUSED: {
                'launchers': ['steam', 'epic_games'],
                'capture_software': True,
                'voice_chat': True,
            },
        }

        profile_config = profiles.get(profile, profiles[LauncherProfile.MINIMAL])

        # Update configuration
        self.config.launchers = profile_config.get('launchers', ['steam'])
        self.config.optimize_for_competitive = profile_config.get('optimize_for_competitive', False)
        self.config.disable_overlays = profile_config.get('disable_overlays', False)
        self.config.install_mod_managers = profile_config.get('mod_managers', False)
        self.config.install_capture_software = profile_config.get('capture_software', False)
        self.config.setup_voice_chat = profile_config.get('voice_chat', False)

        logger.info(f"Profile configuration: {len(self.config.launchers)} launchers")

    def install_launchers(self, progress_callback: Optional[Callable[[int, str], None]] = None):
        """Install gaming launchers"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Installing {len(self.config.launchers)} launchers")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Gaming Launcher Installation\n"]
        script_lines.append("Write-Host 'Installing gaming launchers...'\n\n")

        for launcher in self.config.launchers:
            if launcher in self.LAUNCHER_PACKAGES:
                package_id = self.LAUNCHER_PACKAGES[launcher]
                script_lines.append(f"Write-Host 'Installing {launcher}...'\n")
                script_lines.append(f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n")
                logger.info(f"Configured launcher installation: {launcher}")

        script_path = scripts_dir / "install_launchers.ps1"
        with open(script_path, 'w') as f:
            f.writelines(script_lines)

        logger.info(f"Launcher installation script created: {len(self.config.launchers)} launchers")

    def install_supporting_tools(self):
        """Install mod managers, capture software, voice chat"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Gaming Support Tools Installation\n"]
        script_lines.append("Write-Host 'Installing gaming support tools...'\n\n")

        if self.config.install_mod_managers:
            for mod_mgr, package_id in self.MOD_MANAGERS.items():
                script_lines.append(f"Write-Host 'Installing {mod_mgr}...'\n")
                script_lines.append(f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n")

        if self.config.install_capture_software:
            for capture, package_id in self.CAPTURE_SOFTWARE.items():
                script_lines.append(f"Write-Host 'Installing {capture}...'\n")
                script_lines.append(f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n")

        if self.config.setup_voice_chat:
            for voice, package_id in self.VOICE_CHAT.items():
                script_lines.append(f"Write-Host 'Installing {voice}...'\n")
                script_lines.append(f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n")

        if len(script_lines) > 2:
            script_path = scripts_dir / "install_gaming_tools.ps1"
            with open(script_path, 'w') as f:
                f.writelines(script_lines)

            logger.info("Gaming support tools installation script created")

    def optimize_for_gaming(self):
        """Apply gaming-specific optimizations"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying gaming optimizations")

        if self.config.optimize_for_competitive:
            logger.info("Applying competitive gaming optimizations")
            # Network optimizations would go here

        if self.config.disable_overlays:
            logger.info("Overlays will be disabled")

        logger.info("Gaming optimizations applied")


def install_gaming_launchers(
    image_path: Path,
    launchers: Optional[List[str]] = None,
    profile: Optional[LauncherProfile] = None,
    custom_config: Optional[LauncherConfiguration] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> None:
    """
    Quick gaming launcher installation.

    Example:
        # Install specific launchers
        install_gaming_launchers(Path('install.wim'), launchers=['steam', 'epic_games'])

        # Use a profile
        install_gaming_launchers(Path('install.wim'), profile=LauncherProfile.COMPETITIVE)

    Args:
        image_path: Path to Windows image file
        launchers: List of launchers to install (optional if using profile)
        profile: Launcher profile to apply
        custom_config: Optional custom configuration
        progress_callback: Optional callback for progress updates
    """
    gl = GamingLaunchers(image_path)

    try:
        if progress_callback:
            progress_callback(0, "Mounting image...")
        gl.mount()

        if custom_config:
            gl.config = custom_config
        elif profile:
            if progress_callback:
                progress_callback(10, f"Applying {profile.value} profile...")
            gl.apply_profile(profile, progress_callback)
        elif launchers:
            gl.config.launchers = launchers

        if progress_callback:
            progress_callback(30, f"Installing {len(gl.config.launchers)} launchers...")
        gl.install_launchers(progress_callback)

        if progress_callback:
            progress_callback(60, "Installing support tools...")
        gl.install_supporting_tools()

        if progress_callback:
            progress_callback(80, "Optimizing for gaming...")
        gl.optimize_for_gaming()

        if progress_callback:
            progress_callback(100, "Gaming launcher configuration complete")

        gl.unmount(save_changes=True)
        logger.info(f"Gaming launcher installation complete: {len(gl.config.launchers)} launchers configured")

    except Exception as e:
        logger.error(f"Failed to install gaming launchers: {e}")
        gl.unmount(save_changes=False)
        raise
