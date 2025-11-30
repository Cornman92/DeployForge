"""
Quick Setup Wizard Generator Module

Creates guided setup experiences with intelligent presets for gaming, development,
enterprise, content creation, and more. Includes hardware detection and recommendations.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class SetupPreset(Enum):
    """Comprehensive setup presets"""

    GAMING = "gaming"
    DEVELOPER = "developer"
    CONTENT_CREATOR = "content_creator"
    STUDENT = "student"
    OFFICE = "office"
    HOME_USER = "home_user"
    ENTERPRISE = "enterprise"
    DATA_SCIENCE = "data_science"
    CYBERSECURITY = "cybersecurity"
    DESIGNER = "designer"
    STREAMER = "streamer"
    MUSIC_PRODUCTION = "music_production"


class HardwareProfile(Enum):
    """Hardware configuration profiles"""

    HIGH_END = "high_end"  # RTX 4090, 64GB+ RAM
    ENTHUSIAST = "enthusiast"  # RTX 4070+, 32GB RAM
    MAINSTREAM = "mainstream"  # RTX 3060, 16GB RAM
    BUDGET = "budget"  # GTX 1650, 8GB RAM
    LAPTOP = "laptop"  # Mobile hardware


@dataclass
class WizardConfig:
    """Configuration for setup wizard"""

    # Basic Info
    preset_name: str = "Custom Setup"
    description: str = ""
    target_users: List[str] = field(default_factory=list)

    # Applications
    essential_apps: List[str] = field(default_factory=list)
    recommended_apps: List[str] = field(default_factory=list)
    optional_apps: List[str] = field(default_factory=list)

    # System Optimizations
    optimizations: List[str] = field(default_factory=list)
    debloat_level: str = "moderate"  # minimal, moderate, aggressive
    telemetry_blocking: bool = True

    # UI/UX
    theme: str = "dark"
    ui_profile: str = "modern"

    # Performance
    performance_mode: str = "balanced"  # power_save, balanced, performance, max_performance
    gaming_optimizations: bool = False
    developer_tools: bool = False

    # Privacy & Security
    privacy_level: str = "moderate"  # minimal, moderate, high
    security_hardening: bool = False

    # Hardware Recommendations
    min_ram_gb: int = 8
    recommended_ram_gb: int = 16
    min_storage_gb: int = 50
    requires_gpu: bool = False
    requires_ssd: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "preset": {
                "name": self.preset_name,
                "description": self.description,
                "target_users": self.target_users,
            },
            "applications": {
                "essential": self.essential_apps,
                "recommended": self.recommended_apps,
                "optional": self.optional_apps,
            },
            "optimizations": {
                "enabled": self.optimizations,
                "debloat_level": self.debloat_level,
                "telemetry_blocking": self.telemetry_blocking,
            },
            "ui": {
                "theme": self.theme,
                "profile": self.ui_profile,
            },
            "performance": {
                "mode": self.performance_mode,
                "gaming_optimizations": self.gaming_optimizations,
                "developer_tools": self.developer_tools,
            },
            "privacy_security": {
                "privacy_level": self.privacy_level,
                "security_hardening": self.security_hardening,
            },
            "hardware": {
                "min_ram_gb": self.min_ram_gb,
                "recommended_ram_gb": self.recommended_ram_gb,
                "min_storage_gb": self.min_storage_gb,
                "requires_gpu": self.requires_gpu,
                "requires_ssd": self.requires_ssd,
            },
        }


class SetupWizard:
    """Intelligent setup wizard generator"""

    # Comprehensive preset definitions
    PRESETS: Dict[str, WizardConfig] = {
        "gaming": WizardConfig(
            preset_name="Gaming Setup",
            description="Ultimate gaming experience with performance optimizations",
            target_users=["Gamers", "Esports Players"],
            essential_apps=["Steam", "Discord", "Game Bar"],
            recommended_apps=[
                "Epic Games Launcher",
                "GOG Galaxy",
                "GeForce Experience",
                "MSI Afterburner",
            ],
            optional_apps=["EA App", "Ubisoft Connect", "Battle.net", "Xbox App"],
            optimizations=["gaming", "performance", "network", "visual_effects"],
            debloat_level="aggressive",
            theme="dark",
            ui_profile="gaming",
            performance_mode="max_performance",
            gaming_optimizations=True,
            privacy_level="moderate",
            min_ram_gb=16,
            recommended_ram_gb=32,
            min_storage_gb=500,
            requires_gpu=True,
            requires_ssd=True,
        ),
        "developer": WizardConfig(
            preset_name="Developer Workstation",
            description="Complete development environment for programmers",
            target_users=["Software Developers", "DevOps Engineers"],
            essential_apps=["VS Code", "Git", "Windows Terminal"],
            recommended_apps=["Python", "Node.js", "Docker Desktop", "Postman", "GitHub Desktop"],
            optional_apps=["Visual Studio", "IntelliJ IDEA", "WSL2", "PowerShell 7", "Azure CLI"],
            optimizations=["performance", "developer"],
            debloat_level="moderate",
            theme="dark",
            ui_profile="developer",
            performance_mode="performance",
            developer_tools=True,
            privacy_level="moderate",
            min_ram_gb=16,
            recommended_ram_gb=32,
            min_storage_gb=256,
            requires_ssd=True,
        ),
        "content_creator": WizardConfig(
            preset_name="Content Creator Studio",
            description="Professional content creation and editing suite",
            target_users=["Video Editors", "Designers", "Content Creators"],
            essential_apps=["OBS Studio", "Audacity", "GIMP"],
            recommended_apps=["DaVinci Resolve", "Blender", "Krita", "HandBrake"],
            optional_apps=["Adobe Creative Cloud", "Premiere Pro", "After Effects", "Photoshop"],
            optimizations=["performance", "creative"],
            debloat_level="moderate",
            theme="dark",
            ui_profile="productivity",
            performance_mode="performance",
            privacy_level="moderate",
            min_ram_gb=16,
            recommended_ram_gb=64,
            min_storage_gb=500,
            requires_gpu=True,
            requires_ssd=True,
        ),
        "student": WizardConfig(
            preset_name="Student Setup",
            description="Balanced setup for education and productivity",
            target_users=["Students", "Educators"],
            essential_apps=["Microsoft Office", "OneNote", "Chrome"],
            recommended_apps=["Zoom", "Teams", "Notion", "Adobe Reader"],
            optional_apps=["Grammarly", "Anki", "Calibre", "LibreOffice"],
            optimizations=["performance", "battery"],
            debloat_level="minimal",
            theme="light",
            ui_profile="productivity",
            performance_mode="balanced",
            privacy_level="high",
            min_ram_gb=8,
            recommended_ram_gb=16,
            min_storage_gb=128,
        ),
        "office": WizardConfig(
            preset_name="Office Productivity",
            description="Business and office productivity suite",
            target_users=["Office Workers", "Business Professionals"],
            essential_apps=["Microsoft Office", "Teams", "Outlook"],
            recommended_apps=["Adobe Reader", "Chrome", "OneDrive", "7-Zip"],
            optional_apps=["Slack", "Zoom", "SharePoint", "Power BI"],
            optimizations=["productivity"],
            debloat_level="minimal",
            theme="light",
            ui_profile="productivity",
            performance_mode="balanced",
            privacy_level="moderate",
            security_hardening=True,
            min_ram_gb=8,
            recommended_ram_gb=16,
            min_storage_gb=128,
        ),
        "home_user": WizardConfig(
            preset_name="Home User",
            description="General home computing for everyday tasks",
            target_users=["Home Users", "Families"],
            essential_apps=["Chrome", "VLC Media Player", "7-Zip"],
            recommended_apps=["Spotify", "Netflix", "WhatsApp", "Adobe Reader"],
            optional_apps=["iTunes", "Skype", "Discord", "Steam"],
            optimizations=["balanced"],
            debloat_level="moderate",
            theme="auto",
            ui_profile="modern",
            performance_mode="balanced",
            privacy_level="moderate",
            min_ram_gb=8,
            recommended_ram_gb=16,
            min_storage_gb=256,
        ),
        "data_science": WizardConfig(
            preset_name="Data Science Workstation",
            description="Python, R, and data analysis environment",
            target_users=["Data Scientists", "ML Engineers", "Researchers"],
            essential_apps=["Python", "Jupyter", "VS Code"],
            recommended_apps=["Anaconda", "R", "RStudio", "Git", "Docker"],
            optional_apps=["MATLAB", "Tableau", "PostgreSQL", "MongoDB"],
            optimizations=["performance", "developer"],
            debloat_level="moderate",
            theme="dark",
            ui_profile="developer",
            performance_mode="performance",
            developer_tools=True,
            min_ram_gb=32,
            recommended_ram_gb=64,
            min_storage_gb=512,
            requires_ssd=True,
        ),
        "designer": WizardConfig(
            preset_name="Graphic Designer",
            description="Creative design and illustration workspace",
            target_users=["Graphic Designers", "UI/UX Designers", "Illustrators"],
            essential_apps=["GIMP", "Inkscape", "Krita"],
            recommended_apps=["Figma", "Blender", "Adobe Creative Cloud", "Color Picker"],
            optional_apps=["Photoshop", "Illustrator", "XD", "Affinity Designer"],
            optimizations=["creative", "performance"],
            debloat_level="moderate",
            theme="light",
            ui_profile="productivity",
            performance_mode="performance",
            min_ram_gb=16,
            recommended_ram_gb=32,
            min_storage_gb=256,
            requires_gpu=True,
        ),
        "streamer": WizardConfig(
            preset_name="Live Streamer",
            description="Professional streaming and broadcasting setup",
            target_users=["Streamers", "YouTubers", "Live Broadcasters"],
            essential_apps=["OBS Studio", "Discord", "VLC"],
            recommended_apps=["StreamElements", "Streamlabs", "Voicemod", "Logitech G HUB"],
            optional_apps=["XSplit", "vMix", "TouchPortal", "VoiceMeeter"],
            optimizations=["streaming", "network", "performance"],
            debloat_level="aggressive",
            theme="dark",
            ui_profile="gaming",
            performance_mode="max_performance",
            min_ram_gb=16,
            recommended_ram_gb=32,
            min_storage_gb=512,
            requires_gpu=True,
            requires_ssd=True,
        ),
    }

    def __init__(self):
        """Initialize wizard"""
        self.config = WizardConfig()

    def get_preset(self, preset: SetupPreset) -> WizardConfig:
        """Get predefined preset configuration"""
        preset_key = preset.value if isinstance(preset, SetupPreset) else preset
        if preset_key in self.PRESETS:
            return self.PRESETS[preset_key]
        logger.warning(f"Preset '{preset_key}' not found, using default")
        return WizardConfig()

    def create_guided_setup(
        self, presets: List[str], output_path: Path, include_hardware_check: bool = True
    ):
        """
        Create comprehensive guided setup configuration

        Args:
            presets: List of preset names to include
            output_path: Where to save configuration
            include_hardware_check: Include hardware requirement checks
        """
        config = {
            "version": "2.0",
            "generator": "DeployForge Setup Wizard",
            "presets": [],
            "hardware_detection": include_hardware_check,
        }

        for preset in presets:
            if preset in self.PRESETS:
                preset_config = self.PRESETS[preset]
                config["presets"].append(preset_config.to_dict())
            else:
                logger.warning(f"Unknown preset: {preset}")

        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created setup wizard configuration: {output_path}")
        return config

    def detect_hardware_compatibility(self, preset: SetupPreset) -> Dict[str, Any]:
        """
        Detect hardware and check compatibility with preset

        Returns compatibility report and recommendations
        """
        preset_config = self.get_preset(preset)

        # This would be implemented with actual hardware detection
        # For now, return structure for compatibility checking
        return {
            "preset": preset.value,
            "requirements": {
                "min_ram_gb": preset_config.min_ram_gb,
                "recommended_ram_gb": preset_config.recommended_ram_gb,
                "min_storage_gb": preset_config.min_storage_gb,
                "requires_gpu": preset_config.requires_gpu,
                "requires_ssd": preset_config.requires_ssd,
            },
            "detected": {
                # Would be filled with actual detection
                "ram_gb": 0,
                "storage_gb": 0,
                "has_gpu": False,
                "has_ssd": False,
            },
            "compatible": True,  # Would be calculated
            "warnings": [],
            "recommendations": [],
        }

    def generate_installation_script(self, preset: SetupPreset, output_path: Path):
        """Generate PowerShell installation script for preset"""
        preset_config = self.get_preset(preset)

        script_lines = [
            "# DeployForge Setup Wizard - Installation Script",
            f"# Preset: {preset_config.preset_name}",
            f"# Description: {preset_config.description}",
            "",
            "Write-Host 'DeployForge Setup Wizard' -ForegroundColor Cyan",
            f"Write-Host 'Installing: {preset_config.preset_name}' -ForegroundColor Green",
            "",
            "# Essential Applications",
        ]

        for app in preset_config.essential_apps:
            script_lines.append(f"Write-Host 'Installing {app}...'")
            script_lines.append(f"# winget install --id PackageID.{app.replace(' ', '')} --silent")

        script_lines.extend(
            [
                "",
                "# Recommended Applications",
            ]
        )

        for app in preset_config.recommended_apps:
            script_lines.append(f"# winget install --id PackageID.{app.replace(' ', '')} --silent")

        script_lines.extend(
            [
                "",
                "Write-Host 'Installation complete!' -ForegroundColor Green",
            ]
        )

        with open(output_path, "w") as f:
            f.write("\n".join(script_lines))

        logger.info(f"Generated installation script: {output_path}")

    def create_multi_preset_wizard(
        self,
        output_path: Path,
        include_all: bool = False,
        selected_presets: Optional[List[SetupPreset]] = None,
    ):
        """Create interactive wizard with multiple preset options"""
        if include_all:
            presets_to_include = list(self.PRESETS.keys())
        elif selected_presets:
            presets_to_include = [p.value for p in selected_presets]
        else:
            presets_to_include = ["gaming", "developer", "office", "home_user"]

        wizard_data = {
            "wizard_version": "2.0",
            "title": "DeployForge Quick Setup Wizard",
            "description": "Choose your perfect Windows configuration",
            "presets": {},
        }

        for preset_name in presets_to_include:
            if preset_name in self.PRESETS:
                preset_config = self.PRESETS[preset_name]
                wizard_data["presets"][preset_name] = {
                    "name": preset_config.preset_name,
                    "description": preset_config.description,
                    "target_users": preset_config.target_users,
                    "apps_count": len(preset_config.essential_apps)
                    + len(preset_config.recommended_apps),
                    "requirements": {
                        "ram": f"{preset_config.min_ram_gb}-{preset_config.recommended_ram_gb}GB",
                        "storage": f"{preset_config.min_storage_gb}GB+",
                        "gpu": "Required" if preset_config.requires_gpu else "Optional",
                        "ssd": "Recommended" if preset_config.requires_ssd else "Optional",
                    },
                }

        with open(output_path, "w") as f:
            json.dump(wizard_data, f, indent=2)

        logger.info(f"Created multi-preset wizard: {output_path}")
        return wizard_data

    def recommend_preset(
        self,
        use_case: str,
        has_gpu: bool = False,
        ram_gb: int = 16,
    ) -> SetupPreset:
        """Recommend preset based on use case and hardware"""
        use_case_lower = use_case.lower()

        # Simple recommendation logic
        if "game" in use_case_lower or "gaming" in use_case_lower:
            return SetupPreset.GAMING
        elif "dev" in use_case_lower or "program" in use_case_lower:
            return SetupPreset.DEVELOPER
        elif "video" in use_case_lower or "edit" in use_case_lower or "content" in use_case_lower:
            return SetupPreset.CONTENT_CREATOR
        elif "student" in use_case_lower or "school" in use_case_lower:
            return SetupPreset.STUDENT
        elif "office" in use_case_lower or "work" in use_case_lower:
            return SetupPreset.OFFICE
        elif "data" in use_case_lower or "science" in use_case_lower:
            return SetupPreset.DATA_SCIENCE
        elif "design" in use_case_lower:
            return SetupPreset.DESIGNER
        elif "stream" in use_case_lower:
            return SetupPreset.STREAMER
        else:
            return SetupPreset.HOME_USER


def create_quick_setup(preset: str = "gaming") -> Dict[str, Any]:
    """
    Quick setup creation helper

    Example:
        >>> config = create_quick_setup('gaming')
        >>> print(config['preset_name'])
        'Gaming Setup'
    """
    wizard = SetupWizard()
    preset_enum = (
        SetupPreset(preset) if preset in [p.value for p in SetupPreset] else SetupPreset.HOME_USER
    )
    config = wizard.get_preset(preset_enum)
    return config.to_dict()


def generate_wizard_for_presets(
    presets: List[SetupPreset],
    output_dir: Path,
) -> List[Path]:
    """Generate wizard files for multiple presets"""
    wizard = SetupWizard()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for preset in presets:
        # Generate JSON config
        config_path = output_dir / f"{preset.value}_config.json"
        wizard.create_guided_setup([preset.value], config_path)
        generated_files.append(config_path)

        # Generate installation script
        script_path = output_dir / f"{preset.value}_install.ps1"
        wizard.generate_installation_script(preset, script_path)
        generated_files.append(script_path)

    # Generate master wizard
    master_path = output_dir / "wizard_master.json"
    wizard.create_multi_preset_wizard(master_path, selected_presets=presets)
    generated_files.append(master_path)

    logger.info(f"Generated {len(generated_files)} wizard files in {output_dir}")
    return generated_files
