# DeployForge Enterprise Guide

**Version**: 1.7.0
**Last Updated**: 2025-11-17
**Audience**: Enterprise IT Administrators, DevOps Engineers, System Integrators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Enterprise Architecture Overview](#enterprise-architecture-overview)
3. [Infrastructure as Code (IaC)](#infrastructure-as-code-iac)
4. [MDT/SCCM Integration](#mdtsccm-integration)
5. [Automated Testing & Validation](#automated-testing--validation)
6. [Job Scheduling & Automation](#job-scheduling--automation)
7. [Version Control for Images](#version-control-for-images)
8. [Certificate Management](#certificate-management)
9. [Group Policy Deployment](#group-policy-deployment)
10. [Security & Compliance](#security--compliance)
11. [Batch Operations at Scale](#batch-operations-at-scale)
12. [Enterprise Workflows](#enterprise-workflows)
13. [Monitoring & Audit Logging](#monitoring--audit-logging)
14. [Cloud Integration](#cloud-integration)
15. [Best Practices](#best-practices)
16. [Troubleshooting](#troubleshooting)

---

## Introduction

DeployForge Enterprise Edition provides comprehensive automation capabilities for large-scale Windows deployment operations. This guide covers advanced enterprise features including MDT/SCCM integration, Infrastructure as Code, automated testing, job scheduling, and compliance management.

### Target Audience

- **Enterprise IT Administrators** managing 100+ endpoints
- **DevOps Engineers** implementing CI/CD for Windows images
- **System Integrators** deploying standardized images across organizations
- **Compliance Officers** ensuring security baseline adherence

### Prerequisites

- DeployForge installed with enterprise dependencies
- Windows Server environment (recommended for MDT/SCCM)
- Administrative privileges for deployment operations
- Basic understanding of Windows deployment technologies

### Key Enterprise Features

| Feature | Module | Purpose |
|---------|--------|---------|
| Infrastructure as Code | `iac.py` | YAML/JSON deployment definitions |
| MDT/SCCM Integration | `integration.py` | Enterprise deployment tooling |
| Automated Testing | `testing.py` | VM-based validation |
| Job Scheduling | `scheduler.py` | Cron-based automation |
| Version Control | `versioning.py` | Git-like image versioning |
| Certificate Management | `certificates.py` | PKI integration |
| Group Policy | `gpo.py` | GPO deployment |
| Batch Operations | `batch.py` | Parallel processing |

---

## Enterprise Architecture Overview

### Deployment Models

#### 1. Centralized Model

```
┌─────────────────────────────────────┐
│     DeployForge Central Server      │
│  - Master image repository          │
│  - Job scheduler                    │
│  - Version control                  │
│  - Audit logging                    │
└──────────────┬──────────────────────┘
               │
       ┌───────┼───────┐
       ▼       ▼       ▼
    ┌────┐  ┌────┐  ┌────┐
    │MDT │  │SCCM│  │WDS │
    └────┘  └────┘  └────┘
       │       │       │
       └───────┼───────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   Endpoints    Distribution Points
```

**Use Case**: Large enterprises with centralized IT management

#### 2. Distributed Model

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Region A    │  │  Region B    │  │  Region C    │
│  DeployForge │  │  DeployForge │  │  DeployForge │
│  + MDT       │  │  + SCCM      │  │  + WDS       │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                  ┌───────┴────────┐
                  │  Central Sync  │
                  │  (Git/S3/Azure)│
                  └────────────────┘
```

**Use Case**: Global organizations with regional autonomy

#### 3. Hybrid Cloud Model

```
┌─────────────────────────────────────┐
│        On-Premises                   │
│  DeployForge + MDT/SCCM             │
└──────────────┬──────────────────────┘
               │
               │ Sync
               ▼
┌─────────────────────────────────────┐
│         Cloud (AWS/Azure)            │
│  - S3/Blob storage                  │
│  - Lambda/Functions (automation)    │
│  - EC2/VM instances (testing)       │
└─────────────────────────────────────┘
```

**Use Case**: Hybrid environments with cloud backup/DR

---

## Infrastructure as Code (IaC)

### Overview

DeployForge's IaC module (`iac.py`, 770 lines) enables declarative Windows image builds using YAML or JSON configurations. This provides version-controlled, repeatable, and auditable deployments.

### Build Stages

DeployForge supports 12 predefined build stages:

1. **init** - Initialize build environment
2. **partitions** - Create UEFI/GPT partitions
3. **base** - Apply base configuration and debloat
4. **drivers** - Inject hardware drivers
5. **updates** - Apply Windows updates
6. **applications** - Install applications
7. **security** - Security hardening
8. **certificates** - Certificate injection
9. **gpo** - Group Policy configuration
10. **languages** - Language pack installation
11. **customization** - Final tweaks and customization
12. **finalize** - Cleanup and validation

### Configuration Syntax

#### Basic Example

```yaml
# enterprise_build.yaml
version: "1.0"
name: "Windows 11 Enterprise - Standard Build"
image: "sources/install.wim"
index: 1
output: "Win11_Enterprise_v1.0.wim"

variables:
  company: "Acme Corporation"
  domain: "acme.local"
  timezone: "Eastern Standard Time"
  version: "1.0.0"

stages:
  - name: base
    profile: enterprise
    debloat:
      - Xbox
      - Teams
      - OneDrive
      - Cortana
    privacy: enhanced

  - name: applications
    install:
      - name: "Microsoft Office 365"
        source: "apps/Office365_Enterprise.exe"
        args: "/configure config.xml"
      - name: "7-Zip"
        source: "apps/7z-installer.msi"
        args: "/quiet"

  - name: finalize
    validate: true
    optimize: true
    cleanup_temp: true
```

#### Advanced Example with All Stages

```yaml
# enterprise_complete.yaml
version: "1.0"
name: "Windows 11 Enterprise - Complete Build"
image: "sources/install.wim"
index: 1
output: "Win11_Enterprise_Complete_v${version}.wim"

variables:
  company: "Acme Corporation"
  domain: "acme.local"
  timezone: "Eastern Standard Time"
  version: "2.0.0"
  admin_user: "LocalAdmin"
  support_url: "https://support.acme.local"

# Stage 1: Initialize
stages:
  - name: init
    create_dirs:
      - "C:\\Temp\\Deploy"
      - "C:\\Logs"
    set_environment:
      COMPANY: "${company}"
      DEPLOY_VERSION: "${version}"

  # Stage 2: Partitioning
  - name: partitions
    action: create
    type: uefi_gpt
    layout:
      - name: "EFI System"
        size: 260MB
        type: efi
      - name: "Windows"
        size: 100GB
        type: primary
      - name: "Recovery"
        size: 1GB
        type: recovery
    recovery: true

  # Stage 3: Base Configuration
  - name: base
    profile: enterprise
    debloat:
      # Consumer Apps
      - Xbox
      - XboxGameOverlay
      - XboxGamingOverlay
      - XboxIdentityProvider
      - XboxSpeechToTextOverlay
      - Microsoft.Teams
      - OneDrive
      - Cortana
      - Microsoft.BingWeather
      - Microsoft.GetHelp
      - Microsoft.Getstarted
      - Microsoft.MicrosoftSolitaireCollection
      - Microsoft.People
      - Microsoft.WindowsFeedbackHub
      - Microsoft.YourPhone
      - Microsoft.ZuneMusic
      - Microsoft.ZuneVideo

    privacy: maximum
    telemetry: disabled
    windows_update: managed
    defender: enabled

  # Stage 4: Drivers
  - name: drivers
    packages:
      - "drivers/dell/latitude_7000/*.inf"
      - "drivers/dell/precision_workstation/*.inf"
      - "drivers/intel/chipset/*.inf"
      - "drivers/intel/me/*.inf"
      - "drivers/nvidia/quadro/*.inf"
    force_unsigned: false
    remove_duplicates: true

  # Stage 5: Windows Updates
  - name: updates
    source: "updates/"
    types:
      - cumulative
      - security
      - servicing_stack
      - dotnet
    latest_only: true
    cleanup_superseded: true

  # Stage 6: Applications
  - name: applications
    install:
      # Productivity
      - name: "Microsoft Office 365 ProPlus"
        source: "apps/Office365/setup.exe"
        args: "/configure apps/Office365/enterprise_config.xml"
        reboot: false

      # Security
      - name: "CrowdStrike Falcon"
        source: "apps/security/falcon_sensor.exe"
        args: "/install /quiet CID=${crowdstrike_cid}"
        reboot: false

      # Remote Management
      - name: "Bomgar Jump Client"
        source: "apps/remote/bomgar_client.msi"
        args: "/quiet SITE_KEY=${bomgar_key}"

      # Development Tools (optional)
      - name: "Git for Windows"
        source: "apps/dev/git-installer.exe"
        args: "/VERYSILENT /NORESTART"
        condition: "${profile} == 'developer'"

  # Stage 7: Security Hardening
  - name: security
    level: high

    firewall:
      enabled: true
      default_inbound: block
      default_outbound: allow
      rules:
        - name: "Allow RDP"
          port: 3389
          protocol: tcp
          action: allow
        - name: "Allow WinRM"
          port: 5985
          protocol: tcp
          action: allow

    defender:
      realtime_protection: true
      cloud_protection: true
      sample_submission: true
      pua_protection: true
      exploit_guard: true

    bitlocker:
      prepare: true
      algorithm: aes256
      recovery_key: ad_backup

    policies:
      - disable_guest_account: true
      - require_ctrl_alt_del: true
      - password_complexity: true
      - account_lockout_threshold: 5
      - audit_policy_change: true

  # Stage 8: Certificates
  - name: certificates
    import:
      # Root CA
      - path: "certs/${company}_root_ca.cer"
        store: Root

      # Intermediate CAs
      - path: "certs/${company}_intermediate_ca.cer"
        store: CA

      # Code Signing
      - path: "certs/${company}_codesign.cer"
        store: TrustedPublisher

    crl_distribution:
      - "http://pki.${domain}/crl/root.crl"
      - "http://pki.${domain}/crl/intermediate.crl"

    ocsp_responder: "http://ocsp.${domain}"

  # Stage 9: Group Policy
  - name: gpo
    import:
      - source: "policies/baseline_security.xml"
        name: "Enterprise Security Baseline"

      - source: "policies/corporate_settings.xml"
        name: "Corporate Standards"

      - source: "policies/windows11_hardening.xml"
        name: "Windows 11 Security Hardening"

    apply:
      - "Enterprise Security Baseline"
      - "Corporate Standards"
      - "Windows 11 Security Hardening"

    administrative_templates:
      - source: "admx/Office365.admx"
      - source: "admx/Edge.admx"
      - source: "admx/Defender.admx"

  # Stage 10: Languages
  - name: languages
    base_language: "en-US"
    additional:
      - "es-ES"
      - "fr-FR"
      - "de-DE"
    features:
      - "Basic"
      - "Fonts"
      - "OCR"
      - "Speech"
    fallback: "en-US"

  # Stage 11: Customization
  - name: customization

    registry:
      # Company Branding
      - key: "HKLM\\SOFTWARE\\${company}"
        value: "DeployedBy"
        data: "DeployForge ${version}"
        type: REG_SZ

      - key: "HKLM\\SOFTWARE\\${company}"
        value: "DeploymentDate"
        data: "${timestamp}"
        type: REG_SZ

      # Disable Consumer Features
      - key: "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent"
        value: "DisableWindowsConsumerFeatures"
        data: 1
        type: REG_DWORD

      # Set Time Zone
      - key: "HKLM\\SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation"
        value: "TimeZoneKeyName"
        data: "${timezone}"
        type: REG_SZ

    wallpaper:
      source: "branding/corporate_wallpaper.jpg"
      style: fill

    lockscreen:
      source: "branding/lockscreen.jpg"

    oem_info:
      manufacturer: "${company}"
      model: "Standard Build v${version}"
      support_hours: "24/7"
      support_phone: "1-800-ACME-HELP"
      support_url: "${support_url}"
      logo: "branding/logo.bmp"

    start_menu:
      layout: "configs/start_layout.xml"
      remove_default_apps: true

    taskbar:
      layout: "configs/taskbar_layout.xml"
      hide_search: false
      hide_task_view: true
      hide_people: true

  # Stage 12: Finalize
  - name: finalize

    cleanup:
      - temp_files: true
      - winsxs: true
      - update_cache: true
      - recycle_bin: true
      - thumbnail_cache: true

    optimize:
      - defragment: true
      - sfc_scan: false
      - dism_cleanup: true
      - compact_os: false

    validate:
      - file_integrity: true
      - registry_health: true
      - driver_signatures: true
      - certificate_validity: true

    metadata:
      version: "${version}"
      build_date: "${timestamp}"
      deployed_by: "DeployForge Enterprise"
      description: "Windows 11 Enterprise - Complete Build"
```

### Running IaC Builds

#### Python API

```python
from deployforge.iac import IaCRunner
from pathlib import Path

# Load configuration
runner = IaCRunner(Path('enterprise_build.yaml'))

# Validate configuration
if not runner.validate():
    print("Configuration validation failed")
    for error in runner.validation_errors:
        print(f"  - {error}")
    exit(1)

# Execute all stages
print("Starting build...")
result = runner.execute_all_stages(
    progress_callback=lambda stage, percent: print(f"{stage}: {percent}%")
)

# Check results
print(f"\nBuild completed:")
print(f"  Successful stages: {result.successful_stages}/{result.total_stages}")
print(f"  Duration: {result.duration}s")

if result.failed_stages:
    print(f"  Failed stages: {', '.join(result.failed_stages)}")

# Generate report
runner.generate_report(Path('build_report.txt'))
runner.generate_html_report(Path('build_report.html'))
```

#### CLI

```bash
# Validate configuration
deployforge iac validate enterprise_build.yaml

# Execute build
deployforge iac build enterprise_build.yaml --output Win11_Enterprise.wim

# Execute specific stages only
deployforge iac build enterprise_build.yaml --stages base,applications,security

# Dry run (validation only)
deployforge iac build enterprise_build.yaml --dry-run

# Generate report
deployforge iac report enterprise_build.yaml --output report.html
```

### Variable Substitution

IaC configurations support variable substitution:

```yaml
variables:
  company: "Acme Corporation"
  domain: "acme.local"
  version: "1.0.0"
  environment: "production"

stages:
  - name: customization
    registry:
      - key: "HKLM\\SOFTWARE\\${company}"
        value: "Environment"
        data: "${environment}"
        type: REG_SZ

      - key: "HKLM\\SOFTWARE\\${company}\\Support"
        value: "URL"
        data: "https://support.${domain}"
        type: REG_SZ
```

**Built-in Variables:**
- `${timestamp}` - Current timestamp (ISO 8601)
- `${date}` - Current date (YYYY-MM-DD)
- `${time}` - Current time (HH:MM:SS)
- `${user}` - Current user executing build
- `${hostname}` - Hostname of build server

### Conditional Logic

```yaml
stages:
  - name: applications
    install:
      - name: "Visual Studio 2022"
        source: "apps/vs2022_enterprise.exe"
        condition: "${profile} == 'developer'"

      - name: "Adobe Creative Cloud"
        source: "apps/adobe_cc.exe"
        condition: "${profile} == 'creative'"

      - name: "CAD Software"
        source: "apps/autocad.exe"
        condition: "${department} == 'engineering'"
```

### Schema Validation

IaC configurations are validated against a JSON schema:

```bash
# Validate before execution
deployforge iac validate config.yaml

# Validation checks:
# - Required fields present
# - Valid stage names
# - Correct data types
# - File paths exist
# - Variable references valid
```

---

## MDT/SCCM Integration

### Overview

DeployForge's integration module (`integration.py`, 786 lines) provides seamless integration with Microsoft Deployment Toolkit (MDT) and System Center Configuration Manager (SCCM).

### MDT Integration

#### Creating a Deployment Share

```python
from deployforge.integration import MDTManager
from pathlib import Path

# Initialize MDT manager
mdt = MDTManager()

# Create deployment share
mdt.create_share(
    path=Path('D:\\DeploymentShare'),
    name='Production',
    description='Production deployment share for Windows 11'
)

# Configure share settings
mdt.configure_share(
    share_name='Production',
    settings={
        'boot_image_x64': True,
        'boot_image_x86': False,
        'monitoring': True,
        'event_logging': True,
        'debug_logging': False
    }
)
```

#### Importing OS Images

```python
# Import Windows image
os_id = mdt.import_os_image(
    wim_path=Path('Win11_Enterprise_Custom.wim'),
    name='Windows 11 Enterprise (Custom)',
    version='22H2',
    architecture='x64'
)

print(f"OS imported with ID: {os_id}")
```

#### Creating Task Sequences

```python
from deployforge.integration import TaskSequenceBuilder, TaskSequenceType

# Initialize builder
builder = TaskSequenceBuilder(mdt)

# Create standard client task sequence
ts_id = builder.create_standard_client(
    name='Windows 11 Enterprise Deployment',
    os_id=os_id,
    admin_password='P@ssw0rd',  # Will be encrypted
    org_name='Acme Corporation',
    home_page='https://www.acme.local'
)

# Add custom steps
builder.add_step(
    sequence_id=ts_id,
    step_type='InstallApplication',
    config={
        'application_name': 'Microsoft Office 365',
        'condition': None
    }
)

builder.add_step(
    sequence_id=ts_id,
    step_type='RunCommandLine',
    config={
        'command': 'powershell.exe -ExecutionPolicy Bypass -File Configure-Security.ps1',
        'working_directory': r'%SCRIPTROOT%\Scripts',
        'condition': None
    }
)

builder.add_step(
    sequence_id=ts_id,
    step_type='InstallUpdates',
    config={
        'update_source': 'WSUS',
        'reboot_if_required': True
    }
)
```

#### Managing Applications

```python
from deployforge.integration import MDTApplication

# Define application
app = MDTApplication(
    name='7-Zip 23.01',
    publisher='Igor Pavlov',
    version='23.01',
    source_path=Path('apps/7zip'),
    command_line='7z-installer.msi /quiet',
    working_directory='.',
    platform='x64',
    reboot_required=False
)

# Import to MDT
app_id = mdt.import_application(app)

# Create application bundle
bundle_id = mdt.create_application_bundle(
    name='Standard Software Package',
    applications=[
        '7-Zip 23.01',
        'Microsoft Office 365',
        'Adobe Acrobat Reader',
        'Google Chrome'
    ]
)
```

#### Driver Management

```python
# Import driver package
driver_id = mdt.import_drivers(
    source_path=Path('drivers/dell/latitude_7000'),
    name='Dell Latitude 7000 Series',
    make='Dell',
    model='Latitude 7490',
    os_version='Windows 11',
    architecture='x64'
)

# Create selection profile for drivers
profile_id = mdt.create_selection_profile(
    name='Dell Latitude Drivers',
    driver_groups=['Dell/Latitude 7000']
)

# Associate with task sequence
builder.set_driver_selection_profile(
    sequence_id=ts_id,
    profile_id=profile_id
)
```

#### Boot Image Generation

```python
# Generate custom WinPE boot image
boot_image_path = mdt.generate_boot_image(
    architecture='x64',
    include_drivers=[
        Path('drivers/network/intel_i219.inf'),
        Path('drivers/storage/nvme.inf')
    ],
    include_applications=[
        'DaRT 10'  # Microsoft Diagnostics and Recovery Toolset
    ],
    background_image=Path('branding/winpe_background.jpg'),
    scratch_space='512'  # MB
)

print(f"Boot image created: {boot_image_path}")
```

#### Updating Deployment Share

```python
# Update deployment share (regenerate boot images)
mdt.update_share(
    share_name='Production',
    optimize=True,  # Optimize boot images
    compress=True   # Compress boot images
)
```

### SCCM Integration

#### Package Creation

```python
from deployforge.integration import SCCMManager, SCCMPackage

# Initialize SCCM manager
sccm = SCCMManager(
    server='sccm01.acme.local',
    site_code='ACM'
)

# Create OS image package
os_package_id = sccm.create_os_package(
    name='Windows 11 Enterprise (Custom)',
    version='22H2',
    source_path=Path('\\\\fileserver\\sources\\Win11_Enterprise.wim'),
    description='Customized Windows 11 Enterprise with company applications'
)

# Create application package
app_package_id = sccm.create_application_package(
    name='Microsoft Office 365 ProPlus',
    version='2023',
    source_path=Path('\\\\fileserver\\apps\\Office365'),
    command_line='setup.exe /configure config.xml',
    detection_method='file',
    detection_path=r'C:\Program Files\Microsoft Office\root\Office16',
    detection_file='WINWORD.EXE'
)
```

#### Distribution

```python
# Distribute to distribution points
sccm.distribute_content(
    package_id=os_package_id,
    distribution_points=[
        'DP01.acme.local',
        'DP02.acme.local',
        'DP03.acme.local'
    ],
    priority='high'
)

# Monitor distribution status
status = sccm.get_distribution_status(os_package_id)
for dp in status:
    print(f"{dp['name']}: {dp['status']} ({dp['percent']}%)")
```

#### Task Sequence Deployment

```python
# Create SCCM task sequence
ts_id = sccm.create_task_sequence(
    name='Windows 11 Enterprise Deployment',
    type=TaskSequenceType.BARE_METAL,
    os_package_id=os_package_id,
    boot_image_id='ACM00001'
)

# Deploy task sequence to collection
deployment_id = sccm.deploy_task_sequence(
    task_sequence_id=ts_id,
    collection_id='SMS00001',  # All Systems
    deployment_type='required',
    make_available_to_pxe=True,
    make_available_to_media=True,
    schedule='2025-12-01T02:00:00'
)
```

### Hybrid MDT + SCCM Workflow

```python
# 1. Create custom image with DeployForge
from deployforge import ImageManager

with ImageManager(Path('install.wim')) as img:
    img.mount()
    # ... customizations ...
    img.unmount(save_changes=True)

# 2. Import to MDT
os_id = mdt.import_os_image(
    wim_path=Path('Win11_Custom.wim'),
    name='Windows 11 Enterprise (Custom)'
)

# 3. Create MDT task sequence
ts_id = builder.create_standard_client(
    name='Win11 Deployment',
    os_id=os_id
)

# 4. Export MDT task sequence
mdt.export_task_sequence(
    sequence_id=ts_id,
    output_path=Path('tasksequence_export.xml')
)

# 5. Import to SCCM
sccm_ts_id = sccm.import_task_sequence(
    xml_path=Path('tasksequence_export.xml'),
    os_package_id=os_package_id
)

# 6. Deploy via SCCM
deployment_id = sccm.deploy_task_sequence(
    task_sequence_id=sccm_ts_id,
    collection_id='SMS00010'  # Pilot group
)
```

---

## Automated Testing & Validation

### Overview

The testing module (`testing.py`, 823 lines) provides comprehensive automated testing capabilities including integrity validation, VM-based bootability testing, driver verification, and compliance checking.

### Image Integrity Validation

```python
from deployforge.testing import ImageValidator, TestStatus
from pathlib import Path

validator = ImageValidator()

# Validate file integrity
integrity_result = validator.validate_integrity(
    image_path=Path('Win11_Enterprise.wim')
)

if integrity_result.status == TestStatus.PASSED:
    print(f"Integrity check passed: {integrity_result.message}")
    print(f"SHA256: {integrity_result.details['sha256']}")
else:
    print(f"Integrity check failed: {integrity_result.message}")

# Validate WIM structure
structure_result = validator.validate_structure(
    image_path=Path('Win11_Enterprise.wim')
)

print(f"Image contains {structure_result.details['index_count']} indexes")
print(f"Compression: {structure_result.details['compression']}")
```

### VM-Based Bootability Testing

#### Supported Hypervisors

- **Hyper-V** (Windows Server/Windows 10/11 Pro)
- **VirtualBox** (Cross-platform)
- **VMware** Workstation/Player
- **QEMU/KVM** (Linux)

#### Basic Boot Test

```python
from deployforge.testing import VMTester, Hypervisor

# Create VM tester
tester = VMTester(
    image_path=Path('Win11_Enterprise.wim'),
    hypervisor=Hypervisor.HYPER_V
)

# Configure VM specs
tester.configure(
    memory_mb=4096,
    cpu_cores=2,
    disk_size_gb=60,
    network='NAT',
    secure_boot=True,
    tpm=True
)

# Create temporary VM
vm_id = tester.create_vm()
print(f"Created test VM: {vm_id}")

# Test boot (timeout 300 seconds)
boot_result = tester.test_boot(timeout=300)

if boot_result.status == TestStatus.PASSED:
    print(f"Boot test passed in {boot_result.duration}s")
    print(f"OOBE reached: {boot_result.details['oobe_reached']}")
    print(f"Boot time: {boot_result.details['boot_time']}s")
else:
    print(f"Boot test failed: {boot_result.message}")
    print(f"Error code: {boot_result.details.get('error_code')}")

# Cleanup
tester.cleanup_vm()
```

#### Advanced Testing with Screenshots

```python
# Configure screenshot capture
tester.configure(
    memory_mb=4096,
    cpu_cores=2,
    disk_size_gb=60,
    capture_screenshots=True,
    screenshot_interval=30  # seconds
)

# Test with extended validation
boot_result = tester.test_boot(
    timeout=600,
    wait_for_oobe=True,
    capture_logs=True
)

# Save screenshots
if boot_result.details.get('screenshots'):
    for idx, screenshot in enumerate(boot_result.details['screenshots']):
        screenshot_path = Path(f'test_screenshots/boot_{idx}.png')
        screenshot_path.write_bytes(screenshot)

# Save logs
if boot_result.details.get('logs'):
    Path('test_logs/boot_log.txt').write_text(boot_result.details['logs'])
```

### Driver Validation

```python
from deployforge.testing import DriverValidator

driver_validator = DriverValidator()

# Validate driver signatures
driver_result = driver_validator.validate_driver_signatures(
    image_path=Path('Win11_Enterprise.wim'),
    strict_mode=True  # Fail on any unsigned drivers
)

if driver_result.status == TestStatus.WARNING:
    print("Warning: Some drivers are not signed")
    for driver in driver_result.details['unsigned_drivers']:
        print(f"  - {driver['name']}: {driver['path']}")

# Validate driver compatibility
compat_result = driver_validator.validate_compatibility(
    image_path=Path('Win11_Enterprise.wim'),
    target_version='10.0.22000'  # Windows 11 22H2
)
```

### Compliance Verification

```python
from deployforge.testing import ComplianceValidator

compliance = ComplianceValidator()

# Check security baseline
baseline_result = compliance.check_security_baseline(
    image_path=Path('Win11_Enterprise.wim'),
    baseline='CIS_Windows_11_v1.0.0'
)

print(f"Compliance: {baseline_result.details['compliance_percentage']}%")
print(f"Passed: {baseline_result.details['passed_checks']}")
print(f"Failed: {baseline_result.details['failed_checks']}")

# Failed checks details
for check in baseline_result.details['failures']:
    print(f"\nCheck: {check['id']} - {check['name']}")
    print(f"  Status: {check['status']}")
    print(f"  Recommendation: {check['recommendation']}")

# Check update compliance
update_result = compliance.check_update_compliance(
    image_path=Path('Win11_Enterprise.wim'),
    required_updates=[
        'KB5031354',  # Latest cumulative update
        'KB5031445'   # Latest .NET update
    ]
)
```

### Performance Benchmarking

```python
from deployforge.testing import PerformanceTester

perf_tester = PerformanceTester(
    image_path=Path('Win11_Enterprise.wim'),
    hypervisor=Hypervisor.VIRTUALBOX
)

# Run performance tests
perf_results = perf_tester.run_benchmarks(
    tests=[
        'boot_time',
        'application_launch',
        'file_operations',
        'memory_usage'
    ],
    iterations=3  # Average of 3 runs
)

print(f"Average boot time: {perf_results['boot_time']['average']}s")
print(f"Memory usage (idle): {perf_results['memory_usage']['idle_mb']}MB")
print(f"Memory usage (active): {perf_results['memory_usage']['active_mb']}MB")
```

### Test Runner - Full Suite

```python
from deployforge.testing import TestRunner, TestSuite

# Create test suite
suite = TestSuite(
    name='Windows 11 Enterprise Validation',
    image_path=Path('Win11_Enterprise.wim')
)

# Add tests
suite.add_test('integrity', validator.validate_integrity)
suite.add_test('structure', validator.validate_structure)
suite.add_test('boot_hyperv', lambda: tester.test_boot(timeout=300))
suite.add_test('drivers', driver_validator.validate_driver_signatures)
suite.add_test('compliance', lambda: compliance.check_security_baseline(
    baseline='CIS_Windows_11_v1.0.0'
))

# Run test suite
runner = TestRunner()
results = runner.run_suite(suite)

# Generate reports
runner.generate_json_report(results, Path('test_report.json'))
runner.generate_html_report(results, Path('test_report.html'))
runner.generate_junit_report(results, Path('test_report.xml'))

# Summary
print(f"\nTest Summary:")
print(f"  Total: {results.total_tests}")
print(f"  Passed: {results.passed_tests}")
print(f"  Failed: {results.failed_tests}")
print(f"  Warnings: {results.warning_tests}")
print(f"  Duration: {results.total_duration}s")
```

### CI/CD Integration

```yaml
# .github/workflows/image-validation.yml
name: Image Validation

on:
  push:
    paths:
      - 'images/**/*.wim'

jobs:
  validate:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install DeployForge
        run: pip install deployforge

      - name: Run Validation Tests
        run: |
          python scripts/validate_image.py images/Win11_Enterprise.wim

      - name: Upload Test Reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

---

## Job Scheduling & Automation

### Overview

The scheduler module (`scheduler.py`, 716 lines) provides cron-based job scheduling and queue management for automated image builds.

### Job Priority Levels

```python
from deployforge.scheduler import JobPriority

# Available priorities:
JobPriority.LOW      # Background tasks
JobPriority.NORMAL   # Standard builds
JobPriority.HIGH     # Important updates
JobPriority.URGENT   # Critical patches
```

### Scheduling Jobs

#### One-Time Job

```python
from deployforge.scheduler import JobScheduler, JobPriority
from pathlib import Path

scheduler = JobScheduler()

# Schedule immediate job
job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={
        'profile': 'enterprise',
        'output': 'Win11_Enterprise_v1.0.wim'
    },
    priority=JobPriority.HIGH,
    retry_count=3,
    notify_email='admin@acme.local'
)

print(f"Job ID: {job.id}")
print(f"Status: {job.status}")
```

#### Recurring Job (Cron)

```python
# Schedule nightly build at 2 AM
nightly_job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={'profile': 'enterprise'},
    schedule='0 2 * * *',  # 2 AM daily
    priority=JobPriority.NORMAL,
    retry_count=3,
    notify_email='admin@acme.local',
    notify_webhook='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
)

# Schedule weekly full rebuild (Sunday 1 AM)
weekly_job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={
        'profile': 'enterprise',
        'full_rebuild': True,
        'run_tests': True
    },
    schedule='0 1 * * 0',  # 1 AM on Sundays
    priority=JobPriority.HIGH
)

# Schedule monthly update integration (1st of month, 3 AM)
monthly_job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={
        'update_only': True,
        'update_source': 'wsus.acme.local'
    },
    schedule='0 3 1 * *',  # 3 AM on 1st of month
    priority=JobPriority.URGENT
)
```

### Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, Sunday = 0)
│ │ │ │ │
* * * * *

Examples:
0 2 * * *        # Every day at 2 AM
0 0 * * 0        # Every Sunday at midnight
*/15 * * * *     # Every 15 minutes
0 9-17 * * 1-5   # Every hour from 9 AM to 5 PM, Monday-Friday
0 0 1,15 * *     # 1st and 15th of every month at midnight
```

### Job Management

```python
# List all jobs
all_jobs = scheduler.list_jobs()
for job in all_jobs:
    print(f"{job.id}: {job.name} - {job.status} (Next run: {job.next_run})")

# Get specific job status
job_status = scheduler.get_job_status(job.id)
print(f"Status: {job_status.status}")
print(f"Progress: {job_status.progress}%")
print(f"Started: {job_status.start_time}")
print(f"Duration: {job_status.duration}s")

# Cancel a job
scheduler.cancel_job(job.id)

# Pause/Resume job
scheduler.pause_job(job.id)
scheduler.resume_job(job.id)

# Delete job
scheduler.delete_job(job.id)
```

### Job Notifications

#### Email Notifications

```python
# Configure email settings
scheduler.configure_email(
    smtp_server='smtp.acme.local',
    smtp_port=587,
    username='deployforge@acme.local',
    password='password',
    use_tls=True,
    from_address='deployforge@acme.local'
)

# Schedule with email notification
job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={'profile': 'enterprise'},
    notify_email='admin@acme.local',
    notify_on=['success', 'failure', 'warning']
)
```

#### Webhook Notifications

```python
# Schedule with webhook (Slack, Teams, etc.)
job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={'profile': 'enterprise'},
    notify_webhook='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    webhook_format='slack'  # or 'teams', 'discord', 'generic'
)
```

### Queue Management

```python
# Get queue statistics
stats = scheduler.get_queue_stats()
print(f"Pending: {stats['pending']}")
print(f"Running: {stats['running']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")

# Set concurrent job limit
scheduler.set_max_concurrent_jobs(4)

# Clear completed jobs from queue
scheduler.clear_completed_jobs(older_than_days=7)
```

### Advanced Job Configuration

```python
from deployforge.scheduler import JobConfig

# Create detailed job configuration
config = JobConfig(
    image_path=Path('install.wim'),
    output_path=Path('Win11_Enterprise.wim'),
    profile='enterprise',

    # Build options
    build_options={
        'debloat': True,
        'privacy': 'enhanced',
        'updates': True,
        'drivers': ['network', 'storage']
    },

    # Testing options
    run_tests=True,
    test_options={
        'boot_test': True,
        'compliance_check': True,
        'performance_benchmark': False
    },

    # Retry configuration
    retry_count=3,
    retry_delay=300,  # seconds
    retry_on=['network_error', 'temporary_failure'],

    # Resource limits
    timeout=3600,  # seconds
    memory_limit_mb=8192,
    cpu_limit_percent=80,

    # Cleanup
    cleanup_on_success=True,
    cleanup_on_failure=False,
    keep_logs_days=30
)

# Schedule with config
job = scheduler.schedule_job(
    config=config,
    schedule='0 2 * * *',
    priority=JobPriority.HIGH
)
```

### Job Logging and History

```python
# Get job logs
logs = scheduler.get_job_logs(job.id)
for log_entry in logs:
    print(f"[{log_entry.timestamp}] {log_entry.level}: {log_entry.message}")

# Get job history
history = scheduler.get_job_history(
    job_id=job.id,
    limit=10
)
for execution in history:
    print(f"Run: {execution.timestamp}")
    print(f"  Status: {execution.status}")
    print(f"  Duration: {execution.duration}s")
    print(f"  Output: {execution.output_path}")

# Export job history to CSV
scheduler.export_history(
    output_path=Path('job_history.csv'),
    start_date='2025-01-01',
    end_date='2025-12-31'
)
```

---

## Version Control for Images

### Overview

The versioning module (`versioning.py`, 689 lines) provides Git-like version control for Windows images with commit history, branching, tagging, and diff capabilities.

### Repository Initialization

```python
from deployforge.versioning import ImageRepository
from pathlib import Path

# Initialize repository
repo = ImageRepository(Path('/images/repo'))
repo.init()

# Configure repository
repo.config(
    user_name='John Doe',
    user_email='john.doe@acme.local',
    compression='lzma',  # or 'gzip', 'none'
    storage_backend='filesystem'  # or 's3', 'azure'
)
```

### Committing Images

```python
# Commit an image
commit = repo.commit(
    image_path=Path('Win11_Enterprise_v1.0.wim'),
    message='Initial Windows 11 customization with gaming optimizations',
    version='1.0.0',
    tags=['production', 'baseline', 'Q4-2025'],
    metadata={
        'profile': 'gaming',
        'features': 150,
        'build_time': '45m'
    }
)

print(f"Committed: {commit.hash}")
print(f"Version: {commit.version}")
print(f"Timestamp: {commit.timestamp}")
```

### Viewing History

```python
# List commit history
history = repo.log(limit=10)
for commit in history:
    print(f"{commit.hash[:8]} - {commit.version}: {commit.message}")
    print(f"  Author: {commit.author}")
    print(f"  Date: {commit.timestamp}")
    print(f"  Tags: {', '.join(commit.tags)}")
    print()

# Get specific commit details
commit_details = repo.show(commit_hash='abc123def')
print(f"Version: {commit_details.version}")
print(f"Message: {commit_details.message}")
print(f"Changes: {len(commit_details.changes)} files modified")
```

### Branching

```python
# Create branch for variant
repo.create_branch('gaming-variant')

# Switch to branch
repo.checkout('gaming-variant')

# Commit to branch
commit = repo.commit(
    image_path=Path('Win11_Gaming.wim'),
    message='Add gaming-specific optimizations',
    version='1.0.0-gaming'
)

# List branches
branches = repo.list_branches()
for branch in branches:
    print(f"{'*' if branch.is_active else ' '} {branch.name}")
    print(f"  Latest: {branch.latest_commit_hash[:8]}")
    print(f"  Updated: {branch.last_updated}")

# Merge branch back to main
repo.checkout('main')
merge_result = repo.merge(
    branch='gaming-variant',
    strategy='ours',  # or 'theirs', 'manual'
    message='Merge gaming variant optimizations'
)
```

### Tagging

```python
# Create tag
repo.create_tag(
    name='v1.0.0',
    commit_hash='abc123def',
    message='Production release 1.0.0'
)

# Create annotated tag
repo.create_tag(
    name='production-2025-q4',
    commit_hash='abc123def',
    message='Q4 2025 production release',
    metadata={
        'approved_by': 'John Doe',
        'approval_date': '2025-11-01',
        'tested': True
    }
)

# List tags
tags = repo.list_tags()
for tag in tags:
    print(f"{tag.name} -> {tag.commit_hash[:8]}")
    print(f"  Message: {tag.message}")

# Checkout by tag
repo.checkout('v1.0.0')
```

### Comparing Versions

```python
# Diff between two versions
diff = repo.diff(
    from_version='v1.0.0',
    to_version='v1.1.0',
    detailed=True
)

print(f"Comparison: {diff.from_version} -> {diff.to_version}")
print(f"Files changed: {len(diff.files_changed)}")
print(f"Size difference: {diff.size_delta_mb}MB")

# Detailed changes
for file_change in diff.files_changed:
    print(f"\n{file_change.path}")
    print(f"  Status: {file_change.status}")  # added, modified, deleted
    print(f"  Size: {file_change.size_before} -> {file_change.size_after}")

# Registry changes
if diff.registry_changes:
    print(f"\nRegistry changes: {len(diff.registry_changes)}")
    for reg_change in diff.registry_changes:
        print(f"  {reg_change.key}\\{reg_change.value}")
        print(f"    Before: {reg_change.before}")
        print(f"    After: {reg_change.after}")

# Generate changelog
changelog = repo.generate_changelog(
    from_version='v1.0.0',
    to_version='v1.1.0',
    format='markdown'
)
Path('CHANGELOG.md').write_text(changelog)
```

### Rollback and Restore

```python
# Checkout previous version
repo.checkout('v1.0.0')

# Extract image from specific commit
repo.export(
    commit_hash='abc123def',
    output_path=Path('Win11_Enterprise_v1.0.0.wim')
)

# Restore from backup
repo.restore(
    commit_hash='abc123def',
    target_path=Path('restore/')
)

# Revert last commit
repo.revert(
    commit_hash='latest',
    message='Revert problematic changes from v1.1.0'
)
```

### Remote Repositories

```python
# Add remote repository
repo.add_remote(
    name='origin',
    url='s3://acme-deployforge/images',
    credentials={
        'access_key': 'AKIAIOSFODNN7EXAMPLE',
        'secret_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }
)

# Push to remote
repo.push(
    remote='origin',
    branch='main',
    tags=True
)

# Pull from remote
repo.pull(
    remote='origin',
    branch='main'
)

# Clone repository
new_repo = ImageRepository.clone(
    remote_url='s3://acme-deployforge/images',
    local_path=Path('/images/clone')
)
```

### Garbage Collection

```python
# Clean up unreferenced data
stats = repo.gc(
    aggressive=True,
    compress=True
)

print(f"Freed space: {stats.space_freed_mb}MB")
print(f"Objects removed: {stats.objects_removed}")
print(f"Duration: {stats.duration}s")
```

---

## Certificate Management

### Overview

The certificates module (`certificates.py`, 622 lines) handles certificate installation and management for trusted certificate stores in Windows images.

### Supported Certificate Stores

- **Root** - Trusted Root Certification Authorities
- **CA** - Intermediate Certification Authorities
- **TrustedPublisher** - Trusted Publishers (code signing)
- **TrustedPeople** - Trusted People
- **My** - Personal certificates

### Installing Certificates

```python
from deployforge.certificates import CertificateManager
from pathlib import Path

cert_manager = CertificateManager(
    image_path=Path('install.wim'),
    index=1
)

# Mount image
cert_manager.mount()

# Install root CA certificate
cert_manager.install_certificate(
    cert_path=Path('certs/Acme_Root_CA.cer'),
    store='Root',
    verify_before_install=True
)

# Install intermediate CA
cert_manager.install_certificate(
    cert_path=Path('certs/Acme_Intermediate_CA.cer'),
    store='CA'
)

# Install code signing certificate
cert_manager.install_certificate(
    cert_path=Path('certs/Acme_CodeSign.cer'),
    store='TrustedPublisher'
)

# Unmount and save
cert_manager.unmount(save_changes=True)
```

### Bulk Certificate Installation

```python
# Install multiple certificates
certificates = [
    {'path': 'certs/root_ca.cer', 'store': 'Root'},
    {'path': 'certs/intermediate_ca.cer', 'store': 'CA'},
    {'path': 'certs/codesign1.cer', 'store': 'TrustedPublisher'},
    {'path': 'certs/codesign2.cer', 'store': 'TrustedPublisher'},
]

cert_manager.install_bulk(certificates)
```

### PFX/P12 Certificates (with private keys)

```python
# Install PFX certificate
cert_manager.install_pfx(
    pfx_path=Path('certs/certificate.pfx'),
    password='P@ssw0rd',
    store='My',
    mark_exportable=False  # Security: prevent private key export
)
```

### Certificate Verification

```python
# Verify certificate before installation
from deployforge.certificates import CertificateValidator

validator = CertificateValidator()

# Validate certificate
validation_result = validator.validate_certificate(
    cert_path=Path('certs/root_ca.cer')
)

if validation_result.is_valid:
    print(f"Certificate is valid")
    print(f"  Subject: {validation_result.subject}")
    print(f"  Issuer: {validation_result.issuer}")
    print(f"  Valid from: {validation_result.not_before}")
    print(f"  Valid until: {validation_result.not_after}")
    print(f"  Thumbprint: {validation_result.thumbprint}")
else:
    print(f"Certificate validation failed: {validation_result.error}")

# Check if certificate is expired
if validation_result.is_expired:
    print("Warning: Certificate is expired")

# Check if certificate is revoked
revocation_status = validator.check_revocation(
    cert_path=Path('certs/root_ca.cer'),
    check_crl=True,
    check_ocsp=True
)

if revocation_status.is_revoked:
    print(f"Certificate is revoked: {revocation_status.reason}")
```

### CRL and OCSP Configuration

```python
# Configure CRL distribution points
cert_manager.configure_crl(
    crl_urls=[
        'http://pki.acme.local/crl/root.crl',
        'http://pki.acme.local/crl/intermediate.crl'
    ],
    cache_directory='C:\\Windows\\System32\\CertSrv\\CertEnroll',
    auto_update=True,
    update_interval_hours=24
)

# Configure OCSP responder
cert_manager.configure_ocsp(
    responder_url='http://ocsp.acme.local',
    fallback_to_crl=True,
    timeout_seconds=10
)
```

### Certificate Chain Validation

```python
# Verify certificate chain
chain_result = validator.verify_chain(
    cert_path=Path('certs/server_cert.cer'),
    intermediate_certs=[
        Path('certs/intermediate1.cer'),
        Path('certs/intermediate2.cer')
    ],
    root_cert=Path('certs/root_ca.cer')
)

if chain_result.is_valid:
    print("Certificate chain is valid")
    for idx, cert in enumerate(chain_result.chain):
        print(f"  {idx}: {cert.subject}")
else:
    print(f"Chain validation failed: {chain_result.error}")
```

### Enterprise PKI Integration

```python
# Configure for Active Directory Certificate Services
cert_manager.configure_enterprise_ca(
    ca_server='ca01.acme.local',
    ca_name='Acme-Enterprise-CA',
    auto_enrollment=True,
    certificate_templates=[
        'Workstation Authentication',
        'User'
    ]
)

# Enable auto-enrollment
cert_manager.enable_auto_enrollment(
    user_certificates=True,
    computer_certificates=True,
    update_expired_certificates=True
)
```

---

## Group Policy Deployment

### Overview

The GPO module (`gpo.py`, 658 lines) provides Group Policy Objects management and deployment for enterprise Windows images.

### Importing GPO Policies

```python
from deployforge.gpo import GPOManager
from pathlib import Path

gpo_manager = GPOManager(
    image_path=Path('install.wim'),
    index=1
)

# Mount image
gpo_manager.mount()

# Import GPO from XML
gpo_manager.import_policy(
    xml_path=Path('policies/baseline_security.xml'),
    name='Enterprise Security Baseline',
    apply=True
)

# Import multiple policies
policies = [
    'policies/windows11_hardening.xml',
    'policies/corporate_standards.xml',
    'policies/compliance_cis.xml'
]

for policy in policies:
    gpo_manager.import_policy(xml_path=Path(policy), apply=True)

# Unmount
gpo_manager.unmount(save_changes=True)
```

### Creating GPO Policies

```python
from deployforge.gpo import PolicyBuilder

# Create new policy
policy = PolicyBuilder(name='Custom Security Policy')

# Add settings
policy.add_setting(
    category='Security Settings/Local Policies/Security Options',
    setting='Interactive logon: Do not require CTRL+ALT+DEL',
    value='Disabled'
)

policy.add_setting(
    category='Security Settings/Account Policies/Password Policy',
    setting='Minimum password length',
    value=14
)

policy.add_setting(
    category='Security Settings/Account Policies/Account Lockout Policy',
    setting='Account lockout threshold',
    value=5
)

# Export to XML
policy.export(Path('policies/custom_security.xml'))

# Import to image
gpo_manager.import_policy(
    xml_path=Path('policies/custom_security.xml'),
    apply=True
)
```

### Administrative Templates (ADMX)

```python
# Import ADMX templates
gpo_manager.import_admx(
    admx_path=Path('admx/Office365.admx'),
    adml_path=Path('admx/en-US/Office365.adml')
)

# Configure Office 365 policy
policy = PolicyBuilder(name='Office 365 Configuration')

policy.add_setting(
    category='Microsoft Office 2016/Miscellaneous',
    setting='Block macros from running in Office files from the Internet',
    value='Enabled'
)

policy.add_setting(
    category='Microsoft Office 2016/Security Settings',
    setting='Scan encrypted macros in Word Open XML documents',
    value='Enabled'
)

gpo_manager.apply_policy(policy)
```

### Registry-Based Policies

```python
# Apply registry-based policy
gpo_manager.add_registry_policy(
    key='HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU',
    value='NoAutoUpdate',
    data=0,
    value_type='REG_DWORD',
    description='Enable automatic updates'
)

gpo_manager.add_registry_policy(
    key='HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender',
    value='DisableAntiSpyware',
    data=0,
    value_type='REG_DWORD',
    description='Enable Windows Defender'
)
```

### Compliance Policies

```python
# Apply CIS Windows 11 Benchmark
gpo_manager.apply_compliance_baseline(
    baseline='CIS_Windows_11_Enterprise_v1.0.0',
    level=1  # Level 1 or Level 2
)

# Apply STIG compliance
gpo_manager.apply_compliance_baseline(
    baseline='DISA_Windows_11_STIG_v1r1',
    severity=['CAT1', 'CAT2']  # CAT1, CAT2, CAT3
)

# Verify compliance
compliance_report = gpo_manager.verify_compliance(
    baseline='CIS_Windows_11_Enterprise_v1.0.0'
)

print(f"Compliance: {compliance_report.percentage}%")
print(f"Passed: {compliance_report.passed_checks}/{compliance_report.total_checks}")

for failed_check in compliance_report.failed_checks:
    print(f"\n{failed_check.id}: {failed_check.title}")
    print(f"  Severity: {failed_check.severity}")
    print(f"  Recommendation: {failed_check.recommendation}")
```

---

## Security & Compliance

### Security Hardening Profiles

```python
from deployforge.security import SecurityHardener, HardeningLevel

hardener = SecurityHardener(
    image_path=Path('install.wim'),
    index=1
)

# Apply hardening profile
hardener.mount()

# Basic hardening
hardener.apply_profile(HardeningLevel.BASIC)

# Enhanced hardening
hardener.apply_profile(HardeningLevel.ENHANCED)

# Maximum hardening
hardener.apply_profile(HardeningLevel.MAXIMUM)

# Custom hardening
hardener.configure(
    disable_guest_account=True,
    disable_admin_account=False,
    rename_admin_account='LocalAdmin',
    password_policy={
        'minimum_length': 14,
        'complexity': True,
        'max_age_days': 90,
        'history_count': 24
    },
    lockout_policy={
        'threshold': 5,
        'duration_minutes': 30,
        'reset_minutes': 30
    },
    audit_policy={
        'logon_events': True,
        'object_access': True,
        'policy_change': True,
        'account_management': True,
        'process_tracking': False
    },
    firewall={
        'enabled': True,
        'default_inbound': 'block',
        'default_outbound': 'allow'
    }
)

hardener.unmount(save_changes=True)
```

### Audit Logging

```python
from deployforge.audit import AuditLogger

# Configure audit logging
audit = AuditLogger(
    log_path=Path('/var/log/deployforge/audit.jsonl'),
    log_level='INFO',
    include_system_events=True,
    include_user_events=True
)

# Log operation
audit.log_operation(
    operation='image_modification',
    user='john.doe@acme.local',
    image_path='Win11_Enterprise.wim',
    changes=['debloat', 'privacy', 'security'],
    result='success',
    duration=245.3
)

# Query audit logs
entries = audit.query(
    start_date='2025-01-01',
    end_date='2025-12-31',
    operation='image_modification',
    user='john.doe@acme.local'
)

for entry in entries:
    print(f"{entry.timestamp}: {entry.operation} by {entry.user}")
    print(f"  Result: {entry.result}")
    print(f"  Changes: {', '.join(entry.changes)}")
```

---

## Batch Operations at Scale

### Parallel Processing

```python
from deployforge.batch import BatchProcessor
from pathlib import Path

# Initialize batch processor
batch = BatchProcessor(max_workers=4)

# Add images to batch
images = [
    Path('images/win11_pro.wim'),
    Path('images/win11_enterprise.wim'),
    Path('images/win11_education.wim'),
    Path('images/win10_ltsc.wim')
]

for image in images:
    batch.add_job(
        image_path=image,
        profile='enterprise',
        output_suffix='_custom'
    )

# Execute batch
results = batch.execute(
    progress_callback=lambda current, total: print(f"Progress: {current}/{total}")
)

# Check results
for result in results:
    print(f"{result.image_path}: {result.status}")
    if result.status == 'failed':
        print(f"  Error: {result.error}")
```

---

## Enterprise Workflows

### Workflow 1: Automated Monthly Update Integration

```python
# monthly_update_workflow.py
from deployforge import ImageManager
from deployforge.updates import UpdateManager
from deployforge.testing import VMTester, Hypervisor
from deployforge.versioning import ImageRepository
from deployforge.scheduler import JobScheduler
from pathlib import Path

def monthly_update_workflow():
    """Automated workflow for monthly Windows update integration"""

    # 1. Checkout latest baseline
    repo = ImageRepository(Path('/images/repo'))
    repo.checkout('production-baseline')
    repo.export('latest', Path('Win11_Baseline.wim'))

    # 2. Apply updates
    with ImageManager(Path('Win11_Baseline.wim')) as img:
        img.mount()

        updater = UpdateManager(img)
        updates = updater.download_latest_cumulative()
        updater.install_updates(updates)

        img.unmount(save_changes=True)

    # 3. Test updated image
    tester = VMTester(Path('Win11_Baseline.wim'), Hypervisor.HYPER_V)
    boot_result = tester.test_boot(timeout=300)

    if boot_result.status != 'PASSED':
        print("Boot test failed, aborting workflow")
        return False

    tester.cleanup_vm()

    # 4. Commit to version control
    commit = repo.commit(
        image_path=Path('Win11_Baseline.wim'),
        message=f'Monthly update integration - {datetime.now().strftime("%B %Y")}',
        version=f'1.0.{datetime.now().strftime("%Y%m")}',
        tags=['monthly-update', f'{datetime.now().strftime("%Y-%m")}']
    )

    # 5. Notify team
    send_notification(
        subject='Monthly Windows Update Integration Complete',
        message=f'Version {commit.version} is ready for testing'
    )

    return True

# Schedule for 1st of every month at 3 AM
scheduler = JobScheduler()
scheduler.schedule_function(
    func=monthly_update_workflow,
    schedule='0 3 1 * *',
    name='Monthly Update Integration'
)
```

### Workflow 2: Multi-Region Deployment

```python
# multi_region_deployment.py
from deployforge.integration import MDTManager
from deployforge.cloud import S3Storage, AzureBlobStorage
from deployforge.versioning import ImageRepository

def deploy_to_regions():
    """Deploy image to multiple regions"""

    # 1. Get latest production image
    repo = ImageRepository(Path('/images/repo'))
    repo.export('production', Path('Win11_Production.wim'))

    # 2. Upload to cloud storage (multi-region)
    # US East
    s3_us = S3Storage(region='us-east-1', bucket='acme-deploy-us')
    s3_us.upload(Path('Win11_Production.wim'), 'images/Win11_Production.wim')

    # EU West
    s3_eu = S3Storage(region='eu-west-1', bucket='acme-deploy-eu')
    s3_eu.upload(Path('Win11_Production.wim'), 'images/Win11_Production.wim')

    # Asia Pacific
    s3_ap = S3Storage(region='ap-southeast-1', bucket='acme-deploy-ap')
    s3_ap.upload(Path('Win11_Production.wim'), 'images/Win11_Production.wim')

    # 3. Update MDT deployment shares in each region
    regions = [
        {'name': 'US-East', 'mdt_server': 'mdt-us.acme.local'},
        {'name': 'EU-West', 'mdt_server': 'mdt-eu.acme.local'},
        {'name': 'Asia-Pacific', 'mdt_server': 'mdt-ap.acme.local'}
    ]

    for region in regions:
        mdt = MDTManager(server=region['mdt_server'])
        mdt.update_os_image(
            image_id='Win11_Production',
            wim_path=Path('Win11_Production.wim')
        )
        mdt.update_share()

        print(f"Updated {region['name']} deployment share")
```

---

## Monitoring & Audit Logging

### Real-Time Monitoring

```python
from deployforge.monitoring import Monitor

monitor = Monitor()

# Monitor build operations
monitor.start()

# Metrics collected:
# - CPU usage
# - Memory usage
# - Disk I/O
# - Network I/O
# - Operation duration
# - Error rates

# Get current metrics
metrics = monitor.get_metrics()
print(f"CPU: {metrics.cpu_percent}%")
print(f"Memory: {metrics.memory_mb}MB")
print(f"Operations/min: {metrics.operations_per_minute}")

# Export metrics
monitor.export_prometheus(Path('/metrics'))
```

---

## Cloud Integration

### AWS S3 Integration

```python
from deployforge.cloud import S3Storage

s3 = S3Storage(
    region='us-east-1',
    bucket='acme-deployforge',
    access_key='AKIAIOSFODNN7EXAMPLE',
    secret_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
)

# Upload image
s3.upload(
    local_path=Path('Win11_Enterprise.wim'),
    remote_path='images/Win11_Enterprise_v1.0.wim',
    metadata={
        'version': '1.0.0',
        'profile': 'enterprise',
        'created_by': 'DeployForge'
    }
)

# Download image
s3.download(
    remote_path='images/Win11_Enterprise_v1.0.wim',
    local_path=Path('downloaded.wim')
)
```

### Azure Blob Storage Integration

```python
from deployforge.cloud import AzureBlobStorage

azure = AzureBlobStorage(
    account_name='acmedeployforge',
    account_key='your_account_key',
    container='images'
)

# Upload
azure.upload(
    local_path=Path('Win11_Enterprise.wim'),
    blob_name='Win11_Enterprise_v1.0.wim'
)

# Download
azure.download(
    blob_name='Win11_Enterprise_v1.0.wim',
    local_path=Path('downloaded.wim')
)
```

---

## Best Practices

### 1. Version Control Everything
- Commit all image changes to version control
- Tag production releases
- Use branches for variants

### 2. Automate Testing
- Run VM boot tests for all images
- Validate compliance before deployment
- Test driver functionality

### 3. Schedule Regular Rebuilds
- Monthly update integration
- Quarterly full rebuilds
- Annual baseline reviews

### 4. Implement Proper Audit Logging
- Log all modifications
- Track user actions
- Maintain compliance records

### 5. Use Infrastructure as Code
- Define builds in YAML/JSON
- Version control configurations
- Enable reproducible builds

### 6. Secure Certificate Management
- Validate certificates before installation
- Use proper certificate stores
- Enable CRL/OCSP checking

### 7. Test Before Production
- Use VM testing
- Pilot deployments
- Staged rollouts

### 8. Monitor and Alert
- Track build success rates
- Monitor resource usage
- Alert on failures

---

## Troubleshooting

### Common Issues

#### Issue: VM Boot Test Fails

**Solution:**
```python
# Enable detailed logging
tester.configure(
    capture_screenshots=True,
    capture_logs=True,
    verbose=True
)

boot_result = tester.test_boot(timeout=600)

# Review screenshots
for screenshot in boot_result.details['screenshots']:
    # Inspect screenshots for boot errors
    pass

# Check logs
logs = boot_result.details['logs']
print(logs)
```

#### Issue: MDT Import Fails

**Solution:**
```python
# Verify MDT service status
mdt.check_service_status()

# Verify share permissions
mdt.verify_permissions(share_name='Production')

# Check logs
logs = mdt.get_logs(share_name='Production')
```

#### Issue: Certificate Installation Fails

**Solution:**
```python
# Validate certificate first
validator = CertificateValidator()
result = validator.validate_certificate(cert_path)

if not result.is_valid:
    print(f"Certificate invalid: {result.error}")

# Check certificate format
cert_info = validator.get_certificate_info(cert_path)
print(f"Format: {cert_info.format}")
print(f"Type: {cert_info.type}")
```

---

## Conclusion

This enterprise guide covers the advanced features of DeployForge for large-scale Windows deployment operations. For additional support:

- **Documentation**: See `/docs` directory
- **Examples**: See `/examples` directory
- **Issues**: Report at https://github.com/Cornman92/DeployForge/issues
- **Support**: Contact enterprise-support@deployforge.com

**Version**: 1.7.0
**Last Updated**: 2025-11-17
