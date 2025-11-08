"""
Ansible/Terraform Automation Module

Provides integration with Ansible and Terraform for infrastructure automation.

Features:
- Ansible module for image building
- Terraform provider resources
- State management
- Module documentation generation
- Example playbooks/configurations
"""

import logging
import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class AnsibleModuleResult:
    """Ansible module execution result"""
    changed: bool
    failed: bool = False
    msg: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Ansible JSON output format"""
        return {
            'changed': self.changed,
            'failed': self.failed,
            'msg': self.msg,
            'meta': self.meta
        }


class AnsibleModule:
    """
    DeployForge Ansible module.

    Allows DeployForge to be used within Ansible playbooks.

    Example playbook:
        - name: Build Windows image
          deployforge.image:
            base_image: "windows11.iso"
            output: "/images/custom.wim"
            applications:
              - name: "Office 365"
                path: "/apps/office"
            security_baseline: "CIS-Windows-11"
    """

    DOCUMENTATION = """
---
module: deployforge.image
short_description: Build Windows deployment images
description:
    - Build customized Windows deployment images
    - Supports WIM and VHDX formats
    - Integrates drivers, updates, applications
    - Applies security baselines
options:
    base_image:
        description: Path to base Windows image
        required: true
        type: str
    output:
        description: Path for output image
        required: true
        type: str
    output_format:
        description: Output format (wim or vhdx)
        required: false
        default: wim
        type: str
    drivers:
        description: List of driver paths to inject
        required: false
        type: list
    updates:
        description: List of update packages to apply
        required: false
        type: list
    applications:
        description: Applications to install
        required: false
        type: list
    security_baseline:
        description: Security baseline to apply
        required: false
        choices: ['CIS-Windows-11', 'DISA-STIG']
        type: str
"""

    EXAMPLES = """
# Build basic Windows 11 image
- name: Build Windows 11 image
  deployforge.image:
    base_image: "/iso/windows11.iso"
    output: "/images/win11-custom.wim"

# Build with applications and security
- name: Build hardened workstation image
  deployforge.image:
    base_image: "/iso/windows11.iso"
    output: "/images/win11-workstation.wim"
    applications:
      - name: "Microsoft 365"
        path: "/apps/office365"
        type: "exe"
        arguments: "/configure config.xml"
    security_baseline: "CIS-Windows-11"

# Build from configuration file
- name: Build from deployment config
  deployforge.build:
    config: "/configs/production.yaml"
