"""
Tests for unattend.xml generation
"""

import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from deployforge.unattend import (
    UnattendGenerator,
    UnattendConfig,
    UserAccount,
    RegionalSettings,
    NetworkSettings,
    OOBESettings,
    DiskConfiguration,
    ProcessorArchitecture,
    create_basic_unattend,
    create_enterprise_unattend,
    create_deployment_unattend_with_partitions
)


def test_user_account_creation():
    """Test creating user account"""
    user = UserAccount(
        username="TestUser",
        password="TestPassword123",
        group="Administrators"
    )

    assert user.username == "TestUser"
    assert user.password == "TestPassword123"
    assert user.group == "Administrators"

    data = user.to_dict()
    assert data['username'] == "TestUser"
    assert data['group'] == "Administrators"


def test_regional_settings():
    """Test regional settings"""
    regional = RegionalSettings(
        input_locale="en-US",
        ui_language="en-US",
        time_zone="Pacific Standard Time"
    )

    data = regional.to_dict()
    assert data['InputLocale'] == "en-US"
    assert data['UILanguage'] == "en-US"
    assert data['TimeZone'] == "Pacific Standard Time"


def test_network_settings():
    """Test network settings"""
    network = NetworkSettings(
        computer_name="TEST-PC",
        workgroup="WORKGROUP",
        enable_dhcp=True
    )

    data = network.to_dict()
    assert data['computer_name'] == "TEST-PC"
    assert data['workgroup'] == "WORKGROUP"
    assert data['enable_dhcp'] is True


def test_oobe_settings():
    """Test OOBE settings"""
    oobe = OOBESettings(
        hide_eula_page=True,
        hide_online_account_screens=True,
        protect_your_pc=3
    )

    data = oobe.to_dict()
    assert data['HideEULAPage'] is True
    assert data['HideOnlineAccountScreens'] is True
    assert data['ProtectYourPC'] == 3


def test_disk_configuration():
    """Test disk configuration"""
    disk_config = DiskConfiguration()

    disk_config.add_efi_partition(100)
    disk_config.add_msr_partition(16)
    disk_config.add_windows_partition(label="Windows")
    disk_config.add_recovery_partition(500)

    assert len(disk_config.partitions) == 4
    assert disk_config.partitions[0]['Type'] == 'EFI'
    assert disk_config.partitions[1]['Type'] == 'MSR'
    assert disk_config.partitions[2]['Type'] == 'Primary'
    assert disk_config.partitions[3]['Type'] == 'Recovery'


def test_unattend_config_add_user():
    """Test adding users to config"""
    config = UnattendConfig()

    user = config.add_user("TestUser", "TestPassword", group="Users")

    assert len(config.user_accounts) == 1
    assert user.username == "TestUser"
    assert user.group == "Users"


def test_unattend_config_commands():
    """Test adding commands to config"""
    config = UnattendConfig()

    config.add_first_logon_command("cmd.exe /c echo test")
    config.add_synchronous_command("setup.exe /quiet")

    assert len(config.first_logon_commands) == 1
    assert len(config.synchronous_commands) == 1


def test_unattend_config_components():
    """Test enabling/disabling components"""
    config = UnattendConfig()

    config.enable_component("Windows-Defender")
    config.disable_component("Internet-Explorer")

    assert config.components["Windows-Defender"] is True
    assert config.components["Internet-Explorer"] is False


def test_basic_unattend_generation(tmp_path):
    """Test generating basic unattend.xml"""
    config = create_basic_unattend(
        username="Admin",
        password="P@ssw0rd",
        computer_name="TEST-PC",
        time_zone="Pacific Standard Time"
    )

    output_path = tmp_path / "unattend.xml"
    generator = UnattendGenerator(config)
    generator.save(output_path)

    assert output_path.exists()

    # Parse and verify XML structure
    tree = ET.parse(output_path)
    root = tree.getroot()

    assert root.tag == 'unattend'
    assert 'urn:schemas-microsoft-com:unattend' in root.attrib.values()


def test_enterprise_unattend_generation():
    """Test generating enterprise unattend.xml"""
    config = create_enterprise_unattend(
        domain="example.com",
        domain_username="Administrator",
        domain_password="DomainPassword123"
    )

    assert config.network_settings.domain == "example.com"
    assert config.network_settings.domain_username == "Administrator"
    assert config.oobe_settings.skip_machine_oobe is True


def test_deployment_unattend_with_partitions():
    """Test generating deployment unattend with partitions"""
    config = create_deployment_unattend_with_partitions(
        disk_size_gb=50,
        include_recovery=True
    )

    assert config.disk_configuration is not None
    assert len(config.disk_configuration.partitions) == 4  # EFI, MSR, Windows, Recovery
    assert len(config.user_accounts) == 1  # Default user


def test_unattend_xml_structure(tmp_path):
    """Test generated XML structure is valid"""
    config = UnattendConfig(
        architecture=ProcessorArchitecture.AMD64,
        product_key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
    )

    config.add_user("TestUser", "TestPassword")

    output_path = tmp_path / "test_unattend.xml"
    generator = UnattendGenerator(config)
    generator.save(output_path)

    # Parse XML
    tree = ET.parse(output_path)
    root = tree.getroot()

    # Check for settings nodes
    settings_nodes = root.findall('.//{urn:schemas-microsoft-com:unattend}settings')
    assert len(settings_nodes) > 0

    # Check for components
    component_nodes = root.findall('.//{urn:schemas-microsoft-com:unattend}component')
    assert len(component_nodes) > 0


def test_unattend_generator_namespace():
    """Test UnattendGenerator namespaces"""
    config = UnattendConfig()
    generator = UnattendGenerator(config)

    assert 'unattend' in generator.NAMESPACES
    assert 'wcm' in generator.NAMESPACES
    assert 'xsi' in generator.NAMESPACES


def test_product_key_configuration():
    """Test product key configuration"""
    config = UnattendConfig(
        product_key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
    )

    assert config.product_key == "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"


def test_regional_settings_in_config():
    """Test regional settings in unattend config"""
    regional = RegionalSettings(
        input_locale="de-DE",
        system_locale="de-DE",
        ui_language="de-DE",
        time_zone="W. Europe Standard Time"
    )

    config = UnattendConfig(regional_settings=regional)

    assert config.regional_settings.input_locale == "de-DE"
    assert config.regional_settings.time_zone == "W. Europe Standard Time"


def test_network_domain_configuration():
    """Test domain join configuration"""
    network = NetworkSettings(
        computer_name="WORKSTATION01",
        domain="corporate.local",
        domain_username="admin",
        domain_password="password123"
    )

    config = UnattendConfig(network_settings=network)

    assert config.network_settings.domain == "corporate.local"
    assert config.network_settings.computer_name == "WORKSTATION01"
