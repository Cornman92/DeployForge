"""
Infrastructure as Code (IaC) Module

Provides YAML/JSON-based deployment automation for complete infrastructure as code.

Features:
- YAML/JSON deployment definitions
- Complete build automation
- Template variables and interpolation
- Multi-stage builds
- Schema validation
- CLI integration
"""

import logging
import yaml
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import subprocess

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Configuration file format"""

    YAML = "yaml"
    JSON = "json"


class BuildStage(Enum):
    """Build stage"""

    INIT = "init"
    PARTITIONS = "partitions"
    BASE = "base"
    DRIVERS = "drivers"
    UPDATES = "updates"
    APPLICATIONS = "applications"
    SECURITY = "security"
    CERTIFICATES = "certificates"
    GPO = "gpo"
    LANGUAGES = "languages"
    CUSTOMIZATION = "customization"
    FINALIZE = "finalize"


@dataclass
class DeploymentVariable:
    """Deployment variable for interpolation"""

    name: str
    value: Any
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {"name": self.name, "value": self.value, "description": self.description}


@dataclass
class DeploymentConfig:
    """
    Complete deployment configuration.

    Represents a full deployment definition loaded from YAML/JSON.
    """

    version: str
    name: str
    description: str = ""

    # Base image
    base_image_source: Optional[Path] = None
    base_image_index: int = 1

    # Output
    output_path: Optional[Path] = None
    output_format: str = "wim"

    # Partitions
    partition_layout: Optional[str] = None
    disk_size_gb: Optional[int] = None

    # Drivers
    driver_paths: List[Path] = field(default_factory=list)

    # Updates
    update_paths: List[Path] = field(default_factory=list)

    # Applications
    applications: List[Dict[str, Any]] = field(default_factory=list)

    # Security
    security_baseline: Optional[str] = None
    security_custom: Optional[Dict[str, Any]] = None

    # Certificates
    certificates: List[Dict[str, Any]] = field(default_factory=list)

    # GPO
    gpo_backups: List[Path] = field(default_factory=list)
    gpo_settings: Optional[Dict[str, Any]] = None

    # Languages
    languages: List[str] = field(default_factory=list)
    default_language: str = "en-US"

    # Unattend
    unattend_settings: Optional[Dict[str, Any]] = None

    # Variables
    variables: Dict[str, Any] = field(default_factory=dict)

    # Stages to run
    stages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "base_image": {
                "source": str(self.base_image_source) if self.base_image_source else None,
                "index": self.base_image_index,
            },
            "output": {
                "path": str(self.output_path) if self.output_path else None,
                "format": self.output_format,
            },
            "partitions": {"layout": self.partition_layout, "disk_size_gb": self.disk_size_gb},
            "drivers": [str(p) for p in self.driver_paths],
            "updates": [str(p) for p in self.update_paths],
            "applications": self.applications,
            "security": {"baseline": self.security_baseline, "custom": self.security_custom},
            "certificates": self.certificates,
            "gpo": {"backups": [str(p) for p in self.gpo_backups], "settings": self.gpo_settings},
            "languages": {"default": self.default_language, "additional": self.languages},
            "unattend": self.unattend_settings,
            "variables": self.variables,
            "stages": self.stages,
        }


class ConfigLoader:
    """
    Loads and validates deployment configurations.

    Example:
        loader = ConfigLoader()
        config = loader.load(Path('deployment.yaml'))
        loader.validate(config)
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self):
        """Initialize config loader"""
        self.variables: Dict[str, Any] = {}

    def load(self, config_path: Path) -> DeploymentConfig:
        """
        Load configuration from file.

        Args:
            config_path: Path to YAML or JSON file

        Returns:
            DeploymentConfig instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Detect format
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
        elif config_path.suffix.lower() == ".json":
            with open(config_path, "r") as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")

        logger.info(f"Loaded configuration from {config_path}")

        # Parse configuration
        config = self._parse_config(data, config_path.parent)

        return config

    def _parse_config(self, data: Dict[str, Any], base_path: Path) -> DeploymentConfig:
        """Parse configuration data"""
        # Extract variables first
        variables = data.get("variables", {})
        self.variables = variables

        # Perform variable interpolation
        data = self._interpolate_variables(data, variables)

        # Create config object
        config = DeploymentConfig(
            version=data.get("version", "1.0"),
            name=data.get("name", "Unnamed Deployment"),
            description=data.get("description", ""),
            variables=variables,
        )

        # Parse base image
        if "base_image" in data:
            base_img = data["base_image"]
            if isinstance(base_img, str):
                config.base_image_source = base_path / base_img
            elif isinstance(base_img, dict):
                config.base_image_source = base_path / base_img.get("source", "")
                config.base_image_index = base_img.get("index", 1)

        # Parse output
        if "output" in data:
            output = data["output"]
            if isinstance(output, str):
                config.output_path = base_path / output
            elif isinstance(output, dict):
                config.output_path = base_path / output.get("path", "")
                config.output_format = output.get("format", "wim")

        # Parse partitions
        if "partitions" in data:
            partitions = data["partitions"]
            if isinstance(partitions, dict):
                config.partition_layout = partitions.get("layout", "uefi-standard")
                config.disk_size_gb = partitions.get("disk_size_gb", 100)

        # Parse drivers
        if "drivers" in data:
            drivers = data["drivers"]
            if isinstance(drivers, list):
                config.driver_paths = [base_path / d for d in drivers]
            elif isinstance(drivers, str):
                config.driver_paths = [base_path / drivers]

        # Parse updates
        if "updates" in data:
            updates = data["updates"]
            if isinstance(updates, list):
                config.update_paths = [base_path / u for u in updates]
            elif isinstance(updates, str):
                config.update_paths = [base_path / updates]

        # Parse customizations
        if "customizations" in data:
            custom = data["customizations"]

            # Applications
            if "applications" in custom:
                config.applications = custom["applications"]

            # Security
            if "security" in custom:
                security = custom["security"]
                if isinstance(security, str):
                    config.security_baseline = security
                elif isinstance(security, dict):
                    config.security_baseline = security.get("baseline")
                    config.security_custom = security.get("custom")

            # Certificates
            if "certificates" in custom:
                config.certificates = custom["certificates"]

            # GPO
            if "gpo" in custom:
                gpo = custom["gpo"]
                if isinstance(gpo, list):
                    config.gpo_backups = [base_path / g for g in gpo]
                elif isinstance(gpo, dict):
                    config.gpo_backups = [base_path / g for g in gpo.get("backups", [])]
                    config.gpo_settings = gpo.get("settings")

            # Languages
            if "languages" in custom:
                langs = custom["languages"]
                if isinstance(langs, dict):
                    config.default_language = langs.get("default", "en-US")
                    config.languages = langs.get("additional", [])
                elif isinstance(langs, list):
                    config.languages = langs

            # Unattend
            if "unattend" in custom:
                config.unattend_settings = custom["unattend"]

        # Parse stages
        if "stages" in data:
            config.stages = data["stages"]
        else:
            # Default stages
            config.stages = ["all"]

        return config

    def _interpolate_variables(self, data: Any, variables: Dict[str, Any]) -> Any:
        """
        Recursively interpolate variables in configuration.

        Supports ${VAR_NAME} syntax.
        """
        if isinstance(data, dict):
            return {k: self._interpolate_variables(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._interpolate_variables(item, variables) for item in data]
        elif isinstance(data, str):
            # Replace ${VAR_NAME} with variable value
            pattern = r"\$\{([^}]+)\}"
            matches = re.findall(pattern, data)

            result = data
            for var_name in matches:
                if var_name in variables:
                    result = result.replace(f"${{{var_name}}}", str(variables[var_name]))
                else:
                    logger.warning(f"Variable ${{{var_name}}} not defined")

            return result
        else:
            return data

    def validate(self, config: DeploymentConfig) -> List[str]:
        """
        Validate configuration.

        Args:
            config: DeploymentConfig to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check version
        if config.version != self.SCHEMA_VERSION:
            errors.append(f"Unsupported version: {config.version} (expected {self.SCHEMA_VERSION})")

        # Check base image
        if config.base_image_source and not config.base_image_source.exists():
            errors.append(f"Base image not found: {config.base_image_source}")

        # Check output path
        if config.output_path and not config.output_path.parent.exists():
            errors.append(f"Output directory does not exist: {config.output_path.parent}")

        # Check drivers
        for driver_path in config.driver_paths:
            if not driver_path.exists():
                errors.append(f"Driver path not found: {driver_path}")

        # Check updates
        for update_path in config.update_paths:
            if not update_path.exists():
                errors.append(f"Update path not found: {update_path}")

        # Check GPO backups
        for gpo_path in config.gpo_backups:
            if not gpo_path.exists():
                errors.append(f"GPO backup not found: {gpo_path}")

        if errors:
            logger.error(f"Configuration validation failed with {len(errors)} errors")
        else:
            logger.info("Configuration validation passed")

        return errors

    def save(self, config: DeploymentConfig, output_path: Path, format: str = "yaml"):
        """
        Save configuration to file.

        Args:
            config: DeploymentConfig to save
            output_path: Path to save file
            format: Output format ('yaml' or 'json')
        """
        data = config.to_dict()

        if format == "yaml":
            with open(output_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        elif format == "json":
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Saved configuration to {output_path}")


class DeploymentBuilder:
    """
    Builds Windows deployments from configuration files.

    Example:
        builder = DeploymentBuilder()
        builder.build(Path('deployment.yaml'))
    """

    def __init__(self):
        """Initialize deployment builder"""
        self.config: Optional[DeploymentConfig] = None
        self.loader = ConfigLoader()

    def build(self, config_path: Path, dry_run: bool = False) -> bool:
        """
        Build deployment from configuration.

        Args:
            config_path: Path to configuration file
            dry_run: If True, validate but don't execute

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load configuration
            self.config = self.loader.load(config_path)

            # Validate
            errors = self.loader.validate(self.config)
            if errors:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                return False

            if dry_run:
                logger.info("Dry run mode - validation successful, build not executed")
                return True

            # Execute build stages
            logger.info(f"Starting build: {self.config.name}")

            stages_to_run = self.config.stages
            if "all" in stages_to_run:
                stages_to_run = [stage.value for stage in BuildStage]

            for stage_name in stages_to_run:
                if not self._execute_stage(stage_name):
                    logger.error(f"Build failed at stage: {stage_name}")
                    return False

            logger.info(f"Build completed successfully: {self.config.output_path}")
            return True

        except Exception as e:
            logger.error(f"Build failed: {e}")
            return False

    def _execute_stage(self, stage_name: str) -> bool:
        """Execute a build stage"""
        logger.info(f"Executing stage: {stage_name}")

        try:
            if stage_name == BuildStage.INIT.value:
                return self._stage_init()
            elif stage_name == BuildStage.PARTITIONS.value:
                return self._stage_partitions()
            elif stage_name == BuildStage.BASE.value:
                return self._stage_base()
            elif stage_name == BuildStage.DRIVERS.value:
                return self._stage_drivers()
            elif stage_name == BuildStage.UPDATES.value:
                return self._stage_updates()
            elif stage_name == BuildStage.APPLICATIONS.value:
                return self._stage_applications()
            elif stage_name == BuildStage.SECURITY.value:
                return self._stage_security()
            elif stage_name == BuildStage.CERTIFICATES.value:
                return self._stage_certificates()
            elif stage_name == BuildStage.GPO.value:
                return self._stage_gpo()
            elif stage_name == BuildStage.LANGUAGES.value:
                return self._stage_languages()
            elif stage_name == BuildStage.CUSTOMIZATION.value:
                return self._stage_customization()
            elif stage_name == BuildStage.FINALIZE.value:
                return self._stage_finalize()
            else:
                logger.warning(f"Unknown stage: {stage_name}")
                return True

        except Exception as e:
            logger.error(f"Stage {stage_name} failed: {e}")
            return False

    def _stage_init(self) -> bool:
        """Initialize build environment"""
        logger.info("Initializing build environment...")

        # Create output directory
        if self.config.output_path:
            self.config.output_path.parent.mkdir(parents=True, exist_ok=True)

        return True

    def _stage_partitions(self) -> bool:
        """Create partition layout"""
        if not self.config.partition_layout:
            logger.info("No partition layout specified, skipping")
            return True

        logger.info(f"Creating partition layout: {self.config.partition_layout}")

        # Import and use partition module
        from deployforge.partitions import PartitionManager

        pm = PartitionManager(self.config.output_path)

        if self.config.partition_layout == "uefi-standard":
            pm.create_standard_windows_layout(
                disk_size_gb=self.config.disk_size_gb or 100, include_recovery=True
            )
        elif self.config.partition_layout == "bios-legacy":
            pm.create_standard_windows_layout(
                disk_size_gb=self.config.disk_size_gb or 100, include_recovery=False
            )

        return True

    def _stage_base(self) -> bool:
        """Copy base image"""
        if not self.config.base_image_source:
            logger.error("No base image specified")
            return False

        logger.info(f"Copying base image: {self.config.base_image_source}")

        # Copy base image to output
        import shutil

        shutil.copy2(self.config.base_image_source, self.config.output_path)

        return True

    def _stage_drivers(self) -> bool:
        """Inject drivers"""
        if not self.config.driver_paths:
            logger.info("No drivers specified, skipping")
            return True

        logger.info(f"Injecting {len(self.config.driver_paths)} driver packages")

        from deployforge.drivers import DriverManager

        dm = DriverManager(self.config.output_path)
        dm.mount()

        for driver_path in self.config.driver_paths:
            dm.add_driver(driver_path)

        dm.unmount(save_changes=True)

        return True

    def _stage_updates(self) -> bool:
        """Apply updates"""
        if not self.config.update_paths:
            logger.info("No updates specified, skipping")
            return True

        logger.info(f"Applying {len(self.config.update_paths)} updates")

        from deployforge.updates import UpdateManager

        um = UpdateManager(self.config.output_path)
        um.mount()

        for update_path in self.config.update_paths:
            um.add_update(update_path)

        um.unmount(save_changes=True)

        return True

    def _stage_applications(self) -> bool:
        """Install applications"""
        if not self.config.applications:
            logger.info("No applications specified, skipping")
            return True

        logger.info(f"Installing {len(self.config.applications)} applications")

        from deployforge.applications import ApplicationInjector, AppPackage, InstallType

        ai = ApplicationInjector(self.config.output_path)
        ai.mount()

        for app_config in self.config.applications:
            app = AppPackage(
                name=app_config.get("name", ""),
                installer=Path(app_config.get("source", "")),
                install_type=InstallType(app_config.get("type", "msi")),
                arguments=app_config.get("arguments", ""),
            )
            ai.add_application(app)

        ai.unmount(save_changes=True)

        return True

    def _stage_security(self) -> bool:
        """Apply security hardening"""
        if not self.config.security_baseline and not self.config.security_custom:
            logger.info("No security settings specified, skipping")
            return True

        logger.info("Applying security hardening")

        from deployforge.security import SecurityBaseline

        sb = SecurityBaseline(self.config.output_path)
        sb.mount()

        if self.config.security_baseline:
            if self.config.security_baseline == "CIS-Windows-11-Enterprise":
                profile = SecurityBaseline.load_cis_windows11_enterprise()
                sb.apply_profile(profile)
            elif self.config.security_baseline == "DISA-STIG-Win11":
                profile = SecurityBaseline.load_disa_stig()
                sb.apply_profile(profile)

        sb.unmount(save_changes=True)

        return True

    def _stage_certificates(self) -> bool:
        """Install certificates"""
        if not self.config.certificates:
            logger.info("No certificates specified, skipping")
            return True

        logger.info(f"Installing {len(self.config.certificates)} certificates")

        from deployforge.certificates import CertificateManager, CertificateStore

        cm = CertificateManager(self.config.output_path)
        cm.mount()

        for cert_config in self.config.certificates:
            cert_path = Path(cert_config.get("path", ""))
            store = CertificateStore(cert_config.get("store", "Root"))
            cm.add_certificate(cert_path, store)

        cm.unmount(save_changes=True)

        return True

    def _stage_gpo(self) -> bool:
        """Apply GPO settings"""
        if not self.config.gpo_backups and not self.config.gpo_settings:
            logger.info("No GPO settings specified, skipping")
            return True

        logger.info("Applying GPO settings")

        from deployforge.gpo import GroupPolicyManager

        gpm = GroupPolicyManager(self.config.output_path)
        gpm.mount()

        for gpo_backup in self.config.gpo_backups:
            gpm.import_gpo(gpo_backup)

        if self.config.gpo_settings:
            for policy_name, settings in self.config.gpo_settings.items():
                gpm.set_policy(policy_name, settings)

        gpm.unmount(save_changes=True)

        return True

    def _stage_languages(self) -> bool:
        """Install language packs"""
        if not self.config.languages:
            logger.info("No language packs specified, skipping")
            return True

        logger.info(f"Installing {len(self.config.languages)} language packs")

        from deployforge.languages import LanguagePackManager

        lpm = LanguagePackManager(self.config.output_path)
        lpm.mount()

        for lang in self.config.languages:
            # Language packs would need to be sourced
            logger.info(f"Would install language: {lang}")

        lpm.set_default_language(self.config.default_language)
        lpm.unmount(save_changes=True)

        return True

    def _stage_customization(self) -> bool:
        """Apply unattend and customizations"""
        if not self.config.unattend_settings:
            logger.info("No unattend settings specified, skipping")
            return True

        logger.info("Applying unattend customizations")

        from deployforge.unattend import UnattendGenerator, UnattendConfig

        config = UnattendConfig()

        # Apply unattend settings from config
        if "computer_name" in self.config.unattend_settings:
            config.network_settings.computer_name = self.config.unattend_settings["computer_name"]

        # Generate and inject unattend.xml
        generator = UnattendGenerator(config)
        unattend_path = self.config.output_path.parent / "unattend.xml"
        generator.save(unattend_path)

        return True

    def _stage_finalize(self) -> bool:
        """Finalize build"""
        logger.info("Finalizing build...")

        # Optimize image
        logger.info("Optimizing image...")

        # Export image info
        logger.info(f"Build complete: {self.config.output_path}")

        return True


def build_from_config(config_path: Path, dry_run: bool = False) -> bool:
    """
    Quick build from configuration file.

    Args:
        config_path: Path to YAML/JSON configuration
        dry_run: If True, validate only

    Returns:
        True if successful

    Example:
        success = build_from_config(Path('deployment.yaml'))
    """
    builder = DeploymentBuilder()
    return builder.build(config_path, dry_run=dry_run)
