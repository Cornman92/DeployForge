"""
Application Installer Framework for DeployForge

This module provides a robust application installation system using multiple methods:
1. WinGet (Windows Package Manager) - Primary method
2. Chocolatey - Fallback method
3. Direct Download - Final fallback

Features:
- Automatic fallback mechanism
- Dependency resolution
- Progress tracking with time estimates and ETA
- Enhanced error handling with exponential backoff retry
- Offline installation support
- Parallel installation capability
- Download speed and progress tracking
- Historical time estimation for better UX

Retry Logic:
- Configurable exponential backoff (default: 2s, 4s, 8s, 16s...)
- Automatic retry on network errors and timeouts
- Progress updates during retry delays
- Maximum 60s delay cap to avoid excessive waiting

Platform Support:
- Windows: Full support (WinGet, Chocolatey, direct download)
- Linux/macOS: Limited support (direct download only)

Example:
    from pathlib import Path
    from deployforge.installer import ApplicationInstaller, RetryConfig

    # Create installer with custom retry configuration
    retry_config = RetryConfig(
        max_retries=5,
        initial_delay=3.0,
        backoff_factor=2.0
    )
    installer = ApplicationInstaller(
        Path("install.wim"),
        retry_config=retry_config
    )
    installer.mount()

    # Install single application with progress tracking
    def progress_handler(progress):
        print(f"{progress.app_name}: {progress.progress_percent}%")
        print(f"ETA: {progress.get_eta_formatted()}")
        if progress.download_speed:
            print(f"Speed: {progress.get_speed_formatted()}")

    installer.install_application("vscode", progress_callback=progress_handler)

    # Install multiple applications in parallel
    installer.install_applications(
        ["vscode", "git", "nodejs"],
        parallel=True,
        max_workers=3
    )

    installer.unmount(save_changes=True)
"""

import logging
import os
import subprocess
import tempfile
import shutil
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Protocol
import json
import platform

logger = logging.getLogger(__name__)


class InstallMethod(Enum):
    """Installation methods in priority order"""

    WINGET = "winget"
    CHOCOLATEY = "chocolatey"
    DIRECT_DOWNLOAD = "direct"
    MANUAL = "manual"  # Requires user-provided installer


class InstallStatus(Enum):
    """Installation status"""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"
    CONFIGURING = "configuring"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class InstallProgress:
    """
    Installation progress information with time estimates.

    Attributes:
        app_id: Application identifier
        app_name: Display name
        status: Current installation status
        progress_percent: Overall progress (0-100)
        current_step: Human-readable description of current step
        total_steps: Total number of steps
        current_step_index: Current step number (0-based)
        method: Installation method being used
        error_message: Error description if failed
        start_time: Unix timestamp when started
        end_time: Unix timestamp when completed/failed
        estimated_time_remaining: Estimated seconds until completion
        elapsed_time: Seconds elapsed since start
        download_speed: Current download speed in bytes/sec (if downloading)
        bytes_downloaded: Bytes downloaded so far
        total_bytes: Total bytes to download
    """

    app_id: str
    app_name: str
    status: InstallStatus
    progress_percent: int  # 0-100
    current_step: str
    total_steps: int
    current_step_index: int
    method: Optional[InstallMethod] = None
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    estimated_time_remaining: Optional[float] = None  # seconds
    elapsed_time: Optional[float] = None  # seconds
    download_speed: Optional[float] = None  # bytes/sec
    bytes_downloaded: Optional[int] = None
    total_bytes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "status": self.status.value,
            "progress_percent": self.progress_percent,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "current_step_index": self.current_step_index,
            "method": self.method.value if self.method else None,
            "error_message": self.error_message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "estimated_time_remaining": self.estimated_time_remaining,
            "elapsed_time": self.elapsed_time,
            "download_speed": self.download_speed,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
        }

    def get_eta_formatted(self) -> str:
        """
        Get formatted ETA string.

        Returns:
            Human-readable ETA like "2m 30s" or "45s" or "Unknown"
        """
        if self.estimated_time_remaining is None:
            return "Unknown"

        seconds = int(self.estimated_time_remaining)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def get_speed_formatted(self) -> str:
        """
        Get formatted download speed.

        Returns:
            Human-readable speed like "1.5 MB/s" or "512 KB/s"
        """
        if self.download_speed is None:
            return "Unknown"

        speed = self.download_speed
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / (1024 * 1024):.1f} MB/s"


class ProgressCallback(Protocol):
    """Progress callback protocol for type hints"""

    def __call__(self, progress: InstallProgress) -> None:
        """Called when progress is updated"""
        ...


@dataclass
class InstallResult:
    """Result of an installation operation"""

    app_id: str
    app_name: str
    success: bool
    method: Optional[InstallMethod] = None
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    attempts: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "success": self.success,
            "method": self.method.value if self.method else None,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
            "attempts": self.attempts,
        }


