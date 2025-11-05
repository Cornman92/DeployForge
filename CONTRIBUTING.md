# Contributing to DeployForge

Thank you for your interest in contributing to DeployForge! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Commit Message Guidelines](#commit-message-guidelines)

---

## 🤝 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🚀 Getting Started

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DeployForge.git
   cd DeployForge
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Cornman92/DeployForge.git
   ```

4. **Install dependencies**
   - See [Development Setup Guide](docs/DEVELOPMENT_SETUP.md)

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `chore/` - Build/tooling changes

### 2. Make Your Changes

- Follow the [Coding Standards](#coding-standards)
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd src/backend
dotnet test

# Frontend tests
cd src/frontend
npm test

# PowerShell tests
cd tests/powershell
Invoke-Pester
```

### 4. Commit Your Changes

Follow our [Commit Message Guidelines](#commit-message-guidelines)

```bash
git add .
git commit -m "feat: add image mounting for VHDX files"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 💻 Coding Standards

### C# (.NET)

- Follow [Microsoft C# Coding Conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)
- Use XML documentation comments for public APIs
- Use async/await for I/O operations
- Handle exceptions appropriately
- Use dependency injection

**Example:**
```csharp
/// <summary>
/// Mounts a Windows image file
/// </summary>
/// <param name="imagePath">Path to the image file</param>
/// <returns>Mount path</returns>
public async Task<OperationResult<string>> MountImageAsync(string imagePath)
{
    ArgumentNullException.ThrowIfNull(imagePath);

    try
    {
        // Implementation
        return OperationResult<string>.SuccessResult(mountPath);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to mount image: {ImagePath}", imagePath);
        return OperationResult<string>.ExceptionResult(ex);
    }
}
```

### TypeScript/React

- Use TypeScript strict mode
- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks
- Use Prettier for formatting
- Use ESLint for linting

**Example:**
```typescript
interface ImageInfo {
  path: string;
  format: ImageFormat;
  size: number;
}

const ImageViewer: React.FC<{ image: ImageInfo }> = ({ image }) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load image details
  }, [image.path]);

  return <div>{/* Component JSX */}</div>;
};
```

### PowerShell

- Follow [PowerShell Practice and Style Guide](https://poshcode.gitbook.io/powershell-practice-and-style/)
- Use approved verbs (Get-, Set-, New-, Remove-, etc.)
- Include comment-based help
- Use PSScriptAnalyzer

**Example:**
```powershell
function Mount-DFImage {
    <#
    .SYNOPSIS
        Mounts a Windows image file.

    .DESCRIPTION
        The Mount-DFImage cmdlet mounts a Windows image file to a specified location.

    .PARAMETER Path
        Path to the image file.

    .EXAMPLE
        Mount-DFImage -Path "C:\Images\Win11.wim" -Index 1
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_})]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [int]$Index = 1
    )

    # Implementation
}
```

---

## 🧪 Testing Requirements

### Minimum Coverage

- **Backend**: 90% code coverage
- **Frontend**: 80% code coverage
- **PowerShell**: 80% code coverage

### Test Types

1. **Unit Tests**
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution

2. **Integration Tests**
   - Test component integration
   - Use test databases
   - Verify API contracts

3. **E2E Tests**
   - Test user workflows
   - Use real or mocked images
   - Cover critical paths

### Writing Tests

**Backend (xUnit):**
```csharp
public class DismManagerTests
{
    [Fact]
    public void Initialize_ShouldSucceed()
    {
        // Arrange
        var manager = new DismManager();

        // Act
        var result = manager.Initialize();

        // Assert
        Assert.True(result.Success);
    }
}
```

**Frontend (Vitest):**
```typescript
describe('ImageViewer', () => {
  it('should render image information', () => {
    const image = { path: 'test.wim', format: 'WIM', size: 1024 };
    render(<ImageViewer image={image} />);
    expect(screen.getByText('test.wim')).toBeInTheDocument();
  });
});
```

**PowerShell (Pester):**
```powershell
Describe 'Mount-DFImage' {
    It 'Should mount valid WIM file' {
        $result = Mount-DFImage -Path 'TestDrive:\test.wim' -Index 1
        $result | Should -Not -BeNullOrEmpty
    }
}
```

---

## 📤 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Code coverage meets requirements
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

### PR Checklist

Use the PR template (`.github/PULL_REQUEST_TEMPLATE.md`)

### Review Process

1. **Automated Checks**: CI/CD pipeline must pass
2. **Code Review**: At least 2 approvals required
3. **Testing**: Reviewers verify functionality
4. **Merge**: Squash and merge to maintain clean history

---

## 📝 Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Build/tooling changes
- `ci`: CI/CD changes

### Examples

```
feat(image): add VHDX mounting support

Implement VHDX file mounting using DISM API with support for
both read-only and read-write modes.

Closes #123
```

```
fix(dism): handle mount path already exists error

Add check for existing mount directory and clean up if needed
before attempting to mount.

Fixes #456
```

---

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority:high` - High priority
- `priority:low` - Low priority

---

## 🎯 Development Priorities

See [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) for current development phases.

**Current Focus** (Phase 1):
- Core backend infrastructure
- DISM integration
- Basic image operations (WIM, ISO)
- Frontend foundation

---

## ❓ Questions?

- **GitHub Discussions**: https://github.com/Cornman92/DeployForge/discussions
- **GitHub Issues**: https://github.com/Cornman92/DeployForge/issues

---

Thank you for contributing to DeployForge! 🎉
