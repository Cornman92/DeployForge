# DeployForge Quick Start Guide

**Get up and running with DeployForge in 10 minutes!**

**Version**: 1.7.0
**Last Updated**: 2025-11-17

---

## What is DeployForge?

DeployForge is an enterprise Windows deployment suite that automates Windows image customization. It helps you:

- 🗑️ **Remove bloatware** - Remove Xbox, OneDrive, Teams, Cortana, and 100+ unwanted apps
- 🔒 **Enhance privacy** - Disable telemetry, tracking, and data collection
- 🎮 **Optimize for gaming** - Install drivers, optimize performance, add gaming platforms
- 💻 **Set up dev environments** - Python, Node.js, Docker, IDEs, and more
- 🏢 **Harden for enterprise** - Security baselines, GPO, certificates, compliance
- ⚡ **Automate everything** - Infrastructure as Code, job scheduling, batch processing

---

## Installation

### Requirements

- **Python** 3.9, 3.10, 3.11, or 3.12
- **Windows 10/11**, Linux, or macOS
- **Administrator/root privileges**
- **8GB+ RAM** (16GB recommended)
- **20GB+ free disk space**

### Install from PyPI

```bash
pip install deployforge
```

### Install from Source

```bash
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge
pip install -e .
```

### Verify Installation

```bash
deployforge --version
# Output: DeployForge version 0.3.0
```

---

## Your First Image Customization (5 minutes)

### Step 1: Get a Windows Image

**Option A: Extract from Windows ISO**

1. Download Windows 11 ISO from [Microsoft](https://www.microsoft.com/software-download/windows11)
2. Mount or extract the ISO
3. Copy `sources/install.wim` to your working directory

**Option B: Use Existing Image**

If you already have a `install.wim`, `install.esd`, or Windows ISO, you're ready!

### Step 2: Open the Modern GUI

```bash
deployforge gui
```

Or on Windows, run:
```
python -m deployforge.gui_modern
```

### Step 3: Load Your Image

**Three ways to load:**

1. **Drag and drop** the WIM/ESD/ISO file onto the window
2. Click **"Select Image"** button and browse
3. Select from **Recent Files** (if you've used it before)

### Step 4: Choose a Profile

Click the **"Profiles"** tab and select one:

- **🎮 Gaming** - Optimized for gaming PCs (Steam, drivers, performance)
- **💻 Developer** - Development tools (Python, Node.js, Docker, IDEs)
- **🏢 Enterprise** - Security hardening and corporate tools
- **🎓 Student** - Educational tools and productivity apps
- **🎨 Creator** - Creative software (OBS, GIMP, video editing)
- **⚙️ Custom** - Pick your own features

### Step 5: Build Your Image

1. Click **"Build"** tab to review selected features
2. Click **"Start Build"** button
3. Wait 10-30 minutes (depending on selections)
4. Your customized image will be saved!

**Done!** Your customized Windows image is ready for deployment.

---

## Command-Line Quick Start (3 minutes)

### Get Image Info

```bash
deployforge info install.wim
```

**Output:**
```
Image: install.wim
Format: WIM
Size: 4.3 GB
Indexes: 4
  [1] Windows 11 Home
  [2] Windows 11 Home N
  [3] Windows 11 Pro
  [4] Windows 11 Pro N
```

### Mount an Image

```bash
# Windows
deployforge mount install.wim --index 3

# Linux
sudo deployforge mount install.wim --index 3
```

### List Files in Image

```bash
deployforge list install.wim --index 3 --path /Windows/System32
```

### Add a File

```bash
deployforge add install.wim --index 3 \
    --source myapp.exe \
    --destination /Windows/System32/myapp.exe
```

### Unmount and Save

```bash
deployforge unmount install.wim --save
```

---

## Python API Quick Start (5 minutes)

### Basic Usage

```python
from pathlib import Path
from deployforge import ImageManager

# Open image with context manager
with ImageManager(Path('install.wim')) as img:
    # Get info
    info = img.get_info()
    print(f"Image has {info['index_count']} indexes")

    # Mount image
    mount_point = img.mount(index=3)

    # List files
    files = img.list_files('/Windows')
    print(f"Found {len(files)} files")

    # Add file
    img.add_file(
        source=Path('myapp.exe'),
        destination='/Windows/System32/myapp.exe'
    )

    # Unmount and save
    img.unmount(save_changes=True)

print("✓ Image customized successfully!")
```

### Gaming PC Optimization

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.gaming import GamingOptimizer, GamingProfile

# Open image
with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)

    # Apply gaming optimizations
    gaming = GamingOptimizer(img)
    gaming.apply_profile(GamingProfile.EXTREME)

    # Install gaming runtimes
    gaming.install_runtimes(
        directx=True,
        vcredist=True,
        dotnet=True
    )

    # Optimize services
    gaming.optimize_services()

    # Save changes
    img.unmount(save_changes=True)

print("🎮 Gaming optimizations applied!")
```

### Remove Bloatware

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.debloat import DebloatManager

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)

    # Remove bloatware
    debloat = DebloatManager(img)
    debloat.remove_default_apps([
        'Microsoft.XboxApp',
        'Microsoft.XboxGameOverlay',
        'Microsoft.Teams',
        'Microsoft.OneDrive',
        'Microsoft.BingWeather',
        'Cortana'
    ])

    img.unmount(save_changes=True)

print("🗑️ Bloatware removed!")
```

### Privacy Hardening

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.privacy_hardening import PrivacyManager, PrivacyLevel

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)

    # Apply privacy hardening
    privacy = PrivacyManager(img)
    privacy.apply_level(PrivacyLevel.ENHANCED)

    # Disable specific tracking
    privacy.disable_telemetry()
    privacy.disable_cortana()
    privacy.disable_advertising_id()
    privacy.disable_location_tracking()

    img.unmount(save_changes=True)

