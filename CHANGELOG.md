# Changelog

All notable changes to DeployForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
