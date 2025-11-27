# DeployForge Architecture

Comprehensive technical documentation of DeployForge's architecture, design patterns, and implementation details.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Core Architecture](#core-architecture)
- [Design Patterns](#design-patterns)
- [Module Organization](#module-organization)
- [Data Flow](#data-flow)
- [Component Details](#component-details)
- [Extension Points](#extension-points)
- [Performance Considerations](#performance-considerations)
- [Security Architecture](#security-architecture)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interfaces Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   CLI    │  │ GUI PyQt6│  │ REST API │  │  Python  │   │
│  │  (Click) │  │  Modern  │  │ FastAPI  │  │   API    │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
└────────┼─────────────┼─────────────┼─────────────┼─────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  Core Business Logic Layer                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ImageManager (Factory)                   │  │
│  │         Creates and manages image handlers            │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────▼────────────────────────────────┐  │
│  │          BaseImageHandler (Abstract Base)             │  │
│  │      Defines interface for all image handlers         │  │
│  └─────┬──────┬──────┬──────┬──────┬──────┬────────────┘  │
└────────┼──────┼──────┼──────┼──────┼──────┼──────────────┘
         │      │      │      │      │      │
┌────────▼──────▼──────▼──────▼──────▼──────▼──────────────┐
│                   Image Handlers Layer                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ ISO  │ │ WIM  │ │ ESD  │ │ PPKG │ │ VHD  │ │VHDX │  │
│  │      │ │      │ │      │ │      │ │      │ │      │  │
│  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘  │
└─────┼────────┼────────┼────────┼────────┼────────┼───────┘
      │        │        │        │        │        │
┌─────▼────────▼────────▼────────▼────────▼────────▼───────┐
│              Platform Tools & Libraries Layer              │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │pycdlib │  │  DISM  │  │ wimlib │  │zipfile │  ...    │
│  │(Python)│  │(Win)   │  │(Linux) │  │(Python)│         │
│  └────────┘  └────────┘  └────────┘  └────────┘         │
└────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Separation of Concerns**: Clear boundaries between UI, business logic, and platform tools
2. **Abstraction**: Common interface for all image formats via BaseImageHandler
3. **Factory Pattern**: ImageManager creates appropriate handlers based on file extension
4. **Platform Independence**: Abstraction layer over platform-specific tools
5. **Modularity**: Features organized into independent, reusable modules

---

## Core Architecture

### Component Layers

#### 1. User Interface Layer

**Purpose**: Provide multiple ways for users to interact with DeployForge

**Components**:
- **CLI (cli.py)**: Command-line interface using Click and Rich
- **GUI (gui_modern.py)**: PyQt6 desktop application (3,200+ lines)
- **REST API (api/main.py)**: FastAPI web service
- **Python API**: Direct library usage via imports

**Responsibilities**:
- Accept user input
- Validate parameters
- Display results and progress
- Handle user errors gracefully

#### 2. Business Logic Layer

**Purpose**: Core image manipulation logic independent of UI

**Components**:
- **ImageManager**: Factory for creating handlers
- **BaseImageHandler**: Abstract interface all handlers implement
- **Feature Modules**: Self-contained feature implementations
- **Configuration**: Settings and profile management

**Responsibilities**:
- Image format detection
- Handler lifecycle management
- Operation orchestration
- Progress tracking
- Error handling

#### 3. Image Handlers Layer

**Purpose**: Format-specific image manipulation

**Components**:
- **ISOHandler**: ISO 9660 disk images (pycdlib)
- **WIMHandler**: Windows Imaging Format (DISM/wimlib)
- **ESDHandler**: Electronic Software Download (compressed WIM)
- **PPKGHandler**: Provisioning Packages (ZIP-based)
- **VHDHandler**: Virtual Hard Disk formats

**Responsibilities**:
- Mount/unmount operations
- File operations (add, remove, extract)
- Format-specific metadata handling
- Compression/decompression

#### 4. Platform Tools Layer

**Purpose**: Interface with OS-specific tools

**Components**:
- **pycdlib**: Pure Python ISO library
- **DISM**: Windows Deployment Image Servicing (Windows)
- **wimlib**: WIM library (Linux/macOS)
- **zipfile**: Python ZIP library
- **subprocess**: Execute external commands

---

## Design Patterns

### 1. Factory Pattern

**Implementation**: `ImageManager.get_handler()`

```python
class ImageManager:
    _handlers = {
        '.iso': ISOHandler,
        '.wim': WIMHandler,
        '.esd': ESDHandler,
        '.ppkg': PPKGHandler,
        '.vhd': VHDHandler,
        '.vhdx': VHDXHandler,
    }

    @classmethod
    def get_handler(cls, image_path: Path) -> BaseImageHandler:
        """Factory method to create appropriate handler."""
        ext = image_path.suffix.lower()
        handler_class = cls._handlers.get(ext)
        if not handler_class:
            raise UnsupportedFormatError(f"Format {ext} not supported")
        return handler_class(image_path)
```

**Benefits**:
- Centralized handler creation
- Easy to add new formats
- Client code doesn't need to know specific handler classes

### 2. Strategy Pattern

**Implementation**: Different handlers for different formats, same interface

```python
class BaseImageHandler(ABC):
    @abstractmethod
    def mount(self, mount_point: Optional[Path] = None) -> Path:
        """Mount image to filesystem."""
        pass

    @abstractmethod
    def unmount(self, save_changes: bool = False) -> None:
        """Unmount image."""
        pass
```

**Benefits**:
- Swap implementations at runtime
- Add new formats without changing existing code
- Consistent interface for all formats

### 3. Template Method Pattern

**Implementation**: BaseHandler provides common validation, subclasses implement specifics

```python
class BaseImageHandler:
    def validate_image(self) -> bool:
        """Template method with common validation."""
        if not self.image_path.exists():
            raise ImageNotFoundError(f"Image not found: {self.image_path}")

        # Subclass-specific validation
        return self._validate_format()

    @abstractmethod
    def _validate_format(self) -> bool:
        """Subclass implements format-specific validation."""
        pass
```

### 4. Context Manager Pattern

**Implementation**: Automatic cleanup with `with` statement

```python
class ImageManager:
    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context with cleanup."""
        if self.is_mounted:
            self.unmount(save_changes=False)
        return False
```

**Usage**:
```python
with ImageManager(Path('install.wim')) as manager:
    manager.mount()
    # Operations...
    # Automatic cleanup on exit
```

### 5. Observer Pattern

**Implementation**: Progress callbacks for long operations

```python
class ProgressTracker:
    def __init__(self):
        self.observers = []

    def attach(self, observer: Callable[[int, str], None]):
        """Attach progress observer."""
        self.observers.append(observer)

    def notify(self, progress: int, message: str):
        """Notify all observers."""
        for observer in self.observers:
            observer(progress, message)
```

### 6. Singleton Pattern

**Implementation**: Configuration manager (single instance)

```python
class ConfigurationManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

## Module Organization

### Directory Structure

```
src/deployforge/
├── core/                      # Core architecture (3 files, 500+ lines)
│   ├── __init__.py
│   ├── image_manager.py       # Factory and main entry point
│   ├── base_handler.py        # Abstract base for handlers
│   └── exceptions.py          # Custom exception hierarchy
│
├── handlers/                  # Image format handlers (6 files, 2,000+ lines)
│   ├── __init__.py
│   ├── iso_handler.py         # ISO 9660 (pycdlib)
│   ├── wim_handler.py         # WIM (DISM/wimlib)
│   ├── esd_handler.py         # ESD (compressed WIM)
│   ├── ppkg_handler.py        # PPKG (provisioning)
│   ├── vhd_handler.py         # VHD/VHDX (virtual disks)
│   └── base_handler.py        # Base handler implementation
│
├── Enhanced Modules (9 files, 5,185 lines) - World-Class Standard
│   ├── gaming.py              # Gaming optimization (443 lines, reference)
│   ├── devenv.py              # Dev environments (750 lines, 10 profiles)
│   ├── browsers.py            # Browsers (686 lines, 17+ browsers)
│   ├── creative.py            # Creative software (545 lines)
│   ├── privacy_hardening.py   # Privacy (397 lines, 4 levels)
│   ├── launchers.py           # Gaming platforms (399 lines, 12+)
│   ├── ui_customization.py    # UI themes (618 lines, 6 profiles)
│   ├── backup.py              # Backup/recovery (650 lines, 5 profiles)
│   ├── wizard.py              # Setup wizard (527 lines, 9 presets)
│   └── portable.py            # Portable apps (613 lines, 20+ catalog)
│
├── Feature Modules (25+ files, 10,000+ lines)
│   ├── debloat.py             # Bloatware removal
│   ├── registry.py            # Registry editing
│   ├── drivers.py             # Driver injection
│   ├── updates.py             # Windows Update
│   ├── templates.py           # Template system
│   ├── batch.py               # Batch operations
│   ├── comparison.py          # Image comparison
│   ├── performance.py         # Performance optimization
│   ├── security.py            # Security hardening
│   ├── network.py             # Network configuration
│   ├── packages.py            # Package management
│   ├── partitions.py          # UEFI/GPT partitioning
│   ├── unattend.py            # Answer file generation
│   ├── winpe.py               # WinPE customization
│   ├── languages.py           # Multi-language (MUI)
│   └── ...                    # And more
│
├── User Interfaces (3 interfaces)
│   ├── cli.py                 # Command-line (Click + Rich)
│   ├── gui_modern.py          # Desktop GUI (PyQt6, 3,200+ lines)
│   └── api/
│       └── main.py            # REST API (FastAPI)
│
└── utils/                     # Utilities
    ├── logger.py              # Logging configuration
    ├── progress.py            # Progress tracking
    └── config.py              # Configuration management
```

### Module Categories

1. **Core Infrastructure**: Foundation classes, exceptions, factory
2. **Format Handlers**: Image format-specific implementations
3. **Enhanced Modules**: World-class feature modules (gaming.py standard)
4. **Feature Modules**: Self-contained features
5. **User Interfaces**: CLI, GUI, API
6. **Utilities**: Cross-cutting concerns (logging, config, progress)

---

## Data Flow

### Image Customization Flow

```
User Request (CLI/GUI/API)
    ↓
Parameter Validation
    ↓
ImageManager.get_handler(path)
    ├─→ Detect format (.wim, .iso, etc.)
    ├─→ Create appropriate handler
    └─→ Return handler instance
        ↓
Handler.mount(mount_point)
    ├─→ Create mount point directory
    ├─→ Call platform tool (DISM/wimlib)
    ├─→ Verify mount successful
    └─→ Return mount point path
        ↓
Apply Customizations
    ├─→ Feature Module 1 (e.g., gaming.py)
    ├─→ Feature Module 2 (e.g., debloat.py)
    ├─→ Feature Module N
    │   ├─→ Modify registry
    │   ├─→ Add/remove files
    │   ├─→ Configure settings
    │   └─→ Report progress
    └─→ All customizations complete
        ↓
Handler.unmount(save_changes=True)
    ├─→ Call platform tool to commit
    ├─→ Cleanup mount point
    └─→ Verify completion
        ↓
Result (Success/Error)
    ├─→ Return to user
    └─→ Log operation
```

### Batch Processing Flow

```
Batch Request (multiple images)
    ↓
BatchOperation.add_operation() for each image
    ↓
BatchOperation.execute(parallel=True)
    ├─→ Create ThreadPoolExecutor
    ├─→ Submit all operations
    │   ├─→ Worker 1: Process image 1
    │   ├─→ Worker 2: Process image 2
    │   ├─→ Worker 3: Process image 3
    │   └─→ Worker N: Process image N
    │       ↓
    │   Each worker:
    │       ├─→ Load image
    │       ├─→ Mount
    │       ├─→ Apply customizations
    │       ├─→ Unmount
    │       └─→ Report result
    ├─→ Wait for all workers
    ├─→ Aggregate results
    └─→ Return summary
```

---

## Component Details

### ImageManager

**File**: `src/deployforge/core/image_manager.py`

**Purpose**: Central entry point and factory for image operations

**Key Methods**:
```python
- get_handler(image_path) -> BaseImageHandler
- supported_formats() -> List[str]
- register_handler(extension, handler_class)
```

**Design Decisions**:
- Registry-based handler system (extensible)
- Lazy handler instantiation
- Format detection by file extension
- Context manager support for auto-cleanup

### BaseImageHandler

**File**: `src/deployforge/core/base_handler.py`

**Purpose**: Define interface all handlers must implement

**Abstract Methods**:
```python
- mount(mount_point: Optional[Path]) -> Path
- unmount(save_changes: bool) -> None
- list_files(path: str) -> List[str]
- add_file(source: Path, destination: str) -> None
- remove_file(path: str) -> None
- extract_file(source: str, destination: Path) -> None
- get_info() -> Dict[str, Any]
```

**Concrete Methods** (shared by all handlers):
```python
- validate_image() -> bool
- __enter__() / __exit__()  # Context manager
```

### Enhanced Module Pattern (gaming.py Reference)

**Structure** (all 9 enhanced modules follow this):

```python
"""Module docstring with feature list."""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# 1. Enums for profiles/options
class GamingProfile(Enum):
    COMPETITIVE = "competitive"
    BALANCED = "balanced"
    QUALITY = "quality"
    STREAMING = "streaming"

# 2. Dataclasses for configuration
@dataclass
class GamingOptimization:
    enable_game_mode: bool = True
    gpu_scheduling: bool = True
    disable_fullscreen_opt: bool = False
    # ... more settings

    def to_dict(self) -> Dict[str, Any]:
        return {...}

# 3. Main optimizer/manager class
class GamingOptimizer:
    """Main class with comprehensive implementation."""

    def __init__(self, image_path: Path, index: int = 1):
        self.image_path = image_path
        self.index = index
        self.config = GamingOptimization()

    def apply_profile(self, profile: GamingProfile) -> None:
        """Apply predefined profile."""
        # Implementation

    def _private_helper(self) -> None:
        """Private methods prefixed with underscore."""
        pass
```

**All modules include**:
- Type hints on all functions
- Google-style docstrings
- Comprehensive error handling
- Progress callbacks
- Logging at appropriate levels
- `to_dict()` for serialization

---

## Extension Points

### Adding New Image Format

1. **Create handler** in `src/deployforge/handlers/`
2. **Extend BaseImageHandler**
3. **Implement all abstract methods**
4. **Register handler** in `__init__.py`

```python
# new_format_handler.py
from deployforge.core.base_handler import BaseImageHandler

class NewFormatHandler(BaseImageHandler):
    def mount(self, mount_point=None):
        # Implementation
        pass

    # Implement all required methods...

# handlers/__init__.py
from deployforge.core.image_manager import ImageManager
from .new_format_handler import NewFormatHandler

ImageManager.register_handler('.new', NewFormatHandler)
```

### Adding New Feature Module

1. **Create module** in `src/deployforge/`
2. **Follow gaming.py pattern** (Enum, Dataclass, Main class)
3. **Add comprehensive docstrings**
4. **Include error handling**
5. **Add tests** in `tests/`

### Adding New Profile

1. **Add to enum** in appropriate module
2. **Implement profile method**
3. **Document in README**
4. **Add to GUI** if applicable

---

## Performance Considerations

### Bottlenecks

1. **Disk I/O**: WIM operations are disk-intensive
   - Mitigation: Use SSD, batch operations

2. **Compression/Decompression**: CPU-intensive
   - Mitigation: Parallel processing where possible

3. **Large Images**: Memory usage for >10GB images
   - Mitigation: Streaming operations, chunked processing

### Optimizations

1. **Caching Layer**: Cache frequently accessed data
2. **Parallel Processing**: Use ThreadPoolExecutor for batch
3. **Lazy Loading**: Load resources only when needed
4. **Connection Pooling**: Reuse connections for API

### Benchmarks

Typical performance (SSD, i7 CPU, 16GB RAM):
- Mount WIM: 10-20 seconds
- Apply registry tweaks: 1-2 seconds
- Add file (100MB): 5-10 seconds
- Unmount with save: 30-60 seconds
- Full customization: 5-15 minutes

---

## Security Architecture

### Threat Model

**Threats Addressed**:
1. Path traversal attacks
2. Command injection
3. Privilege escalation
4. Data exposure
5. Code injection

### Mitigations

1. **Input Validation**: All paths validated
2. **Sandboxing**: Operations in isolated mount points
3. **Privilege Checks**: Verify required permissions
4. **Audit Logging**: All operations logged
5. **Safe Defaults**: Secure by default configuration

### Security Layers

```
┌─────────────────────────────────┐
│   Input Validation Layer        │  ← Validate all user input
├─────────────────────────────────┤
│   Authorization Layer           │  ← Check permissions
├─────────────────────────────────┤
│   Business Logic Layer          │  ← Execute operations
├─────────────────────────────────┤
│   Audit/Logging Layer          │  ← Log all operations
├─────────────────────────────────┤
│   Platform Security Layer       │  ← OS-level security
└─────────────────────────────────┘
```

---

## Future Architecture

### Planned Enhancements

1. **Plugin System**: Dynamic module loading
2. **Distributed Processing**: Process images across multiple machines
3. **Event-Driven**: Async operations with event bus
4. **Microservices**: Split into independent services
5. **Caching Service**: Redis/Memcached for state

### Web Platform Architecture (v2.0)

```
┌────────────────────────────────────────────┐
│         React/Vue Web Frontend             │
└────────────────┬───────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼───────────────────────────┐
│         FastAPI REST API Gateway           │
├────────────────────────────────────────────┤
│         Authentication/Authorization        │
└────────┬────────┬────────┬─────────────────┘
         │        │        │
    ┌────▼───┐ ┌─▼────┐ ┌─▼──────┐
    │ Image  │ │ User │ │ Queue  │
    │Service │ │Service│ │Service │
    └────┬───┘ └──┬───┘ └───┬────┘
         │        │         │
    ┌────▼────────▼─────────▼────┐
    │     PostgreSQL Database     │
    └─────────────────────────────┘
         │
    ┌────▼────┐
    │  Redis  │  (Caching/Sessions)
    └─────────┘
```

---

## Additional Resources

- **Code Examples**: See `examples/` directory
- **API Reference**: (Coming soon with Sphinx)
- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Version**: 0.3.0
**Last Updated**: 2025-11-23
**Maintained By**: DeployForge Team
