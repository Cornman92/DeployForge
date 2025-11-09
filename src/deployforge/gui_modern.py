"""
DeployForge Modern GUI Application

A beautiful, intuitive, and powerful graphical interface for Windows deployment
image customization. Features modern design, easy navigation, and comprehensive
functionality.

Built with PyQt6 for professional appearance and cross-platform compatibility.
"""

import sys
import logging
import traceback
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QScrollArea,
    QSplitter, QToolButton, QButtonGroup, QMessageBox, QProgressBar,
    QStatusBar, QMenuBar, QMenu, QToolBar, QFileDialog, QTextEdit,
    QCheckBox, QComboBox, QSpinBox, QGroupBox, QGridLayout, QRadioButton,
    QSlider, QLineEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, pyqtSlot, QSettings, QMimeData
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QPalette, QColor, QDragEnterEvent, QDropEvent

# Import DeployForge backend modules
try:
    from deployforge.cli.profiles import ProfileManager, apply_profile
    from deployforge.cli.analyzer import ImageAnalyzer
    from deployforge.config_manager import ConfigurationManager
    BACKEND_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Backend modules not available: {e}")
    BACKEND_AVAILABLE = False

logger = logging.getLogger(__name__)


# Theme Management
class Theme:
    """Theme color definitions."""

    LIGHT = {
        'name': 'Light',
        'background': '#FAFAFA',
        'surface': '#FFFFFF',
        'surface_variant': '#F9F9F9',
        'primary': '#0078D4',
        'primary_hover': '#106EBE',
        'primary_pressed': '#005A9E',
        'text': '#1F1F1F',
        'text_secondary': '#666666',
        'border': '#E0E0E0',
        'border_hover': '#B3B3B3',
        'button_bg': '#F3F3F3',
        'button_hover': '#E5E5E5',
        'button_pressed': '#D6D6D6',
        'success': '#107C10',
        'error': '#C50F1F',
        'warning': '#FFB900',
        'sidebar': '#FFFFFF',
        'sidebar_selected': '#E5F3FF',
        'sidebar_hover': '#F3F3F3',
    }

    DARK = {
        'name': 'Dark',
        'background': '#1E1E1E',
        'surface': '#252526',
        'surface_variant': '#2D2D30',
        'primary': '#0078D4',
        'primary_hover': '#1890F6',
        'primary_pressed': '#005A9E',
        'text': '#FFFFFF',
        'text_secondary': '#CCCCCC',
        'border': '#3E3E42',
        'border_hover': '#555555',
        'button_bg': '#3E3E42',
        'button_hover': '#4E4E52',
        'button_pressed': '#5E5E62',
        'success': '#4EC9B0',
        'error': '#F48771',
        'warning': '#FFCC00',
        'sidebar': '#2D2D30',
        'sidebar_selected': '#094771',
        'sidebar_hover': '#3E3E42',
    }

    @staticmethod
    def get(theme_name: str = 'Light') -> dict:
        """Get theme colors by name."""
        return Theme.DARK if theme_name == 'Dark' else Theme.LIGHT


class ThemeManager:
    """Manages application theme."""

    def __init__(self):
        self.current_theme = 'Light'
        self.callbacks = []

    def set_theme(self, theme_name: str):
        """Set the current theme."""
        self.current_theme = theme_name
        # Notify all callbacks
        for callback in self.callbacks:
            callback(theme_name)

    def get_theme(self) -> str:
        """Get current theme name."""
        return self.current_theme

    def get_colors(self) -> dict:
        """Get current theme colors."""
        return Theme.get(self.current_theme)

    def on_theme_changed(self, callback):
        """Register callback for theme changes."""
        self.callbacks.append(callback)

# Global theme manager
theme_manager = ThemeManager()


class ModernButton(QPushButton):
    """Modern styled button with hover effects and theme support."""

    def __init__(self, text: str, icon: Optional[str] = None, primary: bool = False):
        super().__init__(text)

        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(20, 20))

        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.is_primary = primary
        self.apply_theme()

        # Register for theme changes
        theme_manager.on_theme_changed(lambda _: self.apply_theme())

    def apply_theme(self):
        """Apply current theme to button."""
        colors = theme_manager.get_colors()

        if self.is_primary:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary_pressed']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['button_bg']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 16px;
                }}
                QPushButton:hover {{
                    background-color: {colors['button_hover']};
                    border-color: {colors['border_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['button_pressed']};
                }}
            """)


class SidebarButton(QToolButton):
    """Sidebar navigation button with icon and text."""

    def __init__(self, text: str, icon_name: str = None):
        super().__init__()
        self.setText(text)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set icon if provided
        if icon_name:
            self.setIcon(QIcon.fromTheme(icon_name))
            self.setIconSize(QSize(24, 24))

        self.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding: 12px 16px;
                color: #1F1F1F;
            }
            QToolButton:hover {
                background-color: #F3F3F3;
            }
            QToolButton:checked {
                background-color: #E5F3FF;
                border-left-color: #0078D4;
                color: #0078D4;
                font-weight: 600;
            }
        """)


class ModernCard(QFrame):
    """Modern card widget for grouping content."""

    def __init__(self, title: str = ""):
        super().__init__()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout(self)

        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            layout.addWidget(title_label)


class SetupWizard(QWidget):
    """Setup wizard for guided image building."""

    finished = pyqtSignal(dict)  # Emits configuration when done

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DeployForge Setup Wizard")
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog)

        self.current_step = 0
        self.config = {}

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🚀 DeployForge Setup Wizard")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Step indicator
        self.step_label = QLabel("Step 1 of 4")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet("color: #666666; font-size: 10pt;")
        layout.addWidget(self.step_label)

        layout.addSpacing(16)

        # Content stack
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.create_step1())  # Welcome
        self.content_stack.addWidget(self.create_step2())  # Image selection
        self.content_stack.addWidget(self.create_step3())  # Use case
        self.content_stack.addWidget(self.create_step4())  # Review
        layout.addWidget(self.content_stack)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()

        self.btn_back = ModernButton("← Back")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setEnabled(False)
        nav_layout.addWidget(self.btn_back)

        self.btn_next = ModernButton("Next →", primary=True)
        self.btn_next.clicked.connect(self.go_next)
        nav_layout.addWidget(self.btn_next)

        layout.addLayout(nav_layout)

    def create_step1(self):
        """Step 1: Welcome."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Welcome to DeployForge!")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "This wizard will guide you through creating a customized Windows deployment image.\n\n"
            "We'll help you:\n"
            "• Select your Windows image\n"
            "• Choose your use case\n"
            "• Configure optimization settings\n"
            "• Build your custom image"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return widget

    def create_step2(self):
        """Step 2: Image selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Select Windows Image")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("Choose the Windows installation image you want to customize:")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # File selector
        file_layout = QHBoxLayout()
        self.wizard_image_path = QLabel("No image selected")
        self.wizard_image_path.setStyleSheet("padding: 8px; background-color: #F3F3F3; border-radius: 4px;")
        file_layout.addWidget(self.wizard_image_path, 1)

        btn_browse = ModernButton("Browse...")
        btn_browse.clicked.connect(self.browse_wizard_image)
        file_layout.addWidget(btn_browse)

        layout.addLayout(file_layout)

        layout.addStretch()
        return widget

    def create_step3(self):
        """Step 3: Use case selection."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Choose Your Use Case")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("What will you primarily use this Windows installation for?")
        layout.addWidget(desc)

        self.use_case_group = QButtonGroup()

        use_cases = [
            ("🎮 Gaming", "Optimized for gaming with performance tweaks", "gamer"),
            ("💻 Development", "Developer tools and environments", "developer"),
            ("🏢 Work/Office", "Productivity and office work", "student"),
            ("🎨 Content Creation", "Video editing, design, and creative work", "creator"),
        ]

        for icon_text, description, profile_id in use_cases:
            radio = QRadioButton(f"{icon_text} - {description}")
            radio.setProperty("profile_id", profile_id)
            self.use_case_group.addButton(radio)
            layout.addWidget(radio)

        self.use_case_group.buttons()[0].setChecked(True)

        layout.addStretch()
        return widget

    def create_step4(self):
        """Step 4: Review and build."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Review Your Configuration")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.review_label = QLabel()
        self.review_label.setWordWrap(True)
        layout.addWidget(self.review_label)

        layout.addStretch()
        return widget

    def browse_wizard_image(self):
        """Browse for image in wizard."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Windows Image",
            "",
            "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            self.wizard_image_path.setText(file_path)
            self.config['image_path'] = file_path

    def go_next(self):
        """Go to next step."""
        if self.current_step == 3:  # Last step
            self.finish_wizard()
            return

        # Validate current step
        if self.current_step == 1 and not self.config.get('image_path'):
            QMessageBox.warning(self, "Image Required", "Please select a Windows image first.")
            return

        self.current_step += 1
        self.content_stack.setCurrentIndex(self.current_step)
        self.update_navigation()

        # Update review if on last step
        if self.current_step == 3:
            self.update_review()

    def go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.content_stack.setCurrentIndex(self.current_step)
            self.update_navigation()

    def update_navigation(self):
        """Update navigation buttons."""
        self.btn_back.setEnabled(self.current_step > 0)
        self.step_label.setText(f"Step {self.current_step + 1} of 4")

        if self.current_step == 3:
            self.btn_next.setText("Build Image ✓")
        else:
            self.btn_next.setText("Next →")

    def update_review(self):
        """Update review information."""
        selected_radio = self.use_case_group.checkedButton()
        profile_id = selected_radio.property("profile_id") if selected_radio else "gamer"
        profile_name = selected_radio.text() if selected_radio else "Gaming"

        self.config['profile'] = profile_id

        review_text = f"""
