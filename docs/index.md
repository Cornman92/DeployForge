# DeployForge Documentation

Welcome to DeployForge - the comprehensive Windows deployment suite for customizing, personalizing, and optimizing Windows images and packages.

## Quick Links

- [Getting Started](getting-started.md)
- [API Reference](api/index.md)
- [User Guide](user-guide/index.md)
- [Examples](examples/index.md)
- [Security Guide](security.md)

## What is DeployForge?

DeployForge is an enterprise-grade tool for managing Windows deployment images. It provides:

- **Multi-format support**: ISO, WIM, ESD, PPKG, VHD, VHDX
- **Advanced customization**: Registry editing, driver injection, updates
- **Batch operations**: Process multiple images in parallel
- **REST API**: Automate with HTTP endpoints
- **GUI Application**: User-friendly desktop interface
- **Template System**: Reusable customization templates

## Features

### Image Format Support

- **ISO 9660**: Optical disc images
- **WIM**: Windows Imaging Format
- **ESD**: Electronic Software Download
- **PPKG**: Provisioning Packages
- **VHD/VHDX**: Virtual Hard Disks

### Customization Capabilities

- **Registry Editing**: Modify Windows registry hives offline
- **Driver Injection**: Automated driver package integration
- **Windows Updates**: Offline update application
- **File Operations**: Add, remove, extract files
- **Template System**: Reusable customization workflows

### Enterprise Features

- **Batch Operations**: Process hundreds of images
- **REST API**: Automation and integration
- **Audit Logging**: Compliance and tracking
- **Remote Repositories**: S3, Azure Blob, HTTP
- **Caching**: Performance optimization

## Installation

```bash
pip install deployforge
```

See [Installation Guide](installation.md) for detailed instructions.

## Quick Start

```python
from deployforge import ImageManager

# Open an image
with ImageManager("install.wim") as manager:
    # Get information
    info = manager.get_info()

    # Mount image
    manager.mount()

    # List files
    files = manager.list_files("/")

    # Unmount
    manager.unmount()
```

## Architecture

DeployForge uses a modular architecture:

```
deployforge/
├── core/           # Core functionality
├── handlers/       # Format-specific handlers
├── api/            # REST API
├── gui/            # Desktop application
└── utils/          # Utilities
```

## Support

- [GitHub Issues](https://github.com/Cornman92/DeployForge/issues)
- [Discussions](https://github.com/Cornman92/DeployForge/discussions)
- [Documentation](https://docs.deployforge.io)

## License

MIT License - See [LICENSE](../LICENSE) for details.