print("🔒 Privacy hardened!")
```

---

## Common Use Cases

### 1. Create a Gaming PC Image (10 minutes)

```bash
# Using GUI
deployforge gui
# Select Gaming profile → Build

# Using CLI with example
python examples/gaming_pc_build.py \
    --source install.wim \
    --output Win11_Gaming.wim
```

**What it does:**
- Removes Xbox, Teams, OneDrive, Cortana
- Installs GPU drivers (NVIDIA/AMD)
- Enables Game Mode and optimizations
- Installs DirectX, Visual C++ runtimes
- Sets Ultimate Performance power plan
- Optimizes services for gaming

### 2. Create a Privacy-Focused Image (15 minutes)

```bash
# Using GUI
deployforge gui
# Select features: Privacy (all), Debloat (aggressive) → Build

# Using Python
python -c "
from pathlib import Path
from deployforge import ImageManager
from deployforge.privacy_hardening import PrivacyManager, PrivacyLevel

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)
    privacy = PrivacyManager(img)
    privacy.apply_level(PrivacyLevel.MAXIMUM)
    img.unmount(save_changes=True)
"
```

**What it does:**
- Disables all telemetry and tracking
- Removes Cortana, Bing, OneDrive
- Disables advertising ID
- Blocks data collection
- Removes Microsoft Edge (optional)

### 3. Create a Developer Workstation (20 minutes)

```bash
# Using GUI
deployforge gui
# Select Developer profile → Build

# Using Python
python -c "
from pathlib import Path
from deployforge import ImageManager
from deployforge.devenv import DevEnvironmentManager, DevProfile

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)
    dev = DevEnvironmentManager(img)
    dev.apply_profile(DevProfile.FULL_STACK)  # Python, Node, Docker, etc.
    img.unmount(save_changes=True)
"
```

**What it does:**
- Installs Python 3.11, Node.js, Git
- Installs VS Code, Visual Studio
- Installs Docker, WSL2, PowerShell 7
- Installs 4 browsers (Chrome, Firefox, Edge, Brave)
- Configures development tools

### 4. Create an Enterprise Secure Image (30 minutes)

```bash
# Using Python example
python examples/enterprise_workstation.py \
    --source install.wim \
    --output Win11_Enterprise_Secure.wim \
    --company "Your Company" \
    --domain "company.local"
