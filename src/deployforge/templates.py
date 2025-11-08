"""Template system for image customization."""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from deployforge.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


@dataclass
class FileOperation:
    """Represents a file operation in a template."""
    action: str  # add, remove, replace
    source: Optional[str] = None
    destination: str = ""
    content: Optional[str] = None


@dataclass
class RegistryTweak:
    """Represents a registry tweak in a template."""
    hive: str
    path: str
    name: str
    data: Any
    type: str = "REG_SZ"
    action: str = "set"


@dataclass
class DriverPackage:
    """Represents a driver package in a template."""
    name: str
    path: str
    force_unsigned: bool = False


@dataclass
class UpdatePackageTemplate:
    """Represents an update package in a template."""
    kb_number: str
    path: str
    package_type: str = "msu"


@dataclass
class CustomizationTemplate:
    """
    Template for Windows image customization.

    Defines all customization operations to apply to an image.
    """
    name: str
    version: str = "1.0"
    description: str = ""
    author: str = ""

    # Operations
    files: List[FileOperation] = field(default_factory=list)
    registry: List[RegistryTweak] = field(default_factory=list)
    drivers: List[DriverPackage] = field(default_factory=list)
    updates: List[UpdatePackageTemplate] = field(default_factory=list)

    # Windows features
    features: Dict[str, bool] = field(default_factory=dict)

    # Packages to remove
    remove_packages: List[str] = field(default_factory=list)

    # Custom scripts (PowerShell)
    scripts: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)


class TemplateManager:
    """Manage customization templates."""

    def __init__(self, templates_dir: Path):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def load_template(self, template_path: Path) -> CustomizationTemplate:
        """
        Load a template from a file.

        Args:
            template_path: Path to template file (JSON or YAML)

        Returns:
            CustomizationTemplate object

        Raises:
            ValidationError: If template is invalid
        """
        template_path = Path(template_path)

        if not template_path.exists():
            raise ValidationError(f"Template not found: {template_path}")

        # Load based on extension
        with open(template_path, 'r') as f:
            if template_path.suffix.lower() in ['.json']:
                data = json.load(f)
            elif template_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                raise ValidationError(f"Unsupported template format: {template_path.suffix}")

        # Validate and create template
        template = self._parse_template(data)

        logger.info(f"Loaded template: {template.name}")
        return template

    def _parse_template(self, data: Dict[str, Any]) -> CustomizationTemplate:
        """Parse template data into CustomizationTemplate."""
        template = CustomizationTemplate(
            name=data.get('name', 'Unnamed'),
            version=data.get('version', '1.0'),
            description=data.get('description', ''),
            author=data.get('author', ''),
            tags=data.get('tags', []),
            features=data.get('features', {}),
            remove_packages=data.get('remove_packages', []),
            scripts=data.get('scripts', [])
        )

        # Parse file operations
        for file_op in data.get('files', []):
            template.files.append(FileOperation(**file_op))

        # Parse registry tweaks
        for reg_tweak in data.get('registry', []):
            template.registry.append(RegistryTweak(**reg_tweak))

        # Parse drivers
        for driver in data.get('drivers', []):
            template.drivers.append(DriverPackage(**driver))

        # Parse updates
        for update in data.get('updates', []):
            template.updates.append(UpdatePackageTemplate(**update))

        return template

    def save_template(self, template: CustomizationTemplate, output_path: Path) -> None:
        """
        Save a template to a file.

        Args:
            template: Template to save
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        data = asdict(template)

        # Save based on extension
        with open(output_path, 'w') as f:
            if output_path.suffix.lower() in ['.json']:
                json.dump(data, f, indent=2)
            elif output_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.safe_dump(data, f, default_flow_style=False)
            else:
                raise ValidationError(f"Unsupported template format: {output_path.suffix}")

        logger.info(f"Saved template to {output_path}")

    def list_templates(self) -> List[CustomizationTemplate]:
        """
        List all available templates.

        Returns:
            List of CustomizationTemplate objects
        """
        templates = []

        for template_file in self.templates_dir.glob('*.json'):
            try:
                template = self.load_template(template_file)
                templates.append(template)
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")

        for template_file in self.templates_dir.glob('*.yaml'):
            try:
                template = self.load_template(template_file)
                templates.append(template)
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")

        return templates

    def validate_template(self, template: CustomizationTemplate) -> bool:
        """
        Validate a template.

        Args:
            template: Template to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        if not template.name:
            raise ValidationError("Template name is required")

        # Validate file operations
        for file_op in template.files:
            if file_op.action not in ['add', 'remove', 'replace']:
                raise ValidationError(f"Invalid file action: {file_op.action}")

            if file_op.action in ['add', 'replace'] and not (file_op.source or file_op.content):
                raise ValidationError("File operations require source or content")

        # Validate registry tweaks
        for reg_tweak in template.registry:
            if reg_tweak.action not in ['set', 'delete']:
                raise ValidationError(f"Invalid registry action: {reg_tweak.action}")

        logger.info(f"Template {template.name} is valid")
        return True


# Pre-defined common templates
GAMING_TEMPLATE = CustomizationTemplate(
    name="Gaming Optimized",
    version="1.0",
    description="Windows optimization for gaming performance",
    author="DeployForge",
    tags=["gaming", "performance"],
    features={
        "NetFx3": True,  # .NET Framework 3.5
        "DirectPlay": True,
    },
    remove_packages=[
        "Microsoft.BingWeather",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
        "Microsoft.Messaging",
        "Microsoft.Microsoft3DViewer",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.MixedReality.Portal",
        "Microsoft.OneConnect",
        "Microsoft.People",
        "Microsoft.Print3D",
        "Microsoft.SkypeApp",
        "Microsoft.Wallet",
        "Microsoft.WindowsAlarms",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.WindowsMaps",
        "Microsoft.Xbox.TCUI",
        "Microsoft.XboxGameOverlay",
        "Microsoft.XboxGamingOverlay",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.XboxSpeechToTextOverlay",
        "Microsoft.YourPhone",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
    ],
    registry=[
        RegistryTweak(
            hive="HKLM\\SOFTWARE",
            path="Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
            name="GPU Priority",
            data="8",
            type="REG_DWORD",
            action="set"
        ),
        RegistryTweak(
            hive="HKLM\\SOFTWARE",
            path="Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile\\Tasks\\Games",
            name="Priority",
            data="6",
            type="REG_DWORD",
            action="set"
        ),
    ]
)
