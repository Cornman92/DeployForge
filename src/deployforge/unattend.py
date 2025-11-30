"""
Windows Answer File (unattend.xml) Generation for DeployForge

This module provides functionality for creating and customizing Windows answer files
for automated deployment. Answer files automate the Windows Setup process.

Features:
- Complete unattend.xml generation
- All configuration passes (windowsPE, offlineServicing, specialize, oobeSystem)
- User account creation
- Product key and licensing
- Regional settings
- Disk partitioning automation
- Network configuration
- Component customization
- FirstLogonCommands and RunSynchronous

References:
- https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/update-windows-settings-and-scripts-create-your-own-answer-file-sxs
"""

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import xml.dom.minidom as minidom

logger = logging.getLogger(__name__)


class ConfigPass(Enum):
    """Windows Setup configuration passes"""

    WINDOWS_PE = "windowsPE"
    OFFLINE_SERVICING = "offlineServicing"
    SPECIALIZE = "specialize"
    GENERALIZE = "generalize"
    AUDIT_SYSTEM = "auditSystem"
    AUDIT_USER = "auditUser"
    OOBE_SYSTEM = "oobeSystem"


class ProcessorArchitecture(Enum):
    """Processor architectures"""

    AMD64 = "amd64"
    X86 = "x86"
    ARM64 = "arm64"


class ImageLanguage(Enum):
    """Common languages"""

    EN_US = "en-US"
    EN_GB = "en-GB"
    DE_DE = "de-DE"
    FR_FR = "fr-FR"
    ES_ES = "es-ES"
    IT_IT = "it-IT"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"
    PT_BR = "pt-BR"
    ZH_CN = "zh-CN"
    ZH_TW = "zh-TW"


@dataclass
class UserAccount:
    """User account configuration"""

    username: str
    password: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    group: str = "Administrators"
    password_never_expires: bool = False
    plaintext_password: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "username": self.username,
            "display_name": self.display_name or self.username,
            "description": self.description,
            "group": self.group,
            "password_never_expires": self.password_never_expires,
        }


@dataclass
class RegionalSettings:
    """Regional and language settings"""

    input_locale: str = "en-US"
    system_locale: str = "en-US"
    ui_language: str = "en-US"
    user_locale: str = "en-US"
    time_zone: str = "Pacific Standard Time"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "InputLocale": self.input_locale,
            "SystemLocale": self.system_locale,
            "UILanguage": self.ui_language,
            "UserLocale": self.user_locale,
            "TimeZone": self.time_zone,
        }


@dataclass
class NetworkSettings:
    """Network configuration"""

    computer_name: Optional[str] = None
    domain: Optional[str] = None
    domain_username: Optional[str] = None
    domain_password: Optional[str] = None
    workgroup: str = "WORKGROUP"
    enable_dhcp: bool = True
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "computer_name": self.computer_name,
            "domain": self.domain,
            "workgroup": self.workgroup,
            "enable_dhcp": self.enable_dhcp,
            "ip_address": self.ip_address,
            "subnet_mask": self.subnet_mask,
            "gateway": self.gateway,
            "dns_servers": self.dns_servers,
        }


@dataclass
class OOBESettings:
    """Out-of-Box Experience settings"""

    hide_eula_page: bool = True
    hide_oem_registration_page: bool = True
    hide_online_account_screens: bool = True
    hide_wireless_setup: bool = True
    protect_your_pc: int = 3  # Disable
    skip_machine_oobe: bool = False
    skip_user_oobe: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "HideEULAPage": self.hide_eula_page,
            "HideOEMRegistrationPage": self.hide_oem_registration_page,
            "HideOnlineAccountScreens": self.hide_online_account_screens,
            "HideWirelessSetupInOOBE": self.hide_wireless_setup,
            "ProtectYourPC": self.protect_your_pc,
            "SkipMachineOOBE": self.skip_machine_oobe,
            "SkipUserOOBE": self.skip_user_oobe,
        }


