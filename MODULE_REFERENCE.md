# DeployForge Module Reference

**Version**: 1.7.0 / 0.3.0 (Release)
**Last Updated**: 2025-11-15
**Total Modules**: 54
**Total Lines**: 29,163

Complete reference documentation for all Python modules in DeployForge.

---

## Table of Contents

1. [Module Overview](#module-overview)
2. [By Category](#modules-by-category)
3. [By Size](#modules-by-size)
4. [Core Modules](#core-modules) (3)
5. [Format Handlers](#format-handlers) (5)
6. [User Interfaces](#user-interfaces) (4)
7. [Enhanced Modules](#enhanced-modules) (9)
8. [Enterprise Features](#enterprise-features) (8)
9. [Automation & Integration](#automation--integration) (5)
10. [Security & Compliance](#security--compliance) (4)
11. [Customization Features](#customization-features) (6)
12. [Utility Modules](#utility-modules) (10+)

---

## Module Overview

### Statistics by Category

| Category | Modules | Lines | Percentage |
|----------|---------|-------|------------|
| User Interfaces | 4 | 4,433 | 15.2% |
| Enhanced Modules | 9 | 5,185 | 17.8% |
| Enterprise Features | 8 | 5,897 | 20.2% |
| Automation & Integration | 5 | 3,508 | 12.0% |
| Format Handlers | 5 | ~2,500 | 8.6% |
| Customization Features | 6 | 2,868 | 9.8% |
| Core Infrastructure | 3 | ~1,000 | 3.4% |
| Utilities & Tools | 14+ | 3,772+ | 12.9% |
| **Total** | **54** | **29,163** | **100%** |

---

## Modules by Category

### 1. Core Infrastructure (3 modules, ~1,000 lines)

Foundation of the entire system.

- `core/image_manager.py` - Factory and orchestration
- `core/base_handler.py` - Abstract handler interface
- `core/exceptions.py` - Custom exception hierarchy

### 2. Format Handlers (5 modules, ~2,500 lines)

Image format-specific implementations.

- `handlers/iso_handler.py` - ISO 9660 optical disc images
- `handlers/wim_handler.py` - Windows Imaging Format
- `handlers/esd_handler.py` - Electronic Software Download (compressed WIM)
- `handlers/ppkg_handler.py` - Provisioning packages
- `handlers/vhd_handler.py` - Virtual Hard Disk (VHD/VHDX)

### 3. User Interfaces (4 modules, 4,433 lines)

Three separate interface implementations + legacy GUI.

- `gui_modern.py` (3,229) - **PRIMARY INTERFACE** - Modern PyQt6 GUI
- `cli.py` (480) - Command-line interface (Click + Rich)
- `api/main.py` - REST API (FastAPI)
- `gui.py` (491) + `gui/main_window.py` - Legacy GUI

### 4. Enhanced Modules (9 modules, 5,185 lines)

World-class enhanced modules following gaming.py standard.

- `devenv.py` (749) - Development environments
- `browsers.py` (685) - Browser management
- `ui_customization.py` (618) - UI themes
- `backup.py` (650) - Backup/recovery
- `wizard.py` (527) - Setup wizard
- `portable.py` (613) - Portable applications
- `creative.py` (545) - Creative software
- `privacy_hardening.py` (397) - Privacy features
- `launchers.py` (399) - Gaming platforms

### 5. Enterprise Features (8 modules, 5,897 lines)

Advanced enterprise deployment capabilities.

- `testing.py` (823) - Automated testing & validation
- `integration.py` (786) - MDT/SCCM integration
- `iac.py` (770) - Infrastructure as Code
- `partitions.py` (720) - UEFI/GPT partitioning
- `scheduler.py` (716) - Job scheduling
- `versioning.py` (689) - Version control
- `gpo.py` (658) - Group Policy Objects
- `certificates.py` (622) - Certificate management
- `unattend.py` (675) - Answer file generation
- `languages.py` (654) - Multi-language support
- `security.py` (642) - Security hardening
- `winpe.py` (639) - Windows PE customization

### 6. Automation & Integration (5 modules, 3,508 lines)

DevOps and infrastructure automation.

- `automation.py` (677) - Ansible/Terraform integration
- `ai.py` (597) - AI-powered features
- `differential.py` (596) - Differential updates
- `containers.py` (585) - Container support
- `cloud.py` (573) - Cloud deployment

### 7. Customization Features (6 modules, 2,868 lines)

Feature-specific customizations.

- `config_manager.py` (569) - Configuration management
- `encryption.py` (560) - Image encryption
- `applications.py` (525) - Application installation
- `optimizer.py` (482) - General optimization
- `rollback.py` (465) - Rollback capabilities
- `features.py` (444) - Feature management
- `gaming.py` (443) - Gaming optimization (reference)
- `network.py` (440) - Network configuration
- `debloat.py` (419) - Bloatware removal

---

## Modules by Size

### Largest 20 Modules

| Rank | Module | Lines | Category |
|------|--------|-------|----------|
| 1 | gui_modern.py | 3,229 | User Interface |
| 2 | testing.py | 823 | Enterprise |
| 3 | integration.py | 786 | Enterprise |
| 4 | iac.py | 770 | Enterprise |
| 5 | devenv.py | 749 | Enhanced |
| 6 | partitions.py | 720 | Enterprise |
| 7 | scheduler.py | 716 | Enterprise |
| 8 | versioning.py | 689 | Enterprise |
| 9 | browsers.py | 685 | Enhanced |
| 10 | automation.py | 677 | Automation |
| 11 | unattend.py | 675 | Enterprise |
| 12 | gpo.py | 658 | Enterprise |
| 13 | languages.py | 654 | Enterprise |
| 14 | backup.py | 650 | Enhanced |
| 15 | security.py | 642 | Enterprise |
| 16 | winpe.py | 639 | Enterprise |
| 17 | certificates.py | 622 | Enterprise |
| 18 | ui_customization.py | 618 | Enhanced |
| 19 | portable.py | 613 | Enhanced |
| 20 | ai.py | 597 | Automation |

---

## Core Modules

### image_manager.py

**Location**: `src/deployforge/core/image_manager.py`
**Lines**: ~400
**Status**: Production-ready, core architecture
**Stability**: 🔒 Stable - Modify with extreme caution

#### Purpose
Central factory and orchestration for all image operations. Main entry point for the system.

#### Key Components
- `ImageManager` class - Factory pattern implementation
- Handler registry system
- Format detection logic
- Context manager support

#### Key Methods
```python
@classmethod
def register_handler(cls, extension: str, handler_class: type) -> None
    """Register a format handler"""

@classmethod
def get_handler(cls, image_path: Path) -> BaseImageHandler
    """Factory method - returns appropriate handler"""

@classmethod
def supported_formats(cls) -> list
    """List supported image formats"""

def mount(self, mount_point: Optional[Path] = None) -> Path
def unmount(self, save_changes: bool = False) -> None
def list_files(self, path: str = "/") -> list
def add_file(self, source: Path, destination: str) -> None
def remove_file(self, path: str) -> None
def extract_file(self, source: str, destination: Path) -> None
```

#### Usage Example
```python
from deployforge import ImageManager
from pathlib import Path

with ImageManager(Path('install.wim')) as manager:
    manager.mount()
    files = manager.list_files('/Windows')
    manager.add_file(Path('driver.sys'), '/Windows/System32/drivers/')
    manager.unmount(save_changes=True)
```

#### Dependencies
- `base_handler.py` - Handler interface
- `exceptions.py` - Custom exceptions

#### Used By
- All user interfaces (CLI, GUI, API)
- All feature modules
- Batch operations

---

### base_handler.py

**Location**: `src/deployforge/core/base_handler.py`
**Lines**: ~200
**Status**: Production-ready, core architecture
**Stability**: 🔒 Stable - Modify with extreme caution

#### Purpose
Abstract base class defining the interface all image format handlers must implement.

#### Key Components
- `BaseImageHandler` class - ABC with abstract methods
- Common validation logic
- Lifecycle management

#### Abstract Methods
All subclasses must implement:
```python
@abstractmethod
def mount(self, mount_point: Optional[Path] = None) -> Path
    """Mount the image"""

@abstractmethod
def unmount(self, save_changes: bool = False) -> None
    """Unmount the image"""

@abstractmethod
def list_files(self, path: str = "/") -> List[Dict[str, Any]]
    """List files in image"""

@abstractmethod
def add_file(self, source: Path, destination: str) -> None
    """Add file to image"""

@abstractmethod
def remove_file(self, path: str) -> None
    """Remove file from image"""

@abstractmethod
def extract_file(self, source: str, destination: Path) -> None
    """Extract file from image"""

@abstractmethod
def get_info(self) -> Dict[str, Any]
    """Get image information"""
```

#### Template Methods
Common logic provided to all handlers:
- `_validate_image()` - Checks file exists
- Initialization pattern
- State management (`is_mounted`, `mount_point`)

#### When to Extend
Create a new handler subclass when adding support for a new image format.

---

### exceptions.py

**Location**: `src/deployforge/core/exceptions.py`
**Lines**: ~200
**Status**: Production-ready
**Stability**: ⚠️ Extend as needed

#### Purpose
Custom exception hierarchy for DeployForge-specific errors.

#### Exception Hierarchy
```
DeployForgeError (base)
├── ImageNotFoundError
├── UnsupportedFormatError
├── MountError
├── RegistryError
├── DriverInjectionError
├── ValidationError
├── ConfigurationError
└── ... (additional exceptions)
```

#### Usage Example
```python
from deployforge.core.exceptions import ImageNotFoundError, MountError

try:
    manager = ImageManager(Path('missing.wim'))
except ImageNotFoundError as e:
    logger.error(f"Image not found: {e}")
except MountError as e:
    logger.error(f"Mount failed: {e}")
```

---

## Format Handlers

### handlers/iso_handler.py

**Lines**: ~500
**Purpose**: ISO 9660 optical disc image handling
**Technology**: pycdlib
**Platforms**: Windows, Linux, macOS

#### Features
- Read/write ISO 9660 images
- Rock Ridge extensions
- Joliet extensions
- El Torito bootable images

#### Key Classes
- `ISOHandler` - Main handler class

---

### handlers/wim_handler.py

**Lines**: ~500
**Purpose**: Windows Imaging Format handling
**Technology**: DISM (Windows), wimlib (Linux/macOS)
**Platforms**: Windows (native), Linux, macOS (wimlib)

#### Features
- Multi-index WIM support
- Compression (LZX, XPRESS)
- Incremental updates
- Split WIM handling

#### Platform-Specific
- **Windows**: Uses DISM (built-in)
- **Linux/macOS**: Uses wimlib-imagex

---

### handlers/esd_handler.py

**Lines**: ~400
**Purpose**: Electronic Software Download (compressed WIM)
**Technology**: DISM/wimlib with LZMS compression
**Platforms**: Windows, Linux, macOS

#### Features
- Ultra-high compression (LZMS)
- Microsoft distribution format
- Conversion to/from WIM

---

### handlers/ppkg_handler.py

**Lines**: ~400
**Purpose**: Provisioning package handling
**Technology**: ZIP-based format
**Platforms**: Windows, Linux, macOS

#### Features
- Windows 10/11 provisioning
- OOBE customization
- Runtime provisioning

---

### handlers/vhd_handler.py

**Lines**: ~500
**Purpose**: Virtual Hard Disk handling
**Technology**: PowerShell (Windows), qemu-nbd/libguestfs (Linux)
**Platforms**: Windows, Linux (limited macOS)

#### Features
- VHD format support
- VHDX format support
- Fixed and dynamic disks
- Differencing disks

---

## User Interfaces

### gui_modern.py

**Location**: `src/deployforge/gui_modern.py`
**Lines**: 3,229 (LARGEST MODULE)
**Status**: Production-ready, PRIMARY INTERFACE
**Stability**: ⚠️ Active development
**Technology**: PyQt6

#### Purpose
Modern graphical user interface with 150+ features across 16 categories. The primary user-facing interface for DeployForge.

#### Architecture

**5-Page Navigation System**:
1. **WelcomePage** - Drag-and-drop image loading, recent files
2. **BuildPage** - 150+ feature checkboxes in 16 categories
3. **ProfilesPage** - 6 pre-configured profiles
4. **AnalyzePage** - Image analysis and comparison
5. **SettingsPage** - Configuration management

#### Key Classes

```python
class Theme:
    """Theme color definitions (Light/Dark)"""
    LIGHT = {...}
    DARK = {...}

class ThemeManager:
    """Manages application theming"""
    def apply_theme(theme_name: str) -> None
    def generate_stylesheet() -> str

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self)
    def setup_ui(self)
    def create_sidebar(self)
    def switch_page(page_index: int)

class WelcomePage(QWidget):
    """Welcome/home page with drag-and-drop"""
    def dragEnterEvent(event: QDragEnterEvent)
    def dropEvent(event: QDropEvent)
    def load_image(path: Path)

class BuildPage(QWidget):
    """Feature selection page (150+ checkboxes)"""
    def __init__(self)
    def _init_gaming_features(self)
    def _init_debloat_features(self)
    def _init_privacy_features(self)
    # ... 13 more category methods

class ProfilesPage(QWidget):
    """Pre-configured profile selection"""
    profiles = {
        'Gaming': [...],
        'Developer': [...],
        'Enterprise': [...],
        'Student': [...],
        'Creator': [...],
        'Custom': [...]
    }

class AnalyzePage(QWidget):
    """Image analysis tools"""

class SettingsPage(QWidget):
    """Settings management with QSettings persistence"""
```

#### Features

**16 Feature Categories** (150+ total features):
1. 🎮 **Gaming** (15) - Optimization, drivers, platforms
2. 🗑️ **Debloat** (20) - Remove bloatware
3. 🔒 **Privacy** (16) - Telemetry, tracking
4. 🎨 **Visual** (19) - UI customization
5. 💻 **Developer** (19) - IDEs, runtimes, tools
6. 🏢 **Enterprise** (12) - Security, policies
7. 🌐 **Browsers** (6) - Firefox, Chrome, Brave, etc.
8. 📝 **Office & Productivity** (10) - Office, Teams, Slack
9. 🎨 **Creative & Media** (10) - OBS, GIMP, Blender
10. 🎮 **Gaming Platforms** (7) - Steam, Epic, GOG
11. 🔧 **System Utilities** (10) - 7-Zip, PowerToys
12. ⚡ **Performance** (10) - Services, indexing
13. 🔌 **Services** (8) - Windows Update, Print Spooler
14. 🔋 **Power** (5) - Power plans
15. 📁 **File Explorer** (7) - Quick Access, libraries
16. 🌐 **Network** (13) - DNS, firewall, IPv6

**6 Profiles**:
- **Gaming** (27 features) - Steam, Epic, GOG, NVIDIA, DirectX
- **Developer** (28 features) - Python, Node.js, Java, .NET, 4 browsers
- **Enterprise** (24 features) - Security, compliance, Office
- **Student** (23 features) - Office, browsers, privacy
- **Creator** (27 features) - Creative apps, performance
- **Custom** - User-defined

#### Theme System

**Light Theme Colors**:
```python
background: '#FAFAFA'
surface: '#FFFFFF'
primary: '#0078D4'
text: '#1F1F1F'
# ... more colors
```

**Dark Theme Colors**:
```python
background: '#1E1E1E'
surface: '#252526'
primary: '#0078D4'
text: '#FFFFFF'
# ... more colors
```

#### Settings Persistence

Uses QSettings for automatic persistence:
```python
settings = QSettings('DeployForge', 'ModernGUI')
settings.setValue('theme', 'Dark')
settings.setValue('window_geometry', self.saveGeometry())
settings.setValue('recent_files', recent_files)
```

#### Drag-and-Drop Implementation

```python
def dragEnterEvent(self, event: QDragEnterEvent):
    if event.mimeData().hasUrls():
        event.acceptProposedAction()

def dropEvent(self, event: QDropEvent):
    for url in event.mimeData().urls():
        path = Path(url.toLocalFile())
        if path.suffix.lower() in ['.wim', '.esd', '.iso']:
            self.load_image(path)
```

#### Modification Guide

**Adding a Feature Checkbox**:
```python
# In BuildPage._init_gaming_features()
self.feature_checkboxes['new_feature'] = QCheckBox("New Feature")
self.feature_checkboxes['new_feature'].setToolTip("Description")
layout.addWidget(self.feature_checkboxes['new_feature'])
```

**Adding a Profile**:
```python
# In ProfilesPage
self.profiles['NewProfile'] = [
    'feature1', 'feature2', 'feature3'
]
```

**Adding a Theme Color**:
```python
# In Theme.LIGHT or Theme.DARK
'new_color': '#HEXCODE'
```

#### Dependencies
- PyQt6 - GUI framework
- `cli.profiles` - Profile backend
- `cli.analyzer` - Analysis tools
- `config_manager` - Configuration

#### Related Files
- `gui.py` - Legacy GUI (deprecated)
- `gui/main_window.py` - Legacy implementation

---

### cli.py

**Location**: `src/deployforge/cli.py`
**Lines**: 480
**Status**: Production-ready
**Technology**: Click + Rich

#### Purpose
Command-line interface with rich terminal output and progress bars.

#### Commands
```bash
deployforge formats                    # List supported formats
deployforge info <image>              # Get image information
deployforge list <image> [--path]     # List files
deployforge add <image> <src> <dst>   # Add file
deployforge remove <image> <path>     # Remove file
deployforge extract <image> <src> <dst> # Extract file
deployforge mount <image> [--point]   # Mount image
deployforge unmount <image>           # Unmount
deployforge compare <img1> <img2>     # Compare images
deployforge batch <operation> <images> # Batch operations
deployforge gui                       # Launch GUI
deployforge api [--port] [--host]     # Start API server
```

#### Features
- Rich terminal formatting
- Progress bars for long operations
- Color-coded output
- Table formatting
- Interactive prompts

---

### api/main.py

**Location**: `src/deployforge/api/main.py`
**Lines**: ~400
**Status**: Production-ready
**Technology**: FastAPI + Uvicorn

#### Purpose
REST API with OpenAPI/Swagger documentation for automation and integration.

#### Endpoints

**Image Operations**:
- `POST /images/info` - Get image information
- `POST /images/list` - List files
- `POST /images/add` - Add file
- `POST /images/remove` - Remove file
- `POST /images/extract` - Extract file

**Registry Operations**:
- `POST /registry/set` - Set registry value
- `POST /registry/get` - Get registry value
- `POST /registry/delete` - Delete registry key

**Driver Operations**:
- `POST /drivers/inject` - Inject driver package
- `GET /drivers/list` - List installed drivers

**Batch Operations**:
- `POST /batch/operations` - Create batch job
- `GET /batch/status/{job_id}` - Get job status
- `GET /batch/results/{job_id}` - Get job results

**Template Operations**:
- `POST /templates/apply` - Apply template
- `GET /templates/list` - List available templates

**Health Check**:
- `GET /health` - API health status
- `GET /docs` - OpenAPI/Swagger UI
- `GET /redoc` - ReDoc documentation

#### Usage Example
```python
import requests

response = requests.post(
    'http://localhost:8000/images/info',
    json={'image_path': '/path/to/install.wim'}
)
info = response.json()
```

---

## Enhanced Modules

### devenv.py

**Lines**: 749
**Category**: Enhanced Module (1 of 9)
**Status**: World-class standard
**Profiles**: 10

#### Purpose
Development environment setup with IDE installation, language runtimes, and cloud tools.

#### Profiles
1. **Python** - Python 3.x, pip, virtual environments
2. **JavaScript** - Node.js, npm, yarn
3. **DotNet** - .NET SDK, Visual Studio
4. **Java** - JDK, Maven, Gradle
5. **C/C++** - MSVC, MinGW, CMake
6. **Web** - PHP, Ruby, Go
7. **Mobile** - Android SDK, Flutter
8. **Data Science** - Anaconda, Jupyter
9. **Cloud** - AWS CLI, Azure CLI, kubectl
10. **Full Stack** - Combination of all

#### Key Classes
```python
class DevelopmentProfile(Enum)
class DevelopmentConfig(dataclass)
class DevelopmentEnvironmentManager
```

---

### browsers.py

**Lines**: 685
**Category**: Enhanced Module (2 of 9)
**Status**: World-class standard
**Browsers**: 17+

#### Purpose
Browser installation and configuration with enterprise policies and privacy settings.

#### Supported Browsers
- Firefox, Chrome, Brave, Edge, Opera, Vivaldi
- Tor Browser, Ungoogled Chromium
- LibreWolf, Waterfox, Pale Moon
- And more...

#### Features
- Automated installation
- Enterprise policy configuration
- Privacy hardening
- Extension management
- Profile configuration

---

### ui_customization.py

**Lines**: 618
**Category**: Enhanced Module (6 of 9)
**Status**: World-class standard
**Profiles**: 6

#### Purpose
Windows UI customization including taskbar, Start Menu, File Explorer, and themes.

#### Profiles
1. **Classic** - Windows 7-style interface
2. **Minimal** - Clean, minimal UI
3. **Productivity** - Workflow optimization
4. **Gaming** - Streamlined for gaming
5. **Modern** - Windows 11 enhancements
6. **Custom** - User-defined

---

### backup.py

**Lines**: 650
**Category**: Enhanced Module (7 of 9)
**Status**: World-class standard
**Profiles**: 5

#### Purpose
Backup and recovery configuration with System Restore, VSS, File History.

#### Profiles
1. **Basic** - System Restore only
2. **Standard** - System Restore + File History
3. **Advanced** - VSS + incremental backups
4. **Server** - Enterprise backup
5. **Custom** - User-defined

---

### wizard.py

**Lines**: 527
**Category**: Enhanced Module (8 of 9)
**Status**: World-class standard
**Presets**: 9

#### Purpose
Setup wizard with hardware detection and preset configurations.

#### Presets
1. **Gaming PC** - GPU, gaming optimizations
2. **Developer Workstation** - Dev tools, performance
3. **Enterprise Desktop** - Security, compliance
4. **Student Laptop** - Productivity, efficiency
5. **Creator Station** - Creative apps, GPU
6. **Home Office** - General productivity
7. **Server** - Server roles, stability
8. **HTPC** - Media center optimization
9. **Custom** - Guided custom setup

---

### portable.py

**Lines**: 613
**Category**: Enhanced Module (9 of 9)
**Status**: World-class standard
**Apps**: 20+ catalog

#### Purpose
Portable application management with PortableApps.com integration.

#### Profiles
1. **Essential** - Basic utilities
2. **Developer** - Dev tools
3. **Office** - Productivity apps
4. **Media** - Audio/video tools
5. **Gaming** - Game-related utilities
6. **Security** - Security tools
7. **Custom** - User selection

---

### creative.py

**Lines**: 545
**Category**: Enhanced Module (3 of 9)
**Status**: World-class standard

#### Purpose
Creative software installation with GPU optimization.

#### Applications
- OBS Studio, GIMP, Inkscape, Blender
- DaVinci Resolve, Audacity, Kdenlive
- And more...

---

### privacy_hardening.py

**Lines**: 397
**Category**: Enhanced Module (4 of 9)
**Status**: World-class standard
**Levels**: 4

#### Purpose
Privacy protection with comprehensive telemetry blocking.

#### Levels
1. **Basic** - Essential privacy
2. **Standard** - Recommended settings
3. **Enhanced** - Strict privacy
4. **Maximum** - Complete lockdown

---

### launchers.py

**Lines**: 399
**Category**: Enhanced Module (5 of 9)
**Status**: World-class standard
**Platforms**: 12+

#### Purpose
Gaming platform installation with mod manager support.

#### Platforms
- Steam, Epic Games Store, GOG Galaxy
- Origin, Ubisoft Connect, Battle.net
- Xbox App, EA App
- And more...

---

### gaming.py

**Lines**: 443
**Category**: Enhanced Module (REFERENCE IMPLEMENTATION)
**Status**: World-class standard - ALL MODULES FOLLOW THIS PATTERN
**Profiles**: 4

#### Purpose
Gaming optimization with GPU drivers and runtime installation.
**This is the reference implementation all enhanced modules follow.**

#### Quality Standard
All enhanced modules match this pattern:
- Enums for profiles
- Dataclasses for configuration with `to_dict()`
- Main optimizer/manager class
- Full type hints
- Google-style docstrings
- Comprehensive error handling
- Extensive logging

---

## Enterprise Features

### testing.py

**Lines**: 823 (2nd largest)
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Automated image testing and validation with VM-based checks.

#### Features
- Image integrity validation (checksums, signatures)
- VM-based bootability testing
- Driver signature validation
- Update compliance verification
- Performance metrics collection
- Automated test report generation

#### Supported Hypervisors
- Hyper-V (Windows)
- VirtualBox (cross-platform)
- VMware Workstation/Player
- QEMU/KVM (Linux)

#### Key Classes
```python
class TestStatus(Enum)
class Hypervisor(Enum)
class TestResult(dataclass)
class ImageValidator
class VMTester
class TestRunner
class TestReport
```

#### Usage Example
```python
from deployforge.testing import ImageValidator, VMTester

# Validate integrity
validator = ImageValidator(Path('install.wim'))
result = validator.validate_all()

# Boot test in VM
tester = VMTester(Path('install.wim'), Hypervisor.VIRTUALBOX)
boot_result = tester.test_boot(timeout=300)
```

---

### integration.py

**Lines**: 786 (3rd largest)
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Microsoft Deployment Toolkit (MDT) and System Center Configuration Manager (SCCM) integration for enterprise deployment.

#### MDT Features
- Deployment share management
- Task sequence creation/modification
- Application import/export
- Driver package management
- Boot image generation
- Selection profile creation

#### SCCM Features
- Package creation
- Application management
- OS image deployment
- Distribution point management
- Task sequence deployment

#### Key Classes
```python
class TaskSequenceType(Enum)
class MDTApplicationType(Enum)
class MDTApplication(dataclass)
class MDTManager
class TaskSequenceBuilder
class SCCMPackageCreator
class DeploymentShareManager
```

#### Usage Example
```python
from deployforge.integration import MDTManager, TaskSequenceBuilder

# Create deployment share
mdt = MDTManager(Path('D:\\DeploymentShare'))
mdt.create_share()

# Import OS image
mdt.import_os_image(Path('install.wim'), 'Windows 11 Pro')

# Create task sequence
builder = TaskSequenceBuilder(mdt)
task_seq = builder.create_standard_client(
    name='Windows 11 Enterprise',
    template='Standard Client'
)
```

---

### iac.py

**Lines**: 770 (4th largest)
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Infrastructure as Code for complete build automation using YAML/JSON definitions.

#### Features
- YAML/JSON deployment definitions
- Template variables and interpolation
- Multi-stage builds
- Schema validation
- CLI integration
- Variable substitution
- Conditional logic

#### Build Stages
1. `init` - Initialization
2. `partitions` - Partition creation
3. `base` - Base image setup
4. `drivers` - Driver injection
5. `updates` - Windows updates
6. `applications` - App installation
7. `security` - Security hardening
8. `certificates` - Certificate injection
9. `gpo` - Group Policy
10. `languages` - Language packs
11. `customization` - Final tweaks
12. `finalize` - Cleanup and validation

#### Configuration Example
```yaml
# deploy.yaml
version: "1.0"
name: "Enterprise Windows 11 Build"
image: "install.wim"
index: 1
output: "Win11_Enterprise.wim"

variables:
  company: "Acme Corp"
  domain: "acme.local"

stages:
  - name: partitions
    action: create
    type: uefi_gpt
    size: 50GB

  - name: base
    profile: enterprise
    debloat: true
    privacy: enhanced

  - name: drivers
    packages:
      - "drivers/nvidia/*.inf"
      - "drivers/intel/*.inf"

  - name: security
    level: high
    firewall: enabled
    defender: configured

  - name: certificates
    import:
      - "certs/root_ca.cer"
      - "certs/intermediate.cer"

  - name: customization
    registry:
      - key: "HKLM\\SOFTWARE\\${company}"
        value: "Deployed"
        data: "true"
```

#### Key Classes
```python
class ConfigFormat(Enum)
class BuildStage(Enum)
class IaCConfig(dataclass)
class IaCRunner
class TemplateEngine
class StageExecutor
```

#### Usage Example
```python
from deployforge.iac import IaCRunner

runner = IaCRunner(Path('deploy.yaml'))
result = runner.execute_all_stages()
runner.generate_report(Path('build_report.txt'))
```

---

### scheduler.py

**Lines**: 716
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Cron-based job scheduling and queue management for automated builds.

#### Features
- Cron-based scheduling (e.g., `0 2 * * *` for 2 AM daily)
- Job queue with priority levels
- Background task execution
- Job status tracking
- Retry logic with exponential backoff
- Email/webhook notifications
- Persistent job storage (JSON/SQLite)

#### Job Priorities
1. **LOW** - Background tasks
2. **NORMAL** - Standard builds
3. **HIGH** - Important deployments
4. **URGENT** - Critical updates

#### Key Classes
```python
class JobStatus(Enum)
class JobPriority(Enum)
class Job(dataclass)
class JobScheduler
class JobQueue
class JobExecutor
class NotificationManager
```

#### Usage Example
```python
from deployforge.scheduler import JobScheduler, JobPriority
from datetime import datetime

scheduler = JobScheduler()

# Schedule daily build at 2 AM
job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config=build_config,
    schedule='0 2 * * *',  # Cron format
    priority=JobPriority.HIGH,
    retry_count=3,
    notify_email='admin@company.com'
)

# Check job status
status = scheduler.get_job_status(job.id)
```

---

### versioning.py

**Lines**: 689
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Git-like version control system for Windows images.

#### Features
- Image versioning with commit history
- Commit/checkout workflow
- Version tags (e.g., `v1.0.0`, `production`)
- Branch support for variants
- Diff between versions
- Rollback capability
- Change log generation
- SHA256 hash tracking

#### Key Classes
```python
class ImageCommit(dataclass)
class ImageBranch(dataclass)
class ImageTag(dataclass)
class ImageRepository
class VersionControl
class DiffEngine
```

#### Usage Example
```python
from deployforge.versioning import ImageRepository

repo = ImageRepository(Path('/images/repo'))

# Initialize repository
repo.init()

# Commit an image
commit = repo.commit(
    image_path=Path('Win11_Custom.wim'),
    message='Initial Windows 11 customization',
    version='1.0.0',
    tags=['production', 'baseline']
)

# List history
history = repo.log()

# Checkout previous version
repo.checkout('v1.0.0')

# Create branch for variant
repo.create_branch('gaming-variant')

# Diff between versions
diff = repo.diff('v1.0.0', 'v1.1.0')
```

---

### gpo.py

**Lines**: 658
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Group Policy Objects (GPO) management and deployment.

#### Features
- GPO creation and modification
- Policy import/export (XML)
- Template-based policies
- Registry-based GPO
- Administrative templates (ADMX)
- Compliance checking
- Policy reporting

#### Key Classes
```python
class PolicyScope(Enum)
class PolicyType(Enum)
class GroupPolicy(dataclass)
class GPOManager
class PolicyTemplate
class ComplianceChecker
```

#### Usage Example
```python
from deployforge.gpo import GPOManager, PolicyScope

gpo = GPOManager()

# Create security policy
policy = gpo.create_policy(
    name='Security Baseline',
    scope=PolicyScope.COMPUTER,
    settings={
        'password_policy': {...},
        'audit_policy': {...},
        'user_rights': {...}
    }
)

# Apply to image
gpo.apply_to_image(
    image_path=Path('install.wim'),
    policy_path=Path('security_baseline.xml')
)
```

---

### certificates.py

**Lines**: 622
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Certificate management and injection for trusted certificate stores.

#### Features
- Certificate installation (Root, Intermediate, Personal)
- Trust store management
- Enterprise CA integration
- Certificate validation
- CRL/OCSP configuration
- Auto-enrollment setup

#### Supported Formats
- .CER (DER/PEM)
- .PFX/.P12 (with password)
- .CRT
- .P7B (certificate chain)

#### Key Classes
```python
class CertificateStore(Enum)
class CertificateType(Enum)
class Certificate(dataclass)
class CertificateManager
class TrustStoreManager
class EnterpriseCAManager
```

#### Usage Example
```python
from deployforge.certificates import CertificateManager, CertificateStore

cert_mgr = CertificateManager(Path('install.wim'))

# Install root CA
cert_mgr.install_certificate(
    cert_path=Path('root_ca.cer'),
    store=CertificateStore.ROOT,
    trust=True
)

# Install intermediate CA
cert_mgr.install_certificate(
    cert_path=Path('intermediate.cer'),
    store=CertificateStore.INTERMEDIATE
)

# Configure enterprise CA
cert_mgr.configure_enterprise_ca(
    ca_server='ca.company.com',
    auto_enroll=True
)
```

---

### partitions.py

**Lines**: 720
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
UEFI/GPT partitioning and disk management.

#### Features
- GPT partition table creation
- UEFI boot partition setup
- EFI System Partition (ESP)
- Microsoft Reserved Partition (MSR)
- Recovery partition
- Data partitions
- Disk initialization

#### Key Classes
```python
class PartitionType(Enum)
class PartitionScheme(Enum)
class Partition(dataclass)
class DiskManager
class PartitionManager
class UEFIManager
```

---

### unattend.py

**Lines**: 675
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Automated answer file (unattend.xml) generation for Windows deployment.

#### Features
- Unattend.xml generation
- OOBE automation
- User account creation
- Product key insertion
- Domain join configuration
- Network settings
- Regional settings

---

### languages.py

**Lines**: 654
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Multi-language support and MUI (Multilingual User Interface) package management.

#### Supported Languages
40+ languages including:
- English (US, UK, AU, CA)
- Spanish (ES, MX, AR)
- French (FR, CA)
- German, Italian, Portuguese
- Chinese (Simplified, Traditional)
- Japanese, Korean
- Arabic, Russian
- And more...

---

### security.py

**Lines**: 642
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Security hardening and compliance.

#### Features
- Windows Defender configuration
- Firewall rules
- User Account Control (UAC)
- BitLocker preparation
- Security baselines (CIS, STIG)
- Vulnerability scanning
- Compliance reporting

---

### winpe.py

**Lines**: 639
**Category**: Enterprise
**Status**: Production-ready

#### Purpose
Windows Preinstallation Environment (WinPE) customization.

#### Features
- WinPE image creation
- Driver injection into WinPE
- Package addition (WinPE-*)
- Network configuration
- Storage drivers
- Boot media generation

---

## Automation & Integration

### automation.py

**Lines**: 677
**Category**: Automation
**Status**: Production-ready

#### Purpose
Ansible and Terraform integration for infrastructure automation.

#### Ansible Module
```yaml
# Example Ansible playbook
- name: Build Windows image
  deployforge:
    image: install.wim
    profile: enterprise
    output: win11_enterprise.wim
```

#### Terraform Provider
```hcl
# Example Terraform configuration
resource "deployforge_image" "windows11" {
  source  = "install.wim"
  profile = "enterprise"
  output  = "win11_enterprise.wim"
}
```

---

### ai.py

**Lines**: 597
**Category**: Automation
**Status**: Beta

#### Purpose
AI-powered features and automation.

#### Features
- Image analysis with ML
- Automatic optimization recommendations
- Intelligent driver selection
- Predictive update management
- Natural language queries

---

### differential.py

**Lines**: 596
**Category**: Automation
**Status**: Production-ready

#### Purpose
Differential updates and incremental changes.

#### Features
- Delta patch generation
- Incremental updates
- Binary diff/patch
- Bandwidth optimization

---

### containers.py

**Lines**: 585
**Category**: Automation
**Status**: Beta

#### Purpose
Container support for Windows Server.

#### Features
- Windows Server container images
- Docker integration
- Kubernetes manifests
- Container optimization

---

### cloud.py

**Lines**: 573
**Category**: Automation
**Status**: Production-ready

#### Purpose
Cloud deployment to AWS, Azure, GCP.

#### Features
- Azure VM image upload
- AWS AMI creation
- GCP image import
- Cloud-init configuration

---

## Utility Modules

### config_manager.py

**Lines**: 569
**Purpose**: Centralized configuration management

---

### encryption.py

**Lines**: 560
**Purpose**: Image encryption with BitLocker

---

### applications.py

**Lines**: 525
**Purpose**: Application installation management

---

### optimizer.py

**Lines**: 482
**Purpose**: General system optimization

---

### rollback.py

**Lines**: 465
**Purpose**: Rollback and recovery capabilities

---

### features.py

**Lines**: 444
**Purpose**: Feature flag management

---

### network.py

**Lines**: 440
**Purpose**: Network configuration (DNS, firewall, IPv6)

---

### debloat.py

**Lines**: 419
**Purpose**: Bloatware removal (AppX packages, features)

---

### feature_updates.py

**Lines**: 387
**Purpose**: Windows feature update management

---

### sandbox.py

**Lines**: 361
**Purpose**: Windows Sandbox integration

---

### remote.py

**Lines**: 354
**Purpose**: Remote storage (S3, Azure Blob, HTTP)

---

### comparison.py

**Lines**: 335
**Purpose**: Image comparison and diff

---

### batch.py

**Lines**: 321
**Purpose**: Batch operations with parallel processing

---

### registry.py

**Lines**: 301
**Purpose**: Offline registry editing

---

### templates.py

**Lines**: 299
**Purpose**: Template system for reusable workflows

---

### drivers.py

**Lines**: 286
**Purpose**: Driver injection via DISM

---

### performance.py

**Lines**: 228
**Purpose**: Performance monitoring with psutil

---

### updates.py

**Lines**: 216
**Purpose**: Windows Update integration (MSU/CAB)

---

### themes.py

**Lines**: 211
**Purpose**: Windows theme management

---

### cache.py

**Lines**: 192
**Purpose**: Caching layer with TTL

---

### config.py

**Lines**: 186
**Purpose**: YAML configuration file handling

---

### audit.py

**Lines**: 179
**Purpose**: JSONL audit logging

---

### packages.py

**Lines**: 130
**Purpose**: Package management (AppX, MSI)

---

## Quick Reference

### Module Categorization

**By Importance (AI Assistant Priority)**:
1. 🔴 CRITICAL: core/, handlers/, gui_modern.py, cli.py, api/
2. 🟡 HIGH: Enhanced modules (9), enterprise features (8)
3. 🟢 MEDIUM: Automation, utilities
4. ⚪ LOW: Experimental features

**By Modification Frequency**:
- 🔒 **Never modify**: core/
- ⚠️ **Careful modification**: handlers/, gui_modern.py
- ✅ **Safe to modify**: Feature modules, utilities
- 🚀 **Actively developed**: Enhanced modules, enterprise

**By User Interface**:
- 🖥️ **GUI**: gui_modern.py (primary)
- 💻 **CLI**: cli.py
- 🌐 **API**: api/main.py
- 🔧 **Backend**: All other modules

---

## Conclusion

This reference documents all 54 modules in DeployForge totaling 29,163 lines of code. Each module serves a specific purpose in the comprehensive Windows deployment automation system.

**For AI Assistants**: Refer to this document to understand module purposes, relationships, and modification guidelines. Always check module stability before making changes.

**For Developers**: Use this as a quick reference to navigate the codebase and understand the architecture.

---

**Last Updated**: 2025-11-15
**Maintained By**: DeployForge Team
**Version**: 1.7.0 (Documentation) / 0.3.0 (Release)
