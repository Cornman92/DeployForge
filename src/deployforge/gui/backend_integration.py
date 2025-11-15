"""
GUI Integration Module - Connects Backend Modules to GUI

Provides centralized connection between all enhanced backend modules
(modules 6-9) and the GUI interface with progress tracking and error handling.
"""

import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal, QObject

# Import all enhanced modules
from deployforge.ui_customization import UICustomizer, UIProfile
from deployforge.backup import BackupIntegrator, BackupProfile
from deployforge.wizard import SetupWizard, SetupPreset
from deployforge.portable import PortableAppManager, PortableProfile

logger = logging.getLogger(__name__)


class ProgressSignals(QObject):
    """Qt signals for progress tracking"""
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(dict)  # Operation result
    error = pyqtSignal(str)  # Error message


class UICustomizationWorker(QThread):
    """Background worker for UI customization operations"""

    def __init__(self, image_path: Path, profile: UIProfile, config: Dict[str, Any] = None):
        super().__init__()
        self.image_path = image_path
        self.profile = profile
        self.config = config
        self.signals = ProgressSignals()

    def run(self):
        """Run UI customization in background"""
        try:
            self.signals.progress.emit("Starting UI customization...")

            customizer = UICustomizer(self.image_path)

            # Progress callback
            def progress_cb(msg: str):
                self.signals.progress.emit(msg)

            customizer.mount(progress_callback=progress_cb)

            if self.profile:
                self.signals.progress.emit(f"Applying {self.profile.value} profile...")
                customizer.apply_profile(self.profile, progress_callback=progress_cb)
            elif self.config:
                # Apply custom configuration
                for key, value in self.config.items():
                    setattr(customizer.config, key, value)
                customizer._apply_context_menu()
                customizer._apply_taskbar_settings()
                customizer._apply_explorer_settings()
                customizer._apply_theme_settings()

            customizer.unmount(save_changes=True, progress_callback=progress_cb)

            self.signals.progress.emit("UI customization complete!")
            self.signals.finished.emit({"success": True})

        except Exception as e:
            logger.error(f"UI customization failed: {e}")
            self.signals.error.emit(str(e))


class BackupConfigWorker(QThread):
    """Background worker for backup configuration"""

    def __init__(self, image_path: Path, profile: BackupProfile, config: Dict[str, Any] = None):
        super().__init__()
        self.image_path = image_path
        self.profile = profile
        self.config = config
        self.signals = ProgressSignals()

    def run(self):
        """Run backup configuration in background"""
        try:
            self.signals.progress.emit("Starting backup configuration...")

            integrator = BackupIntegrator(self.image_path)

            def progress_cb(msg: str):
                self.signals.progress.emit(msg)

            integrator.mount(progress_callback=progress_cb)

            if self.profile:
                self.signals.progress.emit(f"Applying {self.profile.value} backup profile...")
                integrator.apply_profile(self.profile, progress_callback=progress_cb)
            elif self.config:
                for key, value in self.config.items():
                    setattr(integrator.config, key, value)
                if integrator.config.enable_system_restore:
                    integrator.configure_system_restore()
                if integrator.config.enable_vss:
                    integrator.configure_vss()
                if integrator.config.create_restore_point_on_boot:
                    integrator.create_restore_point_on_boot()
                if integrator.config.enable_recovery_environment:
                    integrator.configure_recovery_environment()

            integrator.unmount(save_changes=True, progress_callback=progress_cb)

            self.signals.progress.emit("Backup configuration complete!")
            self.signals.finished.emit({"success": True})

        except Exception as e:
            logger.error(f"Backup configuration failed: {e}")
            self.signals.error.emit(str(e))


class WizardGeneratorWorker(QThread):
    """Background worker for wizard generation"""

    def __init__(self, preset: SetupPreset, output_path: Path):
        super().__init__()
        self.preset = preset
        self.output_path = output_path
        self.signals = ProgressSignals()

    def run(self):
        """Generate wizard in background"""
        try:
            self.signals.progress.emit(f"Generating {self.preset.value} wizard...")

            wizard = SetupWizard()

            # Create guided setup
            wizard.create_guided_setup(
                presets=[self.preset.value],
                output_path=self.output_path
            )

            # Generate installation script
            script_path = self.output_path.parent / f"{self.preset.value}_install.ps1"
            wizard.generate_installation_script(self.preset, script_path)

            self.signals.progress.emit("Wizard generation complete!")
            self.signals.finished.emit({
                "success": True,
                "config_path": str(self.output_path),
                "script_path": str(script_path)
            })

        except Exception as e:
            logger.error(f"Wizard generation failed: {e}")
            self.signals.error.emit(str(e))