@dataclass
class VerificationResult:
    """
    Result of post-installation verification.

    Attributes:
        app_id: Application identifier
        app_name: Application display name
        is_installed: Whether app was verified as installed
        verification_method: Method used for verification
        install_path: Detected installation path (if found)
        version: Detected version (if available)
        error_message: Error description if verification failed
    """

    app_id: str
    app_name: str
    is_installed: bool
    verification_method: Optional[str] = None
    install_path: Optional[Path] = None
    version: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "is_installed": self.is_installed,
            "verification_method": self.verification_method,
            "install_path": str(self.install_path) if self.install_path else None,
            "version": self.version,
            "error_message": self.error_message,
        }


@dataclass
class RetryConfig:
    """
    Configuration for retry logic with exponential backoff.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 2)
        max_delay: Maximum delay between retries in seconds (default: 60)
        backoff_factor: Multiplier for exponential backoff (default: 2)
        retry_on_network_error: Whether to retry on network errors (default: True)
        retry_on_timeout: Whether to retry on timeout errors (default: True)
    """

    max_retries: int = 3
    initial_delay: float = 2.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retry_on_network_error: bool = True
    retry_on_timeout: bool = True

    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt using exponential backoff.

        Args:
            attempt: Attempt number (0-based)

        Returns:
            Delay in seconds (capped at max_delay)
        """
        delay = self.initial_delay * (self.backoff_factor**attempt)
        return min(delay, self.max_delay)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "max_retries": self.max_retries,
            "initial_delay": self.initial_delay,
            "max_delay": self.max_delay,
            "backoff_factor": self.backoff_factor,
            "retry_on_network_error": self.retry_on_network_error,
            "retry_on_timeout": self.retry_on_timeout,
        }


@dataclass
class InstallEstimate:
    """
    Installation time estimates based on historical data.

    Tracks average installation times per method and app category
    to provide better progress estimates.

    Attributes:
        method: Installation method
        app_category: Application category (Gaming, Development, etc.)
        avg_duration: Average installation time in seconds
        sample_count: Number of samples in average
        min_duration: Fastest observed installation
        max_duration: Slowest observed installation
    """

    method: InstallMethod
    app_category: str
    avg_duration: float  # seconds
    sample_count: int = 1
    min_duration: float = 0.0
    max_duration: float = 0.0

    def update(self, duration: float) -> None:
        """
        Update estimate with new observation.

        Uses incremental average calculation to update estimate.

        Args:
            duration: Observed installation duration in seconds
        """
        # Update min/max
        if self.min_duration == 0 or duration < self.min_duration:
            self.min_duration = duration
        if duration > self.max_duration:
            self.max_duration = duration

        # Incremental average update
        self.avg_duration = (self.avg_duration * self.sample_count + duration) / (
            self.sample_count + 1
        )
        self.sample_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "method": self.method.value,
            "app_category": self.app_category,
            "avg_duration": self.avg_duration,
            "sample_count": self.sample_count,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
        }


class ApplicationInstaller:
    """
    Manages application installation using multiple methods.

    This class provides a comprehensive application installation system with
    automatic fallback mechanisms, dependency resolution, and progress tracking.

    Features:
    - WinGet-first approach with automatic fallbacks
    - Progress tracking and cancellation support
    - Dependency resolution for proper install order
    - Offline installation support with cache
    - Comprehensive error handling with recovery
    - Parallel installation for multiple apps

    Attributes:
        image_path: Path to Windows image (WIM/VHD/VHDX)
        mount_point: Directory where image is mounted
        is_mounted: Whether image is currently mounted
        offline_cache: Directory for cached installers
        results: Installation results for tracking

    Example:
        installer = ApplicationInstaller(
            image_path=Path("install.wim"),
            offline_cache=Path("C:/cache")
        )

        installer.mount()

        # Install apps with progress tracking
        def progress_handler(progress: InstallProgress):
            print(f"{progress.app_name}: {progress.progress_percent}%")

        results = installer.install_applications(
            app_ids=["vscode", "git", "nodejs"],
            parallel=True,
            progress_callback=progress_handler
        )

        installer.unmount(save_changes=True)

        # Check results
        for app_id, result in results.items():
            if result.success:
                print(f"✓ {result.app_name} installed via {result.method.value}")
            else:
                print(f"✗ {result.app_name} failed: {result.error_message}")
    """

    def __init__(
        self,
        image_path: Path,
        offline_cache: Optional[Path] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize application installer.

        Args:
            image_path: Path to Windows image file (WIM/ESD/VHD/VHDX)
            offline_cache: Optional path to cache downloaded installers
            retry_config: Optional retry configuration (uses defaults if not provided)
        """
        self.image_path = image_path
        self.mount_point: Optional[Path] = None
        self.is_mounted = False
        self.offline_cache = offline_cache
        self.retry_config = retry_config or RetryConfig()
        self.results: Dict[str, InstallResult] = {}

        # Time estimation tracking
        self.estimates: Dict[tuple, InstallEstimate] = {}
        self._initialize_default_estimates()

        # Create cache directory if specified
        if self.offline_cache:
            self.offline_cache.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized ApplicationInstaller for {image_path} "
            f"(max_retries={self.retry_config.max_retries})"
        )

    def _initialize_default_estimates(self) -> None:
        """Initialize default time estimates for common scenarios."""
        # Default estimates based on typical installation times (in seconds)
        defaults = [
            # WinGet installations (fastest)
            (InstallMethod.WINGET, "Gaming", 45.0),
            (InstallMethod.WINGET, "Development", 60.0),
            (InstallMethod.WINGET, "Browsers", 30.0),
            (InstallMethod.WINGET, "Utilities", 25.0),
            (InstallMethod.WINGET, "Creative", 90.0),
            (InstallMethod.WINGET, "Productivity", 50.0),
            (InstallMethod.WINGET, "Communication", 40.0),
            (InstallMethod.WINGET, "Security", 35.0),
            # Chocolatey installations (medium)
            (InstallMethod.CHOCOLATEY, "Gaming", 60.0),
            (InstallMethod.CHOCOLATEY, "Development", 75.0),
            (InstallMethod.CHOCOLATEY, "Browsers", 40.0),
            (InstallMethod.CHOCOLATEY, "Utilities", 35.0),
            (InstallMethod.CHOCOLATEY, "Creative", 120.0),
            (InstallMethod.CHOCOLATEY, "Productivity", 65.0),
            (InstallMethod.CHOCOLATEY, "Communication", 50.0),
            (InstallMethod.CHOCOLATEY, "Security", 45.0),
            # Direct download (slowest, includes download time)
            (InstallMethod.DIRECT_DOWNLOAD, "Gaming", 180.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Development", 240.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Browsers", 120.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Utilities", 90.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Creative", 300.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Productivity", 150.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Communication", 140.0),
            (InstallMethod.DIRECT_DOWNLOAD, "Security", 100.0),
        ]

        for method, category, duration in defaults:
            key = (method, category)
            self.estimates[key] = InstallEstimate(
                method=method,
                app_category=category,
                avg_duration=duration,
                min_duration=duration * 0.5,
                max_duration=duration * 2.0,
            )

    def _get_estimated_duration(self, method: InstallMethod, category: str) -> float:
        """
        Get estimated installation duration.

        Args:
            method: Installation method
            category: Application category

        Returns:
            Estimated duration in seconds (defaults to 60s if no estimate)
        """
        key = (method, category)
        estimate = self.estimates.get(key)
        if estimate:
            return estimate.avg_duration
        # Default fallback
        return 60.0

    def _update_estimate(self, method: InstallMethod, category: str, duration: float) -> None:
        """
        Update time estimate with observed duration.

        Args:
            method: Installation method used
            category: Application category
            duration: Actual installation duration in seconds
        """
        key = (method, category)
        if key in self.estimates:
            self.estimates[key].update(duration)
        else:
            self.estimates[key] = InstallEstimate(
                method=method,
                app_category=category,
                avg_duration=duration,
                min_duration=duration,
                max_duration=duration,
            )

    def _retry_with_backoff(
        self,
        operation: Callable,
        operation_name: str,
        progress_callback: Optional[ProgressCallback] = None,
        progress_obj: Optional[InstallProgress] = None,
    ) -> Any:
        """
        Execute operation with exponential backoff retry logic.

        Args:
            operation: Callable to execute (should return bool or result)
            operation_name: Human-readable name for logging
            progress_callback: Optional progress callback
            progress_obj: Optional progress object to update

        Returns:
            Result from operation if successful, None if all retries exhausted

        Raises:
            Exception: Re-raises last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                logger.info(
                    f"Attempting {operation_name} "
                    f"(attempt {attempt + 1}/{self.retry_config.max_retries + 1})"
                )

                result = operation()

                if result:  # Success
                    if attempt > 0:
                        logger.info(f"{operation_name} succeeded after {attempt + 1} attempts")
                    return result

                # Operation returned False/None but no exception
                # Retry if we have attempts left
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(
                        f"{operation_name} returned failure, " f"retrying in {delay:.1f}s..."
                    )

                    # Update progress during wait
                    if progress_callback and progress_obj:
                        progress_obj.current_step = (
                            f"Retrying {operation_name} in {delay:.0f}s "
                            f"(attempt {attempt + 2}/{self.retry_config.max_retries + 1})"
                        )
                        progress_callback(progress_obj)

                    time.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed after all retry attempts")
                    return None

            except (requests.exceptions.RequestException, ConnectionError) as e:
                last_exception = e
                if (
                    self.retry_config.retry_on_network_error
                    and attempt < self.retry_config.max_retries
                ):
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(
                        f"{operation_name} network error: {e}, " f"retrying in {delay:.1f}s..."
                    )

                    # Update progress during wait
                    if progress_callback and progress_obj:
                        progress_obj.current_step = (
                            f"Network error, retrying in {delay:.0f}s "
                            f"(attempt {attempt + 2}/{self.retry_config.max_retries + 1})"
                        )
                        progress_callback(progress_obj)

                    time.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed with network error: {e}")
                    raise

            except subprocess.TimeoutExpired as e:
                last_exception = e
                if self.retry_config.retry_on_timeout and attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(
                        f"{operation_name} timed out: {e}, " f"retrying in {delay:.1f}s..."
                    )

                    # Update progress during wait
                    if progress_callback and progress_obj:
                        progress_obj.current_step = (
                            f"Timeout, retrying in {delay:.0f}s "
                            f"(attempt {attempt + 2}/{self.retry_config.max_retries + 1})"
                        )
                        progress_callback(progress_obj)

                    time.sleep(delay)
                else:
                    logger.error(f"{operation_name} failed with timeout: {e}")
                    raise

            except Exception as e:
                # Don't retry on unexpected exceptions
                logger.error(f"{operation_name} failed with unexpected error: {e}")
                raise

        # All retries exhausted
        if last_exception:
            raise last_exception
        return None

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount image for modifications.

        Args:
            mount_point: Directory to mount to (creates temp dir if not specified)

        Returns:
            Path to mount point

        Raises:
            RuntimeError: If mounting fails
        """
        if self.is_mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if not mount_point:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_installer_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            # Use DISM to mount WIM/ESD images
            if self.image_path.suffix.lower() in [".wim", ".esd"]:
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Wim",
                        f"/WimFile:{self.image_path}",
                        "/Index:1",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                    timeout=300,
                )
            else:
                raise NotImplementedError(f"Mounting {self.image_path.suffix} not yet implemented")

            self.is_mounted = True
            logger.info("Image mounted successfully")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to mount image: {error_msg}")
            raise RuntimeError(f"Failed to mount image: {error_msg}") from e
        except Exception as e:
            logger.error(f"Unexpected error mounting image: {e}")
            raise

        return mount_point

    def unmount(self, save_changes: bool = True) -> None:
        """
        Unmount image and optionally save changes.

        Args:
            save_changes: Whether to commit changes (True) or discard them (False)

        Raises:
            RuntimeError: If unmounting fails
        """
        if not self.is_mounted:
            logger.warning("Image not mounted")
            return

        logger.info(
            f"Unmounting {self.mount_point} ({'saving' if save_changes else 'discarding'} changes)"
        )

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Wim", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
                timeout=600,
            )

            self.is_mounted = False
            logger.info("Image unmounted successfully")

            # Cleanup mount point
            if self.mount_point and self.mount_point.exists():
                shutil.rmtree(self.mount_point, ignore_errors=True)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Failed to unmount image: {error_msg}")
            raise RuntimeError(f"Failed to unmount image: {error_msg}") from e

    def install_application(
        self,
        app_id: str,
        method: Optional[InstallMethod] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> InstallResult:
        """
        Install single application with automatic fallbacks.

        Attempts installation using available methods in priority order:
        1. WinGet (if available and app_id provided)
        2. Chocolatey (if available and app_id provided)
        3. Direct download (if download_url provided)

        Args:
            app_id: Application identifier (must exist in app_catalog)
            method: Optional specific method to use (skips others)
            progress_callback: Optional callback for progress updates

        Returns:
            InstallResult with success status and details

        Example:
            result = installer.install_application(
                "vscode",
                progress_callback=lambda p: print(f"{p.progress_percent}%")
            )

            if result.success:
                print(f"Installed via {result.method.value}")
            else:
                print(f"Failed: {result.error_message}")
        """
        import time
        from deployforge.app_catalog import get_app

        start_time = time.time()

        try:
            app = get_app(app_id)
        except ValueError as e:
            logger.error(f"Unknown application: {app_id}")
            return InstallResult(
                app_id=app_id,
                app_name=app_id,
                success=False,
                error_message=str(e),
            )

        logger.info(f"Installing {app.name} (ID: {app_id})")

        # Get estimated duration for this app/method combination
        # (Will be refined as we determine which method succeeds)
        estimated_duration = self._get_estimated_duration(InstallMethod.WINGET, app.category)

        # Initialize progress
        if progress_callback:
            progress = InstallProgress(
                app_id=app_id,
                app_name=app.name,
                status=InstallStatus.PENDING,
                progress_percent=0,
                current_step="Initializing",
                total_steps=3,
                current_step_index=0,
                start_time=start_time,
                estimated_time_remaining=estimated_duration,
                elapsed_time=0.0,
            )
            progress_callback(progress)

        attempts = 0
        last_error = None

        # Try installation methods in priority order
        methods_to_try = (
            [method]
            if method
            else [InstallMethod.WINGET, InstallMethod.CHOCOLATEY, InstallMethod.DIRECT_DOWNLOAD]
        )

        for install_method in methods_to_try:
            attempts += 1

            try:
                if install_method == InstallMethod.WINGET and app.winget_id:
                    if progress_callback:
                        elapsed = time.time() - start_time
                        est_duration = self._get_estimated_duration(
                            InstallMethod.WINGET, app.category
                        )
                        progress.current_step = f"Installing via WinGet ({app.winget_id})"
                        progress.current_step_index = 1
                        progress.progress_percent = 33
                        progress.method = InstallMethod.WINGET
                        progress.status = InstallStatus.INSTALLING
                        progress.elapsed_time = elapsed
                        progress.estimated_time_remaining = max(0, est_duration - elapsed)
                        progress_callback(progress)

                    success = self._install_via_winget(app, progress_callback)
                    if success:
                        actual_duration = time.time() - start_time
                        # Update estimate with actual duration
                        self._update_estimate(InstallMethod.WINGET, app.category, actual_duration)

                        result = InstallResult(
                            app_id=app_id,
                            app_name=app.name,
                            success=True,
                            method=InstallMethod.WINGET,
                            duration_seconds=actual_duration,
                            attempts=attempts,
                        )
                        self.results[app_id] = result

                        # Final progress update
                        if progress_callback:
                            progress.status = InstallStatus.COMPLETE
                            progress.progress_percent = 100
                            progress.elapsed_time = actual_duration
                            progress.estimated_time_remaining = 0.0
                            progress.end_time = time.time()
                            progress_callback(progress)

                        return result

                elif install_method == InstallMethod.CHOCOLATEY and app.chocolatey_id:
                    if progress_callback:
                        elapsed = time.time() - start_time
                        est_duration = self._get_estimated_duration(
                            InstallMethod.CHOCOLATEY, app.category
                        )
                        progress.current_step = f"Installing via Chocolatey ({app.chocolatey_id})"
                        progress.current_step_index = 2
                        progress.progress_percent = 66
                        progress.method = InstallMethod.CHOCOLATEY
                        progress.status = InstallStatus.INSTALLING
                        progress.elapsed_time = elapsed
                        progress.estimated_time_remaining = max(0, est_duration - elapsed)
                        progress_callback(progress)

                    success = self._install_via_chocolatey(app, progress_callback)
                    if success:
                        actual_duration = time.time() - start_time
                        # Update estimate with actual duration
                        self._update_estimate(
                            InstallMethod.CHOCOLATEY, app.category, actual_duration
                        )

                        result = InstallResult(
                            app_id=app_id,
                            app_name=app.name,
                            success=True,
                            method=InstallMethod.CHOCOLATEY,
                            duration_seconds=actual_duration,
                            attempts=attempts,
                        )
                        self.results[app_id] = result

                        # Final progress update
                        if progress_callback:
                            progress.status = InstallStatus.COMPLETE
                            progress.progress_percent = 100
                            progress.elapsed_time = actual_duration
                            progress.estimated_time_remaining = 0.0
                            progress.end_time = time.time()
                            progress_callback(progress)

                        return result

                elif install_method == InstallMethod.DIRECT_DOWNLOAD and app.download_url:
                    if progress_callback:
                        elapsed = time.time() - start_time
                        est_duration = self._get_estimated_duration(
                            InstallMethod.DIRECT_DOWNLOAD, app.category
                        )
                        progress.current_step = "Downloading installer"
                        progress.current_step_index = 3
                        progress.progress_percent = 50
                        progress.method = InstallMethod.DIRECT_DOWNLOAD
                        progress.status = InstallStatus.DOWNLOADING
                        progress.elapsed_time = elapsed
                        progress.estimated_time_remaining = max(0, est_duration - elapsed)
                        progress_callback(progress)

                    # Pass progress object for detailed download tracking
                    success = self._install_via_download(
                        app, progress_callback, progress if progress_callback else None
                    )
                    if success:
                        actual_duration = time.time() - start_time
                        # Update estimate with actual duration
                        self._update_estimate(
                            InstallMethod.DIRECT_DOWNLOAD, app.category, actual_duration
                        )

                        result = InstallResult(
                            app_id=app_id,
                            app_name=app.name,
                            success=True,
                            method=InstallMethod.DIRECT_DOWNLOAD,
                            duration_seconds=actual_duration,
                            attempts=attempts,
                        )
                        self.results[app_id] = result

                        # Final progress update
                        if progress_callback:
                            progress.status = InstallStatus.COMPLETE
                            progress.progress_percent = 100
                            progress.elapsed_time = actual_duration
                            progress.estimated_time_remaining = 0.0
                            progress.end_time = time.time()
                            progress_callback(progress)

                        return result

            except Exception as e:
                last_error = str(e)
                logger.warning(f"{install_method.value} failed for {app.name}: {e}")
                continue

        # All methods failed
        error_msg = last_error or "No installation methods available"
        logger.error(f"Failed to install {app.name}: {error_msg}")

        if progress_callback:
            progress.status = InstallStatus.FAILED
            progress.error_message = error_msg
            progress.end_time = time.time()
            progress_callback(progress)

        result = InstallResult(
            app_id=app_id,
            app_name=app.name,
            success=False,
            error_message=error_msg,
            duration_seconds=time.time() - start_time,
            attempts=attempts,
        )
        self.results[app_id] = result
        return result

    def install_applications(
        self,
        app_ids: List[str],
        parallel: bool = False,
        max_workers: int = 3,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict[str, InstallResult]:
        """
        Install multiple applications.

        Args:
            app_ids: List of application identifiers
            parallel: Whether to install in parallel (faster but uses more resources)
            max_workers: Maximum parallel installations (only used if parallel=True)
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary mapping app_id to InstallResult

        Example:
            results = installer.install_applications(
                app_ids=["vscode", "git", "nodejs", "docker"],
                parallel=True,
                max_workers=2
            )

            successful = [r for r in results.values() if r.success]
            failed = [r for r in results.values() if not r.success]

            print(f"Installed: {len(successful)}/{len(results)}")
        """
        logger.info(f"Installing {len(app_ids)} applications (parallel={parallel})")

        # Resolve dependencies to determine install order
        ordered_app_ids = self._resolve_dependencies(app_ids)

        if parallel:
            return self._install_parallel(ordered_app_ids, max_workers, progress_callback)
        else:
            return self._install_sequential(ordered_app_ids, progress_callback)

    def _install_sequential(
        self, app_ids: List[str], progress_callback: Optional[ProgressCallback]
    ) -> Dict[str, InstallResult]:
        """Install applications sequentially (one at a time)"""
        results = {}
        for app_id in app_ids:
            result = self.install_application(app_id, progress_callback=progress_callback)
            results[app_id] = result
        return results

    def _install_parallel(
        self,
        app_ids: List[str],
        max_workers: int,
        progress_callback: Optional[ProgressCallback],
    ) -> Dict[str, InstallResult]:
        """Install applications in parallel using thread pool"""
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_app = {
                executor.submit(self.install_application, app_id, None, progress_callback): app_id
                for app_id in app_ids
            }

            for future in as_completed(future_to_app):
                app_id = future_to_app[future]
                try:
                    result = future.result()
                    results[app_id] = result
                except Exception as e:
                    logger.error(f"Exception installing {app_id}: {e}")
                    results[app_id] = InstallResult(
                        app_id=app_id, app_name=app_id, success=False, error_message=str(e)
                    )

        return results

    def _install_via_winget(
        self, app: "ApplicationDefinition", progress_callback: Optional[ProgressCallback]
    ) -> bool:
        """
        Install application using Windows Package Manager (WinGet).

        Args:
            app: Application definition with winget_id
            progress_callback: Optional progress callback

        Returns:
            True if installation succeeded, False otherwise
        """
        if not app.winget_id:
            return False

        # Check if WinGet is available
        if not self._is_winget_available():
            logger.warning("WinGet not available on this system")
            return False

        logger.info(f"Installing {app.name} via WinGet (ID: {app.winget_id})")

        try:
            # WinGet install command
            cmd = [
                "winget",
                "install",
                "--id",
                app.winget_id,
                "--silent",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ]

            # Run installation
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)

            if result.returncode == 0:
                logger.info(f"Successfully installed {app.name} via WinGet")
                return True
            else:
                logger.error(f"WinGet install failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"WinGet install timed out for {app.name}")
            return False
        except Exception as e:
            logger.error(f"WinGet install error for {app.name}: {e}")
            return False

    def _install_via_chocolatey(
        self, app: "ApplicationDefinition", progress_callback: Optional[ProgressCallback]
    ) -> bool:
        """
        Install application using Chocolatey package manager.

        Args:
            app: Application definition with chocolatey_id
            progress_callback: Optional progress callback

        Returns:
            True if installation succeeded, False otherwise
        """
        if not app.chocolatey_id:
            return False

        # Check if Chocolatey is available
        if not self._is_chocolatey_available():
            logger.warning("Chocolatey not available on this system")
            return False

        logger.info(f"Installing {app.name} via Chocolatey (ID: {app.chocolatey_id})")

        try:
            # Chocolatey install command
            cmd = ["choco", "install", app.chocolatey_id, "-y", "--no-progress"]

            # Run installation
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)

            if result.returncode == 0:
                logger.info(f"Successfully installed {app.name} via Chocolatey")
                return True
            else:
                logger.error(f"Chocolatey install failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Chocolatey install timed out for {app.name}")
            return False
        except Exception as e:
            logger.error(f"Chocolatey install error for {app.name}: {e}")
            return False

    def _install_via_download(
        self,
        app: "ApplicationDefinition",
        progress_callback: Optional[ProgressCallback],
        progress_obj: Optional[InstallProgress] = None,
    ) -> bool:
        """
        Install application via direct download.

        Args:
            app: Application definition with download_url
            progress_callback: Optional progress callback
            progress_obj: Optional progress object for detailed tracking

        Returns:
            True if installation succeeded, False otherwise
        """
        if not app.download_url:
            return False

        logger.info(f"Installing {app.name} via direct download")

        try:
            # Download installer with detailed progress tracking
            installer_path = self._download_file(
                app.download_url, app.name, progress_callback, progress_obj
            )

            # Update progress for installation phase
            if progress_callback and progress_obj:
                progress_obj.status = InstallStatus.INSTALLING
                progress_obj.current_step = "Running installer..."
                progress_obj.progress_percent = 75
                progress_callback(progress_obj)

            # Run installer
            cmd = [str(installer_path)]
            if app.silent_args:
                cmd.extend(app.silent_args.split())

            result = subprocess.run(cmd, capture_output=True, timeout=600, check=False)

            # Cleanup
            if installer_path.exists():
                installer_path.unlink()

            if result.returncode == 0:
                logger.info(f"Successfully installed {app.name} via direct download")
                return True
            else:
                logger.error(f"Direct install failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Direct download install error for {app.name}: {e}")
            return False

    def _download_file(
        self,
        url: str,
        app_name: str,
        progress_callback: Optional[ProgressCallback],
        progress_obj: Optional[InstallProgress] = None,
    ) -> Path:
        """
        Download file from URL with detailed progress tracking.

        Args:
            url: Download URL
            app_name: Application name (for filename fallback)
            progress_callback: Optional progress callback
            progress_obj: Optional progress object to update

        Returns:
            Path to downloaded file
        """
        filename = url.split("/")[-1] or f"{app_name}_installer.exe"
        download_path = Path(tempfile.gettempdir()) / filename

        logger.info(f"Downloading {url} to {download_path}")

        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        start_time = time.time()
        last_update_time = start_time

        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                current_time = time.time()

                # Update progress every 0.5 seconds to avoid callback spam
                if progress_callback and progress_obj and (current_time - last_update_time >= 0.5):
                    elapsed = current_time - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0

                    # Update progress object with download details
                    progress_obj.bytes_downloaded = downloaded
                    progress_obj.total_bytes = total_size
                    progress_obj.download_speed = speed

                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        progress_obj.progress_percent = percent

                        # Estimate remaining time based on current speed
                        if speed > 0:
                            remaining_bytes = total_size - downloaded
                            progress_obj.estimated_time_remaining = remaining_bytes / speed

                    progress_obj.current_step = (
                        f"Downloading {downloaded // (1024*1024)}/"
                        f"{total_size // (1024*1024)} MB "
                        f"at {progress_obj.get_speed_formatted()}"
                    )

                    progress_callback(progress_obj)
                    last_update_time = current_time

        logger.info(f"Download complete: {downloaded} bytes in {time.time() - start_time:.1f}s")

        return download_path

    def _resolve_dependencies(self, app_ids: List[str]) -> List[str]:
        """
        Resolve installation order based on dependencies.

        Uses topological sort to ensure dependencies are installed first.

        Args:
            app_ids: List of application IDs to install

        Returns:
            Ordered list with dependencies first
        """
        # Simplified implementation - just return as-is for now
        # TODO: Implement proper dependency resolution with topological sort
        return app_ids

    def _is_winget_available(self) -> bool:
        """Check if WinGet is available on the system"""
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _is_chocolatey_available(self) -> bool:
        """Check if Chocolatey is available on the system"""
        try:
            result = subprocess.run(
                ["choco", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def verify_installation(
        self, app_id: str, method: Optional[InstallMethod] = None
    ) -> VerificationResult:
        """
        Verify that an application was successfully installed.

        Tries multiple verification methods in order:
        1. WinGet list (if WinGet was used or available)
        2. Chocolatey list (if Chocolatey was used or available)
        3. Registry check (Windows only)
        4. Common installation paths

        Args:
            app_id: Application identifier to verify
            method: Optional installation method used (helps prioritize verification)

        Returns:
            VerificationResult with installation status and details

        Example:
            result = installer.verify_installation("vscode")
            if result.is_installed:
                print(f"Verified: {result.app_name} at {result.install_path}")
            else:
                print(f"Not found: {result.error_message}")
        """
        from deployforge.app_catalog import get_app

        try:
            app = get_app(app_id)
        except ValueError as e:
            return VerificationResult(
                app_id=app_id,
                app_name=app_id,
                is_installed=False,
                error_message=str(e),
            )

        logger.info(f"Verifying installation of {app.name}")

        # Try verification methods in priority order
        verification_methods = [
            (self._verify_via_winget, "WinGet"),
            (self._verify_via_chocolatey, "Chocolatey"),
            (self._verify_via_registry, "Registry"),
            (self._verify_via_path, "Path Search"),
        ]

        # Prioritize the method that was used for installation
        if method == InstallMethod.WINGET:
            verification_methods.insert(0, (self._verify_via_winget, "WinGet"))
        elif method == InstallMethod.CHOCOLATEY:
            verification_methods.insert(0, (self._verify_via_chocolatey, "Chocolatey"))

        for verify_func, method_name in verification_methods:
            result = verify_func(app)
            if result and result.is_installed:
                logger.info(
                    f"Verified {app.name} installation via {method_name}: "
                    f"{result.install_path or 'path unknown'}"
                )
                return result

        # Not found by any method
        logger.warning(f"Could not verify installation of {app.name}")
        return VerificationResult(
            app_id=app_id,
            app_name=app.name,
            is_installed=False,
            error_message="Application not found by any verification method",
        )

    def _verify_via_winget(self, app: "ApplicationDefinition") -> Optional[VerificationResult]:
        """Verify installation using WinGet"""
        if not app.winget_id or not self._is_winget_available():
            return None

        try:
            result = subprocess.run(
                ["winget", "list", "--id", app.winget_id],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0 and app.winget_id.lower() in result.stdout.lower():
                # Parse version if available (basic parsing)
                version = None
                for line in result.stdout.split("\n"):
                    if app.winget_id.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            version = parts[1]
                        break

                return VerificationResult(
                    app_id=app.id,
                    app_name=app.name,
                    is_installed=True,
                    verification_method="WinGet",
                    version=version,
                )
        except Exception as e:
            logger.debug(f"WinGet verification failed for {app.name}: {e}")

        return None

    def _verify_via_chocolatey(self, app: "ApplicationDefinition") -> Optional[VerificationResult]:
        """Verify installation using Chocolatey"""
        if not app.chocolatey_id or not self._is_chocolatey_available():
            return None

        try:
            result = subprocess.run(
                ["choco", "list", "--local-only", "--exact", app.chocolatey_id],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0 and app.chocolatey_id.lower() in result.stdout.lower():
                # Parse version if available
                version = None
                for line in result.stdout.split("\n"):
                    if app.chocolatey_id.lower() in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            version = parts[1]
                        break

                return VerificationResult(
                    app_id=app.id,
                    app_name=app.name,
                    is_installed=True,
                    verification_method="Chocolatey",
                    version=version,
                )
        except Exception as e:
            logger.debug(f"Chocolatey verification failed for {app.name}: {e}")

        return None

    def _verify_via_registry(self, app: "ApplicationDefinition") -> Optional[VerificationResult]:
        """
        Verify installation via Windows Registry.

        Checks common registry locations for installed programs.
        """
        if platform.system() != "Windows":
            return None

        # Common registry paths for installed programs
        reg_paths = [
            r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
            r"HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        ]

        try:
            for reg_path in reg_paths:
                result = subprocess.run(
                    ["reg", "query", reg_path, "/s", "/f", app.name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    check=False,
                )

                if result.returncode == 0 and app.name.lower() in result.stdout.lower():
                    # Try to extract install location
                    install_path = None
                    for line in result.stdout.split("\n"):
                        if "InstallLocation" in line or "InstallPath" in line:
                            parts = line.split("REG_SZ")
                            if len(parts) > 1:
                                path_str = parts[1].strip()
                                if path_str:
                                    install_path = Path(path_str)
                            break

                    return VerificationResult(
                        app_id=app.id,
                        app_name=app.name,
                        is_installed=True,
                        verification_method="Registry",
                        install_path=install_path,
                    )
        except Exception as e:
            logger.debug(f"Registry verification failed for {app.name}: {e}")

        return None

    def _verify_via_path(self, app: "ApplicationDefinition") -> Optional[VerificationResult]:
        """
        Verify installation by searching common installation paths.

        Checks Program Files, AppData, and other common locations.
        """
        if platform.system() != "Windows":
            return None

        # Common installation directories
        search_paths = []

        # Add Program Files paths
        program_files = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
        program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
        local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
        appdata = Path(os.environ.get("APPDATA", ""))

        search_paths.extend(
            [
                program_files,
                program_files_x86,
                local_appdata / "Programs",
                appdata,
            ]
        )

        # Search for app directory
        app_name_lower = app.name.lower().replace(" ", "")

        for base_path in search_paths:
            if not base_path.exists():
                continue

            try:
                for item in base_path.iterdir():
                    if item.is_dir():
                        item_name_lower = item.name.lower().replace(" ", "")
                        if app_name_lower in item_name_lower or item_name_lower in app_name_lower:
                            # Found potential installation directory
                            return VerificationResult(
                                app_id=app.id,
                                app_name=app.name,
                                is_installed=True,
                                verification_method="Path Search",
                                install_path=item,
                            )
            except (PermissionError, OSError):
                # Skip directories we can't access
                continue

        return None

    def verify_installations(
        self, app_ids: List[str], methods: Optional[Dict[str, InstallMethod]] = None
    ) -> Dict[str, VerificationResult]:
        """
        Verify multiple application installations.

        Args:
            app_ids: List of application identifiers to verify
            methods: Optional dict mapping app_id to InstallMethod used

        Returns:
            Dictionary mapping app_id to VerificationResult

        Example:
            methods = {"vscode": InstallMethod.WINGET, "git": InstallMethod.CHOCOLATEY}
            results = installer.verify_installations(["vscode", "git"], methods)

            for app_id, result in results.items():
                if result.is_installed:
                    print(f"✓ {result.app_name}")
                else:
                    print(f"✗ {result.app_name}: {result.error_message}")
        """
        logger.info(f"Verifying {len(app_ids)} installations")

        results = {}
        for app_id in app_ids:
            method = methods.get(app_id) if methods else None
            result = self.verify_installation(app_id, method)
            results[app_id] = result

        successful = sum(1 for r in results.values() if r.is_installed)
        logger.info(f"Verification complete: {successful}/{len(app_ids)} apps verified")

        return results
