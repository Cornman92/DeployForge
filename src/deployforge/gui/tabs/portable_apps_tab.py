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
        self.parent = parent
        self.setup_ui()
        self.load_apps()
        self.connect_signals()

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

    def load_apps(self):
        """Load available portable apps into list"""
        from deployforge.portable import APP_CATALOG

        self.apps_list.clear()
        for app_id, app_info in APP_CATALOG.items():
            item_text = f"{app_info.name} ({app_info.size_mb}MB)"
            self.apps_list.addItem(item_text)

    def connect_signals(self):
        """Connect signals to slots"""
        self.install_btn.clicked.connect(self.install_apps)

    def get_selected_apps(self):
        """Get list of selected app IDs"""
        from deployforge.portable import APP_CATALOG

        selected_items = self.apps_list.selectedItems()
        app_ids = []
        app_list = list(APP_CATALOG.keys())

        for item in selected_items:
            row = self.apps_list.row(item)
            if row < len(app_list):
                app_ids.append(app_list[row])

        return app_ids

    def install_apps(self):
        """Install portable apps using backend integration"""
        from PyQt6.QtWidgets import QMessageBox

        # Get current image
        image_path = self.parent.get_current_image()
        if not image_path:
            QMessageBox.warning(self, "No Image", "Please open an image first")
            return

        # Get selected profile or custom apps
        profile = self.profile_combo.currentData()
        custom_apps = self.get_selected_apps()

        # Start backend operation
        self.parent.backend_integration.install_portable_apps(
            image_path=image_path,
            profile=profile if not custom_apps else None,
            custom_apps=custom_apps if custom_apps else None,
            progress_callback=self.parent.on_operation_progress,
            finished_callback=self.parent.on_operation_finished,
            error_callback=self.parent.on_operation_error
        )

        if custom_apps:
            self.parent.log(f"Installing {len(custom_apps)} custom portable apps...")
        else:
            self.parent.log(f"Installing {profile.value} portable apps profile...")
