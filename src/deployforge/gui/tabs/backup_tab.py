"""Backup Configuration Tab for GUI"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox,
    QComboBox, QCheckBox, QPushButton, QLabel
)
from deployforge.backup import BackupProfile


class BackupTab(QWidget):
    """Tab for backup configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Profile Selection
        profile_group = QGroupBox("Backup Profile")
        profile_layout = QVBoxLayout()

        self.profile_combo = QComboBox()
        for profile in BackupProfile:
            self.profile_combo.addItem(profile.value.title(), profile)

        profile_layout.addWidget(QLabel("Select Backup Profile:"))
        profile_layout.addWidget(self.profile_combo)
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # Backup Options
        options_group = QGroupBox("Backup Options")
        options_layout = QVBoxLayout()

        self.system_restore_cb = QCheckBox("Enable System Restore")
        self.vss_cb = QCheckBox("Enable Volume Shadow Copy")
        self.file_history_cb = QCheckBox("Enable File History")
        self.recovery_cb = QCheckBox("Configure Recovery Environment")

        options_layout.addWidget(self.system_restore_cb)
        options_layout.addWidget(self.vss_cb)
        options_layout.addWidget(self.file_history_cb)
        options_layout.addWidget(self.recovery_cb)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Apply Button
        self.apply_btn = QPushButton("Apply Backup Configuration")
        layout.addWidget(self.apply_btn)

        layout.addStretch()

    def connect_signals(self):
        """Connect signals to slots"""
        self.apply_btn.clicked.connect(self.apply_backup)

    def get_config(self):
        """Get current configuration from UI"""
        from deployforge.backup import BackupConfig

        config = BackupConfig()
        config.enable_system_restore = self.system_restore_cb.isChecked()
        config.enable_vss = self.vss_cb.isChecked()
        config.enable_file_history = self.file_history_cb.isChecked()
        config.enable_recovery_environment = self.recovery_cb.isChecked()

        return config

    def apply_backup(self):
        """Apply backup configuration using backend integration"""
        from PyQt6.QtWidgets import QMessageBox

        # Get current image
        image_path = self.parent.get_current_image()
        if not image_path:
            QMessageBox.warning(self, "No Image", "Please open an image first")
            return

        # Get selected profile or custom config
        profile = self.profile_combo.currentData()
        config_dict = self.get_config().to_dict()

        # Start backend operation
        self.parent.backend_integration.configure_backup(
            image_path=image_path,
            profile=profile,
            config=config_dict,
            progress_callback=self.parent.on_operation_progress,
            finished_callback=self.parent.on_operation_finished,
            error_callback=self.parent.on_operation_error
        )

        self.parent.log(f"Starting backup configuration with {profile.value} profile...")
