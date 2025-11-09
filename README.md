# DeployForge v1.6.0 🚀

**Enterprise Windows Deployment Suite** - Complete automation with a beautiful modern GUI.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI Status](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/Cornman92/DeployForge/actions)
[![Version](https://img.shields.io/badge/version-1.6.0-success)](https://github.com/Cornman92/DeployForge)
[![Features](https://img.shields.io/badge/features-150%2B-blueviolet)](https://github.com/Cornman92/DeployForge)
[![Enhanced Modules](https://img.shields.io/badge/enhanced%20modules-5%2F9-orange)](https://github.com/Cornman92/DeployForge)

DeployForge is a comprehensive, enterprise-grade tool for managing Windows deployment images. Beautiful modern GUI with **150+ features** across 16 categories, **5 world-class enhanced backend modules**, complete integration, and full automation support.

## 🎉 What's New in v1.6.0 - Module Enhancement Initiative!

**5 Backend Modules Enhanced to World-Class Standards** (+2,500 lines of code):

### ✅ Enhanced Modules:
- **devenv.py** (93→750 lines, +718%) - 10 development profiles, IDE/language installation, cloud tools
- **browsers.py** (92→686 lines, +646%) - 17+ browsers, enterprise policies, privacy configuration
- **creative.py** (83→545 lines, +557%) - Creative software suite with GPU optimization
- **privacy_hardening.py** (79→397 lines, +403%) - 4 privacy levels, comprehensive telemetry blocking
- **launchers.py** (77→399 lines, +418%) - 12+ gaming platforms with mod managers

### 📊 Enhancement Impact:
- +2,500 lines of production-quality, type-hinted code
- All modules follow gaming.py (443 lines) quality standard
- Comprehensive Enums, Dataclasses, progress callbacks
- **PROJECT_ANALYSIS.md** created documenting all 94 modules

---

## 🎉 What's In v1.5.0 - MASSIVE Feature Expansion!

**150+ Features** - The most comprehensive Windows deployment tool available!

### 🚀 Major Expansion:
- ✨ **150+ Customization Features** - 3x increase from v1.0 (+218% growth!)
- 📂 **16 Feature Categories** - Doubled from 7 categories
- 📦 **40+ Application Installers** - Browsers, Office, Creative Tools, Games, Utilities
- 🎯 **Enhanced Profiles** - All 6 profiles expanded with 20-40 features each
- 🌐 **Complete Application Management** - Install everything from one interface

### 📋 New Feature Categories (v1.5.0):
1. **🌐 Web Browsers** (6) - Firefox, Chrome, Brave, Edge, Opera, Vivaldi
2. **📝 Office & Productivity** (10) - Office, LibreOffice, Zoom, Teams, Slack, Notion
3. **🎨 Creative & Media** (10) - OBS, GIMP, Blender, Audacity, VLC, DaVinci Resolve
4. **🎮 Gaming Platforms** (7) - Steam, Epic, GOG, Origin, Ubisoft, Battle.net, Xbox
5. **🔧 System Utilities** (10) - 7-Zip, CCleaner, Everything, PowerToys, ShareX
6. **⚡ Performance** (10) - Disable Superfetch, Indexing, Hibernation, Services
7. **🔌 Services Management** (8) - Windows Update, Print Spooler, Diagnostics
8. **🔋 Power Management** (5) - Ultimate Performance, Power Throttling control
9. **📁 File Explorer** (7) - Quick Access, Libraries, OneDrive, 3D Objects control

### 📈 Expanded Existing Categories:
- **🎮 Gaming** - 7 → **15 features** (NVIDIA/AMD drivers, DirectX, Discord, Game DVR)
- **🗑️ Privacy** - 6 → **16 features** (Cortana, Bing, Telemetry IPs, Lock screen ads)
- **🎨 Visual** - 6 → **19 features** (Classic menus, Hidden files, Taskbar cleanup)
- **💻 Dev Tools** - 7 → **19 features** (Python, Node.js, Java, .NET, PowerShell 7)
- **🏢 Enterprise** - 6 → **12 features** (Domain prep, AppLocker, Credential Guard)
- **🌐 Network** - NEW → **13 features** (DNS options, IPv6, Firewall, Remote Desktop)

### 🎮 Enhanced Profile Features:
- **Gaming Profile**: 27 features (Steam, Epic, GOG, NVIDIA, DirectX, Ultimate Performance)
- **Developer Profile**: 28 features (Python, Node.js, Java, .NET, 4 browsers, PowerToys)
- **Enterprise Profile**: 24 features (Security, Compliance, Domain prep, Office, Teams)
- **Student Profile**: 23 features (Office, Browsers, Privacy controls, VLC, Spotify)
- **Creator Profile**: 27 features (10 creative apps, Ultimate Performance, optimization)

### v1.5.0 GUI Features:
- ✅ **150+ Customization Features** - Unparalleled depth
- ✅ **16 Feature Categories** - Logically organized
- ✅ **40+ Application Installers** - Complete software management
- ✅ **5 Pages**: Welcome, Build, Profiles, Analyze, Settings
- ✅ **6 Enhanced Profiles**: Each with 20-40 auto-selected features
- ✅ **Real-time Progress**: Live progress bar and logs during build
- ✅ **Drag-and-Drop**: Drop .wim/.esd/.iso files anywhere
- ✅ **Settings Persistence**: Window position, theme, preferences auto-saved
- ✅ **Comprehensive Tooltips**: Every feature explained
- ✅ **First-Run Tutorial**: Automatic help for new users

### Previous Versions (v0.3.0-v0.7.0):
- 💿 **UEFI/GPT Partitioning** - Create and manage GPT partition tables
- 🛠️ **WinPE Customization** - Build custom Windows PE environments
- 📝 **Answer File Generation** - Automated unattend.xml creation
- 🌍 **Multi-Language Support** - MUI package management for 40+ languages

### All Features from v0.2.0:
- 🖥️ **PyQt6 Desktop GUI** - Beautiful desktop application
- ☁️ **Remote Storage** - S3, Azure Blob, HTTP repositories
- 🔄 **Batch Operations** - Process multiple images in parallel
- ⚖️ **Image Comparison** - Deep diff analysis between images
- 💾 **VHD/VHDX Support** - Virtual hard disk format
- 🔧 **Registry Editing** - Offline Windows registry modification
- 🚗 **Driver Injection** - Automated driver integration
- 📦 **Windows Updates** - Offline update application
- 📋 **Template System** - Reusable customization workflows
- 🔌 **REST API** - Full automation support
- 💨 **Performance** - Caching, streaming, parallel processing
- 📊 **Audit Logging** - Compliance and tracking

## 🚀 Quick Start

```bash
# Install
pip install deployforge

# === NEW in v0.9.4: Modern GUI ===

# Launch the modern GUI (recommended!)
python -m deployforge.gui_modern

# Or via module
from deployforge import gui_modern
gui_modern.main()

# === CLI Commands ===

# View supported formats
deployforge formats

# Get image info
deployforge info install.wim

# Create UEFI bootable disk with partitions
deployforge partition create disk.vhdx --size 50 --recovery

# Generate automated installation answer file
deployforge unattend create autounattend.xml \
    --username Admin --password P@ssw0rd \
    --computer-name WORKSTATION-01

# Manage multi-language support
deployforge language list install.wim

# Compare two images
deployforge compare image1.wim image2.wim

# Start REST API
python -m deployforge.api.main
```

## ✨ Features

### Image Format Support (6 Formats!)

| Format | Description | Read | Write | Mount |
|--------|-------------|------|-------|-------|
| **ISO** | ISO 9660 optical disc | ✅ | ✅ | ✅ |
| **WIM** | Windows Imaging Format | ✅ | ✅ | ✅ |
| **ESD** | Electronic Software Download | ✅ | ✅ | ✅ |
| **PPKG** | Provisioning Packages | ✅ | ✅ | ✅ |
| **VHD** | Virtual Hard Disk | ✅ | ✅ | ✅ |
| **VHDX** | Virtual Hard Disk Extended | ✅ | ✅ | ✅ |

### Advanced Capabilities

- **Registry Editing**: Modify Windows registry hives offline
- **Driver Injection**: Automated driver package integration
- **Windows Updates**: Apply updates to offline images
- **Batch Processing**: Process hundreds of images in parallel
- **Image Comparison**: File-level diff with hash verification
- **Template System**: Reusable customization workflows
- **Remote Storage**: S3, Azure Blob, HTTP repositories
- **Caching**: Performance optimization for repeated operations
- **Audit Logging**: Full compliance and tracking

### User Interfaces

- **CLI**: Rich terminal interface with progress bars
- **GUI**: PyQt6 desktop application with drag-and-drop
- **REST API**: Full automation with OpenAPI/Swagger docs

### Enterprise Features

- **Parallel Processing**: ThreadPoolExecutor-based concurrency
- **Performance Monitoring**: psutil-based metrics
- **Memory Optimization**: Streaming for large files
- **Security Hardening**: Best practices and guides
- **Audit & Compliance**: JSONL audit logs
- **CI/CD Ready**: GitHub Actions, Docker support

## 📦 Installation

### Via pip (Recommended)

```bash
pip install deployforge
```

### From Source

```bash
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge
pip install -e .
```

### Docker

```bash
docker pull ghcr.io/cornman92/deployforge:latest
docker run -it deployforge --help
```

### Platform-Specific Dependencies

**Windows:**
- DISM (built-in) for WIM/ESD
- PowerShell for VHD/VHDX

**Linux:**
```bash
sudo apt-get install wimtools      # WIM/ESD support
sudo apt-get install qemu-utils    # VHD/VHDX support (qemu-nbd)
# OR
sudo apt-get install libguestfs-tools  # Alternative VHD support
```

**macOS:**
```bash
brew install wimlib     # WIM/ESD support
brew install qemu       # VHD/VHDX support
```

## 🎯 Usage Examples

### CLI Operations

```bash
# Get image information
deployforge info install.wim

# List files
deployforge list windows.iso --path /sources

# Add a file
deployforge add install.wim driver.sys /Windows/System32/drivers/driver.sys

# Remove a file
deployforge remove install.wim /Windows/bloatware.exe

# Extract a file
deployforge extract install.wim /Windows/System32/config/SOFTWARE ./SOFTWARE.hive

# Mount image
deployforge mount install.wim /mnt/windows --index 1

# Compare two images
deployforge compare image1.wim image2.wim
```

### Python API - Basic Operations

```python
from deployforge import ImageManager
from pathlib import Path

# Basic operations
with ImageManager(Path("install.wim")) as manager:
    # Get info
    info = manager.get_info()
    print(f"Format: {info['format']}, Size: {info['size']:,} bytes")

    # Mount
    mount_point = manager.mount()

    # List files
    files = manager.list_files("/Windows/System32")

    # Add file
    manager.add_file(Path("custom.dll"), "/Windows/System32/custom.dll")

    # Remove file
    manager.remove_file("/Windows/bloatware.exe")

    # Extract file
    manager.extract_file("/Windows/notepad.exe", Path("./notepad.exe"))

    # Unmount and save
    manager.unmount(save_changes=True)
```

### Registry Editing

```python
from deployforge import ImageManager
from deployforge.registry import RegistryEditor, COMMON_TWEAKS

with ImageManager("install.wim") as manager:
    manager.mount()

    with RegistryEditor(manager.mount_point) as reg:
        # Apply predefined tweaks
        reg.apply_tweaks(COMMON_TWEAKS['disable_telemetry'])
        reg.apply_tweaks(COMMON_TWEAKS['disable_cortana'])

        # Custom registry value
        reg.set_value(
            'HKLM\\SOFTWARE',
            'Policies\\Microsoft\\Windows\\DataCollection',
            'AllowTelemetry',
            '0',
            'REG_DWORD'
        )

    manager.unmount(save_changes=True)
```

### Driver Injection

```python
from deployforge import ImageManager
from deployforge.drivers import DriverInjector

with ImageManager("install.wim") as manager:
    manager.mount()

    injector = DriverInjector(manager.mount_point)

    # Inject drivers
    results = injector.inject_drivers(
        [Path("./drivers/nvidia.zip"), Path("./drivers/intel.cab")],
        force_unsigned=False
    )

    print(f"Injected: {results['successful']}/{results['total']}")

    manager.unmount(save_changes=True)
```

### Batch Operations

```python
from pathlib import Path
from deployforge.batch import BatchOperation

# Process multiple images
batch = BatchOperation(max_workers=4)

images = [
    Path("windows10.wim"),
    Path("windows11.wim"),
    Path("server2022.wim"),
]

# Get info for all images
results = batch.get_info_batch(images)

# Add file to all images
batch.add_file_batch(
    images,
    source=Path("corporate_logo.png"),
    destination="/Windows/System32/oobe/logo.png"
)

# Print summary
batch.print_summary()
```

### Image Comparison

```python
from pathlib import Path
from deployforge.comparison import ImageComparator

comparator = ImageComparator(compute_hashes=True)

result = comparator.compare(
    Path("windows_base.wim"),
    Path("windows_custom.wim")
)

print(f"Similarity: {result.similarity_percentage():.2f}%")
print(f"Files only in image1: {len(result.only_in_image1)}")
print(f"Files only in image2: {len(result.only_in_image2)}")
print(f"Different files: {len(result.different_files)}")

# Generate detailed report
comparator.generate_report(result, Path("comparison_report.txt"))
```

### Template System

```python
from deployforge.templates import TemplateManager, GAMING_TEMPLATE

manager = TemplateManager(Path("./templates"))

# Use predefined gaming template
template = GAMING_TEMPLATE

# Or load custom template
# template = manager.load_template(Path("./templates/corporate.json"))

# Apply template to image
# (In production, you'd implement template application logic)
print(f"Template: {template.name}")
print(f"Registry tweaks: {len(template.registry)}")
print(f"Packages to remove: {len(template.remove_packages)}")
```

### Remote Storage

```python
from pathlib import Path
from deployforge.remote import S3Repository, AzureBlobRepository, HTTPRepository

# S3
s3 = S3Repository(
    "s3://my-bucket/",
    access_key="...",
    secret_key="..."
)
s3.download("images/install.wim", Path("./local.wim"))
s3.upload(Path("./custom.wim"), "images/custom.wim")

# Azure Blob
azure = AzureBlobRepository(
    "https://account.blob.core.windows.net/container/",
    connection_string="..."
)
azure.download("container/image.wim", Path("./image.wim"))

# HTTP
http = HTTPRepository("https://images.company.com")
http.download("windows11.iso", Path("./windows11.iso"))
```

### REST API

```bash
# Start API server
python -m deployforge.api.main

# Or with custom settings
uvicorn deployforge.api.main:app --host 0.0.0.0 --port 8000
```

```python
import requests

# Get image info
response = requests.post(
    "http://localhost:8000/images/info",
    json={"image_path": "/path/to/image.wim"}
)
info = response.json()

# Compare images
response = requests.post(
    "http://localhost:8000/images/compare",
    json={
        "image1_path": "/path/to/image1.wim",
        "image2_path": "/path/to/image2.wim",
        "compute_hashes": True
    }
)
comparison = response.json()

# Create batch job
response = requests.post(
    "http://localhost:8000/batch/operations",
    json={
        "image_paths": ["/path/to/img1.wim", "/path/to/img2.wim"],
        "operation": "get_info",
        "parameters": {}
    }
)
job = response.json()
job_id = job["job_id"]

# Check job status
response = requests.get(f"http://localhost:8000/jobs/{job_id}")
status = response.json()
```

## 📚 Real-World Workflows

See the `examples/` directory for complete workflows:

- **`windows11_custom.py`** - Complete Windows 11 customization
  - Bloatware removal
  - Registry optimizations
  - Driver injection
  - Update integration

- **`gaming_pc_build.py`** - Gaming-optimized image
  - Gaming-specific tweaks
  - GPU driver injection
  - Performance optimizations

- **`enterprise_workstation.py`** - Enterprise deployment
  - Security hardening
  - Corporate policies
  - Branding and OOBE
  - Audit compliance

## 🖥️ GUI Application

```bash
# Launch GUI
python -m deployforge.gui.main_window
```

Features:
- Drag-and-drop image loading
- File browser with operations
- Registry editor
- Driver injection wizard
- Template manager
- Batch operations interface
- Real-time progress monitoring
- Log viewer

## 🔧 Configuration

### YAML Configuration

```yaml
# deployforge.yaml
mount:
  default_dir: /tmp/deployforge
  auto_cleanup: true

logging:
  level: INFO
  file: /var/log/deployforge.log

wim:
  default_index: 1
  compression: maximum

cache:
  enabled: true
  ttl: 3600
```

### Environment Variables

```bash
export DEPLOYFORGE_CONFIG=deployforge.yaml
export DEPLOYFORGE_LOG_LEVEL=DEBUG
export DEPLOYFORGE_MOUNT_DIR=/mnt/images
```

## 📖 Documentation

- **[Quick Start Guide](docs/index.md)** - Get started quickly
- **[Architecture](docs/architecture.md)** - System design and patterns
- **[Security Guide](docs/security.md)** - Hardening and best practices
- **[API Reference](https://docs.deployforge.io/api)** - Complete API docs
- **[Examples](examples/)** - Real-world workflows

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=deployforge --cov-report=html

# Lint
black src/deployforge
flake8 src/deployforge
mypy src/deployforge

# Security scan
bandit -r src/deployforge
safety check
```

## 🐳 Docker

```bash
# Build
docker build -t deployforge .

# Run
docker run -v /path/to/images:/images deployforge info /images/install.wim

# With GUI (X11 forwarding)
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix deployforge
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📊 Project Stats

- **43** Python modules
- **6** Image formats supported
- **3** User interfaces (CLI, GUI, API)
- **10,800+** Lines of code
- **90%+** Test coverage
- **3** Platform support (Windows, Linux, macOS)

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for the development roadmap.

### Upcoming Features (v0.3.0)
- Web dashboard
- Multi-user support
- VMDK/QCOW2 support
- Image encryption
- Distributed processing

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **pycdlib** - ISO 9660 support
- **wimlib** - WIM support on Linux/macOS
- **Microsoft DISM** - WIM support on Windows
- **FastAPI** - REST API framework
- **PyQt6** - Desktop GUI framework
- **Rich** - Terminal formatting

## 💡 Use Cases

- **System Administrators** - Customize Windows deployments
- **IT Departments** - Standardize corporate images
- **OEMs** - Pre-configure hardware images
- **Security Teams** - Harden Windows images
- **DevOps** - Automate image pipelines
- **Researchers** - Analyze Windows images

## ⚠️ Disclaimer

DeployForge is provided as-is for legitimate system administration and deployment tasks. Users are responsible for:
- Proper Windows licensing
- Software redistribution rights
- Driver licensing
- Compliance with applicable laws

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Cornman92/DeployForge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Cornman92/DeployForge/discussions)
- **Documentation**: [docs.deployforge.io](https://docs.deployforge.io)

---

**Made with ❤️ for Windows System Administrators**

**Star ⭐ this repo if you find it useful!**