@dataclass
class DiskConfiguration:
    """Disk partition configuration for automated partitioning"""

    disk_id: int = 0
    will_wipe_disk: bool = True
    partitions: List[Dict[str, Any]] = field(default_factory=list)

    def add_efi_partition(self, size_mb: int = 100):
        """Add EFI system partition"""
        self.partitions.append(
            {
                "Order": len(self.partitions) + 1,
                "Type": "EFI",
                "Size": size_mb,
                "Format": "FAT32",
                "Label": "System",
            }
        )

    def add_msr_partition(self, size_mb: int = 16):
        """Add Microsoft Reserved partition"""
        self.partitions.append({"Order": len(self.partitions) + 1, "Type": "MSR", "Size": size_mb})

    def add_windows_partition(self, size_mb: Optional[int] = None, label: str = "Windows"):
        """Add Windows partition (None = use remaining space)"""
        self.partitions.append(
            {
                "Order": len(self.partitions) + 1,
                "Type": "Primary",
                "Size": size_mb,
                "Format": "NTFS",
                "Label": label,
                "Letter": "C",
            }
        )

    def add_recovery_partition(self, size_mb: int = 500):
        """Add recovery partition"""
        self.partitions.append(
            {
                "Order": len(self.partitions) + 1,
                "Type": "Recovery",
                "Size": size_mb,
                "Format": "NTFS",
                "Label": "Recovery",
            }
        )


@dataclass
class UnattendConfig:
    """Complete unattend.xml configuration"""

    # Basic settings
    architecture: ProcessorArchitecture = ProcessorArchitecture.AMD64
    product_key: Optional[str] = None
    organization: Optional[str] = None
    owner: Optional[str] = None

    # Regional settings
    regional_settings: RegionalSettings = field(default_factory=RegionalSettings)

    # Network settings
    network_settings: NetworkSettings = field(default_factory=NetworkSettings)

    # User accounts
    user_accounts: List[UserAccount] = field(default_factory=list)

    # OOBE settings
    oobe_settings: OOBESettings = field(default_factory=OOBESettings)

    # Disk configuration
    disk_configuration: Optional[DiskConfiguration] = None

    # First logon commands
    first_logon_commands: List[str] = field(default_factory=list)

    # RunSynchronous commands (during setup)
    synchronous_commands: List[str] = field(default_factory=list)

    # Additional components to enable/disable
    components: Dict[str, bool] = field(default_factory=dict)

    def add_user(
        self, username: str, password: str, group: str = "Administrators", **kwargs
    ) -> UserAccount:
        """Add user account"""
        user = UserAccount(username=username, password=password, group=group, **kwargs)
        self.user_accounts.append(user)
        return user

    def add_first_logon_command(self, command: str, description: str = ""):
        """Add first logon command"""
        self.first_logon_commands.append(command)

    def add_synchronous_command(self, command: str):
        """Add synchronous command"""
        self.synchronous_commands.append(command)

    def enable_component(self, component: str):
        """Enable Windows component"""
        self.components[component] = True

    def disable_component(self, component: str):
        """Disable Windows component"""
        self.components[component] = False


