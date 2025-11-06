# DeployForge

**Windows Deployment Suite** - Customize, personalize and optimize your Windows images and packages.

DeployForge enables users to add, remove, and edit files inside Windows deployment images including:
- **ISO** - ISO 9660 optical disc images
- **WIM** - Windows Imaging Format
- **ESD** - Electronic Software Download (compressed WIM)
- **PPKG** - Provisioning Packages

## Features

- 🔧 **Multi-format support** - Work with ISO, WIM, ESD, and PPKG files
- 🖥️ **Cross-platform** - Works on Windows, Linux, and macOS
- 📦 **Enterprise-ready** - Robust error handling and logging
- 🎯 **Easy to use** - Simple CLI interface with rich output
- 🔌 **Extensible** - Plugin architecture for custom handlers
- ⚡ **Efficient** - Optimized for large image files

## Installation

### From Source

```bash
git clone https://github.com/Cornman92/DeployForge.git
cd DeployForge
pip install -e .
```

### Using pip

```bash
pip install deployforge
```

### Dependencies

DeployForge requires Python 3.9 or later.

**For ISO support:**
```bash
pip install pycdlib
```

**For WIM/ESD support:**
- **Windows**: DISM (built-in)
- **Linux/macOS**: [wimlib](https://wimlib.net/)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install wimtools

  # macOS
  brew install wimlib
  ```

**For PPKG support:**
```bash
pip install xmltodict
```

## Quick Start

### View Supported Formats

```bash
deployforge formats
```

### Get Image Information

```bash
deployforge info path/to/image.wim
```

### List Files in an Image

```bash
deployforge list path/to/image.iso
deployforge list path/to/image.wim --path /Windows/System32
```

### Add a File to an Image

```bash
deployforge add path/to/image.wim source.txt /destination/path/file.txt
```

### Remove a File from an Image

```bash
deployforge remove path/to/image.iso /path/to/file.txt
```

### Extract a File from an Image

```bash
deployforge extract path/to/image.wim /Windows/System32/config/SOFTWARE output.hive
```

### Mount an Image

```bash
deployforge mount path/to/image.wim /mnt/windows --index 1
```

## Usage Examples

### Working with ISO Files

```bash
# Get ISO information
deployforge info windows.iso

# List files in the ISO
deployforge list windows.iso --path /sources

# Add a driver to the ISO
deployforge add windows.iso driver.inf /sources/drivers/driver.inf

# Extract boot.wim from ISO
deployforge extract windows.iso /sources/boot.wim ./boot.wim
```

### Working with WIM Files

```bash
# Get WIM information
deployforge info install.wim

# Mount WIM image (index 1)
deployforge mount install.wim /mnt/wim --index 1

# Add files while mounted
cp custom.exe /mnt/wim/Windows/System32/

# Unmount and save changes
# (On Windows) dism /Unmount-Wim /MountDir:/mnt/wim /Commit
# (On Linux) wimlib-imagex unmount /mnt/wim --commit
```

### Working with ESD Files

```bash
# ESD files work the same as WIM files
deployforge info install.esd

# List contents
deployforge list install.esd

# Convert ESD to WIM (programmatically)
# Use the Python API for advanced operations
```

### Working with PPKG Files

```bash
# Get PPKG information
deployforge info custom.ppkg

# List contents
deployforge list custom.ppkg

# Add a custom script
deployforge add custom.ppkg script.ps1 /Scripts/custom.ps1

# Extract customizations.xml
deployforge extract custom.ppkg /customizations.xml ./customizations.xml
```

## Python API

DeployForge can also be used as a Python library:

```python
from deployforge import ImageManager
from pathlib import Path

# Open an image
with ImageManager(Path('install.wim')) as manager:
    # Get information
    info = manager.get_info()
    print(info)

    # Mount the image
    mount_point = manager.mount()

    # List files
    files = manager.list_files('/')
    for file in files:
        print(f"{file['name']}: {file['size']} bytes")

    # Add a file
    manager.add_file(Path('custom.exe'), '/Windows/System32/custom.exe')

    # Remove a file
    manager.remove_file('/Windows/System32/unwanted.exe')

    # Extract a file
    manager.extract_file('/Windows/System32/config/SOFTWARE', Path('./SOFTWARE'))

    # Unmount and save changes
    manager.unmount(save_changes=True)
```

### Working with Specific Handlers

```python
from deployforge.handlers import ISOHandler, WIMHandler, ESDHandler, PPKGHandler
from pathlib import Path

# ISO Handler
iso = ISOHandler(Path('windows.iso'))
iso.mount()
files = iso.list_files('/')
iso.unmount()

# WIM Handler
wim = WIMHandler(Path('install.wim'))
wim.mount(index=1)
wim.add_file(Path('driver.sys'), '/Windows/System32/drivers/driver.sys')
wim.unmount(save_changes=True)

# ESD Handler (inherits from WIMHandler)
esd = ESDHandler(Path('install.esd'))
esd.convert_to_wim(Path('install.wim'), compression='maximum')

# PPKG Handler
ppkg = PPKGHandler(Path('custom.ppkg'))
ppkg.mount()
customizations = ppkg.get_customizations()
ppkg.unmount()
```

## Configuration

DeployForge can be configured using a YAML configuration file or environment variables.

### Configuration File

Create a `deployforge.yaml` file:

```yaml
mount:
  default_dir: /tmp/deployforge
  auto_cleanup: true

logging:
  level: INFO
  file: /var/log/deployforge.log

wim:
  default_index: 1
  compression: maximum  # none, fast, maximum, lzx, xpress

iso:
  preserve_permissions: true

ppkg:
  validate_xml: true
```

Use the configuration:

```bash
export DEPLOYFORGE_CONFIG=deployforge.yaml
deployforge info install.wim
```

### Environment Variables

- `DEPLOYFORGE_CONFIG` - Path to configuration file
- `DEPLOYFORGE_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEPLOYFORGE_MOUNT_DIR` - Default mount directory

## Architecture

DeployForge uses a modular architecture:

```
deployforge/
├── core/
│   ├── base_handler.py      # Abstract base handler
│   ├── image_manager.py     # Main entry point
│   └── exceptions.py        # Custom exceptions
├── handlers/
│   ├── iso_handler.py       # ISO image handler
│   ├── wim_handler.py       # WIM image handler
│   ├── esd_handler.py       # ESD image handler
│   └── ppkg_handler.py      # PPKG handler
├── utils/
│   └── logger.py            # Logging utilities
├── config.py                # Configuration management
└── cli.py                   # Command-line interface
```

### Extending DeployForge

You can create custom handlers by extending `BaseImageHandler`:

```python
from deployforge.core.base_handler import BaseImageHandler
from deployforge.core.image_manager import ImageManager

class CustomHandler(BaseImageHandler):
    def mount(self, mount_point=None):
        # Implementation
        pass

    def unmount(self, save_changes=False):
        # Implementation
        pass

    # Implement other required methods...

# Register the handler
ImageManager.register_handler('.custom', CustomHandler)
```

## Requirements

### System Requirements

- **Python**: 3.9 or later
- **OS**: Windows 10/11, Linux, macOS

### Platform-Specific Tools

**Windows:**
- DISM (Deployment Image Servicing and Management) - Built-in
- Administrator privileges may be required for mounting

**Linux/macOS:**
- `wimlib-imagex` - For WIM/ESD support
- `fuse` - For mounting (some handlers)

## Logging

DeployForge provides comprehensive logging:

```bash
# Enable verbose logging
deployforge -v info install.wim

# Log to file
deployforge --log-file deployforge.log info install.wim

# Set log level via environment
export DEPLOYFORGE_LOG_LEVEL=DEBUG
deployforge info install.wim
```

## Testing

Run tests with pytest:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=deployforge --cov-report=html
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/Cornman92/DeployForge/issues)
- **Documentation**: [Full Documentation](https://github.com/Cornman92/DeployForge/wiki)

## Acknowledgments

- **pycdlib** - ISO 9660 library
- **wimlib** - WIM library for Linux/macOS
- **Microsoft DISM** - Windows image servicing
- **Click** - CLI framework
- **Rich** - Terminal formatting

## Disclaimer

DeployForge is provided as-is for legitimate system administration and deployment tasks. Users are responsible for ensuring they have proper licenses and permissions for any Windows images they modify.

---

**Made with ❤️ for Windows System Administrators**
