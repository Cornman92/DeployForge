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
    QStatusBar, QMenuBar, QMenu, QToolBar, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QTimer
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


class BuildPage(QWidget):
    """Image builder page with profile selection."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Build Custom Image")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        # Source Image Card
        source_card = ModernCard("Source Image")
        source_layout = QVBoxLayout()

        source_label = QLabel("Select a Windows installation image:")
        source_layout.addWidget(source_label)

        source_buttons = QHBoxLayout()
        self.source_path = QLabel("No image selected")
        self.source_path.setStyleSheet("color: #666666; padding: 8px;")
        source_buttons.addWidget(self.source_path, 1)

        btn_browse = ModernButton("Browse...")
        btn_browse.clicked.connect(self.browse_source)
        source_buttons.addWidget(btn_browse)

        source_layout.addLayout(source_buttons)
        source_card.layout().addLayout(source_layout)
        layout.addWidget(source_card)

        # Profile Selection Card
        profile_card = ModernCard("Select Profile")
        profile_layout = QVBoxLayout()

        profiles_label = QLabel("Choose a customization profile:")
        profile_layout.addWidget(profiles_label)

        # Profile buttons
        self.profile_buttons = []
        profiles = [
            ("🎮 Gaming", "Optimized for gaming performance", "gamer"),
            ("💻 Developer", "Development tools and environments", "developer"),
            ("🏢 Enterprise", "Enterprise security and management", "enterprise"),
            ("📚 Student", "Balanced productivity setup", "student"),
            ("🎨 Creator", "Content creation tools", "creator"),
            ("🔧 Custom", "Manual customization", "custom")
        ]

        for icon_text, description, profile_id in profiles:
            btn_container = QFrame()
            btn_container.setStyleSheet("""
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

            btn_layout = QVBoxLayout(btn_container)

            title = QLabel(icon_text)
            title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn_layout.addWidget(title)

            desc = QLabel(description)
            desc.setStyleSheet("color: #666666; font-size: 9pt;")
            btn_layout.addWidget(desc)

            profile_layout.addWidget(btn_container)

        profile_card.layout().addLayout(profile_layout)
        layout.addWidget(profile_card)

        # Output Settings Card
        output_card = ModernCard("Output Settings")
        output_layout = QVBoxLayout()

        output_label = QLabel("Output location:")
        output_layout.addWidget(output_label)

        output_buttons = QHBoxLayout()
        self.output_path = QLabel("Same as source")
        self.output_path.setStyleSheet("color: #666666; padding: 8px;")
        output_buttons.addWidget(self.output_path, 1)

        btn_output = ModernButton("Change...")
        output_buttons.addWidget(btn_output)

        output_layout.addLayout(output_buttons)
        output_card.layout().addLayout(output_layout)
        layout.addWidget(output_card)

        # Build Button
        btn_build = ModernButton("Build Image", primary=True)
        btn_build.setMinimumHeight(50)
        btn_build.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(btn_build)

        layout.addStretch()

    def browse_source(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Windows Image",
            "",
            "Windows Images (*.wim *.esd *.iso);;All Files (*)"
        )

        if file_path:
            self.source_path.setText(file_path)
            self.source_path.setStyleSheet("color: #1F1F1F; padding: 8px;")


class ProfilesPage(QWidget):
    """Profiles management page."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        header = QLabel("Manage Profiles")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        layout.addWidget(QLabel("Profile management features coming soon..."))
        layout.addStretch()


class AnalyzePage(QWidget):
    """Image analysis page."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)

        header = QLabel("Analyze Image")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(header)

        layout.addWidget(QLabel("Image analysis features coming soon..."))
        layout.addStretch()


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
