"""
Application Catalog for DeployForge

Centralized repository of application definitions for automated installation.
Contains 40+ pre-configured applications across multiple categories.

Categories:
- Gaming: 12 applications
- Development: 15 applications
- Browsers: 8 applications
- Utilities: 10+ applications
- Creative: 5 applications

Each application includes:
- WinGet ID (primary installation method)
- Chocolatey ID (fallback method)
- Direct download URL (final fallback)
- Silent installation arguments
- Dependencies and conflicts

Example:
    from deployforge.app_catalog import get_app, GAMING_APPS

    # Get single application
    vscode = get_app("vscode")
    print(f"Installing {vscode.name} via WinGet: {vscode.winget_id}")

    # Get all gaming applications
    for app_id, app in GAMING_APPS.items():
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
        silent_args="--lang=enUS --installpath=\"C:\\Program Files (x86)\\Battle.net\"",
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
        silent_args="/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=\"icons,ext\\reg\\shellhere,assoc,assoc_sh\"",
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
# ALL APPLICATIONS REGISTRY
# =============================================================================

ALL_APPS: Dict[str, ApplicationDefinition] = {
    **GAMING_APPS,
    **DEVELOPMENT_APPS,
    **BROWSER_APPS,
    **UTILITY_APPS,
    **CREATIVE_APPS,
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
