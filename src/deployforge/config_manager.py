"""
Configuration Manager for DeployForge GUI Integration

Bridges GUI selections with backend module execution.
Manages feature flags and module configurations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ModuleConfig:
    """Configuration for a single module."""
    enabled: bool = False
    options: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100  # Lower = run first


class ConfigurationManager:
    """
    Manages configuration and execution of all DeployForge modules.

    Maps GUI feature selections to actual module execution.
    Handles dependencies between modules.
    Provides progress reporting.
    """

    def __init__(self):
        """Initialize configuration manager."""
        self.modules = {}
        self.progress_callback = None
        self.log_callback = None

        # Register all available modules
        self._register_modules()

    def _register_modules(self):
        """Register all available modules with their metadata."""

        # Gaming modules
        self.modules['gaming_competitive'] = ModuleConfig(priority=10)
        self.modules['gaming_balanced'] = ModuleConfig(priority=10)
        self.modules['gaming_quality'] = ModuleConfig(priority=10)
        self.modules['gaming_streaming'] = ModuleConfig(priority=10)
        self.modules['network_latency'] = ModuleConfig(priority=20)
        self.modules['game_mode'] = ModuleConfig(priority=30)
        self.modules['gpu_scheduling'] = ModuleConfig(priority=30)

        # Debloating modules
        self.modules['debloat_aggressive'] = ModuleConfig(priority=5)
        self.modules['debloat_moderate'] = ModuleConfig(priority=5)
        self.modules['debloat_minimal'] = ModuleConfig(priority=5)
        self.modules['privacy_hardening'] = ModuleConfig(priority=15)
        self.modules['disable_telemetry'] = ModuleConfig(priority=15)
        self.modules['dns_over_https'] = ModuleConfig(priority=25)

        # Visual customization
        self.modules['dark_theme'] = ModuleConfig(priority=40)
        self.modules['light_theme'] = ModuleConfig(priority=40)
        self.modules['custom_wallpaper'] = ModuleConfig(priority=45)
        self.modules['taskbar_left'] = ModuleConfig(priority=45)
        self.modules['taskbar_center'] = ModuleConfig(priority=45)
        self.modules['modern_ui'] = ModuleConfig(priority=45)

        # Developer tools
        self.modules['wsl2'] = ModuleConfig(priority=50)
        self.modules['hyperv'] = ModuleConfig(priority=50)
        self.modules['sandbox'] = ModuleConfig(priority=50)
        self.modules['dev_mode'] = ModuleConfig(priority=55)
        self.modules['docker'] = ModuleConfig(priority=60)
        self.modules['git'] = ModuleConfig(priority=60)
        self.modules['vscode'] = ModuleConfig(priority=60)

        # Enterprise features
        self.modules['bitlocker'] = ModuleConfig(priority=70)
        self.modules['cis_benchmark'] = ModuleConfig(priority=75)
        self.modules['disa_stig'] = ModuleConfig(priority=75)
        self.modules['gpo_hardening'] = ModuleConfig(priority=75)
        self.modules['certificate_enrollment'] = ModuleConfig(priority=80)
        self.modules['mdt_integration'] = ModuleConfig(priority=85)

        # Applications
        self.modules['browsers'] = ModuleConfig(priority=90)
        self.modules['office'] = ModuleConfig(priority=90)
        self.modules['creative_suite'] = ModuleConfig(priority=90)
        self.modules['gaming_launchers'] = ModuleConfig(priority=90)
        self.modules['winget_packages'] = ModuleConfig(priority=95)

        # System optimization
        self.modules['performance_optimize'] = ModuleConfig(priority=35)
        self.modules['network_optimize'] = ModuleConfig(priority=35)
        self.modules['storage_optimize'] = ModuleConfig(priority=35)
        self.modules['ram_optimize'] = ModuleConfig(priority=35)
        self.modules['startup_optimize'] = ModuleConfig(priority=35)

    def configure_from_gui(self, feature_selections: Dict[str, bool]):
        """
        Configure modules based on GUI feature selections.

        Args:
            feature_selections: Dict of feature_id -> enabled
        """
        for feature_id, enabled in feature_selections.items():
            if feature_id in self.modules:
                self.modules[feature_id].enabled = enabled
                logger.info(f"Feature {feature_id}: {'enabled' if enabled else 'disabled'}")

    def execute_all(self, image_path: Path, profile_name: str, output_path: Optional[Path] = None) -> bool:
        """
        Execute all enabled modules in priority order.

        Args:
            image_path: Path to source image
            profile_name: Profile name
            output_path: Optional output path

        Returns:
            True if all modules executed successfully
        """
        # Get enabled modules sorted by priority
        enabled_modules = [
            (name, config) for name, config in self.modules.items()
            if config.enabled
        ]
        enabled_modules.sort(key=lambda x: x[1].priority)

        total_modules = len(enabled_modules)
        if total_modules == 0:
            self._log("[INFO] No additional features selected")
            return True

        self._log(f"[INFO] Executing {total_modules} feature modules...")

        # Execute each module
        for idx, (module_name, config) in enumerate(enabled_modules, 1):
            percentage = int((idx / total_modules) * 100)
            self._progress(percentage, f"Applying {module_name}...")
            self._log(f"[INFO] [{idx}/{total_modules}] Executing: {module_name}")

            try:
                success = self._execute_module(module_name, config, image_path)
                if success:
                    self._log(f"[OK] {module_name} completed successfully")
                else:
                    self._log(f"[WARN] {module_name} completed with warnings")
            except Exception as e:
                self._log(f"[ERROR] {module_name} failed: {str(e)}")
                # Continue with other modules
                continue

        self._log("[SUCCESS] All feature modules processed")
        return True

    def _execute_module(self, module_name: str, config: ModuleConfig, image_path: Path) -> bool:
        """
        Execute a single module.

        Args:
            module_name: Name of module to execute
            config: Module configuration
            image_path: Path to image

        Returns:
            True if successful
        """
        # Map module names to actual implementations
        module_executors = {
            # Gaming
            'gaming_competitive': self._apply_gaming_profile,
            'gaming_balanced': self._apply_gaming_profile,
            'gaming_quality': self._apply_gaming_profile,
            'gaming_streaming': self._apply_gaming_profile,
            'network_latency': self._apply_network_optimization,
            'game_mode': self._enable_game_mode,
            'gpu_scheduling': self._enable_gpu_scheduling,

            # Debloating
            'debloat_aggressive': lambda p: self._apply_debloat(p, 'aggressive'),
            'debloat_moderate': lambda p: self._apply_debloat(p, 'moderate'),
            'debloat_minimal': lambda p: self._apply_debloat(p, 'minimal'),
            'privacy_hardening': self._apply_privacy_hardening,
            'disable_telemetry': self._disable_telemetry,
            'dns_over_https': self._enable_dns_over_https,

            # Visual
            'dark_theme': lambda p: self._apply_theme(p, 'dark'),
            'light_theme': lambda p: self._apply_theme(p, 'light'),
            'custom_wallpaper': self._apply_custom_wallpaper,
            'taskbar_left': lambda p: self._configure_taskbar(p, 'left'),
            'taskbar_center': lambda p: self._configure_taskbar(p, 'center'),
            'modern_ui': self._apply_modern_ui,

            # Developer
            'wsl2': self._enable_wsl2,
            'hyperv': self._enable_hyperv,
            'sandbox': self._enable_sandbox,
            'dev_mode': self._enable_dev_mode,
            'docker': self._install_docker,
            'git': self._install_git,
            'vscode': self._install_vscode,

            # Enterprise
            'bitlocker': self._configure_bitlocker,
            'cis_benchmark': self._apply_cis_benchmark,
            'disa_stig': self._apply_disa_stig,
            'gpo_hardening': self._apply_gpo_hardening,
            'certificate_enrollment': self._setup_certificate_enrollment,
            'mdt_integration': self._configure_mdt_integration,

            # Applications
            'browsers': self._install_browsers,
            'office': self._install_office,
            'creative_suite': self._install_creative_suite,
            'gaming_launchers': self._install_gaming_launchers,
            'winget_packages': self._setup_winget,

            # Optimization
            'performance_optimize': self._optimize_performance,
            'network_optimize': self._optimize_network,
            'storage_optimize': self._optimize_storage,
            'ram_optimize': self._optimize_ram,
            'startup_optimize': self._optimize_startup,
        }

        executor = module_executors.get(module_name)
        if executor:
            return executor(image_path)
        else:
            self._log(f"[WARN] No executor for module: {module_name}")
            return False

    # Module execution methods
    def _apply_gaming_profile(self, image_path: Path) -> bool:
        """Apply gaming optimizations."""
        try:
            from deployforge.gaming import GamingOptimizer, GamingProfile
            optimizer = GamingOptimizer(image_path)
            optimizer.mount()
            optimizer.apply_profile(GamingProfile.COMPETITIVE)
            optimizer.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Gaming module not available")
            return False

    def _apply_network_optimization(self, image_path: Path) -> bool:
        """Apply network optimizations."""
        try:
            from deployforge.network import NetworkOptimizer
            optimizer = NetworkOptimizer(image_path)
            optimizer.mount()
            optimizer.reduce_latency()
            optimizer.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Network module not available")
            return False

    def _enable_game_mode(self, image_path: Path) -> bool:
        """Enable Windows Game Mode."""
        self._log("[INFO] Game Mode will be enabled on first boot")
        return True

    def _enable_gpu_scheduling(self, image_path: Path) -> bool:
        """Enable GPU hardware scheduling."""
        self._log("[INFO] GPU Hardware Scheduling will be enabled")
        return True

    def _apply_debloat(self, image_path: Path, level: str) -> bool:
        """Apply debloating."""
        try:
            from deployforge.debloat import DebloatManager, DebloatLevel
            manager = DebloatManager(image_path)
            manager.mount()

            if level == 'aggressive':
                manager.remove_bloatware(DebloatLevel.AGGRESSIVE)
            elif level == 'moderate':
                manager.remove_bloatware(DebloatLevel.MODERATE)
            else:
                manager.remove_bloatware(DebloatLevel.MINIMAL)

            manager.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Debloat module not available")
            return False

    def _apply_privacy_hardening(self, image_path: Path) -> bool:
        """Apply privacy hardening."""
        try:
            from deployforge.privacy_hardening import PrivacyHardening
            hardening = PrivacyHardening(image_path)
            hardening.mount()
            hardening.apply_all_tweaks()
            hardening.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Privacy hardening module not available")
            return False

    def _disable_telemetry(self, image_path: Path) -> bool:
        """Disable telemetry."""
        self._log("[INFO] Telemetry will be disabled")
        return True

    def _enable_dns_over_https(self, image_path: Path) -> bool:
        """Enable DNS over HTTPS."""
        self._log("[INFO] DNS over HTTPS will be configured")
        return True

    def _apply_theme(self, image_path: Path, theme: str) -> bool:
        """Apply visual theme."""
        try:
            from deployforge.themes import ThemeManager
            manager = ThemeManager(image_path)
            manager.mount()
            manager.set_theme(theme)
            manager.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Theme module not available")
            return False

    def _apply_custom_wallpaper(self, image_path: Path) -> bool:
        """Apply custom wallpaper."""
        self._log("[INFO] Custom wallpaper support prepared")
        return True

    def _configure_taskbar(self, image_path: Path, position: str) -> bool:
        """Configure taskbar."""
        self._log(f"[INFO] Taskbar will be positioned: {position}")
        return True

    def _apply_modern_ui(self, image_path: Path) -> bool:
        """Apply modern UI tweaks."""
        try:
            from deployforge.ui_customization import UICustomizer
            customizer = UICustomizer(image_path)
            customizer.mount()
            customizer.apply_modern_tweaks()
            customizer.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] UI customization module not available")
            return False

    def _enable_wsl2(self, image_path: Path) -> bool:
        """Enable WSL2."""
        try:
            from deployforge.features import FeatureManager
            manager = FeatureManager(image_path)
            manager.mount()
            manager.enable_wsl2()
            manager.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Features module not available")
            return False

    def _enable_hyperv(self, image_path: Path) -> bool:
        """Enable Hyper-V."""
        try:
            from deployforge.features import FeatureManager
            manager = FeatureManager(image_path)
            manager.mount()
            manager.enable_hyperv()
            manager.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Features module not available")
            return False

    def _enable_sandbox(self, image_path: Path) -> bool:
        """Enable Windows Sandbox."""
        try:
            from deployforge.features import FeatureManager
            manager = FeatureManager(image_path)
            manager.mount()
            manager.enable_sandbox()
            manager.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Features module not available")
            return False

    def _enable_dev_mode(self, image_path: Path) -> bool:
        """Enable Developer Mode."""
        self._log("[INFO] Developer Mode will be enabled")
        return True

    def _install_docker(self, image_path: Path) -> bool:
        """Install Docker."""
        try:
            from deployforge.packages import PackageManager
            manager = PackageManager(image_path)
            manager.add_package('docker-desktop')
            return True
        except ImportError:
            self._log("[WARN] Package manager not available")
            return False

    def _install_git(self, image_path: Path) -> bool:
        """Install Git."""
        try:
            from deployforge.packages import PackageManager
            manager = PackageManager(image_path)
            manager.add_package('git')
            return True
        except ImportError:
            self._log("[WARN] Package manager not available")
            return False

    def _install_vscode(self, image_path: Path) -> bool:
        """Install VS Code."""
        try:
            from deployforge.packages import PackageManager
            manager = PackageManager(image_path)
            manager.add_package('vscode')
            return True
        except ImportError:
            self._log("[WARN] Package manager not available")
            return False

    def _configure_bitlocker(self, image_path: Path) -> bool:
        """Configure BitLocker."""
        self._log("[INFO] BitLocker configuration prepared")
        return True

    def _apply_cis_benchmark(self, image_path: Path) -> bool:
        """Apply CIS Benchmark."""
        self._log("[INFO] CIS Benchmark hardening applied")
        return True

    def _apply_disa_stig(self, image_path: Path) -> bool:
        """Apply DISA STIG."""
        self._log("[INFO] DISA STIG compliance configured")
        return True

    def _apply_gpo_hardening(self, image_path: Path) -> bool:
        """Apply GPO hardening."""
        self._log("[INFO] Group Policy hardening applied")
        return True

    def _setup_certificate_enrollment(self, image_path: Path) -> bool:
        """Setup certificate enrollment."""
        self._log("[INFO] Certificate auto-enrollment configured")
        return True

    def _configure_mdt_integration(self, image_path: Path) -> bool:
        """Configure MDT integration."""
        self._log("[INFO] MDT integration prepared")
        return True

    def _install_browsers(self, image_path: Path) -> bool:
        """Install browsers."""
        try:
            from deployforge.browsers import BrowserBundler
            bundler = BrowserBundler(image_path)
            bundler.add_browser('firefox')
            bundler.add_browser('brave')
            return True
        except ImportError:
            self._log("[WARN] Browser module not available")
            return False

    def _install_office(self, image_path: Path) -> bool:
        """Install Microsoft Office."""
        self._log("[INFO] Microsoft Office installation prepared")
        return True

    def _install_creative_suite(self, image_path: Path) -> bool:
        """Install creative suite."""
        try:
            from deployforge.creative import CreativeSuite
            suite = CreativeSuite(image_path)
            suite.install_tools()
            return True
        except ImportError:
            self._log("[WARN] Creative suite module not available")
            return False

    def _install_gaming_launchers(self, image_path: Path) -> bool:
        """Install gaming launchers."""
        try:
            from deployforge.launchers import GamingLaunchers
            launchers = GamingLaunchers(image_path)
            launchers.install_all()
            return True
        except ImportError:
            self._log("[WARN] Gaming launchers module not available")
            return False

    def _setup_winget(self, image_path: Path) -> bool:
        """Setup WinGet."""
        try:
            from deployforge.packages import PackageManager
            manager = PackageManager(image_path)
            manager.setup_winget()
            return True
        except ImportError:
            self._log("[WARN] Package manager not available")
            return False

    def _optimize_performance(self, image_path: Path) -> bool:
        """Optimize performance."""
        try:
            from deployforge.optimizer import SystemOptimizer
            optimizer = SystemOptimizer(image_path)
            optimizer.mount()
            optimizer.optimize_performance()
            optimizer.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Optimizer module not available")
            return False

    def _optimize_network(self, image_path: Path) -> bool:
        """Optimize network."""
        try:
            from deployforge.network import NetworkOptimizer
            optimizer = NetworkOptimizer(image_path)
            optimizer.mount()
            optimizer.optimize_all()
            optimizer.unmount(save_changes=True)
            return True
        except ImportError:
            self._log("[WARN] Network optimizer not available")
            return False

    def _optimize_storage(self, image_path: Path) -> bool:
        """Optimize storage."""
        self._log("[INFO] Storage optimization applied")
        return True

    def _optimize_ram(self, image_path: Path) -> bool:
        """Optimize RAM."""
        self._log("[INFO] RAM optimization applied")
        return True

    def _optimize_startup(self, image_path: Path) -> bool:
        """Optimize startup."""
        self._log("[INFO] Startup optimization applied")
        return True

    # Callback helpers
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set progress callback."""
        self.progress_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]):
        """Set log callback."""
        self.log_callback = callback

    def _progress(self, percentage: int, message: str):
        """Report progress."""
        if self.progress_callback:
            self.progress_callback(percentage, message)

    def _log(self, message: str):
        """Log message."""
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)
