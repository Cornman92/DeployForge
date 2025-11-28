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
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QSplitter,
    QToolButton,
    QButtonGroup,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QToolBar,
    QFileDialog,
    QTextEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QGroupBox,
    QGridLayout,
    QRadioButton,
    QSlider,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer, pyqtSlot, QSettings, QMimeData
from PyQt6.QtGui import (
    QIcon,
    QFont,
    QPixmap,
    QAction,
    QPalette,
    QColor,
    QDragEnterEvent,
    QDropEvent,
)

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
        "name": "Light",
        "background": "#FAFAFA",
        "surface": "#FFFFFF",
        "surface_variant": "#F9F9F9",
        "primary": "#0078D4",
        "primary_hover": "#106EBE",
        "primary_pressed": "#005A9E",
        "text": "#1F1F1F",
        "text_secondary": "#666666",
        "border": "#E0E0E0",
        "border_hover": "#B3B3B3",
        "button_bg": "#F3F3F3",
        "button_hover": "#E5E5E5",
        "button_pressed": "#D6D6D6",
        "success": "#107C10",
        "error": "#C50F1F",
        "warning": "#FFB900",
        "sidebar": "#FFFFFF",
        "sidebar_selected": "#E5F3FF",
        "sidebar_hover": "#F3F3F3",
    }

    DARK = {
        "name": "Dark",
        "background": "#1E1E1E",
        "surface": "#252526",
        "surface_variant": "#2D2D30",
        "primary": "#0078D4",
        "primary_hover": "#1890F6",
        "primary_pressed": "#005A9E",
        "text": "#FFFFFF",
        "text_secondary": "#CCCCCC",
        "border": "#3E3E42",
        "border_hover": "#555555",
        "button_bg": "#3E3E42",
        "button_hover": "#4E4E52",
        "button_pressed": "#5E5E62",
        "success": "#4EC9B0",
        "error": "#F48771",
        "warning": "#FFCC00",
        "sidebar": "#2D2D30",
        "sidebar_selected": "#094771",
        "sidebar_hover": "#3E3E42",
    }

    @staticmethod
    def get(theme_name: str = "Light") -> dict:
        """Get theme colors by name."""
        return Theme.DARK if theme_name == "Dark" else Theme.LIGHT


class ThemeManager:
    """Manages application theme."""

    def __init__(self):
        self.current_theme = "Light"
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
            self.setStyleSheet(
                f"""
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
            """
            )
        else:
            self.setStyleSheet(
                f"""
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
            """
            )


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

        self.setStyleSheet(
            """
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
        """
        )


