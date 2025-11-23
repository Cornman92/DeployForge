# Changelog

All notable changes to DeployForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Application installer framework (WinGet-based)
- Comprehensive test suite (85%+ coverage)
- Enhanced documentation (user guides, API docs)
- PyPI package distribution
- Windows installer packages

## [0.3.0] - 2025-11-15

### Added - Advanced Features
- **UEFI/GPT Partitioning**: Full support for modern UEFI systems
- **WinPE Customization**: Customize Windows Preinstallation Environment
- **Answer Files**: Unattend.xml generation and customization
- **Multi-language Support**: MUI (Multilingual User Interface) and language packs
- **VHD/VHDX Support**: Virtual hard disk format handling

### Added - Enhanced Modules (World-Class Standard)
- **Enhanced devenv.py** (750 lines): Developer environment builder with 10 profiles
- **Enhanced browsers.py** (686 lines): 17+ browsers with enterprise policies
- **Enhanced creative.py** (545 lines): Creative software suite with GPU optimization
- **Enhanced privacy_hardening.py** (397 lines): Privacy hardening with 4 security levels
- **Enhanced launchers.py** (399 lines): 12+ gaming platforms with mod managers
- **Enhanced ui_customization.py** (618 lines): UI themes and customization with 6 profiles
- **Enhanced backup.py** (650 lines): Backup and recovery with 5 backup profiles
- **Enhanced wizard.py** (527 lines): Setup wizard with 9 presets and hardware detection
- **Enhanced portable.py** (613 lines): Portable apps manager with 20+ app catalog

### Added - Feature Modules
- Partitioning module (`partitions.py`) for disk operations
- Unattend module (`unattend.py`) for answer file generation
- WinPE module (`winpe.py`) for boot environment customization
- Languages module (`languages.py`) for multi-language support
- Package management improvements
- Network configuration module enhancements
- Optimizer module enhancements

### Added - Documentation
- **CLAUDE.md** (37,909 lines): Comprehensive AI assistant guide
- **TODO.md**: Consolidated task list and project planning
- Module enhancement documentation
- Architecture documentation improvements

### Improved
- Module Enhancement Initiative: All 9 targeted modules enhanced (+4,500 lines)
- Configuration management improvements
- Error handling enhancements
- Logging improvements across all modules

### Changed
- Updated module structure following gaming.py reference pattern
- Improved type hints across all enhanced modules
- Better docstrings (Google-style) for all public APIs
- Enhanced enum and dataclass patterns

### Fixed
- Various bug fixes in image handling
- Registry operation improvements
- Driver injection reliability

## [0.2.0] - 2025-11-10

### Added - Enterprise Features
- **Batch Operations**: Parallel processing of multiple images
- **Image Comparison**: Compare two images and identify differences
- **Template System**: Reusable customization workflows
  - Pre-defined templates (Gaming, Workstation, Enterprise)
  - Template validation and management
  - Template import/export
- **Audit Logging**: JSONL-based compliance logging system
- **Cache Layer**: Performance optimization for repeated operations

### Added - Customization Features
- **Registry Editing**: Offline registry modification support
  - Pre-defined registry tweaks library
  - Custom registry operations
  - Registry backup and restore
- **Driver Injection**: Automated driver integration workflows
  - INF file parsing and validation
  - Driver compatibility checking
  - Bulk driver injection
- **Windows Update Integration**: Control update behavior in images
- **Security Module**: Security hardening features

### Added - User Interfaces
- **REST API**: FastAPI-based API server
  - OpenAPI/Swagger documentation
  - Image management endpoints
  - Registry operation endpoints
  - Driver injection endpoints
  - Batch operation endpoints
  - Template management endpoints
- **Modern GUI** (gui_modern.py): PyQt6 desktop application
  - 150+ customization features
  - 16 feature categories
  - 6 intelligent profiles (Gaming, Developer, Enterprise, Student, Creator, Custom)
  - Dark/Light theme support
  - Drag-and-drop image loading
  - Real-time progress tracking
  - Settings persistence

### Added - Feature Modules
- Gaming optimization module (`gaming.py`) - Reference implementation
- Debloating module (`debloat.py`)
- Performance optimization module (`performance.py`)
- Network configuration module (`network.py`)
- Services management module
- Visual customization module
- Power management module

### Added - Infrastructure
- Background job processing
- Progress tracking improvements
- Configuration management enhancements
- Performance monitoring

### Improved
- Enhanced error handling and validation
- Better progress reporting
- Improved logging across all modules
- Cross-platform compatibility improvements

### Dependencies
- Added FastAPI >= 0.104.0
- Added uvicorn[standard] >= 0.24.0
- Added pydantic >= 2.0.0
- Added PyQt6 >= 6.6.0
- Added psutil >= 5.9.0
- Added requests >= 2.31.0

## [0.1.0] - 2025-11-06

### Added
- Initial release of DeployForge
- Support for ISO 9660 image files
- Support for WIM (Windows Imaging Format) files
- Support for ESD (Electronic Software Download) files
- Support for PPKG (Provisioning Package) files
- CLI interface with rich terminal output
- Python API for programmatic image manipulation
- Cross-platform support (Windows, Linux, macOS)
- Configuration management with YAML and environment variables
- Comprehensive logging system
- Error handling and validation
- Context manager support for automatic cleanup
- Mount/unmount operations for all supported formats
- File add/remove/extract operations
- Image information and metadata retrieval
- ESD to WIM conversion capability
- PPKG customizations.xml parsing
- Unit tests for core functionality
- Comprehensive documentation in README

### Supported Operations
- `deployforge formats` - List supported formats
- `deployforge info` - Get image information
- `deployforge list` - List files in an image
- `deployforge add` - Add files to an image
- `deployforge remove` - Remove files from an image
- `deployforge extract` - Extract files from an image
- `deployforge mount` - Mount an image
- `deployforge unmount` - Unmount an image

### Dependencies
- click >= 8.1.0
- rich >= 13.0.0
- pyyaml >= 6.0
- pycdlib >= 1.14.0
- xmltodict >= 0.13.0

### Platform-Specific Requirements
- Windows: DISM (built-in)
- Linux/macOS: wimlib-imagex for WIM/ESD support

[0.1.0]: https://github.com/Cornman92/DeployForge/releases/tag/v0.1.0