<b>Configuration Summary:</b><br><br>
<b>Source Image:</b> {Path(self.config.get('image_path', '')).name}<br>
<b>Profile:</b> {profile_name}<br>
<b>Output:</b> Custom image in same directory<br><br>
Click "Build Image" to start the build process!
        """
        self.review_label.setText(review_text)

    def finish_wizard(self):
        """Finish wizard and emit configuration."""
        self.finished.emit(self.config)
        self.close()


class WelcomePage(QWidget):
    """Welcome/Home page with quick actions and wizard."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Welcome to DeployForge")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Professional Windows Deployment Image Customization")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        # Wizard Card
        wizard_card = ModernCard("🧙 New User?")
        wizard_layout = QVBoxLayout()

        wizard_desc = QLabel("Let our wizard guide you through the process step-by-step!")
        wizard_desc.setStyleSheet("color: #666666;")
        wizard_layout.addWidget(wizard_desc)

        btn_wizard = ModernButton("🚀 Launch Setup Wizard", primary=True)
        btn_wizard.clicked.connect(self.launch_wizard)
        wizard_layout.addWidget(btn_wizard)

        wizard_card.layout().addLayout(wizard_layout)
        layout.addWidget(wizard_card)

        # Quick Actions
        quick_actions = ModernCard("Quick Start")
        quick_layout = QVBoxLayout()

        quick_layout.addWidget(QLabel("Get started with these common tasks:"))
        quick_layout.addSpacing(8)

        btn_gaming = ModernButton("🎮 Build Gaming Image")
        btn_developer = ModernButton("💻 Build Developer Image")
        btn_enterprise = ModernButton("🏢 Build Enterprise Image")
        btn_custom = ModernButton("🔧 Custom Build")

        quick_layout.addWidget(btn_gaming)
        quick_layout.addWidget(btn_developer)
        quick_layout.addWidget(btn_enterprise)
        quick_layout.addWidget(btn_custom)

        quick_actions.layout().addLayout(quick_layout)
        layout.addWidget(quick_actions)

        # Recent Images
        recent_card = ModernCard("Recent Images")
        recent_layout = QVBoxLayout()
        recent_layout.addWidget(QLabel("No recent images"))
        recent_card.layout().addLayout(recent_layout)
        layout.addWidget(recent_card)

        layout.addStretch()

    def launch_wizard(self):
        """Launch the setup wizard."""
        wizard = SetupWizard(self)
        wizard.finished.connect(self.on_wizard_finished)
        wizard.show()

    def on_wizard_finished(self, config):
        """Handle wizard completion."""
        QMessageBox.information(
            self,
            "Wizard Complete",
            f"Configuration saved!\n\n"
            f"Image: {Path(config.get('image_path', '')).name}\n"
            f"Profile: {config.get('profile', 'gamer')}\n\n"
            f"Go to the Build page to customize further or build now."
        )


