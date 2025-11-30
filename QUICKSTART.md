# Quick Start Guide

Get started with DeployForge in 5 minutes! This guide will walk you through creating your first customized Windows deployment image.

## ⏱️ 5-Minute Quick Start

### Prerequisites

- ✅ DeployForge installed ([Installation Guide](INSTALLATION.md))
- ✅ Windows installation image (install.wim or install.esd)
- ✅ 10-20 GB free disk space
- ✅ Administrator/sudo privileges (Windows/Linux)

**Don't have a Windows image?** Download Windows 11 from [Microsoft](https://www.microsoft.com/software-download/windows11) and extract `install.wim` from the `sources/` folder.

---

## 🚀 Method 1: GUI (Easiest)

The fastest way to get started is with the modern GUI.

### Step 1: Launch GUI

```bash
# Windows
deployforge gui

# Linux/macOS (may need sudo)
sudo deployforge gui
```

### Step 2: Load Your Image

**Option A: Drag & Drop**
- Drag your `.wim`, `.esd`, or `.iso` file onto the window

**Option B: File Picker**
- Click "Browse" button
- Navigate to your Windows image
- Select `install.wim` (usually in `sources/` folder)

### Step 3: Choose a Profile

Select one of 6 pre-configured profiles:

- **🎮 Gaming**: Optimized for gaming PCs (27 features auto-selected)
- **💻 Developer**: Perfect for developers (28 features auto-selected)
- **🏢 Enterprise**: Security-hardened for business (24 features)
- **🎓 Student**: Productivity-focused (23 features)
- **🎨 Creator**: For content creation (27 features)
- **⚙️ Custom**: Pick your own features

### Step 4: Customize (Optional)

Expand "Advanced Options" to fine-tune:
- 150+ customization features
- 16 feature categories
- 40+ application installers

### Step 5: Build!

1. Click "Build Image"
2. Choose output location
3. Watch real-time progress
4. Done! 🎉

Your customized Windows image is ready for deployment.

---

## 💻 Method 2: CLI (Quick & Scriptable)

For automation and scripting, use the command-line interface.

### Example 1: Gaming PC Build

```bash
# Create a gaming-optimized Windows 11 image
deployforge build \
  --input install.wim \
  --output gaming-win11.wim \
  --profile gaming \
  --index 1
```

**What this does:**
- ✅ Optimizes for gaming performance
- ✅ Installs Steam, Epic Games, GOG
- ✅ Configures NVIDIA/AMD drivers
- ✅ Enables Game Mode and GPU scheduling
- ✅ Applies Ultimate Performance power plan
- ✅ Moderate debloating for space

### Example 2: Developer Workstation

```bash
deployforge build \
  --input install.wim \
  --output dev-win11.wim \
  --profile developer \
  --features "wsl2,docker,vscode,git,python,nodejs"
```

**What this does:**
- ✅ Installs WSL2, Docker, Hyper-V
- ✅ Adds VS Code, Git, Python, Node.js
- ✅ Configures 4 browsers for testing
- ✅ Includes PowerShell 7, Windows Terminal
- ✅ Minimal debloating (keeps dev tools)

### Example 3: Enterprise Hardened

```bash
deployforge build \
  --input install.wim \
  --output enterprise-win11.wim \
  --profile enterprise \
  --features "bitlocker,cis-benchmark,domain-prep"
```

**What this does:**
- ✅ Enables BitLocker encryption
- ✅ Applies CIS Benchmark hardening
- ✅ Configures DISA STIG compliance
- ✅ Prepares for domain join
- ✅ Installs Office, Teams, Adobe Reader

---

## 📝 Method 3: Python API (Advanced)

For custom workflows and integration.

### Example 1: Basic Image Customization

```python
from deployforge import ImageManager
from pathlib import Path

# Load the image
with ImageManager(Path('install.wim')) as manager:
    # Mount the image
    manager.mount()

    # Apply gaming optimizations
    from deployforge.gaming import GamingOptimizer
    gaming = GamingOptimizer(Path('install.wim'))
    gaming.apply_profile('competitive')

    # Apply debloating
    from deployforge.debloat import DebloatManager
    debloat = DebloatManager(Path('install.wim'))
    debloat.apply_level('moderate')

    # Save changes
    manager.unmount(save_changes=True)

print("✅ Image customized successfully!")
```

### Example 2: Batch Processing

```python
from deployforge.batch import BatchOperation
from pathlib import Path

# Process multiple images
images = [
    Path('win11-home.wim'),
    Path('win11-pro.wim'),
    Path('win11-enterprise.wim')
]

batch = BatchOperation()
for image in images:
    batch.add_operation(
        image_path=image,
        profile='gaming',
        output_path=image.with_suffix('.customized.wim')
    )

# Execute all operations in parallel
batch.execute(parallel=True)
```

---

## 🎯 Common Use Cases

### Use Case 1: Clean Windows Install

**Goal**: Remove bloatware, keep essentials

```bash
deployforge build \
  --input install.wim \
  --output clean-windows.wim \
  --debloat moderate \
  --features "-cortana,-bing,-onedrive,-3d-objects"
```

**Result**: ~2-3 GB smaller, faster boot time

### Use Case 2: Gaming Cafe Build

**Goal**: Multiple gaming platforms, performance-optimized

```bash
deployforge build \
  --input install.wim \
  --output gaming-cafe.wim \
  --profile gaming \
  --features "steam,epic,gog,origin,ubisoft,battlenet,discord" \
  --power-plan ultimate \
  --debloat aggressive
```

