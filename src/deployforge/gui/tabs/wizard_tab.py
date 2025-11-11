"""Setup Wizard Tab for GUI"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget,
    QPushButton, QLabel, QTextEdit
)
from deployforge.wizard import SetupPreset


class WizardTab(QWidget):
    """Tab for setup wizard presets"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Setup Wizard Presets"))

        self.preset_list = QListWidget()
        for preset in SetupPreset:
            self.preset_list.addItem(preset.value.replace('_', ' ').title())

        layout.addWidget(self.preset_list)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        layout.addWidget(QLabel("Preset Details:"))
        layout.addWidget(self.details_text)

        self.generate_btn = QPushButton("Generate Setup Wizard")
        layout.addWidget(self.generate_btn)
