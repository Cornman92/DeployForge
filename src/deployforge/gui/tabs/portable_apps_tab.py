"""Portable Apps Tab for GUI"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget,
    QComboBox, QPushButton, QLabel
)
from deployforge.portable import PortableProfile


class PortableAppsTab(QWidget):
    """Tab for portable apps management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Portable Apps Profile:"))

        self.profile_combo = QComboBox()
        for profile in PortableProfile:
            self.profile_combo.addItem(profile.value.title(), profile)

        layout.addWidget(self.profile_combo)

        layout.addWidget(QLabel("Available Apps:"))

        self.apps_list = QListWidget()
        self.apps_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.apps_list)

        self.install_btn = QPushButton("Install Selected Apps")
        layout.addWidget(self.install_btn)
