"""
Application Catalog for DeployForge

Centralized repository of application definitions for automated installation.
Contains 113 pre-configured applications across 11 categories.

Categories:
- Gaming: 12 applications
- Development: 15 applications
- Browsers: 8 applications
- Utilities: 10 applications
- Creative: 5 applications
- Productivity: 15 applications
- Communication: 12 applications
- Security: 10 applications (VPNs, password managers, antivirus)
- Cloud Storage: 8 applications
- Media: 8 applications (music and video players)
- System Tools: 10 applications (monitoring, benchmarking)

Each application includes:
- WinGet ID (primary installation method)
- Chocolatey ID (fallback method)
- Direct download URL (final fallback)
- Silent installation arguments
- Dependencies and conflicts

Example:
    from deployforge.app_catalog import get_app, GAMING_APPS, PRODUCTIVITY_APPS

    # Get single application
    vscode = get_app("vscode")
    print(f"Installing {vscode.name} via WinGet: {vscode.winget_id}")

    # Get all gaming applications
    for app_id, app in GAMING_APPS.items():
        print(f"{app.name}: {app.description}")

    # Get all productivity applications
    for app_id, app in PRODUCTIVITY_APPS.items():
        print(f"{app.name}: {app.description}")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class ApplicationDefinition:
    """
    Defines how to install an application.

    Attributes:
        id: Unique identifier (e.g., "vscode")
        name: Display name (e.g., "Visual Studio Code")
        description: Brief description of the application
        category: Category (Gaming, Development, Browsers, etc.)
        winget_id: Windows Package Manager ID
        chocolatey_id: Chocolatey package ID
        download_url: Direct download URL (final fallback)
        silent_args: Silent installation arguments
        install_location: Preferred installation location
        requires_admin: Whether admin privileges are required
        version: Specific version to install (None = latest)
        architecture: Target architecture (x64, x86, arm64, any)
        min_os_version: Minimum OS version required
        dependencies: List of app IDs that must be installed first
        conflicts_with: List of app IDs that conflict
        post_install_script: Optional post-install PowerShell script
        registry_tweaks: Optional registry modifications
    """

    id: str
    name: str
    description: str
    category: str
    winget_id: Optional[str] = None
    chocolatey_id: Optional[str] = None
    download_url: Optional[str] = None
    silent_args: str = "/S"
    install_location: Optional[Path] = None
    requires_admin: bool = True
    version: Optional[str] = None
    architecture: str = "x64"
    min_os_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    post_install_script: Optional[str] = None
    registry_tweaks: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "winget_id": self.winget_id,
            "chocolatey_id": self.chocolatey_id,
            "has_download_url": self.download_url is not None,
            "requires_admin": self.requires_admin,
            "architecture": self.architecture,
            "dependencies": self.dependencies,
        }


# =============================================================================
# GAMING APPLICATIONS (12 apps)
# =============================================================================

GAMING_APPS: Dict[str, ApplicationDefinition] = {
    "steam": ApplicationDefinition(
        id="steam",
        name="Steam",
        description="Valve's digital distribution platform for gaming",
        category="Gaming",
        winget_id="Valve.Steam",
        chocolatey_id="steam",
        download_url="https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe",
        silent_args="/S",
        requires_admin=True,
    ),
    "epic_games": ApplicationDefinition(
        id="epic_games",
        name="Epic Games Launcher",
        description="Epic Games Store and launcher",
        category="Gaming",
        winget_id="EpicGames.EpicGamesLauncher",
        chocolatey_id="epicgameslauncher",
        download_url="https://launcher-public-service-prod06.ol.epicgames.com/launcher/api/installer/download/EpicGamesLauncherInstaller.msi",
        silent_args="/quiet /norestart",
        requires_admin=True,
    ),
    "gog_galaxy": ApplicationDefinition(
        id="gog_galaxy",
        name="GOG Galaxy",
        description="GOG.com gaming platform and launcher",
        category="Gaming",
        winget_id="GOG.Galaxy",
        chocolatey_id="goggalaxy",
        silent_args="/SILENT /SUPPRESSMSGBOXES /NORESTART",
        requires_admin=True,
    ),
    "battle_net": ApplicationDefinition(
        id="battle_net",
        name="Battle.net",
        description="Blizzard Entertainment game launcher",
        category="Gaming",
        winget_id="Blizzard.BattleNet",
        chocolatey_id="battle.net",
        silent_args='--lang=enUS --installpath="C:\\Program Files (x86)\\Battle.net"',
        requires_admin=True,
    ),
    "ea_app": ApplicationDefinition(
        id="ea_app",
        name="EA App",
        description="Electronic Arts gaming platform",
        category="Gaming",
        winget_id="ElectronicArts.EADesktop",
        chocolatey_id="ea-app",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "ubisoft_connect": ApplicationDefinition(
        id="ubisoft_connect",
        name="Ubisoft Connect",
        description="Ubisoft gaming platform and launcher",
        category="Gaming",
        winget_id="Ubisoft.Connect",
        chocolatey_id="ubisoft-connect",
        silent_args="/S",
        requires_admin=True,
    ),
    "xbox_app": ApplicationDefinition(
        id="xbox_app",
        name="Xbox App",
        description="Microsoft Xbox gaming app for Windows",
        category="Gaming",
        winget_id="Microsoft.GamingApp",
        requires_admin=False,
    ),
    "discord": ApplicationDefinition(
        id="discord",
        name="Discord",
        description="Voice, video, and text communication for gamers",
        category="Communication",
        winget_id="Discord.Discord",
        chocolatey_id="discord",
        download_url="https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64",
        silent_args="/S",
        requires_admin=False,
    ),
    "obs_studio": ApplicationDefinition(
        id="obs_studio",
        name="OBS Studio",
        description="Free and open-source streaming and recording software",
        category="Streaming",
        winget_id="OBSProject.OBSStudio",
        chocolatey_id="obs-studio",
        download_url="https://cdn-fastly.obsproject.com/downloads/OBS-Studio-Latest-Full-Installer-x64.exe",
        silent_args="/S",
        requires_admin=True,
    ),
    "nvidia_geforce": ApplicationDefinition(
        id="nvidia_geforce",
        name="GeForce Experience",
        description="NVIDIA GPU driver and optimization software",
        category="Drivers",
        winget_id="Nvidia.GeForceExperience",
        chocolatey_id="geforce-experience",
        silent_args="/s /noreboot",
        requires_admin=True,
    ),
    "amd_adrenalin": ApplicationDefinition(
        id="amd_adrenalin",
        name="AMD Adrenalin",
        description="AMD GPU driver and control software",
        category="Drivers",
        winget_id="AMD.AdrenalinEdition",
        silent_args="/S",
        requires_admin=True,
    ),
    "msi_afterburner": ApplicationDefinition(
        id="msi_afterburner",
        name="MSI Afterburner",
        description="GPU overclocking and monitoring utility",
        category="Utilities",
        chocolatey_id="msiafterburner",
        silent_args="/S",
        requires_admin=True,
    ),
}

# =============================================================================
# DEVELOPMENT APPLICATIONS (15 apps)
# =============================================================================

DEVELOPMENT_APPS: Dict[str, ApplicationDefinition] = {
    "vscode": ApplicationDefinition(
        id="vscode",
        name="Visual Studio Code",
        description="Lightweight but powerful source code editor",
        category="Development",
        winget_id="Microsoft.VisualStudioCode",
        chocolatey_id="vscode",
        download_url="https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
        silent_args="/VERYSILENT /NORESTART /MERGETASKS=!runcode",
        requires_admin=False,
        dependencies=["git"],
    ),
    "visual_studio": ApplicationDefinition(
        id="visual_studio",
        name="Visual Studio 2022 Community",
        description="Full-featured IDE for .NET and C++ development",
        category="Development",
        winget_id="Microsoft.VisualStudio.2022.Community",
        chocolatey_id="visualstudio2022community",
        silent_args="--quiet --wait --norestart",
        requires_admin=True,
    ),
    "pycharm": ApplicationDefinition(
        id="pycharm",
        name="PyCharm Community Edition",
        description="Python IDE for professional developers",
        category="Development",
        winget_id="JetBrains.PyCharm.Community",
        chocolatey_id="pycharm-community",
        silent_args="/S /CONFIG=silent.config",
        requires_admin=True,
    ),
    "intellij": ApplicationDefinition(
        id="intellij",
        name="IntelliJ IDEA Community",
        description="Java and Kotlin IDE",
        category="Development",
        winget_id="JetBrains.IntelliJIDEA.Community",
        chocolatey_id="intellijidea-community",
        silent_args="/S",
        requires_admin=True,
    ),
    "git": ApplicationDefinition(
        id="git",
        name="Git for Windows",
        description="Distributed version control system",
        category="Development",
        winget_id="Git.Git",
        chocolatey_id="git",
        download_url="https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe",
        silent_args='/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS="icons,ext\\reg\\shellhere,assoc,assoc_sh"',
        requires_admin=True,
    ),
    "github_desktop": ApplicationDefinition(
        id="github_desktop",
        name="GitHub Desktop",
        description="Git GUI client for GitHub",
        category="Development",
        winget_id="GitHub.GitHubDesktop",
        chocolatey_id="github-desktop",
        silent_args="/S",
        requires_admin=False,
        dependencies=["git"],
    ),
    "nodejs": ApplicationDefinition(
        id="nodejs",
        name="Node.js LTS",
        description="JavaScript runtime built on Chrome's V8 engine",
        category="Development",
        winget_id="OpenJS.NodeJS.LTS",
        chocolatey_id="nodejs-lts",
        download_url="https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi",
        silent_args="/quiet /norestart",
        requires_admin=True,
    ),
    "python": ApplicationDefinition(
        id="python",
        name="Python 3.11",
        description="High-level programming language",
        category="Development",
        winget_id="Python.Python.3.11",
        chocolatey_id="python311",
        download_url="https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe",
        silent_args="/quiet InstallAllUsers=1 PrependPath=1",
        requires_admin=True,
    ),
    "docker": ApplicationDefinition(
        id="docker",
        name="Docker Desktop",
        description="Containerization platform",
        category="Development",
        winget_id="Docker.DockerDesktop",
        chocolatey_id="docker-desktop",
        silent_args="install --quiet",
        requires_admin=True,
        min_os_version="10.0.19041",  # Windows 10 20H1
    ),
    "postman": ApplicationDefinition(
        id="postman",
        name="Postman",
        description="API development and testing platform",
        category="Development",
        winget_id="Postman.Postman",
        chocolatey_id="postman",
        silent_args="/S",
        requires_admin=False,
    ),
    "windows_terminal": ApplicationDefinition(
        id="windows_terminal",
        name="Windows Terminal",
        description="Modern terminal application for Windows",
        category="Development",
        winget_id="Microsoft.WindowsTerminal",
        chocolatey_id="microsoft-windows-terminal",
        requires_admin=False,
    ),
    "powershell7": ApplicationDefinition(
        id="powershell7",
        name="PowerShell 7",
        description="Cross-platform PowerShell",
        category="Development",
        winget_id="Microsoft.PowerShell",
        chocolatey_id="powershell-core",
        download_url="https://github.com/PowerShell/PowerShell/releases/download/v7.4.0/PowerShell-7.4.0-win-x64.msi",
        silent_args="/quiet /norestart",
        requires_admin=True,
    ),
    "azure_cli": ApplicationDefinition(
        id="azure_cli",
        name="Azure CLI",
        description="Command-line interface for Azure",
        category="Development",
        winget_id="Microsoft.AzureCLI",
        chocolatey_id="azure-cli",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "aws_cli": ApplicationDefinition(
        id="aws_cli",
        name="AWS CLI",
        description="Command-line interface for AWS",
        category="Development",
        winget_id="Amazon.AWSCLI",
        chocolatey_id="awscli",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "vscode_insiders": ApplicationDefinition(
        id="vscode_insiders",
        name="Visual Studio Code Insiders",
        description="VS Code preview build with latest features",
        category="Development",
        winget_id="Microsoft.VisualStudioCode.Insiders",
        chocolatey_id="vscode-insiders",
        silent_args="/VERYSILENT /NORESTART",
        requires_admin=False,
    ),
}

# =============================================================================
# BROWSER APPLICATIONS (8 apps)
# =============================================================================

BROWSER_APPS: Dict[str, ApplicationDefinition] = {
    "chrome": ApplicationDefinition(
        id="chrome",
        name="Google Chrome",
        description="Fast, secure web browser by Google",
        category="Browsers",
        winget_id="Google.Chrome",
        chocolatey_id="googlechrome",
        download_url="https://dl.google.com/chrome/install/latest/chrome_installer.exe",
        silent_args="/silent /install",
        requires_admin=True,
    ),
    "firefox": ApplicationDefinition(
        id="firefox",
        name="Mozilla Firefox",
        description="Free and open-source web browser",
        category="Browsers",
        winget_id="Mozilla.Firefox",
        chocolatey_id="firefox",
        download_url="https://download.mozilla.org/?product=firefox-latest-ssl&os=win64&lang=en-US",
        silent_args="/S",
        requires_admin=True,
    ),
    "edge": ApplicationDefinition(
        id="edge",
        name="Microsoft Edge",
        description="Microsoft's modern web browser",
        category="Browsers",
        winget_id="Microsoft.Edge",
        chocolatey_id="microsoft-edge",
        requires_admin=True,
    ),
    "brave": ApplicationDefinition(
        id="brave",
        name="Brave Browser",
        description="Privacy-focused browser with ad blocking",
        category="Browsers",
        winget_id="Brave.Brave",
        chocolatey_id="brave",
        download_url="https://laptop-updates.brave.com/latest/winx64",
        silent_args="/silent /install",
        requires_admin=True,
    ),
    "opera": ApplicationDefinition(
        id="opera",
        name="Opera",
        description="Feature-rich web browser",
        category="Browsers",
        winget_id="Opera.Opera",
        chocolatey_id="opera",
        silent_args="/silent /launchopera=0 /setdefaultbrowser=0",
        requires_admin=True,
    ),
    "opera_gx": ApplicationDefinition(
        id="opera_gx",
        name="Opera GX",
        description="Gaming browser with CPU/RAM limiters",
        category="Browsers",
        winget_id="Opera.OperaGX",
        chocolatey_id="opera-gx",
        silent_args="/silent",
        requires_admin=True,
    ),
    "vivaldi": ApplicationDefinition(
        id="vivaldi",
        name="Vivaldi",
        description="Highly customizable web browser",
        category="Browsers",
        winget_id="VivaldiTechnologies.Vivaldi",
        chocolatey_id="vivaldi",
        silent_args="/S",
        requires_admin=True,
    ),
    "tor_browser": ApplicationDefinition(
        id="tor_browser",
        name="Tor Browser",
        description="Privacy browser using the Tor network",
        category="Browsers",
        winget_id="TorProject.TorBrowser",
        chocolatey_id="tor-browser",
        silent_args="/S",
        requires_admin=False,
    ),
}

# =============================================================================
# UTILITY APPLICATIONS (10+ apps)
# =============================================================================

UTILITY_APPS: Dict[str, ApplicationDefinition] = {
    "7zip": ApplicationDefinition(
        id="7zip",
        name="7-Zip",
        description="Free file archiver with high compression ratio",
        category="Utilities",
        winget_id="7zip.7zip",
        chocolatey_id="7zip",
        download_url="https://www.7-zip.org/a/7z2301-x64.exe",
        silent_args="/S",
        requires_admin=True,
    ),
    "winrar": ApplicationDefinition(
        id="winrar",
        name="WinRAR",
        description="Powerful archive manager",
        category="Utilities",
        winget_id="RARLab.WinRAR",
        chocolatey_id="winrar",
        silent_args="/S",
        requires_admin=True,
    ),
    "vlc": ApplicationDefinition(
        id="vlc",
        name="VLC Media Player",
        description="Free and open-source multimedia player",
        category="Media",
        winget_id="VideoLAN.VLC",
        chocolatey_id="vlc",
        download_url="https://get.videolan.org/vlc/last/win64/vlc-3.0.20-win64.exe",
        silent_args="/S",
        requires_admin=True,
    ),
    "everything": ApplicationDefinition(
        id="everything",
        name="Everything Search",
        description="Lightning-fast file search utility",
        category="Utilities",
        winget_id="voidtools.Everything",
        chocolatey_id="everything",
        silent_args="/S",
        requires_admin=True,
    ),
    "powertoys": ApplicationDefinition(
        id="powertoys",
        name="Microsoft PowerToys",
        description="Windows system utilities for power users",
        category="Utilities",
        winget_id="Microsoft.PowerToys",
        chocolatey_id="powertoys",
        silent_args="/quiet",
        requires_admin=True,
        min_os_version="10.0.19041",
    ),
    "ccleaner": ApplicationDefinition(
        id="ccleaner",
        name="CCleaner",
        description="System optimization and privacy tool",
        category="Utilities",
        winget_id="Piriform.CCleaner",
        chocolatey_id="ccleaner",
        silent_args="/S",
        requires_admin=True,
    ),
    "notepadplusplus": ApplicationDefinition(
        id="notepadplusplus",
        name="Notepad++",
        description="Free source code editor",
        category="Utilities",
        winget_id="Notepad++.Notepad++",
        chocolatey_id="notepadplusplus",
        download_url="https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6/npp.8.6.Installer.x64.exe",
        silent_args="/S",
        requires_admin=True,
    ),
    "sharex": ApplicationDefinition(
        id="sharex",
        name="ShareX",
        description="Screen capture and file sharing tool",
        category="Utilities",
        winget_id="ShareX.ShareX",
        chocolatey_id="sharex",
        silent_args="/VERYSILENT /NORESTART",
        requires_admin=False,
    ),
    "windirstat": ApplicationDefinition(
        id="windirstat",
        name="WinDirStat",
        description="Disk usage statistics viewer",
        category="Utilities",
        winget_id="WinDirStat.WinDirStat",
        chocolatey_id="windirstat",
        silent_args="/S",
        requires_admin=True,
    ),
    "cpu_z": ApplicationDefinition(
        id="cpu_z",
        name="CPU-Z",
        description="System information utility",
        category="Utilities",
        winget_id="CPUID.CPU-Z",
        chocolatey_id="cpu-z",
        silent_args="/S",
        requires_admin=False,
    ),
}

# =============================================================================
# CREATIVE APPLICATIONS (5 apps)
# =============================================================================

CREATIVE_APPS: Dict[str, ApplicationDefinition] = {
    "gimp": ApplicationDefinition(
        id="gimp",
        name="GIMP",
        description="Free and open-source image editor",
        category="Creative",
        winget_id="GIMP.GIMP",
        chocolatey_id="gimp",
        download_url="https://download.gimp.org/gimp/v2.10/windows/gimp-2.10.34-setup.exe",
        silent_args="/VERYSILENT /NORESTART",
        requires_admin=True,
    ),
    "inkscape": ApplicationDefinition(
        id="inkscape",
        name="Inkscape",
        description="Free vector graphics editor",
        category="Creative",
        winget_id="Inkscape.Inkscape",
        chocolatey_id="inkscape",
        silent_args="/S",
        requires_admin=True,
    ),
    "blender": ApplicationDefinition(
        id="blender",
        name="Blender",
        description="Free 3D creation suite",
        category="Creative",
        winget_id="BlenderFoundation.Blender",
        chocolatey_id="blender",
        silent_args="/S",
        requires_admin=True,
    ),
    "audacity": ApplicationDefinition(
        id="audacity",
        name="Audacity",
        description="Free audio editor and recorder",
        category="Creative",
        winget_id="Audacity.Audacity",
        chocolatey_id="audacity",
        silent_args="/VERYSILENT /NORESTART",
        requires_admin=True,
    ),
    "kdenlive": ApplicationDefinition(
        id="kdenlive",
        name="Kdenlive",
        description="Free video editor",
        category="Creative",
        winget_id="KDE.Kdenlive",
        chocolatey_id="kdenlive",
        silent_args="/S",
        requires_admin=True,
    ),
}

# =============================================================================
# PRODUCTIVITY APPLICATIONS (15 apps)
# =============================================================================

PRODUCTIVITY_APPS: Dict[str, ApplicationDefinition] = {
    "libreoffice": ApplicationDefinition(
        id="libreoffice",
        name="LibreOffice",
        description="Free and powerful office suite",
        category="Productivity",
        winget_id="TheDocumentFoundation.LibreOffice",
        chocolatey_id="libreoffice-fresh",
        silent_args="/S",
        requires_admin=True,
    ),
    "onlyoffice": ApplicationDefinition(
        id="onlyoffice",
        name="ONLYOFFICE Desktop Editors",
        description="Office suite compatible with Microsoft formats",
        category="Productivity",
        winget_id="ONLYOFFICE.DesktopEditors",
        chocolatey_id="onlyoffice",
        silent_args="/S",
        requires_admin=True,
    ),
    "notion": ApplicationDefinition(
        id="notion",
        name="Notion",
        description="All-in-one workspace for notes and collaboration",
        category="Productivity",
        winget_id="Notion.Notion",
        chocolatey_id="notion",
        silent_args="--silent",
        requires_admin=False,
    ),
    "obsidian": ApplicationDefinition(
        id="obsidian",
        name="Obsidian",
        description="Powerful knowledge base on local Markdown files",
        category="Productivity",
        winget_id="Obsidian.Obsidian",
        chocolatey_id="obsidian",
        silent_args="--silent",
        requires_admin=False,
    ),
    "onenote": ApplicationDefinition(
        id="onenote",
        name="Microsoft OneNote",
        description="Digital notebook from Microsoft",
        category="Productivity",
        winget_id="Microsoft.Office.OneNote",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "evernote": ApplicationDefinition(
        id="evernote",
        name="Evernote",
        description="Note-taking and organization app",
        category="Productivity",
        winget_id="Evernote.Evernote",
        chocolatey_id="evernote",
        silent_args="--silent",
        requires_admin=False,
    ),
    "todoist": ApplicationDefinition(
        id="todoist",
        name="Todoist",
        description="Task management and to-do list app",
        category="Productivity",
        winget_id="Doist.Todoist",
        silent_args="--silent",
        requires_admin=False,
    ),
    "trello": ApplicationDefinition(
        id="trello",
        name="Trello",
        description="Visual collaboration tool for organizing projects",
        category="Productivity",
        winget_id="Trello.Trello",
        silent_args="--silent",
        requires_admin=False,
    ),
    "adobereader": ApplicationDefinition(
        id="adobereader",
        name="Adobe Acrobat Reader",
        description="PDF viewer from Adobe",
        category="Productivity",
        winget_id="Adobe.Acrobat.Reader.64-bit",
        chocolatey_id="adobereader",
        silent_args="/sAll /rs /msi EULA_ACCEPT=YES",
        requires_admin=True,
    ),
    "foxit": ApplicationDefinition(
        id="foxit",
        name="Foxit PDF Reader",
        description="Fast and lightweight PDF reader",
        category="Productivity",
        winget_id="Foxit.FoxitReader",
        chocolatey_id="foxitreader",
        silent_args="/VERYSILENT /NORESTART",
        requires_admin=True,
    ),
    "sumatrapdf": ApplicationDefinition(
        id="sumatrapdf",
        name="Sumatra PDF",
        description="Lightweight PDF reader",
        category="Productivity",
        winget_id="SumatraPDF.SumatraPDF",
        chocolatey_id="sumatrapdf",
        silent_args="-s",
        requires_admin=False,
    ),
    "calibre": ApplicationDefinition(
        id="calibre",
        name="Calibre",
        description="E-book management application",
        category="Productivity",
        winget_id="calibre.calibre",
        chocolatey_id="calibre",
        silent_args="/S",
        requires_admin=True,
    ),
    "mindmanager": ApplicationDefinition(
        id="xmind",
        name="XMind",
        description="Mind mapping and brainstorming tool",
        category="Productivity",
        winget_id="XMind.XMind",
        silent_args="--silent",
        requires_admin=False,
    ),
    "anki": ApplicationDefinition(
        id="anki",
        name="Anki",
        description="Flashcard program for memorization",
        category="Productivity",
        winget_id="Anki.Anki",
        chocolatey_id="anki",
        silent_args="/S",
        requires_admin=True,
    ),
    "typora": ApplicationDefinition(
        id="typora",
        name="Typora",
        description="Minimalist Markdown editor",
        category="Productivity",
        winget_id="Typora.Typora",
        chocolatey_id="typora",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
}

# =============================================================================
# COMMUNICATION APPLICATIONS (12 apps)
# =============================================================================

COMMUNICATION_APPS: Dict[str, ApplicationDefinition] = {
    "zoom": ApplicationDefinition(
        id="zoom",
        name="Zoom",
        description="Video conferencing and online meetings",
        category="Communication",
        winget_id="Zoom.Zoom",
        chocolatey_id="zoom",
        silent_args="/silent",
        requires_admin=True,
    ),
    "teams": ApplicationDefinition(
        id="teams",
        name="Microsoft Teams",
        description="Collaboration and communication platform",
        category="Communication",
        winget_id="Microsoft.Teams",
        chocolatey_id="microsoft-teams",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "slack": ApplicationDefinition(
        id="slack",
        name="Slack",
        description="Team communication and collaboration",
        category="Communication",
        winget_id="SlackTechnologies.Slack",
        chocolatey_id="slack",
        silent_args="--silent",
        requires_admin=False,
    ),
    "skype": ApplicationDefinition(
        id="skype",
        name="Skype",
        description="Video chat and voice call application",
        category="Communication",
        winget_id="Microsoft.Skype",
        chocolatey_id="skype",
        silent_args="/silent",
        requires_admin=True,
    ),
    "telegram": ApplicationDefinition(
        id="telegram",
        name="Telegram Desktop",
        description="Messaging app with focus on speed and security",
        category="Communication",
        winget_id="Telegram.TelegramDesktop",
        chocolatey_id="telegram",
        silent_args="/VERYSILENT",
        requires_admin=False,
    ),
    "signal": ApplicationDefinition(
        id="signal",
        name="Signal",
        description="Private messenger with end-to-end encryption",
        category="Communication",
        winget_id="OpenWhisperSystems.Signal",
        chocolatey_id="signal",
        silent_args="--silent",
        requires_admin=False,
    ),
    "whatsapp": ApplicationDefinition(
        id="whatsapp",
        name="WhatsApp Desktop",
        description="Cross-platform messaging app",
        category="Communication",
        winget_id="WhatsApp.WhatsApp",
        silent_args="--silent",
        requires_admin=False,
    ),
    "thunderbird": ApplicationDefinition(
        id="thunderbird",
        name="Mozilla Thunderbird",
        description="Open-source email client",
        category="Communication",
        winget_id="Mozilla.Thunderbird",
        chocolatey_id="thunderbird",
        silent_args="/S",
        requires_admin=True,
    ),
    "mailbird": ApplicationDefinition(
        id="mailbird",
        name="Mailbird",
        description="Email client for Windows",
        category="Communication",
        winget_id="Mailbird.Mailbird",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "discord-canary": ApplicationDefinition(
        id="discord-canary",
        name="Discord Canary",
        description="Alpha testing version of Discord",
        category="Communication",
        winget_id="Discord.Discord.Canary",
        silent_args="--silent",
        requires_admin=False,
    ),
    "teamspeak": ApplicationDefinition(
        id="teamspeak",
        name="TeamSpeak 3",
        description="Voice communication for gaming",
        category="Communication",
        winget_id="TeamSpeakSystems.TeamSpeakClient",
        chocolatey_id="teamspeak",
        silent_args="/S",
        requires_admin=True,
    ),
    "mumble": ApplicationDefinition(
        id="mumble",
        name="Mumble",
        description="Open-source voice chat software",
        category="Communication",
        winget_id="Mumble.Mumble",
        chocolatey_id="mumble",
        silent_args="/S",
        requires_admin=True,
    ),
}

# =============================================================================
# SECURITY & VPN APPLICATIONS (10 apps)
# =============================================================================

SECURITY_APPS: Dict[str, ApplicationDefinition] = {
    "bitwarden": ApplicationDefinition(
        id="bitwarden",
        name="Bitwarden",
        description="Open-source password manager",
        category="Security",
        winget_id="Bitwarden.Bitwarden",
        chocolatey_id="bitwarden",
        silent_args="--silent",
        requires_admin=False,
    ),
    "1password": ApplicationDefinition(
        id="1password",
        name="1Password",
        description="Password manager and digital vault",
        category="Security",
        winget_id="AgileBits.1Password",
        chocolatey_id="1password",
        silent_args="--silent",
        requires_admin=False,
    ),
    "keepass": ApplicationDefinition(
        id="keepass",
        name="KeePass",
        description="Free and open-source password manager",
        category="Security",
        winget_id="KeePassXCTeam.KeePassXC",
        chocolatey_id="keepass",
        silent_args="/S",
        requires_admin=True,
    ),
    "lastpass": ApplicationDefinition(
        id="lastpass",
        name="LastPass",
        description="Password manager",
        category="Security",
        winget_id="LogMeIn.LastPass",
        silent_args="--silent",
        requires_admin=False,
    ),
    "nordvpn": ApplicationDefinition(
        id="nordvpn",
        name="NordVPN",
        description="VPN service",
        category="Security",
        winget_id="NordVPN.NordVPN",
        chocolatey_id="nordvpn",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "expressvpn": ApplicationDefinition(
        id="expressvpn",
        name="ExpressVPN",
        description="Fast and secure VPN",
        category="Security",
        winget_id="ExpressVPN.ExpressVPN",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "protonvpn": ApplicationDefinition(
        id="protonvpn",
        name="ProtonVPN",
        description="Secure VPN from Swiss company",
        category="Security",
        winget_id="ProtonTechnologies.ProtonVPN",
        silent_args="--silent",
        requires_admin=True,
    ),
    "malwarebytes": ApplicationDefinition(
        id="malwarebytes",
        name="Malwarebytes",
        description="Anti-malware software",
        category="Security",
        winget_id="Malwarebytes.Malwarebytes",
        chocolatey_id="malwarebytes",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "veracrypt": ApplicationDefinition(
        id="veracrypt",
        name="VeraCrypt",
        description="Disk encryption software",
        category="Security",
        winget_id="IDRIX.VeraCrypt",
        chocolatey_id="veracrypt",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "wireguard": ApplicationDefinition(
        id="wireguard",
        name="WireGuard",
        description="Fast and modern VPN",
        category="Security",
        winget_id="WireGuard.WireGuard",
        chocolatey_id="wireguard",
        silent_args="/quiet",
        requires_admin=True,
    ),
}

# =============================================================================
# CLOUD STORAGE APPLICATIONS (8 apps)
# =============================================================================

CLOUD_STORAGE_APPS: Dict[str, ApplicationDefinition] = {
    "dropbox": ApplicationDefinition(
        id="dropbox",
        name="Dropbox",
        description="Cloud storage and file synchronization",
        category="Cloud Storage",
        winget_id="Dropbox.Dropbox",
        chocolatey_id="dropbox",
        silent_args="/S",
        requires_admin=True,
    ),
    "googledrive": ApplicationDefinition(
        id="googledrive",
        name="Google Drive",
        description="Cloud storage from Google",
        category="Cloud Storage",
        winget_id="Google.GoogleDrive",
        silent_args="--silent",
        requires_admin=True,
    ),
    "onedrive": ApplicationDefinition(
        id="onedrive",
        name="Microsoft OneDrive",
        description="Cloud storage from Microsoft",
        category="Cloud Storage",
        winget_id="Microsoft.OneDrive",
        silent_args="/silent",
        requires_admin=False,
    ),
    "megasync": ApplicationDefinition(
        id="megasync",
        name="MEGA Sync",
        description="Secure cloud storage and sync",
        category="Cloud Storage",
        winget_id="Mega.MEGASync",
        chocolatey_id="megasync",
        silent_args="/S",
        requires_admin=True,
    ),
    "nextcloud": ApplicationDefinition(
        id="nextcloud",
        name="Nextcloud Desktop",
        description="Self-hosted cloud storage client",
        category="Cloud Storage",
        winget_id="Nextcloud.NextcloudDesktop",
        chocolatey_id="nextcloud-client",
        silent_args="/S",
        requires_admin=True,
    ),
    "syncthing": ApplicationDefinition(
        id="syncthing",
        name="Syncthing",
        description="Continuous file synchronization",
        category="Cloud Storage",
        winget_id="Syncthing.Syncthing",
        chocolatey_id="syncthing",
        silent_args="/S",
        requires_admin=True,
    ),
    "pcloud": ApplicationDefinition(
        id="pcloud",
        name="pCloud Drive",
        description="Secure cloud storage",
        category="Cloud Storage",
        winget_id="pCloud.pCloudDrive",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "box": ApplicationDefinition(
        id="box",
        name="Box Drive",
        description="Enterprise cloud storage",
        category="Cloud Storage",
        winget_id="Box.BoxDrive",
        silent_args="/quiet",
        requires_admin=True,
    ),
}

# =============================================================================
# MEDIA PLAYERS (8 apps)
# =============================================================================

MEDIA_APPS: Dict[str, ApplicationDefinition] = {
    "spotify": ApplicationDefinition(
        id="spotify",
        name="Spotify",
        description="Music streaming service",
        category="Media",
        winget_id="Spotify.Spotify",
        chocolatey_id="spotify",
        silent_args="/silent",
        requires_admin=False,
    ),
    "itunes": ApplicationDefinition(
        id="itunes",
        name="iTunes",
        description="Media player and library from Apple",
        category="Media",
        winget_id="Apple.iTunes",
        chocolatey_id="itunes",
        silent_args="/quiet",
        requires_admin=True,
    ),
    "foobar2000": ApplicationDefinition(
        id="foobar2000",
        name="foobar2000",
        description="Advanced audio player",
        category="Media",
        winget_id="PeterPawlowski.foobar2000",
        chocolatey_id="foobar2000",
        silent_args="/S",
        requires_admin=True,
    ),
    "aimp": ApplicationDefinition(
        id="aimp",
        name="AIMP",
        description="Audio player with versatile features",
        category="Media",
        winget_id="AIMP.AIMP",
        chocolatey_id="aimp",
        silent_args="/SILENT",
        requires_admin=True,
    ),
    "kodi": ApplicationDefinition(
        id="kodi",
        name="Kodi",
        description="Open-source media center",
        category="Media",
        winget_id="XBMCFoundation.Kodi",
        chocolatey_id="kodi",
        silent_args="/S",
        requires_admin=True,
    ),
    "plex": ApplicationDefinition(
        id="plex",
        name="Plex Media Player",
        description="Stream your media to any device",
        category="Media",
        winget_id="Plex.Plex",
        chocolatey_id="plex",
        silent_args="/install /quiet",
        requires_admin=True,
    ),
    "mediamonkey": ApplicationDefinition(
        id="mediamonkey",
        name="MediaMonkey",
        description="Music manager and player",
        category="Media",
        winget_id="Ventis.MediaMonkey",
        chocolatey_id="mediamonkey",
        silent_args="/S",
        requires_admin=True,
    ),
    "musicbee": ApplicationDefinition(
        id="musicbee",
        name="MusicBee",
        description="Music manager and player",
        category="Media",
        winget_id="MusicBee.MusicBee",
        chocolatey_id="musicbee",
        silent_args="/S",
        requires_admin=True,
    ),
}

# =============================================================================
# SYSTEM TOOLS (10 apps)
# =============================================================================

SYSTEM_TOOLS_APPS: Dict[str, ApplicationDefinition] = {
    "cpuz": ApplicationDefinition(
        id="cpuz",
        name="CPU-Z",
        description="System information utility",
        category="System Tools",
        winget_id="CPUID.CPU-Z",
        chocolatey_id="cpu-z",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "gpuz": ApplicationDefinition(
        id="gpuz",
        name="GPU-Z",
        description="Graphics card information utility",
        category="System Tools",
        winget_id="TechPowerUp.GPU-Z",
        chocolatey_id="gpu-z",
        silent_args="/S",
        requires_admin=False,
    ),
    "hwinfo": ApplicationDefinition(
        id="hwinfo",
        name="HWiNFO",
        description="Hardware information and monitoring tool",
        category="System Tools",
        winget_id="REALiX.HWiNFO",
        chocolatey_id="hwinfo",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "hwmonitor": ApplicationDefinition(
        id="hwmonitor",
        name="HWMonitor",
        description="Hardware monitoring program",
        category="System Tools",
        winget_id="CPUID.HWMonitor",
        chocolatey_id="hwmonitor",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "crystaldiskinfo": ApplicationDefinition(
        id="crystaldiskinfo",
        name="CrystalDiskInfo",
        description="HDD/SSD health monitoring utility",
        category="System Tools",
        winget_id="CrystalDewWorld.CrystalDiskInfo",
        chocolatey_id="crystaldiskinfo",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "crystaldiskmark": ApplicationDefinition(
        id="crystaldiskmark",
        name="CrystalDiskMark",
        description="Disk benchmark utility",
        category="System Tools",
        winget_id="CrystalDewWorld.CrystalDiskMark",
        chocolatey_id="crystaldiskmark",
        silent_args="/VERYSILENT",
        requires_admin=True,
    ),
    "speccy": ApplicationDefinition(
        id="speccy",
        name="Speccy",
        description="System information tool from Piriform",
        category="System Tools",
        winget_id="Piriform.Speccy",
        chocolatey_id="speccy",
        silent_args="/S",
        requires_admin=True,
    ),
    "coretemp": ApplicationDefinition(
        id="coretemp",
        name="Core Temp",
        description="CPU temperature monitor",
        category="System Tools",
        winget_id="ALCPU.CoreTemp",
        chocolatey_id="coretemp",
        silent_args="/S",
        requires_admin=True,
    ),
    "msiafterburner": ApplicationDefinition(
        id="msiafterburner",
        name="MSI Afterburner",
        description="Graphics card overclocking utility",
        category="System Tools",
        winget_id="Guru3D.Afterburner",
        chocolatey_id="msiafterburner",
        silent_args="/S",
        requires_admin=True,
    ),
    "rufus": ApplicationDefinition(
        id="rufus",
        name="Rufus",
        description="USB bootable drive creator",
        category="System Tools",
        winget_id="Rufus.Rufus",
        chocolatey_id="rufus",
        silent_args="/S",
        requires_admin=True,
    ),
}

# =============================================================================
# ALL APPLICATIONS REGISTRY
# =============================================================================

ALL_APPS: Dict[str, ApplicationDefinition] = {
    **GAMING_APPS,
    **DEVELOPMENT_APPS,
    **BROWSER_APPS,
    **UTILITY_APPS,
    **CREATIVE_APPS,
    **PRODUCTIVITY_APPS,
    **COMMUNICATION_APPS,
    **SECURITY_APPS,
    **CLOUD_STORAGE_APPS,
    **MEDIA_APPS,
    **SYSTEM_TOOLS_APPS,
}


# =============================================================================
# APPLICATION GROUPS (Curated Sets for Batch Installation)
# =============================================================================


@dataclass
class ApplicationGroup:
    """
    Curated set of applications for specific use cases.

    Attributes:
        id: Unique identifier for the group
        name: Display name
        description: Description of the group's purpose
        app_ids: List of application IDs in this group
        category: Primary category
        install_order: Whether to install in specified order (for dependencies)
    """

    id: str
    name: str
    description: str
    app_ids: List[str]
    category: str = "Group"
    install_order: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "app_ids": self.app_ids,
            "category": self.category,
            "install_order": self.install_order,
            "app_count": len(self.app_ids),
        }


# Predefined application groups
APPLICATION_GROUPS: Dict[str, ApplicationGroup] = {
    # Development Groups
    "web_dev_essentials": ApplicationGroup(
        id="web_dev_essentials",
        name="Web Development Essentials",
        description="Essential tools for web development",
        app_ids=["vscode", "git", "nodejs", "postman", "chrome", "firefox"],
        category="Development",
        install_order=True,
    ),
    "python_dev_stack": ApplicationGroup(
        id="python_dev_stack",
        name="Python Development Stack",
        description="Complete Python development environment",
        app_ids=["python", "vscode", "git", "github-desktop", "pycharm"],
        category="Development",
        install_order=True,
    ),
    "full_stack_dev": ApplicationGroup(
        id="full_stack_dev",
        name="Full Stack Development",
        description="Complete stack for full-stack development",
        app_ids=[
            "vscode",
            "git",
            "nodejs",
            "python",
            "docker",
            "postman",
            "mongodb-compass",
            "dbeaver",
            "windows-terminal",
        ],
        category="Development",
        install_order=True,
    ),
    # Content Creation Groups
    "content_creator_suite": ApplicationGroup(
        id="content_creator_suite",
        name="Content Creator Suite",
        description="Tools for content creators and streamers",
        app_ids=["obs-studio", "davinci-resolve", "audacity", "gimp", "discord", "spotify"],
        category="Creative",
    ),
    "video_production": ApplicationGroup(
        id="video_production",
        name="Video Production",
        description="Professional video editing and production",
        app_ids=["davinci-resolve", "handbrake", "vlc", "audacity", "obs-studio"],
        category="Creative",
    ),
    "graphic_design": ApplicationGroup(
        id="graphic_design",
        name="Graphic Design",
        description="Tools for graphic designers",
        app_ids=["gimp", "inkscape", "blender", "krita"],
        category="Creative",
    ),
    # Gaming Groups
    "gaming_essentials": ApplicationGroup(
        id="gaming_essentials",
        name="Gaming Essentials",
        description="Must-have applications for gamers",
        app_ids=["steam", "discord", "obs-studio", "msiafterburner", "cpuz"],
        category="Gaming",
    ),
    "all_gaming_platforms": ApplicationGroup(
        id="all_gaming_platforms",
        name="All Gaming Platforms",
        description="Install all major gaming platforms",
        app_ids=[
            "steam",
            "epic-games",
            "gog-galaxy",
            "origin",
            "ubisoft-connect",
            "battle-net",
            "xbox-app",
        ],
        category="Gaming",
    ),
    # Productivity Groups
    "student_essentials": ApplicationGroup(
        id="student_essentials",
        name="Student Essentials",
        description="Tools for students",
        app_ids=["libreoffice", "notion", "zoom", "teams", "anki", "calibre", "spotify"],
        category="Productivity",
    ),
    "remote_work_setup": ApplicationGroup(
        id="remote_work_setup",
        name="Remote Work Setup",
        description="Everything needed for remote work",
        app_ids=["zoom", "teams", "slack", "notion", "trello", "bitwarden", "nordvpn"],
        category="Productivity",
    ),
    "office_productivity": ApplicationGroup(
        id="office_productivity",
        name="Office Productivity",
        description="Office and productivity applications",
        app_ids=["libreoffice", "onlyoffice", "adobereader", "notion", "trello", "todoist"],
        category="Productivity",
    ),
    # Security & Privacy Groups
    "privacy_focused": ApplicationGroup(
        id="privacy_focused",
        name="Privacy-Focused Setup",
        description="Privacy-oriented applications",
        app_ids=["brave", "bitwarden", "signal", "protonvpn", "veracrypt", "tor-browser"],
        category="Security",
    ),
    "security_suite": ApplicationGroup(
        id="security_suite",
        name="Security Suite",
        description="Comprehensive security tools",
        app_ids=["bitwarden", "malwarebytes", "veracrypt", "nordvpn", "keepass"],
        category="Security",
    ),
    # Media & Entertainment Groups
    "media_center": ApplicationGroup(
        id="media_center",
        name="Media Center",
        description="Complete media entertainment setup",
        app_ids=["vlc", "kodi", "plex", "spotify", "foobar2000"],
        category="Media",
    ),
    "audiophile_setup": ApplicationGroup(
        id="audiophile_setup",
        name="Audiophile Setup",
        description="High-quality audio playback and management",
        app_ids=["foobar2000", "musicbee", "spotify", "audacity", "aimp"],
        category="Media",
    ),
    # Cloud & Backup Groups
    "cloud_backup": ApplicationGroup(
        id="cloud_backup",
        name="Cloud & Backup",
        description="Cloud storage and backup solutions",
        app_ids=["dropbox", "googledrive", "onedrive", "megasync", "syncthing"],
        category="Cloud Storage",
    ),
    # Communication Groups
    "communication_hub": ApplicationGroup(
        id="communication_hub",
        name="Communication Hub",
        description="All communication tools",
        app_ids=["zoom", "teams", "slack", "discord", "telegram", "signal"],
        category="Communication",
    ),
    # System Utilities Groups
    "system_monitoring": ApplicationGroup(
        id="system_monitoring",
        name="System Monitoring",
        description="System information and monitoring tools",
        app_ids=["cpuz", "gpuz", "hwinfo", "hwmonitor", "crystaldiskinfo", "crystaldiskmark"],
        category="System Tools",
    ),
    "pc_enthusiast": ApplicationGroup(
        id="pc_enthusiast",
        name="PC Enthusiast Tools",
        description="Tools for PC building and overclocking",
        app_ids=["cpuz", "gpuz", "hwinfo", "msiafterburner", "crystaldiskmark", "coretemp"],
        category="System Tools",
    ),
    # Browser Collection
    "all_browsers": ApplicationGroup(
        id="all_browsers",
        name="All Browsers",
        description="Install all major browsers",
        app_ids=["chrome", "firefox", "brave", "edge", "opera", "opera-gx", "vivaldi"],
        category="Browsers",
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_app(app_id: str) -> ApplicationDefinition:
    """
    Get application definition by ID.

    Args:
        app_id: Application identifier

    Returns:
        ApplicationDefinition for the requested app

    Raises:
        ValueError: If app_id is not found

    Example:
        app = get_app("vscode")
        print(f"{app.name}: {app.winget_id}")
    """
    if app_id not in ALL_APPS:
        raise ValueError(
            f"Unknown application: {app_id}. "
            f"Available apps: {', '.join(sorted(ALL_APPS.keys()))}"
        )
    return ALL_APPS[app_id]


def get_apps_by_category(category: str) -> Dict[str, ApplicationDefinition]:
    """
    Get all applications in a specific category.

    Args:
        category: Category name (Gaming, Development, Browsers, etc.)

    Returns:
        Dictionary of app_id -> ApplicationDefinition

    Example:
        gaming_apps = get_apps_by_category("Gaming")
        for app_id, app in gaming_apps.items():
            print(f"{app.name}")
    """
    return {app_id: app for app_id, app in ALL_APPS.items() if app.category == category}


def list_all_apps() -> List[str]:
    """
    List all available application IDs.

    Returns:
        Sorted list of app IDs

    Example:
        apps = list_all_apps()
        print(f"Total apps: {len(apps)}")
        print(f"Apps: {', '.join(apps)}")
    """
    return sorted(ALL_APPS.keys())


def list_categories() -> List[str]:
    """
    List all application categories.

    Returns:
        Sorted list of unique categories

    Example:
        categories = list_categories()
        for category in categories:
            apps = get_apps_by_category(category)
            print(f"{category}: {len(apps)} apps")
    """
    categories = {app.category for app in ALL_APPS.values()}
    return sorted(categories)


def search_apps(query: str) -> List[ApplicationDefinition]:
    """
    Search applications by name or description.

    Args:
        query: Search term (case-insensitive)

    Returns:
        List of matching ApplicationDefinitions

    Example:
        results = search_apps("code")
        for app in results:
            print(f"{app.name}: {app.description}")
    """
    query_lower = query.lower()
    matches = []

    for app in ALL_APPS.values():
        if (
            query_lower in app.name.lower()
            or query_lower in app.description.lower()
            or query_lower in app.id.lower()
        ):
            matches.append(app)

    return matches