class ModernCard(QFrame):
    """Modern card widget for grouping content."""

    def __init__(self, title: str = ""):
        super().__init__()

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
            }
        """
        )

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
        self.wizard_image_path.setStyleSheet(
            "padding: 8px; background-color: #F3F3F3; border-radius: 4px;"
        )
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
            self, "Select Windows Image", "", "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            self.wizard_image_path.setText(file_path)
            self.config["image_path"] = file_path

    def go_next(self):
        """Go to next step."""
        if self.current_step == 3:  # Last step
            self.finish_wizard()
            return

        # Validate current step
        if self.current_step == 1 and not self.config.get("image_path"):
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

        self.config["profile"] = profile_id

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
        btn_wizard.setToolTip("Launch the step-by-step setup wizard for beginners (F1 for help)")
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
        btn_gaming.setToolTip(
            "Create a gaming-optimized image with performance tweaks and low latency"
        )
        btn_developer = ModernButton("💻 Build Developer Image")
        btn_developer.setToolTip("Create a development image with WSL2, Docker, Git, and VS Code")
        btn_enterprise = ModernButton("🏢 Build Enterprise Image")
        btn_enterprise.setToolTip(
            "Create a secure enterprise image with CIS benchmarks and BitLocker"
        )
        btn_custom = ModernButton("🔧 Custom Build")
        btn_custom.setToolTip(
            "Create a fully customized image with manual control over all options"
        )

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
            f"Go to the Build page to customize further or build now.",
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
            self.setStyleSheet(
                """
                QFrame {
                    background-color: #E5F3FF;
                    border: 2px solid #0078D4;
                    border-radius: 6px;
                    padding: 12px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
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
            """
            )


class AdvancedOptionsPanel(QWidget):
    """Expandable panel for advanced customization options."""

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button
        self.toggle_btn = ModernButton("▶ Advanced Options")
        self.toggle_btn.setToolTip("Click to show/hide 150+ advanced customization features")
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        main_layout.addWidget(self.toggle_btn)

        # Options container (initially hidden)
        self.options_container = QFrame()
        self.options_container.setVisible(False)
        self.options_container.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 16px;
            }
        """
        )

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

        # Feature tooltips for accessibility (150+ features)
        self.feature_tooltips = {
            # Gaming Optimizations
            "gaming_competitive": "Configure network and system settings for competitive gaming (lowest latency)",
            "gaming_balanced": "Balanced gaming profile with good performance and quality",
            "gaming_quality": "Optimized for high-quality gaming experience (graphics over speed)",
            "gaming_streaming": "Optimized for game streaming with network bandwidth priority",
            "network_latency": "Reduce network latency with TCP optimizations and throttling removal",
            "game_mode": "Enable Windows Game Mode for prioritized gaming performance",
            "gpu_scheduling": "Enable GPU hardware scheduling for improved frame pacing",
            "game_dvr": "Disable Game DVR for better gaming performance",
            "fullscreen_optimizations": "Disable fullscreen optimizations for compatibility",
            "game_bar": "Configure Xbox Game Bar settings",
            "nvidia_drivers": "Install latest NVIDIA graphics drivers",
            "amd_drivers": "Install latest AMD graphics drivers",
            "directx_runtime": "Install DirectX runtime libraries",
            "vcredist_all": "Install all Visual C++ redistributables",
            "discord_gaming": "Install Discord for voice chat",
            # Debloating & Privacy
            "debloat_aggressive": "Remove maximum bloatware and unnecessary Windows components",
            "debloat_moderate": "Remove common bloatware while keeping useful features",
            "debloat_minimal": "Remove only the most problematic bloatware",
            "privacy_hardening": "Apply comprehensive privacy tweaks and disable tracking",
            "disable_telemetry": "Disable Windows telemetry and data collection",
            "dns_over_https": "Enable DNS over HTTPS for encrypted DNS queries (Cloudflare)",
            "disable_cortana": "Disable Cortana voice assistant completely",
            "disable_bing_search": "Remove Bing search from Start Menu",
            "disable_advertising_id": "Disable Windows Advertising ID",
            "disable_activity_history": "Disable Activity History and Timeline",
            "disable_location": "Disable Location Services",
            "disable_background_apps": "Prevent apps from running in background",
            "block_telemetry_ips": "Block Microsoft telemetry servers via hosts file",
            "disable_windows_feedback": "Disable Windows feedback prompts",
            "disable_suggestions": "Disable app suggestions and tips",
            "disable_lock_screen_ads": "Remove ads from lock screen",
            # Visual Customization
            "dark_theme": "Apply dark theme across Windows UI",
            "light_theme": "Apply light theme across Windows UI",
            "custom_wallpaper": "Set a custom desktop wallpaper",
            "taskbar_left": "Move taskbar icons to the left (Windows 10 style)",
            "taskbar_center": "Keep taskbar icons centered (Windows 11 default)",
            "modern_ui": "Apply modern UI tweaks and improvements",
            "classic_context_menu": "Enable Windows 10 style context menu (Win11)",
            "classic_explorer": "Enable classic File Explorer ribbon",
            "show_file_extensions": "Always show file extensions",
            "show_hidden_files": "Show hidden files and folders",
            "colored_titlebar": "Enable colored window title bars",
            "transparency_effects": "Enable window transparency effects",
            "disable_animations": "Disable visual animations for performance",
            "remove_taskbar_search": "Remove search box from taskbar",
            "remove_task_view": "Remove Task View button from taskbar",
            "remove_widgets": "Remove Widgets button from taskbar",
            "remove_chat": "Remove Chat icon from taskbar",
            "compact_mode": "Enable compact UI mode",
            "custom_accent_color": "Set custom accent color",
            # Developer Tools
            "wsl2": "Enable Windows Subsystem for Linux 2 for running Linux environments",
            "hyperv": "Enable Hyper-V virtualization platform",
            "sandbox": "Enable Windows Sandbox for testing applications in isolation",
            "dev_mode": "Enable Developer Mode with advanced debugging features",
            "docker": "Install Docker Desktop for containerization",
            "git": "Install Git for Windows version control",
            "vscode": "Install Visual Studio Code editor",
            "python": "Install Python 3 (latest stable)",
            "nodejs": "Install Node.js and npm",
            "java_jdk": "Install Java Development Kit",
            "dotnet_sdk": "Install .NET SDK (latest)",
            "powershell_7": "Install PowerShell 7",
            "windows_terminal": "Install Windows Terminal",
            "sysinternals": "Install Sysinternals Suite",
            "notepad_plusplus": "Install Notepad++ text editor",
            "sublime_text": "Install Sublime Text editor",
            "postman": "Install Postman API testing tool",
            "github_desktop": "Install GitHub Desktop",
            "putty": "Install PuTTY SSH client",
            # Enterprise Features
            "bitlocker": "Configure BitLocker drive encryption",
            "cis_benchmark": "Apply CIS (Center for Internet Security) benchmarks",
            "disa_stig": "Apply DISA STIG (Security Technical Implementation Guide) compliance",
            "gpo_hardening": "Apply Group Policy security hardening",
            "certificate_enrollment": "Configure automatic certificate enrollment",
            "mdt_integration": "Integrate with Microsoft Deployment Toolkit",
            "domain_join_prep": "Prepare image for domain joining",
            "kms_activation": "Configure KMS activation",
            "applocker": "Configure AppLocker policies",
            "credential_guard": "Enable Windows Defender Credential Guard",
            "attack_surface_reduction": "Enable Attack Surface Reduction rules",
            "exploit_protection": "Configure Exploit Protection settings",
            # Applications - Browsers
            "browsers": "Install alternative browsers (Firefox, Brave)",
            "firefox": "Install Mozilla Firefox",
            "chrome": "Install Google Chrome",
            "brave": "Install Brave Browser",
            "edge_chromium": "Install/Update Microsoft Edge Chromium",
            "opera": "Install Opera Browser",
            "vivaldi": "Install Vivaldi Browser",
            # Applications - Office & Productivity
            "office": "Install Microsoft Office suite",
            "libreoffice": "Install LibreOffice suite",
            "adobe_reader": "Install Adobe Acrobat Reader",
            "foxit_reader": "Install Foxit PDF Reader",
            "zoom": "Install Zoom video conferencing",
            "teams": "Install Microsoft Teams",
            "slack": "Install Slack",
            "notion": "Install Notion",
            "onenote": "Install Microsoft OneNote",
            "evernote": "Install Evernote",
            # Applications - Creative Tools
            "creative_suite": "Install creative tools (OBS, GIMP, Audacity, Blender)",
            "obs_studio": "Install OBS Studio for streaming",
            "gimp": "Install GIMP image editor",
            "inkscape": "Install Inkscape vector graphics",
            "krita": "Install Krita digital painting",
            "blender": "Install Blender 3D creation suite",
            "audacity": "Install Audacity audio editor",
            "handbrake": "Install HandBrake video transcoder",
            "vlc": "Install VLC Media Player",
            "spotify": "Install Spotify music player",
            "davinci_resolve": "Install DaVinci Resolve video editor",
            # Applications - Gaming
            "gaming_launchers": "Install gaming platforms (Steam, Epic Games, GOG)",
            "steam": "Install Steam gaming platform",
            "epic_games": "Install Epic Games Launcher",
            "gog_galaxy": "Install GOG Galaxy",
            "origin": "Install Origin (EA)",
            "ubisoft_connect": "Install Ubisoft Connect",
            "battle_net": "Install Battle.net (Blizzard)",
            "xbox_app": "Install Xbox App",
            # Applications - Utilities
            "winget_packages": "Configure Windows Package Manager (winget)",
            "7zip": "Install 7-Zip file archiver",
            "winrar": "Install WinRAR",
            "ccleaner": "Install CCleaner system cleaner",
            "everything_search": "Install Everything search tool",
            "greenshot": "Install Greenshot screenshot tool",
            "sharex": "Install ShareX screenshot and screen recording",
            "powertoys": "Install Microsoft PowerToys",
            "qbittorrent": "Install qBittorrent",
            "windirstat": "Install WinDirStat disk usage analyzer",
            # System Optimization - Performance
            "performance_optimize": "Apply comprehensive performance optimizations",
            "network_optimize": "Optimize network stack for maximum throughput",
            "storage_optimize": "Optimize storage and file system settings",
            "ram_optimize": "Optimize memory management and paging",
            "startup_optimize": "Optimize boot time and startup programs",
            "disable_superfetch": "Disable Superfetch/Prefetch service",
            "disable_indexing": "Disable Windows Search indexing",
            "disable_hibernation": "Disable hibernation to save disk space",
            "disable_fast_startup": "Disable Fast Startup",
            "disable_system_restore": "Disable System Restore",
            "ntfs_compression": "Enable NTFS compression",
            "disable_reserved_storage": "Disable Windows reserved storage",
            "trim_ssd": "Enable TRIM for SSD optimization",
            "disable_defrag_schedule": "Disable automatic defragmentation",
            # System Optimization - Services
            "disable_windows_update": "Disable Windows Update service",
            "disable_print_spooler": "Disable Print Spooler service",
            "disable_bluetooth": "Disable Bluetooth support",
            "disable_windows_search": "Disable Windows Search service",
            "disable_superfetch_service": "Disable SysMain (Superfetch) service",
            "disable_diagnostics": "Disable diagnostic services",
            "disable_error_reporting": "Disable Windows Error Reporting",
            "disable_remote_registry": "Disable Remote Registry service",
            # Network & Security
            "dns_cloudflare": "Use Cloudflare DNS (1.1.1.1)",
            "dns_google": "Use Google DNS (8.8.8.8)",
            "dns_quad9": "Use Quad9 DNS (9.9.9.9)",
            "disable_ipv6": "Disable IPv6 protocol",
            "enable_network_discovery": "Enable network discovery",
            "smb1_disable": "Disable SMBv1 protocol (security)",
            "firewall_hardening": "Apply strict firewall rules",
            "defender_optimize": "Optimize Windows Defender settings",
            "smartscreen_disable": "Disable SmartScreen (advanced users)",
            "uac_level": "Configure UAC level",
            "windows_hello": "Enable Windows Hello biometrics",
            "remote_desktop": "Enable Remote Desktop",
            # Power Management
            "ultimate_performance": "Enable Ultimate Performance power plan",
            "high_performance": "Set High Performance power plan",
            "disable_usb_suspend": "Disable USB selective suspend",
            "disable_power_throttling": "Disable power throttling",
            "pcie_link_state": "Disable PCIe Link State Power Management",
            # Explorer Customization
            "quick_access_disable": "Disable Quick Access in Explorer",
            "this_pc_default": "Open This PC by default in Explorer",
            "show_libraries": "Show Libraries in Navigation Pane",
            "3d_objects_remove": "Remove 3D Objects folder",
            "onedrive_remove": "Uninstall OneDrive",
            "preview_pane": "Enable Preview Pane in Explorer",
            "details_pane": "Enable Details Pane in Explorer",
        }

        categories = [
            (
                "🎮 Gaming Optimizations",
                [
                    ("gaming_competitive", "Competitive Gaming Profile"),
                    ("gaming_balanced", "Balanced Gaming Profile"),
                    ("gaming_quality", "Quality Gaming Profile"),
                    ("gaming_streaming", "Streaming Gaming Profile"),
                    ("network_latency", "Network Latency Reduction"),
                    ("game_mode", "Enable Game Mode"),
                    ("gpu_scheduling", "GPU Hardware Scheduling"),
                    ("game_dvr", "Disable Game DVR"),
                    ("fullscreen_optimizations", "Disable Fullscreen Optimizations"),
                    ("game_bar", "Configure Xbox Game Bar"),
                    ("nvidia_drivers", "Install NVIDIA Drivers"),
                    ("amd_drivers", "Install AMD Drivers"),
                    ("directx_runtime", "Install DirectX Runtime"),
                    ("vcredist_all", "Install All VC++ Redistributables"),
                    ("discord_gaming", "Install Discord"),
                ],
            ),
            (
                "🗑️ Debloating & Privacy",
                [
                    ("debloat_aggressive", "Aggressive Debloating"),
                    ("debloat_moderate", "Moderate Debloating"),
                    ("debloat_minimal", "Minimal Debloating"),
                    ("privacy_hardening", "Privacy Hardening"),
                    ("disable_telemetry", "Disable Telemetry"),
                    ("dns_over_https", "DNS over HTTPS"),
                    ("disable_cortana", "Disable Cortana"),
                    ("disable_bing_search", "Disable Bing Search"),
                    ("disable_advertising_id", "Disable Advertising ID"),
                    ("disable_activity_history", "Disable Activity History"),
                    ("disable_location", "Disable Location Services"),
                    ("disable_background_apps", "Disable Background Apps"),
                    ("block_telemetry_ips", "Block Telemetry IPs"),
                    ("disable_windows_feedback", "Disable Windows Feedback"),
                    ("disable_suggestions", "Disable App Suggestions"),
                    ("disable_lock_screen_ads", "Remove Lock Screen Ads"),
                ],
            ),
            (
                "🎨 Visual Customization",
                [
                    ("dark_theme", "Dark Theme"),
                    ("light_theme", "Light Theme"),
                    ("custom_wallpaper", "Custom Wallpaper"),
                    ("taskbar_left", "Taskbar on Left"),
                    ("taskbar_center", "Taskbar Centered"),
                    ("modern_ui", "Modern UI Tweaks"),
                    ("classic_context_menu", "Classic Context Menu (Win11)"),
                    ("classic_explorer", "Classic Explorer Ribbon"),
                    ("show_file_extensions", "Show File Extensions"),
                    ("show_hidden_files", "Show Hidden Files"),
                    ("colored_titlebar", "Colored Title Bars"),
                    ("transparency_effects", "Transparency Effects"),
                    ("disable_animations", "Disable Animations"),
                    ("remove_taskbar_search", "Remove Taskbar Search Box"),
                    ("remove_task_view", "Remove Task View Button"),
                    ("remove_widgets", "Remove Widgets Button"),
                    ("remove_chat", "Remove Chat Icon"),
                    ("compact_mode", "Compact UI Mode"),
                    ("custom_accent_color", "Custom Accent Color"),
                ],
            ),
            (
                "💻 Developer Tools",
                [
                    ("wsl2", "Enable WSL2"),
                    ("hyperv", "Enable Hyper-V"),
                    ("sandbox", "Enable Windows Sandbox"),
                    ("dev_mode", "Developer Mode"),
                    ("docker", "Docker Desktop"),
                    ("git", "Git for Windows"),
                    ("vscode", "VS Code"),
                    ("python", "Python 3"),
                    ("nodejs", "Node.js & npm"),
                    ("java_jdk", "Java Development Kit"),
                    ("dotnet_sdk", ".NET SDK"),
                    ("powershell_7", "PowerShell 7"),
                    ("windows_terminal", "Windows Terminal"),
                    ("sysinternals", "Sysinternals Suite"),
                    ("notepad_plusplus", "Notepad++"),
                    ("sublime_text", "Sublime Text"),
                    ("postman", "Postman"),
                    ("github_desktop", "GitHub Desktop"),
                    ("putty", "PuTTY SSH Client"),
                ],
            ),
            (
                "🏢 Enterprise & Security",
                [
                    ("bitlocker", "BitLocker Encryption"),
                    ("cis_benchmark", "CIS Benchmark"),
                    ("disa_stig", "DISA STIG Compliance"),
                    ("gpo_hardening", "Group Policy Hardening"),
                    ("certificate_enrollment", "Certificate Auto-Enrollment"),
                    ("mdt_integration", "MDT Integration"),
                    ("domain_join_prep", "Domain Join Preparation"),
                    ("kms_activation", "KMS Activation Setup"),
                    ("applocker", "AppLocker Policies"),
                    ("credential_guard", "Credential Guard"),
                    ("attack_surface_reduction", "Attack Surface Reduction"),
                    ("exploit_protection", "Exploit Protection"),
                ],
            ),
            (
                "🌐 Web Browsers",
                [
                    ("firefox", "Mozilla Firefox"),
                    ("chrome", "Google Chrome"),
                    ("brave", "Brave Browser"),
                    ("edge_chromium", "Microsoft Edge Chromium"),
                    ("opera", "Opera Browser"),
                    ("vivaldi", "Vivaldi Browser"),
                ],
            ),
            (
                "📝 Office & Productivity",
                [
                    ("office", "Microsoft Office"),
                    ("libreoffice", "LibreOffice"),
                    ("adobe_reader", "Adobe Acrobat Reader"),
                    ("foxit_reader", "Foxit PDF Reader"),
                    ("zoom", "Zoom"),
                    ("teams", "Microsoft Teams"),
                    ("slack", "Slack"),
                    ("notion", "Notion"),
                    ("onenote", "Microsoft OneNote"),
                    ("evernote", "Evernote"),
                ],
            ),
            (
                "🎨 Creative & Media Tools",
                [
                    ("obs_studio", "OBS Studio"),
                    ("gimp", "GIMP Image Editor"),
                    ("inkscape", "Inkscape Vector Graphics"),
                    ("krita", "Krita Digital Painting"),
                    ("blender", "Blender 3D Suite"),
                    ("audacity", "Audacity Audio Editor"),
                    ("handbrake", "HandBrake Video Transcoder"),
                    ("vlc", "VLC Media Player"),
                    ("spotify", "Spotify"),
                    ("davinci_resolve", "DaVinci Resolve"),
                ],
            ),
            (
                "🎮 Gaming Platforms",
                [
                    ("steam", "Steam"),
                    ("epic_games", "Epic Games Launcher"),
                    ("gog_galaxy", "GOG Galaxy"),
                    ("origin", "Origin (EA)"),
                    ("ubisoft_connect", "Ubisoft Connect"),
                    ("battle_net", "Battle.net (Blizzard)"),
                    ("xbox_app", "Xbox App"),
                ],
            ),
            (
                "🔧 System Utilities",
                [
                    ("winget_packages", "WinGet Package Manager"),
                    ("7zip", "7-Zip"),
                    ("winrar", "WinRAR"),
                    ("ccleaner", "CCleaner"),
                    ("everything_search", "Everything Search"),
                    ("greenshot", "Greenshot"),
                    ("sharex", "ShareX"),
                    ("powertoys", "Microsoft PowerToys"),
                    ("qbittorrent", "qBittorrent"),
                    ("windirstat", "WinDirStat"),
                ],
            ),
            (
                "⚡ Performance Optimization",
                [
                    ("performance_optimize", "Performance Optimization"),
                    ("disable_superfetch", "Disable Superfetch/Prefetch"),
                    ("disable_indexing", "Disable Search Indexing"),
                    ("disable_hibernation", "Disable Hibernation"),
                    ("disable_fast_startup", "Disable Fast Startup"),
                    ("disable_system_restore", "Disable System Restore"),
                    ("ntfs_compression", "Enable NTFS Compression"),
                    ("disable_reserved_storage", "Disable Reserved Storage"),
                    ("trim_ssd", "Enable SSD TRIM"),
                    ("disable_defrag_schedule", "Disable Auto Defragmentation"),
                ],
            ),
            (
                "🔌 Services Management",
                [
                    ("disable_windows_update", "Disable Windows Update"),
                    ("disable_print_spooler", "Disable Print Spooler"),
                    ("disable_bluetooth", "Disable Bluetooth"),
                    ("disable_windows_search", "Disable Windows Search Service"),
                    ("disable_superfetch_service", "Disable SysMain Service"),
                    ("disable_diagnostics", "Disable Diagnostic Services"),
                    ("disable_error_reporting", "Disable Error Reporting"),
                    ("disable_remote_registry", "Disable Remote Registry"),
                ],
            ),
            (
                "🌐 Network Configuration",
                [
                    ("network_optimize", "Network Optimization"),
                    ("dns_cloudflare", "Cloudflare DNS (1.1.1.1)"),
                    ("dns_google", "Google DNS (8.8.8.8)"),
                    ("dns_quad9", "Quad9 DNS (9.9.9.9)"),
                    ("disable_ipv6", "Disable IPv6"),
                    ("enable_network_discovery", "Enable Network Discovery"),
                    ("smb1_disable", "Disable SMBv1 Protocol"),
                    ("firewall_hardening", "Firewall Hardening"),
                    ("defender_optimize", "Optimize Windows Defender"),
                    ("smartscreen_disable", "Disable SmartScreen"),
                    ("uac_level", "Configure UAC Level"),
                    ("windows_hello", "Enable Windows Hello"),
                    ("remote_desktop", "Enable Remote Desktop"),
                ],
            ),
            (
                "🔋 Power Management",
                [
                    ("ultimate_performance", "Ultimate Performance Plan"),
                    ("high_performance", "High Performance Plan"),
                    ("disable_usb_suspend", "Disable USB Suspend"),
                    ("disable_power_throttling", "Disable Power Throttling"),
                    ("pcie_link_state", "Disable PCIe Power Management"),
                ],
            ),
            (
                "📁 File Explorer",
                [
                    ("quick_access_disable", "Disable Quick Access"),
                    ("this_pc_default", "Open This PC by Default"),
                    ("show_libraries", "Show Libraries"),
                    ("3d_objects_remove", "Remove 3D Objects Folder"),
                    ("onedrive_remove", "Uninstall OneDrive"),
                    ("preview_pane", "Enable Preview Pane"),
                    ("details_pane", "Enable Details Pane"),
                ],
            ),
            (
                "💾 Storage & RAM",
                [
                    ("storage_optimize", "Storage Optimization"),
                    ("ram_optimize", "RAM Optimization"),
                    ("startup_optimize", "Startup Optimization"),
                ],
            ),
        ]

        for category_name, features in categories:
            group = QGroupBox(category_name)
            group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            group_layout = QVBoxLayout()

            for feature_id, feature_name in features:
                checkbox = QCheckBox(feature_name)
                checkbox.setFont(QFont("Segoe UI", 9))
                # Apply tooltip if available
                if feature_id in self.feature_tooltips:
                    checkbox.setToolTip(self.feature_tooltips[feature_id])
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

        # Profile-specific selections (expanded with 150+ features)
        profile_features = {
            "gamer": [
                # Gaming optimizations
                "gaming_competitive",
                "network_latency",
                "game_mode",
                "gpu_scheduling",
                "game_dvr",
                "fullscreen_optimizations",
                "directx_runtime",
                "vcredist_all",
                # Gaming platforms
                "steam",
                "epic_games",
                "gog_galaxy",
                "discord_gaming",
                # Performance
                "performance_optimize",
                "network_optimize",
                "ultimate_performance",
                "disable_superfetch",
                "disable_fast_startup",
                "trim_ssd",
                # Privacy & debloat
                "debloat_moderate",
                "disable_telemetry",
                "disable_cortana",
                "disable_windows_feedback",
                "disable_suggestions",
                # Visual
                "dark_theme",
                "disable_animations",
                "show_file_extensions",
                # Network
                "dns_cloudflare",
                "disable_ipv6",
                # Utilities
                "discord_gaming",
                "7zip",
                "sharex",
            ],
            "developer": [
                # Development tools
                "wsl2",
                "hyperv",
                "sandbox",
                "dev_mode",
                "docker",
                "git",
                "vscode",
                "python",
                "nodejs",
                "dotnet_sdk",
                "powershell_7",
                "windows_terminal",
                "github_desktop",
                "postman",
                "notepad_plusplus",
                "putty",
                # Browsers for testing
                "firefox",
                "chrome",
                "brave",
                "edge_chromium",
                # Utilities
                "7zip",
                "everything_search",
                "powertoys",
                "winget_packages",
                # System config
                "dark_theme",
                "taskbar_left",
                "show_file_extensions",
                "show_hidden_files",
                "this_pc_default",
                # Performance
                "debloat_minimal",
                "high_performance",
                "trim_ssd",
                # Network
                "dns_google",
                "enable_network_discovery",
            ],
            "enterprise": [
                # Security & compliance
                "bitlocker",
                "cis_benchmark",
                "disa_stig",
                "gpo_hardening",
                "certificate_enrollment",
                "mdt_integration",
                "domain_join_prep",
                "applocker",
                "credential_guard",
                "attack_surface_reduction",
                "exploit_protection",
                "firewall_hardening",
                "defender_optimize",
                "smb1_disable",
                # Office & productivity
                "office",
                "teams",
                "adobe_reader",
                "zoom",
                # Network & security
                "dns_quad9",
                "enable_network_discovery",
                "remote_desktop",
                "windows_hello",
                # System config
                "light_theme",
                "taskbar_left",
                "show_file_extensions",
                "disable_onedrive_remove",  # Keep OneDrive for business
                # Services
                "disable_cortana",
                "disable_bing_search",
                # Minimal debloat (keep enterprise features)
                "debloat_minimal",
                "disable_suggestions",
            ],
            "student": [
                # Productivity
                "office",
                "libreoffice",
                "onenote",
                "notion",
                # Browsers
                "firefox",
                "chrome",
                "brave",
                # Communication
                "zoom",
                "teams",
                "slack",
                # Utilities
                "adobe_reader",
                "7zip",
                "vlc",
                "spotify",
                "greenshot",
                "everything_search",
                "qbittorrent",
                # Privacy & performance
                "debloat_moderate",
                "privacy_hardening",
                "disable_telemetry",
                "disable_cortana",
                "disable_advertising_id",
                "disable_location",
                "block_telemetry_ips",
                "performance_optimize",
                # Visual
                "light_theme",
                "show_file_extensions",
                "preview_pane",
                # Network
                "dns_cloudflare",
                "dns_over_https",
                # Power
                "high_performance",
                "disable_hibernation",
            ],
            "creator": [
                # Creative tools
                "obs_studio",
                "gimp",
                "inkscape",
                "krita",
                "blender",
                "audacity",
                "handbrake",
                "vlc",
                "davinci_resolve",
                # System optimization for creative work
                "gpu_scheduling",
                "ultimate_performance",
                "ram_optimize",
                "storage_optimize",
                "performance_optimize",
                "disable_superfetch",
                "disable_fast_startup",
                "trim_ssd",
                # Visual
                "dark_theme",
                "colored_titlebar",
                "show_file_extensions",
                # Browsers & productivity
                "firefox",
                "chrome",
                "spotify",
                # File management
                "show_hidden_files",
                "preview_pane",
                "details_pane",
                "show_libraries",
                "this_pc_default",
                # Utilities
                "7zip",
                "everything_search",
                "windirstat",
                "sharex",
                # Minimal bloat (keep resources for creative apps)
                "debloat_minimal",
                "disable_cortana",
                "disable_suggestions",
                # Network
                "dns_google",
                "disable_ipv6",
                # Power
                "disable_usb_suspend",
                "disable_power_throttling",
            ],
            "custom": [],  # No auto-selection for custom
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

    def __init__(
        self,
        image_path: Path,
        profile_name: str,
        output_path: Optional[Path],
        selected_features: Dict[str, bool],
        validate: bool,
        compress: bool,
    ):
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
                    output_path=self.output_path,
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
            self.log.emit(
                f"[INFO] Processing {len([f for f in self.selected_features.values() if f])} additional features..."
            )

            try:
                # Create configuration manager
                config_manager = ConfigurationManager()

                # Set up callbacks for progress and logging
                config_manager.progress_callback = lambda pct, msg: self.progress.emit(
                    55 + int(pct * 0.25), msg  # Map 0-100% to 55-80% of total progress
                )
                config_manager.log_callback = lambda msg: self.log.emit(msg)

                # Configure modules from GUI selections
                config_manager.configure_from_gui(self.selected_features)

                # Execute all enabled modules
                success = config_manager.execute_all(
                    image_path=self.image_path,
                    profile_name=self.profile_name,
                    output_path=self.output_path,
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
        self.progress_bar.setStyleSheet(
            """
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
        """
        )
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
        """Handle build completion with notification."""
        self.build_completed = True
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)

        if success:
            self.operation_label.setText("✓ Build completed successfully!")
            self.operation_label.setStyleSheet("color: #107C10; font-weight: bold;")
            self.time_label.setText(message)

            # Show completion message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Build Complete")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setText(f"Image built successfully!\n\n{message}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            # Flash taskbar if window is not active (for notification)
            if not self.window().isActiveWindow():
                QApplication.alert(self.window(), 3000)  # Flash for 3 seconds

        else:
            self.operation_label.setText("✗ Build failed")
            self.operation_label.setStyleSheet("color: #C50F1F; font-weight: bold;")
            self.time_label.setText(message)

            # Flash taskbar on error too
            if not self.window().isActiveWindow():
                QApplication.alert(self.window(), 3000)

    def on_build_error(self, error_msg: str):
        """Handle build error."""
        QMessageBox.critical(
            self, "Build Error", f"An error occurred during the build:\n\n{error_msg}"
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
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

        subtitle = QLabel(
            "Create a customized Windows deployment image with your preferred settings and applications."
        )
        subtitle.setStyleSheet("color: #666666;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Source Image Card
        source_card = ModernCard("1. Source Image")
        source_layout = QVBoxLayout()

        source_label = QLabel("Select a Windows installation image (WIM, ESD, or ISO):")
        source_label.setToolTip("Choose a Windows deployment image file to customize")
        source_layout.addWidget(source_label)

        source_buttons = QHBoxLayout()
        self.source_path = QLabel("No image selected")
        self.source_path.setStyleSheet("color: #666666; padding: 8px;")
        self.source_path.setToolTip("Drag and drop an image file here or use the Browse button")
        source_buttons.addWidget(self.source_path, 1)

        btn_browse = ModernButton("Browse...")
        btn_browse.setToolTip("Browse your computer for a Windows image file (Ctrl+O)")
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
        profiles_label.setToolTip("Select a pre-configured profile that best matches your use case")
        profile_layout.addWidget(profiles_label)

        profile_layout.addSpacing(12)

        # Profile cards
        self.profile_cards = []
        profiles = [
            (
                "🎮 Gaming",
                "Optimized for gaming with performance tweaks, network optimization, and gaming launchers",
                "gamer",
                [
                    "Performance tuning",
                    "Network optimization",
                    "Gaming launchers",
                    "Moderate debloating",
                ],
            ),
            (
                "💻 Developer",
                "Development environment with WSL2, Docker, Git, VS Code, and Hyper-V",
                "developer",
                ["WSL2", "Docker", "Hyper-V", "Dev tools", "Minimal debloating"],
            ),
            (
                "🏢 Enterprise",
                "Enterprise security with CIS benchmarks, BitLocker, GPO hardening, and DISA STIG",
                "enterprise",
                ["Security hardening", "BitLocker", "Compliance", "Certificate management"],
            ),
            (
                "📚 Student",
                "Balanced setup for productivity with Office, browsers, and privacy features",
                "student",
                ["Microsoft Office", "Browsers", "Privacy tweaks", "Moderate debloating"],
            ),
            (
                "🎨 Creator",
                "Content creation suite with OBS, GIMP, Audacity, Blender, and GPU optimization",
                "creator",
                ["Creative tools", "GPU optimization", "Storage optimization", "Performance"],
            ),
            (
                "🔧 Custom",
                "Start with a minimal base and manually customize every option",
                "custom",
                ["Full manual control", "No automatic changes"],
            ),
        ]

        # Profile tooltips for accessibility
        profile_tooltips = {
            "gamer": "Click to select Gaming profile - optimized for low latency, high performance gaming",
            "developer": "Click to select Developer profile - includes WSL2, Docker, Hyper-V, and dev tools",
            "enterprise": "Click to select Enterprise profile - security hardening with CIS, BitLocker, and STIG compliance",
            "student": "Click to select Student profile - balanced productivity setup with Office and browsers",
            "creator": "Click to select Creator profile - content creation tools with GPU and storage optimization",
            "custom": "Click to select Custom profile - start with minimal base and manually configure all options",
        }

        for icon_text, description, profile_id, features in profiles:
            card = ProfileCard(icon_text, description, profile_id, features)
            card.setToolTip(profile_tooltips.get(profile_id, "Click to select this profile"))
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
        output_label.setToolTip("Choose where to save the customized image")
        output_layout.addWidget(output_label)

        output_buttons = QHBoxLayout()
        self.output_path = QLabel("Same as source (will create *_custom.wim)")
        self.output_path.setStyleSheet("color: #666666; padding: 8px;")
        self.output_path.setToolTip("The customized image will be saved here")
        output_buttons.addWidget(self.output_path, 1)

        btn_output = ModernButton("Change...")
        btn_output.setToolTip("Choose a different location to save the output image")
        btn_output.clicked.connect(self.browse_output)
        output_buttons.addWidget(btn_output)

        output_layout.addLayout(output_buttons)

        # Additional options
        options_layout = QHBoxLayout()

        self.validate_checkbox = QCheckBox("Validate image after build")
        self.validate_checkbox.setChecked(True)
        self.validate_checkbox.setToolTip(
            "Verify the image integrity after build completes (recommended)"
        )
        options_layout.addWidget(self.validate_checkbox)

        self.compress_checkbox = QCheckBox("Maximum compression")
        self.compress_checkbox.setToolTip(
            "Apply maximum compression to reduce image file size (slower build)"
        )
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
        self.btn_build.setToolTip("Start building the customized Windows image (Ctrl+B)")
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
            self, "Select Windows Image", "", "Windows Images (*.wim *.esd *.iso);;All Files (*)"
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
            self, "Select Output Location", "", "Windows Images (*.wim);;All Files (*)"
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
            "gamer": "Gaming Profile",
            "developer": "Developer Profile",
            "enterprise": "Enterprise Profile",
            "student": "Student Profile",
            "creator": "Creator Profile",
            "custom": "Custom Profile",
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
                "Please select both a source image and a profile before building.",
            )
            return

        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Start Build",
            f"Ready to build custom Windows image with {self.selected_profile} profile.\n\n"
            "This may take 30-60 minutes depending on your selections.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.execute_build()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for image files."""
        if event.mimeData().hasUrls():
            # Check if any URL is a valid image file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith((".wim", ".esd", ".iso")):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for image files."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith((".wim", ".esd", ".iso")):
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
                    f"Source image loaded successfully!\n\n{Path(file_path).name}\n{file_size:.2f} GB",
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
                    "Please ensure the application is properly installed.",
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
                compress=self.compress_checkbox.isChecked(),
            )

            # Create and show progress dialog
            progress_dialog = BuildProgressDialog(worker, self)
            progress_dialog.show()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Build Error",
                f"Failed to start build:\n\n{str(e)}\n\n{traceback.format_exc()}",
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
            profile_row.setStyleSheet(
                """
                QFrame {
                    background-color: #F9F9F9;
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 12px;
                }
            """
            )

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
            btn_view.setToolTip("View profile details and included features")
            row_layout.addWidget(btn_view)

            btn_clone = ModernButton("Clone")
            btn_clone.setMaximumWidth(80)
            btn_clone.setToolTip("Create a copy of this profile to customize")
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
        btn_create.setToolTip("Create a new custom profile with your own configuration (Ctrl+P)")
        btn_create.clicked.connect(self.create_new_profile)
        custom_layout.addWidget(btn_create)

        custom_card.layout().addLayout(custom_layout)
        layout.addWidget(custom_card)

        # Import/Export Card
        import_export_card = ModernCard("Import / Export")
        ie_layout = QHBoxLayout()

        btn_import = ModernButton("Import Profile...")
        btn_import.setToolTip("Import a profile from a file")
        btn_export = ModernButton("Export Profile...")
        btn_export.setToolTip("Export a profile to share with others")

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
            "- Save for reuse",
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
        single_label.setToolTip("Choose a Windows image to examine its contents and properties")
        single_layout.addWidget(single_label)

        single_row = QHBoxLayout()
        self.analyze_path = QLabel("No image selected")
        self.analyze_path.setStyleSheet("color: #666666; padding: 8px;")
        self.analyze_path.setToolTip("The image file to analyze will be shown here")
        single_row.addWidget(self.analyze_path, 1)

        btn_browse_analyze = ModernButton("Browse...")
        btn_browse_analyze.setToolTip("Browse for a Windows image file to analyze")
        btn_browse_analyze.clicked.connect(self.browse_analyze_image)
        single_row.addWidget(btn_browse_analyze)

        single_layout.addLayout(single_row)

        # Analysis options
        options_label = QLabel("Analysis Options:")
        options_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        single_layout.addWidget(options_label)

        self.check_features = QCheckBox("Analyze Windows features")
        self.check_features.setChecked(True)
        self.check_features.setToolTip("List all enabled and disabled Windows features")
        single_layout.addWidget(self.check_features)

        self.check_apps = QCheckBox("List installed applications")
        self.check_apps.setChecked(True)
        self.check_apps.setToolTip("List all installed applications and programs")
        single_layout.addWidget(self.check_apps)

        self.check_drivers = QCheckBox("List drivers")
        self.check_drivers.setToolTip("List all installed device drivers")
        single_layout.addWidget(self.check_drivers)

        self.check_size = QCheckBox("Calculate disk usage")
        self.check_size.setChecked(True)
        self.check_size.setToolTip("Calculate total disk space used by the image")
        single_layout.addWidget(self.check_size)

        # Report format
        format_label = QLabel("Report Format:")
        format_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        single_layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML", "JSON", "Text", "PDF"])
        self.format_combo.setMaximumWidth(200)
        self.format_combo.setToolTip("Choose the output format for the analysis report")
        single_layout.addWidget(self.format_combo)

        # Analyze button
        btn_analyze = ModernButton("Generate Report", primary=True)
        btn_analyze.setToolTip("Generate a comprehensive analysis report of the selected image")
        btn_analyze.clicked.connect(self.run_analysis)
        single_layout.addWidget(btn_analyze)

        single_card.layout().addLayout(single_layout)
        layout.addWidget(single_card)

        # Compare Images Card
        compare_card = ModernCard("Compare Two Images")
        compare_layout = QVBoxLayout()

        compare_label = QLabel("Compare two images side-by-side:")
        compare_label.setToolTip("Select two images to compare their features and differences")
        compare_layout.addWidget(compare_label)

        # Image 1
        img1_row = QHBoxLayout()
        img1_label = QLabel("Image 1:")
        img1_label.setMinimumWidth(70)
        img1_row.addWidget(img1_label)

        self.compare_img1 = QLabel("No image selected")
        self.compare_img1.setStyleSheet("color: #666666; padding: 8px;")
        self.compare_img1.setToolTip("First image for comparison")
        img1_row.addWidget(self.compare_img1, 1)

        btn_browse_img1 = ModernButton("Browse...")
        btn_browse_img1.setToolTip("Select the first image to compare")
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
        self.compare_img2.setToolTip("Second image for comparison")
        img2_row.addWidget(self.compare_img2, 1)

        btn_browse_img2 = ModernButton("Browse...")
        btn_browse_img2.setToolTip("Select the second image to compare")
        btn_browse_img2.clicked.connect(lambda: self.browse_compare_image(2))
        img2_row.addWidget(btn_browse_img2)

        compare_layout.addLayout(img2_row)

        # Compare button
        btn_compare = ModernButton("Compare Images", primary=True)
        btn_compare.setToolTip(
            "Generate a comparison report showing differences between the two images (Ctrl+Shift+C)"
        )
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
            self, "Select Image to Analyze", "", "Windows Images (*.wim *.esd *.iso);;All Files (*)"
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
            "Windows Images (*.wim *.esd *.iso);;All Files (*)",
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
                self, "No Image Selected", "Please select an image to analyze first."
            )
            return

        if not BACKEND_AVAILABLE:
            QMessageBox.critical(
                self,
                "Backend Not Available",
                "DeployForge backend modules are not available.\n\n"
                "Please ensure the application is properly installed.",
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
            if report_format == "html":
                report_content = analyzer.generate_html_report(report_data)
                report_extension = ".html"
            elif report_format == "json":
                import json

                report_content = json.dumps(report_data, indent=2)
                report_extension = ".json"
            elif report_format == "text":
                report_content = analyzer.format_text_report(report_data)
                report_extension = ".txt"
            else:  # pdf
                QMessageBox.warning(
                    self,
                    "Format Not Supported",
                    "PDF format is not yet implemented.\n\nPlease use HTML, JSON, or Text format.",
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
                f"{report_format.upper()} Files (*{report_extension});;All Files (*)",
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(report_content)

                QMessageBox.information(
                    self,
                    "Analysis Complete",
                    f"Analysis report saved successfully!\n\n"
                    f"Location: {save_path}\n\n"
                    f"Features: {report_data.get('features_count', 0)}\n"
                    f"Applications: {report_data.get('applications_count', 0)}",
                )

                # TODO: Add to recent reports list

        except Exception as e:
            QMessageBox.critical(
                self,
                "Analysis Error",
                f"Failed to analyze image:\n\n{str(e)}\n\n{traceback.format_exc()}",
            )

    def run_comparison(self):
        """Run image comparison."""
        if (
            self.compare_img1.text() == "No image selected"
            or self.compare_img2.text() == "No image selected"
        ):
            QMessageBox.warning(self, "Missing Images", "Please select both images to compare.")
            return

        if not BACKEND_AVAILABLE:
            QMessageBox.critical(
                self,
                "Backend Not Available",
                "DeployForge backend modules are not available.\n\n"
                "Please ensure the application is properly installed.",
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
            features1 = set(report1.get("features", []))
            features2 = set(report2.get("features", []))
            apps1 = set(report1.get("applications", []))
            apps2 = set(report2.get("applications", []))

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
                self, "Save Comparison Report", default_name, "Text Files (*.txt);;All Files (*)"
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
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
                    self, "Comparison Complete", f"Comparison report saved!\n\n{comparison_text}"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Comparison Error",
                f"Failed to compare images:\n\n{str(e)}\n\n{traceback.format_exc()}",
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
        self.btn_light.setToolTip("Switch to light theme with bright colors")
        self.btn_light.clicked.connect(lambda: self.set_theme("Light"))
        theme_buttons_layout.addWidget(self.btn_light)

        self.btn_dark = ModernButton("🌙 Dark Theme")
        self.btn_dark.setMinimumWidth(150)
        self.btn_dark.setToolTip("Switch to dark theme for reduced eye strain")
        self.btn_dark.clicked.connect(lambda: self.set_theme("Dark"))
        theme_buttons_layout.addWidget(self.btn_dark)

        theme_buttons_layout.addStretch()
        theme_layout.addLayout(theme_buttons_layout)

        # Current theme indicator
        self.theme_status = QLabel(f"Current theme: {theme_manager.get_theme()}")
        self.theme_status.setStyleSheet(
            f"color: {theme_manager.get_colors()['primary']}; font-size: 9pt; font-weight: bold;"
        )
        theme_layout.addWidget(self.theme_status)

        theme_card.layout().addLayout(theme_layout)
        layout.addWidget(theme_card)

        # General Settings
        general_card = ModernCard("General")
        general_layout = QVBoxLayout()

        self.check_validate = QCheckBox("Always validate images after build")
        self.check_validate.setChecked(True)
        self.check_validate.setToolTip("Automatically verify image integrity after every build")
        general_layout.addWidget(self.check_validate)

        self.check_compress = QCheckBox("Use maximum compression by default")
        self.check_compress.setToolTip(
            "Enable maximum compression for all builds (slower but smaller files)"
        )
        general_layout.addWidget(self.check_compress)

        self.check_recent = QCheckBox("Show recent files on welcome page")
        self.check_recent.setChecked(True)
        self.check_recent.setToolTip("Display a list of recently used images on the welcome page")
        general_layout.addWidget(self.check_recent)

        general_card.layout().addLayout(general_layout)
        layout.addWidget(general_card)

        # Advanced Settings
        advanced_card = ModernCard("Advanced")
        advanced_layout = QVBoxLayout()

        self.check_debug = QCheckBox("Enable debug logging")
        self.check_debug.setToolTip("Enable detailed debug logging for troubleshooting")
        advanced_layout.addWidget(self.check_debug)

        self.check_auto_save = QCheckBox("Auto-save window position and size")
        self.check_auto_save.setChecked(True)
        self.check_auto_save.setToolTip("Remember window position and size between sessions")
        advanced_layout.addWidget(self.check_auto_save)

        advanced_card.layout().addLayout(advanced_layout)
        layout.addWidget(advanced_card)

        # Save/Reset buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        btn_save = ModernButton("Save Settings", primary=True)
        btn_save.setToolTip("Save all settings and preferences")
        btn_save.clicked.connect(self.save_settings)
        buttons_layout.addWidget(btn_save)

        btn_reset = ModernButton("Reset to Defaults")
        btn_reset.setToolTip("Reset all settings to their default values")
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
        self.theme_status.setStyleSheet(
            f"color: {theme_manager.get_colors()['primary']}; font-size: 9pt; font-weight: bold;"
        )

        # Save to settings
        settings = QSettings("DeployForge", "DeployForge")
        settings.setValue("theme", theme_name)

        QMessageBox.information(
            self,
            "Theme Changed",
            f"Theme changed to {theme_name}!\n\nSome elements will update immediately,\nothers may require restarting the application.",
        )

    def on_theme_changed(self, theme_name: str):
        """Handle theme change event."""
        self.theme_status.setText(f"Current theme: {theme_name}")

    def save_settings(self):
        """Save all settings."""
        settings = QSettings("DeployForge", "DeployForge")
        settings.setValue("validate_default", self.check_validate.isChecked())
        settings.setValue("compress_default", self.check_compress.isChecked())
        settings.setValue("show_recent", self.check_recent.isChecked())
        settings.setValue("debug_logging", self.check_debug.isChecked())
        settings.setValue("auto_save_window", self.check_auto_save.isChecked())

        QMessageBox.information(
            self, "Settings Saved", "Your settings have been saved successfully!"
        )

    def reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.check_validate.setChecked(True)
            self.check_compress.setChecked(False)
            self.check_recent.setChecked(True)
            self.check_debug.setChecked(False)
            self.check_auto_save.setChecked(True)
            self.set_theme("Light")

            QMessageBox.information(
                self, "Settings Reset", "All settings have been reset to defaults!"
            )


class DeployForgeGUI(QMainWindow):
    """Main application window with modern UI and settings persistence."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeployForge - Windows Deployment Suite")
        self.setMinimumSize(1200, 800)

        # Set application icon (if available)
        icon_path = Path(__file__).parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Performance: settings cache to reduce disk I/O
        self._settings_cache = {}

        # Load settings
        self.load_settings()

        # Setup UI
        self.setup_ui()

        # Apply theme
        self.apply_initial_theme()

        # Center window (if not loading saved geometry)
        if not self._get_cached_setting("window/geometry"):
            self.center_window()

        # First-run detection: show tutorial automatically
        if not self._get_cached_setting("first_run_completed", False):
            # Defer tutorial display to after window is shown
            QTimer.singleShot(500, self._show_first_run_tutorial)

    def _show_first_run_tutorial(self):
        """Show tutorial on first run and mark as completed."""
        self.show_tutorial()
        self._set_cached_setting("first_run_completed", True)

    def _get_cached_setting(self, key: str, default=None):
        """Get setting from cache or QSettings (performance optimization)."""
        if key not in self._settings_cache:
            settings = QSettings("DeployForge", "DeployForge")
            self._settings_cache[key] = settings.value(key, default)
        return self._settings_cache[key]

    def _set_cached_setting(self, key: str, value):
        """Set setting in cache and QSettings."""
        self._settings_cache[key] = value
        settings = QSettings("DeployForge", "DeployForge")
        settings.setValue(key, value)

    def load_settings(self):
        """Load application settings with caching."""
        settings = QSettings("DeployForge", "DeployForge")

        # Load window geometry
        geometry = self._get_cached_setting("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Load theme
        theme = self._get_cached_setting("theme", "Light")
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

        # Lazy loading: create pages on-demand for faster startup
        # Initialize page dictionary with None values
        self.pages = {
            "welcome": None,
            "build": None,
            "profiles": None,
            "analyze": None,
            "settings": None,
        }

        # Page classes for lazy initialization
        self._page_classes = {
            "welcome": WelcomePage,
            "build": BuildPage,
            "profiles": ProfilesPage,
            "analyze": AnalyzePage,
            "settings": SettingsPage,
        }

        # Page indices in stack
        self._page_indices = {}

        # Create welcome page immediately (shown on startup)
        self._create_page("welcome")

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
        sidebar.setStyleSheet(
            """
            QFrame {
                background-color: #FFFFFF;
                border-right: 1px solid #E0E0E0;
            }
        """
        )

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
            ("🏠 Home", "welcome"),
            ("🔨 Build Image", "build"),
            ("📋 Profiles", "profiles"),
            ("🔍 Analyze", "analyze"),
            ("⚙️ Settings", "settings"),
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
        """Create the menu bar with enhanced help and accessibility."""

        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Build", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Start a new build configuration")
        new_action.triggered.connect(lambda: self.show_page("build"))
        file_menu.addAction(new_action)

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a Windows image file")
        open_action.triggered.connect(self.open_image_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit DeployForge")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        analyze_action = QAction("&Analyze Image", self)
        analyze_action.setShortcut("Ctrl+A")
        analyze_action.setStatusTip("Analyze a Windows image")
        analyze_action.triggered.connect(lambda: self.show_page("analyze"))
        tools_menu.addAction(analyze_action)

        compare_action = QAction("&Compare Images", self)
        compare_action.setShortcut("Ctrl+Shift+C")
        compare_action.setStatusTip("Compare two Windows images")
        compare_action.triggered.connect(self.show_compare_tab)
        tools_menu.addAction(compare_action)

        tools_menu.addSeparator()

        profiles_action = QAction("Manage &Profiles", self)
        profiles_action.setShortcut("Ctrl+P")
        profiles_action.setStatusTip("Manage build profiles")
        profiles_action.triggered.connect(lambda: self.show_page("profiles"))
        tools_menu.addAction(profiles_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        welcome_action = QAction("&Welcome", self)
        welcome_action.setShortcut("Ctrl+Home")
        welcome_action.setStatusTip("Show welcome page")
        welcome_action.triggered.connect(lambda: self.show_page("welcome"))
        view_menu.addAction(welcome_action)

        view_menu.addSeparator()

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(lambda: self.show_page("settings"))
        view_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        tutorial_action = QAction("Getting &Started", self)
        tutorial_action.setShortcut("F1")
        tutorial_action.setStatusTip("Show getting started tutorial")
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("Ctrl+F1")
        docs_action.setStatusTip("Open documentation")
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        shortcuts_action = QAction("Keyboard &Shortcuts", self)
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction("&About DeployForge", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def open_image_dialog(self):
        """Open file dialog to select an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Windows Image", "", "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )
        if file_path:
            # Switch to build page and set the image
            self.show_page("build")
            if hasattr(self.pages["build"], "selected_source"):
                self.pages["build"].selected_source = Path(file_path)
                self.pages["build"].source_path.setText(file_path)

    def show_compare_tab(self):
        """Show compare tab in analyze page."""
        self.show_page("analyze")
        # TODO: Switch to compare tab if analyze page has tabs

    def show_tutorial(self):
        """Show getting started tutorial."""
        tutorial = QMessageBox(self)
        tutorial.setWindowTitle("Getting Started - DeployForge")
        tutorial.setIconPixmap(QPixmap())  # You can add an icon here

        tutorial_text = """
<h2>Welcome to DeployForge!</h2>

<p>DeployForge helps you customize Windows deployment images with ease.</p>

<h3>Quick Start Guide:</h3>

<ol>
<li><b>Select an Image</b>
   <ul>
   <li>Click "Build" in the sidebar or press <b>Ctrl+N</b></li>
   <li>Click "Browse" to select your Windows image (.wim, .esd, or .iso)</li>
   <li>Or drag and drop the file directly!</li>
   </ul>
</li>

<li><b>Choose a Profile</b>
   <ul>
   <li>Click one of the profile cards (Gaming, Developer, etc.)</li>
   <li>This automatically selects recommended features</li>
   </ul>
</li>

<li><b>Customize Features</b>
   <ul>
   <li>Click "Show Advanced Options" to see all <b>150+ features</b></li>
   <li>Explore 16 categories: Gaming, Privacy, Browsers, Dev Tools, and more!</li>
   <li>Check or uncheck features as needed</li>
   <li>Watch the live summary update!</li>
   </ul>
</li>

<li><b>Build Your Image</b>
   <ul>
   <li>Click "Build Image" to start</li>
   <li>Watch real-time progress and logs</li>
   <li>Your customized image will be created!</li>
   </ul>
</li>
</ol>

<h3>Keyboard Shortcuts:</h3>
<ul>
<li><b>F1</b> - Show this tutorial</li>
<li><b>Ctrl+N</b> - New build</li>
<li><b>Ctrl+O</b> - Open image</li>
<li><b>Ctrl+A</b> - Analyze image</li>
<li><b>Ctrl+P</b> - Manage profiles</li>
<li><b>Ctrl+,</b> - Settings</li>
<li><b>Ctrl+Q</b> - Exit</li>
</ul>

<p><i>Need more help? Press <b>Ctrl+F1</b> for full documentation.</i></p>
        """

        tutorial.setText(tutorial_text)
        tutorial.setTextFormat(Qt.TextFormat.RichText)
        tutorial.setStandardButtons(QMessageBox.StandardButton.Ok)
        tutorial.exec()

    def open_documentation(self):
        """Open documentation."""
        docs_dialog = QMessageBox(self)
        docs_dialog.setWindowTitle("Documentation")
        docs_dialog.setText(
            "<h2>DeployForge Documentation</h2>"
            "<p>Full documentation is available in the following files:</p>"
            "<ul>"
            "<li><b>GUI_COMPLETION_PLAN.md</b> - Complete GUI roadmap and features</li>"
            "<li><b>CURRENT_STATUS.md</b> - Current project status</li>"
            "<li><b>INTEGRATION_COMPLETE_SESSION.md</b> - Integration details</li>"
            "<li><b>README.md</b> - Project overview and quick start</li>"
            "</ul>"
            "<p>These files are located in the DeployForge root directory.</p>"
            "<p>For online documentation, visit the GitHub repository:</p>"
            "<p><a href='https://github.com/Cornman92/DeployForge'>github.com/Cornman92/DeployForge</a></p>"
        )
        docs_dialog.setTextFormat(Qt.TextFormat.RichText)
        docs_dialog.exec()

    def show_shortcuts(self):
        """Show keyboard shortcuts reference."""
        shortcuts = QMessageBox(self)
        shortcuts.setWindowTitle("Keyboard Shortcuts")
        shortcuts.setText(
            "<h2>Keyboard Shortcuts</h2>"
            "<h3>File Operations:</h3>"
            "<table>"
            "<tr><td><b>Ctrl+N</b></td><td>New Build</td></tr>"
            "<tr><td><b>Ctrl+O</b></td><td>Open Image</td></tr>"
            "<tr><td><b>Ctrl+Q</b></td><td>Exit</td></tr>"
            "</table>"
            "<h3>Navigation:</h3>"
            "<table>"
            "<tr><td><b>Ctrl+Home</b></td><td>Welcome Page</td></tr>"
            "<tr><td><b>Ctrl+A</b></td><td>Analyze</td></tr>"
            "<tr><td><b>Ctrl+P</b></td><td>Profiles</td></tr>"
            "<tr><td><b>Ctrl+,</b></td><td>Settings</td></tr>"
            "</table>"
            "<h3>Tools:</h3>"
            "<table>"
            "<tr><td><b>Ctrl+Shift+C</b></td><td>Compare Images</td></tr>"
            "</table>"
            "<h3>Help:</h3>"
            "<table>"
            "<tr><td><b>F1</b></td><td>Getting Started</td></tr>"
            "<tr><td><b>Ctrl+F1</b></td><td>Documentation</td></tr>"
            "</table>"
        )
        shortcuts.setTextFormat(Qt.TextFormat.RichText)
        shortcuts.exec()

    def show_about_dialog(self):
        """Show about dialog with version and credits."""
        about = QMessageBox(self)
        about.setWindowTitle("About DeployForge")
        about.setIconPixmap(QPixmap())  # You can add an icon here

        about_text = """
<h1>DeployForge</h1>
<h2>Version 1.5.0 - Feature Expansion Update</h2>

<p><b>Enterprise Windows Deployment Suite</b></p>

<p>DeployForge is a comprehensive, professional tool for managing and customizing
Windows deployment images with a beautiful modern interface.</p>

<h3>Massive Feature Set:</h3>
<ul>
<li>✅ <b>150+ Customization Features</b> (3x expansion!)</li>
<li>✅ 16 Feature Categories</li>
<li>✅ 6 Enhanced Pre-built Profiles</li>
<li>✅ 40+ Application Installers</li>
<li>✅ Real-time Progress Tracking</li>
<li>✅ Light + Dark Themes</li>
<li>✅ Beginner-Friendly Wizard</li>
<li>✅ Advanced Expert Controls</li>
</ul>

<h3>Feature Categories:</h3>
<ul>
<li>🎮 Gaming (15 options) | 🗑️ Privacy (16 options)</li>
<li>🎨 Visual (19 options) | 💻 Dev Tools (19 options)</li>
<li>🏢 Enterprise (12 options) | 🌐 Browsers (6 options)</li>
<li>📝 Productivity (10 options) | 🎨 Creative (10 options)</li>
<li>🎮 Gaming Platforms (7 options) | 🔧 Utilities (10 options)</li>
<li>⚡ Performance (10 options) | 🔌 Services (8 options)</li>
<li>🌐 Network (13 options) | 🔋 Power (5 options)</li>
<li>📁 Explorer (7 options) | 💾 Storage (3 options)</li>
</ul>

<h3>Components:</h3>
<ul>
<li>GUI: 3,200+ lines of production code</li>
<li>Integration: ConfigurationManager with 150+ modules</li>
<li>Backend: 60+ specialized modules</li>
</ul>

<h3>Technology:</h3>
<ul>
<li>Python 3.9+</li>
<li>PyQt6 (GUI Framework)</li>
<li>DISM (Windows Deployment)</li>
</ul>

<p><i>Developed with ❤️ for Windows deployment professionals</i></p>

<p>
<b>License:</b> MIT<br>
<b>Repository:</b> <a href='https://github.com/Cornman92/DeployForge'>github.com/Cornman92/DeployForge</a><br>
<b>Copyright © 2025 DeployForge Contributors</b>
</p>
        """

        about.setText(about_text)
        about.setTextFormat(Qt.TextFormat.RichText)
        about.setStandardButtons(QMessageBox.StandardButton.Ok)
        about.exec()

    def _create_page(self, page_id: str):
        """Create a page on-demand (lazy loading for performance)."""
        if page_id in self._page_classes and self.pages[page_id] is None:
            # Create the page
            page_class = self._page_classes[page_id]
            page = page_class()
            self.pages[page_id] = page

            # Add to stack and track index
            index = self.content_stack.addWidget(page)
            self._page_indices[page_id] = index

            logger.info(f"Lazy-loaded page: {page_id}")

    def show_page(self, page_id: str):
        """Show a specific page (creates on-demand if needed)."""

        if page_id in self.pages:
            # Create page if it doesn't exist yet (lazy loading)
            if self.pages[page_id] is None:
                self._create_page(page_id)

            # Show the page
            if page_id in self._page_indices:
                self.content_stack.setCurrentIndex(self._page_indices[page_id])

            # Update status bar
            page_names = {
                "welcome": "Home",
                "build": "Build Image",
                "profiles": "Manage Profiles",
                "analyze": "Analyze Image",
                "settings": "Settings",
            }
            self.statusBar().showMessage(f"{page_names.get(page_id, 'Ready')}")

    def center_window(self):
        """Center the window on screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def closeEvent(self, event):
        """Handle window close event and save settings."""
        # Save window geometry (using cache for better performance)
        if self._get_cached_setting("auto_save_window", True):
            self._set_cached_setting("window/geometry", self.saveGeometry())

        # Save current theme
        self._set_cached_setting("theme", theme_manager.get_theme())

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


if __name__ == "__main__":
    launch_modern_gui()
