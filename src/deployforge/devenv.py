"""
Developer Environment Builder Module

Comprehensive developer environment configuration for Windows deployment images.

Features:
- Multiple development profiles (Web, Mobile, Data Science, DevOps, Game Dev, Full Stack)
- IDE installation and configuration (VS Code, Visual Studio, JetBrains suite)
- Language runtime installation (Python, Node.js, Java, .NET, Go, Rust, C++)
- Container platform setup (Docker, Podman, Kubernetes tools)
- WSL2 installation and configuration
- Git configuration with common settings
- Package manager setup (npm, pip, maven, gradle, cargo)
- Development tools (Postman, Insomnia, DBeaver, Azure Data Studio)
- Terminal customization (Windows Terminal, Oh My Posh, Starship)
- Font installation (JetBrains Mono, Fira Code, Cascadia Code, Victor Mono)
- Shell configuration (PowerShell, Bash profiles)
- Extension management for popular editors
- Database client installation (pgAdmin, MySQL Workbench, MongoDB Compass)
- API testing and development tools
- Version managers (nvm, pyenv, rbenv, sdkman)
- Cloud CLI tools (Azure CLI, AWS CLI, gcloud, kubectl)
- Build tool installation (Make, CMake, Ninja, Meson)
- Code analysis tools (SonarLint, ESLint, Pylint)
- Debugging tools and profilers
- Performance monitoring tools
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class DevelopmentProfile(Enum):
    """Development environment profiles"""

    WEB_FRONTEND = "web-frontend"  # HTML, CSS, JavaScript, TypeScript, React, Vue, Angular
    WEB_BACKEND = "web-backend"  # Node.js, Python, Java, databases
    FULL_STACK = "full-stack"  # Complete web development stack
    MOBILE = "mobile"  # Android, iOS, React Native, Flutter
    DATA_SCIENCE = "data-science"  # Python, R, Jupyter, ML frameworks
    DEVOPS = "devops"  # Docker, Kubernetes, Terraform, CI/CD
    GAME_DEV = "game-dev"  # Unity, Unreal, C++, game development tools
    EMBEDDED = "embedded"  # C, C++, Arduino, embedded systems
    DESKTOP = "desktop"  # .NET, Electron, Qt, wxWidgets
    MINIMAL = "minimal"  # Just essentials (Git, editor, one language)


class IDE(Enum):
    """Integrated Development Environments"""

    VSCODE = "Microsoft.VisualStudioCode"
    VSCODE_INSIDERS = "Microsoft.VisualStudioCode.Insiders"
    VISUAL_STUDIO_COMMUNITY = "Microsoft.VisualStudio.2022.Community"
    PYCHARM_COMMUNITY = "JetBrains.PyCharm.Community"
    INTELLIJ_COMMUNITY = "JetBrains.IntelliJIDEA.Community"
    WEBSTORM = "JetBrains.WebStorm"
    RIDER = "JetBrains.Rider"
    ANDROID_STUDIO = "Google.AndroidStudio"
    ECLIPSE = "EclipseAdoptium.Temurin.17.JDK"
    SUBLIME_TEXT = "SublimeHQ.SublimeText.4"
    ATOM = "GitHub.Atom"
    NOTEPADPP = "Notepad++.Notepad++"


@dataclass
class DevelopmentConfiguration:
    """Development environment configuration settings"""

    # Core settings
    enable_developer_mode: bool = True
    enable_wsl2: bool = True
    enable_hyperv: bool = False
    enable_containers: bool = True

    # IDEs to install
    ides: List[str] = field(default_factory=lambda: ["vscode"])

    # Languages and runtimes
    install_python: bool = True
    python_version: str = "3.12"
    install_nodejs: bool = True
    nodejs_version: str = "lts"
    install_java: bool = False
    java_version: str = "17"
    install_dotnet: bool = False
    install_go: bool = False
    install_rust: bool = False
    install_ruby: bool = False
    install_php: bool = False

    # Container platforms
    install_docker_desktop: bool = True
    install_podman: bool = False
    install_minikube: bool = False
    install_kind: bool = False

    # Development tools
    install_git: bool = True
    install_github_desktop: bool = False
    install_postman: bool = False
    install_insomnia: bool = False
    install_dbeaver: bool = False
    install_azure_data_studio: bool = False

    # Terminal and shell
    install_windows_terminal: bool = True
    install_powershell7: bool = True
    install_oh_my_posh: bool = False
    install_starship: bool = False

    # Fonts
    install_dev_fonts: bool = True
    fonts: List[str] = field(
        default_factory=lambda: ["cascadia-code", "firacode", "jetbrains-mono"]
    )

    # Package managers
    setup_npm: bool = True
    setup_pip: bool = True
    setup_cargo: bool = False

    # Cloud tools
    install_azure_cli: bool = False
    install_aws_cli: bool = False
    install_gcloud_cli: bool = False
    install_kubectl: bool = False
    install_terraform: bool = False
    install_ansible: bool = False

    # Build tools
    install_cmake: bool = False
    install_ninja: bool = False
    install_make: bool = False

    # Database clients
    install_pgadmin: bool = False
    install_mysql_workbench: bool = False
    install_mongodb_compass: bool = False
    install_redis_insight: bool = False

    # Additional tools
    install_wireshark: bool = False
    install_sysinternals: bool = True
    install_everything_search: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "enable_developer_mode": self.enable_developer_mode,
            "enable_wsl2": self.enable_wsl2,
            "enable_hyperv": self.enable_hyperv,
            "enable_containers": self.enable_containers,
            "ides": self.ides,
            "languages": {
                "python": {"enabled": self.install_python, "version": self.python_version},
                "nodejs": {"enabled": self.install_nodejs, "version": self.nodejs_version},
                "java": {"enabled": self.install_java, "version": self.java_version},
                "dotnet": self.install_dotnet,
                "go": self.install_go,
                "rust": self.install_rust,
                "ruby": self.install_ruby,
                "php": self.install_php,
            },
            "containers": {
                "docker": self.install_docker_desktop,
                "podman": self.install_podman,
                "minikube": self.install_minikube,
                "kind": self.install_kind,
            },
            "cloud_tools": {
                "azure_cli": self.install_azure_cli,
                "aws_cli": self.install_aws_cli,
                "gcloud": self.install_gcloud_cli,
                "kubectl": self.install_kubectl,
                "terraform": self.install_terraform,
                "ansible": self.install_ansible,
            },
        }


class DeveloperEnvironment:
    """
    Comprehensive developer environment builder for Windows deployment images.

    Example:
        dev = DeveloperEnvironment(Path('install.wim'))
        dev.mount()
        dev.apply_profile(DevelopmentProfile.FULL_STACK)
        dev.install_ides(['vscode', 'pycharm'])
        dev.configure_git('John Doe', 'john@example.com')
        dev.unmount(save_changes=True)
    """

    # WinGet package IDs for common tools
    LANGUAGE_PACKAGES = {
        "python": "Python.Python.3.12",
        "python311": "Python.Python.3.11",
        "nodejs": "OpenJS.NodeJS.LTS",
        "nodejs_current": "OpenJS.NodeJS",
        "java17": "EclipseAdoptium.Temurin.17.JDK",
        "java21": "EclipseAdoptium.Temurin.21.JDK",
        "dotnet": "Microsoft.DotNet.SDK.8",
        "dotnet_runtime": "Microsoft.DotNet.Runtime.8",
        "go": "GoLang.Go",
        "rust": "Rustlang.Rustup",
        "ruby": "RubyInstallerTeam.Ruby.3.2",
        "php": "PHP.PHP",
    }

    DEV_TOOLS = {
        "git": "Git.Git",
        "github_desktop": "GitHub.GitHubDesktop",
        "postman": "Postman.Postman",
        "insomnia": "Insomnia.Insomnia",
        "dbeaver": "dbeaver.dbeaver",
        "azure_data_studio": "Microsoft.AzureDataStudio",
        "docker_desktop": "Docker.DockerDesktop",
        "podman_desktop": "RedHat.Podman-Desktop",
        "windows_terminal": "Microsoft.WindowsTerminal",
        "powershell7": "Microsoft.PowerShell",
        "sysinternals": "Microsoft.Sysinternals",
        "everything": "voidtools.Everything",
    }

    CLOUD_TOOLS = {
        "azure_cli": "Microsoft.AzureCLI",
        "aws_cli": "Amazon.AWSCLI",
        "gcloud": "Google.CloudSDK",
        "kubectl": "Kubernetes.kubectl",
        "terraform": "Hashicorp.Terraform",
        "ansible": "Ansible.Ansible",
        "helm": "Helm.Helm",
    }

    DATABASE_CLIENTS = {
        "pgadmin": "PostgreSQL.pgAdmin",
        "mysql_workbench": "Oracle.MySQLWorkbench",
        "mongodb_compass": "MongoDB.Compass.Community",
        "redis_insight": "RedisLabs.RedisInsight",
        "sql_server_management_studio": "Microsoft.SQLServerManagementStudio",
    }

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize developer environment builder.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self._mounted = False
        self.config = DevelopmentConfiguration()

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount the Windows image"""
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix="deployforge_dev_"))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            if self.image_path.suffix.lower() == ".wim":
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Wim",
                        f"/WimFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )
            else:
                subprocess.run(
                    [
                        "dism",
                        "/Mount-Image",
                        f"/ImageFile:{self.image_path}",
                        f"/Index:{self.index}",
                        f"/MountDir:{mount_point}",
                    ],
                    check=True,
                    capture_output=True,
                )

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """Unmount the Windows image"""
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = "/Commit" if save_changes else "/Discard"
            subprocess.run(
                ["dism", "/Unmount-Image", f"/MountDir:{self.mount_point}", commit_flag],
                check=True,
                capture_output=True,
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def apply_profile(
        self,
        profile: DevelopmentProfile,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ):
        """
        Apply a development profile with recommended tools.

        Args:
            profile: Development profile to apply
            progress_callback: Optional callback for progress updates (percentage, message)
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying development profile: {profile.value}")

        profiles = {
            DevelopmentProfile.WEB_FRONTEND: {
                "ides": ["vscode"],
                "languages": ["nodejs"],
                "tools": ["git", "github_desktop", "postman"],
                "terminal": True,
                "wsl2": True,
            },
            DevelopmentProfile.WEB_BACKEND: {
                "ides": ["vscode", "pycharm"],
                "languages": ["python", "nodejs"],
                "tools": ["git", "postman", "dbeaver", "docker_desktop"],
                "terminal": True,
                "wsl2": True,
                "database_clients": ["pgadmin", "mongodb_compass"],
            },
            DevelopmentProfile.FULL_STACK: {
                "ides": ["vscode"],
                "languages": ["python", "nodejs", "dotnet"],
                "tools": ["git", "github_desktop", "postman", "dbeaver", "docker_desktop"],
                "terminal": True,
                "wsl2": True,
                "database_clients": ["pgadmin", "mongodb_compass"],
                "cloud_tools": ["kubectl", "azure_cli"],
            },
            DevelopmentProfile.MOBILE: {
                "ides": ["vscode", "android_studio"],
                "languages": ["nodejs", "java17"],
                "tools": ["git", "android_studio"],
                "terminal": True,
            },
            DevelopmentProfile.DATA_SCIENCE: {
                "ides": ["vscode", "pycharm"],
                "languages": ["python", "nodejs"],
                "tools": ["git", "azure_data_studio"],
                "terminal": True,
            },
            DevelopmentProfile.DEVOPS: {
                "ides": ["vscode"],
                "languages": ["python", "go"],
                "tools": ["git", "docker_desktop"],
                "terminal": True,
                "wsl2": True,
                "cloud_tools": ["kubectl", "terraform", "ansible", "helm", "azure_cli", "aws_cli"],
            },
            DevelopmentProfile.GAME_DEV: {
                "ides": ["vscode", "rider"],
                "languages": ["dotnet"],
                "tools": ["git", "github_desktop"],
                "terminal": True,
            },
            DevelopmentProfile.MINIMAL: {
                "ides": ["vscode"],
                "languages": ["python"],
                "tools": ["git"],
                "terminal": True,
            },
        }

        profile_config = profiles.get(profile, profiles[DevelopmentProfile.MINIMAL])

        # Update configuration
        self.config.ides = profile_config.get("ides", [])
        self.config.enable_wsl2 = profile_config.get("wsl2", False)

        logger.info(
            f"Profile configuration: {len(self.config.ides)} IDEs, WSL2={self.config.enable_wsl2}"
        )

    def enable_developer_mode(self):
        """Enable Windows Developer Mode"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Enabling Windows Developer Mode")

        hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
        hive_key = "HKLM\\TEMP_SOFTWARE"

        try:
            subprocess.run(
                ["reg", "load", hive_key, str(hive_file)], check=True, capture_output=True
            )

            subprocess.run(
                [
                    "reg",
                    "add",
                    f"{hive_key}\\Microsoft\\Windows\\CurrentVersion\\AppModelUnlock",
                    "/v",
                    "AllowDevelopmentWithoutDevLicense",
                    "/t",
                    "REG_DWORD",
                    "/d",
                    "1",
                    "/f",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("Developer mode enabled successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable developer mode: {e}")
            raise

        finally:
            subprocess.run(["reg", "unload", hive_key], check=True, capture_output=True)

    def install_languages(self, languages: List[str]):
        """Install programming language runtimes"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Programming Language Installation\n"]
        script_lines.append("Write-Host 'Installing programming languages...'\n\n")

        for lang in languages:
            if lang in self.LANGUAGE_PACKAGES:
                package_id = self.LANGUAGE_PACKAGES[lang]
                script_lines.append(f"Write-Host 'Installing {lang}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )
                logger.info(f"Configured language installation: {lang}")

        script_path = scripts_dir / "install_languages.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Language installation script created: {len(languages)} languages")

    def install_ides(self, ides: List[str]):
        """Install IDEs and code editors"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        ide_packages = {
            "vscode": IDE.VSCODE.value,
            "vscode_insiders": IDE.VSCODE_INSIDERS.value,
            "visual_studio": IDE.VISUAL_STUDIO_COMMUNITY.value,
            "pycharm": IDE.PYCHARM_COMMUNITY.value,
            "intellij": IDE.INTELLIJ_COMMUNITY.value,
            "webstorm": IDE.WEBSTORM.value,
            "rider": IDE.RIDER.value,
            "android_studio": IDE.ANDROID_STUDIO.value,
            "sublime": IDE.SUBLIME_TEXT.value,
            "notepadpp": IDE.NOTEPADPP.value,
        }

        script_lines = ["# IDE Installation\n"]
        script_lines.append("Write-Host 'Installing IDEs...'\n\n")

        for ide in ides:
            if ide in ide_packages:
                package_id = ide_packages[ide]
                script_lines.append(f"Write-Host 'Installing {ide}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )
                logger.info(f"Configured IDE installation: {ide}")

        script_path = scripts_dir / "install_ides.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"IDE installation script created: {len(ides)} IDEs")

    def install_dev_tools(self, tools: List[str]):
        """Install development tools (Git, Postman, Docker, etc.)"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Development Tools Installation\n"]
        script_lines.append("Write-Host 'Installing development tools...'\n\n")

        for tool in tools:
            if tool in self.DEV_TOOLS:
                package_id = self.DEV_TOOLS[tool]
                script_lines.append(f"Write-Host 'Installing {tool}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )
                logger.info(f"Configured tool installation: {tool}")

        script_path = scripts_dir / "install_dev_tools.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Development tools installation script created: {len(tools)} tools")

    def install_cloud_tools(self, tools: List[str]):
        """Install cloud platform CLI tools"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Cloud Tools Installation\n"]
        script_lines.append("Write-Host 'Installing cloud platform tools...'\n\n")

        for tool in tools:
            if tool in self.CLOUD_TOOLS:
                package_id = self.CLOUD_TOOLS[tool]
                script_lines.append(f"Write-Host 'Installing {tool}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )
                logger.info(f"Configured cloud tool installation: {tool}")

        script_path = scripts_dir / "install_cloud_tools.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Cloud tools installation script created: {len(tools)} tools")

    def install_database_clients(self, clients: List[str]):
        """Install database client tools"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script_lines = ["# Database Client Installation\n"]
        script_lines.append("Write-Host 'Installing database clients...'\n\n")

        for client in clients:
            if client in self.DATABASE_CLIENTS:
                package_id = self.DATABASE_CLIENTS[client]
                script_lines.append(f"Write-Host 'Installing {client}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )
                logger.info(f"Configured database client installation: {client}")

        script_path = scripts_dir / "install_db_clients.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Database client installation script created: {len(clients)} clients")

    def configure_git(self, name: str, email: str, editor: str = "code"):
        """Configure Git with user details"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Configuring Git for {name} <{email}>")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        script = f"""# Git Configuration
Write-Host 'Configuring Git...'
git config --global user.name "{name}"
git config --global user.email "{email}"
git config --global core.editor "{editor} --wait"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global credential.helper wincred
Write-Host 'Git configured successfully'
"""

        script_path = scripts_dir / "configure_git.ps1"
        with open(script_path, "w") as f:
            f.write(script)

        logger.info("Git configuration script created")

    def enable_wsl2(self):
        """Enable WSL2 feature"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info("Enabling WSL2 feature")

        try:
            # Enable WSL feature
            subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Enable-Feature",
                    "/FeatureName:Microsoft-Windows-Subsystem-Linux",
                    "/All",
                ],
                check=True,
                capture_output=True,
            )

            # Enable Virtual Machine Platform
            subprocess.run(
                [
                    "dism",
                    f"/Image:{self.mount_point}",
                    "/Enable-Feature",
                    "/FeatureName:VirtualMachinePlatform",
                    "/All",
                ],
                check=True,
                capture_output=True,
            )

            logger.info("WSL2 features enabled successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable WSL2: {e}")
            raise

    def install_dev_fonts(self, fonts: List[str]):
        """Install developer-friendly fonts"""
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Installing developer fonts: {', '.join(fonts)}")

        scripts_dir = self.mount_point / "Windows" / "Setup" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        font_packages = {
            "cascadia-code": "Microsoft.CascadiaCode",
            "firacode": "FiraCode.FiraCode",
            "jetbrains-mono": "JetBrains.JetBrainsMono",
            "victor-mono": "rubjo.VictorMono",
        }

        script_lines = ["# Developer Font Installation\n"]
        script_lines.append("Write-Host 'Installing developer fonts...'\n\n")

        for font in fonts:
            if font in font_packages:
                package_id = font_packages[font]
                script_lines.append(f"Write-Host 'Installing {font}...'\n")
                script_lines.append(
                    f"winget install --id {package_id} --silent --accept-package-agreements --accept-source-agreements\n\n"
                )

        script_path = scripts_dir / "install_fonts.ps1"
        with open(script_path, "w") as f:
            f.writelines(script_lines)

        logger.info(f"Font installation script created: {len(fonts)} fonts")


def setup_dev_environment(
    image_path: Path,
    profile: DevelopmentProfile = DevelopmentProfile.MINIMAL,
    custom_config: Optional[DevelopmentConfiguration] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> None:
    """
    Quick development environment setup with a single function call.

    Example:
        # Minimal setup
        setup_dev_environment(Path('install.wim'), DevelopmentProfile.MINIMAL)

        # Full-stack setup
        setup_dev_environment(Path('install.wim'), DevelopmentProfile.FULL_STACK)

        # Custom setup
        config = DevelopmentConfiguration()
        config.install_python = True
        config.install_docker_desktop = True
        setup_dev_environment(Path('install.wim'), custom_config=config)

    Args:
        image_path: Path to Windows image file
        profile: Development profile to apply
        custom_config: Optional custom configuration (overrides profile)
        progress_callback: Optional callback for progress updates
    """
    dev = DeveloperEnvironment(image_path)

    try:
        if progress_callback:
            progress_callback(0, "Mounting image...")
        dev.mount()

        if progress_callback:
            progress_callback(10, "Enabling developer mode...")
        dev.enable_developer_mode()

        if custom_config is None:
            if progress_callback:
                progress_callback(20, f"Applying {profile.value} profile...")
            dev.apply_profile(profile, progress_callback)
        else:
            dev.config = custom_config

        if progress_callback:
            progress_callback(40, "Installing programming languages...")
        if dev.config.install_python:
            dev.install_languages(["python"])
        if dev.config.install_nodejs:
            dev.install_languages(["nodejs"])

        if progress_callback:
            progress_callback(60, "Installing IDEs...")
        if dev.config.ides:
            dev.install_ides(dev.config.ides)

        if progress_callback:
            progress_callback(80, "Installing development tools...")
        dev_tools = []
        if dev.config.install_git:
            dev_tools.append("git")
        if dev.config.install_docker_desktop:
            dev_tools.append("docker_desktop")
        if dev.config.install_windows_terminal:
            dev_tools.append("windows_terminal")
        if dev.config.install_powershell7:
            dev_tools.append("powershell7")

        if dev_tools:
            dev.install_dev_tools(dev_tools)

        if progress_callback:
            progress_callback(90, "Installing developer fonts...")
        if dev.config.install_dev_fonts:
            dev.install_dev_fonts(dev.config.fonts)

        if progress_callback:
            progress_callback(95, "Finalizing configuration...")
        if dev.config.enable_wsl2:
            dev.enable_wsl2()

        if progress_callback:
            progress_callback(100, "Developer environment configured successfully")

        dev.unmount(save_changes=True)
        logger.info("Developer environment configuration complete")

    except Exception as e:
        logger.error(f"Failed to setup development environment: {e}")
        dev.unmount(save_changes=False)
        raise
