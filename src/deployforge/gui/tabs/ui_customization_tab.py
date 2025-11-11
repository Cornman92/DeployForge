"""UI Customization Tab for GUI

Provides interface for Windows UI customization with profiles and custom settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QCheckBox, QPushButton, QLabel
)
from deployforge.ui_customization import UIProfile, ThemeMode, TaskbarAlignment


class UICustomizationTab(QWidget):
    """Tab for UI customization features"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)

        # Profile Selection
        profile_group = QGroupBox("UI Profile")
        profile_layout = QVBoxLayout()

        self.profile_combo = QComboBox()
        for profile in UIProfile:
            self.profile_combo.addItem(profile.value.title(), profile)

        profile_layout.addWidget(QLabel("Select UI Profile:"))
        profile_layout.addWidget(self.profile_combo)
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # Theme Settings
        theme_group = QGroupBox("Theme & Appearance")
        theme_layout = QVBoxLayout()

        self.theme_combo = QComboBox()
        for theme in ThemeMode:
            self.theme_combo.addItem(theme.value.title(), theme)

        self.taskbar_combo = QComboBox()
        for alignment in TaskbarAlignment:
            self.taskbar_combo.addItem(alignment.value.title(), alignment)

        theme_layout.addWidget(QLabel("Theme Mode:"))
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(QLabel("Taskbar Alignment:"))
        theme_layout.addWidget(self.taskbar_combo)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Explorer Settings
        explorer_group = QGroupBox("File Explorer")
        explorer_layout = QVBoxLayout()

        self.show_extensions_cb = QCheckBox("Show file extensions")
        self.show_hidden_cb = QCheckBox("Show hidden files")
        self.win10_context_cb = QCheckBox("Windows 10 context menu")

        explorer_layout.addWidget(self.show_extensions_cb)
        explorer_layout.addWidget(self.show_hidden_cb)
        explorer_layout.addWidget(self.win10_context_cb)
        explorer_group.setLayout(explorer_layout)
        layout.addWidget(explorer_group)

        # Apply Button
        self.apply_btn = QPushButton("Apply UI Customization")
        layout.addWidget(self.apply_btn)

        layout.addStretch()

    def get_config(self):
        """Get current configuration from UI"""
        from deployforge.ui_customization import UICustomizationConfig

        config = UICustomizationConfig()
        config.theme_mode = self.theme_combo.currentData()
        config.taskbar_alignment = self.taskbar_combo.currentData()
        config.show_file_extensions = self.show_extensions_cb.isChecked()
        config.show_hidden_files = self.show_hidden_cb.isChecked()
        config.windows10_context_menu = self.win10_context_cb.isChecked()

        return config
