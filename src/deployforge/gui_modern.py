"""
DeployForge Modern GUI Application

A beautiful, intuitive, and powerful graphical interface for Windows deployment
image customization. Features modern design, easy navigation, and comprehensive
functionality.

Built with PyQt6 for professional appearance and cross-platform compatibility.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame, QScrollArea,
    QSplitter, QToolButton, QButtonGroup, QMessageBox, QProgressBar,
    QStatusBar, QMenuBar, QMenu, QToolBar, QFileDialog, QTextEdit,
    QCheckBox, QComboBox, QSpinBox, QGroupBox, QGridLayout, QRadioButton,
    QSlider, QLineEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction, QPalette, QColor

logger = logging.getLogger(__name__)


class ModernButton(QPushButton):
    """Modern styled button with hover effects."""

    def __init__(self, text: str, icon: Optional[str] = None, primary: bool = False):
        super().__init__(text)

        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(20, 20))

        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #106EBE;
                }
                QPushButton:pressed {
                    background-color: #005A9E;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F3F3F3;
                    color: #1F1F1F;
                    border: 1px solid #D1D1D1;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #E5E5E5;
                    border-color: #B3B3B3;
                }
                QPushButton:pressed {
                    background-color: #D6D6D6;
                }
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


class WelcomePage(QWidget):
    """Welcome/Home page with quick actions."""

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

        # Quick Actions
        quick_actions = ModernCard("Quick Start")
        quick_layout = QVBoxLayout()

        quick_layout.addWidget(QLabel("Get started with these common tasks:"))
        quick_layout.addSpacing(8)

        btn_gaming = ModernButton("🎮 Build Gaming Image", primary=True)
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


class BuildProgressDialog(QWidget):
    """Progress dialog for build operations."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Building Image")
        self.setMinimumSize(500, 300)

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
        self.time_label = QLabel("Calculating time remaining...")
        self.time_label.setStyleSheet("color: #666666; font-size: 9pt;")
        layout.addWidget(self.time_label)

        # Log output
        log_label = QLabel("Build Log:")
        log_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = ModernButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_build)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def update_progress(self, value: int, operation: str):
        """Update progress bar and current operation."""
        self.progress_bar.setValue(value)
        self.operation_label.setText(operation)

    def add_log(self, message: str):
        """Add a message to the build log."""
        self.log_text.append(message)

    def cancel_build(self):
        """Cancel the build operation."""
        reply = QMessageBox.question(
            self,
            "Cancel Build",
            "Are you sure you want to cancel the build?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.close()


class BuildPage(QWidget):
    """Image builder page with profile selection and advanced options."""

    def __init__(self):
        super().__init__()

        self.selected_profile = None
        self.selected_source = None
        self.selected_output = None

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

    def execute_build(self):
        """Execute the actual build operation."""
        # Create progress dialog
        progress = BuildProgressDialog(self)
        progress.show()

        # TODO: Integrate with actual build logic from cli/profiles.py
        # This would call apply_profile() with selected options

        # Simulated progress for now
        progress.update_progress(10, "Mounting source image...")
        progress.add_log("[INFO] Starting build process...")
        progress.add_log(f"[INFO] Source: {self.selected_source}")
        progress.add_log(f"[INFO] Profile: {self.selected_profile}")

        QMessageBox.information(
            self,
            "Build Started",
            "Build process has started. This is a demonstration.\n\n"
            "In production, this would call the actual profile application logic."
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

        # TODO: Integrate with actual analyzer from cli/analyzer.py

        QMessageBox.information(
            self,
            "Analysis Started",
            f"Analysis started for {Path(self.analyze_path.text()).name}\n\n"
            f"Report format: {self.format_combo.currentText()}\n\n"
            "In production, this would call the actual analysis logic and generate a report."
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

        # TODO: Integrate with actual comparator from comparison module

        QMessageBox.information(
            self,
            "Comparison Started",
            "Image comparison started.\n\n"
            "This would show:\n"
            "- Files only in Image 1\n"
            "- Files only in Image 2\n"
            "- Different files\n"
            "- Similarity percentage"
        )


class SettingsPage(QWidget):
    """Settings page."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        header = QLabel("Settings")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        # Theme Settings
        theme_card = ModernCard("Appearance")
        theme_layout = QVBoxLayout()

        theme_label = QLabel("Theme:")
        theme_layout.addWidget(theme_label)

        btn_light = ModernButton("Light Theme")
        btn_dark = ModernButton("Dark Theme")

        theme_layout.addWidget(btn_light)
        theme_layout.addWidget(btn_dark)

        theme_card.layout().addLayout(theme_layout)
        layout.addWidget(theme_card)

        layout.addStretch()


class DeployForgeGUI(QMainWindow):
    """Main application window with modern UI."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeployForge - Windows Deployment Suite")
        self.setMinimumSize(1200, 800)

        # Setup UI
        self.setup_ui()

        # Center window
        self.center_window()

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
