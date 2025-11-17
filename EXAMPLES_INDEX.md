# DeployForge Examples Index

**Version**: 1.7.0
**Last Updated**: 2025-11-17
**Location**: `/examples` directory

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Examples](#quick-start-examples)
3. [Use Case Examples](#use-case-examples)
4. [Advanced Examples](#advanced-examples)
5. [How to Use Examples](#how-to-use-examples)
6. [Example Categories](#example-categories)
7. [Contributing Examples](#contributing-examples)

---

## Introduction

This document provides a comprehensive index of all DeployForge example scripts. Each example demonstrates specific features and real-world use cases to help you get started with DeployForge.

### Example Organization

Examples are organized by complexity and use case:
- **Beginner** - Simple, focused demonstrations of core features
- **Intermediate** - Real-world scenarios with multiple features
- **Advanced** - Complex enterprise workflows with multiple modules

### Prerequisites

Before running examples:

1. **Install DeployForge**:
   ```bash
   pip install deployforge
   ```

2. **Obtain Windows images**:
   - Download Windows 11 ISO from Microsoft
   - Extract `install.wim` from `sources/` folder

3. **Run as Administrator** (Windows) or with `sudo` (Linux)

4. **Update file paths** in examples to match your environment

---

## Quick Start Examples

### 1. Basic Usage (`basic_usage.py`)

**Difficulty**: Beginner
**Lines**: 196
**Estimated Runtime**: 2-5 minutes

#### Description

Demonstrates fundamental DeployForge operations including:
- Getting image information
- Listing files in images
- Adding files to images
- Extracting files from images
- Mounting and unmounting images

#### Key Concepts

- Using `ImageManager` context manager
- Image file operations (list, add, extract)
- Working with different image formats (WIM, ISO)

#### Usage

```bash
# 1. Edit file paths in script
nano examples/basic_usage.py

# Update these paths:
# - image_path = Path("path/to/your/image.wim")
# - iso_path = Path("path/to/windows.iso")

# 2. Run script
python examples/basic_usage.py
```

#### Example Functions

```python
# Example 1: Get image information
example_1_get_info()

# Example 2: List files in image
example_2_list_files()

# Example 3: Add file to image
example_3_add_file()

# Example 4: Extract file from image
example_4_extract_file()

# Example 5: Mount and work with image
example_5_mount_and_work()
```

#### Expected Output

```
============================================================
Example 1: Get Image Information
============================================================

Image: install.wim
Format: wim
Size: 4,523,456,789 bytes
Mounted: False
```

---

## Use Case Examples

### 2. Gaming PC Build (`gaming_pc_build.py`)

**Difficulty**: Intermediate
**Lines**: 258
**Estimated Runtime**: 30-45 minutes

#### Description

Creates a Windows image optimized for gaming performance with:
- Bloatware removal (Xbox, Teams, OneDrive, Cortana)
- Gaming-specific registry optimizations
- GPU driver injection (NVIDIA/AMD)
- Gaming runtime libraries (DirectX, Visual C++)
- Performance power plan
- Game Mode enabled

#### Key Features

- Template system usage (`GAMING_TEMPLATE`)
- Registry editing for performance
- Driver injection
- Service optimization
- Gaming runtime installation

#### Usage

```bash
# 1. Prepare files
# - Source: install.wim (Windows 11)
# - GPU drivers folder (e.g., NVIDIA Game Ready Driver)

# 2. Run builder
python examples/gaming_pc_build.py \
    --source install.wim \
    --output Win11_Gaming.wim \
    --gpu-drivers drivers/nvidia/

# Or edit script and run:
python examples/gaming_pc_build.py
```

#### Customization Points

```python
# Modify bloatware removal list
GAMING_BLOATWARE = [
    'Microsoft.XboxApp',
    'Microsoft.XboxGameOverlay',
    'Microsoft.Teams',
    'Microsoft.OneDrive',
    # Add more apps to remove
]

# Modify registry tweaks
GAMING_REGISTRY_TWEAKS = {
    'Game Bar': ('HKCU\\SOFTWARE\\Microsoft\\GameBar', 'AllowAutoGameMode', 1),
    'Game Mode': ('HKCU\\SOFTWARE\\Microsoft\\GameBar', 'AutoGameModeEnabled', 1),
    # Add more tweaks
}
```

#### Target Audience

- Gamers building custom Windows installations
- System builders optimizing for gaming PCs
- Anyone wanting maximum gaming performance

---

### 3. Enterprise Workstation (`enterprise_workstation.py`)

**Difficulty**: Intermediate
**Lines**: 412
**Estimated Runtime**: 45-60 minutes

#### Description

Creates a hardened enterprise workstation image with:
- Security baseline (CIS/STIG)
- Corporate applications (Office 365, Teams)
- Security tools (endpoint protection, VPN client)
- Group Policy Objects
- Certificate installation
- Audit logging enabled
- BitLocker preparation
- Domain join configuration

#### Key Features

- Security hardening profiles
- GPO import and application
- Certificate management
- Corporate branding (wallpaper, OEM info)
- Compliance verification

#### Usage

```bash
python examples/enterprise_workstation.py \
    --source install.wim \
    --output Win11_Enterprise_Secure.wim \
    --company "Acme Corporation" \
    --domain "acme.local"
```

#### Configuration Files Required

```
config/
├── certificates/
│   ├── root_ca.cer
│   ├── intermediate_ca.cer
│   └── codesign.cer
├── policies/
│   ├── baseline_security.xml
│   └── corporate_standards.xml
├── branding/
│   ├── wallpaper.jpg
│   └── logo.bmp
└── apps/
    ├── Office365/
    ├── CrowdStrike/
    └── VPN_Client/
```

#### Target Audience

- Enterprise IT administrators
- Security professionals
- System administrators managing corporate fleets

---

### 4. Windows 11 Custom (`windows11_custom.py`)

**Difficulty**: Beginner to Intermediate
**Lines**: 286
**Estimated Runtime**: 20-30 minutes

#### Description

Demonstrates common Windows 11 customizations:
- Privacy-focused debloating
- UI customization (Start Menu, Taskbar)
- Microsoft Edge configuration
- Windows Update settings
- Performance optimizations
- Modern context menus

#### Key Features

- Windows 11 specific tweaks
- Privacy hardening (telemetry, Cortana, ads)
- UI/UX improvements
- Edge browser management
- Windows Update control

#### Usage

```bash
python examples/windows11_custom.py \
    --source install.wim \
    --output Win11_Custom.wim \
    --privacy enhanced \
    --debloat aggressive
```

#### Privacy Levels

- **Basic**: Disable telemetry and ads
- **Enhanced**: + Disable Cortana, location services
- **Maximum**: + Disable all data collection, remove Edge

#### Target Audience

- Privacy-conscious users
- Home users wanting cleaner Windows 11
- Anyone tired of Windows bloatware

---

### 5. Enterprise Deployment (`enterprise_deployment.py`)

**Difficulty**: Advanced
**Lines**: 220
**Estimated Runtime**: 15-20 minutes (script only, deployment varies)

#### Description

Demonstrates enterprise deployment workflows:
- MDT deployment share integration
- SCCM package creation
- Task sequence automation
- Multi-region distribution
- Automated testing before deployment

#### Key Features

- MDT integration
- SCCM integration
- Automated testing
- Multi-region deployment
- Rollback procedures

#### Usage

```bash
python examples/enterprise_deployment.py \
    --image Win11_Enterprise.wim \
    --mdt-share "\\\\mdt01\\DeploymentShare$" \
    --sccm-server "sccm01.acme.local" \
    --sccm-site "ACM"
```

#### Workflow Steps

1. Import image to MDT
2. Create task sequence
3. Generate boot images
4. Create SCCM package
5. Distribute to distribution points
6. Deploy to pilot collection
7. Monitor deployment status

#### Target Audience

- Enterprise deployment engineers
- SCCM administrators
- MDT power users

---

### 6. Multilingual Image (`multilingual_image.py`)

**Difficulty**: Intermediate
**Lines**: 340
**Estimated Runtime**: 60-90 minutes (large downloads)

#### Description

Creates a multilingual Windows image with:
- Multiple language packs (5+ languages)
- Language features (fonts, OCR, speech)
- Default language configuration
- Keyboard layouts
- Regional settings

#### Key Features

- Language pack installation
- MUI (Multilingual User Interface)
- Feature on Demand installation
- Time zone configuration
- Regional format settings

#### Supported Languages

- English (en-US)
- Spanish (es-ES)
- French (fr-FR)
- German (de-DE)
- Chinese Simplified (zh-CN)
- Japanese (ja-JP)
- Arabic (ar-SA)
- And 30+ more...

#### Usage

```bash
python examples/multilingual_image.py \
    --source install.wim \
    --output Win11_Multilingual.wim \
    --languages en-US,es-ES,fr-FR,de-DE,ja-JP \
    --default en-US
```

#### Target Audience

- Multinational corporations
- Educational institutions
- Government organizations
- Global deployment scenarios

---

### 7. Enhanced Modules Examples (`enhanced_modules_examples.py`)

**Difficulty**: Intermediate
**Lines**: 442
**Estimated Runtime**: 30-45 minutes

#### Description

Comprehensive demonstration of all 9 enhanced modules:

1. **DevEnv** - Development environments (Python, Node.js, .NET, Java)
2. **Browsers** - Browser installation and configuration (17+ browsers)
3. **Creative** - Creative software suite (Adobe, OBS, GIMP, Blender)
4. **Privacy** - Privacy hardening (4 levels: Basic → Maximum)
5. **Launchers** - Gaming platforms (Steam, Epic, GOG, Origin)
6. **UI Customization** - UI themes and profiles (6 profiles)
7. **Backup** - Backup and recovery solutions (5 profiles)
8. **Wizard** - Setup wizard with presets (9 presets)
9. **Portable** - Portable applications (20+ app catalog)

#### Module Highlights

```python
# Example 1: Developer Workstation
from deployforge.devenv import DevEnvironmentManager, DevProfile

dev_mgr = DevEnvironmentManager(image)
dev_mgr.apply_profile(DevProfile.FULL_STACK)  # Python, Node, Docker, VSCode

# Example 2: Privacy Hardening
from deployforge.privacy_hardening import PrivacyManager, PrivacyLevel

privacy = PrivacyManager(image)
privacy.apply_level(PrivacyLevel.MAXIMUM)  # Maximum privacy protection

# Example 3: UI Theme
from deployforge.ui_customization import UICustomizer, UIProfile

ui = UICustomizer(image)
ui.apply_profile(UIProfile.DARK_MODERN)  # Modern dark theme
```

#### Usage

```bash
# Run all examples
python examples/enhanced_modules_examples.py --all

# Run specific example
python examples/enhanced_modules_examples.py --module devenv
python examples/enhanced_modules_examples.py --module privacy
python examples/enhanced_modules_examples.py --module browsers
```

#### Target Audience

- Developers learning DeployForge enhanced modules
- Anyone wanting to see advanced features
- System builders creating specialized images

---

## Advanced Examples

### 8. Templates Example (`templates_example.py`)

**Difficulty**: Beginner
**Lines**: 124
**Estimated Runtime**: 5-10 minutes (demo only)

#### Description

Demonstrates the template system for reusable customization workflows:
- Using predefined templates (Gaming, Workstation, Enterprise)
- Creating custom templates
- Saving and loading templates
- Template composition (combining templates)

#### Key Features

- Predefined template usage
- Custom template creation
- Template serialization (YAML/JSON)
- Template variables

#### Usage

```bash
python examples/templates_example.py
```

#### Template Structure

```python
from deployforge.templates import Template

# Create custom template
template = Template(
    name="Custom Development Template",
    description="Optimized for full-stack development",
    steps=[
        {'action': 'debloat', 'apps': ['Xbox', 'Teams']},
        {'action': 'install', 'app': 'VSCode'},
        {'action': 'install', 'app': 'Python 3.11'},
        {'action': 'registry', 'key': 'HKLM\\...', 'value': '...'},
    ]
)

# Save template
template.save('templates/dev_template.yaml')

# Load and apply
template = Template.load('templates/dev_template.yaml')
template.apply(image)
```

#### Target Audience

- Users who build multiple similar images
- Organizations standardizing configurations
- Anyone wanting reproducible builds

---

### 9. WinPE Deployment (`deployment_winpe.py`)

**Difficulty**: Advanced
**Lines**: 293
**Estimated Runtime**: 20-30 minutes

#### Description

Creates a customized Windows PE (Preinstallation Environment) image for deployment:
- Custom WinPE with drivers
- PowerShell support
- Network utilities
- Deployment scripts
- Custom branding

#### Key Features

- WinPE customization
- Driver injection (network, storage)
- PowerShell module installation
- Script integration
- Boot menu customization

#### Usage

```bash
python examples/deployment_winpe.py \
    --winpe-wim "C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Windows Preinstallation Environment\amd64\en-us\winpe.wim" \
    --output custom_winpe.wim \
    --drivers drivers/ \
    --scripts scripts/
```

#### WinPE Components

- **Base WinPE** - Windows PE 11.0
- **Drivers** - Network and storage drivers
- **Tools** - Deployment utilities (DISM, diskpart)
- **PowerShell** - PowerShell 7.x
- **Scripts** - Custom deployment automation

#### Target Audience

- Deployment engineers
- IT professionals doing bare-metal deployments
- Advanced users creating recovery media

---

## How to Use Examples

### General Instructions

1. **Clone or Download Repository**:
   ```bash
   git clone https://github.com/Cornman92/DeployForge.git
   cd DeployForge/examples
   ```

2. **Install Dependencies**:
   ```bash
   pip install -e ..
   ```

3. **Edit File Paths**:
   - Open example script in text editor
   - Update paths to match your environment:
     - Source images
     - Output paths
     - Driver locations
     - Configuration files

4. **Run as Administrator/Root**:
   ```bash
   # Windows (PowerShell as Administrator)
   python examples/basic_usage.py

   # Linux
   sudo python3 examples/basic_usage.py
   ```

5. **Review Output**:
   - Check console output for progress
   - Review logs in `~/.config/DeployForge/logs/`
   - Inspect output image

### Modifying Examples

All examples are designed to be educational and modifiable:

```python
# Example: Modify gaming_pc_build.py

# 1. Add more bloatware to remove
GAMING_BLOATWARE.append('Microsoft.YourPhone')

# 2. Add custom registry tweaks
GAMING_REGISTRY_TWEAKS['Custom Setting'] = (
    'HKLM\\SOFTWARE\\CustomKey',
    'CustomValue',
    1
)

# 3. Change GPU driver path
gpu_drivers = Path('drivers/my_custom_drivers/')
```

### Best Practices

1. **Test on Copy**: Always work on a copy of your original image
2. **Backup**: Keep backups of working images
3. **Incremental Changes**: Make one change at a time, test thoroughly
4. **Document**: Comment your modifications
5. **Version Control**: Use git to track changes to example scripts

---

## Example Categories

### By Difficulty

#### Beginner
- `basic_usage.py` - Core functionality demonstration
- `templates_example.py` - Template system basics
- `windows11_custom.py` - Simple customization

#### Intermediate
- `gaming_pc_build.py` - Gaming optimization
- `enterprise_workstation.py` - Enterprise hardening
- `multilingual_image.py` - Multi-language support
- `enhanced_modules_examples.py` - Enhanced modules demo

#### Advanced
- `enterprise_deployment.py` - MDT/SCCM integration
- `deployment_winpe.py` - WinPE customization

### By Use Case

#### Personal Use
- `gaming_pc_build.py` - Gaming PC
- `windows11_custom.py` - Privacy-focused Windows 11

#### Business/Enterprise
- `enterprise_workstation.py` - Secure workstation
- `enterprise_deployment.py` - Large-scale deployment
- `multilingual_image.py` - Global deployments

#### Development
- `enhanced_modules_examples.py` - Developer tools
- `templates_example.py` - Automated workflows

#### Education
- `basic_usage.py` - Learning DeployForge
- All examples serve as learning resources

---

## Example Comparison Table

| Example | Difficulty | Runtime | Key Features | Target Audience |
|---------|-----------|---------|--------------|----------------|
| `basic_usage.py` | Beginner | 2-5 min | Core operations | New users |
| `windows11_custom.py` | Beginner-Int | 20-30 min | Privacy, debloat | Home users |
| `templates_example.py` | Beginner | 5-10 min | Template system | Automation |
| `gaming_pc_build.py` | Intermediate | 30-45 min | Gaming optimization | Gamers |
| `enterprise_workstation.py` | Intermediate | 45-60 min | Security hardening | IT admins |
| `multilingual_image.py` | Intermediate | 60-90 min | Multi-language | Global orgs |
| `enhanced_modules_examples.py` | Intermediate | 30-45 min | All 9 modules | Developers |
| `enterprise_deployment.py` | Advanced | 15-20 min | MDT/SCCM | Deployment engineers |
| `deployment_winpe.py` | Advanced | 20-30 min | WinPE customization | Advanced users |

---

## Running All Examples

### Sequential Execution

```bash
# Run all examples in sequence
for example in examples/*.py; do
    echo "Running: $example"
    python "$example" || echo "Failed: $example"
done
```

### Testing Examples

```bash
# Test all examples (dry-run mode)
python test_examples.py --dry-run

# Test specific example
python test_examples.py --example gaming_pc_build.py
```

---

## Common Issues

### Issue: "Image not found"

**Solution**: Update file paths in example scripts to match your environment.

```python
# Change this:
image_path = Path("path/to/your/image.wim")

# To your actual path:
image_path = Path("C:/Users/Admin/Downloads/install.wim")  # Windows
# or
image_path = Path("/home/user/images/install.wim")  # Linux
```

### Issue: "Permission denied"

**Solution**: Run as Administrator (Windows) or with sudo (Linux).

```bash
# Windows: Run PowerShell as Administrator
python examples/basic_usage.py

# Linux
sudo python3 examples/basic_usage.py
```

### Issue: "Module not found"

**Solution**: Install DeployForge and dependencies.

```bash
pip install deployforge
# or
pip install -e .
```

### Issue: Example runs but produces errors

**Solution**: Check logs for detailed error messages.

```bash
# View logs
tail -f ~/.config/DeployForge/logs/deployforge.log  # Linux
# or
type %LOCALAPPDATA%\DeployForge\logs\deployforge.log  # Windows
```

---

## Contributing Examples

We welcome community contributions! To submit an example:

### Contribution Guidelines

1. **Clear Purpose**: Example should demonstrate specific feature or use case
2. **Well-Documented**: Include comprehensive docstrings and comments
3. **Self-Contained**: Minimize external dependencies
4. **Educational**: Teach best practices
5. **Tested**: Verify example works correctly

### Example Template

```python
#!/usr/bin/env python3
"""
Example Title

Brief description of what this example demonstrates.

Key Features:
- Feature 1
- Feature 2
- Feature 3

Requirements:
- Requirement 1
- Requirement 2

Usage:
    python example_name.py --arg1 value1 --arg2 value2
"""

from pathlib import Path
from deployforge import ImageManager

def main():
    """Main example function."""
    print("=" * 60)
    print("Example: Title")
    print("=" * 60)

    # Your code here
    pass

if __name__ == "__main__":
    main()
```

### Submission Process

1. Fork repository
2. Create example in `examples/` directory
3. Add entry to this EXAMPLES_INDEX.md
4. Submit pull request
5. Address review feedback

---

## Additional Resources

### Documentation

- **README.md** - Project overview and quick start
- **CLAUDE.md** - AI assistant guide and architecture
- **GUI_GUIDE.md** - Modern GUI user guide
- **ENTERPRISE_GUIDE.md** - Enterprise features guide
- **TROUBLESHOOTING.md** - Common issues and solutions
- **API_REFERENCE.md** - Complete API documentation
- **MODULE_REFERENCE.md** - All 54 modules catalog

### External Resources

- **GitHub Repository**: https://github.com/Cornman92/DeployForge
- **Issue Tracker**: https://github.com/Cornman92/DeployForge/issues
- **Documentation Site**: https://deployforge.readthedocs.io
- **Discord Community**: https://discord.gg/deployforge

### Getting Help

If you have questions about examples:

1. Check this index first
2. Review example source code and comments
3. Check TROUBLESHOOTING.md
4. Search GitHub issues
5. Ask on Discord
6. Open a GitHub issue

---

## Quick Reference

### Running Examples

```bash
# Basic usage
python examples/basic_usage.py

# Gaming build
python examples/gaming_pc_build.py

# Enterprise workstation
python examples/enterprise_workstation.py

# Windows 11 custom
python examples/windows11_custom.py

# All enhanced modules
python examples/enhanced_modules_examples.py --all

# Templates
python examples/templates_example.py

# Multilingual
python examples/multilingual_image.py

# Enterprise deployment
python examples/enterprise_deployment.py

# WinPE
python examples/deployment_winpe.py
```

### Example Downloads

All examples are included in the repository. To download only examples:

```bash
# Clone repository
git clone https://github.com/Cornman92/DeployForge.git

# Navigate to examples
cd DeployForge/examples

# Or download specific example
curl -O https://raw.githubusercontent.com/Cornman92/DeployForge/main/examples/basic_usage.py
```

---

**Version**: 1.7.0
**Last Updated**: 2025-11-17
**Total Examples**: 9
**Repository**: https://github.com/Cornman92/DeployForge

For questions or contributions, please visit our GitHub repository or join our Discord community.
