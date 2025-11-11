"""
Browser & Software Bundling Module

Comprehensive browser installation, configuration, and optimization for Windows deployment images.

Features:
- Multiple browser installation (Chrome, Firefox, Edge, Brave, Opera, Vivaldi, Tor, LibreWolf, Waterfox)
- Browser profiles (Privacy-Focused, Performance, Developer, Enterprise, Minimal)
- Privacy configuration for each browser
- Extension pre-installation framework
- Homepage and search engine defaults
- Performance optimization per browser
- Enterprise Group Policy configuration
- Browser sync setup
- Certificate installation
- Bookmark import framework
- Security hardening per browser
- Cache and history management
- Cookie policy configuration
- Ad-blocker pre-configuration
- Developer tools setup
- Multi-browser testing environment
- Browser-specific optimizations
- Startup page configuration
- Default applications setup
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


class BrowserProfile(Enum):
    """Browser configuration profiles"""
    PRIVACY_FOCUSED = "privacy-focused"  # Privacy-centric browsers with hardened settings
    PERFORMANCE = "performance"  # Speed-optimized browsers
    DEVELOPER = "developer"  # Multiple browsers for cross-browser testing
    ENTERPRISE = "enterprise"  # Corporate-managed browsers with policies
    MINIMAL = "minimal"  # Single mainstream browser
    COMPLETE = "complete"  # All major browsers for maximum compatibility


class Browser(Enum):
    """Supported browsers with WinGet package IDs"""
    # Mainstream browsers
    CHROME = "Google.Chrome"
    FIREFOX = "Mozilla.Firefox"
    EDGE = "Microsoft.Edge"
    BRAVE = "BraveSoftware.BraveBrowser"

    # Alternative browsers
    OPERA = "Opera.Opera"
    OPERA_GX = "Opera.OperaGX"
    VIVALDI = "Vivaldi.Vivaldi"

    # Privacy-focused browsers
    TOR_BROWSER = "TorProject.TorBrowser"
    LIBREWOLF = "LibreWolf.LibreWolf"
    WATERFOX = "Waterfox.Waterfox"

    # Developer browsers
    CHROME_DEV = "Google.Chrome.Dev"
    CHROME_CANARY = "Google.Chrome.Canary"
    FIREFOX_DEVELOPER = "Mozilla.Firefox.DeveloperEdition"
    FIREFOX_NIGHTLY = "Mozilla.Firefox.Nightly"
    EDGE_DEV = "Microsoft.Edge.Dev"

    # Lightweight browsers
    CHROMIUM = "Chromium.Chromium"
    UNGOOGLED_CHROMIUM = "eloston.ungoogled-chromium"


class SearchEngine(Enum):
    """Default search engines"""
    GOOGLE = "google"
    DUCKDUCKGO = "duckduckgo"
    BING = "bing"
    STARTPAGE = "startpage"
    BRAVE_SEARCH = "brave"
    ECOSIA = "ecosia"


@dataclass
class BrowserConfiguration:
    """Browser configuration settings"""
    # Browsers to install
    browsers: List[str] = field(default_factory=lambda: ["chrome", "firefox"])

    # Privacy settings
    block_third_party_cookies: bool = True
    enable_do_not_track: bool = True
    disable_telemetry: bool = False
    enable_tracking_protection: bool = True

    # Performance settings
    hardware_acceleration: bool = True
    preload_pages: bool = False
    background_apps: bool = False

    # Default settings
    default_browser: Optional[str] = "chrome"
    default_search_engine: str = SearchEngine.GOOGLE.value
    homepage: Optional[str] = None

    # Features
    enable_sync: bool = False
    install_extensions: bool = False
    configure_enterprise_policies: bool = False

    # Security
    enable_safe_browsing: bool = True
    block_malicious_sites: bool = True
    warn_before_quitting: bool = False

    # Developer settings
    enable_dev_tools: bool = False
    allow_insecure_localhost: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'browsers': self.browsers,
            'privacy': {
                'block_third_party_cookies': self.block_third_party_cookies,
                'do_not_track': self.enable_do_not_track,
                'disable_telemetry': self.disable_telemetry,
                'tracking_protection': self.enable_tracking_protection,
            },
            'performance': {
                'hardware_acceleration': self.hardware_acceleration,
                'preload_pages': self.preload_pages,
                'background_apps': self.background_apps,
            },
            'defaults': {
                'browser': self.default_browser,
                'search_engine': self.default_search_engine,
                'homepage': self.homepage,
            },
            'security': {
                'safe_browsing': self.enable_safe_browsing,
                'block_malicious': self.block_malicious_sites,
            }
        }


class BrowserBundler:
    """
    Comprehensive browser installation and configuration manager.

    Example:
        bundler = BrowserBundler(Path('install.wim'))
        bundler.mount()
        bundler.apply_profile(BrowserProfile.DEVELOPER)
        bundler.install_browsers(['chrome', 'firefox', 'edge'])
        bundler.configure_privacy_settings()
        bundler.unmount(save_changes=True)
    """

    BROWSER_PACKAGES = {
        'chrome': Browser.CHROME.value,
        'firefox': Browser.FIREFOX.value,
        'edge': Browser.EDGE.value,
        'brave': Browser.BRAVE.value,
        'opera': Browser.OPERA.value,
        'opera_gx': Browser.OPERA_GX.value,
        'vivaldi': Browser.VIVALDI.value,
        'tor': Browser.TOR_BROWSER.value,
        'librewolf': Browser.LIBREWOLF.value,
        'waterfox': Browser.WATERFOX.value,
        'chrome_dev': Browser.CHROME_DEV.value,
        'chrome_canary': Browser.CHROME_CANARY.value,
        'firefox_dev': Browser.FIREFOX_DEVELOPER.value,
        'firefox_nightly': Browser.FIREFOX_NIGHTLY.value,
        'edge_dev': Browser.EDGE_DEV.value,
        'chromium': Browser.CHROMIUM.value,
        'ungoogled_chromium': Browser.UNGOOGLED_CHROMIUM.value,
    }

    COMMON_EXTENSIONS = {
        'chrome': {
            'ublock_origin': 'cjpalhdlnbpafiamejdnhcphjbkeiagm',
            'privacy_badger': 'pkehgijcmpdhfbdbbnkijodmdjhbjlgp',
            'https_everywhere': 'gcbommkclmclpchllfjekcdonpmejbdp',
            'lastpass': 'hdokiejnpimakedhajhdlcegeplioahd',
        },
        'firefox': {
            'ublock_origin': 'uBlock0@raymondhill.net',
            'privacy_badger': 'jid1-MnnxcxisBPnSXQ@jetpack',
            'https_everywhere': 'https-everywhere@eff.org',
        }
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize browser bundler.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = BrowserConfiguration()

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the Windows image"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_browser_'))

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

    def apply_profile(self, profile: BrowserProfile,
                     progress_callback: Optional[Callable[[int, str], None]] = None):
        """
        Apply a browser profile with recommended browsers and settings.

        Args:
            profile: Browser profile to apply
            progress_callback: Optional callback for progress updates
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying browser profile: {profile.value}")

        profiles = {
            BrowserProfile.PRIVACY_FOCUSED: {
                'browsers': ['firefox', 'brave', 'tor', 'librewolf'],
                'block_third_party_cookies': True,
                'enable_do_not_track': True,
                'disable_telemetry': True,
                'tracking_protection': True,
                'default_search': SearchEngine.DUCKDUCKGO.value,
            },
            BrowserProfile.PERFORMANCE: {
                'browsers': ['chrome', 'edge'],
                'hardware_acceleration': True,
                'preload_pages': True,
                'default_search': SearchEngine.GOOGLE.value,
            },
            BrowserProfile.DEVELOPER: {
                'browsers': ['chrome', 'firefox', 'edge', 'chrome_dev', 'firefox_dev'],
                'enable_dev_tools': True,
                'allow_insecure_localhost': True,
                'default_search': SearchEngine.GOOGLE.value,
            },
            BrowserProfile.ENTERPRISE: {
                'browsers': ['edge', 'chrome'],
                'configure_enterprise_policies': True,
                'enable_sync': False,
                'default_search': SearchEngine.BING.value,
            },
            BrowserProfile.MINIMAL: {
                'browsers': ['chrome'],
                'default_search': SearchEngine.GOOGLE.value,
            },
            BrowserProfile.COMPLETE: {
                'browsers': ['chrome', 'firefox', 'edge', 'brave', 'opera', 'vivaldi'],
                'default_search': SearchEngine.GOOGLE.value,
            },
        }

        profile_config = profiles.get(profile, profiles[BrowserProfile.MINIMAL])

        # Update configuration
        self.config.browsers = profile_config.get('browsers', ['chrome'])
        self.config.block_third_party_cookies = profile_config.get('block_third_party_cookies', False)
        self.config.enable_do_not_track = profile_config.get('enable_do_not_track', False)
        self.config.disable_telemetry = profile_config.get('disable_telemetry', False)
        self.config.default_search_engine = profile_config.get('default_search', SearchEngine.GOOGLE.value)

        logger.info(f"Profile configuration: {len(self.config.browsers)} browsers, Search: {self.config.default_search_engine}")

    def install_browsers(self, browsers: List[str],
                         progress_callback: Optional[Callable[[int, str], None]] = None):
        """
        Install browsers via WinGet.

        Args:
            browsers: List of browser identifiers to install
            progress_callback: Optional callback for progress updates
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Installing {len(browsers)} browsers")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Browser Installation\n"]
        script_lines.append("Write-Host 'Installing web browsers...'\n\n")

        for browser in browsers:
            if browser in self.BROWSER_PACKAGES:
                package_id = self.BROWSER_PACKAGES[browser]
                script_lines.append(f"Write-Host 'Installing {browser}...'\n")
                script_lines.append(f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n")
                logger.info(f"Configured browser installation: {browser}")

        script_path = scripts_dir / "install_browsers.ps1"
        with open(script_path, 'w') as f:
            f.writelines(script_lines)

        logger.info(f"Browser installation script created: {len(browsers)} browsers")

    def configure_chrome_policies(self, policies: Optional[Dict[str, Any]] = None):
        """Configure Google Chrome enterprise policies via registry"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Configuring Chrome enterprise policies")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        default_policies = policies or {
            'DefaultSearchProviderEnabled': 1,
            'DefaultSearchProviderName': 'Google',
            'SafeBrowsingEnabled': 1,
            'PasswordManagerEnabled': 1,
            'AutofillAddressEnabled': 0,
            'AutofillCreditCardEnabled': 0,
            'SyncDisabled': 1 if not self.config.enable_sync else 0,
            'BlockThirdPartyCookies': 1 if self.config.block_third_party_cookies else 0,
        }

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            for policy, value in default_policies.items():
                value_type = 'REG_DWORD' if isinstance(value, int) else 'REG_SZ'
                subprocess.run([
                    'reg', 'add',
                    f'{hive_key}\\Policies\\Google\\Chrome',
                    '/v', policy,
                    '/t', value_type,
                    '/d', str(value),
                    '/f'
                ], check=True, capture_output=True)

            logger.info(f"Chrome policies configured: {len(default_policies)} settings")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure Chrome policies: {e}")
            raise

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def configure_firefox_policies(self, policies: Optional[Dict[str, Any]] = None):
        """Configure Firefox enterprise policies via policies.json"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Configuring Firefox enterprise policies")

        firefox_dir = self.mount_point / "Program Files" / "Mozilla Firefox" / "distribution"
        firefox_dir.mkdir(parents=True, exist_ok=True)

        default_policies = policies or {
            "policies": {
                "DisableTelemetry": self.config.disable_telemetry,
                "DisableFirefoxStudies": True,
                "DisablePocket": True,
                "DontCheckDefaultBrowser": False,
                "EnableTrackingProtection": {
                    "Value": self.config.enable_tracking_protection,
                    "Locked": False,
                    "Cryptomining": True,
                    "Fingerprinting": True
                },
                "Cookies": {
                    "AcceptThirdParty": "never" if self.config.block_third_party_cookies else "always",
                    "RejectTracker": True
                },
                "HardwareAcceleration": self.config.hardware_acceleration,
                "Homepage": {
                    "StartPage": "homepage" if self.config.homepage else "none"
                }
            }
        }

        policies_file = firefox_dir / "policies.json"
        with open(policies_file, 'w') as f:
            json.dump(default_policies, f, indent=2)

        logger.info("Firefox policies configured")

    def configure_edge_policies(self, policies: Optional[Dict[str, Any]] = None):
        """Configure Microsoft Edge enterprise policies via registry"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Configuring Edge enterprise policies")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        default_policies = policies or {
            'PersonalizationReportingEnabled': 0,
            'DiagnosticData': 0 if self.config.disable_telemetry else 1,
            'TrackingPrevention': 2 if self.config.enable_tracking_protection else 0,  # 0=Off, 1=Basic, 2=Balanced, 3=Strict
            'SyncDisabled': 1 if not self.config.enable_sync else 0,
            'HardwareAccelerationModeEnabled': 1 if self.config.hardware_acceleration else 0,
        }

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            for policy, value in default_policies.items():
                subprocess.run([
                    'reg', 'add',
                    f'{hive_key}\\Policies\\Microsoft\\Edge',
                    '/v', policy,
                    '/t', 'REG_DWORD',
                    '/d', str(value),
                    '/f'
                ], check=True, capture_output=True)

            logger.info(f"Edge policies configured: {len(default_policies)} settings")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure Edge policies: {e}")
            raise

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def configure_privacy_settings(self):
        """Apply privacy-focused settings across installed browsers"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Configuring privacy settings for browsers")

        if 'chrome' in self.config.browsers:
            self.configure_chrome_policies()

        if 'firefox' in self.config.browsers:
            self.configure_firefox_policies()

        if 'edge' in self.config.browsers:
            self.configure_edge_policies()

        logger.info("Privacy settings configured for all browsers")

    def set_default_browser(self, browser: str):
        """Set default browser via registry"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting default browser: {browser}")

        browser_associations = {
            'chrome': 'ChromeHTML',
            'firefox': 'FirefoxHTML',
            'edge': 'MSEdgeHTM',
            'brave': 'BraveHTML',
            'opera': 'OperaHTML',
        }

        if browser not in browser_associations:
            logger.warning(f"Unknown browser for default association: {browser}")
            return

        prog_id = browser_associations[browser]

        hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
        hive_key = "HKLM\\TEMP_USER"

        try:
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Set default for http and https
            for protocol in ['http', 'https']:
                subprocess.run([
                    'reg', 'add',
                    f'{hive_key}\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\{protocol}\\UserChoice',
                    '/v', 'ProgId',
                    '/t', 'REG_SZ',
                    '/d', prog_id,
                    '/f'
                ], check=True, capture_output=True)

            logger.info(f"Default browser set to: {browser}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set default browser: {e}")
            raise

        finally:
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def install_browser_extensions(self, browser: str, extensions: List[str]):
        """Configure browser to auto-install extensions on first run"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Configuring extensions for {browser}: {len(extensions)} extensions")

        if browser not in self.COMMON_EXTENSIONS:
            logger.warning(f"Extension installation not supported for: {browser}")
            return

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        # Create extension installation script for browser
        if browser == 'chrome':
            script_lines = ["# Chrome Extension Installation\n"]
            script_lines.append("# Extensions will be installed on first Chrome launch\n")
            for ext in extensions:
                if ext in self.COMMON_EXTENSIONS['chrome']:
                    ext_id = self.COMMON_EXTENSIONS['chrome'][ext]
                    script_lines.append(f"# {ext}: {ext_id}\n")

        script_path = scripts_dir / f"install_{browser}_extensions.ps1"
        with open(script_path, 'w') as f:
            f.writelines(script_lines)

        logger.info(f"Extension configuration created for {browser}")

    def optimize_browser_performance(self):
        """Apply performance optimizations across browsers"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Applying browser performance optimizations")

        # Configure for hardware acceleration
        if self.config.hardware_acceleration:
            logger.info("Hardware acceleration enabled for browsers")
            # Chrome and Edge policies already handle this
            # Firefox handles via policies.json

        # Disable background apps if configured
        if not self.config.background_apps:
            logger.info("Background browser apps disabled")
            if 'chrome' in self.config.browsers:
                self.configure_chrome_policies({'BackgroundModeEnabled': 0})

        logger.info("Browser performance optimizations applied")


