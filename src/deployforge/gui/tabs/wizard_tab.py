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
        self.parent = parent
        self.setup_ui()
        self.connect_signals()

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

    def connect_signals(self):
        """Connect signals to slots"""
        self.preset_list.currentRowChanged.connect(self.update_preset_details)
        self.generate_btn.clicked.connect(self.generate_wizard)

    def update_preset_details(self, row):
        """Update preset details when selection changes"""
        if row < 0:
            return

        from deployforge.wizard import SetupWizard
        presets = list(SetupPreset)
        if row < len(presets):
            preset = presets[row]
            wizard = SetupWizard()
            config = wizard.get_preset(preset)

            details = f"""
Preset: {config.preset_name}
Description: {config.description}

Essential Apps: {', '.join(config.essential_apps)}
Recommended Apps: {', '.join(config.recommended_apps)}

Hardware Requirements:
- Minimum RAM: {config.min_ram_gb}GB
- Recommended RAM: {config.recommended_ram_gb}GB
- Minimum Storage: {config.min_storage_gb}GB
- Recommended Storage: {config.recommended_storage_gb}GB
            """.strip()

            self.details_text.setPlainText(details)

    def generate_wizard(self):
        """Generate setup wizard using backend integration"""
        from PyQt6.QtWidgets import QMessageBox, QFileDialog
        from pathlib import Path

        # Get selected preset
        selected_row = self.preset_list.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Preset", "Please select a preset first")
            return

        presets = list(SetupPreset)
        preset = presets[selected_row]

        # Ask for output path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Setup Wizard Configuration",
            f"{preset.value}_setup.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        output_path = Path(file_path)

        # Start backend operation
        self.parent.backend_integration.generate_wizard(
            preset=preset,
            output_path=output_path,
            progress_callback=self.parent.on_operation_progress,
            finished_callback=self.parent.on_operation_finished,
            error_callback=self.parent.on_operation_error
        )

        self.parent.log(f"Generating {preset.value} wizard to {output_path.name}...")
