# DeployForge Native - Windows Deployment Suite

**Version**: 2.0.0  
**Platform**: Windows Native (.NET 8 + PowerShell)  
**Architecture**: MVVM + WinUI 3

## Overview

DeployForge Native is a complete Windows-native rewrite of the DeployForge Python application. It provides comprehensive automation for Windows image customization using a modern architecture:

- **PowerShell Backend**: Native Windows image manipulation using DISM, reg.exe, and PowerShell cmdlets
- **C# Services**: Business logic and PowerShell interop using .NET 8
- **WinUI 3 GUI**: Modern Windows 11-style interface with MVVM pattern
- **CLI**: Command-line interface using System.CommandLine and Spectre.Console

## Project Structure

```
native/
├── DeployForge.sln              # Visual Studio solution
├── Directory.Build.props        # Common build properties
├── global.json                  # .NET SDK configuration
│
├── src/
│   ├── DeployForge.Core/        # Core models, enums, interfaces
│   │   ├── Enums/               # ImageFormat, GamingProfile, etc.
│   │   ├── Exceptions/          # Custom exception types
│   │   ├── Interfaces/          # Service interfaces
│   │   └── Models/              # Data models
│   │
│   ├── DeployForge.Services/    # Business logic layer
│   │   ├── PowerShellExecutor   # PowerShell interop
│   │   ├── ImageService         # Image operations
│   │   ├── FeatureService       # Gaming, Debloat, etc.
│   │   ├── TemplateService      # Profile management
│   │   └── SettingsService      # Application settings
│   │
│   ├── DeployForge.App/         # WinUI 3 GUI application
│   │   ├── ViewModels/          # MVVM ViewModels
│   │   ├── Views/               # XAML pages
│   │   └── Themes/              # UI themes
│   │
│   ├── DeployForge.CLI/         # Command-line interface
│   │   └── Commands/            # CLI command implementations
│   │
│   └── DeployForge.PowerShell/  # PowerShell backend module
│       ├── Core/                # Image, Registry management
│       └── Features/            # Gaming, Debloat, DevEnv, etc.
│
└── tests/
    ├── DeployForge.Core.Tests/
    └── DeployForge.Services.Tests/
```

## Features

### Image Management
- Mount/Unmount WIM, ESD, VHD, VHDX images
- File operations within mounted images
- Image information and analysis

### Build Profiles
- **Gaming**: Game Mode, network optimization, runtime installation
- **Developer**: Developer Mode, WSL2, IDEs, languages
- **Enterprise**: Security hardening, policy enforcement
- **Student**: Productivity tools, educational software
- **Creator**: Creative software, multimedia tools
- **Custom**: Full customization control

### Debloat & Privacy
- Remove pre-installed apps
- Disable telemetry and tracking
- Privacy-focused configurations
- Multiple debloat levels

### UI Customization
- Dark/Light mode
- Taskbar configuration
- Start menu settings
- Classic context menu

### Browser Configuration
- Install Chrome, Firefox, Brave, etc.
- Set default browser
- Apply enterprise policies

## Requirements

- Windows 10 version 1809 or later
- Windows 11 recommended
- .NET 8.0 SDK
- Windows App SDK 1.4+
- Administrator privileges (for image operations)
- PowerShell 5.1 or later

## Building

### Prerequisites

1. Install [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
2. Install [Windows App SDK](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/)
3. Install Visual Studio 2022 with:
   - .NET Desktop Development workload
   - Windows App SDK C# Templates

### Build Commands

```bash
# Restore dependencies
dotnet restore

# Build all projects
dotnet build

# Build release version
dotnet build -c Release

# Run tests
dotnet test

# Publish GUI application
dotnet publish src/DeployForge.App -c Release -r win-x64

# Publish CLI
dotnet publish src/DeployForge.CLI -c Release -r win-x64
```

## Usage

### GUI Application

Launch the WinUI 3 application:

```bash
dotnet run --project src/DeployForge.App
```

Or run the published executable:

```bash
.\publish\DeployForge.App.exe
```

### CLI Application

```bash
# Get help
deployforge --help

# Get image info
deployforge image info path/to/install.wim

# Mount an image
deployforge image mount path/to/install.wim --index 1

# Apply gaming profile
deployforge build gaming /mount/path --profile Performance

# Apply debloat settings
deployforge build debloat /mount/path --level Standard --disable-telemetry

# List available profiles
deployforge profile list

# Unmount with save
deployforge image unmount /mount/path --save
```

### PowerShell Module

```powershell
# Import the module
Import-Module .\src\DeployForge.PowerShell\DeployForge.psd1

# Mount an image
Mount-DeployForgeImage -ImagePath "C:\images\install.wim" -Index 1

# Apply gaming optimizations
Set-GamingProfile -MountPath "C:\mount" -Profile Performance

# Remove bloatware
Remove-Bloatware -MountPath "C:\mount" -Level Standard

# Configure developer environment
Set-DeveloperEnvironment -MountPath "C:\mount" -Profile WebDevelopment

# Unmount and save
Dismount-DeployForgeImage -MountPath "C:\mount" -Save
```

## Architecture

### MVVM Pattern

The GUI follows the Model-View-ViewModel pattern:

```
View (XAML) ←→ ViewModel ←→ Services ←→ PowerShell
```

- **Views**: WinUI 3 XAML pages with minimal code-behind
- **ViewModels**: Observable objects with commands using CommunityToolkit.Mvvm
- **Services**: Business logic with PowerShell interop
- **PowerShell**: Native Windows operations

### Dependency Injection

Services are registered and injected using Microsoft.Extensions.DependencyInjection:

```csharp
services.AddDeployForgeServices();
services.AddSingleton<MainViewModel>();
```

### PowerShell Integration

The C# services execute PowerShell commands through the PowerShellExecutor:

```csharp
var result = await _executor.ExecuteCommandAsync(
    "Mount-DeployForgeImage",
    new Dictionary<string, object>
    {
        ["ImagePath"] = imagePath,
        ["Index"] = index
    });
```

## License

See the main DeployForge LICENSE file.

## Contributing

See CONTRIBUTING.md in the main repository.
