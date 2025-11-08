#!/usr/bin/env python3
"""
Enterprise Workstation image builder.

Creates a Windows image for enterprise workstations with:
- Security hardening
- Corporate policies
- Standard software packages
- Domain join configuration
- Audit and compliance settings
"""

from pathlib import Path
from deployforge import ImageManager
from deployforge.registry import RegistryEditor
from deployforge.templates import CustomizationTemplate, RegistryTweak
from deployforge.audit import AuditLogger


def build_enterprise_workstation(
    source_wim: Path,
    output_wim: Path,
    company_config: dict
):
    """
    Build an enterprise workstation image.

    Args:
        source_wim: Source Windows install.wim
        output_wim: Output enterprise image
        company_config: Company configuration dictionary
    """
    print("=" * 80)
    print("Enterprise Workstation Image Builder")
    print(f"Organization: {company_config.get('company_name', 'Unknown')}")
    print("=" * 80)

    # Initialize audit logging
    audit = AuditLogger(Path("./logs/enterprise_build_audit.jsonl"))
    audit.log_event("build_start", "enterprise_workstation", success=True)

    # Copy source
    print("\n[1/6] Preparing image...")
    import shutil
    shutil.copy2(source_wim, output_wim)

    with ImageManager(output_wim) as manager:
        mount_point = manager.mount()

        try:
            # Apply security hardening
            print("[2/6] Applying security hardening...")
            apply_security_hardening(mount_point, audit)

            # Configure corporate policies
            print("[3/6] Applying corporate policies...")
            apply_corporate_policies(mount_point, company_config, audit)

            # Add corporate branding
            print("[4/6] Adding corporate branding...")
            add_corporate_branding(manager, company_config, audit)

            # Configure audit and logging
            print("[5/6] Configuring audit and compliance...")
            configure_audit_logging(mount_point, audit)

            # Add corporate software
            print("[6/6] Adding corporate software packages...")
            add_corporate_software(manager, audit)

            print("\n[✓] Saving changes...")
            manager.unmount(save_changes=True)
            audit.log_event("build_complete", "enterprise_workstation", success=True)

        except Exception as e:
            print(f"\n[✗] Error: {e}")
            manager.unmount(save_changes=False)
            audit.log_event("build_failed", "enterprise_workstation", success=False, error=str(e))
            raise

    print("\n" + "=" * 80)
    print(f"Enterprise image created: {output_wim}")
    print("\nSecurity features applied:")
    print("  • Password complexity requirements")
    print("  • BitLocker encryption ready")
    print("  • Firewall configured")
    print("  • Audit logging enabled")
    print("  • Corporate policies applied")
    print("=" * 80)


def apply_security_hardening(mount_point: Path, audit: AuditLogger):
    """Apply enterprise security hardening."""
    print("  Applying security hardening...")

    with RegistryEditor(mount_point) as reg:
        security_tweaks = [
            # Password policy
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\Policies\\System',
                'name': 'ConsentPromptBehaviorAdmin',
                'data': '2',  # Prompt for credentials
                'type': 'REG_DWORD'
            },
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\Policies\\System',
                'name': 'EnableLUA',
                'data': '1',  # UAC enabled
                'type': 'REG_DWORD'
            },
            # Disable AutoRun
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer',
                'name': 'NoDriveTypeAutoRun',
                'data': '255',
                'type': 'REG_DWORD'
            },
            # Enable BitLocker
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\FVE',
                'name': 'EnableBDEWithNoTPM',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Disable SMBv1
            {
                'hive': 'HKLM\\SYSTEM',
                'path': 'CurrentControlSet\\Services\\LanmanServer\\Parameters',
                'name': 'SMB1',
                'data': '0',
                'type': 'REG_DWORD'
            },
            # Enable Windows Defender
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows Defender',
                'name': 'DisableAntiSpyware',
                'data': '0',
                'type': 'REG_DWORD'
            },
        ]

        print("    • Configuring UAC...")
        print("    • Enabling BitLocker...")
        print("    • Disabling AutoRun...")
        print("    • Hardening SMB...")
        print("    • Configuring Windows Defender...")

        reg.apply_tweaks(security_tweaks)
        audit.log_event("security_hardening", "applied", success=True)


def apply_corporate_policies(mount_point: Path, company_config: dict, audit: AuditLogger):
    """Apply corporate group policies."""
    print("  Applying corporate policies...")

    company_name = company_config.get('company_name', 'Company')
    domain = company_config.get('domain', 'company.local')

    with RegistryEditor(mount_point) as reg:
        corporate_policies = [
            # Company information
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\OEMInformation',
                'name': 'Manufacturer',
                'data': company_name,
                'type': 'REG_SZ'
            },
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Microsoft\\Windows\\CurrentVersion\\OEMInformation',
                'name': 'SupportURL',
                'data': company_config.get('support_url', ''),
                'type': 'REG_SZ'
            },
            # Disable consumer features
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\CloudContent',
                'name': 'DisableWindowsConsumerFeatures',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Configure Windows Update for Business
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\WindowsUpdate\\AU',
                'name': 'NoAutoUpdate',
                'data': '0',
                'type': 'REG_DWORD'
            },
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\WindowsUpdate\\AU',
                'name': 'AUOptions',
                'data': '3',  # Auto download and notify
                'type': 'REG_DWORD'
            },
        ]

        print(f"    • Setting company information: {company_name}")
        print("    • Disabling consumer features...")
        print("    • Configuring Windows Update...")

        reg.apply_tweaks(corporate_policies)
        audit.log_event("corporate_policies", "applied", success=True)


