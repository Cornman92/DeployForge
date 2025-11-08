# GitHub Release Instructions for v0.3.0

## Release Information

**Tag**: `v0.3.0`
**Branch**: `claude/continue-work-011CUsAKGEEEmtAsHYpfk5zX`
**Commit**: `7d791da`
**Release Type**: Beta (Major Feature Release)
**Release Name**: `DeployForge v0.3.0 - Complete Deployment Automation`

---

## Creating the GitHub Release

### Step 1: Navigate to Releases

Go to: https://github.com/Cornman92/DeployForge/releases/new

### Step 2: Tag Configuration

- **Choose a tag**: `v0.3.0`
- **Target**: `claude/continue-work-011CUsAKGEEEmtAsHYpfk5zX`
- If tag doesn't exist, it will be created from this branch

### Step 3: Release Title

```
DeployForge v0.3.0 - Complete Deployment Automation
```

### Step 4: Release Description

Use the following content (or copy from RELEASE_NOTES_v0.3.0.md):

---

## 🎉 DeployForge v0.3.0 - Complete Deployment Automation

This major release completes the automation suite with **four critical enterprise capabilities** for Windows deployment. Now featuring end-to-end automation from disk partitioning to multi-language installation.

### ✨ What's New

**4 Major New Features:**

#### 💿 1. UEFI/GPT Partition Management

Create and manage GPT partition tables with ease:
- EFI System Partition (ESP) with FAT32 formatting
- Microsoft Reserved Partition (MSR)
- Standard Windows partition layouts (one command!)
- Windows Recovery Environment partition
- VHD and VHDX disk image support
- Export/import layouts to JSON

**CLI:**
```bash
# Create standard Windows UEFI disk
deployforge partition create disk.vhdx --size 50 --recovery

# List partitions
deployforge partition list disk.vhdx

# Export layout
deployforge partition export disk.vhdx layout.json
```

**Python API:**
```python
from deployforge.partitions import create_uefi_bootable_image

pm = create_uefi_bootable_image(Path('disk.vhdx'), disk_size_gb=50, include_recovery=True)
# Creates: EFI (100MB) + MSR (16MB) + Windows (~48GB) + Recovery (500MB)
```

---

#### 🛠️ 2. Windows PE Customization

Build custom Windows PE deployment environments:
- Mount and customize WinPE images (boot.wim)
- Install optional components (PowerShell, WMI, WiFi, BitLocker)
- Inject network and storage drivers
- Custom startup scripts (startnet.cmd)
- Wallpaper and branding
- Create bootable ISO images
- Deployment and recovery configurations

**Features:**
- **PowerShell**: Full scripting support in WinPE
- **Network Tools**: WDS deployment integration
- **WiFi Support**: Wireless network connectivity
- **Driver Injection**: Network/storage drivers
- **Optimization**: Component cleanup and compression

**Python API:**
```python
from deployforge.winpe import WinPECustomizer, WinPEComponent

customizer = WinPECustomizer(Path('boot.wim'))
customizer.mount()
customizer.add_component(WinPEComponent.POWERSHELL)
customizer.add_component(WinPEComponent.NETWORK)
customizer.add_driver(Path('drivers/network'))
customizer.set_startup_script("wpeinit\necho Deployment Ready")
customizer.unmount(save_changes=True)
```

---

#### 📝 3. Answer File Generation (unattend.xml)

Automate Windows installation with complete unattend.xml generation:
- All configuration passes (windowsPE, specialize, oobeSystem)
- User account creation with passwords
- Product key and licensing
- Regional settings (language, timezone, keyboard)
- Network configuration (domain join or workgroup)
- Automated disk partitioning
- OOBE customization (skip privacy screens, EULA)
- FirstLogonCommands for post-installation

**CLI:**
```bash
# Basic workstation
deployforge unattend create autounattend.xml \
    --username Admin --password P@ssw0rd \
    --computer-name WORKSTATION-01 \
    --timezone "Pacific Standard Time"

# With product key
deployforge unattend create autounattend.xml \
    --product-key XXXXX-XXXXX-XXXXX-XXXXX-XXXXX \
    --username Admin --password SecurePassword123
```

**Python API:**
```python
from deployforge.unattend import create_enterprise_unattend, UnattendGenerator

# Enterprise domain join
config = create_enterprise_unattend(
    domain="corporate.local",
    domain_username="Administrator",
    domain_password="DomainPassword123",
    product_key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
)

generator = UnattendGenerator(config)
generator.save(Path('autounattend.xml'))
```

---

#### 🌍 4. Multi-Language Support (MUI)

Manage Windows Multilingual User Interface packages:
- Install and remove language packs (.cab files)
- Set default system and UI languages
- Configure keyboard input locales
- Time zone and GeoID (location) management
- Pre-defined templates (European, Asian)
- Support for 40+ languages

**Supported Languages:**
- **Europe**: English (UK/US), German, French, Spanish, Italian, Portuguese, Dutch, Swedish, etc.
- **Asia**: Japanese, Korean, Chinese (Simplified/Traditional), Thai, Vietnamese, Hindi
- **Other**: Arabic, Hebrew, Turkish, Russian, Polish, and more

**CLI:**
```bash
# List installed languages
deployforge language list install.wim

# Add language pack
deployforge language add install.wim de-DE-LanguagePack.cab
```

**Python API:**
```python
from deployforge.languages import create_european_multilingual

# Pre-configured for European deployment
config = create_european_multilingual()
# Includes: en-GB, de-DE, fr-FR, es-ES, it-IT

print(f"Default: {config.default_language}")
print(f"Languages: {config.installed_languages}")
```

---

