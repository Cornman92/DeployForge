# Troubleshooting Guide

Solutions to common issues when using DeployForge.

## 📋 Table of Contents

- [Installation Issues](#installation-issues)
- [Image Operations](#image-operations)
- [GUI Problems](#gui-problems)
- [Performance Issues](#performance-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### Python Not Found

**Problem**: `python: command not found` or `python3: command not found`

**Symptoms**:
```bash
$ python --version
bash: python: command not found
```

**Solutions**:

1. **Install Python**:
   ```bash
   # Windows: Download from https://www.python.org/downloads/
   # Ubuntu/Debian:
   sudo apt-get install python3 python3-pip
   # macOS:
   brew install python@3.11
   ```

2. **Try python3 instead**:
   ```bash
   python3 --version
   ```

3. **Add Python to PATH** (Windows):
   - Search "Environment Variables" in Start Menu
   - Edit PATH variable
   - Add Python installation directory

---

### Pip Installation Fails

**Problem**: `pip install deployforge` fails with errors

**Common Errors & Solutions**:

#### Error: "No matching distribution found"

```bash
# Update pip first
python -m pip install --upgrade pip

# Try again
pip install deployforge
```

#### Error: "Could not build wheels for PyQt6"

```bash
# Install system dependencies first

# Ubuntu/Debian:
sudo apt-get install python3-pyqt6 python3-dev

# macOS:
brew install pyqt6

# Or install without GUI dependencies:
pip install deployforge --no-deps
pip install click rich pyyaml pycdlib xmltodict
```

#### Error: "Permission denied"

```bash
# Use --user flag
pip install --user deployforge

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install deployforge
```

---

### wimlib/DISM Not Found

**Problem**: `wimlib-imagex: command not found` or DISM errors

**Platform Solutions**:

#### Windows (DISM)

DISM is built-in, but ensure it's accessible:

```powershell
# Check if DISM is available
dism /?

# If not found, repair Windows or reinstall
```

#### Linux (wimlib)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wimtools

# RHEL/CentOS/Fedora
sudo dnf install wimlib-utils

# Arch
sudo pacman -S wimlib

# Verify installation
wimlib-imagex --version
```

#### macOS (wimlib)

```bash
# Install via Homebrew
brew install wimlib

# Verify installation
wimlib-imagex --version
```

---

## Image Operations

### Permission Denied When Mounting

**Problem**: Cannot mount images due to permissions

**Symptoms**:
```
Error: Permission denied mounting image
Mount operation failed
```

**Solutions**:

1. **Windows**: Run as Administrator
   ```powershell
   # Right-click PowerShell → "Run as Administrator"
   deployforge gui
   ```

2. **Linux/macOS**: Use sudo
   ```bash
   sudo deployforge gui
   ```

3. **Linux**: Add user to fuse group
   ```bash
   sudo usermod -a -G fuse $USER
   # Log out and back in
   ```

---

### Image Corruption

**Problem**: Image becomes corrupted during operations

**Symptoms**:
```
Error: Invalid image file
Image verification failed
Checksum mismatch
```

**Solutions**:

1. **Verify original image**:
   ```bash
   deployforge info original-image.wim
   ```

2. **Check disk space**:
   ```bash
   # Linux/macOS
   df -h

   # Windows
   wmic logicaldisk get size,freespace,caption
   ```

3. **Restore from backup**:
   - Always keep backups of original images
   - Never modify original without backup

4. **Check for disk errors**:
   ```bash
   # Windows
   chkdsk /f C:

   # Linux
   sudo fsck /dev/sdX
   ```

---

### Mount Point Already in Use

**Problem**: Cannot mount because mount point exists

**Symptoms**:
```
Error: Mount point already in use
Directory not empty
```

**Solutions**:

1. **Unmount existing image**:
   ```bash
   deployforge unmount /path/to/mountpoint
   ```

2. **Check what's mounted**:
   ```bash
   # Windows
   dism /Get-MountedImageInfo

   # Linux
   mount | grep wim
   ```

3. **Force cleanup**:
   ```bash
   # Windows
   dism /Cleanup-Mountpoints

   # Linux
   sudo umount -f /mountpoint
   ```

---

### Out of Disk Space

**Problem**: Build fails due to insufficient space

**Symptoms**:
```
Error: No space left on device
Write operation failed
```

**Solutions**:

1. **Check available space**:
   ```bash
   # Need at least 2x image size
   # Typical: 20-50 GB for Windows images
   ```

2. **Clean temporary files**:
   ```bash
   # Windows
   cleanmgr

   # Linux
   sudo apt-get clean
   sudo apt-get autoclean

   # Clear DeployForge temp files
   rm -rf /tmp/deployforge_*
   ```

3. **Use different output location**:
   ```bash
   deployforge build --input image.wim \
     --output /large-disk/custom.wim
   ```

---

## GUI Problems

### GUI Won't Launch

**Problem**: GUI fails to start

**Symptoms**:
```
ImportError: No module named 'PyQt6'
QApplication: invalid style override
Display not available
```

**Solutions**:

1. **PyQt6 not installed**:
   ```bash
   pip install PyQt6
   ```

2. **Missing display (Linux)**:
   ```bash
   # If running via SSH, enable X11 forwarding
   ssh -X user@host

   # Or set DISPLAY variable
   export DISPLAY=:0
   ```

3. **Wayland issues (Linux)**:
   ```bash
   # Force X11 backend
   export QT_QPA_PLATFORM=xcb
   deployforge gui
   ```

4. **macOS permissions**:
   - System Preferences → Security & Privacy
   - Grant terminal app necessary permissions

---

### GUI Crashes or Freezes

**Problem**: GUI becomes unresponsive

**Solutions**:

1. **Check logs**:
   ```bash
   # Logs are typically in:
   # Windows: %APPDATA%\deployforge\logs
   # Linux: ~/.config/deployforge/logs
   # macOS: ~/Library/Logs/deployforge
   ```

2. **Run with verbose output**:
   ```bash
   deployforge gui --verbose
   ```

3. **Reset settings**:
   ```bash
   # Delete config file
   # Windows: %APPDATA%\deployforge\config.yaml
   # Linux: ~/.config/deployforge/config.yaml
   # macOS: ~/Library/Application Support/deployforge/config.yaml
   ```

4. **Update Qt**:
   ```bash
   pip install --upgrade PyQt6
   ```

---

### Theme/Display Issues

**Problem**: GUI looks broken or has visual glitches

**Solutions**:

1. **Switch theme**:
   - Settings → Theme → Try Light/Dark

2. **Reset to defaults**:
   - Settings → Reset to Defaults

3. **Check graphics drivers** (Windows):
   - Update GPU drivers from manufacturer

4. **Disable hardware acceleration**:
   ```bash
   export QT_XCB_GL_INTEGRATION=none  # Linux
   deployforge gui
   ```

---

## Performance Issues

### Slow Image Operations

**Problem**: Operations take too long

**Causes & Solutions**:

1. **Large images** (>10 GB):
   - Normal behavior, WIM operations are disk-intensive
   - Use SSD if possible
   - Consider parallel operations for multiple images

2. **Antivirus scanning**:
   - Temporarily disable real-time scanning
   - Add DeployForge to exclusions

3. **Low memory**:
   ```bash
   # Close other applications
   # Ensure 8 GB+ RAM available
   ```

4. **Network storage**:
   - Copy images to local disk first
   - Network I/O is slower than local

---

### High Memory Usage

**Problem**: DeployForge uses too much RAM

**Solutions**:

1. **Normal for large images**:
   - WIM operations require memory
   - 4-8 GB usage is normal

2. **Limit parallel operations**:
   ```bash
   # Reduce worker threads
   deployforge batch --workers 2  # instead of default 4
   ```

3. **Process images sequentially**:
   ```bash
   # Don't use --parallel for batch operations
   deployforge batch --no-parallel
   ```

---

### CPU Usage Too High

**Problem**: 100% CPU usage during operations

**Solutions**:

1. **Expected during builds**:
   - Image compression is CPU-intensive
   - Normal to see high CPU usage

2. **Limit CPU cores**:
   ```bash
   # Linux: Use taskset
   taskset -c 0-3 deployforge build ...

   # Windows: Use Process Priority
   # Task Manager → Details → Set Priority to "Below Normal"
   ```

---

## Platform-Specific Issues

### Windows Issues

#### UAC Prompts

**Problem**: Constant UAC prompts

**Solution**:
```powershell
# Run PowerShell as Administrator once
# Right-click PowerShell → "Run as Administrator"
```

#### Long Path Names

**Problem**: Error with long file paths

**Solution**:
```powershell
# Enable long path support
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

#### Windows Defender

**Problem**: Defender quarantines files

**Solution**:
- Add DeployForge directory to exclusions
- Windows Security → Virus & Threat Protection → Exclusions

---

### Linux Issues

#### fuse Not Available

**Problem**: FUSE filesystem errors

**Solution**:
```bash
# Install FUSE
sudo apt-get install fuse  # Ubuntu/Debian
sudo dnf install fuse      # RHEL/Fedora

# Load kernel module
sudo modprobe fuse

# Add user to fuse group
sudo usermod -a -G fuse $USER
```

#### SELinux Blocks Operations

**Problem**: SELinux denies operations

**Solution**:
```bash
# Temporarily disable (not recommended for production)
sudo setenforce 0

# Or add SELinux policy
sudo ausearch -m avc -ts recent
# Create policy based on denials
```

---

### macOS Issues

#### Gatekeeper Blocks Execution

**Problem**: "Cannot verify developer"

**Solution**:
```bash
# Allow app in Security & Privacy
# System Preferences → Security & Privacy → Allow
```

#### SIP (System Integrity Protection)

**Problem**: Operations blocked by SIP

**Solution**:
- SIP should not affect DeployForge
- If needed, operations can be done in user space
- Do NOT disable SIP unless absolutely necessary

---

## Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Review logs** for error messages
3. **Search existing issues** on GitHub
4. **Try with --verbose** flag for detailed output

### How to Get Help

1. **GitHub Issues** (bugs): [Create Bug Report](https://github.com/Cornman92/DeployForge/issues/new?template=bug_report.yml)

2. **GitHub Discussions** (questions): [Ask Question](https://github.com/Cornman92/DeployForge/discussions)

3. **Question Template**: [Submit Question](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml)

### Information to Include

When asking for help, provide:

1. **DeployForge version**:
   ```bash
   deployforge --version
   ```

2. **Operating system**:
   ```bash
   # Linux
   uname -a

   # macOS
   sw_vers

   # Windows
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
   ```

3. **Python version**:
   ```bash
   python --version
   ```

4. **Error messages**:
   - Full error output
   - Stack trace if available

5. **Steps to reproduce**:
   - Exact commands used
   - Image format and size
   - What you expected vs what happened

6. **Logs** (if applicable):
   ```bash
   # Run with verbose logging
   deployforge --verbose --log debug.log [command]
   ```

---

## Common Error Messages

### "Image format not supported"

**Cause**: Trying to use unsupported image format

**Solution**:
```bash
# Check supported formats
deployforge formats

# Supported: ISO, WIM, ESD, PPKG, VHD, VHDX
```

### "Index not found in image"

**Cause**: Specified index doesn't exist

**Solution**:
```bash
# List available indexes
deployforge info image.wim

# Use correct index (usually 1 for install.wim)
deployforge build --index 1 ...
```

### "Registry hive not found"

**Cause**: Cannot locate Windows registry in image

**Solution**:
- Ensure you're using a valid Windows image
- Check that image is properly mounted
- Verify image is not corrupted

### "Operation requires elevated privileges"

**Cause**: Need admin/sudo access

**Solution**:
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo
sudo deployforge [command]
```

---

## Diagnostic Commands

### Check Installation

```bash
# Verify DeployForge is installed
deployforge --version

# Check Python
python --version

# Check pip packages
pip list | grep deployforge

# Verify dependencies
deployforge formats
```

### Check System Resources

```bash
# Disk space
df -h  # Linux/macOS
wmic logicaldisk get size,freespace,caption  # Windows

# Memory
free -h  # Linux
vm_stat  # macOS
systeminfo | findstr /C:"Available Physical Memory"  # Windows

# CPU
lscpu  # Linux
sysctl -n machdep.cpu.brand_string  # macOS
wmic cpu get name  # Windows
```

### Check Logs

```bash
# Enable verbose output
deployforge --verbose [command]

# Save logs to file
deployforge --log debug.log [command]

# View recent logs (Linux/macOS)
tail -f ~/.config/deployforge/logs/deployforge.log
```

---

## Still Having Issues?

If none of these solutions work:

1. **Create detailed bug report**: [Bug Report Template](https://github.com/Cornman92/DeployForge/issues/new?template=bug_report.yml)

2. **Join community discussion**: [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions)

3. **Check documentation**:
   - [README.md](README.md)
   - [INSTALLATION.md](INSTALLATION.md)
   - [FAQ.md](FAQ.md)

4. **Review examples**: `examples/` directory for working code

---

## Additional Resources

- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **FAQ**: [FAQ.md](FAQ.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)

---

**Most issues can be resolved quickly!** If you find a solution not listed here, please [contribute](CONTRIBUTING.md) to help others. 🙏