```

**What it does:**
- Applies CIS security baseline
- Installs Office 365, Teams
- Configures BitLocker preparation
- Installs root certificates
- Applies Group Policy Objects
- Enables audit logging
- Domain join configuration

---

## Next Steps

### Learn More

- **📖 Full Documentation**: See [README.md](README.md)
- **🎨 GUI Guide**: See [GUI_GUIDE.md](GUI_GUIDE.md)
- **🏢 Enterprise Features**: See [ENTERPRISE_GUIDE.md](ENTERPRISE_GUIDE.md)
- **💡 Examples**: See [EXAMPLES_INDEX.md](EXAMPLES_INDEX.md)
- **🔧 Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **🤖 For AI Assistants**: See [CLAUDE.md](CLAUDE.md)

### Explore Advanced Features

#### Infrastructure as Code (IaC)

Define your builds in YAML:

```yaml
# build.yaml
version: "1.0"
name: "Custom Windows 11 Build"
image: "install.wim"
index: 3
output: "Win11_Custom.wim"

stages:
  - name: base
    profile: gaming
    debloat: [Xbox, Teams, OneDrive]
    privacy: enhanced

  - name: applications
    install:
      - name: "Steam"
      - name: "Discord"
      - name: "OBS Studio"
```

Run with:
```bash
deployforge iac build build.yaml
```

#### Job Scheduling

Schedule automated builds:

```python
from deployforge.scheduler import JobScheduler

scheduler = JobScheduler()

# Schedule nightly build at 2 AM
scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={'profile': 'enterprise'},
    schedule='0 2 * * *',  # Cron syntax
    notify_email='admin@company.com'
)
```

#### Version Control

Track image versions like Git:

```python
from deployforge.versioning import ImageRepository

repo = ImageRepository(Path('/images/repo'))
repo.init()

# Commit image
commit = repo.commit(
    image_path=Path('Win11_Custom.wim'),
    message='Added gaming optimizations',
    version='1.1.0',
    tags=['gaming', 'production']
)

# View history
history = repo.log(limit=10)

# Rollback to previous version
repo.checkout('1.0.0')
```

#### Automated Testing

Test images in VMs before deployment:

```python
from deployforge.testing import VMTester, Hypervisor

# Test boot in VirtualBox
tester = VMTester(
    image_path=Path('Win11_Custom.wim'),
    hypervisor=Hypervisor.VIRTUALBOX
)

result = tester.test_boot(timeout=300)
if result.status == 'PASSED':
    print("✓ Image boots successfully!")
```

---

## Tips for Beginners

### 1. Start Small

Don't try to customize everything at once:
- Start with a simple gaming or privacy profile
- Test the image in a VM
- Add more customizations incrementally

### 2. Always Work on a Copy

```bash
# Make a backup first
cp install.wim install_backup.wim

# Work on the copy
deployforge mount install.wim
```

### 3. Use the GUI First

The Modern GUI is the easiest way to learn:
- Visual feedback
- Clear options
- Progress monitoring
- No coding required

### 4. Read the Logs

When something goes wrong, check the logs:

```bash
# Linux
tail -f ~/.config/DeployForge/logs/deployforge.log

# Windows
type %LOCALAPPDATA%\DeployForge\logs\deployforge.log
```

### 5. Test in a VM

Before deploying to real hardware:
- VirtualBox (free, cross-platform)
- Hyper-V (Windows Pro/Enterprise)
- VMware Workstation/Player

### 6. Join the Community

Get help and share experiences:
- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discord**: https://discord.gg/deployforge
- **Reddit**: r/DeployForge

---

## Common Issues

### "Permission Denied"

**Solution**: Run as Administrator (Windows) or with `sudo` (Linux)

```bash
# Windows: Run PowerShell as Administrator
deployforge gui

# Linux
sudo deployforge gui
```

### "Image Not Found"

**Solution**: Check file path and ensure file exists

```bash
# Verify file exists
ls -lh install.wim  # Linux
dir install.wim     # Windows
```

### "Mount Failed"

**Solution**: Ensure no other process is using the image

```bash
# Check mounted images
deployforge list-mounts

# Force unmount
deployforge unmount install.wim --force
```

### "Out of Disk Space"

**Solution**: Free up space or use a different drive

- Windows images need 10-20GB free space
- Ensure working directory has adequate space

### GUI Won't Start

**Solution**: Install PyQt6

```bash
pip install PyQt6
```

For more troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Quick Command Reference

### Essential Commands

```bash
# Show version
deployforge --version

