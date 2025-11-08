# DeployForge Architecture

## Overview

DeployForge is built with a modular, extensible architecture designed for enterprise-scale Windows image management.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
├─────────────────┬───────────────┬──────────────────────┤
│   CLI (Click)   │  GUI (PyQt6)  │   REST API (FastAPI) │
└────────┬────────┴───────┬───────┴──────────┬───────────┘
         │                │                  │
         └────────────────┼──────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │      ImageManager (Core)       │
         │   - Format detection           │
         │   - Handler delegation         │
         │   - Context management         │
         └────────────────┬───────────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                 │
         ▼                                 ▼
┌────────────────────┐          ┌──────────────────────┐
│  Format Handlers   │          │   Utilities & Tools  │
├────────────────────┤          ├──────────────────────┤
│ • ISOHandler       │          │ • Batch Operations   │
│ • WIMHandler       │          │ • Comparison         │
│ • ESDHandler       │          │ • Registry Editor    │
│ • PPKGHandler      │          │ • Driver Injector    │
│ • VHDHandler       │          │ • Update Integrator  │
└────────┬───────────┘          │ • Template Manager   │
         │                      │ • Cache Layer        │
         │                      │ • Audit Logger       │
         ▼                      │ • Performance Monitor│
┌────────────────────┐          └──────────────────────┘
│  Storage Backends  │
├────────────────────┤
│ • Local Filesystem │
│ • S3 Repository    │
│ • Azure Blob       │
│ • HTTP/HTTPS       │
└────────────────────┘
```

## Core Components

### 1. Image Manager

The central orchestrator that:
- Detects image format from file extension
- Selects appropriate handler
- Manages handler lifecycle
- Provides unified interface

```python
class ImageManager:
    _handlers: Dict[str, type] = {}

    @classmethod
    def register_handler(cls, extension: str, handler_class: type)

    def get_handler(cls, image_path: Path) -> BaseImageHandler

    def mount(self, mount_point: Optional[Path] = None) -> Path
    def unmount(self, save_changes: bool = False) -> None
    def list_files(self, path: str = "/") -> list
    def add_file(self, source: Path, destination: str) -> None
    def remove_file(self, path: str) -> None
    def extract_file(self, source: str, destination: Path) -> None
```

### 2. Base Handler

Abstract base class defining the handler interface:

```python
class BaseImageHandler(ABC):
    @abstractmethod
    def mount(self, mount_point: Optional[Path] = None) -> Path

    @abstractmethod
    def unmount(self, save_changes: bool = False) -> None

    @abstractmethod
    def list_files(self, path: str = "/") -> List[Dict[str, Any]]

    @abstractmethod
    def add_file(self, source: Path, destination: str) -> None

    @abstractmethod
    def remove_file(self, path: str) -> None

    @abstractmethod
    def extract_file(self, source: str, destination: Path) -> None

    @abstractmethod
    def get_info(self) -> Dict[str, Any]
```

### 3. Format Handlers

Specific implementations for each format:

#### ISO Handler
- Uses `pycdlib` for ISO 9660 support
- Direct file manipulation
- In-memory modifications

#### WIM Handler
- Uses DISM (Windows) or wimlib (Linux/macOS)
- Subprocess-based operations
- Index support for multi-image WIMs

#### VHD Handler
- PowerShell on Windows
- qemu-nbd or libguestfs on Linux
- Partition mounting support

## Data Flow

### Image Mounting Flow

```
User Request
    │
    ▼
ImageManager.mount()
    │
    ├─> Detect format
    │
    ├─> Get handler
    │
    ├─> Handler.mount()
    │   │
    │   ├─> Create mount point
    │   │
    │   ├─> Execute platform-specific mount
    │   │   (DISM/wimlib/pycdlib/etc)
    │   │
    │   └─> Return mount point
    │
    └─> Return to user
```

### Batch Operation Flow

```
Batch Request
    │
    ▼
BatchOperation.process_images()
    │
    ├─> ThreadPoolExecutor (max_workers=4)
    │   │
    │   ├─> Worker Thread 1 ─> Process Image 1
    │   │
    │   ├─> Worker Thread 2 ─> Process Image 2
    │   │
    │   ├─> Worker Thread 3 ─> Process Image 3
    │   │
    │   └─> Worker Thread 4 ─> Process Image 4
    │
    ├─> Collect results
    │
    └─> Return aggregated results