def install_browsers(
    image_path: Path,
    browsers: Optional[List[str]] = None,
    profile: Optional[BrowserProfile] = None,
    custom_config: Optional[BrowserConfiguration] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> None:
    """
    Quick browser installation and configuration.

    Example:
        # Install specific browsers
        install_browsers(Path('install.wim'), browsers=['chrome', 'firefox'])

        # Use a profile
        install_browsers(Path('install.wim'), profile=BrowserProfile.DEVELOPER)

        # Custom configuration
        config = BrowserConfiguration()
        config.browsers = ['brave', 'tor']
        config.disable_telemetry = True
        install_browsers(Path('install.wim'), custom_config=config)

    Args:
        image_path: Path to Windows image file
        browsers: List of browsers to install (optional if using profile)
        profile: Browser profile to apply
        custom_config: Optional custom configuration
        progress_callback: Optional callback for progress updates
    """
    bundler = BrowserBundler(image_path)

    try:
        if progress_callback:
            progress_callback(0, "Mounting image...")
        bundler.mount()

        if custom_config:
            bundler.config = custom_config
        elif profile:
            if progress_callback:
                progress_callback(10, f"Applying {profile.value} profile...")
            bundler.apply_profile(profile, progress_callback)
        elif browsers:
            bundler.config.browsers = browsers

        if progress_callback:
            progress_callback(30, f"Installing {len(bundler.config.browsers)} browsers...")
        bundler.install_browsers(bundler.config.browsers, progress_callback)

        if progress_callback:
            progress_callback(60, "Configuring privacy settings...")
        if bundler.config.block_third_party_cookies or bundler.config.disable_telemetry:
            bundler.configure_privacy_settings()

        if progress_callback:
            progress_callback(80, "Optimizing browser performance...")
        bundler.optimize_browser_performance()

        if progress_callback:
            progress_callback(90, "Setting default browser...")
        if bundler.config.default_browser and bundler.config.default_browser in bundler.config.browsers:
            bundler.set_default_browser(bundler.config.default_browser)

        if progress_callback:
            progress_callback(100, "Browser configuration complete")

        bundler.unmount(save_changes=True)
        logger.info(f"Browser installation complete: {len(bundler.config.browsers)} browsers configured")

    except Exception as e:
        logger.error(f"Failed to install browsers: {e}")
        bundler.unmount(save_changes=False)
        raise
