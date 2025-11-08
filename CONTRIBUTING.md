# Contributing to DeployForge

Thank you for considering contributing to DeployForge! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Cornman92/DeployForge/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Any potential drawbacks

### Submitting Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the coding standards
4. Add or update tests as needed
5. Ensure all tests pass:
   ```bash
   pytest
   ```
6. Update documentation if needed
7. Commit your changes with clear messages:
   ```bash
   git commit -m "Add feature: description"
   ```
8. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
9. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - Screenshots if applicable

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Cornman92/DeployForge.git
   cd DeployForge
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Formatting

Format your code with Black:
```bash
black src/deployforge
```

Check with flake8:
```bash
flake8 src/deployforge
```

Type check with mypy:
```bash
mypy src/deployforge
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic

Example docstring:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ExceptionType: Description of when this exception is raised
    """
    pass
```

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Use pytest for testing
- Mock external dependencies

Run tests:
```bash
pytest
pytest --cov=deployforge --cov-report=html
```

### Commit Messages

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

Example:
```
feat: add support for VHD image format

- Implement VHDHandler class
- Add mount/unmount operations
- Update documentation
- Add unit tests
```

## Adding New Image Formats

To add support for a new image format:

1. Create a new handler in `src/deployforge/handlers/`:
   ```python
   from deployforge.core.base_handler import BaseImageHandler

   class NewFormatHandler(BaseImageHandler):
       def mount(self, mount_point=None):
           # Implementation
           pass

       # Implement all required methods
   ```

2. Register the handler in `src/deployforge/handlers/__init__.py`:
   ```python
   from deployforge.handlers.new_format_handler import NewFormatHandler
   ImageManager.register_handler('.ext', NewFormatHandler)
   ```

3. Add tests in `tests/test_new_format_handler.py`

4. Update documentation

## Project Structure

```
DeployForge/
├── src/deployforge/        # Source code
│   ├── core/              # Core functionality
│   ├── handlers/          # Image format handlers
│   ├── utils/             # Utility functions
│   ├── config.py          # Configuration
│   └── cli.py             # CLI interface
├── tests/                 # Test files
├── docs/                  # Documentation
├── pyproject.toml         # Project metadata
└── README.md              # Main documentation
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a new tag:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```
4. Create a GitHub release

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion in GitHub Discussions
- Contact maintainers directly

Thank you for contributing to DeployForge!