class UnattendGenerator:
    """Generates Windows unattend.xml files"""

    NAMESPACES = {
        "unattend": "urn:schemas-microsoft-com:unattend",
        "wcm": "http://schemas.microsoft.com/WMIConfig/2002/State",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    def __init__(self, config: UnattendConfig):
        """
        Initialize generator

        Args:
            config: UnattendConfig object
        """
        self.config = config

    def generate(self) -> ET.Element:
        """
        Generate complete unattend.xml structure

        Returns:
            XML Element tree root
        """
        logger.info("Generating unattend.xml")

        # Create root element
        root = ET.Element("unattend")
        root.set("xmlns", self.NAMESPACES["unattend"])
        root.set("xmlns:wcm", self.NAMESPACES["wcm"])
        root.set("xmlns:xsi", self.NAMESPACES["xsi"])

        # Add configuration passes
        self._add_windowspe_settings(root)
        self._add_specialize_settings(root)
        self._add_oobesystem_settings(root)

        logger.info("unattend.xml generation complete")

        return root

    def _create_settings(self, parent: ET.Element, pass_name: str) -> ET.Element:
        """Create settings element for a configuration pass"""
        settings = ET.SubElement(parent, "settings")
        settings.set("pass", pass_name)
        return settings

    def _create_component(
        self,
        parent: ET.Element,
        name: str,
        processor_arch: str,
        public_key_token: str = "31bf3856ad364e35",
        language: str = "neutral",
        version_scope: str = "nonSxS",
    ) -> ET.Element:
        """Create component element"""
        component = ET.SubElement(parent, "component")
        component.set("name", name)
        component.set("processorArchitecture", processor_arch)
        component.set("publicKeyToken", public_key_token)
        component.set("language", language)
        component.set("versionScope", version_scope)

        return component

    def _add_windowspe_settings(self, root: ET.Element):
        """Add windowsPE configuration pass"""
        settings = self._create_settings(root, ConfigPass.WINDOWS_PE.value)

        # International settings
        intl_component = self._create_component(
            settings, "Microsoft-Windows-International-Core-WinPE", self.config.architecture.value
        )

        ET.SubElement(
            intl_component, "SetupUILanguage"
        ).text = self.config.regional_settings.ui_language
        ET.SubElement(
            intl_component, "InputLocale"
        ).text = self.config.regional_settings.input_locale
        ET.SubElement(
            intl_component, "SystemLocale"
        ).text = self.config.regional_settings.system_locale
        ET.SubElement(intl_component, "UILanguage").text = self.config.regional_settings.ui_language
        ET.SubElement(intl_component, "UserLocale").text = self.config.regional_settings.user_locale

        # Product key
        if self.config.product_key:
            setup_component = self._create_component(
                settings, "Microsoft-Windows-Setup", self.config.architecture.value
            )

            user_data = ET.SubElement(setup_component, "UserData")
            ET.SubElement(user_data, "AcceptEula").text = "true"

            product_key = ET.SubElement(user_data, "ProductKey")
            ET.SubElement(product_key, "Key").text = self.config.product_key

            if self.config.organization:
                ET.SubElement(user_data, "Organization").text = self.config.organization
            if self.config.owner:
                ET.SubElement(user_data, "FullName").text = self.config.owner

        # Disk configuration
        if self.config.disk_configuration:
            self._add_disk_configuration(settings)

    def _add_disk_configuration(self, settings: ET.Element):
        """Add disk partitioning configuration"""
        setup_component = self._create_component(
            settings, "Microsoft-Windows-Setup", self.config.architecture.value
        )

        disk_config = self.config.disk_configuration
        disk_conf = ET.SubElement(setup_component, "DiskConfiguration")

        disk = ET.SubElement(disk_conf, "Disk")
        disk.set("wcm:action", "add")

        ET.SubElement(disk, "DiskID").text = str(disk_config.disk_id)
        ET.SubElement(disk, "WillWipeDisk").text = str(disk_config.will_wipe_disk).lower()

        # Create partitions
        create_partitions = ET.SubElement(disk, "CreatePartitions")

        for part_config in disk_config.partitions:
            partition = ET.SubElement(create_partitions, "CreatePartition")
            partition.set("wcm:action", "add")

            ET.SubElement(partition, "Order").text = str(part_config["Order"])
            ET.SubElement(partition, "Type").text = part_config["Type"]

            if part_config.get("Size"):
                ET.SubElement(partition, "Size").text = str(part_config["Size"])
            else:
                ET.SubElement(partition, "Extend").text = "true"

        # Modify partitions (formatting)
        modify_partitions = ET.SubElement(disk, "ModifyPartitions")

        for idx, part_config in enumerate(disk_config.partitions, 1):
            if part_config.get("Format"):
                partition = ET.SubElement(modify_partitions, "ModifyPartition")
                partition.set("wcm:action", "add")

                ET.SubElement(partition, "Order").text = str(idx)
                ET.SubElement(partition, "PartitionID").text = str(idx)
                ET.SubElement(partition, "Format").text = part_config["Format"]

                if part_config.get("Label"):
                    ET.SubElement(partition, "Label").text = part_config["Label"]
                if part_config.get("Letter"):
                    ET.SubElement(partition, "Letter").text = part_config["Letter"]

        # Image install
        image_install = ET.SubElement(setup_component, "ImageInstall")
        os_image = ET.SubElement(image_install, "OSImage")

        install_to = ET.SubElement(os_image, "InstallTo")
        ET.SubElement(install_to, "DiskID").text = "0"
        ET.SubElement(install_to, "PartitionID").text = "3"  # Typically Windows partition

    def _add_specialize_settings(self, root: ET.Element):
        """Add specialize configuration pass"""
        settings = self._create_settings(root, ConfigPass.SPECIALIZE.value)

        # Computer name and network
        shell_setup = self._create_component(
            settings, "Microsoft-Windows-Shell-Setup", self.config.architecture.value
        )

        if self.config.network_settings.computer_name:
            ET.SubElement(
                shell_setup, "ComputerName"
            ).text = self.config.network_settings.computer_name

        # Time zone
        ET.SubElement(shell_setup, "TimeZone").text = self.config.regional_settings.time_zone

        # Product key (if not in windowsPE)
        if self.config.product_key:
            ET.SubElement(shell_setup, "ProductKey").text = self.config.product_key

        # Network identification
        identification = ET.SubElement(shell_setup, "Identification")

        if self.config.network_settings.domain:
            credentials = ET.SubElement(identification, "Credentials")
            ET.SubElement(credentials, "Domain").text = self.config.network_settings.domain
            ET.SubElement(credentials, "Username").text = (
                self.config.network_settings.domain_username or "Administrator"
            )
            ET.SubElement(credentials, "Password").text = (
                self.config.network_settings.domain_password or ""
            )

            ET.SubElement(identification, "JoinDomain").text = self.config.network_settings.domain
        else:
            ET.SubElement(
                identification, "JoinWorkgroup"
            ).text = self.config.network_settings.workgroup

    def _add_oobesystem_settings(self, root: ET.Element):
        """Add oobeSystem configuration pass"""
        settings = self._create_settings(root, ConfigPass.OOBE_SYSTEM.value)

        # Shell setup
        shell_setup = self._create_component(
            settings, "Microsoft-Windows-Shell-Setup", self.config.architecture.value
        )

        # OOBE settings
        oobe = ET.SubElement(shell_setup, "OOBE")
        oobe_config = self.config.oobe_settings

        ET.SubElement(oobe, "HideEULAPage").text = str(oobe_config.hide_eula_page).lower()
        ET.SubElement(oobe, "HideOEMRegistrationPage").text = str(
            oobe_config.hide_oem_registration_page
        ).lower()
        ET.SubElement(oobe, "HideOnlineAccountScreens").text = str(
            oobe_config.hide_online_account_screens
        ).lower()
        ET.SubElement(oobe, "HideWirelessSetupInOOBE").text = str(
            oobe_config.hide_wireless_setup
        ).lower()
        ET.SubElement(oobe, "ProtectYourPC").text = str(oobe_config.protect_your_pc)

        # User accounts
        if self.config.user_accounts:
            user_accounts = ET.SubElement(shell_setup, "UserAccounts")
            local_accounts = ET.SubElement(user_accounts, "LocalAccounts")

            for user in self.config.user_accounts:
                local_account = ET.SubElement(local_accounts, "LocalAccount")
                local_account.set("wcm:action", "add")

                ET.SubElement(local_account, "Name").text = user.username
                ET.SubElement(local_account, "DisplayName").text = (
                    user.display_name or user.username
                )
                ET.SubElement(local_account, "Group").text = user.group

                password_elem = ET.SubElement(local_account, "Password")
                ET.SubElement(password_elem, "Value").text = user.password
                ET.SubElement(password_elem, "PlainText").text = str(
                    user.plaintext_password
                ).lower()

                if user.description:
                    ET.SubElement(local_account, "Description").text = user.description

        # First logon commands
        if self.config.first_logon_commands:
            first_logon = ET.SubElement(shell_setup, "FirstLogonCommands")

            for idx, cmd in enumerate(self.config.first_logon_commands, 1):
                sync_cmd = ET.SubElement(first_logon, "SynchronousCommand")
                sync_cmd.set("wcm:action", "add")

                ET.SubElement(sync_cmd, "CommandLine").text = cmd
                ET.SubElement(sync_cmd, "Description").text = f"First logon command {idx}"
                ET.SubElement(sync_cmd, "Order").text = str(idx)

    def save(self, output_path: Path):
        """
        Generate and save unattend.xml to file

        Args:
            output_path: Output file path
        """
        root = self.generate()

        # Pretty print XML
        xml_string = ET.tostring(root, encoding="unicode")
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Remove extra blank lines
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        pretty_xml = "\n".join(lines)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        logger.info(f"Saved unattend.xml to {output_path}")


def create_basic_unattend(
    product_key: Optional[str] = None,
    username: str = "Admin",
    password: str = "P@ssw0rd",
    computer_name: str = "DESKTOP-PC",
    time_zone: str = "Pacific Standard Time",
) -> UnattendConfig:
    """
    Create basic unattend.xml configuration

    Args:
        product_key: Windows product key
        username: Local admin username
        password: Local admin password
        computer_name: Computer name
        time_zone: Time zone

    Returns:
        UnattendConfig object
    """
    config = UnattendConfig(product_key=product_key, organization="Organization", owner="Owner")

    config.regional_settings.time_zone = time_zone
    config.network_settings.computer_name = computer_name

    config.add_user(username, password, group="Administrators")

    return config


def create_enterprise_unattend(
    domain: str,
    domain_username: str,
    domain_password: str,
    product_key: Optional[str] = None,
    computer_name: Optional[str] = None,
) -> UnattendConfig:
    """
    Create enterprise domain-joined unattend.xml configuration

    Args:
        domain: Domain to join
        domain_username: Domain admin username
        domain_password: Domain admin password
        product_key: Windows product key
        computer_name: Computer name (optional, auto-generated if None)

    Returns:
        UnattendConfig object
    """
    config = UnattendConfig(product_key=product_key)

    config.network_settings.domain = domain
    config.network_settings.domain_username = domain_username
    config.network_settings.domain_password = domain_password

    if computer_name:
        config.network_settings.computer_name = computer_name

    # Skip OOBE for enterprise
    config.oobe_settings.skip_machine_oobe = True

    return config


def create_deployment_unattend_with_partitions(
    disk_size_gb: int, product_key: Optional[str] = None, include_recovery: bool = True
) -> UnattendConfig:
    """
    Create unattend.xml with automatic disk partitioning

    Args:
        disk_size_gb: Total disk size in GB
        product_key: Windows product key
        include_recovery: Include recovery partition

    Returns:
        UnattendConfig object with disk configuration
    """
    config = UnattendConfig(product_key=product_key)

    # Create disk configuration
    disk_config = DiskConfiguration()
    disk_config.add_efi_partition(100)  # 100MB EFI
    disk_config.add_msr_partition(16)  # 16MB MSR
    disk_config.add_windows_partition()  # Remaining space

    if include_recovery:
        disk_config.add_recovery_partition(500)  # 500MB recovery

    config.disk_configuration = disk_config

    # Add default user
    config.add_user("Admin", "P@ssw0rd", group="Administrators")

    return config