class PortableAppsWorker(QThread):
    """Background worker for portable apps installation"""

    def __init__(self, image_path: Path, profile: PortableProfile, custom_apps: list = None):
        super().__init__()
        self.image_path = image_path
        self.profile = profile
        self.custom_apps = custom_apps
        self.signals = ProgressSignals()

    def run(self):
        """Install portable apps in background"""
        try:
            self.signals.progress.emit("Starting portable apps installation...")

            manager = PortableAppManager(self.image_path)

            def progress_cb(msg: str):
                self.signals.progress.emit(msg)

            manager.mount(progress_callback=progress_cb)

            if self.custom_apps:
                manager.config.selected_apps = self.custom_apps
                manager.install_selected_apps(progress_callback=progress_cb)
            elif self.profile:
                self.signals.progress.emit(f"Applying {self.profile.value} profile...")
                manager.apply_profile(self.profile, progress_callback=progress_cb)

            manager.create_launcher_script()
            manager.unmount(save_changes=True, progress_callback=progress_cb)

            self.signals.progress.emit("Portable apps installation complete!")
            self.signals.finished.emit({
                "success": True,
                "apps_installed": len(manager.config.selected_apps)
            })

        except Exception as e:
            logger.error(f"Portable apps installation failed: {e}")
            self.signals.error.emit(str(e))


class BackendIntegration:
    """Central integration point for all backend operations"""

    def __init__(self):
        self.active_workers = []

    def customize_ui(
        self,
        image_path: Path,
        profile: Optional[UIProfile] = None,
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        finished_callback: Optional[Callable[[dict], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Start UI customization operation

        Args:
            image_path: Path to Windows image
            profile: UI profile to apply (or None for custom config)
            config: Custom configuration dict
            progress_callback: Callback for progress updates
            finished_callback: Callback when operation completes
            error_callback: Callback for errors
        """
        worker = UICustomizationWorker(image_path, profile, config)

        if progress_callback:
            worker.signals.progress.connect(progress_callback)
        if finished_callback:
            worker.signals.finished.connect(finished_callback)
        if error_callback:
            worker.signals.error.connect(error_callback)

        self.active_workers.append(worker)
        worker.start()
        return worker

    def configure_backup(
        self,
        image_path: Path,
        profile: Optional[BackupProfile] = None,
        config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        finished_callback: Optional[Callable[[dict], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """Start backup configuration operation"""
        worker = BackupConfigWorker(image_path, profile, config)

        if progress_callback:
            worker.signals.progress.connect(progress_callback)
        if finished_callback:
            worker.signals.finished.connect(finished_callback)
        if error_callback:
            worker.signals.error.connect(error_callback)

        self.active_workers.append(worker)
        worker.start()
        return worker

    def generate_wizard(
        self,
        preset: SetupPreset,
        output_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None,
        finished_callback: Optional[Callable[[dict], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """Start wizard generation operation"""
        worker = WizardGeneratorWorker(preset, output_path)

        if progress_callback:
            worker.signals.progress.connect(progress_callback)
        if finished_callback:
            worker.signals.finished.connect(finished_callback)
        if error_callback:
            worker.signals.error.connect(error_callback)

        self.active_workers.append(worker)
        worker.start()
        return worker

    def install_portable_apps(
        self,
        image_path: Path,
        profile: Optional[PortableProfile] = None,
        custom_apps: Optional[list] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
        finished_callback: Optional[Callable[[dict], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None
    ):
        """Start portable apps installation operation"""
        worker = PortableAppsWorker(image_path, profile, custom_apps)

        if progress_callback:
            worker.signals.progress.connect(progress_callback)
        if finished_callback:
            worker.signals.finished.connect(finished_callback)
        if error_callback:
            worker.signals.error.connect(error_callback)

        self.active_workers.append(worker)
        worker.start()
        return worker

    def cleanup(self):
        """Clean up all workers"""
        for worker in self.active_workers:
            if worker.isRunning():
                worker.quit()
                worker.wait()
        self.active_workers.clear()