**Result**: Ready-to-game image with all major platforms

### Use Case 3: Developer Team Image

**Goal**: Standardized development environment

```bash
deployforge build \
  --input install.wim \
  --output dev-team.wim \
  --profile developer \
  --features "python,nodejs,java,dotnet,docker,git,vscode" \
  --browsers "firefox,chrome,edge,brave"
```

**Result**: Consistent dev environment across team

### Use Case 4: Privacy-Focused Build

**Goal**: Maximum privacy, minimal telemetry

```bash
deployforge build \
  --input install.wim \
  --output private-windows.wim \
  --privacy-level maximum \
  --debloat aggressive \
  --features "-telemetry,-cortana,-bing,-location,-advertising"
```

**Result**: Privacy-hardened Windows installation

---

## 📚 Next Steps

### Learn More Features

1. **Browse Examples**: Check `examples/` directory for real-world scenarios
2. **Read Documentation**: [README.md](README.md) has complete feature list
3. **Watch Tutorials**: Video guides (coming soon)

### Common Customizations

#### Add/Remove Features

```bash
# Add specific features
deployforge build --input image.wim --features "+docker,+vscode,+python"

# Remove features
deployforge build --input image.wim --features "-cortana,-onedrive"
```

#### Change Power Plan

```bash
# Set power plan
deployforge build --input image.wim --power-plan ultimate  # or high, balanced
```

#### Configure Network

```bash
# Set DNS and network options
deployforge build --input image.wim --dns cloudflare  # or google, quad9
```

#### Install Applications

```bash
# Install specific apps
deployforge build --input image.wim --install "7zip,firefox,vlc,vscode"
```

---

## 🔍 Verify Your Build

After building, verify the image:

```bash
# Check image info
deployforge info customized-image.wim

# List files in image
deployforge list customized-image.wim

# Compare with original
deployforge compare original.wim customized-image.wim
```

---

## 📦 Deploy Your Image

### Method 1: USB Boot Drive

```bash
# 1. Create bootable USB with Rufus, Ventoy, or similar
# 2. Replace install.wim in sources/ folder with your customized image
# 3. Boot from USB and install
```

### Method 2: Network Deployment (WDS/MDT)

```bash
# 1. Import customized image into WDS/MDT
# 2. Create deployment task sequence
# 3. Deploy to target machines
```

### Method 3: Virtual Machine

```bash
# 1. Create new VM in VMware/VirtualBox/Hyper-V
# 2. Mount your customized WIM as installation source
# 3. Install Windows from customized image
```

---

## ⚠️ Important Notes

### Before Building

1. **Backup**: Always keep a backup of the original image
2. **Test**: Test customized images in a VM before production deployment
3. **Licensing**: Ensure you have proper Windows licensing
4. **Space**: Ensure adequate disk space (2x image size recommended)

### During Building

1. **Don't Interrupt**: Let the build process complete
2. **Admin Rights**: Run with administrator/sudo privileges
3. **Disk Space**: Monitor available space during build
4. **Logs**: Check logs if something goes wrong

### After Building

1. **Verify**: Use `deployforge info` to verify image integrity
2. **Test**: Deploy to a test VM before production
3. **Document**: Keep notes on customizations made
4. **Version**: Tag/version your custom images

---

## 🆘 Troubleshooting

### Build Fails

**Problem**: Build process errors out

**Solutions**:
```bash
# 1. Check logs
deployforge build --verbose --log build.log

# 2. Verify image integrity
deployforge info original-image.wim

# 3. Check disk space
df -h  # Linux/macOS
wmic logicaldisk get size,freespace,caption  # Windows
```

### Permission Denied

**Problem**: Cannot mount/modify image

**Solutions**:
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo
sudo deployforge build --input image.wim
```

### Missing Dependencies

**Problem**: "wimlib not found" or similar

**Solutions**:
```bash
# Ubuntu/Debian
sudo apt-get install wimtools

# macOS
brew install wimlib

# Or see INSTALLATION.md
```

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [ask a question](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml).

---

## 🎓 Learning Resources

### Documentation

- **Full Documentation**: [README.md](README.md)
- **Installation**: [INSTALLATION.md](INSTALLATION.md)
- **FAQ**: [FAQ.md](FAQ.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

### Examples

Browse real-world examples in the `examples/` directory:

- `examples/gaming_pc_build.py` - Gaming optimization
- `examples/enterprise_workstation.py` - Enterprise hardening
- `examples/developer_setup.py` - Developer environment
- `examples/privacy_focused.py` - Privacy customization

### Community

- **GitHub Discussions**: Ask questions, share builds
- **Issue Tracker**: Report bugs, request features
- **Contributing**: Help improve DeployForge

---

## ✅ Quick Reference Card

```bash
# ESSENTIAL COMMANDS

# Launch GUI
deployforge gui

# Build with profile
deployforge build --input image.wim --output custom.wim --profile gaming

# List supported formats
deployforge formats

# Get image info
deployforge info image.wim

# List files in image
deployforge list image.wim

# Compare images
deployforge compare image1.wim image2.wim

# Show help
deployforge --help
```

---

## 🚀 You're Ready!

You now know how to:
- ✅ Load and customize Windows images
- ✅ Use profiles for quick setup
- ✅ Build custom images via GUI and CLI
- ✅ Deploy your customized images
- ✅ Troubleshoot common issues

**Start customizing your Windows images with DeployForge!**

Need more help? Check [README.md](README.md) or [open an issue](https://github.com/Cornman92/DeployForge/issues/new).

---

**Happy Building! 🎉**
