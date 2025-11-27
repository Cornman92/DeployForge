# Installation Guide

Complete installation instructions for DeployForge on all supported platforms.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Windows Installation](#windows-installation)
- [Linux Installation](#linux-installation)
- [macOS Installation](#macOS-installation)
- [Docker Installation](#docker-installation)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

---

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 2 GB for DeployForge + space for Windows images (10-50 GB)
- **Operating System**:
  - Windows 10/11 (64-bit)
  - Linux (Ubuntu 20.04+, RHEL 8+, or equivalent)
  - macOS 11+ (Big Sur or later)

### Platform-Specific Requirements

#### Windows
- **DISM** (Deployment Image Servicing and Management) - Built-in
- **Administrator privileges** for mounting/modifying images
- **PowerShell 5.1** or higher (built-in)

#### Linux
- **wimlib-imagex** for WIM/ESD support
- **sudo access** for mounting operations
- **fuse** for mounting support

#### macOS
- **wimlib** for WIM/ESD support (via Homebrew)
- **sudo access** for mounting operations

---

## Windows Installation

### Method 1: Pip Install (Recommended)

```powershell
# 1. Ensure Python 3.9+ is installed
python --version

# 2. Create a virtual environment (recommended)
python -m venv deployforge-env
deployforge-env\Scripts\activate

# 3. Install DeployForge
pip install deployforge

# 4. Verify installation
deployforge --version
```

### Method 2: From Source

```powershell
# 1. Clone the repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Verify installation
python -m deployforge --version
```

### Method 3: Windows Installer (Coming Soon)

Download the `.msi` installer from the [Releases](https://github.com/Cornman92/DeployForge/releases) page.

### Method 4: Chocolatey (Coming Soon)

```powershell
choco install deployforge
```

### Method 5: WinGet (Coming Soon)

```powershell
winget install DeployForge
```

### Windows Post-Installation

1. **Verify DISM is available**:
   ```powershell
   dism /?
   ```

2. **Run as Administrator** when modifying images:
   ```powershell
   # Right-click PowerShell → "Run as Administrator"
   deployforge gui
   ```

3. **Optional: Add to PATH**:
   The installer should add DeployForge to your PATH automatically.

---

## Linux Installation

### Ubuntu/Debian

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv wimtools fuse

# 2. Create virtual environment
python3 -m venv deployforge-env
source deployforge-env/bin/activate

# 3. Install DeployForge
pip install deployforge

# 4. Verify installation
deployforge --version
```

### RHEL/CentOS/Fedora

```bash
# 1. Install system dependencies
sudo dnf install -y python3 python3-pip wimlib-utils fuse

# Or for CentOS/RHEL 8:
# sudo yum install -y python3 python3-pip wimlib-utils fuse

# 2. Create virtual environment
python3 -m venv deployforge-env
source deployforge-env/bin/activate

# 3. Install DeployForge
pip install deployforge

# 4. Verify installation
deployforge --version
```

### Arch Linux

```bash
# 1. Install system dependencies
sudo pacman -S python python-pip wimlib fuse2

# 2. Create virtual environment
python -m venv deployforge-env
source deployforge-env/bin/activate

# 3. Install DeployForge
pip install deployforge

# 4. Verify installation
deployforge --version
```

### From Source (Any Linux Distribution)

```bash
# 1. Install wimlib (if not available via package manager)
# Download from https://wimlib.net/downloads/

# 2. Clone repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -e ".[dev]"

# 5. Verify installation
python -m deployforge --version
```

### Linux Post-Installation

1. **Verify wimlib is installed**:
   ```bash
   wimlib-imagex --version
   ```

2. **Add user to fuse group** (optional, for mounting without sudo):
   ```bash
   sudo usermod -a -G fuse $USER
   # Log out and back in for changes to take effect
   ```

3. **Test basic functionality**:
   ```bash
   deployforge formats
   ```

---

## macOS Installation

### Using Homebrew (Recommended)

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install wimlib
brew install wimlib

# 3. Install Python 3.9+ (if needed)
brew install python@3.11

# 4. Create virtual environment
python3 -m venv deployforge-env
source deployforge-env/bin/activate

# 5. Install DeployForge
pip install deployforge

# 6. Verify installation
deployforge --version
```

### From Source

```bash
# 1. Ensure wimlib is installed
brew install wimlib

# 2. Clone repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -e ".[dev]"

# 5. Verify installation
python -m deployforge --version
```

### macOS Post-Installation

1. **Verify wimlib**:
   ```bash
   wimlib-imagex --version
   ```

2. **Grant necessary permissions**:
   - System Preferences → Security & Privacy → Full Disk Access
   - Add Terminal or your preferred terminal emulator

---

## Docker Installation

Run DeployForge in a containerized environment:

```bash
# 1. Pull the Docker image (when available)
docker pull deployforge/deployforge:latest

# 2. Run DeployForge
docker run -it --rm \
  -v /path/to/images:/images \
  -v /path/to/output:/output \
  deployforge/deployforge:latest

# 3. Run with GUI (X11 forwarding)
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /path/to/images:/images \
  deployforge/deployforge:latest gui
```

### Building from Source

```bash
# 1. Clone repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# 2. Build Docker image
docker build -t deployforge:local .

# 3. Run container
docker run -it --rm deployforge:local
```

---

## Development Installation

For contributors and developers:

### Prerequisites

- Git
- Python 3.9+
- Text editor or IDE (VS Code recommended)

### Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/DeployForge.git
cd DeployForge

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# 3. Install in development mode with all dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install

# 5. Verify development setup
pytest
black src/deployforge --check
flake8 src/deployforge
mypy src/deployforge
```

### Development Tools

The development installation includes:

- **pytest** - Testing framework
- **pytest-cov** - Code coverage
- **black** - Code formatter
- **flake8** - Linter
- **mypy** - Type checker
- **bandit** - Security scanner
- **sphinx** - Documentation generator

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=deployforge --cov-report=html

# Run specific test file
pytest tests/test_image_manager.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code
black src/deployforge

# Check formatting
black src/deployforge --check

# Lint code
flake8 src/deployforge

# Type check
mypy src/deployforge --ignore-missing-imports

# Security scan
bandit -r src/deployforge
```

---

## Troubleshooting

### Python Version Issues

**Problem**: `python: command not found`

**Solution**:
```bash
# Try python3 instead
python3 --version

# Or install Python from https://www.python.org/downloads/
```

### Permission Errors

**Problem**: `Permission denied when mounting image`

**Solution**:
- **Windows**: Run PowerShell as Administrator
- **Linux/macOS**: Use `sudo` or add user to appropriate group

### wimlib Not Found (Linux/macOS)

**Problem**: `wimlib-imagex: command not found`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install wimtools

# RHEL/CentOS/Fedora
sudo dnf install wimlib-utils

# macOS
brew install wimlib
```

### PyQt6 Installation Issues

**Problem**: PyQt6 fails to install

**Solution**:
```bash
# Install system dependencies first

# Ubuntu/Debian
sudo apt-get install python3-pyqt6

# Or try installing without GUI
pip install deployforge --no-deps
pip install click rich pyyaml pycdlib xmltodict fastapi uvicorn pydantic psutil requests
```

### Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'deployforge'`

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Reinstall if needed
pip install --upgrade --force-reinstall deployforge
```

### Virtual Environment Issues

**Problem**: Virtual environment activation fails

**Solution**:
```bash
# Delete old environment
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Create new environment
python -m venv venv
```

For more troubleshooting help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or [open an issue](https://github.com/Cornman92/DeployForge/issues/new?template=question.yml).

---

## Verification

After installation, verify everything works:

```bash
# 1. Check version
deployforge --version

# 2. List supported formats
deployforge formats

# 3. Launch GUI (if using GUI)
deployforge gui

# 4. Run help
deployforge --help
```

Expected output:
```
DeployForge v0.3.0
Enterprise Windows Deployment Suite
```

---

## Next Steps

Now that DeployForge is installed:

1. **Quick Start**: Read [QUICKSTART.md](QUICKSTART.md) for a 5-minute tutorial
2. **Documentation**: See [README.md](README.md) for full feature list
3. **Examples**: Check `examples/` directory for real-world usage
4. **Community**: Join [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions)

### Recommended First Steps

```bash
# 1. Get a Windows image (example: Windows 11 ISO)
# Download from Microsoft: https://www.microsoft.com/software-download/windows11

# 2. Extract install.wim from ISO
# The install.wim file is usually in the sources/ directory

# 3. Try the Quick Start guide
# See QUICKSTART.md for a guided walkthrough
```

---

## Updating DeployForge

### Pip Installation

```bash
pip install --upgrade deployforge
```

### From Source

```bash
cd DeployForge
git pull origin main
pip install -e ".[dev]"
```

### Check for Updates

```bash
pip list --outdated | grep deployforge
```

---

## Uninstallation

### Pip Installation

```bash
pip uninstall deployforge
```

### Complete Cleanup

```bash
# Uninstall package
pip uninstall deployforge

# Remove virtual environment
rm -rf deployforge-env  # Linux/macOS
rmdir /s deployforge-env  # Windows

# Remove cloned repository (if applicable)
rm -rf DeployForge
```

---

## Additional Resources

- **Main Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)
- **FAQ**: [FAQ.md](FAQ.md)
- **Security**: [SECURITY.md](SECURITY.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/Cornman92/DeployForge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions)
- **Documentation**: [README.md](README.md)

---

**Installation successful?** Proceed to [QUICKSTART.md](QUICKSTART.md) to build your first custom Windows image! 🚀