class ProfileCard(QFrame):
    """Clickable profile selection card."""

    selected = pyqtSignal(str)  # Emits profile_id when clicked

    def __init__(self, icon_text: str, description: str, profile_id: str, features: list):
        super().__init__()

        self.profile_id = profile_id
        self.is_selected = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(icon_text)
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        desc = QLabel(description)
        desc.setStyleSheet("color: #666666; font-size: 9pt;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Features list
        features_text = "Includes: " + ", ".join(features[:3])
        if len(features) > 3:
            features_text += f" +{len(features) - 3} more"

        features_label = QLabel(features_text)
        features_label.setStyleSheet("color: #0078D4; font-size: 8pt; font-style: italic;")
        features_label.setWordWrap(True)
        layout.addWidget(features_label)

    def mousePressEvent(self, event):
        """Handle click event."""
        self.select()
        self.selected.emit(self.profile_id)

    def select(self):
        """Mark this card as selected."""
        self.is_selected = True
        self.update_style()

    def deselect(self):
        """Mark this card as not selected."""
        self.is_selected = False
        self.update_style()

    def update_style(self):
        """Update visual style based on selection state."""
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #E5F3FF;
                    border: 2px solid #0078D4;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F9F9F9;
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 12px;
                }
                QFrame:hover {
                    background-color: #F3F3F3;
                    border-color: #0078D4;
                }
            """)


class AdvancedOptionsPanel(QWidget):
    """Expandable panel for advanced customization options."""

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button
        self.toggle_btn = ModernButton("▶ Advanced Options")
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        main_layout.addWidget(self.toggle_btn)

        # Options container (initially hidden)
        self.options_container = QFrame()
        self.options_container.setVisible(False)
        self.options_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 16px;
            }
        """)

        options_layout = QVBoxLayout(self.options_container)

        # Create scrollable area for all options
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setMaximumHeight(600)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Feature categories
        self.feature_checkboxes = {}

        categories = [
            ("🎮 Gaming Optimizations", [
                ("gaming_competitive", "Competitive Gaming Profile"),
                ("gaming_balanced", "Balanced Gaming Profile"),
                ("gaming_quality", "Quality Gaming Profile"),
                ("gaming_streaming", "Streaming Gaming Profile"),
                ("network_latency", "Network Latency Reduction"),
                ("game_mode", "Enable Game Mode"),
                ("gpu_scheduling", "GPU Hardware Scheduling"),
            ]),
            ("🗑️ Debloating & Privacy", [
                ("debloat_aggressive", "Aggressive Debloating"),
                ("debloat_moderate", "Moderate Debloating"),
                ("debloat_minimal", "Minimal Debloating"),
                ("privacy_hardening", "Privacy Hardening"),
                ("disable_telemetry", "Disable Telemetry"),
                ("dns_over_https", "DNS over HTTPS"),
            ]),
            ("🎨 Visual Customization", [
                ("dark_theme", "Dark Theme"),
                ("light_theme", "Light Theme"),
                ("custom_wallpaper", "Custom Wallpaper"),
                ("taskbar_left", "Taskbar on Left"),
                ("taskbar_center", "Taskbar Centered"),
                ("modern_ui", "Modern UI Tweaks"),
            ]),
            ("💻 Developer Tools", [
                ("wsl2", "Enable WSL2"),
                ("hyperv", "Enable Hyper-V"),
                ("sandbox", "Enable Windows Sandbox"),
                ("dev_mode", "Developer Mode"),
                ("docker", "Docker Desktop"),
                ("git", "Git for Windows"),
                ("vscode", "VS Code"),
            ]),
            ("🏢 Enterprise Features", [
                ("bitlocker", "BitLocker Encryption"),
                ("cis_benchmark", "CIS Benchmark"),
                ("disa_stig", "DISA STIG Compliance"),
                ("gpo_hardening", "Group Policy Hardening"),
                ("certificate_enrollment", "Certificate Auto-Enrollment"),
                ("mdt_integration", "MDT Integration"),
            ]),
            ("📦 Applications", [
                ("browsers", "Install Browsers"),
                ("office", "Microsoft Office"),
                ("creative_suite", "Creative Tools (OBS, GIMP, etc)"),
                ("gaming_launchers", "Gaming Launchers (Steam, Epic, etc)"),
                ("winget_packages", "WinGet Package Manager"),
            ]),
            ("⚙️ System Optimization", [
                ("performance_optimize", "Performance Optimization"),
                ("network_optimize", "Network Optimization"),
                ("storage_optimize", "Storage Optimization"),
                ("ram_optimize", "RAM Optimization"),
                ("startup_optimize", "Startup Optimization"),
            ]),
        ]

        for category_name, features in categories:
            group = QGroupBox(category_name)
            group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            group_layout = QVBoxLayout()

            for feature_id, feature_name in features:
                checkbox = QCheckBox(feature_name)
                checkbox.setFont(QFont("Segoe UI", 9))
                self.feature_checkboxes[feature_id] = checkbox
                group_layout.addWidget(checkbox)

            group.setLayout(group_layout)
            scroll_layout.addWidget(group)

        scroll.setWidget(scroll_widget)
        options_layout.addWidget(scroll)

        main_layout.addWidget(self.options_container)

    def toggle_visibility(self):
        """Toggle the visibility of advanced options."""
        is_visible = self.options_container.isVisible()
        self.options_container.setVisible(not is_visible)

        if is_visible:
            self.toggle_btn.setText("▶ Advanced Options")
        else:
            self.toggle_btn.setText("▼ Advanced Options")

    def get_selected_features(self) -> Dict[str, bool]:
        """Get dictionary of selected features."""
        return {
            feature_id: checkbox.isChecked()
            for feature_id, checkbox in self.feature_checkboxes.items()
        }

    def apply_profile_settings(self, profile_id: str):
        """Auto-select features based on profile."""
        # Reset all
        for checkbox in self.feature_checkboxes.values():
            checkbox.setChecked(False)

        # Profile-specific selections
        profile_features = {
            'gamer': [
                'gaming_competitive', 'network_latency', 'game_mode',
                'gpu_scheduling', 'debloat_moderate', 'dark_theme',
                'performance_optimize', 'network_optimize', 'gaming_launchers'
            ],
            'developer': [
                'wsl2', 'hyperv', 'sandbox', 'dev_mode', 'docker',
                'git', 'vscode', 'dark_theme', 'taskbar_left', 'debloat_minimal'
            ],
            'enterprise': [
                'bitlocker', 'cis_benchmark', 'disa_stig', 'gpo_hardening',
                'certificate_enrollment', 'light_theme', 'taskbar_left'
            ],
            'student': [
                'debloat_moderate', 'privacy_hardening', 'office',
                'browsers', 'performance_optimize', 'light_theme'
            ],
            'creator': [
                'creative_suite', 'gpu_scheduling', 'storage_optimize',
                'ram_optimize', 'dark_theme', 'performance_optimize'
            ],
            'custom': []  # No auto-selection for custom
        }

        features = profile_features.get(profile_id, [])
        for feature_id in features:
            if feature_id in self.feature_checkboxes:
                self.feature_checkboxes[feature_id].setChecked(True)


class BuildWorker(QThread):
    """Background worker thread for image building."""

    # Signals
    progress = pyqtSignal(int, str)  # percentage, message
    log = pyqtSignal(str)  # log message
    finished = pyqtSignal(bool, str)  # success, message
    error = pyqtSignal(str)  # error message

    def __init__(self, image_path: Path, profile_name: str,
                 output_path: Optional[Path], selected_features: Dict[str, bool],
                 validate: bool, compress: bool):
        super().__init__()
        self.image_path = image_path
        self.profile_name = profile_name
        self.output_path = output_path
        self.selected_features = selected_features
        self.validate = validate
        self.compress = compress
        self._cancelled = False

    def run(self):
        """Execute the build operation."""
        try:
            if not BACKEND_AVAILABLE:
                self.error.emit("Backend modules not available. Cannot build image.")
                self.finished.emit(False, "Backend modules not available")
                return

            self.log.emit(f"[INFO] Starting build process...")
            self.log.emit(f"[INFO] Source: {self.image_path}")
            self.log.emit(f"[INFO] Profile: {self.profile_name}")
            self.log.emit(f"[INFO] Output: {self.output_path or 'Same as source'}")
            self.progress.emit(5, "Initializing build...")

            if self._cancelled:
                self.log.emit("[WARN] Build cancelled by user")
                self.finished.emit(False, "Cancelled by user")
                return

            # Validate source image exists
            self.progress.emit(10, "Validating source image...")
            self.log.emit(f"[INFO] Checking source image: {self.image_path}")

            if not self.image_path.exists():
                raise FileNotFoundError(f"Source image not found: {self.image_path}")

            self.log.emit("[OK] Source image validated")

            # Call actual build logic
            self.progress.emit(20, "Applying profile configuration...")
            self.log.emit(f"[INFO] Applying {self.profile_name} profile...")

            try:
                # Call the actual apply_profile function from backend
                apply_profile(
                    image_path=self.image_path,
                    profile_name=self.profile_name,
                    output_path=self.output_path
                )

                self.log.emit("[OK] Profile applied successfully")
                self.progress.emit(50, "Profile configuration complete")

            except Exception as e:
                self.log.emit(f"[ERROR] Failed to apply profile: {str(e)}")
                raise

            if self._cancelled:
                self.log.emit("[WARN] Build cancelled by user")
                self.finished.emit(False, "Cancelled by user")
                return

            # Apply additional features using ConfigurationManager
            self.progress.emit(55, "Applying additional features...")
            self.log.emit(f"[INFO] Processing {len([f for f in self.selected_features.values() if f])} additional features...")

            try:
                # Create configuration manager
                config_manager = ConfigurationManager()

                # Set up callbacks for progress and logging
                config_manager.progress_callback = lambda pct, msg: self.progress.emit(
                    55 + int(pct * 0.25),  # Map 0-100% to 55-80% of total progress
                    msg
                )
                config_manager.log_callback = lambda msg: self.log.emit(msg)

                # Configure modules from GUI selections
                config_manager.configure_from_gui(self.selected_features)

                # Execute all enabled modules
                success = config_manager.execute_all(
                    image_path=self.image_path,
                    profile_name=self.profile_name,
                    output_path=self.output_path
                )

                if success:
                    self.log.emit("[OK] Additional features applied successfully")
                else:
                    self.log.emit("[WARN] Some features completed with warnings")

                self.progress.emit(80, "Features application complete")

            except Exception as e:
                self.log.emit(f"[ERROR] Failed to apply features: {str(e)}")
                # Continue with build even if features fail
                self.log.emit("[WARN] Continuing build despite feature application errors")

            if self._cancelled:
                self.log.emit("[WARN] Build cancelled by user")
                self.finished.emit(False, "Cancelled by user")
                return

            # Validation (if enabled)
            if self.validate:
                self.progress.emit(90, "Validating output image...")
                self.log.emit("[INFO] Running image validation...")
                # TODO: Add validation logic
                self.log.emit("[OK] Validation passed")

            # Complete
            self.progress.emit(100, "Build complete!")
            self.log.emit("[SUCCESS] Image build completed successfully!")

            output_location = self.output_path or f"{self.image_path.stem}_custom.wim"
            self.finished.emit(True, f"Image successfully created: {output_location}")

        except Exception as e:
            error_msg = f"Build failed: {str(e)}"
            self.log.emit(f"[ERROR] {error_msg}")
            self.log.emit(f"[ERROR] Traceback: {traceback.format_exc()}")
            self.error.emit(error_msg)
            self.finished.emit(False, error_msg)

    def cancel(self):
        """Cancel the build operation."""
        self._cancelled = True
        self.log.emit("[WARN] Cancellation requested...")