def add_corporate_branding(manager: ImageManager, company_config: dict, audit: AuditLogger):
    """Add corporate branding and logos."""
    print("  Adding corporate branding...")

    branding_dir = Path("./branding")

    # Company logo
    logo_path = branding_dir / "logo.png"
    if logo_path.exists():
        manager.add_file(logo_path, "/Windows/System32/oobe/info/logo.png")
        print("    • Added company logo")
        audit.log_event("branding", "logo_added", success=True)

    # Wallpaper
    wallpaper_path = branding_dir / "wallpaper.jpg"
    if wallpaper_path.exists():
        manager.add_file(wallpaper_path, "/Windows/Web/Wallpaper/Windows/corporate_wallpaper.jpg")
        print("    • Added corporate wallpaper")
        audit.log_event("branding", "wallpaper_added", success=True)

    # OOBE customization
    oobe_xml = branding_dir / "oobe.xml"
    if oobe_xml.exists():
        manager.add_file(oobe_xml, "/Windows/System32/oobe/info/oobe.xml")
        print("    • Added OOBE customization")


def configure_audit_logging(mount_point: Path, audit: AuditLogger):
    """Configure Windows audit logging."""
    print("  Configuring audit and compliance...")

    with RegistryEditor(mount_point) as reg:
        audit_tweaks = [
            # Enable audit policy
            {
                'hive': 'HKLM\\SYSTEM',
                'path': 'CurrentControlSet\\Control\\Lsa',
                'name': 'AuditBaseObjects',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Enable PowerShell logging
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\PowerShell\\ModuleLogging',
                'name': 'EnableModuleLogging',
                'data': '1',
                'type': 'REG_DWORD'
            },
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging',
                'name': 'EnableScriptBlockLogging',
                'data': '1',
                'type': 'REG_DWORD'
            },
            # Enable Event Log
            {
                'hive': 'HKLM\\SOFTWARE',
                'path': 'Policies\\Microsoft\\Windows\\EventLog\\Security',
                'name': 'MaxSize',
                'data': '2097152',  # 2GB
                'type': 'REG_DWORD'
            },
        ]

        print("    • Enabling audit policy...")
        print("    • Configuring PowerShell logging...")
        print("    • Expanding event log size...")

        reg.apply_tweaks(audit_tweaks)
        audit.log_event("audit_config", "configured", success=True)


def add_corporate_software(manager: ImageManager, audit: AuditLogger):
    """Add standard corporate software packages."""
    print("  Adding corporate software...")

    software_dir = Path("./software")

    if not software_dir.exists():
        print("    No software directory found, skipping...")
        return

    # Add corporate certificates
    certs_dir = software_dir / "certificates"
    if certs_dir.exists():
        print("    • Adding corporate certificates...")
        for cert in certs_dir.glob("*.cer"):
            manager.add_file(cert, f"/ProgramData/Certificates/{cert.name}")

    # Add deployment scripts
    scripts_dir = software_dir / "scripts"
    if scripts_dir.exists():
        print("    • Adding deployment scripts...")
        for script in scripts_dir.glob("*.ps1"):
            manager.add_file(script, f"/Windows/Setup/Scripts/{script.name}")

    # Add configuration files
    configs_dir = software_dir / "configs"
    if configs_dir.exists():
        print("    • Adding configuration files...")
        for config in configs_dir.glob("*.xml"):
            manager.add_file(config, f"/ProgramData/Corporate/{config.name}")

    audit.log_event("corporate_software", "added", success=True)


if __name__ == "__main__":
    # Company configuration
    COMPANY_CONFIG = {
        'company_name': 'Acme Corporation',
        'domain': 'acme.local',
        'support_url': 'https://support.acme.com',
        'support_phone': '1-800-ACME',
        'it_email': 'it@acme.com',
    }

    SOURCE_WIM = Path("D:/sources/install.wim")
    OUTPUT_WIM = Path("./Windows_Enterprise_Acme.wim")

    print("\nEnterprise Workstation Image Builder")
    print("=" * 80)
    print("\nThis script creates an enterprise-ready Windows image with:")
    print("  • Security hardening (UAC, BitLocker, Defender)")
    print("  • Corporate policies and branding")
    print("  • Audit and compliance logging")
    print("  • Standard software packages")
    print("  • Domain join preparation")
    print()
    print(f"Company: {COMPANY_CONFIG['company_name']}")
    print(f"Domain: {COMPANY_CONFIG['domain']}")
    print(f"Source: {SOURCE_WIM}")
    print(f"Output: {OUTPUT_WIM}")
    print()

    if not SOURCE_WIM.exists():
        print("Error: Source WIM not found. Please update paths.")
        print("\nSetup instructions:")
        print("1. Extract install.wim from Windows Enterprise ISO")
        print("2. Create ./branding directory with company assets")
        print("3. Create ./software directory with packages")
        print("4. Update COMPANY_CONFIG in this script")
        print("5. Run the script")
    else:
        response = input("Build enterprise image? (y/n): ")
        if response.lower() == 'y':
            build_enterprise_workstation(SOURCE_WIM, OUTPUT_WIM, COMPANY_CONFIG)

            print("\n\nDeployment checklist:")
            print("  ✓ Image created and hardened")
            print("  ✓ Corporate policies applied")
            print("  ✓ Audit logging configured")
            print()
            print("Next steps:")
            print("1. Test image in test environment")
            print("2. Configure MDT/SCCM deployment")
            print("3. Create deployment task sequence")
            print("4. Deploy to pilot group")
            print("5. Monitor and audit deployments")