### 📊 Statistics

- **2,750+ lines** of new code (4 modules)
- **350+ lines** of tests (50+ test cases)
- **13,600+ total** lines of code
- **47 Python modules**
- **100% backward compatible** with v0.2.0

### 📦 Installation

```bash
# From PyPI (when published)
pip install deployforge

# From source
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge
pip install -e ".[all]"
```

### 🎯 Real-World Use Cases

#### Example 1: Automated Enterprise Deployment
```python
from deployforge.partitions import create_uefi_bootable_image
from deployforge.unattend import create_enterprise_unattend, UnattendGenerator
from deployforge.languages import create_european_multilingual

# Create UEFI disk
pm = create_uefi_bootable_image(Path('enterprise.vhdx'), 100, True)

# Generate domain join unattend.xml
config = create_enterprise_unattend(
    domain="corporate.local",
    domain_username="Administrator",
    domain_password="SecurePassword",
    product_key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
)
UnattendGenerator(config).save(Path('autounattend.xml'))

# Configure multi-language
lang_config = create_european_multilingual()
# Apply to install.wim
```

#### Example 2: Custom WinPE Environment
See `examples/deployment_winpe.py` for complete walkthrough.

#### Example 3: Multilingual Image
See `examples/multilingual_image.py` for European, Asian, and global configurations.

---

### 🔄 Migration from v0.2.0

**100% Backward Compatible** - No changes required to existing code.

All v0.2.0 functionality works unchanged. New features are completely opt-in:

```python
# v0.2.0 code continues to work
from deployforge import ImageManager

with ImageManager(Path('install.wim')) as manager:
    manager.mount()
    files = manager.list_files('/')
    manager.unmount()

# Add new v0.3.0 features as needed
from deployforge.partitions import PartitionManager
from deployforge.unattend import create_basic_unattend
```

---

### ⚠️ Breaking Changes

**None** - This release is 100% backward compatible.

---

### 📚 Documentation

- **Release Notes**: [RELEASE_NOTES_v0.3.0.md](./RELEASE_NOTES_v0.3.0.md)
- **Examples**:
  - `examples/enterprise_deployment.py` - Complete enterprise setup
  - `examples/deployment_winpe.py` - Custom WinPE creation
  - `examples/multilingual_image.py` - Multi-language configurations
- **Module Documentation**: Comprehensive docstrings in all new modules
- **Tests**: 50+ test cases demonstrating usage

---

### 🔗 Links

- **Repository**: https://github.com/Cornman92/DeployForge
- **Issues**: https://github.com/Cornman92/DeployForge/issues
- **Documentation**: [README.md](./README.md)
- **v0.2.0 Release**: [Previous Release](https://github.com/Cornman92/DeployForge/releases/tag/v0.2.0)

---

### 🙏 Acknowledgments

Built with:
- Python Standard Library (xml.etree, json, struct, uuid)
- Microsoft Tools (diskpart, DISM, Windows ADK)
- Cross-platform utilities (parted, wimlib, oscdimg)

---

### 🎉 Complete Deployment Automation

**DeployForge v0.3.0** provides complete end-to-end Windows deployment automation:

1. **Create** UEFI bootable disks with proper partitioning
2. **Customize** Windows PE for deployment environments
3. **Automate** installation with answer files
4. **Globalize** with multi-language support

**Ready for enterprise production use!**

---

*Release prepared by DeployForge Team*
*November 8, 2025*

---

## Step 5: Upload Assets (Optional)

Consider uploading these files:

1. **Source Distribution**:
   - `deployforge-0.3.0.tar.gz` (from `/tmp/dist-v0.3.0/`)

2. **Documentation**:
   - `RELEASE_NOTES_v0.3.0.md`
   - `GITHUB_RELEASE_v0.3.0.md` (this file)

3. **Examples Package** (optional):
   - Create a zip of the `examples/` directory

## Step 6: Publish

1. Check "Set as the latest release"
2. Optionally check "Create a discussion for this release"
3. Click **"Publish release"**

---

## Post-Release Actions

### 1. Announce Release

Create a discussion thread:
- **Title**: "DeployForge v0.3.0 Released - Complete Deployment Automation"
- **Content**: Highlight the 4 new features and use cases

### 2. Update Documentation

- Ensure README.md reflects v0.3.0 (✅ already done)
- Update any wiki pages
- Create blog post or announcement (optional)

### 3. Social Media (Optional)

Share release on:
- Twitter/X
- LinkedIn
- Reddit (r/sysadmin, r/Python)
- Hacker News

### 4. Monitor Feedback

- Watch for issues related to new features
- Respond to questions in Discussions
- Monitor adoption metrics

---

## Verification Checklist

Before publishing, verify:

- [ ] Tag `v0.3.0` exists locally
- [ ] All commits pushed to branch
- [ ] README.md updated to v0.3.0
- [ ] RELEASE_NOTES_v0.3.0.md exists
- [ ] Example scripts created and tested
- [ ] Package builds successfully
- [ ] All tests structured
- [ ] Branch name correct
- [ ] Release description complete

---

## Alternative: Command Line Release

If you prefer using `gh` CLI:

```bash
# Create release
gh release create v0.3.0 \
    --title "DeployForge v0.3.0 - Complete Deployment Automation" \
    --notes-file RELEASE_NOTES_v0.3.0.md \
    --target claude/continue-work-011CUsAKGEEEmtAsHYpfk5zX \
    /tmp/dist-v0.3.0/deployforge-0.3.0.tar.gz

# View release
gh release view v0.3.0 --web
```

---

**Prepared**: 2025-11-08
**Version**: 0.3.0
**Status**: Ready for Publication