```

## Module Organization

```
deployforge/
├── __init__.py                 # Package initialization
├── cli.py                      # CLI interface (Click)
├── config.py                   # Configuration management
│
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── base_handler.py         # Abstract handler
│   ├── image_manager.py        # Main manager
│   └── exceptions.py           # Custom exceptions
│
├── handlers/                   # Format handlers
│   ├── __init__.py             # Handler registration
│   ├── iso_handler.py
│   ├── wim_handler.py
│   ├── esd_handler.py
│   ├── ppkg_handler.py
│   └── vhd_handler.py
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── logger.py               # Logging setup
│   └── progress.py             # Progress tracking
│
├── api/                        # REST API
│   ├── __init__.py
│   └── main.py                 # FastAPI application
│
├── gui/                        # Desktop GUI
│   ├── __init__.py
│   └── main_window.py          # PyQt6 interface
│
├── audit.py                    # Audit logging
├── batch.py                    # Batch operations
├── cache.py                    # Caching layer
├── comparison.py               # Image comparison
├── drivers.py                  # Driver injection
├── performance.py              # Performance monitoring
├── registry.py                 # Registry editing
├── remote.py                   # Remote repositories
├── templates.py                # Template system
└── updates.py                  # Windows updates
```

## Design Patterns

### 1. Strategy Pattern

Format handlers implement different strategies for the same operations:

```python
# All handlers implement the same interface
handler = ImageManager.get_handler(image_path)
handler.mount()  # Different implementation per format
```

### 2. Factory Pattern

ImageManager acts as a factory for creating handlers:

```python
handler = ImageManager.get_handler(image_path)
# Returns appropriate handler based on extension
```

### 3. Decorator Pattern

Performance monitoring and caching use decorators:

```python
@perf_monitor.measure("mount_image")
def mount(self):
    # Implementation
    pass

@cached(cache_instance, ttl=3600)
def get_info(self):
    # Implementation
    pass
```

### 4. Template Method Pattern

Base handler defines the template, subclasses implement details:

```python
class BaseImageHandler:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_mounted:
            self.unmount(save_changes=False)
```

### 5. Observer Pattern

Progress callbacks notify observers of operation progress:

```python
def operation(callback):
    for i in range(100):
        # Do work
        callback.update(i, 100)
```

## Extension Points

### Custom Handlers

Add support for new formats:

```python
from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.image_manager import ImageManager

class CustomHandler(BaseImageHandler):
    # Implement required methods
    pass

# Register
ImageManager.register_handler('.custom', CustomHandler)
```

### Custom Templates

Create reusable customization workflows:

```python
from deployforge.templates import CustomizationTemplate

template = CustomizationTemplate(name="Custom")
# Configure template
manager.save_template(template, "custom.json")
```

## Performance Considerations

### Memory Management

- Streaming for large files
- Lazy loading where possible
- Explicit cleanup in context managers
- Garbage collection hints

### Concurrency

- ThreadPoolExecutor for batch operations
- Configurable worker count
- Thread-safe operations
- Progress tracking per thread

### Caching

- File-based cache with TTL
- Decorator-based caching
- Automatic expiration
- Cache key hashing

## Security Architecture

### Defense Layers

1. **Input Validation**: Path traversal prevention
2. **Authentication**: API key/token support
3. **Authorization**: Role-based access control
4. **Audit Logging**: All operations logged
5. **Encryption**: Support for encrypted storage

### Audit Trail

Every operation creates an audit entry:

```python
audit.log_event(
    event_type="modify",
    action="add_file",
    image_path=image_path,
    user=current_user,
    success=True
)
```

## Scalability

### Horizontal Scaling

- REST API can be load-balanced
- Stateless operation design
- Distributed cache support (Redis)
- Queue-based job processing

### Vertical Scaling

- Configurable worker threads
- Memory optimization options
- Streaming for large files
- Efficient file operations

---

This architecture enables DeployForge to handle enterprise-scale deployments while remaining extensible and maintainable.
