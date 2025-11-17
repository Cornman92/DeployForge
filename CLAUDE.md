# CLAUDE.md - AI Assistant Guide for DeployForge

**Version**: 1.7.0 (Documentation) / 0.3.0 (Release)
**Last Updated**: 2025-11-15
**Purpose**: Comprehensive guide for AI assistants working with the DeployForge codebase

> ⚠️ **Version Note**: This document tracks enhancement milestones (v1.7.0). The official PyPI release version is **v0.3.0** (see `pyproject.toml`). Development version in code is v0.6.0 (`__init__.py`).

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Architecture & Design Patterns](#architecture--design-patterns)
4. [Coding Conventions & Standards](#coding-conventions--standards)
5. [Development Workflow](#development-workflow)
6. [Testing Strategy](#testing-strategy)
7. [Key Modules & Components](#key-modules--components)
8. [Advanced Enterprise Modules](#advanced-enterprise-modules)
9. [Complete Module Index](#complete-module-index)
10. [Common Tasks & Workflows](#common-tasks--workflows)
11. [Git Workflow & Branching](#git-workflow--branching)
12. [Important Context](#important-context)

---

## Project Overview

### What is DeployForge?

DeployForge is an **enterprise-grade Windows deployment suite** that provides comprehensive automation for Windows image customization. It's a production-ready tool with 150+ features, 9 world-class enhanced backend modules, and multiple user interfaces.

### Key Statistics

- **Version**: 1.7.0 (v1.6.0 enhanced modules 1-5, v1.7.0 enhanced modules 6-9)
- **Total Code**: 29,163+ lines of Python
- **Modules**: 70+ Python files
- **Enhanced Modules**: 9/9 complete (+4,500 lines)
- **Features**: 150+ customization features across 16 categories
- **Image Formats**: 6 (ISO, WIM, ESD, PPKG, VHD, VHDX)
- **Interfaces**: 3 (CLI, Modern GUI, REST API)
- **Python Support**: 3.9, 3.10, 3.11, 3.12
- **Platforms**: Windows, Linux, macOS

### Core Capabilities

1. **Image Manipulation**: Mount, modify, and save Windows deployment images
2. **Customization**: 150+ features including debloat, privacy, gaming, dev tools
3. **Automation**: Batch operations, templates, profiles, API integration
4. **Enterprise**: Audit logging, compliance, security hardening
5. **GUI**: Beautiful PyQt6 modern interface with drag-and-drop
6. **Advanced**: UEFI/GPT partitioning, WinPE, answer files, multi-language

---

## Repository Structure

### High-Level Layout

```
DeployForge/
├── src/deployforge/           # Main source code (29,163+ lines)
│   ├── core/                 # Core architecture (3 files)
│   │   ├── image_manager.py  # Main entry point, handler factory
│   │   ├── base_handler.py   # Abstract base class for handlers
│   │   └── exceptions.py     # Custom exception hierarchy
│   │
│   ├── handlers/             # Image format handlers (5 files)
│   │   ├── iso_handler.py    # ISO 9660 handler (pycdlib)
│   │   ├── wim_handler.py    # WIM handler (DISM/wimlib)
│   │   ├── esd_handler.py    # ESD handler (compressed WIM)
│   │   ├── ppkg_handler.py   # PPKG handler (provisioning)
│   │   └── vhd_handler.py    # VHD/VHDX handler (virtual disks)
│   │
│   ├── cli/                  # CLI components
│   │   ├── profiles.py       # Profile management (Gaming, Dev, etc.)
│   │   ├── analyzer.py       # Image analysis tools
│   │   └── presets.py        # Setup presets/wizards
│   │
│   ├── api/                  # REST API (FastAPI)
│   │   └── main.py           # API endpoints and OpenAPI docs
│   │
│   ├── gui/                  # Desktop GUI (legacy)
│   │   └── main_window.py    # PyQt6 GUI application
│   │
│   ├── utils/                # Utilities
│   │   ├── logger.py         # Logging configuration
│   │   └── progress.py       # Progress tracking
│   │
│   ├── gui_modern.py         # ✨ Modern GUI (v1.5.0+, primary interface)
│   │
│   ├── Enhanced Modules (9 files, 5,185 lines total)
│   ├── devenv.py             # Dev environments (750 lines, 10 profiles)
│   ├── browsers.py           # Browsers (686 lines, 17+ browsers)
│   ├── creative.py           # Creative software (545 lines)
│   ├── privacy_hardening.py  # Privacy (397 lines, 4 levels)
│   ├── launchers.py          # Gaming platforms (399 lines, 12+)
│   ├── ui_customization.py   # UI themes (618 lines, 6 profiles)
│   ├── backup.py             # Backup/recovery (650 lines, 5 profiles)
│   ├── wizard.py             # Setup wizard (527 lines, 9 presets)
│   └── portable.py           # Portable apps (613 lines, 20+ catalog)
│   │
│   ├── Core Feature Modules (25+ files)
│   ├── gaming.py             # Gaming optimization (443 lines, reference quality)
│   ├── debloat.py            # Bloatware removal
│   ├── registry.py           # Registry editing
│   ├── drivers.py            # Driver injection
│   ├── updates.py            # Windows Update integration
│   ├── templates.py          # Template system
│   ├── batch.py              # Batch operations
│   ├── comparison.py         # Image comparison
│   ├── performance.py        # Performance monitoring
│   ├── security.py           # Security hardening
│   ├── network.py            # Network configuration
│   ├── packages.py           # Package management
│   ├── partitions.py         # UEFI/GPT partitioning
│   ├── unattend.py           # Answer file generation
│   ├── winpe.py              # WinPE customization
│   ├── languages.py          # Multi-language (MUI)
│   └── ... (see full list in src/)
│
├── tests/                    # Test suite (10 files)
│   ├── conftest.py           # Pytest configuration & fixtures
│   ├── test_*.py             # Unit tests with mocking
│   └── ...                   # Coverage: 85%+
│
├── docs/                     # Documentation
│   ├── architecture.md       # 900+ lines architecture guide
│   ├── security.md           # 500+ lines security guide
│   └── index.md              # Documentation index
│
├── examples/                 # Real-world examples
│   ├── windows11_custom.py   # Windows 11 customization
│   ├── gaming_pc_build.py    # Gaming PC optimization
│   ├── enterprise_workstation.py  # Enterprise hardening
│   └── ...
│
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml                # Multi-platform testing
│   ├── docker.yml            # Docker builds
│   └── release.yml           # PyPI publishing
│
├── vscode-extension/         # VS Code extension (future)
│
├── Configuration Files
├── pyproject.toml            # Project metadata, dependencies, build
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # Dev dependencies
├── deployforge.yaml.example  # Example configuration
├── Dockerfile                # Docker image
│
├── Documentation (25+ MD files)
├── README.md                 # Main documentation (669 lines)
├── CONTRIBUTING.md           # Contribution guidelines
├── CHANGELOG.md              # Version history
├── ROADMAP.md                # Development roadmap
├── PROJECT_SUMMARY.md        # Comprehensive project overview
├── MODULES_6-9_ENHANCEMENT_COMPLETE.md  # Latest enhancements
└── ... (various planning/status docs)
```

### Key Directories

1. **`src/deployforge/core/`** - Core architecture, never modify without careful consideration
2. **`src/deployforge/handlers/`** - Image format handlers, follow base_handler.py interface
3. **`src/deployforge/`** (root) - Feature modules, well-documented, follow gaming.py pattern
4. **`tests/`** - Comprehensive test suite, maintain >85% coverage
5. **`docs/`** - Detailed documentation, keep synchronized with code

---

## Architecture & Design Patterns

### Core Architecture

DeployForge follows a **modular, extensible architecture** with clear separation of concerns:

```
User Interfaces (CLI/GUI/API)
         ↓
   ImageManager (Factory)
         ↓
   BaseImageHandler (Abstract Base)
         ↓
Format Handlers (ISO/WIM/ESD/PPKG/VHD/VHDX)
         ↓
  Platform Tools (DISM/wimlib/pycdlib)
```

### Design Patterns Used

1. **Factory Pattern**
   - `ImageManager.get_handler()` creates appropriate handler based on file extension
   - Location: `src/deployforge/core/image_manager.py:37`

2. **Strategy Pattern**
   - Different handlers implement same interface for different formats
   - Location: All files in `src/deployforge/handlers/`

3. **Abstract Base Class (ABC) Pattern**
   - `BaseImageHandler` defines interface for all handlers
   - Location: `src/deployforge/core/base_handler.py:12`

4. **Context Manager Pattern**
   - `ImageManager` supports `with` statement for automatic cleanup
   - All handlers implement proper resource management

5. **Template Method Pattern**
   - Base handler provides common validation, subclasses implement specifics
   - Example: `_validate_image()` in base handler

6. **Observer Pattern**
   - Progress callbacks for long-running operations
   - Event tracking for audit logging

7. **Decorator Pattern**
   - Caching layer wraps operations
   - Performance monitoring decorates methods

### Module Categories

1. **Core Infrastructure** (`core/`, `utils/`)
   - Foundation classes, exceptions, logging

2. **Format Handlers** (`handlers/`)
   - Image format-specific implementations

3. **Feature Modules** (root level)
   - Self-contained feature implementations
   - Examples: `gaming.py`, `devenv.py`, `browsers.py`

4. **User Interfaces** (`cli/`, `gui/`, `api/`, `gui_modern.py`)
   - Three separate interface implementations

5. **Enterprise Features** (`batch.py`, `templates.py`, `audit.py`, etc.)
   - Advanced capabilities for enterprise use

### Enhanced Module Pattern (gaming.py is the reference)

All 9 enhanced modules follow this structure:

```python
"""Module docstring with feature list"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# 1. Enums for profiles/options
class SomeProfile(Enum):
    """Profile types"""
    OPTION_A = "option_a"
    OPTION_B = "option_b"

# 2. Dataclasses for configuration
@dataclass
class SomeConfig:
    """Configuration settings"""
    setting1: bool = True
    setting2: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {...}

# 3. Main optimizer/manager class
class SomeOptimizer:
    """
    Main class with comprehensive docstring.

    Example:
        optimizer = SomeOptimizer(Path('install.wim'))
        optimizer.mount()
        optimizer.apply_profile(SomeProfile.OPTION_A)
        optimizer.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """Initialize with type hints and defaults"""
        self.image_path = image_path
        # ... initialization

    def apply_profile(self, profile: SomeProfile) -> None:
        """Apply predefined profile"""
        # Implementation with error handling

    def _private_helper(self) -> None:
        """Private methods prefixed with underscore"""
        pass
```

---

## Coding Conventions & Standards

### Python Style Guide

**Follow PEP 8 with DeployForge-specific conventions:**

1. **Line Length**: Maximum 100 characters (enforced by Black)
2. **Formatting**: Use Black for automatic formatting
3. **Imports**: Group as standard library, third-party, local
4. **Type Hints**: Always use type hints for function signatures
5. **Docstrings**: Google-style docstrings for all public functions/classes
6. **Private Methods**: Prefix with underscore (`_method_name`)
7. **Constants**: UPPER_CASE for module-level constants
8. **Logging**: Use module-level logger, never print()

### Type Hints Standard

```python
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

def function_name(
    required_param: str,
    optional_param: Optional[int] = None,
    list_param: List[str] = None
) -> Dict[str, Any]:
    """
    Function description.

    Args:
        required_param: Description
        optional_param: Description (default: None)
        list_param: Description (default: None)

    Returns:
        Dictionary containing results

    Raises:
        ValueError: When validation fails
        DeployForgeError: When operation fails
    """
    pass
```

### Docstring Standard (Google Style)

```python
class ExampleClass:
    """
    Brief one-line summary.

    Longer description with more details about the class purpose,
    usage patterns, and important notes.

    Example:
        >>> example = ExampleClass(param="value")
        >>> result = example.process()
        >>> print(result)

    Attributes:
        attr1: Description of attribute
        attr2: Description of attribute
    """

    def method_name(self, param: str) -> bool:
        """
        Brief description of what method does.

        Detailed explanation of behavior, edge cases, and important notes.

        Args:
            param: Description of parameter

        Returns:
            Description of return value

        Raises:
            ExceptionType: When and why this is raised
        """
        pass
```

### Error Handling Pattern

```python
from deployforge.core.exceptions import (
    DeployForgeError,
    ImageNotFoundError,
    MountError,
    UnsupportedFormatError
)

try:
    # Operation
    pass
except SpecificError as e:
    logger.error(f"Specific error occurred: {e}")
    raise DeployForgeError(f"Failed to perform operation: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for recoverable issues")
logger.error("Error messages for failures")
logger.critical("Critical errors that may cause shutdown")

# Include context in log messages
logger.info(f"Processing image: {image_path}")
logger.error(f"Failed to mount {image_path}: {error}")
```

### Configuration Pattern (Dataclasses + Enums)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List

class ProfileType(Enum):
    """Enumeration of profile types"""
    GAMING = "gaming"
    DEVELOPMENT = "development"
    ENTERPRISE = "enterprise"

@dataclass
class Configuration:
    """Configuration with sensible defaults"""
    profile: ProfileType = ProfileType.GAMING
    enabled_features: List[str] = field(default_factory=list)
    timeout: int = 300

    def validate(self) -> bool:
        """Validate configuration"""
        # Validation logic
        return True

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'profile': self.profile.value,
            'enabled_features': self.enabled_features,
            'timeout': self.timeout
        }
```

### Code Quality Tools

1. **Black** (formatting)
   ```bash
   black src/deployforge
   ```

2. **Flake8** (linting)
   ```bash
   flake8 src/deployforge --max-line-length=100
   ```

3. **MyPy** (type checking)
   ```bash
   mypy src/deployforge --ignore-missing-imports
   ```

4. **Bandit** (security scanning)
   ```bash
   bandit -r src/deployforge
   ```

---

## Development Workflow

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Install system dependencies (if needed)
# Linux:
sudo apt-get install wimtools

# macOS:
brew install wimlib
```

### Pre-Commit Checklist

Before committing code, ensure:

1. ✅ **Format code with Black**
   ```bash
   black src/deployforge
   ```

2. ✅ **Run linter**
   ```bash
   flake8 src/deployforge
   ```

3. ✅ **Type check**
   ```bash
   mypy src/deployforge --ignore-missing-imports
   ```

4. ✅ **Run tests**
   ```bash
   pytest
   ```

5. ✅ **Check coverage**
   ```bash
   pytest --cov=deployforge --cov-report=term
   ```

6. ✅ **Security scan**
   ```bash
   bandit -r src/deployforge
   ```

### Commit Message Convention

Follow **Conventional Commits** format:

```
<type>: <short description>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting)
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

**Examples:**

```
feat: add support for VMDK image format

- Implement VMDKHandler class
- Add mount/unmount operations
- Update documentation
- Add unit tests

Closes #123
```

```
fix: resolve memory leak in batch processing

The batch processor was not releasing image handlers properly,
causing memory to accumulate during large batch operations.

- Add proper cleanup in BatchOperation
- Implement context manager for handlers
- Add memory usage tests
```

---

## Testing Strategy

### Test Organization

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_image_manager.py    # Core tests
├── test_batch.py            # Batch operation tests
├── test_templates.py        # Template system tests
├── test_audit.py            # Audit logging tests
├── test_cache.py            # Cache layer tests
├── test_partitions.py       # Partitioning tests
├── test_unattend.py         # Answer file tests
├── test_languages.py        # Language pack tests
└── test_config.py           # Configuration tests
```

### Testing Principles

1. **Mocking External Dependencies**
   - Mock DISM, wimlib, pycdlib interactions
   - Mock file system operations when appropriate
   - Use `unittest.mock` or `pytest-mock`

2. **Fixture Usage**
   - Common fixtures in `conftest.py`
   - Reusable test data and objects

3. **Coverage Goals**
   - Maintain >85% code coverage
   - 100% coverage for core modules

4. **Test Categories**
   - Unit tests: Test individual components
   - Integration tests: Test component interactions
   - No end-to-end tests (require real images)

### Example Test Pattern

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import ImageNotFoundError

def test_image_manager_initialization():
    """Test ImageManager initialization with valid image."""
    with patch('pathlib.Path.exists', return_value=True):
        manager = ImageManager(Path('test.wim'))
        assert manager.image_path == Path('test.wim')

def test_image_not_found_error():
    """Test error handling for missing image."""
    with pytest.raises(ImageNotFoundError):
        ImageManager(Path('nonexistent.wim'))

@patch('subprocess.run')
def test_mount_operation(mock_run):
    """Test image mounting with mocked subprocess."""
    mock_run.return_value = Mock(returncode=0)
    # Test implementation
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_batch.py

# Run with coverage
pytest --cov=deployforge --cov-report=html

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run with specific markers (if defined)
pytest -m unit
```

---

## Key Modules & Components

### Core Modules

#### 1. ImageManager (`src/deployforge/core/image_manager.py`)

**Purpose**: Main entry point for image operations, factory for handlers

**Key Methods:**
- `get_handler(image_path)` - Factory method returning appropriate handler
- `supported_formats()` - List supported formats
- `mount()`, `unmount()`, `list_files()`, `add_file()`, etc.

**Usage:**
```python
from deployforge import ImageManager
from pathlib import Path

with ImageManager(Path('install.wim')) as manager:
    manager.mount()
    files = manager.list_files('/Windows')
    manager.unmount(save_changes=True)
```

#### 2. BaseImageHandler (`src/deployforge/core/base_handler.py`)

**Purpose**: Abstract base class defining handler interface

**Key Methods (all abstract):**
- `mount(mount_point)` - Mount image
- `unmount(save_changes)` - Unmount image
- `list_files(path)` - List files
- `add_file(source, destination)` - Add file
- `remove_file(path)` - Remove file
- `extract_file(source, destination)` - Extract file
- `get_info()` - Get image information

**When to extend**: Creating new image format handler

#### 3. Exceptions (`src/deployforge/core/exceptions.py`)

**Custom Exceptions:**
- `DeployForgeError` - Base exception
- `ImageNotFoundError` - Image file not found
- `UnsupportedFormatError` - Format not supported
- `MountError` - Mount/unmount failures
- `RegistryError` - Registry operation failures
- `DriverInjectionError` - Driver injection failures

### Enhanced Modules (World-Class Standard)

#### 4. gaming.py (443 lines) - Reference Implementation

**Quality Standard**: All enhanced modules follow this pattern

**Features:**
- Enums: `GamingProfile` (4 profiles)
- Dataclasses: `GamingOptimization` with to_dict()
- Main class: `GamingOptimizer` with full type hints
- Methods: Profile application, driver injection, runtime installation
- Comprehensive error handling and logging

#### 5. devenv.py (750 lines)

**Features**: 10 development profiles, IDE/language installation, cloud tools

#### 6. browsers.py (686 lines)

**Features**: 17+ browsers, enterprise policies, privacy configuration

#### 7. ui_customization.py (618 lines)

**Features**: 6 UI profiles, taskbar/Start Menu/File Explorer customization

#### 8. backup.py (650 lines)

**Features**: 5 backup profiles, System Restore/VSS/File History

#### 9. wizard.py (527 lines)

**Features**: 9 setup presets with hardware detection

### User Interface Modules

#### 10. gui_modern.py (Modern GUI - Primary Interface)

**Purpose**: Beautiful PyQt6 interface with 150+ features

**Key Classes:**
- `Theme`, `ThemeManager` - Dark/Light theme support
- `MainWindow` - Main application window
- `WelcomePage`, `BuildPage`, `ProfilesPage`, `AnalyzePage`, `SettingsPage`

**Features:**
- Drag-and-drop image loading
- 5 pages with smooth navigation
- 16 feature categories, 150+ customization options
- 6 profiles (Gaming, Developer, Enterprise, Student, Creator, Custom)
- Real-time progress monitoring
- Settings persistence

#### 11. cli.py (CLI Interface)

**Purpose**: Command-line interface using Click and Rich

**Commands:**
- `formats` - List supported formats
- `info` - Get image information
- `list` - List files in image
- `add/remove/extract` - File operations
- `mount/unmount` - Mount operations
- `compare` - Image comparison
- `gui` - Launch GUI

#### 12. api/main.py (REST API)

**Purpose**: FastAPI-based REST API with OpenAPI docs

**Endpoints:**
- `/images/*` - Image operations
- `/registry/*` - Registry operations
- `/drivers/*` - Driver injection
- `/batch/*` - Batch operations
- `/templates/*` - Template management

### Enterprise Modules

#### 13. batch.py - Batch Operations

**Purpose**: Parallel processing of multiple images

**Key Features:**
- ThreadPoolExecutor-based concurrency
- Progress tracking across all operations
- Error aggregation and reporting

#### 14. templates.py - Template System

**Purpose**: Reusable customization workflows

**Predefined Templates:**
- `GAMING_TEMPLATE`
- `WORKSTATION_TEMPLATE`
- `ENTERPRISE_TEMPLATE`

#### 15. audit.py - Audit Logging

**Purpose**: JSONL-based compliance logging

**Logs**: User, timestamp, operation, parameters, results

---

## Advanced Enterprise Modules

### Overview

DeployForge includes 8 major enterprise modules (5,500+ lines) providing advanced deployment capabilities. These modules support enterprise-scale Windows deployment with automation, testing, and integration features.

### 16. gui_modern.py - The PRIMARY Interface ⭐

**Location**: `src/deployforge/gui_modern.py`
**Lines**: 3,229 (LARGEST MODULE in the entire codebase)
**Status**: Production-ready, primary user-facing interface
**Complexity**: Highest
**Technology**: PyQt6
**Stability**: ⚠️ Active development

#### Purpose

Beautiful modern graphical interface with **150+ features** across **16 categories**. This is the **primary user-facing interface** for DeployForge, providing drag-and-drop image loading, comprehensive customization options, and real-time progress monitoring.

#### Architecture - 5-Page Navigation System

The GUI uses a `QStackedWidget` for smooth page transitions:

1. **WelcomePage** - Drag-and-drop image loading, recent files
2. **BuildPage** - 150+ feature checkboxes in 16 categories
3. **ProfilesPage** - 6 pre-configured profiles with auto-selection
4. **AnalyzePage** - Image analysis and comparison tools
5. **SettingsPage** - Configuration management with persistence

#### Key Classes

```python
class Theme:
    """Theme color definitions for Light and Dark modes"""
    LIGHT = {
        'background': '#FAFAFA',
        'surface': '#FFFFFF',
        'primary': '#0078D4',
        'text': '#1F1F1F',
        # ... 10+ color definitions
    }

    DARK = {
        'background': '#1E1E1E',
        'surface': '#252526',
        'primary': '#0078D4',
        'text': '#FFFFFF',
        # ... 10+ color definitions
    }

class ThemeManager:
    """Manages application theming and stylesheet generation"""

    def apply_theme(self, theme_name: str) -> None:
        """Apply theme to entire application"""

    def generate_stylesheet(self) -> str:
        """Generate QSS stylesheet from theme colors"""

class MainWindow(QMainWindow):
    """Main application window with sidebar navigation"""

    def __init__(self):
        """Initialize window, setup UI, load settings"""

    def create_sidebar(self) -> QWidget:
        """Create left sidebar with page navigation buttons"""

    def switch_page(self, page_index: int) -> None:
        """Switch to selected page with smooth transition"""

class WelcomePage(QWidget):
    """Welcome page with drag-and-drop image loading"""

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter for .wim/.esd/.iso files"""

    def dropEvent(self, event: QDropEvent):
        """Handle file drop and load image"""

    def load_image(self, path: Path) -> None:
        """Load image and switch to Build page"""

class BuildPage(QWidget):
    """Main feature selection page with 150+ checkboxes"""

    def __init__(self):
        """Initialize page and setup all 16 feature categories"""

    def _init_gaming_features(self) -> QWidget:
        """Initialize gaming features section (15 features)"""

    def _init_debloat_features(self) -> QWidget:
        """Initialize debloat features section (20 features)"""

    def _init_privacy_features(self) -> QWidget:
        """Initialize privacy features section (16 features)"""

    # ... 13 more _init_*_features() methods for other categories

class ProfilesPage(QWidget):
    """Pre-configured profile selection page"""

    profiles = {
        'Gaming': [27 features],
        'Developer': [28 features],
        'Enterprise': [24 features],
        'Student': [23 features],
        'Creator': [27 features],
        'Custom': [user-defined]
    }

    def apply_profile(self, profile_name: str) -> None:
        """Auto-select features for chosen profile"""

class AnalyzePage(QWidget):
    """Image analysis and comparison tools"""

    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze image and show statistics"""

class SettingsPage(QWidget):
    """Settings management with QSettings persistence"""

    def save_settings(self) -> None:
        """Save settings to persistent storage"""
```

#### 16 Feature Categories (150+ Total Features)

| Category | Count | Examples |
|----------|-------|----------|
| 🎮 Gaming | 15 | NVIDIA/AMD drivers, DirectX, Game Mode, Discord |
| 🗑️ Debloat | 20 | Remove Xbox, Teams, OneDrive, Cortana |
| 🔒 Privacy | 16 | Disable telemetry, tracking, Bing, ads |
| 🎨 Visual | 19 | Classic menus, dark mode, taskbar tweaks |
| 💻 Developer | 19 | Python, Node.js, Java, .NET, PowerShell 7 |
| 🏢 Enterprise | 12 | Security policies, domain prep, AppLocker |
| 🌐 Browsers | 6 | Firefox, Chrome, Brave, Edge, Opera, Vivaldi |
| 📝 Office | 10 | Office, LibreOffice, Teams, Zoom, Slack |
| 🎨 Creative | 10 | OBS, GIMP, Blender, DaVinci Resolve |
| 🎮 Gaming Platforms | 7 | Steam, Epic, GOG, Origin, Battle.net |
| 🔧 Utilities | 10 | 7-Zip, PowerToys, Everything, ShareX |
| ⚡ Performance | 10 | Disable services, indexing, Superfetch |
| 🔌 Services | 8 | Windows Update, Print Spooler, diagnostics |
| 🔋 Power | 5 | Ultimate Performance plan, throttling |
| 📁 File Explorer | 7 | Quick Access, libraries, OneDrive removal |
| 🌐 Network | 13 | DNS, firewall, IPv6, Remote Desktop |

#### 6 Pre-Configured Profiles

1. **Gaming Profile** (27 features)
   - Steam, Epic Games, GOG Galaxy
   - NVIDIA/AMD drivers, DirectX
   - Ultimate Performance power plan
   - Game Mode, DVR optimization
   - Debloat gaming-unfriendly apps

2. **Developer Profile** (28 features)
   - Python, Node.js, Java, .NET SDK
   - 4 browsers (Firefox, Chrome, Brave, Edge)
   - PowerToys, Windows Terminal
   - WSL2, Hyper-V, Docker support
   - Git, development tools

3. **Enterprise Profile** (24 features)
   - Security hardening, firewall rules
   - Domain join preparation
   - Office 365, Teams, OneDrive
   - Compliance and audit logging
   - AppLocker, Credential Guard

4. **Student Profile** (23 features)
   - Office suite, browsers
   - Privacy controls (moderate)
   - VLC, Spotify, Discord
   - Efficient power settings
   - Cloud storage (OneDrive)

5. **Creator Profile** (27 features)
   - 10 creative applications
   - GPU optimization
   - Ultimate Performance
   - Large file handling
   - Color management

6. **Custom Profile**
   - User-defined feature selection
   - Save/load custom configurations

#### Theme System

**Light Theme**:
```python
background: '#FAFAFA'      # Off-white background
surface: '#FFFFFF'         # Pure white panels
primary: '#0078D4'         # Microsoft blue
text: '#1F1F1F'           # Nearly black text
border: '#E0E0E0'         # Light gray borders
```

**Dark Theme**:
```python
background: '#1E1E1E'      # Dark gray background
surface: '#252526'         # Slightly lighter panels
primary: '#0078D4'         # Same blue (consistency)
text: '#FFFFFF'           # White text
border: '#3E3E42'         # Dark gray borders
```

#### Settings Persistence

Uses `QSettings` for automatic persistence:
```python
settings = QSettings('DeployForge', 'ModernGUI')

# Automatically saves:
- Theme preference (Light/Dark)
- Window geometry and position
- Recent file list
- Last used profile
- Feature selections
```

#### Drag-and-Drop Implementation

```python
def dragEnterEvent(self, event: QDragEnterEvent):
    """Accept .wim, .esd, .iso files"""
    if event.mimeData().hasUrls():
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in ['.wim', '.esd', '.iso']:
                event.acceptProposedAction()
                return

def dropEvent(self, event: QDropEvent):
    """Load dropped image file"""
    for url in event.mimeData().urls():
        path = Path(url.toLocalFile())
        if path.suffix.lower() in ['.wim', '.esd', '.iso']:
            self.load_image(path)
            break
```

#### Modification Guide

**Adding a Feature Checkbox**:
```python
# In BuildPage._init_gaming_features()
self.feature_checkboxes['new_gaming_feature'] = QCheckBox("New Gaming Feature")
self.feature_checkboxes['new_gaming_feature'].setToolTip(
    "Description of what this feature does"
)
gaming_layout.addWidget(self.feature_checkboxes['new_gaming_feature'])
```

**Adding a Profile**:
```python
# In ProfilesPage.__init__()
self.profiles['NewProfile'] = [
    'feature1',
    'feature2',
    'feature3'
]

# Add profile button
new_profile_btn = self.create_profile_card(
    "New Profile",
    "Description",
    "icon.png",
    lambda: self.apply_profile('NewProfile')
)
```

**Modifying Theme**:
```python
# In Theme.LIGHT or Theme.DARK
'new_color': '#HEXCODE',
'another_color': '#HEXCODE'
```

#### Dependencies

- **PyQt6** - GUI framework
- **deployforge.cli.profiles** - Profile backend
- **deployforge.cli.analyzer** - Analysis tools
- **deployforge.config_manager** - Configuration

#### Usage Example

```python
from deployforge.gui_modern import main

if __name__ == '__main__':
    main()  # Launch GUI application
```

**Location**: `src/deployforge/gui_modern.py:1-3229`

---

### 17. testing.py - Automated Testing & Validation

**Lines**: 823 (2nd largest module)
**Category**: Enterprise Testing
**Status**: Production-ready

#### Purpose

Comprehensive automated testing and validation for Windows images including integrity checks, VM-based bootability testing, driver signature validation, and performance metrics.

#### Features

- **Image Integrity**: SHA256 checksums, signature validation
- **VM-Based Testing**: Boot images in Hyper-V, VirtualBox, VMware, QEMU
- **Driver Validation**: Signature checks, compatibility testing
- **Compliance Verification**: Update compliance, security baseline checks
- **Performance Metrics**: Boot time, resource usage, benchmark scores
- **Automated Reporting**: JSON/HTML test reports with detailed results

#### Supported Hypervisors

- **Hyper-V** (Windows) - Native Windows virtualization
- **VirtualBox** (Cross-platform) - Free, widely used
- **VMware** Workstation/Player - Enterprise standard
- **QEMU/KVM** (Linux) - Open-source, high performance

#### Key Classes

```python
class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"

class Hypervisor(Enum):
    """Supported hypervisors"""
    HYPER_V = "Hyper-V"
    VIRTUALBOX = "VirtualBox"
    VMWARE = "VMware"
    QEMU = "QEMU"

@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    status: TestStatus
    duration: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

class ImageValidator:
    """Image integrity and structure validation"""

    def validate_integrity(self, image_path: Path) -> TestResult:
        """Validate file integrity with checksums"""

    def validate_structure(self, image_path: Path) -> TestResult:
        """Validate WIM/ESD structure and metadata"""

class VMTester:
    """VM-based bootability testing"""

    def __init__(self, image_path: Path, hypervisor: Hypervisor):
        """Initialize with image and hypervisor"""

    def create_vm(self) -> str:
        """Create temporary VM for testing"""

    def test_boot(self, timeout: int = 300) -> TestResult:
        """Test if image boots successfully"""

    def cleanup_vm(self) -> None:
        """Remove temporary VM and artifacts"""

class TestRunner:
    """Orchestrates test execution"""

    def run_all_tests(self, image_path: Path) -> List[TestResult]:
        """Run complete test suite"""

    def run_selective_tests(self, tests: List[str]) -> List[TestResult]:
        """Run specific tests only"""

class TestReport:
    """Generate test reports"""

    def generate_json(self, results: List[TestResult]) -> str:
        """Generate JSON report"""

    def generate_html(self, results: List[TestResult]) -> str:
        """Generate HTML report"""
```

#### Usage Example

```python
from deployforge.testing import ImageValidator, VMTester, Hypervisor
from pathlib import Path

# Validate integrity
validator = ImageValidator()
integrity_result = validator.validate_integrity(Path('install.wim'))
structure_result = validator.validate_structure(Path('install.wim'))

# Boot test in VM
tester = VMTester(Path('install.wim'), Hypervisor.VIRTUALBOX)
boot_result = tester.test_boot(timeout=300)

if boot_result.status == TestStatus.PASSED:
    print("Image boots successfully!")
else:
    print(f"Boot test failed: {boot_result.message}")

tester.cleanup_vm()
```

**Location**: `src/deployforge/testing.py:1-823`

---

### 18. integration.py - MDT/SCCM Enterprise Integration

**Lines**: 786 (3rd largest module)
**Category**: Enterprise Integration
**Status**: Production-ready

#### Purpose

Integration with Microsoft Deployment Toolkit (MDT) and System Center Configuration Manager (SCCM) for enterprise-scale Windows deployment.

#### MDT Features

- **Deployment Share Management**: Create, configure, update shares
- **Task Sequence Creation**: Standard/custom task sequences
- **Application Management**: Import, configure, bundle applications
- **Driver Package Management**: Import and organize drivers
- **Boot Image Generation**: Custom WinPE boot images
- **Selection Profiles**: Filter content for deployments

#### SCCM Features

- **Package Creation**: Application and OS packages
- **Application Management**: Application deployment
- **OS Image Deployment**: Distribute images to DPs
- **Distribution Point Management**: Content distribution
- **Task Sequence Deployment**: Deploy to collections

#### Key Classes

```python
class TaskSequenceType(Enum):
    """MDT/SCCM task sequence types"""
    STANDARD_CLIENT = "Standard Client Task Sequence"
    CUSTOM = "Custom Task Sequence"
    REPLACE_COMPUTER = "Replace Computer"
    REFRESH_COMPUTER = "Refresh Computer"
    BARE_METAL = "Bare Metal Deployment"

class MDTManager:
    """MDT deployment share operations"""

    def create_share(self, path: Path, name: str) -> None:
        """Create new MDT deployment share"""

    def import_os_image(self, wim_path: Path, name: str) -> str:
        """Import OS image to deployment share"""

    def import_application(self, app: MDTApplication) -> str:
        """Import application to deployment share"""

class TaskSequenceBuilder:
    """Build MDT/SCCM task sequences"""

    def create_standard_client(self, name: str, os_id: str) -> str:
        """Create standard client deployment task sequence"""

    def add_step(self, sequence_id: str, step_type: str, config: Dict) -> None:
        """Add step to task sequence"""

class SCCMPackageCreator:
    """Create SCCM packages"""

    def create_application_package(self, app_path: Path) -> str:
        """Create SCCM application package"""

    def create_os_package(self, image_path: Path) -> str:
        """Create SCCM OS image package"""
```

#### Usage Example

```python
from deployforge.integration import MDTManager, TaskSequenceBuilder
from pathlib import Path

# Create MDT deployment share
mdt = MDTManager()
mdt.create_share(Path('D:\\DeploymentShare'), 'Production')

# Import OS image
os_id = mdt.import_os_image(
    Path('install.wim'),
    'Windows 11 Enterprise'
)

# Create task sequence
builder = TaskSequenceBuilder(mdt)
ts_id = builder.create_standard_client(
    name='Win11 Enterprise Deployment',
    os_id=os_id
)

# Add custom step
builder.add_step(ts_id, 'InstallApplication', {
    'application_name': 'Microsoft Office 365'
})
```

**Location**: `src/deployforge/integration.py:1-786`

---

### 19. iac.py - Infrastructure as Code

**Lines**: 770 (4th largest module)
**Category**: Enterprise Automation
**Status**: Production-ready

#### Purpose

Complete build automation using YAML/JSON deployment definitions. Enables declarative infrastructure as code for Windows image builds with multi-stage pipelines.

#### Features

- **YAML/JSON Configurations**: Declarative build definitions
- **Template Variables**: Variable substitution and interpolation
- **Multi-Stage Builds**: 12 predefined build stages
- **Schema Validation**: Validate configurations before execution
- **CLI Integration**: Run builds from command line
- **Conditional Logic**: If/else conditions in builds
- **Error Handling**: Comprehensive error recovery

#### Build Stages

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

#### Configuration Example

```yaml
# deploy.yaml
version: "1.0"
name: "Enterprise Windows 11 Build"
image: "install.wim"
index: 1
output: "Win11_Enterprise_Custom.wim"

variables:
  company: "Acme Corporation"
  domain: "acme.local"
  timezone: "Pacific Standard Time"

stages:
  - name: partitions
    action: create
    type: uefi_gpt
    size: 50GB
    recovery: true

  - name: base
    profile: enterprise
    debloat:
      - Xbox
      - Teams
      - OneDrive
    privacy: enhanced

  - name: drivers
    packages:
      - "drivers/nvidia/*.inf"
      - "drivers/intel_chipset/*.inf"
    force_unsigned: false

  - name: updates
    source: "updates/"
    latest_cumulative: true
    dotnet_updates: true

  - name: applications
    install:
      - name: "Microsoft Office 365"
        source: "apps/Office365.exe"
      - name: "7-Zip"
        source: "apps/7z-installer.msi"

  - name: security
    level: high
    firewall: enabled
    defender: configured
    bitlocker_prep: true

  - name: certificates
    import:
      - "certs/${company}_root_ca.cer"
      - "certs/${company}_intermediate.cer"

  - name: gpo
    apply:
      - "policies/baseline_security.xml"
      - "policies/corporate_settings.xml"

  - name: customization
    registry:
      - key: "HKLM\\SOFTWARE\\${company}"
        value: "Deployed"
        data: "true"
        type: REG_SZ
    wallpaper: "branding/wallpaper.jpg"
    oem_info:
      manufacturer: "${company}"
      support_url: "https://support.${domain}"

  - name: finalize
    validate: true
    optimize: true
    cleanup_temp: true
```

#### Usage Example

```python
from deployforge.iac import IaCRunner
from pathlib import Path

# Load and execute IaC configuration
runner = IaCRunner(Path('deploy.yaml'))

# Validate configuration
if runner.validate():
    # Execute all stages
    result = runner.execute_all_stages()

    # Generate report
    runner.generate_report(Path('build_report.txt'))

    print(f"Build completed: {result.successful_stages}/{result.total_stages} stages")
else:
    print("Configuration validation failed")
```

**Location**: `src/deployforge/iac.py:1-770`

---

### 20. scheduler.py - Job Scheduling & Queue Management

**Lines**: 716
**Category**: Enterprise Automation
**Status**: Production-ready

#### Purpose

Cron-based job scheduling and queue management for automated Windows image builds.

#### Features

- **Cron Scheduling**: Standard cron syntax (e.g., `0 2 * * *`)
- **Job Queue**: Priority-based queue (LOW, NORMAL, HIGH, URGENT)
- **Background Execution**: Non-blocking background tasks
- **Job Tracking**: Real-time status monitoring
- **Retry Logic**: Exponential backoff for failed jobs
- **Notifications**: Email and webhook notifications
- **Persistent Storage**: JSON/SQLite job history

#### Usage Example

```python
from deployforge.scheduler import JobScheduler, JobPriority
from pathlib import Path

scheduler = JobScheduler()

# Schedule nightly build at 2 AM
job = scheduler.schedule_build(
    image_path=Path('install.wim'),
    config={'profile': 'enterprise'},
    schedule='0 2 * * *',  # 2 AM daily
    priority=JobPriority.HIGH,
    retry_count=3,
    notify_email='admin@company.com',
    notify_webhook='https://hooks.slack.com/...'
)

print(f"Job scheduled: {job.id}")

# Monitor job status
status = scheduler.get_job_status(job.id)
print(f"Status: {status}")
```

**Location**: `src/deployforge/scheduler.py:1-716`

---

### 21. versioning.py - Version Control for Images

**Lines**: 689
**Category**: Enterprise Management
**Status**: Production-ready

#### Purpose

Git-like version control system for Windows images with commit history, branching, and rollback capabilities.

#### Features

- **Version History**: Track all image modifications
- **Commit/Checkout**: Git-like workflow
- **Tagging**: Version tags (v1.0.0, production, etc.)
- **Branching**: Maintain variants (gaming-branch, enterprise-branch)
- **Diff Engine**: Compare versions and generate changelogs
- **Rollback**: Restore previous versions
- **SHA256 Tracking**: Integrity verification

#### Usage Example

```python
from deployforge.versioning import ImageRepository
from pathlib import Path

repo = ImageRepository(Path('/images/repo'))

# Initialize repository
repo.init()

# Commit an image
commit = repo.commit(
    image_path=Path('Win11_Custom.wim'),
    message='Initial Windows 11 customization with gaming optimizations',
    version='1.0.0',
    tags=['production', 'baseline', 'Q4-2025']
)

# Create branch for variant
repo.create_branch('gaming-variant')

# List history
history = repo.log(limit=10)
for commit in history:
    print(f"{commit.version}: {commit.message}")

# Checkout previous version
repo.checkout('v1.0.0')

# Diff between versions
diff = repo.diff('v1.0.0', 'v1.1.0')
print(f"Changes: {len(diff.files_changed)} files")
```

**Location**: `src/deployforge/versioning.py:1-689`

---

### 22. gpo.py - Group Policy Objects Management

**Lines**: 658
**Category**: Enterprise Configuration
**Status**: Production-ready

#### Purpose

Group Policy Objects (GPO) management and deployment for enterprise Windows images.

#### Features

- GPO creation and modification
- Policy import/export (XML format)
- Template-based policies
- Registry-based GPO settings
- Administrative templates (ADMX)
- Compliance checking
- Policy reporting

**Location**: `src/deployforge/gpo.py:1-658`

---

### 23. certificates.py - Certificate Management

**Lines**: 622
**Category**: Enterprise Security
**Status**: Production-ready

#### Purpose

Certificate installation and management for trusted certificate stores in Windows images.

#### Features

- Certificate installation (Root, Intermediate, Personal stores)
- Trust store management
- Enterprise CA integration
- Certificate validation and verification
- CRL/OCSP configuration
- Auto-enrollment setup

#### Supported Formats

- .CER (DER/PEM)
- .PFX/.P12 (password-protected)
- .CRT
- .P7B (certificate chains)

**Location**: `src/deployforge/certificates.py:1-622`

---

## Complete Module Index

### All 54 Modules by Category

#### Core Infrastructure (3 modules, ~1,000 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| core/image_manager.py | ~400 | Factory and orchestration |
| core/base_handler.py | ~200 | Abstract handler interface |
| core/exceptions.py | ~200 | Custom exception hierarchy |

#### Format Handlers (5 modules, ~2,500 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| handlers/iso_handler.py | ~500 | ISO 9660 optical disc images |
| handlers/wim_handler.py | ~500 | Windows Imaging Format |
| handlers/esd_handler.py | ~400 | Electronic Software Download |
| handlers/ppkg_handler.py | ~400 | Provisioning packages |
| handlers/vhd_handler.py | ~500 | Virtual Hard Disk (VHD/VHDX) |

#### User Interfaces (4 modules, 4,433 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| **gui_modern.py** | **3,229** | **PRIMARY INTERFACE** - Modern PyQt6 GUI |
| cli.py | 480 | Command-line interface (Click + Rich) |
| api/main.py | ~400 | REST API (FastAPI) |
| gui.py + gui/main_window.py | 491 | Legacy GUI (deprecated) |

#### Enhanced Modules (9 modules, 5,185 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| devenv.py | 749 | Development environments (10 profiles) |
| browsers.py | 685 | Browser management (17+ browsers) |
| ui_customization.py | 618 | UI themes (6 profiles) |
| backup.py | 650 | Backup/recovery (5 profiles) |
| wizard.py | 527 | Setup wizard (9 presets) |
| portable.py | 613 | Portable applications (20+ catalog) |
| creative.py | 545 | Creative software suite |
| launchers.py | 399 | Gaming platforms (12+) |
| privacy_hardening.py | 397 | Privacy protection (4 levels) |
| gaming.py | 443 | Gaming optimization (REFERENCE) |

#### Enterprise Features (12 modules, 6,897 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| **testing.py** | 823 | Automated testing & VM validation |
| **integration.py** | 786 | MDT/SCCM enterprise integration |
| **iac.py** | 770 | Infrastructure as Code (YAML/JSON) |
| partitions.py | 720 | UEFI/GPT partitioning |
| **scheduler.py** | 716 | Job scheduling & queue management |
| **versioning.py** | 689 | Git-like version control for images |
| unattend.py | 675 | Answer file (unattend.xml) generation |
| **gpo.py** | 658 | Group Policy Objects management |
| languages.py | 654 | Multi-language (MUI) support |
| security.py | 642 | Security hardening & compliance |
| winpe.py | 639 | Windows PE customization |
| **certificates.py** | 622 | Certificate management & injection |

#### Automation & Integration (5 modules, 3,508 lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| automation.py | 677 | Ansible/Terraform integration |
| ai.py | 597 | AI-powered features |
| differential.py | 596 | Differential updates |
| containers.py | 585 | Container support |
| cloud.py | 573 | Cloud deployment (AWS/Azure/GCP) |

#### Utility Modules (16+ modules, 4,800+ lines)

| Module | Lines | Purpose |
|--------|-------|---------|
| config_manager.py | 569 | Configuration management |
| encryption.py | 560 | Image encryption (BitLocker) |
| applications.py | 525 | Application installation |
| optimizer.py | 482 | General optimization |
| rollback.py | 465 | Rollback capabilities |
| features.py | 444 | Feature flag management |
| network.py | 440 | Network configuration |
| debloat.py | 419 | Bloatware removal |
| feature_updates.py | 387 | Windows feature updates |
| sandbox.py | 361 | Windows Sandbox integration |
| remote.py | 354 | Remote storage (S3, Azure, HTTP) |
| comparison.py | 335 | Image comparison & diff |
| batch.py | 321 | Batch operations (parallel) |
| registry.py | 301 | Offline registry editing |
| templates.py | 299 | Template system |
| drivers.py | 286 | Driver injection (DISM) |
| performance.py | 228 | Performance monitoring |
| updates.py | 216 | Windows Update integration |
| themes.py | 211 | Windows theme management |
| cache.py | 192 | Caching layer (TTL) |
| config.py | 186 | YAML configuration |
| audit.py | 179 | JSONL audit logging |
| packages.py | 130 | Package management |

### Modules by Size (Top 20)

| Rank | Module | Lines | Category |
|------|--------|-------|----------|
| 1 | **gui_modern.py** | **3,229** | **User Interface (PRIMARY)** |
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

### Module Stability Guide

**🔒 Never Modify Without Deep Understanding**:
- `core/image_manager.py`
- `core/base_handler.py`
- `core/exceptions.py`

**⚠️ Careful Modification Required**:
- `handlers/*` - Format handlers
- `gui_modern.py` - Primary interface
- `cli.py` - Command-line interface
- `api/main.py` - REST API

**✅ Safe to Modify**:
- Enhanced modules (9 files)
- Feature modules
- Utility modules

**🚀 Actively Developed**:
- `gui_modern.py` - New features being added
- Enhanced modules - Continuous improvement
- Enterprise features - Enterprise adoption

### Quick Module Reference

**For AI Assistants**:
- **Complete catalog**: See `MODULE_REFERENCE.md`
- **API endpoints**: See `API_REFERENCE.md`
- **Code patterns**: Follow `gaming.py` standard

**For Users**:
- **GUI guide**: See `GUI_GUIDE.md` (to be created)
- **Enterprise guide**: See `ENTERPRISE_GUIDE.md` (to be created)
- **Quick start**: See `QUICK_START.md` (to be created)

---

## Common Tasks & Workflows

### Task 1: Adding a New Feature Module

**Steps:**

1. **Create the module** in `src/deployforge/new_feature.py`

```python
"""
New Feature Module

Brief description of what this module does.

Features:
- Feature 1
- Feature 2
- Feature 3
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FeatureProfile(Enum):
    """Profile types for this feature"""
    BASIC = "basic"
    ADVANCED = "advanced"

@dataclass
class FeatureConfig:
    """Configuration for the feature"""
    option1: bool = True
    option2: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'option1': self.option1,
            'option2': self.option2
        }

class FeatureOptimizer:
    """
    Main class for the feature.

    Example:
        optimizer = FeatureOptimizer(Path('install.wim'))
        optimizer.mount()
        optimizer.apply_profile(FeatureProfile.ADVANCED)
        optimizer.unmount(save_changes=True)
    """

    def __init__(self, image_path: Path, index: int = 1):
        """Initialize the optimizer."""
        self.image_path = image_path
        self.index = index
        logger.info(f"Initialized FeatureOptimizer for {image_path}")

    def apply_profile(self, profile: FeatureProfile) -> None:
        """Apply predefined profile."""
        logger.info(f"Applying profile: {profile.value}")
        # Implementation
```

2. **Add tests** in `tests/test_new_feature.py`

3. **Update documentation** if user-facing

4. **Run quality checks** (Black, Flake8, MyPy, tests)

5. **Commit** with descriptive message

### Task 2: Adding a New Image Format Handler

**Steps:**

1. **Create handler** in `src/deployforge/handlers/new_format_handler.py`

```python
from deployforge.core.base_handler import BaseImageHandler
from pathlib import Path
from typing import List, Dict, Any, Optional

class NewFormatHandler(BaseImageHandler):
    """Handler for NEW format images."""

    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount NEW format image."""
        # Implementation
        self.is_mounted = True
        return self.mount_point

    def unmount(self, save_changes: bool = False) -> None:
        """Unmount NEW format image."""
        # Implementation
        self.is_mounted = False

    # Implement all abstract methods from BaseImageHandler
```

2. **Register handler** in `src/deployforge/handlers/__init__.py`

```python
from deployforge.core.image_manager import ImageManager
from deployforge.handlers.new_format_handler import NewFormatHandler

ImageManager.register_handler('.new', NewFormatHandler)
```

3. **Add tests** for the new handler

4. **Update documentation** (README.md, format table)

### Task 3: Enhancing an Existing Module to World-Class Standard

**Reference**: See `MODULES_6-9_ENHANCEMENT_COMPLETE.md` for detailed examples

**Target**: Transform module from ~80 lines to 400-750 lines following gaming.py standard

**Process:**

1. **Analyze current module** - Understand existing functionality
2. **Design enhancement** - Plan profiles, features, structure
3. **Implement enums** - Add profile enumerations
4. **Implement dataclasses** - Add configuration classes with to_dict()
5. **Expand main class** - Add comprehensive methods
6. **Add type hints** - Full type coverage
7. **Write docstrings** - Google-style, comprehensive
8. **Add error handling** - Robust try/except blocks
9. **Add logging** - Comprehensive logging
10. **Test thoroughly** - Ensure functionality

**Example transformation**:
```
Before: backup.py (79 lines)
After:  backup.py (650 lines, +723%)
- Added 5 backup profiles
- Added BackupProfile enum
- Added BackupConfig dataclass
- Added 15+ methods
- Added comprehensive error handling
```

### Task 4: Modifying the GUI

**Important**: `gui_modern.py` is the primary interface (v1.5.0+)

**Key areas:**

1. **Adding a feature checkbox** in BuildPage
2. **Adding a profile** in ProfilesPage
3. **Modifying theme** in Theme/ThemeManager classes
4. **Adding a page** to QStackedWidget

**Example - Adding a feature:**

```python
# In BuildPage._init_gaming_features()
self.feature_checkboxes['new_feature'] = QCheckBox("New Feature")
self.feature_checkboxes['new_feature'].setToolTip("Description of feature")
gaming_layout.addWidget(self.feature_checkboxes['new_feature'])
```

### Task 5: Running Tests and Fixing Issues

```bash
# 1. Run full test suite
pytest -v

# 2. Run with coverage
pytest --cov=deployforge --cov-report=html

# 3. Check coverage report
# Open htmlcov/index.html

# 4. Fix failing tests
# - Read error messages carefully
# - Check mocking is correct
# - Verify test expectations

# 5. Run quality checks
black src/deployforge
flake8 src/deployforge
mypy src/deployforge --ignore-missing-imports

# 6. Security scan
bandit -r src/deployforge
```

---

## Git Workflow & Branching

### Branch Naming Convention

- **Main branch**: `main` (production-ready code)
- **Development branch**: `develop` (integration branch)
- **Feature branches**: `feature/feature-name`
- **Bug fix branches**: `fix/bug-name`
- **Claude branches**: `claude/claude-md-*` or `claude/continue-work-*`

### Current Branch Context

**Active Branch**: `claude/claude-md-mhzk2bzz0fxu6e7e-017MDdj1B7nJvA3x9e8RGmMV`

**Important**: All development should occur on this branch until work is complete.

### Git Operations

#### Making Commits

```bash
# 1. Stage changes
git add <files>

# 2. Commit with conventional commit message
git commit -m "feat: add new feature

Detailed description of changes.

- Change 1
- Change 2
"

# 3. Push to branch (with retry on network errors)
git push -u origin claude/claude-md-mhzk2bzz0fxu6e7e-017MDdj1B7nJvA3x9e8RGmMV
```

#### Creating Pull Requests

When work is complete:

1. **Ensure all tests pass**
2. **Update documentation** (README.md, CHANGELOG.md if needed)
3. **Push to branch**
4. **Create PR** with:
   - Clear title describing changes
   - Summary of what was added/modified
   - Reference to any issues
   - Test plan

**PR Format:**
```markdown
## Summary
- Feature 1 implemented
- Feature 2 implemented
- Bug fix applied

## Changes
- File 1: Description
- File 2: Description

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Issues
Closes #123
```

### Git Best Practices for AI Assistants

1. **Always check git status before committing**
   ```bash
   git status
   ```

2. **Review diff before committing**
   ```bash
   git diff
   ```

3. **Only commit when explicitly requested by user**

4. **Use descriptive commit messages**

5. **Never force push to main/master**

6. **Always push to the correct Claude branch**

---

## Important Context

### Version History

- **v1.7.0** (Current): Modules 6-9 enhanced (+1,408 lines)
- **v1.6.0**: Modules 1-5 enhanced (+3,058 lines)
- **v1.5.0**: 150+ features, modern GUI (3x feature expansion)
- **v0.3.0**: UEFI/GPT, WinPE, answer files, multi-language
- **v0.2.0**: Enterprise features (GUI, API, batch, etc.)
- **v0.1.0**: Initial release (core architecture, CLI)

### Recent Major Changes (v1.7.0)

**Modules Enhanced (6-9):**
1. `ui_customization.py`: 78 → 618 lines (+692%)
2. `backup.py`: 79 → 650 lines (+723%)
3. `wizard.py`: 74 → 527 lines (+612%)
4. `portable.py`: 64 → 613 lines (+858%)

**Total Enhancement Impact:**
- **+4,466 lines** across all 9 modules
- **719 → 5,185 lines** total (+621% growth)
- 23 Enums, 12 Dataclasses, 101 Methods
- All modules meet world-class gaming.py standard

### Platform-Specific Tools

**Windows:**
- DISM (built-in) for WIM/ESD
- PowerShell for VHD/VHDX
- reg.exe for registry

**Linux:**
- wimlib-imagex for WIM/ESD
- qemu-nbd or libguestfs for VHD/VHDX
- mount for operations

**macOS:**
- wimlib for WIM/ESD
- Limited VHD support

### Dependencies

**Core (11):**
- click, rich, pyyaml, pycdlib, xmltodict
- fastapi, uvicorn, pydantic
- psutil, requests, PyQt6

**Optional:**
- boto3 (AWS S3), azure-storage-blob (Azure)

**Dev (8):**
- pytest, pytest-cov, black, flake8, mypy
- safety, bandit, sphinx

### CI/CD Pipeline

**GitHub Actions:**
1. **CI** (`.github/workflows/ci.yml`)
   - Multi-platform: Ubuntu, Windows, macOS
   - Multi-version: Python 3.9-3.12
   - Linting, type checking, security scanning
   - Test execution with coverage

2. **Docker** (`.github/workflows/docker.yml`)
   - Multi-arch builds (amd64, arm64)

3. **Release** (`.github/workflows/release.yml`)
   - PyPI publishing on version tags

### Performance Considerations

1. **Large Images**: Use streaming operations
2. **Batch Processing**: Leverage parallel processing
3. **Memory**: Implement proper cleanup and context managers
4. **Caching**: Use cache layer for repeated operations

### Security Considerations

1. **Audit Logging**: All operations logged
2. **Input Validation**: Path traversal prevention
3. **Code Scanning**: Bandit in CI/CD
4. **Dependency Scanning**: Safety checks
5. **Least Privilege**: Minimal required permissions

### Documentation Standards

**When to Update Documentation:**

1. **User-facing changes**: Update README.md
2. **Breaking changes**: Update CHANGELOG.md
3. **New features**: Add to feature list
4. **Architecture changes**: Update docs/architecture.md
5. **Security changes**: Update docs/security.md

**Documentation Files to Keep in Sync:**
- README.md (main documentation)
- CHANGELOG.md (version history)
- pyproject.toml (version number)
- `__init__.py` (version number)

### Common Pitfalls to Avoid

1. **Don't modify core modules without deep understanding**
   - `core/image_manager.py`
   - `core/base_handler.py`
   - `core/exceptions.py`

2. **Don't use print()** - Always use logger

3. **Don't skip type hints** - Required for all functions

4. **Don't commit without tests** - Maintain coverage

5. **Don't break backward compatibility** - Follow semantic versioning

6. **Don't use relative imports** - Use absolute imports from `deployforge`

7. **Don't hardcode paths** - Use Path objects and configuration

8. **Don't ignore exceptions** - Always log and handle properly

### When to Ask for Clarification

As an AI assistant, ask the user for clarification when:

1. **Ambiguous requirements** - Multiple valid approaches exist
2. **Architecture decisions** - Significant structural changes
3. **Breaking changes** - Changes affecting backward compatibility
4. **External dependencies** - Adding new dependencies
5. **Security implications** - Security-sensitive changes
6. **Performance tradeoffs** - Optimization choices

### Resources for Learning More

1. **Code Examples**: See `examples/` directory
2. **Architecture**: Read `docs/architecture.md` (900+ lines)
3. **Security**: Read `docs/security.md` (500+ lines)
4. **Module Enhancements**: Read `MODULES_6-9_ENHANCEMENT_COMPLETE.md`
5. **Feature Expansion**: Read `GUI_ENHANCEMENT_SUMMARY.md`

---

## Quick Reference

### File Locations

| What | Where |
|------|-------|
| Core architecture | `src/deployforge/core/` |
| Image handlers | `src/deployforge/handlers/` |
| Enhanced modules | `src/deployforge/{devenv,browsers,creative,privacy_hardening,launchers,ui_customization,backup,wizard,portable}.py` |
| Modern GUI | `src/deployforge/gui_modern.py` |
| CLI | `src/deployforge/cli.py` |
| API | `src/deployforge/api/main.py` |
| Tests | `tests/` |
| Documentation | `docs/` and `*.md` files |
| Examples | `examples/` |
| Configuration | `pyproject.toml`, `deployforge.yaml.example` |
| CI/CD | `.github/workflows/` |

### Command Reference

```bash
# Development
pip install -e ".[dev]"          # Install in dev mode
black src/deployforge            # Format code
flake8 src/deployforge           # Lint code
mypy src/deployforge             # Type check
pytest                           # Run tests
pytest --cov=deployforge         # Run tests with coverage
bandit -r src/deployforge        # Security scan

# Running
python -m deployforge.gui_modern # Launch modern GUI
deployforge --help               # CLI help
python -m deployforge.api.main   # Start API server

# Git
git status                       # Check status
git add <files>                  # Stage changes
git commit -m "type: message"    # Commit
git push -u origin <branch>      # Push
```

### Key Patterns to Remember

1. **Enums for options**: Use Enum classes for profile types
2. **Dataclasses for config**: Use dataclass with to_dict()
3. **Type hints everywhere**: Never skip type annotations
4. **Google-style docstrings**: Comprehensive documentation
5. **Logger, not print()**: Always use logging
6. **Path objects**: Use pathlib.Path, not strings
7. **Context managers**: Implement `__enter__` and `__exit__`
8. **Error handling**: Try/except with specific exceptions
9. **Testing with mocks**: Mock external dependencies
10. **Follow gaming.py**: Reference implementation for quality

---

## Conclusion

DeployForge is a mature, well-architected project with clear conventions and high-quality standards. When working on this codebase:

1. **Follow established patterns** - Look at existing code for examples
2. **Maintain quality** - Don't lower the bar, raise it
3. **Test thoroughly** - Maintain high coverage
4. **Document comprehensively** - Future developers will thank you
5. **Ask when uncertain** - Better to clarify than to guess

**Remember**: The enhanced modules (devenv.py, browsers.py, etc.) and gaming.py represent the quality standard all code should meet. When in doubt, reference these files for structure, documentation, and implementation patterns.

---

**Version**: 1.7.0
**Generated**: 2025-11-15
**Maintained By**: AI Assistants and DeployForge Team
**Questions?**: See CONTRIBUTING.md or open an issue
