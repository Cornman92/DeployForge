"""Main window for DeployForge GUI."""

import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QListWidget, QLabel, QFileDialog, QMessageBox,
        QTabWidget, QTextEdit, QProgressBar, QMenuBar, QMenu, QToolBar
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QAction, QIcon
    PYQT_AVAILABLE = True

    # Import enhanced module tabs
    from deployforge.gui.tabs.ui_customization_tab import UICustomizationTab
    from deployforge.gui.tabs.backup_tab import BackupTab
    from deployforge.gui.tabs.wizard_tab import WizardTab
    from deployforge.gui.tabs.portable_apps_tab import PortableAppsTab
    from deployforge.gui.backend_integration import BackendIntegration

except ImportError:
    PYQT_AVAILABLE = False


if PYQT_AVAILABLE:
    class ImageOperationWorker(QThread):
        """Worker thread for image operations."""

        progress = pyqtSignal(int)
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)

        def __init__(self, operation, *args, **kwargs):
            super().__init__()
            self.operation = operation
            self.args = args
            self.kwargs = kwargs

        def run(self):
            """Run the operation in background."""
            try:
                result = self.operation(*self.args, **self.kwargs)
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(str(e))


    class DeployForgeMainWindow(QMainWindow):
        """Main application window."""

        def __init__(self):
            super().__init__()
            self.current_image = None
            self.backend_integration = BackendIntegration()
            self.init_ui()

        def init_ui(self):
            """Initialize the user interface."""
            self.setWindowTitle("DeployForge - Windows Deployment Suite")
            self.setGeometry(100, 100, 1200, 800)

            # Create menu bar
            self.create_menu_bar()

            # Create toolbar
            self.create_toolbar()

            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Main layout
            main_layout = QVBoxLayout()
            central_widget.setLayout(main_layout)

            # Top section: Image info
            image_info_layout = QHBoxLayout()

            self.image_path_label = QLabel("No image loaded")
            image_info_layout.addWidget(self.image_path_label)

            self.open_image_btn = QPushButton("Open Image")
            self.open_image_btn.clicked.connect(self.open_image)
            image_info_layout.addWidget(self.open_image_btn)

            main_layout.addLayout(image_info_layout)

            # Tab widget for different operations
            self.tabs = QTabWidget()

            # Files tab
            self.files_tab = self.create_files_tab()
            self.tabs.addTab(self.files_tab, "Files")

            # Registry tab
            self.registry_tab = self.create_registry_tab()
            self.tabs.addTab(self.registry_tab, "Registry")

            # Drivers tab
            self.drivers_tab = self.create_drivers_tab()
            self.tabs.addTab(self.drivers_tab, "Drivers")

            # Templates tab
            self.templates_tab = self.create_templates_tab()
            self.tabs.addTab(self.templates_tab, "Templates")

            # Batch tab
            self.batch_tab = self.create_batch_tab()
            self.tabs.addTab(self.batch_tab, "Batch Operations")

            # Enhanced module tabs
            self.ui_customization_tab = UICustomizationTab(self)
            self.tabs.addTab(self.ui_customization_tab, "UI Customization")

            self.backup_tab = BackupTab(self)
            self.tabs.addTab(self.backup_tab, "Backup & Recovery")

            self.wizard_tab = WizardTab(self)
            self.tabs.addTab(self.wizard_tab, "Setup Wizard")

            self.portable_apps_tab = PortableAppsTab(self)
            self.tabs.addTab(self.portable_apps_tab, "Portable Apps")

            main_layout.addWidget(self.tabs)

            # Progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            main_layout.addWidget(self.progress_bar)

            # Log output
            self.log_output = QTextEdit()
            self.log_output.setReadOnly(True)
            self.log_output.setMaximumHeight(150)
            main_layout.addWidget(QLabel("Log Output:"))
            main_layout.addWidget(self.log_output)

        def create_menu_bar(self):
            """Create menu bar."""
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("File")

            open_action = QAction("Open Image", self)
            open_action.triggered.connect(self.open_image)
            file_menu.addAction(open_action)

            file_menu.addSeparator()

            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # Tools menu
            tools_menu = menubar.addMenu("Tools")

            compare_action = QAction("Compare Images", self)
            compare_action.triggered.connect(self.compare_images)
            tools_menu.addAction(compare_action)

            # Help menu
            help_menu = menubar.addMenu("Help")

            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

        def create_toolbar(self):
            """Create toolbar."""
            toolbar = QToolBar("Main Toolbar")
            self.addToolBar(toolbar)

            open_action = QAction("Open", self)
            open_action.triggered.connect(self.open_image)
            toolbar.addAction(open_action)

            toolbar.addSeparator()

            mount_action = QAction("Mount", self)
            mount_action.triggered.connect(self.mount_image)
            toolbar.addAction(mount_action)

            unmount_action = QAction("Unmount", self)
            unmount_action.triggered.connect(self.unmount_image)
            toolbar.addAction(unmount_action)

        def create_files_tab(self):
            """Create files management tab."""
            widget = QWidget()
            layout = QVBoxLayout()

            # File list
            self.file_list = QListWidget()
            layout.addWidget(QLabel("Files in Image:"))
            layout.addWidget(self.file_list)

            # Buttons
            btn_layout = QHBoxLayout()

            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.refresh_file_list)
            btn_layout.addWidget(refresh_btn)

            add_btn = QPushButton("Add File")
            add_btn.clicked.connect(self.add_file_to_image)
            btn_layout.addWidget(add_btn)

            remove_btn = QPushButton("Remove File")
            remove_btn.clicked.connect(self.remove_file_from_image)
            btn_layout.addWidget(remove_btn)

            extract_btn = QPushButton("Extract File")
            extract_btn.clicked.connect(self.extract_file_from_image)
            btn_layout.addWidget(extract_btn)

            layout.addLayout(btn_layout)

            widget.setLayout(layout)
            return widget

        def create_registry_tab(self):
            """Create registry editing tab."""
            widget = QWidget()
            layout = QVBoxLayout()

            label = QLabel("Registry editing functionality")
            layout.addWidget(label)

            # TODO: Add registry editing controls

            widget.setLayout(layout)
            return widget

        def create_drivers_tab(self):
            """Create driver injection tab."""
            widget = QWidget()
            layout = QVBoxLayout()

            label = QLabel("Driver injection functionality")
            layout.addWidget(label)

            inject_btn = QPushButton("Inject Drivers")
            inject_btn.clicked.connect(self.inject_drivers)
            layout.addWidget(inject_btn)

            widget.setLayout(layout)
            return widget

        def create_templates_tab(self):
            """Create templates tab."""
            widget = QWidget()
            layout = QVBoxLayout()

            label = QLabel("Template management")
            layout.addWidget(label)

            # Template list
            self.template_list = QListWidget()
            layout.addWidget(self.template_list)

            # Buttons
            btn_layout = QHBoxLayout()

            load_btn = QPushButton("Load Template")
            btn_layout.addWidget(load_btn)

            apply_btn = QPushButton("Apply Template")
            btn_layout.addWidget(apply_btn)

            layout.addLayout(btn_layout)

            widget.setLayout(layout)
            return widget

        def create_batch_tab(self):
            """Create batch operations tab."""
            widget = QWidget()
            layout = QVBoxLayout()

            label = QLabel("Batch operations on multiple images")
            layout.addWidget(label)

            # Image list for batch
            self.batch_image_list = QListWidget()
            layout.addWidget(self.batch_image_list)

            # Buttons
            btn_layout = QHBoxLayout()

            add_images_btn = QPushButton("Add Images")
            btn_layout.addWidget(add_images_btn)

            run_batch_btn = QPushButton("Run Batch Operation")
            btn_layout.addWidget(run_batch_btn)

            layout.addLayout(btn_layout)

            widget.setLayout(layout)
            return widget

        def open_image(self):
            """Open an image file."""
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Image File",
                "",
                "Image Files (*.iso *.wim *.esd *.ppkg *.vhd *.vhdx);;All Files (*)"
            )

            if file_path:
                self.current_image = Path(file_path)
                self.image_path_label.setText(f"Image: {self.current_image.name}")
                self.log(f"Opened image: {file_path}")
                self.refresh_file_list()

        def mount_image(self):
            """Mount the current image."""
            if not self.current_image:
                QMessageBox.warning(self, "Warning", "No image loaded")
                return

            self.log(f"Mounting {self.current_image.name}...")
            # TODO: Implement mounting

        def unmount_image(self):
            """Unmount the current image."""
            self.log("Unmounting image...")
            # TODO: Implement unmounting

        def refresh_file_list(self):
            """Refresh the file list."""
            if not self.current_image:
                return

            self.file_list.clear()
            self.log("Refreshing file list...")
            # TODO: Implement file listing

        def add_file_to_image(self):
            """Add a file to the image."""
            if not self.current_image:
                QMessageBox.warning(self, "Warning", "No image loaded")
                return

            file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Add")
            if file_path:
                self.log(f"Adding file: {file_path}")
                # TODO: Implement file addition

        def remove_file_from_image(self):
            """Remove selected file from image."""
            selected = self.file_list.currentItem()
            if not selected:
                QMessageBox.warning(self, "Warning", "No file selected")
                return

            self.log(f"Removing file: {selected.text()}")
            # TODO: Implement file removal

        def extract_file_from_image(self):
            """Extract selected file from image."""
            selected = self.file_list.currentItem()
            if not selected:
                QMessageBox.warning(self, "Warning", "No file selected")
                return

            save_path, _ = QFileDialog.getSaveFileName(self, "Save File As")
            if save_path:
                self.log(f"Extracting file to: {save_path}")
                # TODO: Implement file extraction

        def inject_drivers(self):
            """Inject drivers into image."""
            if not self.current_image:
                QMessageBox.warning(self, "Warning", "No image loaded")
                return

            dir_path = QFileDialog.getExistingDirectory(self, "Select Driver Directory")
            if dir_path:
                self.log(f"Injecting drivers from: {dir_path}")
                # TODO: Implement driver injection

        def compare_images(self):
            """Compare two images."""
            self.log("Image comparison feature")
            # TODO: Implement image comparison

        def show_about(self):
            """Show about dialog."""
            from deployforge import __version__

            QMessageBox.about(
                self,
                "About DeployForge",
                f"DeployForge v{__version__}\n\n"
                "Windows Deployment Suite\n"
                "Customize, personalize and optimize Windows images.\n\n"
                "Supported formats: ISO, WIM, ESD, PPKG, VHD, VHDX"
            )

        def log(self, message: str):
            """Add message to log output."""
            self.log_output.append(message)

        def get_current_image(self) -> Optional[Path]:
            """Get the currently loaded image path."""
            return self.current_image

        def on_operation_progress(self, message: str):
            """Handle progress updates from backend operations."""
            self.log(message)
            self.progress_bar.setVisible(True)

        def on_operation_finished(self, result: dict):
            """Handle completion of backend operations."""
            self.progress_bar.setVisible(False)
            if result.get('success'):
                self.log("Operation completed successfully!")
                QMessageBox.information(self, "Success", "Operation completed successfully!")
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.log(f"Operation failed: {error_msg}")
                QMessageBox.warning(self, "Operation Failed", error_msg)

        def on_operation_error(self, error_msg: str):
            """Handle errors from backend operations."""
            self.progress_bar.setVisible(False)
            self.log(f"Error: {error_msg}")
            QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")

        def closeEvent(self, event):
            """Handle window close event."""
            # Clean up backend integration workers
            self.backend_integration.cleanup()
            event.accept()


def run_gui():
    """Run the GUI application."""
    if not PYQT_AVAILABLE:
        print("PyQt6 is not installed. Install it with: pip install PyQt6")
        return

    app = QApplication(sys.argv)
    window = DeployForgeMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