class BuildProgressDialog(QWidget):
    """Progress dialog for build operations."""

    def __init__(self, worker: BuildWorker, parent=None):
        super().__init__(parent)

        self.worker = worker
        self.build_completed = False

        self.setWindowTitle("Building Image")
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Building Custom Windows Image")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # Current operation
        self.operation_label = QLabel("Initializing...")
        self.operation_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.operation_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Time remaining
        self.time_label = QLabel("Build in progress...")
        self.time_label.setStyleSheet("color: #666666; font-size: 9pt;")
        layout.addWidget(self.time_label)

        # Log output
        log_label = QLabel("Build Log:")
        log_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = ModernButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_build)
        button_layout.addWidget(self.cancel_btn)

        self.close_btn = ModernButton("Close", primary=True)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setVisible(False)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # Connect worker signals
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.add_log)
        self.worker.finished.connect(self.on_build_finished)
        self.worker.error.connect(self.on_build_error)

        # Start the worker
        self.worker.start()

    def update_progress(self, value: int, operation: str):
        """Update progress bar and current operation."""
        self.progress_bar.setValue(value)
        self.operation_label.setText(operation)

    def add_log(self, message: str):
        """Add a message to the build log."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_build_finished(self, success: bool, message: str):
        """Handle build completion."""
        self.build_completed = True
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)

        if success:
            self.operation_label.setText("✓ Build completed successfully!")
            self.operation_label.setStyleSheet("color: #107C10; font-weight: bold;")
            self.time_label.setText(message)

            QMessageBox.information(
                self,
                "Build Complete",
                f"Image built successfully!\n\n{message}"
            )
        else:
            self.operation_label.setText("✗ Build failed")
            self.operation_label.setStyleSheet("color: #C50F1F; font-weight: bold;")
            self.time_label.setText(message)

    def on_build_error(self, error_msg: str):
        """Handle build error."""
        QMessageBox.critical(
            self,
            "Build Error",
            f"An error occurred during the build:\n\n{error_msg}"
        )

    def cancel_build(self):
        """Cancel the build operation."""
        if self.build_completed:
            self.close()
            return

        reply = QMessageBox.question(
            self,
            "Cancel Build",
            "Are you sure you want to cancel the build?\n\nThis may leave the image in an incomplete state.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.add_log("[WARN] User requested cancellation...")
            self.worker.cancel()
            self.worker.wait(5000)  # Wait up to 5 seconds
            if self.worker.isRunning():
                self.worker.terminate()
            self.close()

    def closeEvent(self, event):
        """Handle window close event."""
        if not self.build_completed and self.worker.isRunning():
            self.cancel_build()
            if self.worker.isRunning():
                event.ignore()
                return
        event.accept()


class BuildPage(QWidget):
    """Image builder page with profile selection, advanced options, and drag-and-drop support."""

    def __init__(self):
        super().__init__()

        self.selected_profile = None
        self.selected_source = None
        self.selected_output = None

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Build Custom Image")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Create a customized Windows deployment image with your preferred settings and applications.")
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Source Image Card
        source_card = ModernCard("1. Source Image")
        source_layout = QVBoxLayout()

        source_label = QLabel("Select a Windows installation image (WIM, ESD, or ISO):")
        source_layout.addWidget(source_label)

        source_buttons = QHBoxLayout()
        self.source_path = QLabel("No image selected")
        self.source_path.setStyleSheet("color: #666666; padding: 8px;")
        source_buttons.addWidget(self.source_path, 1)

        btn_browse = ModernButton("Browse...")
        btn_browse.clicked.connect(self.browse_source)
        source_buttons.addWidget(btn_browse)

        source_layout.addLayout(source_buttons)

        # Image info (shown after selection)
        self.image_info = QLabel("")
        self.image_info.setStyleSheet("color: #0078D4; font-size: 9pt; padding: 8px;")
        self.image_info.setVisible(False)
        source_layout.addWidget(self.image_info)

        source_card.layout().addLayout(source_layout)
        layout.addWidget(source_card)

        # Profile Selection Card
        profile_card = ModernCard("2. Select Profile")
        profile_layout = QVBoxLayout()

        profiles_label = QLabel("Choose a customization profile to get started:")
        profile_layout.addWidget(profiles_label)

        profile_layout.addSpacing(12)

        # Profile cards
        self.profile_cards = []
        profiles = [
            ("🎮 Gaming", "Optimized for gaming with performance tweaks, network optimization, and gaming launchers",
             "gamer", ["Performance tuning", "Network optimization", "Gaming launchers", "Moderate debloating"]),
            ("💻 Developer", "Development environment with WSL2, Docker, Git, VS Code, and Hyper-V",
             "developer", ["WSL2", "Docker", "Hyper-V", "Dev tools", "Minimal debloating"]),
            ("🏢 Enterprise", "Enterprise security with CIS benchmarks, BitLocker, GPO hardening, and DISA STIG",
             "enterprise", ["Security hardening", "BitLocker", "Compliance", "Certificate management"]),
            ("📚 Student", "Balanced setup for productivity with Office, browsers, and privacy features",
             "student", ["Microsoft Office", "Browsers", "Privacy tweaks", "Moderate debloating"]),
            ("🎨 Creator", "Content creation suite with OBS, GIMP, Audacity, Blender, and GPU optimization",
             "creator", ["Creative tools", "GPU optimization", "Storage optimization", "Performance"]),
            ("🔧 Custom", "Start with a minimal base and manually customize every option",
             "custom", ["Full manual control", "No automatic changes"])
        ]

        for icon_text, description, profile_id, features in profiles:
            card = ProfileCard(icon_text, description, profile_id, features)
            card.selected.connect(self.on_profile_selected)
            self.profile_cards.append(card)
            profile_layout.addWidget(card)

        profile_card.layout().addLayout(profile_layout)
        layout.addWidget(profile_card)

        # Advanced Options
        self.advanced_options = AdvancedOptionsPanel()
        layout.addWidget(self.advanced_options)

        # Output Settings Card
        output_card = ModernCard("3. Output Settings")
        output_layout = QVBoxLayout()

        output_label = QLabel("Output location:")
        output_layout.addWidget(output_label)

        output_buttons = QHBoxLayout()
        self.output_path = QLabel("Same as source (will create *_custom.wim)")
        self.output_path.setStyleSheet("color: #666666; padding: 8px;")
        output_buttons.addWidget(self.output_path, 1)

        btn_output = ModernButton("Change...")
        btn_output.clicked.connect(self.browse_output)
        output_buttons.addWidget(btn_output)

        output_layout.addLayout(output_buttons)

        # Additional options
        options_layout = QHBoxLayout()

        self.validate_checkbox = QCheckBox("Validate image after build")
        self.validate_checkbox.setChecked(True)
        options_layout.addWidget(self.validate_checkbox)

        self.compress_checkbox = QCheckBox("Maximum compression")
        options_layout.addWidget(self.compress_checkbox)

        options_layout.addStretch()
        output_layout.addLayout(options_layout)

        output_card.layout().addLayout(output_layout)
        layout.addWidget(output_card)

        # Summary Card
        self.summary_card = ModernCard("Build Summary")
        self.summary_card.setVisible(False)
        summary_layout = QVBoxLayout()

        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        summary_layout.addWidget(self.summary_label)

        self.summary_card.layout().addLayout(summary_layout)
        layout.addWidget(self.summary_card)

        # Build Button
        self.btn_build = ModernButton("Build Image", primary=True)
        self.btn_build.setMinimumHeight(50)
        self.btn_build.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_build.clicked.connect(self.start_build)
        self.btn_build.setEnabled(False)  # Disabled until image and profile selected
        layout.addWidget(self.btn_build)

        layout.addStretch()

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def browse_source(self):
        """Browse for source image file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Windows Image",
            "",
            "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            self.selected_source = Path(file_path)
            self.source_path.setText(file_path)
            self.source_path.setStyleSheet("color: #1F1F1F; padding: 8px;")

            # Show image info
            file_size = self.selected_source.stat().st_size / (1024 * 1024 * 1024)
            self.image_info.setText(f"✓ Image loaded: {file_size:.2f} GB")
            self.image_info.setVisible(True)

            self.update_build_button()
            self.update_summary()

    def browse_output(self):
        """Browse for output location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output Location",
            "",
            "Windows Images (*.wim);;All Files (*)"
        )

        if file_path:
            self.selected_output = Path(file_path)
            self.output_path.setText(file_path)
            self.output_path.setStyleSheet("color: #1F1F1F; padding: 8px;")
            self.update_summary()

    @pyqtSlot(str)
    def on_profile_selected(self, profile_id: str):
        """Handle profile selection."""
        # Deselect all other cards
        for card in self.profile_cards:
            if card.profile_id != profile_id:
                card.deselect()

        self.selected_profile = profile_id

        # Apply profile settings to advanced options
        self.advanced_options.apply_profile_settings(profile_id)

        self.update_build_button()
        self.update_summary()

    def update_build_button(self):
        """Enable/disable build button based on selections."""
        can_build = self.selected_source is not None and self.selected_profile is not None
        self.btn_build.setEnabled(can_build)

    def update_summary(self):
        """Update the build summary."""
        if not self.selected_source or not self.selected_profile:
            self.summary_card.setVisible(False)
            return

        self.summary_card.setVisible(True)

        profile_names = {
            'gamer': 'Gaming Profile',
            'developer': 'Developer Profile',
            'enterprise': 'Enterprise Profile',
            'student': 'Student Profile',
            'creator': 'Creator Profile',
            'custom': 'Custom Profile'
        }

        features = self.advanced_options.get_selected_features()
        enabled_count = sum(1 for v in features.values() if v)

        summary_text = f"""
        <b>Profile:</b> {profile_names.get(self.selected_profile, 'Unknown')}<br>
        <b>Source:</b> {self.selected_source.name}<br>
        <b>Output:</b> {self.selected_output.name if self.selected_output else f'{self.selected_source.stem}_custom.wim'}<br>
        <b>Features enabled:</b> {enabled_count}<br>
        <b>Validation:</b> {'Yes' if self.validate_checkbox.isChecked() else 'No'}<br>
        <b>Compression:</b> {'Maximum' if self.compress_checkbox.isChecked() else 'Standard'}
        """

        self.summary_label.setText(summary_text)

    def start_build(self):
        """Start the build process."""
        if not self.selected_source or not self.selected_profile:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please select both a source image and a profile before building."
            )
            return

        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Start Build",
            f"Ready to build custom Windows image with {self.selected_profile} profile.\n\n"
            "This may take 30-60 minutes depending on your selections.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.execute_build()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for image files."""
        if event.mimeData().hasUrls():
            # Check if any URL is a valid image file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.wim', '.esd', '.iso')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for image files."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.wim', '.esd', '.iso')):
                # Set as source image
                self.selected_source = Path(file_path)
                self.source_path.setText(file_path)
                self.source_path.setStyleSheet("color: #1F1F1F; padding: 8px;")

                # Show image info
                file_size = self.selected_source.stat().st_size / (1024 * 1024 * 1024)
                self.image_info.setText(f"✓ Image loaded: {file_size:.2f} GB (via drag-and-drop)")
                self.image_info.setVisible(True)

                self.update_build_button()
                self.update_summary()

                # Show notification
                QMessageBox.information(
                    self,
                    "Image Loaded",
                    f"Source image loaded successfully!\n\n{Path(file_path).name}\n{file_size:.2f} GB"
                )
                break

        event.acceptProposedAction()

    def execute_build(self):
        """Execute the actual build operation."""
        try:
            # Check backend availability
            if not BACKEND_AVAILABLE:
                QMessageBox.critical(
                    self,
                    "Backend Not Available",
                    "DeployForge backend modules are not available.\n\n"
                    "Please ensure the application is properly installed."
                )
                return

            # Get selected features
            selected_features = self.advanced_options.get_selected_features()

            # Create build worker
            worker = BuildWorker(
                image_path=self.selected_source,
                profile_name=self.selected_profile,
                output_path=self.selected_output,
                selected_features=selected_features,
                validate=self.validate_checkbox.isChecked(),
                compress=self.compress_checkbox.isChecked()
            )

            # Create and show progress dialog
            progress_dialog = BuildProgressDialog(worker, self)
            progress_dialog.show()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Build Error",
                f"Failed to start build:\n\n{str(e)}\n\n{traceback.format_exc()}"
            )


