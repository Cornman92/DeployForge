"""
Group Policy Object (GPO) Injection Module

Provides offline GPO injection and policy configuration for Windows images.

Features:
- Import GPO backups
- Apply policies offline
- ADMX template processing
- Registry policy conversion
- Security settings
- Administrative templates
- Preferences configuration
"""

import logging
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import xml.etree.ElementTree as ET
import configparser

logger = logging.getLogger(__name__)


class PolicyScope(Enum):
    """GPO policy scope"""
    MACHINE = "Machine"
    USER = "User"


class PolicyType(Enum):
    """GPO policy type"""
    REGISTRY = "Registry"
    SECURITY = "Security"
    ADMINISTRATIVE_TEMPLATE = "Administrative Template"
    PREFERENCE = "Preference"
    SCRIPT = "Script"


@dataclass
class RegistryPolicy:
    """Registry policy setting"""
    key: str
    value_name: str
    value_data: Any
    value_type: str = "REG_DWORD"
    scope: PolicyScope = PolicyScope.MACHINE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'value_name': self.value_name,
            'value_data': self.value_data,
            'value_type': self.value_type,
            'scope': self.scope.value
        }


@dataclass
class SecurityPolicy:
    """Security policy setting"""
    policy_name: str
    policy_value: Union[str, int, bool]
    category: str = "SecurityOptions"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'policy_name': self.policy_name,
            'policy_value': self.policy_value,
            'category': self.category
        }


@dataclass
class ADMXPolicy:
    """ADMX template policy"""
    policy_path: str
    policy_name: str
    setting: Union[str, int, bool]
    scope: PolicyScope = PolicyScope.MACHINE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'policy_path': self.policy_path,
            'policy_name': self.policy_name,
            'setting': self.setting,
            'scope': self.scope.value
        }


@dataclass
class GroupPolicyObject:
    """Complete GPO definition"""
    name: str
    registry_policies: List[RegistryPolicy] = field(default_factory=list)
    security_policies: List[SecurityPolicy] = field(default_factory=list)
    admx_policies: List[ADMXPolicy] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'registry_policies': [p.to_dict() for p in self.registry_policies],
            'security_policies': [p.to_dict() for p in self.security_policies],
            'admx_policies': [p.to_dict() for p in self.admx_policies]
        }


