"""
Preset Management System

Presets are saved configurations that can be applied to images.
Unlike profiles (which are predefined), presets are user-created and customizable.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class PresetAction:
    """Represents a single action in a preset."""
    module: str  # e.g., 'gaming', 'debloat', 'themes'
    action: str  # e.g., 'apply_profile', 'remove_bloatware', 'set_theme'
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Preset:
    """A preset configuration."""
    name: str
    description: str
    version: str = "1.0"
    author: str = ""
    created: str = ""
    actions: List[PresetAction] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    base_profile: Optional[str] = None

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()


class PresetManager:
    """Manages preset configurations."""

    def __init__(self, presets_dir: Optional[Path] = None):
        """
        Initialize preset manager.

        Args:
            presets_dir: Directory for preset storage
        """
        self.presets_dir = presets_dir or Path.home() / '.deployforge' / 'presets'
        self.presets_dir.mkdir(parents=True, exist_ok=True)

        # Create example presets on first run
        self._create_example_presets()

    def _create_example_presets(self):
        """Create example presets if none exist."""
        if not list(self.presets_dir.glob('*.json')):
            # Gaming preset
            gaming_preset = Preset(
                name="High-Performance Gaming",
                description="Optimized for competitive gaming with minimal latency",
                author="DeployForge",
                tags=["gaming", "performance"],
                actions=[
                    PresetAction(
                        module="gaming",
                        action="apply_profile",
                        parameters={"profile": "competitive"}
                    ),
                    PresetAction(
                        module="debloat",
                        action="remove_bloatware",
                        parameters={"level": "moderate"}
                    ),
                    PresetAction(
                        module="network",
                        action="optimize_for_gaming",
                        parameters={}
                    ),
                    PresetAction(
                        module="themes",
                        action="set_theme",
                        parameters={"theme": "dark"}
                    )
                ]
            )
            self.save_preset(gaming_preset)

            # Privacy-focused preset
            privacy_preset = Preset(
                name="Privacy Hardened",
                description="Maximum privacy with telemetry disabled and tracking blocked",
                author="DeployForge",
                tags=["privacy", "security"],
                actions=[
                    PresetAction(
                        module="debloat",
                        action="remove_bloatware",
                        parameters={"level": "aggressive"}
                    ),
                    PresetAction(
                        module="privacy_hardening",
                        action="disable_telemetry",
                        parameters={}
                    ),
                    PresetAction(
                        module="privacy_hardening",
                        action="disable_advertising_id",
                        parameters={}
                    ),
                    PresetAction(
                        module="privacy_hardening",
                        action="configure_dns_over_https",
                        parameters={}
                    )
                ]
            )
            self.save_preset(privacy_preset)

            # Development preset
            dev_preset = Preset(
                name="Full Stack Developer",
                description="Complete development environment with WSL2, Docker, and tools",
                author="DeployForge",
                tags=["development", "programming"],
                actions=[
                    PresetAction(
                        module="devenv",
                        action="configure_developer_mode",
                        parameters={}
                    ),
                    PresetAction(
                        module="features",
                        action="enable_wsl2",
                        parameters={}
                    ),
                    PresetAction(
                        module="features",
                        action="enable_hyperv",
                        parameters={}
                    ),
                    PresetAction(
                        module="packages",
                        action="install_packages",
                        parameters={
                            "packages": ["vscode", "git", "docker-desktop", "python", "nodejs"]
                        }
                    )
                ]
            )
            self.save_preset(dev_preset)

    def create_preset(self, name: str, base_profile: Optional[str] = None) -> Preset:
        """
        Create a new preset.

        Args:
            name: Preset name
            base_profile: Optional base profile to extend

        Returns:
            New preset instance
        """
        preset = Preset(
            name=name,
            description=f"Custom preset: {name}",
            base_profile=base_profile
        )

        return preset

    def save_preset(self, preset: Preset):
        """
        Save a preset to disk.

        Args:
            preset: Preset to save
        """
        # Sanitize name for filename
        filename = preset.name.lower().replace(' ', '_').replace('/', '_')
        preset_path = self.presets_dir / f"{filename}.json"

        with open(preset_path, 'w') as f:
            json.dump(asdict(preset), f, indent=2)

        logger.info(f"Saved preset: {preset.name}")

    def load_preset(self, name: str) -> Preset:
        """
        Load a preset by name.

        Args:
            name: Preset name or filename

        Returns:
            Loaded preset
        """
        # Try exact filename first
        preset_path = self.presets_dir / f"{name}.json"

        if not preset_path.exists():
            # Try sanitized name
            filename = name.lower().replace(' ', '_').replace('/', '_')
            preset_path = self.presets_dir / f"{filename}.json"

        if not preset_path.exists():
            raise ValueError(f"Preset not found: {name}")

        with open(preset_path, 'r') as f:
            data = json.load(f)

        # Convert actions
        if 'actions' in data:
            data['actions'] = [PresetAction(**action) for action in data['actions']]

        return Preset(**data)

    def list_presets(self) -> List[Dict[str, Any]]:
        """
        List all available presets.

        Returns:
            List of preset information
        """
        presets = []

        for preset_file in self.presets_dir.glob('*.json'):
            try:
                preset = self.load_preset(preset_file.stem)
                presets.append({
                    'name': preset.name,
                    'description': preset.description,
                    'author': preset.author,
                    'tags': preset.tags,
                    'actions_count': len(preset.actions),
                    'created': preset.created,
                    'file': preset_file.name
                })
            except Exception as e:
                logger.warning(f"Failed to load preset {preset_file}: {e}")

        return presets

    def delete_preset(self, name: str):
        """
        Delete a preset.

        Args:
            name: Preset name
        """
        filename = name.lower().replace(' ', '_').replace('/', '_')
        preset_path = self.presets_dir / f"{filename}.json"

        if preset_path.exists():
            preset_path.unlink()
            logger.info(f"Deleted preset: {name}")
        else:
            raise ValueError(f"Preset not found: {name}")

    def apply_preset(self, image_path: Path, preset_name: str, output_path: Optional[Path] = None):
        """
        Apply a preset to an image.

        Args:
            image_path: Source image path
            preset_name: Preset name to apply
            output_path: Output image path (optional)
        """
        preset = self.load_preset(preset_name)

        logger.info(f"Applying preset: {preset.name}")
        logger.info(f"Description: {preset.description}")
        logger.info(f"Actions: {len(preset.actions)}")

        # Copy image if output path specified
        working_image = output_path if output_path else image_path
        if output_path and output_path != image_path:
            import shutil
            logger.info(f"Copying image to: {output_path}")
            shutil.copy2(image_path, output_path)

        # Apply base profile if specified
        if preset.base_profile:
            logger.info(f"Applying base profile: {preset.base_profile}")
            from deployforge.cli.profiles import apply_profile
            apply_profile(working_image, preset.base_profile)

        # Apply each action
        for i, action in enumerate(preset.actions, 1):
            logger.info(f"Action {i}/{len(preset.actions)}: {action.module}.{action.action}")

            try:
                self._execute_action(working_image, action)
            except Exception as e:
                logger.error(f"Action failed: {e}")
                raise

        logger.info(f"Preset applied successfully: {preset.name}")

    def _execute_action(self, image_path: Path, action: PresetAction):
        """
        Execute a preset action.

        Args:
            image_path: Image to modify
            action: Action to execute
        """
        # Import required modules dynamically
        module_map = {
            'gaming': 'deployforge.gaming',
            'debloat': 'deployforge.debloat',
            'themes': 'deployforge.themes',
            'packages': 'deployforge.packages',
            'features': 'deployforge.features',
            'optimizer': 'deployforge.optimizer',
            'network': 'deployforge.network',
            'privacy_hardening': 'deployforge.privacy_hardening',
            'devenv': 'deployforge.devenv',
            'creative': 'deployforge.creative',
            'launchers': 'deployforge.launchers',
            'browsers': 'deployforge.browsers',
            'backup': 'deployforge.backup',
            'security': 'deployforge.security',
            'applications': 'deployforge.applications'
        }

        if action.module not in module_map:
            raise ValueError(f"Unknown module: {action.module}")

        # Import module
        import importlib
        module = importlib.import_module(module_map[action.module])

        # Get class name from module
        class_map = {
            'gaming': 'GamingOptimizer',
            'debloat': 'DebloatManager',
            'themes': 'ThemeManager',
            'packages': 'PackageManager',
            'features': 'FeatureManager',
            'optimizer': 'SystemOptimizer',
            'network': 'NetworkOptimizer',
            'privacy_hardening': 'PrivacyHardening',
            'devenv': 'DeveloperEnvironment',
            'creative': 'CreativeSuite',
            'launchers': 'GamingLaunchers',
            'browsers': 'BrowserBundler',
            'backup': 'BackupIntegration',
            'security': 'SecurityHardening',
            'applications': 'ApplicationInjector'
        }

        class_name = class_map.get(action.module)
        if not class_name:
            raise ValueError(f"No class mapping for module: {action.module}")

        # Create instance
        cls = getattr(module, class_name)
        instance = cls(image_path)

        # Mount image
        instance.mount()

        try:
            # Execute action
            method = getattr(instance, action.action)
            method(**action.parameters)
        finally:
            # Unmount image
            instance.unmount(save_changes=True)

    def export_preset(self, preset_name: str, output_path: Path, format: str = 'json'):
        """
        Export a preset to a file.

        Args:
            preset_name: Preset name
            output_path: Output file path
            format: Export format (json or yaml)
        """
        preset = self.load_preset(preset_name)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'yaml':
            with open(output_path, 'w') as f:
                yaml.dump(asdict(preset), f, default_flow_style=False)
        else:
            with open(output_path, 'w') as f:
                json.dump(asdict(preset), f, indent=2)

        logger.info(f"Exported preset to: {output_path}")

    def import_preset(self, import_path: Path):
        """
        Import a preset from a file.

        Args:
            import_path: Path to preset file
        """
        import_path = Path(import_path)

        if not import_path.exists():
            raise FileNotFoundError(f"File not found: {import_path}")

        # Load based on extension
        if import_path.suffix == '.yaml' or import_path.suffix == '.yml':
            with open(import_path, 'r') as f:
                data = yaml.safe_load(f)
        else:
            with open(import_path, 'r') as f:
                data = json.load(f)

        # Convert actions
        if 'actions' in data:
            data['actions'] = [PresetAction(**action) for action in data['actions']]

        preset = Preset(**data)
        self.save_preset(preset)

        logger.info(f"Imported preset: {preset.name}")


def create_preset_from_config(config_path: Path) -> Preset:
    """
    Create a preset from a configuration file.

    Args:
        config_path: Path to configuration file (JSON or YAML)

    Returns:
        Created preset
    """
    config_path = Path(config_path)

    if config_path.suffix in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
    else:
        with open(config_path, 'r') as f:
            data = json.load(f)

    # Convert actions
    if 'actions' in data:
        data['actions'] = [PresetAction(**action) for action in data['actions']]

    return Preset(**data)