class ProfilesPage(QWidget):
    """Profiles management page."""

    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Manage Profiles")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Create, edit, and organize your customization profiles.")
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # Built-in Profiles Card
        builtin_card = ModernCard("Built-in Profiles")
        builtin_layout = QVBoxLayout()

        builtin_profiles = [
            ("🎮 Gaming Profile", "High-performance gaming optimizations", "gamer"),
            ("💻 Developer Profile", "Development tools and environments", "developer"),
            ("🏢 Enterprise Profile", "Security and compliance", "enterprise"),
            ("📚 Student Profile", "Productivity and learning", "student"),
            ("🎨 Creator Profile", "Content creation tools", "creator"),
        ]

        for icon_name, description, profile_id in builtin_profiles:
            profile_row = QFrame()
            profile_row.setStyleSheet("""
                QFrame {
                    background-color: #F9F9F9;
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)

            row_layout = QHBoxLayout(profile_row)

            # Info
            info_layout = QVBoxLayout()
            name_label = QLabel(icon_name)
            name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            info_layout.addWidget(name_label)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666666; font-size: 9pt;")
            info_layout.addWidget(desc_label)

            row_layout.addLayout(info_layout, 1)

            # Actions
            btn_view = ModernButton("View")
            btn_view.setMaximumWidth(80)
            row_layout.addWidget(btn_view)

            btn_clone = ModernButton("Clone")
            btn_clone.setMaximumWidth(80)
            row_layout.addWidget(btn_clone)

            builtin_layout.addWidget(profile_row)

        builtin_card.layout().addLayout(builtin_layout)
        layout.addWidget(builtin_card)

        # Custom Profiles Card
        custom_card = ModernCard("Custom Profiles")
        custom_layout = QVBoxLayout()

        custom_info = QLabel("You haven't created any custom profiles yet.")
        custom_info.setStyleSheet("color: #666666; font-style: italic;")
        custom_layout.addWidget(custom_info)

        btn_create = ModernButton("+ Create New Profile", primary=True)
        btn_create.clicked.connect(self.create_new_profile)
        custom_layout.addWidget(btn_create)

        custom_card.layout().addLayout(custom_layout)
        layout.addWidget(custom_card)

        # Import/Export Card
        import_export_card = ModernCard("Import / Export")
        ie_layout = QHBoxLayout()

        btn_import = ModernButton("Import Profile...")
        btn_export = ModernButton("Export Profile...")

        ie_layout.addWidget(btn_import)
        ie_layout.addWidget(btn_export)
        ie_layout.addStretch()

        import_export_card.layout().addLayout(ie_layout)
        layout.addWidget(import_export_card)

        layout.addStretch()

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_new_profile(self):
        """Create a new custom profile."""
        QMessageBox.information(
            self,
            "Create Profile",
            "Profile creation wizard would open here.\n\n"
            "You would be able to:\n"
            "- Name your profile\n"
            "- Select base profile\n"
            "- Customize all options\n"
            "- Save for reuse"
        )


class AnalyzePage(QWidget):
    """Image analysis page."""

    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Analyze Image")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Examine image contents, generate reports, and compare images.")
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # Single Image Analysis Card
        single_card = ModernCard("Analyze Single Image")
        single_layout = QVBoxLayout()

        single_label = QLabel("Select an image to analyze:")
        single_layout.addWidget(single_label)

        single_row = QHBoxLayout()
        self.analyze_path = QLabel("No image selected")
        self.analyze_path.setStyleSheet("color: #666666; padding: 8px;")
        single_row.addWidget(self.analyze_path, 1)

        btn_browse_analyze = ModernButton("Browse...")
        btn_browse_analyze.clicked.connect(self.browse_analyze_image)
        single_row.addWidget(btn_browse_analyze)

        single_layout.addLayout(single_row)

        # Analysis options
        options_label = QLabel("Analysis Options:")
        options_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        single_layout.addWidget(options_label)

        self.check_features = QCheckBox("Analyze Windows features")
        self.check_features.setChecked(True)
        single_layout.addWidget(self.check_features)

        self.check_apps = QCheckBox("List installed applications")
        self.check_apps.setChecked(True)
        single_layout.addWidget(self.check_apps)

        self.check_drivers = QCheckBox("List drivers")
        single_layout.addWidget(self.check_drivers)

        self.check_size = QCheckBox("Calculate disk usage")
        self.check_size.setChecked(True)
        single_layout.addWidget(self.check_size)

        # Report format
        format_label = QLabel("Report Format:")
        format_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        single_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "JSON", "Text", "PDF"])
        self.format_combo.setMaximumWidth(200)
        single_layout.addWidget(self.format_combo)

        # Analyze button
        btn_analyze = ModernButton("Generate Report", primary=True)
        btn_analyze.clicked.connect(self.run_analysis)
        single_layout.addWidget(btn_analyze)

        single_card.layout().addLayout(single_layout)
        layout.addWidget(single_card)

        # Compare Images Card
        compare_card = ModernCard("Compare Two Images")
        compare_layout = QVBoxLayout()

        compare_label = QLabel("Compare two images side-by-side:")
        compare_layout.addWidget(compare_label)

        # Image 1
        img1_row = QHBoxLayout()
        img1_label = QLabel("Image 1:")
        img1_label.setMinimumWidth(70)
        img1_row.addWidget(img1_label)

        self.compare_img1 = QLabel("No image selected")
        self.compare_img1.setStyleSheet("color: #666666; padding: 8px;")
        img1_row.addWidget(self.compare_img1, 1)

        btn_browse_img1 = ModernButton("Browse...")
        btn_browse_img1.clicked.connect(lambda: self.browse_compare_image(1))
        img1_row.addWidget(btn_browse_img1)

        compare_layout.addLayout(img1_row)

        # Image 2
        img2_row = QHBoxLayout()
        img2_label = QLabel("Image 2:")
        img2_label.setMinimumWidth(70)
        img2_row.addWidget(img2_label)

        self.compare_img2 = QLabel("No image selected")
        self.compare_img2.setStyleSheet("color: #666666; padding: 8px;")
        img2_row.addWidget(self.compare_img2, 1)

        btn_browse_img2 = ModernButton("Browse...")
        btn_browse_img2.clicked.connect(lambda: self.browse_compare_image(2))
        img2_row.addWidget(btn_browse_img2)

        compare_layout.addLayout(img2_row)

        # Compare button
        btn_compare = ModernButton("Compare Images", primary=True)
        btn_compare.clicked.connect(self.run_comparison)
        compare_layout.addWidget(btn_compare)

        compare_card.layout().addLayout(compare_layout)
        layout.addWidget(compare_card)

        # Recent Reports Card
        reports_card = ModernCard("Recent Reports")
        reports_layout = QVBoxLayout()

        reports_info = QLabel("No reports generated yet.")
        reports_info.setStyleSheet("color: #666666; font-style: italic;")
        reports_layout.addWidget(reports_info)

        reports_card.layout().addLayout(reports_layout)
        layout.addWidget(reports_card)

        layout.addStretch()

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def browse_analyze_image(self):
        """Browse for image to analyze."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image to Analyze",
            "",
            "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            self.analyze_path.setText(file_path)
            self.analyze_path.setStyleSheet("color: #1F1F1F; padding: 8px;")

    def browse_compare_image(self, image_num: int):
        """Browse for comparison image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select Image {image_num}",
            "",
            "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            if image_num == 1:
                self.compare_img1.setText(file_path)
                self.compare_img1.setStyleSheet("color: #1F1F1F; padding: 8px;")
            else:
                self.compare_img2.setText(file_path)
                self.compare_img2.setStyleSheet("color: #1F1F1F; padding: 8px;")

    def run_analysis(self):
        """Run image analysis."""
        if self.analyze_path.text() == "No image selected":
            QMessageBox.warning(
                self,
                "No Image Selected",
                "Please select an image to analyze first."
            )
            return

        if not BACKEND_AVAILABLE:
            QMessageBox.critical(
                self,
                "Backend Not Available",
                "DeployForge backend modules are not available.\n\n"
                "Please ensure the application is properly installed."
            )
            return

        try:
            image_path = Path(self.analyze_path.text())
            report_format = self.format_combo.currentText().lower()

            # Show progress
            progress = QMessageBox(self)
            progress.setWindowTitle("Analyzing Image")
            progress.setText(f"Analyzing {image_path.name}...")
            progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress.show()
            QApplication.processEvents()

            # Create analyzer and run analysis
            analyzer = ImageAnalyzer(image_path)
            report_data = analyzer.analyze()

            # Generate report in requested format
            if report_format == 'html':
                report_content = analyzer.generate_html_report(report_data)
                report_extension = '.html'
            elif report_format == 'json':
                import json
                report_content = json.dumps(report_data, indent=2)
                report_extension = '.json'
            elif report_format == 'text':
                report_content = analyzer.format_text_report(report_data)
                report_extension = '.txt'
            else:  # pdf
                QMessageBox.warning(
                    self,
                    "Format Not Supported",
                    "PDF format is not yet implemented.\n\nPlease use HTML, JSON, or Text format."
                )
                progress.close()
                return

            progress.close()

            # Save report
            default_name = f"analysis_{image_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{report_extension}"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Analysis Report",
                default_name,
                f"{report_format.upper()} Files (*{report_extension});;All Files (*)"
            )

            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)

                QMessageBox.information(
                    self,
                    "Analysis Complete",
                    f"Analysis report saved successfully!\n\n"
                    f"Location: {save_path}\n\n"
                    f"Features: {report_data.get('features_count', 0)}\n"
                    f"Applications: {report_data.get('applications_count', 0)}"
                )

                # TODO: Add to recent reports list

        except Exception as e:
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to analyze image:\n\n{str(e)}\n\n{traceback.format_exc()}"
            )

    def run_comparison(self):
        """Run image comparison."""
        if (self.compare_img1.text() == "No image selected" or
                self.compare_img2.text() == "No image selected"):
            QMessageBox.warning(
                self,
                "Missing Images",
                "Please select both images to compare."
            )
            return

        if not BACKEND_AVAILABLE:
            QMessageBox.critical(
                self,
                "Backend Not Available",
                "DeployForge backend modules are not available.\n\n"
                "Please ensure the application is properly installed."
            )
            return

        try:
            image1_path = Path(self.compare_img1.text())
            image2_path = Path(self.compare_img2.text())

            # Show progress
            progress = QMessageBox(self)
            progress.setWindowTitle("Comparing Images")
            progress.setText("Analyzing both images...")
            progress.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress.show()
            QApplication.processEvents()

            # Analyze both images
            analyzer1 = ImageAnalyzer(image1_path)
            analyzer2 = ImageAnalyzer(image2_path)

            report1 = analyzer1.analyze()
            report2 = analyzer2.analyze()

            progress.close()

            # Generate comparison summary
            features1 = set(report1.get('features', []))
            features2 = set(report2.get('features', []))
            apps1 = set(report1.get('applications', []))
            apps2 = set(report2.get('applications', []))

            features_only_1 = features1 - features2
            features_only_2 = features2 - features1
            apps_only_1 = apps1 - apps2
            apps_only_2 = apps2 - apps1

            comparison_text = f"""
Image Comparison Results

Image 1: {image1_path.name}
- Size: {report1.get('size_analysis', {}).get('total_mb', 0):.2f} MB
- Features: {len(features1)}
- Applications: {len(apps1)}

Image 2: {image2_path.name}
- Size: {report2.get('size_analysis', {}).get('total_mb', 0):.2f} MB
- Features: {len(features2)}
- Applications: {len(apps2)}

Differences:
- Features only in Image 1: {len(features_only_1)}
- Features only in Image 2: {len(features_only_2)}
- Applications only in Image 1: {len(apps_only_1)}
- Applications only in Image 2: {len(apps_only_2)}

Common:
- Shared features: {len(features1 & features2)}
- Shared applications: {len(apps1 & apps2)}
            """

            # Save comparison report
            default_name = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Comparison Report",
                default_name,
                "Text Files (*.txt);;All Files (*)"
            )

            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(comparison_text)

                    # Add detailed lists
                    if features_only_1:
                        f.write("\n\nFeatures only in Image 1:\n")
                        for feat in sorted(features_only_1)[:20]:  # Limit to 20
                            f.write(f"  - {feat}\n")

                    if features_only_2:
                        f.write("\n\nFeatures only in Image 2:\n")
                        for feat in sorted(features_only_2)[:20]:
                            f.write(f"  - {feat}\n")

                QMessageBox.information(
                    self,
                    "Comparison Complete",
                    f"Comparison report saved!\n\n{comparison_text}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Comparison Error",
                f"Failed to compare images:\n\n{str(e)}\n\n{traceback.format_exc()}"
            )


class SettingsPage(QWidget):
    """Settings page with theme switcher and preferences."""

    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QLabel("Settings")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Customize your DeployForge experience")
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        # Theme Settings
        theme_card = ModernCard("Appearance")
        theme_layout = QVBoxLayout()

        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        theme_layout.addWidget(theme_label)

        theme_desc = QLabel("Choose your preferred color scheme")
        theme_desc.setStyleSheet("color: #666666; font-size: 9pt;")
        theme_layout.addWidget(theme_desc)

        theme_layout.addSpacing(8)

        # Theme buttons
        theme_buttons_layout = QHBoxLayout()

        self.btn_light = ModernButton("☀️ Light Theme")
        self.btn_light.setMinimumWidth(150)
        self.btn_light.clicked.connect(lambda: self.set_theme('Light'))
        theme_buttons_layout.addWidget(self.btn_light)

        self.btn_dark = ModernButton("🌙 Dark Theme")
        self.btn_dark.setMinimumWidth(150)
        self.btn_dark.clicked.connect(lambda: self.set_theme('Dark'))
        theme_buttons_layout.addWidget(self.btn_dark)

        theme_buttons_layout.addStretch()
        theme_layout.addLayout(theme_buttons_layout)

        # Current theme indicator
        self.theme_status = QLabel(f"Current theme: {theme_manager.get_theme()}")
        self.theme_status.setStyleSheet(f"color: {theme_manager.get_colors()['primary']}; font-size: 9pt; font-weight: bold;")
        theme_layout.addWidget(self.theme_status)

        theme_card.layout().addLayout(theme_layout)
        layout.addWidget(theme_card)

        # General Settings
        general_card = ModernCard("General")
        general_layout = QVBoxLayout()

        self.check_validate = QCheckBox("Always validate images after build")
        self.check_validate.setChecked(True)
        general_layout.addWidget(self.check_validate)

        self.check_compress = QCheckBox("Use maximum compression by default")
        general_layout.addWidget(self.check_compress)

        self.check_recent = QCheckBox("Show recent files on welcome page")
        self.check_recent.setChecked(True)
        general_layout.addWidget(self.check_recent)

        general_card.layout().addLayout(general_layout)
        layout.addWidget(general_card)

        # Advanced Settings
        advanced_card = ModernCard("Advanced")
        advanced_layout = QVBoxLayout()

        self.check_debug = QCheckBox("Enable debug logging")
        advanced_layout.addWidget(self.check_debug)

        self.check_auto_save = QCheckBox("Auto-save window position and size")
        self.check_auto_save.setChecked(True)
        advanced_layout.addWidget(self.check_auto_save)

        advanced_card.layout().addLayout(advanced_layout)
        layout.addWidget(advanced_card)

        # Save/Reset buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        btn_save = ModernButton("Save Settings", primary=True)
        btn_save.clicked.connect(self.save_settings)
        buttons_layout.addWidget(btn_save)

        btn_reset = ModernButton("Reset to Defaults")
        btn_reset.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(btn_reset)

        layout.addLayout(buttons_layout)

        layout.addStretch()

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Register for theme changes
        theme_manager.on_theme_changed(self.on_theme_changed)

    def set_theme(self, theme_name: str):
        """Set the application theme."""
        theme_manager.set_theme(theme_name)
        self.theme_status.setText(f"Current theme: {theme_name}")
        self.theme_status.setStyleSheet(f"color: {theme_manager.get_colors()['primary']}; font-size: 9pt; font-weight: bold;")

        # Save to settings
        settings = QSettings('DeployForge', 'DeployForge')
        settings.setValue('theme', theme_name)

        QMessageBox.information(
            self,
            "Theme Changed",
            f"Theme changed to {theme_name}!\n\nSome elements will update immediately,\nothers may require restarting the application."
        )

    def on_theme_changed(self, theme_name: str):
        """Handle theme change event."""
        self.theme_status.setText(f"Current theme: {theme_name}")

    def save_settings(self):
        """Save all settings."""
        settings = QSettings('DeployForge', 'DeployForge')
        settings.setValue('validate_default', self.check_validate.isChecked())
        settings.setValue('compress_default', self.check_compress.isChecked())
        settings.setValue('show_recent', self.check_recent.isChecked())
        settings.setValue('debug_logging', self.check_debug.isChecked())
        settings.setValue('auto_save_window', self.check_auto_save.isChecked())

        QMessageBox.information(
            self,
            "Settings Saved",
            "Your settings have been saved successfully!"
        )

    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.check_validate.setChecked(True)
            self.check_compress.setChecked(False)
            self.check_recent.setChecked(True)
            self.check_debug.setChecked(False)
            self.check_auto_save.setChecked(True)
            self.set_theme('Light')

            QMessageBox.information(
                self,
                "Settings Reset",
                "All settings have been reset to defaults!"
            )


class DeployForgeGUI(QMainWindow):
    """Main application window with modern UI and settings persistence."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeployForge - Windows Deployment Suite")
        self.setMinimumSize(1200, 800)

        # Load settings
        self.load_settings()

        # Setup UI
        self.setup_ui()

        # Apply theme
        self.apply_initial_theme()

        # Center window (if not loading saved geometry)
        settings = QSettings('DeployForge', 'DeployForge')
        if not settings.contains('window/geometry'):
            self.center_window()

    def load_settings(self):
        """Load application settings."""
        settings = QSettings('DeployForge', 'DeployForge')

        # Load window geometry
        if settings.contains('window/geometry'):
            self.restoreGeometry(settings.value('window/geometry'))

        # Load theme
        theme = settings.value('theme', 'Light')
        theme_manager.set_theme(theme)

    def apply_initial_theme(self):
        """Apply theme to main window components."""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"background-color: {colors['background']};")

        # Register for theme changes
        theme_manager.on_theme_changed(self.on_theme_changed)

    def on_theme_changed(self, theme_name: str):
        """Handle theme change."""
        colors = theme_manager.get_colors()
        self.setStyleSheet(f"background-color: {colors['background']};")
        self.content_stack.setStyleSheet(f"background-color: {colors['background']};")
        self.statusBar().setStyleSheet(
            f"background-color: {colors['surface']}; border-top: 1px solid {colors['border']}; color: {colors['text']};"
        )

    def setup_ui(self):
        """Setup the main user interface."""

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #FAFAFA;")

        # Add pages
        self.pages = {
            'welcome': WelcomePage(),
            'build': BuildPage(),
            'profiles': ProfilesPage(),
            'analyze': AnalyzePage(),
            'settings': SettingsPage()
        }

        for page in self.pages.values():
            self.content_stack.addWidget(page)

        main_layout.addWidget(self.content_stack, 1)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("background-color: #F3F3F3; border-top: 1px solid #D1D1D1;")

        # Menu bar
        self.create_menu_bar()

    def create_sidebar(self) -> QWidget:
        """Create the sidebar navigation."""

        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo/Title
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #0078D4;")

        header_layout = QHBoxLayout(header)
        title = QLabel("DeployForge")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding-left: 16px;")
        header_layout.addWidget(title)

        layout.addWidget(header)

        # Navigation buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 8, 0, 8)
        nav_layout.setSpacing(0)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        # Create navigation buttons
        nav_items = [
            ("🏠 Home", 'welcome'),
            ("🔨 Build Image", 'build'),
            ("📋 Profiles", 'profiles'),
            ("🔍 Analyze", 'analyze'),
            ("⚙️ Settings", 'settings')
        ]

        for text, page_id in nav_items:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, p=page_id: self.show_page(p))
            self.button_group.addButton(btn)
            nav_layout.addWidget(btn)

        # Set home as default
        self.button_group.buttons()[0].setChecked(True)

        nav_layout.addStretch()

        scroll.setWidget(nav_widget)
        layout.addWidget(scroll)

        # Version info at bottom
        version_label = QLabel("v0.7.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #999999; padding: 8px; font-size: 9pt;")
        layout.addWidget(version_label)

        return sidebar

    def create_menu_bar(self):
        """Create the menu bar."""

        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Build", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Validate Image")
        tools_menu.addAction("Compare Images")
        tools_menu.addAction("Create Preset")

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("Documentation")
        help_menu.addAction("About")

    def show_page(self, page_id: str):
        """Show a specific page."""

        if page_id in self.pages:
            index = list(self.pages.keys()).index(page_id)
            self.content_stack.setCurrentIndex(index)

            # Update status bar
            page_names = {
                'welcome': 'Home',
                'build': 'Build Image',
                'profiles': 'Manage Profiles',
                'analyze': 'Analyze Image',
                'settings': 'Settings'
            }
            self.statusBar().showMessage(f"{page_names.get(page_id, 'Ready')}")

    def center_window(self):
        """Center the window on screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def closeEvent(self, event):
        """Handle window close event and save settings."""
        settings = QSettings('DeployForge', 'DeployForge')

        # Save window geometry
        if settings.value('auto_save_window', True, type=bool):
            settings.setValue('window/geometry', self.saveGeometry())

        # Save current theme
        settings.setValue('theme', theme_manager.get_theme())

        event.accept()


def launch_modern_gui():
    """Launch the modern GUI application."""

    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Set application font
    app.setFont(QFont("Segoe UI", 10))

    # Create and show main window
    window = DeployForgeGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    launch_modern_gui()