class GroupPolicyManager:
    """
    Manages Group Policy injection into Windows images.

    Example:
        gpm = GroupPolicyManager(Path('install.wim'))
        gpm.mount()
        gpm.import_gpo(Path('gpo_backups/Corporate_Security'))
        gpm.set_policy('Password Policy', {'MinimumPasswordLength': 14})
        gpm.apply_admx_policy('Microsoft Edge', {'HomepageLocation': 'https://portal.corp.com'})
        gpm.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """
        Initialize GPO manager.

        Args:
            image_path: Path to WIM/VHDX image
            index: Image index (for WIM files)
        """
        self.image_path = image_path
        self.index = index
        self.mount_point: Optional[Path] = None
        self.gpo = GroupPolicyObject(name="DeployForge GPO")
        self._mounted = False

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """
        Mount the image.

        Args:
            mount_point: Optional custom mount point

        Returns:
            Path to mount point
        """
        if self._mounted:
            logger.warning("Image already mounted")
            return self.mount_point

        if mount_point is None:
            mount_point = Path(tempfile.mkdtemp(prefix='deployforge_gpo_'))

        mount_point.mkdir(parents=True, exist_ok=True)
        self.mount_point = mount_point

        logger.info(f"Mounting {self.image_path} to {mount_point}")

        try:
            if self.image_path.suffix.lower() == '.wim':
                subprocess.run(
                    ['dism', '/Mount-Wim', f'/WimFile:{self.image_path}',
                     f'/Index:{self.index}', f'/MountDir:{mount_point}'],
                    check=True,
                    capture_output=True
                )
            elif self.image_path.suffix.lower() in ['.vhd', '.vhdx']:
                subprocess.run(
                    ['dism', '/Mount-Image', f'/ImageFile:{self.image_path}',
                     f'/Index:{self.index}', f'/MountDir:{mount_point}'],
                    check=True,
                    capture_output=True
                )
            else:
                raise ValueError(f"Unsupported image format: {self.image_path.suffix}")

            self._mounted = True
            logger.info("Image mounted successfully")
            return mount_point

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to mount image: {e.stderr.decode()}")
            raise

    def unmount(self, save_changes: bool = True):
        """
        Unmount the image.

        Args:
            save_changes: Whether to commit changes
        """
        if not self._mounted:
            logger.warning("Image not mounted")
            return

        logger.info(f"Unmounting {self.mount_point}")

        try:
            commit_flag = '/Commit' if save_changes else '/Discard'
            subprocess.run(
                ['dism', '/Unmount-Image', f'/MountDir:{self.mount_point}', commit_flag],
                check=True,
                capture_output=True
            )

            self._mounted = False
            logger.info("Image unmounted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount image: {e.stderr.decode()}")
            raise

    def import_gpo(self, gpo_backup_path: Path):
        """
        Import GPO from backup folder.

        Args:
            gpo_backup_path: Path to GPO backup folder
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        if not gpo_backup_path.exists():
            raise FileNotFoundError(f"GPO backup not found: {gpo_backup_path}")

        logger.info(f"Importing GPO from {gpo_backup_path}")

        # Parse GPO backup structure
        # Typical structure: {GUID}/DomainSysvol/GPO/
        machine_path = gpo_backup_path / "DomainSysvol" / "GPO" / "Machine"
        user_path = gpo_backup_path / "DomainSysvol" / "GPO" / "User"

        # Import machine policies
        if machine_path.exists():
            self._import_machine_policies(machine_path)

        # Import user policies
        if user_path.exists():
            self._import_user_policies(user_path)

        logger.info("GPO import completed")

    def _import_machine_policies(self, machine_path: Path):
        """Import machine-level policies"""
        # Registry.pol
        registry_pol = machine_path / "Registry.pol"
        if registry_pol.exists():
            self._import_registry_pol(registry_pol, PolicyScope.MACHINE)

        # GptTmpl.inf (security settings)
        gpttmpl_inf = machine_path / "Microsoft" / "Windows NT" / "SecEdit" / "GptTmpl.inf"
        if gpttmpl_inf.exists():
            self._import_security_template(gpttmpl_inf)

        # Scripts
        scripts_path = machine_path / "Scripts"
        if scripts_path.exists():
            self._import_scripts(scripts_path, PolicyScope.MACHINE)

    def _import_user_policies(self, user_path: Path):
        """Import user-level policies"""
        # Registry.pol
        registry_pol = user_path / "Registry.pol"
        if registry_pol.exists():
            self._import_registry_pol(registry_pol, PolicyScope.USER)

        # Scripts
        scripts_path = user_path / "Scripts"
        if scripts_path.exists():
            self._import_scripts(scripts_path, PolicyScope.USER)

    def _import_registry_pol(self, pol_file: Path, scope: PolicyScope):
        """Import Registry.pol file"""
        # Registry.pol is a binary format - would need proper parser
        # For now, log that we would import it
        logger.info(f"Would import registry policies from {pol_file}")

        # In a real implementation, would parse the binary format
        # and convert to RegistryPolicy objects

    def _import_security_template(self, template_file: Path):
        """Import security template (.inf file)"""
        logger.info(f"Importing security template from {template_file}")

        config = configparser.ConfigParser()
        config.read(template_file)

        # Parse common security settings
        if 'System Access' in config:
            for key, value in config['System Access'].items():
                policy = SecurityPolicy(
                    policy_name=key,
                    policy_value=value,
                    category="SystemAccess"
                )
                self.gpo.security_policies.append(policy)
                self._apply_security_policy(policy)

        if 'Event Audit' in config:
            for key, value in config['Event Audit'].items():
                policy = SecurityPolicy(
                    policy_name=key,
                    policy_value=value,
                    category="EventAudit"
                )
                self.gpo.security_policies.append(policy)
                self._apply_security_policy(policy)

    def _import_scripts(self, scripts_path: Path, scope: PolicyScope):
        """Import GPO scripts"""
        logger.info(f"Importing scripts from {scripts_path}")

        # Copy scripts to image
        scripts_dest = self.mount_point / "Windows" / "System32" / "GroupPolicy"
        scripts_dest.mkdir(parents=True, exist_ok=True)

        if scope == PolicyScope.MACHINE:
            scripts_dest = scripts_dest / "Machine" / "Scripts"
        else:
            scripts_dest = scripts_dest / "User" / "Scripts"

        scripts_dest.mkdir(parents=True, exist_ok=True)

        # Copy all scripts
        for script_file in scripts_path.rglob('*'):
            if script_file.is_file():
                rel_path = script_file.relative_to(scripts_path)
                dest_file = scripts_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(script_file, dest_file)

    def set_policy(self, policy_name: str, settings: Dict[str, Any]):
        """
        Set policy by name (convenience method).

        Args:
            policy_name: Policy category name
            settings: Dictionary of settings
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Setting policy: {policy_name}")

        # Apply based on policy name
        if 'password' in policy_name.lower():
            self._apply_password_policy(settings)
        elif 'audit' in policy_name.lower():
            self._apply_audit_policy(settings)
        else:
            # Default to security policy
            for key, value in settings.items():
                policy = SecurityPolicy(
                    policy_name=key,
                    policy_value=value,
                    category=policy_name
                )
                self.gpo.security_policies.append(policy)
                self._apply_security_policy(policy)

    def _apply_password_policy(self, settings: Dict[str, Any]):
        """Apply password policy settings"""
        # Map to registry/local policy
        policy_map = {
            'MinimumPasswordLength': (r'SYSTEM\CurrentControlSet\Control\Lsa', 'MinimumPasswordLength'),
            'PasswordComplexity': (r'SYSTEM\CurrentControlSet\Control\Lsa', 'PasswordComplexity'),
            'MaximumPasswordAge': (r'SYSTEM\CurrentControlSet\Control\Lsa', 'MaximumPasswordAge'),
            'MinimumPasswordAge': (r'SYSTEM\CurrentControlSet\Control\Lsa', 'MinimumPasswordAge'),
        }

        for setting, value in settings.items():
            if setting in policy_map:
                key, value_name = policy_map[setting]
                self.add_registry_policy(
                    key=key,
                    value_name=value_name,
                    value_data=value,
                    scope=PolicyScope.MACHINE
                )

    def _apply_audit_policy(self, settings: Dict[str, Any]):
        """Apply audit policy settings"""
        for category, value in settings.items():
            policy = SecurityPolicy(
                policy_name=category,
                policy_value=value,
                category="AuditPolicy"
            )
            self.gpo.security_policies.append(policy)
            self._apply_security_policy(policy)

    def _apply_security_policy(self, policy: SecurityPolicy):
        """Apply security policy to image"""
        # Write to local security policy database
        secedit_db = self.mount_point / "Windows" / "security" / "database"
        secedit_db.mkdir(parents=True, exist_ok=True)

        # Create/update secedit.inf
        inf_path = secedit_db / "deployforge.inf"

        config = configparser.ConfigParser()
        if inf_path.exists():
            config.read(inf_path)

        # Add policy to appropriate section
        if policy.category not in config:
            config[policy.category] = {}

        config[policy.category][policy.policy_name] = str(policy.policy_value)

        with open(inf_path, 'w') as f:
            config.write(f)

        logger.info(f"Applied security policy: {policy.policy_name} = {policy.policy_value}")

    def add_registry_policy(
        self,
        key: str,
        value_name: str,
        value_data: Any,
        value_type: str = "REG_DWORD",
        scope: PolicyScope = PolicyScope.MACHINE
    ):
        """
        Add registry policy.

        Args:
            key: Registry key path (relative to hive)
            value_name: Value name
            value_data: Value data
            value_type: Registry value type
            scope: Policy scope (Machine or User)
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        policy = RegistryPolicy(
            key=key,
            value_name=value_name,
            value_data=value_data,
            value_type=value_type,
            scope=scope
        )

        self.gpo.registry_policies.append(policy)

        # Apply to registry
        self._apply_registry_policy(policy)

    def _apply_registry_policy(self, policy: RegistryPolicy):
        """Apply registry policy to image"""
        # Determine hive to load
        if policy.scope == PolicyScope.MACHINE:
            if policy.key.upper().startswith('SOFTWARE'):
                hive_file = self.mount_point / "Windows" / "System32" / "config" / "SOFTWARE"
                hive_key = "HKLM\\TEMP_SOFTWARE"
                software_prefix = 'SOFTWARE\\'
                subkey = policy.key[len(software_prefix):]
                reg_key = f"{hive_key}\\{subkey}"
            else:
                hive_file = self.mount_point / "Windows" / "System32" / "config" / "SYSTEM"
                hive_key = "HKLM\\TEMP_SYSTEM"
                reg_key = f"{hive_key}\\{policy.key}"
        else:
            # User policies would use NTUSER.DAT from default profile
            hive_file = self.mount_point / "Users" / "Default" / "NTUSER.DAT"
            hive_key = "HKLM\\TEMP_USER"
            reg_key = f"{hive_key}\\{policy.key}"

        try:
            # Load hive
            subprocess.run(['reg', 'load', hive_key, str(hive_file)], check=True, capture_output=True)

            # Set registry value
            subprocess.run([
                'reg', 'add', reg_key,
                '/v', policy.value_name,
                '/t', policy.value_type,
                '/d', str(policy.value_data),
                '/f'
            ], check=True, capture_output=True)

            logger.info(f"Applied registry policy: {policy.key}\\{policy.value_name} = {policy.value_data}")

        finally:
            # Unload hive
            subprocess.run(['reg', 'unload', hive_key], check=True, capture_output=True)

    def apply_admx_policy(
        self,
        policy_path: str,
        settings: Dict[str, Any],
        scope: PolicyScope = PolicyScope.MACHINE
    ):
        """
        Apply ADMX template policy.

        Args:
            policy_path: Policy path (e.g., 'Microsoft Edge')
            settings: Dictionary of policy settings
            scope: Policy scope
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        logger.info(f"Applying ADMX policy: {policy_path}")

        for policy_name, setting in settings.items():
            admx_policy = ADMXPolicy(
                policy_path=policy_path,
                policy_name=policy_name,
                setting=setting,
                scope=scope
            )

            self.gpo.admx_policies.append(admx_policy)

            # ADMX policies are ultimately registry-based
            # Map to registry location (this is simplified)
            reg_key = f"SOFTWARE\\Policies\\{policy_path.replace(' ', '_')}"

            self.add_registry_policy(
                key=reg_key,
                value_name=policy_name,
                value_data=setting,
                value_type="REG_SZ" if isinstance(setting, str) else "REG_DWORD",
                scope=scope
            )

    def export_gpo(self, output_path: Path):
        """
        Export GPO to JSON.

        Args:
            output_path: Path to save GPO JSON
        """
        with open(output_path, 'w') as f:
            json.dump(self.gpo.to_dict(), f, indent=2)

        logger.info(f"Exported GPO to {output_path}")

    def import_gpo_json(self, gpo_json_path: Path):
        """
        Import GPO from JSON.

        Args:
            gpo_json_path: Path to GPO JSON file
        """
        if not self._mounted:
            raise RuntimeError("Image must be mounted first")

        with open(gpo_json_path, 'r') as f:
            gpo_data = json.load(f)

        # Import registry policies
        for policy_data in gpo_data.get('registry_policies', []):
            policy = RegistryPolicy(
                key=policy_data['key'],
                value_name=policy_data['value_name'],
                value_data=policy_data['value_data'],
                value_type=policy_data.get('value_type', 'REG_DWORD'),
                scope=PolicyScope(policy_data.get('scope', 'Machine'))
            )
            self.gpo.registry_policies.append(policy)
            self._apply_registry_policy(policy)

        # Import security policies
        for policy_data in gpo_data.get('security_policies', []):
            policy = SecurityPolicy(
                policy_name=policy_data['policy_name'],
                policy_value=policy_data['policy_value'],
                category=policy_data.get('category', 'SecurityOptions')
            )
            self.gpo.security_policies.append(policy)
            self._apply_security_policy(policy)

        # Import ADMX policies
        for policy_data in gpo_data.get('admx_policies', []):
            admx_policy = ADMXPolicy(
                policy_path=policy_data['policy_path'],
                policy_name=policy_data['policy_name'],
                setting=policy_data['setting'],
                scope=PolicyScope(policy_data.get('scope', 'Machine'))
            )
            self.gpo.admx_policies.append(admx_policy)

        logger.info(f"Imported GPO from {gpo_json_path}")


def apply_standard_gpo(
    image_path: Path,
    gpo_type: str = "corporate"
) -> GroupPolicyManager:
    """
    Apply standard GPO template.

    Args:
        image_path: Path to WIM/VHDX image
        gpo_type: GPO template type ('corporate', 'secure', 'minimal')

    Returns:
        GroupPolicyManager instance

    Example:
        gpm = apply_standard_gpo(Path('install.wim'), gpo_type='corporate')
    """
    gpm = GroupPolicyManager(image_path)
    gpm.mount()

    if gpo_type == "corporate":
        # Corporate GPO settings
        gpm.set_policy('Password Policy', {
            'MinimumPasswordLength': 12,
            'PasswordComplexity': 1,
            'MaximumPasswordAge': 90
        })

        gpm.add_registry_policy(
            key=r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU',
            value_name='NoAutoUpdate',
            value_data=0
        )

    elif gpo_type == "secure":
        # Secure GPO settings
        gpm.set_policy('Password Policy', {
            'MinimumPasswordLength': 14,
            'PasswordComplexity': 1,
            'MaximumPasswordAge': 60
        })

        gpm.add_registry_policy(
            key=r'SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU',
            value_name='NoAutoUpdate',
            value_data=0
        )

        # Disable legacy protocols
        gpm.add_registry_policy(
            key=r'SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters',
            value_name='SMB1',
            value_data=0
        )

    gpm.unmount(save_changes=True)

    return gpm