# Launch GUI
deployforge gui

# Get image info
deployforge info image.wim

# List supported formats
deployforge formats

# Mount image
deployforge mount image.wim --index 3

# Unmount image
deployforge unmount image.wim

# List mounted images
deployforge list-mounts

# Clear cache
deployforge cache clear

# Run diagnostics
deployforge diagnose

# View logs
deployforge logs --tail 50
```

### GUI Keyboard Shortcuts

- **Ctrl+O** - Open image
- **Ctrl+S** - Save configuration
- **Ctrl+B** - Start build
- **F5** - Refresh
- **Ctrl+T** - Toggle theme (Light/Dark)
- **Ctrl+Q** - Quit

---

## Recipes

### Recipe 1: Clean Windows 11 (Minimal Bloat)

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.debloat import DebloatManager

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)

    debloat = DebloatManager(img)
    debloat.remove_default_apps([
        'Microsoft.XboxApp',
        'Microsoft.Teams',
        'Microsoft.OneDrive',
        'Cortana'
    ])

    img.unmount(save_changes=True)
```

### Recipe 2: Gaming PC (Maximum Performance)

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.gaming import GamingOptimizer, GamingProfile

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)
    gaming = GamingOptimizer(img)
    gaming.apply_profile(GamingProfile.EXTREME)
    img.unmount(save_changes=True)
```

### Recipe 3: Privacy-Focused (Maximum Privacy)

```python
from pathlib import Path
from deployforge import ImageManager
from deployforge.privacy_hardening import PrivacyManager, PrivacyLevel

with ImageManager(Path('install.wim')) as img:
    img.mount(index=3)
    privacy = PrivacyManager(img)
    privacy.apply_level(PrivacyLevel.MAXIMUM)
    img.unmount(save_changes=True)
```

---

## Video Tutorials (Coming Soon)

- **Getting Started** (5 min) - Installation and first build
- **GUI Walkthrough** (10 min) - Complete GUI tour
- **Gaming Optimization** (15 min) - Create ultimate gaming image
- **Enterprise Deployment** (20 min) - MDT/SCCM integration
- **Advanced Automation** (25 min) - IaC, scheduling, testing

---

## Getting Help

### Documentation Hierarchy

1. **Quick Start** (you are here) - Get started in 10 minutes
2. **README.md** - Comprehensive project overview
3. **GUI_GUIDE.md** - Complete GUI documentation
4. **ENTERPRISE_GUIDE.md** - Advanced enterprise features
5. **TROUBLESHOOTING.md** - Fix common problems
6. **EXAMPLES_INDEX.md** - Real-world code examples
7. **CLAUDE.md** - For AI assistants and developers

### Support Channels

- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues
- **Discord Community**: https://discord.gg/deployforge
- **Email Support**: support@deployforge.com
- **Enterprise Support**: enterprise-support@deployforge.com

### Before Asking for Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Run: `deployforge diagnose`
3. Check logs: `deployforge logs`
4. Search existing GitHub issues
5. Try with latest version: `pip install --upgrade deployforge`

---

## What's Next?

Now that you've got the basics, explore:

1. **Learn the GUI** - Master the 150+ features ([GUI_GUIDE.md](GUI_GUIDE.md))
2. **Try Examples** - Run real-world examples ([EXAMPLES_INDEX.md](EXAMPLES_INDEX.md))
3. **Explore Enterprise** - MDT, SCCM, IaC, automation ([ENTERPRISE_GUIDE.md](ENTERPRISE_GUIDE.md))
4. **Automate** - Create repeatable workflows
5. **Share** - Contribute examples and improvements

**Happy Deploying! 🚀**

---

## Quick Links

- 📦 **PyPI**: https://pypi.org/project/deployforge/
- 🐙 **GitHub**: https://github.com/Cornman92/DeployForge
- 📖 **Docs**: https://deployforge.readthedocs.io
- 💬 **Discord**: https://discord.gg/deployforge
- 🐦 **Twitter**: @DeployForge

---

**Version**: 1.7.0
**Last Updated**: 2025-11-17

*Need help? Open an issue on GitHub or join our Discord community!*
