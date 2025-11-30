# Development Guide

Complete guide for setting up and working with the DeployForge development environment.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Development Workflow](#development-workflow)
- [Code Quality](#code-quality)
- [Testing](#testing)
- [Documentation](#documentation)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Text Editor/IDE** - VS Code recommended

### Recommended Tools

- **VS Code** with extensions:
  - Python
  - Pylance
  - Python Test Explorer
  - GitLens
  - Better Comments
- **GitHub CLI** (`gh`) - [Download](https://cli.github.com/)

### Platform-Specific Requirements

#### Windows
```powershell
# DISM is built-in
# Optionally install:
choco install git python vscode
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv git wimtools

# RHEL/CentOS/Fedora
sudo dnf install python3 python3-pip git wimlib-utils
```

#### macOS
```bash
brew install python git wimlib
```

---

## Initial Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork:
git clone https://github.com/YOUR_USERNAME/DeployForge.git
cd DeployForge

# Add upstream remote
git remote add upstream https://github.com/Cornman92/DeployForge.git
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Verify
which python  # Should point to venv/bin/python or venv\Scripts\python
```

### 3. Install Dependencies

```bash
# Install in development mode with all extras
pip install -e ".[dev]"

# Verify installation
deployforge --version
pytest --version
black --version
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

### 5. Configure Git

```bash
# Set your identity
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Optional: Set up signing commits
git config commit.gpgsign true
```

### 6. Verify Setup

```bash
# Run tests
pytest

# Check code quality
black --check src/deployforge
flake8 src/deployforge
mypy src/deployforge

# All should pass!
```

---

## Development Workflow

### Daily Workflow

```bash
# 1. Start your day - update from upstream
git checkout main
git pull upstream main
git push origin main

# 2. Create feature branch
git checkout -b feature/my-awesome-feature

# 3. Make changes
# ... code code code ...

# 4. Run tests frequently
pytest tests/test_my_feature.py

# 5. Check code quality
black src/deployforge
flake8 src/deployforge

# 6. Commit changes (pre-commit hooks run automatically)
git add <files>
git commit -m "feat: add awesome feature"

# 7. Push to your fork
git push origin feature/my-awesome-feature

# 8. Create Pull Request on GitHub
```

### Branch Naming

Use prefixes for clarity:

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Test additions/changes
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

Examples:
```bash
feature/add-vmdk-support
fix/wim-mount-error
docs/update-installation-guide
test/add-batch-tests
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

<optional detailed description>

<optional footer>
```

**Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `style:` - Code style
- `chore:` - Maintenance
- `perf:` - Performance

**Examples**:
```
feat: add VMDK image format support

Implement VMDKHandler class with mount/unmount operations.
Includes unit tests and documentation updates.

Closes #123

---

fix: resolve memory leak in batch processing

The BatchOperation class was not properly releasing image handlers,
causing memory accumulation during large batch operations.

- Add proper cleanup in __exit__
- Implement garbage collection hints
- Add memory usage tests
```

---

## Code Quality

### Code Style

**We use**:
- **Black** for formatting (100 char line length)
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for type checking

### Running Quality Checks

```bash
# Format code automatically
black src/deployforge tests

# Sort imports
isort src/deployforge tests

# Check for linting issues
flake8 src/deployforge tests --max-line-length=100

# Type check
mypy src/deployforge --ignore-missing-imports

# Security scan
bandit -r src/deployforge

# All at once (via pre-commit)
pre-commit run --all-files
```

### Code Standards

#### Type Hints

Always use type hints:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def process_image(
    image_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process image and return list of applied tweaks."""
    if options is None:
        options = {}
    # ...
    return ["tweak1", "tweak2"]
```

#### Docstrings

Use Google-style docstrings:

```python
def apply_customization(
    image_path: Path,
    profile: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Apply customization profile to image.

    This function mounts the image, applies all customizations
    from the specified profile, and unmounts with changes saved.

    Args:
        image_path: Path to Windows image file
        profile: Profile name (gaming, developer, enterprise)
        dry_run: If True, only simulate changes without saving

    Returns:
        Dictionary containing:
            - success: bool
            - applied_tweaks: List[str]
            - errors: List[str]

    Raises:
        ImageNotFoundError: If image file doesn't exist
        UnsupportedFormatError: If image format not supported
        MountError: If image mounting fails

    Example:
        >>> result = apply_customization(
        ...     Path('install.wim'),
        ...     profile='gaming',
        ...     dry_run=False
        ... )
        >>> print(result['applied_tweaks'])
        ['game_mode', 'gpu_scheduling', 'debloat']
    """
    pass
```

#### Error Handling

Use specific exceptions:

```python
from deployforge.core.exceptions import (
    DeployForgeError,
    ImageNotFoundError,
    MountError
)

try:
    image = load_image(path)
except FileNotFoundError:
    raise ImageNotFoundError(f"Image not found: {path}")
except PermissionError as e:
    raise MountError(f"Permission denied: {e}") from e
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise DeployForgeError(f"Failed to load image: {e}") from e
```

#### Logging

Use module-level logger:

```python
import logging

logger = logging.getLogger(__name__)

def process_something():
    logger.debug("Starting process")
    logger.info("Processing item 1")
    logger.warning("Item 2 skipped")
    logger.error("Failed to process item 3")
    logger.critical("Critical failure, aborting")
```

---

## Testing

### Test Organization

```
tests/
├── conftest.py              # Pytest configuration & fixtures
├── test_core/               # Core module tests
│   ├── test_image_manager.py
│   └── test_exceptions.py
├── test_handlers/           # Handler tests
│   ├── test_iso_handler.py
│   ├── test_wim_handler.py
│   └── ...
├── test_features/           # Feature module tests
│   ├── test_gaming.py
│   ├── test_debloat.py
│   └── ...
└── test_integration/        # Integration tests
    └── test_workflows.py
```

### Writing Tests

**Use pytest**:

```python
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from deployforge.core.image_manager import ImageManager
from deployforge.core.exceptions import ImageNotFoundError

def test_image_manager_initialization(mock_wim_file):
    """Test ImageManager initialization with valid image."""
    manager = ImageManager(mock_wim_file)
    assert manager.image_path == mock_wim_file

def test_image_not_found():
    """Test error handling for missing image."""
    with pytest.raises(ImageNotFoundError):
        ImageManager(Path('nonexistent.wim'))

@patch('subprocess.run')
def test_mount_operation(mock_run, mock_wim_file):
    """Test image mounting with mocked subprocess."""
    mock_run.return_value = Mock(returncode=0, stdout=b"Success")

    manager = ImageManager(mock_wim_file)
    handler = manager.get_handler()
    mount_point = handler.mount()

    assert mount_point.exists()
    mock_run.assert_called_once()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_image_manager.py

# Run specific test
pytest tests/test_image_manager.py::test_initialization

# Run with coverage
pytest --cov=deployforge --cov-report=html --cov-report=term

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_mount"

# Show print statements
pytest -s
```

### Test Coverage

**Target**: 85%+ coverage

```bash
# Generate coverage report
pytest --cov=deployforge --cov-report=html

# View report
# Open htmlcov/index.html in browser

# Check coverage threshold
pytest --cov=deployforge --cov-fail-under=85
```

### Mocking Guidelines

**Mock external dependencies**:

```python
@patch('deployforge.handlers.wim_handler.subprocess.run')
def test_wim_mount(mock_subprocess):
    """Mock subprocess for DISM operations."""
    mock_subprocess.return_value = Mock(
        returncode=0,
        stdout=b"The operation completed successfully."
    )
    # Test implementation
```

**Use fixtures for common mocks**:

```python
# conftest.py
@pytest.fixture
def mock_mount_point(tmp_path):
    """Create mock Windows directory structure."""
    mount = tmp_path / "mount"
    mount.mkdir()
    (mount / "Windows" / "System32" / "config").mkdir(parents=True)
    return mount
```

---

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings in code
2. **User Documentation**: README, guides (Markdown)
3. **API Documentation**: Auto-generated with Sphinx (planned)
4. **Architecture Documentation**: ARCHITECTURE.md

### Writing Documentation

#### Code Docstrings

Every public function/class needs a docstring:

```python
class ImageHandler:
    """
    Handler for Windows image files.

    This class provides operations for mounting, modifying,
    and unmounting Windows installation images.

    Attributes:
        image_path: Path to the image file
        is_mounted: Whether image is currently mounted
        mount_point: Directory where image is mounted

    Example:
        >>> handler = ImageHandler(Path('install.wim'))
        >>> handler.mount()
        >>> handler.add_file(Path('app.exe'), '/Program Files/App/')
        >>> handler.unmount(save_changes=True)
    """
```

#### User Documentation

Update relevant docs when changing features:

- **README.md**: User-facing feature changes
- **INSTALLATION.md**: Installation procedure changes
- **QUICKSTART.md**: Usage example changes
- **CHANGELOG.md**: All notable changes

#### Building API Docs (Planned)

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Build docs
cd docs/
make html

# View docs
open _build/html/index.html
```

---

## Common Tasks

### Adding a New Image Format

1. **Create handler** in `src/deployforge/handlers/new_format_handler.py`
2. **Extend BaseImageHandler**
3. **Implement all abstract methods**
4. **Register handler** in `src/deployforge/handlers/__init__.py`
5. **Add tests** in `tests/test_handlers/test_new_format_handler.py`
6. **Update documentation** in README.md

### Adding a New Feature Module

1. **Create module** following `gaming.py` pattern
2. **Include**: Enum, Dataclass, Main class
3. **Add type hints and docstrings**
4. **Implement error handling**
5. **Add tests**
6. **Update README feature list**

### Debugging

```bash
# Run with verbose logging
DEPLOYFORGE_LOG_LEVEL=DEBUG deployforge [command]

# Use Python debugger
python -m pdb -m deployforge.cli [command]

# Use VS Code debugger
# Set breakpoints and press F5
```

### Profiling

```bash
# Profile with cProfile
python -m cProfile -o profile.stats -m deployforge.cli [command]

# View results
python -m pstats profile.stats
# Then: sort cumulative / stats 20

# Profile memory
python -m memory_profiler script.py
```

---

## Troubleshooting

### Virtual Environment Issues

```bash
# Deactivate and delete
deactivate
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

# Recreate
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -e ".[dev]"
```

### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Check PYTHONPATH
echo $PYTHONPATH  # Should include src/

# Reinstall if needed
pip install --force-reinstall -e ".[dev]"
```

### Test Failures

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run only failed tests
pytest --lf -v
```

### Pre-commit Hook Issues

```bash
# Skip hooks temporarily (not recommended)
git commit --no-verify

# Update hooks
pre-commit autoupdate

# Reinstall hooks
pre-commit uninstall
pre-commit install

# Run specific hook
pre-commit run black --all-files
```

---

## IDE Configuration

### VS Code

**`.vscode/settings.json`**:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=100"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["-v"],
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**`.vscode/launch.json`**:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "DeployForge CLI",
      "type": "python",
      "request": "launch",
      "module": "deployforge.cli",
      "args": ["--help"],
      "console": "integratedTerminal"
    },
    {
      "name": "Pytest: Current File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v", "${file}"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm

1. **Interpreter**: Settings → Project → Python Interpreter → Add → Virtualenv → Existing → `venv/`
2. **Code Style**: Settings → Editor → Code Style → Python → Set line length to 100
3. **Testing**: Settings → Tools → Python Integrated Tools → Default test runner: pytest
4. **Black**: Settings → Tools → Black → Enable on save

---

## Additional Resources

- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Code of Conduct**: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

## Getting Help

- **GitHub Discussions**: https://github.com/Cornman92/DeployForge/discussions
- **Issue Tracker**: https://github.com/Cornman92/DeployForge/issues
- **Documentation**: https://github.com/Cornman92/DeployForge

---

**Happy Coding!** 🚀

---

**Version**: 0.3.0
**Last Updated**: 2025-11-23
**Maintained By**: DeployForge Team
