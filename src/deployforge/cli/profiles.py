"""
Profile Management System

Provides predefined profiles for common use cases (gaming, development, enterprise, etc.)
Each profile is a collection of modules and configurations optimized for specific users.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class ProfileConfiguration:
    """Configuration for a deployment profile."""

    name: str
    description: str

    # Feature flags
    gaming_optimization: bool = False
    developer_tools: bool = False
    creative_suite: bool = False
    enterprise_security: bool = False

    # Debloating and privacy
    debloat_level: str = "none"  # none, minimal, moderate, aggressive
    privacy_hardening: bool = False

    # Visual customization
    theme: str = "dark"  # dark, light
    taskbar_position: str = "center"  # center, left

    # Package installation
    browsers: List[str] = None
    packages: List[str] = None
    gaming_launchers: List[str] = None

    # Windows features
    enable_wsl2: bool = False
    enable_hyperv: bool = False
    enable_sandbox: bool = False

    # Performance
    performance_optimization: bool = False
    network_optimization: bool = False

    # Backup and recovery
    enable_backup: bool = False

    def __post_init__(self):
        if self.browsers is None:
            self.browsers = []
        if self.packages is None:
            self.packages = []
        if self.gaming_launchers is None:
            self.gaming_launchers = []


class ProfileManager:
    """Manages deployment profiles."""

    BUILTIN_PROFILES = {
        "gamer": ProfileConfiguration(
            name="Gaming Profile",
            description="Optimized for gaming with performance tweaks and gaming launchers",
            gaming_optimization=True,
            debloat_level="moderate",
            privacy_hardening=True,
            theme="dark",
            taskbar_position="center",
            browsers=["brave", "firefox"],
            packages=["discord", "obs-studio"],
            gaming_launchers=["steam", "epic", "gog"],
            enable_sandbox=False,
            performance_optimization=True,
            network_optimization=True,
            enable_backup=True,
        ),
        "developer": ProfileConfiguration(
            name="Developer Profile",
            description="Development tools and programming environments",
            developer_tools=True,
            debloat_level="minimal",
            privacy_hardening=True,
            theme="dark",
            taskbar_position="left",
            browsers=["chrome", "firefox"],
            packages=["vscode", "git", "docker-desktop", "python", "nodejs"],
            enable_wsl2=True,
            enable_hyperv=True,
            enable_sandbox=True,
            performance_optimization=True,
            network_optimization=False,
            enable_backup=True,
        ),
        "enterprise": ProfileConfiguration(
            name="Enterprise Profile",
            description="Enterprise security and management features",
            enterprise_security=True,
            debloat_level="none",
            privacy_hardening=False,
            theme="light",
            taskbar_position="left",
            browsers=["edge"],
            packages=["microsoft-365"],
            enable_hyperv=False,
            enable_sandbox=False,
            performance_optimization=False,
            network_optimization=False,
            enable_backup=True,
        ),
        "student": ProfileConfiguration(
            name="Student Profile",
            description="Balanced profile for students with productivity tools",
            developer_tools=False,
            debloat_level="moderate",
            privacy_hardening=True,
            theme="light",
            taskbar_position="center",
            browsers=["edge", "firefox"],
            packages=["microsoft-365", "vscode", "python"],
            enable_wsl2=False,
            enable_hyperv=False,
            enable_sandbox=False,
            performance_optimization=True,
            network_optimization=False,
            enable_backup=True,
        ),
        "creator": ProfileConfiguration(
            name="Content Creator Profile",
            description="Creative tools and optimizations for content creators",
            creative_suite=True,
            gaming_optimization=False,
            debloat_level="minimal",
            privacy_hardening=True,
            theme="dark",
            taskbar_position="center",
            browsers=["chrome"],
            packages=["obs-studio", "gimp", "audacity", "blender", "vlc"],
            enable_sandbox=False,
            performance_optimization=True,
            network_optimization=True,
            enable_backup=True,
        ),
        "custom": ProfileConfiguration(
            name="Custom Profile",
            description="Minimal profile for manual customization",
            debloat_level="none",
            privacy_hardening=False,
            theme="dark",
            taskbar_position="center",
            performance_optimization=False,
            network_optimization=False,
            enable_backup=False,
        ),
    }

    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        Initialize profile manager.

        Args:
            profiles_dir: Directory for custom profiles
        """
        self.profiles_dir = profiles_dir or Path.home() / ".deployforge" / "profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def get_profile(self, name: str) -> ProfileConfiguration:
        """
        Get a profile by name.

        Args:
            name: Profile name

        Returns:
            Profile configuration
        """
        # Check built-in profiles
        if name in self.BUILTIN_PROFILES:
            return self.BUILTIN_PROFILES[name]

        # Check custom profiles
        custom_path = self.profiles_dir / f"{name}.json"
        if custom_path.exists():
            return self._load_custom_profile(custom_path)

        raise ValueError(f"Profile not found: {name}")

    def list_profiles(self) -> List[Dict[str, str]]:
        """
        List all available profiles.

        Returns:
            List of profile info dictionaries
        """
        profiles = []

        # Built-in profiles
        for name, config in self.BUILTIN_PROFILES.items():
            profiles.append(
                {
                    "name": name,
                    "display_name": config.name,
                    "description": config.description,
                    "type": "builtin",
                }
            )

        # Custom profiles
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                config = self._load_custom_profile(profile_file)
                profiles.append(
                    {
                        "name": profile_file.stem,
                        "display_name": config.name,
                        "description": config.description,
                        "type": "custom",
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to load profile {profile_file}: {e}")

        return profiles

    def save_profile(self, name: str, config: ProfileConfiguration):
        """
        Save a custom profile.

        Args:
            name: Profile name
            config: Profile configuration
        """
        profile_path = self.profiles_dir / f"{name}.json"

        with open(profile_path, "w") as f:
            json.dump(asdict(config), f, indent=2)

        logger.info(f"Saved profile: {name}")

    def delete_profile(self, name: str):
        """
        Delete a custom profile.

        Args:
            name: Profile name
        """
        if name in self.BUILTIN_PROFILES:
            raise ValueError("Cannot delete built-in profiles")

        profile_path = self.profiles_dir / f"{name}.json"

        if profile_path.exists():
            profile_path.unlink()
            logger.info(f"Deleted profile: {name}")
        else:
            raise ValueError(f"Profile not found: {name}")

    def _load_custom_profile(self, path: Path) -> ProfileConfiguration:
        """Load a custom profile from file."""
        with open(path, "r") as f:
            data = json.load(f)

        return ProfileConfiguration(**data)


def apply_profile(image_path: Path, profile_name: str, output_path: Optional[Path] = None):
    """
    Apply a profile to an image.

    Args:
        image_path: Source image path
        profile_name: Profile name to apply
        output_path: Output image path (optional)
    """
    from deployforge.gaming import GamingOptimizer, GamingProfile
    from deployforge.debloat import DebloatManager, DebloatLevel
    from deployforge.themes import ThemeManager
    from deployforge.packages import PackageManager
    from deployforge.features import FeatureManager
    from deployforge.optimizer import SystemOptimizer
    from deployforge.network import NetworkOptimizer
    from deployforge.privacy_hardening import PrivacyHardening
    from deployforge.devenv import DeveloperEnvironment
    from deployforge.creative import CreativeSuite
    from deployforge.launchers import GamingLaunchers
    from deployforge.browsers import BrowserBundler
    from deployforge.backup import BackupIntegration

    # Load profile
    manager = ProfileManager()
    config = manager.get_profile(profile_name)

    logger.info(f"Applying profile: {config.name}")

    # Copy image if output path specified
    working_image = output_path if output_path else image_path
    if output_path and output_path != image_path:
        import shutil

        shutil.copy2(image_path, output_path)

    # Apply gaming optimizations
    if config.gaming_optimization:
        logger.info("Applying gaming optimizations...")
        gaming = GamingOptimizer(working_image)
        gaming.mount()
        gaming.apply_profile(GamingProfile.COMPETITIVE)
        gaming.unmount(save_changes=True)

    # Apply developer tools
    if config.developer_tools:
        logger.info("Installing developer tools...")
        devenv = DeveloperEnvironment(working_image)
        devenv.mount()
        devenv.configure_developer_mode()
        devenv.install_git()
        devenv.unmount(save_changes=True)

    # Apply creative suite
    if config.creative_suite:
        logger.info("Installing creative suite...")
        creative = CreativeSuite(working_image)
        creative.mount()
        creative.install_obs_studio()
        creative.install_gimp()
        creative.install_audacity()
        creative.unmount(save_changes=True)

    # Apply debloating
    if config.debloat_level != "none":
        logger.info(f"Applying debloating ({config.debloat_level})...")
        debloat = DebloatManager(working_image)
        debloat.mount()

        level_map = {
            "minimal": DebloatLevel.MINIMAL,
            "moderate": DebloatLevel.MODERATE,
            "aggressive": DebloatLevel.AGGRESSIVE,
        }
        debloat.remove_bloatware(level_map[config.debloat_level])
        debloat.unmount(save_changes=True)

    # Apply privacy hardening
    if config.privacy_hardening:
        logger.info("Applying privacy hardening...")
        privacy = PrivacyHardening(working_image)
        privacy.mount()
        privacy.disable_telemetry()
        privacy.disable_advertising_id()
        privacy.configure_dns_over_https()
        privacy.unmount(save_changes=True)

    # Apply theme
    logger.info(f"Applying theme ({config.theme})...")
    theme = ThemeManager(working_image)
    theme.mount()
    theme.set_default_theme(config.theme)
    theme.customize_taskbar(position=config.taskbar_position)
    theme.unmount(save_changes=True)

    # Install packages
    if config.packages:
        logger.info("Installing packages...")
        pkg_mgr = PackageManager(working_image)
        pkg_mgr.mount()
        pkg_mgr.install_winget_packages(config.packages)
        pkg_mgr.unmount(save_changes=True)

    # Install browsers
    if config.browsers:
        logger.info("Installing browsers...")
        browsers = BrowserBundler(working_image)
        browsers.mount()
        for browser in config.browsers:
            if browser == "chrome":
                browsers.install_chrome()
            elif browser == "firefox":
                browsers.install_firefox()
            elif browser == "brave":
                browsers.install_brave()
        browsers.unmount(save_changes=True)

    # Install gaming launchers
    if config.gaming_launchers:
        logger.info("Installing gaming launchers...")
        launchers = GamingLaunchers(working_image)
        launchers.mount()
        for launcher in config.gaming_launchers:
            if launcher == "steam":
                launchers.install_steam()
            elif launcher == "epic":
                launchers.install_epic_games()
            elif launcher == "gog":
                launchers.install_gog_galaxy()
        launchers.unmount(save_changes=True)

    # Configure Windows features
    if config.enable_wsl2 or config.enable_hyperv or config.enable_sandbox:
        logger.info("Configuring Windows features...")
        features = FeatureManager(working_image)
        features.mount()
        if config.enable_wsl2:
            features.enable_wsl2()
        if config.enable_hyperv:
            features.enable_hyperv()
        if config.enable_sandbox:
            features.enable_windows_sandbox()
        features.unmount(save_changes=True)

    # Apply performance optimization
    if config.performance_optimization:
        logger.info("Applying performance optimizations...")
        optimizer = SystemOptimizer(working_image)
        optimizer.mount()
        optimizer.optimize_boot_time()
        optimizer.disable_hibernation()
        optimizer.unmount(save_changes=True)

    # Apply network optimization
    if config.network_optimization:
        logger.info("Applying network optimizations...")
        network = NetworkOptimizer(working_image)
        network.mount()
        network.optimize_tcp_settings()
        network.reduce_network_latency()
        network.unmount(save_changes=True)

    # Configure backup
    if config.enable_backup:
        logger.info("Configuring backup integration...")
        backup = BackupIntegration(working_image)
        backup.mount()
        backup.configure_file_history()
        backup.enable_system_restore()
        backup.unmount(save_changes=True)

    logger.info(f"Profile applied successfully: {config.name}")