"""

    def __init__(self, params: Dict[str, Any]):
        """
        Initialize Ansible module.

        Args:
            params: Module parameters from Ansible
        """
        self.params = params
        self.result = AnsibleModuleResult(changed=False)

    def run(self) -> AnsibleModuleResult:
        """
        Execute module.

        Returns:
            Module result
        """
        try:
            # Validate required parameters
            if 'base_image' not in self.params:
                self.result.failed = True
                self.result.msg = "base_image is required"
                return self.result

            if 'output' not in self.params:
                self.result.failed = True
                self.result.msg = "output is required"
                return self.result

            # Build image
            success = self._build_image()

            if success:
                self.result.changed = True
                self.result.msg = f"Image built successfully: {self.params['output']}"
                self.result.meta = {
                    'output_path': self.params['output'],
                    'format': self.params.get('output_format', 'wim')
                }
            else:
                self.result.failed = True
                self.result.msg = "Image build failed"

        except Exception as e:
            self.result.failed = True
            self.result.msg = str(e)

        return self.result

    def _build_image(self) -> bool:
        """Build image using DeployForge"""
        from deployforge.iac import DeploymentConfig, DeploymentBuilder

        # Create deployment config from Ansible parameters
        config = DeploymentConfig(
            version="1.0",
            name=self.params.get('name', 'Ansible Build'),
            base_image_source=Path(self.params['base_image']),
            output_path=Path(self.params['output']),
            output_format=self.params.get('output_format', 'wim'),
            driver_paths=[Path(d) for d in self.params.get('drivers', [])],
            update_paths=[Path(u) for u in self.params.get('updates', [])],
            applications=self.params.get('applications', []),
            security_baseline=self.params.get('security_baseline')
        )

        # Build
        builder = DeploymentBuilder()
        builder.config = config

        # Execute build stages
        for stage_name in ['init', 'base', 'drivers', 'updates', 'applications', 'security', 'finalize']:
            if not builder._execute_stage(stage_name):
                return False

        return True


class TerraformProvider:
    """
    DeployForge Terraform provider.

    Allows DeployForge resources to be managed via Terraform.

    Example Terraform configuration:
        resource "deployforge_image" "workstation" {
          base_image = "windows11.iso"
          output_path = "/images/workstation.wim"

          applications = [
            {
              name = "Microsoft 365"
              path = "/apps/office365"
            }
          ]

          security_baseline = "CIS-Windows-11"
        }
    """

    SCHEMA = {
        "version": 1,
        "type": "provider",
        "name": "deployforge",
        "resource": {
            "deployforge_image": {
                "create": "create_image",
                "read": "read_image",
                "update": "update_image",
                "delete": "delete_image",
                "schema": {
                    "base_image": {
                        "type": "string",
                        "required": True,
                        "description": "Path to base Windows image"
                    },
                    "output_path": {
                        "type": "string",
                        "required": True,
                        "description": "Path for output image"
                    },
                    "output_format": {
                        "type": "string",
                        "default": "wim",
                        "description": "Output format (wim or vhdx)"
                    },
                    "drivers": {
                        "type": "list",
                        "elem": {"type": "string"},
                        "optional": True,
                        "description": "Driver paths to inject"
                    },
                    "applications": {
                        "type": "list",
                        "optional": True,
                        "description": "Applications to install"
                    },
                    "security_baseline": {
                        "type": "string",
                        "optional": True,
                        "description": "Security baseline to apply"
                    }
                }
            }
        }
    }

    def __init__(self):
        """Initialize Terraform provider"""
        self.resources: Dict[str, Any] = {}

    def create_image(self, resource_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create image resource.

        Args:
            resource_id: Terraform resource ID
            config: Resource configuration

        Returns:
            Resource state
        """
        from deployforge.iac import DeploymentConfig, DeploymentBuilder

        logger.info(f"Creating image resource: {resource_id}")

        # Create deployment config
        deploy_config = DeploymentConfig(
            version="1.0",
            name=resource_id,
            base_image_source=Path(config['base_image']),
            output_path=Path(config['output_path']),
            output_format=config.get('output_format', 'wim'),
            driver_paths=[Path(d) for d in config.get('drivers', [])],
            applications=config.get('applications', []),
            security_baseline=config.get('security_baseline')
        )

        # Build image
        builder = DeploymentBuilder()
        builder.config = deploy_config

        success = True
        for stage in ['init', 'base', 'drivers', 'applications', 'security', 'finalize']:
            if not builder._execute_stage(stage):
                success = False
                break

        # Store resource state
        state = {
            'id': resource_id,
            'output_path': str(deploy_config.output_path),
            'created': success
        }

        self.resources[resource_id] = state

        return state

    def read_image(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Read image resource state.

        Args:
            resource_id: Resource ID

        Returns:
            Resource state or None
        """
        return self.resources.get(resource_id)

    def update_image(self, resource_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update image resource.

        Args:
            resource_id: Resource ID
            config: Updated configuration

        Returns:
            Updated resource state
        """
        # For images, update = recreate
        self.delete_image(resource_id)
        return self.create_image(resource_id, config)

    def delete_image(self, resource_id: str) -> bool:
        """
        Delete image resource.

        Args:
            resource_id: Resource ID

        Returns:
            True if deleted
        """
        if resource_id in self.resources:
            state = self.resources[resource_id]
            output_path = Path(state['output_path'])

            # Delete image file
            if output_path.exists():
                output_path.unlink()

            del self.resources[resource_id]
            logger.info(f"Deleted image resource: {resource_id}")

            return True

        return False


class AnsiblePlaybookGenerator:
    """
    Generate Ansible playbooks from deployment configurations.
    """

    @staticmethod
    def generate_playbook(
        deployment_name: str,
        tasks: List[Dict[str, Any]],
        output_path: Path
    ):
        """
        Generate Ansible playbook.

        Args:
            deployment_name: Deployment name
            tasks: List of tasks
            output_path: Path to save playbook
        """
        playbook = [
            {
                'name': deployment_name,
                'hosts': 'localhost',
                'gather_facts': False,
                'tasks': tasks
            }
        ]

        with open(output_path, 'w') as f:
            yaml.dump(playbook, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Generated Ansible playbook: {output_path}")

    @staticmethod
    def from_deployment_config(config_path: Path) -> List[Dict[str, Any]]:
        """
        Convert deployment config to Ansible tasks.

        Args:
            config_path: Path to deployment YAML

        Returns:
            List of Ansible tasks
        """
        from deployforge.iac import ConfigLoader

        loader = ConfigLoader()
        config = loader.load(config_path)

        tasks = []

        # Build image task
        task = {
            'name': f'Build {config.name}',
            'deployforge.image': {
                'base_image': str(config.base_image_source),
                'output': str(config.output_path),
                'output_format': config.output_format
            }
        }

        if config.driver_paths:
            task['deployforge.image']['drivers'] = [str(p) for p in config.driver_paths]

        if config.applications:
            task['deployforge.image']['applications'] = config.applications

        if config.security_baseline:
            task['deployforge.image']['security_baseline'] = config.security_baseline

        tasks.append(task)

        return tasks


class TerraformConfigGenerator:
    """
    Generate Terraform configurations from deployment configurations.
    """

    @staticmethod
    def generate_config(
        resource_name: str,
        config: Dict[str, Any],
        output_path: Path
    ):
        """
        Generate Terraform configuration.

        Args:
            resource_name: Resource name
            config: Resource configuration
            output_path: Path to save .tf file
        """
        tf_config = f"""
terraform {{
  required_providers {{
    deployforge = {{
      source  = "deployforge/deployforge"
      version = "~> 1.0"
    }}
  }}
}}

provider "deployforge" {{
}}

resource "deployforge_image" "{resource_name}" {{
  base_image      = "{config['base_image']}"
  output_path     = "{config['output_path']}"
  output_format   = "{config.get('output_format', 'wim')}"
"""

        if config.get('drivers'):
            tf_config += f"  drivers         = {json.dumps(config['drivers'])}\n"

        if config.get('applications'):
            tf_config += "  applications = [\n"
            for app in config['applications']:
                tf_config += "    {\n"
                for key, value in app.items():
                    if isinstance(value, str):
                        tf_config += f'      {key} = "{value}"\n'
                    else:
                        tf_config += f'      {key} = {json.dumps(value)}\n'
                tf_config += "    },\n"
            tf_config += "  ]\n"

        if config.get('security_baseline'):
            tf_config += f'  security_baseline = "{config["security_baseline"]}"\n'

        tf_config += "}\n"

        with open(output_path, 'w') as f:
            f.write(tf_config)

        logger.info(f"Generated Terraform configuration: {output_path}")

    @staticmethod
    def from_deployment_config(config_path: Path, output_path: Path):
        """
        Convert deployment config to Terraform.

        Args:
            config_path: Path to deployment YAML
            output_path: Path to save .tf file
        """
        from deployforge.iac import ConfigLoader

        loader = ConfigLoader()
        config = loader.load(config_path)

        tf_config = {
            'base_image': str(config.base_image_source),
            'output_path': str(config.output_path),
            'output_format': config.output_format,
            'drivers': [str(p) for p in config.driver_paths] if config.driver_paths else None,
            'applications': config.applications if config.applications else None,
            'security_baseline': config.security_baseline
        }

        # Remove None values
        tf_config = {k: v for k, v in tf_config.items() if v is not None}

        TerraformConfigGenerator.generate_config(
            resource_name=config.name.lower().replace(' ', '_'),
            config=tf_config,
            output_path=output_path
        )


def ansible_main():
    """
    Main entry point for Ansible module.

    This would be called by Ansible when the module is executed.
    """
    import sys

    # Read module args from stdin (Ansible convention)
    args = json.load(sys.stdin)

    # Execute module
    module = AnsibleModule(args)
    result = module.run()

    # Output result as JSON
    print(json.dumps(result.to_dict()))

    # Exit with appropriate code
    sys.exit(0 if not result.failed else 1)


def generate_ansible_module_package(output_dir: Path):
    """
    Generate Ansible module package.

    Args:
        output_dir: Directory to create module package
    """
    module_dir = output_dir / "ansible_collections" / "deployforge" / "image"
    module_dir.mkdir(parents=True, exist_ok=True)

    # Create galaxy.yml
    galaxy = {
        'namespace': 'deployforge',
        'name': 'image',
        'version': '1.0.0',
        'readme': 'README.md',
        'authors': ['DeployForge Team'],
        'description': 'Ansible collection for Windows image deployment',
        'license': ['MIT'],
        'tags': ['windows', 'deployment', 'imaging']
    }

    with open(module_dir / 'galaxy.yml', 'w') as f:
        yaml.dump(galaxy, f)

    # Create plugin structure
    plugins_dir = module_dir / 'plugins' / 'modules'
    plugins_dir.mkdir(parents=True, exist_ok=True)

    # Create module file
    module_file = plugins_dir / 'image.py'
    module_file.write_text(AnsibleModule.DOCUMENTATION + "\n\n" + AnsibleModule.EXAMPLES)

    logger.info(f"Generated Ansible module package: {module_dir}")


def generate_terraform_provider_package(output_dir: Path):
    """
    Generate Terraform provider package.

    Args:
        output_dir: Directory to create provider package
    """
    provider_dir = output_dir / "terraform-provider-deployforge"
    provider_dir.mkdir(parents=True, exist_ok=True)

    # Create schema file
    schema_file = provider_dir / "schema.json"
    with open(schema_file, 'w') as f:
        json.dump(TerraformProvider.SCHEMA, f, indent=2)

    # Create example configuration
    example_file = provider_dir / "example.tf"
    example_config = {
        'base_image': '/path/to/windows11.iso',
        'output_path': '/path/to/output.wim',
        'security_baseline': 'CIS-Windows-11'
    }

    TerraformConfigGenerator.generate_config(
        resource_name='example',
        config=example_config,
        output_path=example_file
    )

    logger.info(f"Generated Terraform provider package: {provider_dir}")


# Example usage functions
def create_ansible_playbook_from_config(config_path: Path, output_path: Path):
    """
    Create Ansible playbook from deployment configuration.

    Args:
        config_path: Path to deployment YAML
        output_path: Path to save playbook

    Example:
        create_ansible_playbook_from_config(
            Path('deployment.yaml'),
            Path('playbook.yml')
        )
    """
    tasks = AnsiblePlaybookGenerator.from_deployment_config(config_path)
    AnsiblePlaybookGenerator.generate_playbook(
        deployment_name="DeployForge Build",
        tasks=tasks,
        output_path=output_path
    )


def create_terraform_config_from_deployment(config_path: Path, output_path: Path):
    """
    Create Terraform configuration from deployment configuration.

    Args:
        config_path: Path to deployment YAML
        output_path: Path to save .tf file

    Example:
        create_terraform_config_from_deployment(
            Path('deployment.yaml'),
            Path('main.tf')
        )
    """
    TerraformConfigGenerator.from_deployment_config(config_path, output_path)
