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
        self.setup_ui()

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
