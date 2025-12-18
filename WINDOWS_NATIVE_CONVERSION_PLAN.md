# DeployForge Windows Native Conversion Plan

## Executive Summary

This document outlines the comprehensive plan to convert DeployForge from a Python-based application to a fully Windows-native implementation using:

- **PowerShell Backend**: Native Windows image manipulation via DISM, registry operations, and system management
- **C# Frontend**: Strongly-typed business logic, services, and MVVM architecture
- **WinUI 3 GUI**: Modern Windows 11 native UI with Fluent Design

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Component Mapping](#component-mapping)
4. [Implementation Phases](#implementation-phases)
5. [Detailed Module Conversion](#detailed-module-conversion)
6. [Technology Stack](#technology-stack)

---

## Architecture Overview

### Current Python Architecture
```
Python Application
├── CLI (Click + Rich)
├── GUI (PyQt6)
├── API (FastAPI)
├── Core (ImageManager, Handlers)
├── Feature Modules (Gaming, DevEnv, Debloat, etc.)
└── Utilities (Logging, Progress)
```

### New Windows Native Architecture
```
DeployForge Windows Native
├── DeployForge.PowerShell/           # PowerShell Backend Module
│   ├── Core/                         # Image management functions
│   ├── Features/                     # Feature-specific scripts
│   ├── Utilities/                    # Helper functions
│   └── DeployForge.psd1             # Module manifest
│
├── DeployForge.Core/                 # C# Shared Library
│   ├── Models/                       # Data models, DTOs
│   ├── Enums/                        # Enumerations
│   ├── Exceptions/                   # Custom exceptions
│   └── Interfaces/                   # Service contracts
│
├── DeployForge.Services/             # C# Business Logic
│   ├── PowerShell/                   # PS interop services
│   ├── Image/                        # Image management services
│   ├── Features/                     # Feature services
│   └── Configuration/                # App configuration
│
├── DeployForge.App/                  # WinUI 3 Application
│   ├── ViewModels/                   # MVVM ViewModels
│   ├── Views/                        # XAML Views/Pages
│   ├── Controls/                     # Custom controls
│   ├── Converters/                   # Value converters
│   ├── Helpers/                      # UI helpers
│   └── Resources/                    # Styles, themes
│
└── DeployForge.CLI/                  # C# CLI Application
    └── Commands/                     # CLI commands
```

### MVVM Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                        View Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ WelcomePage │ │  BuildPage  │ │ ProfilesPage │ Settings ││
│  └──────┬──────┘ └──────┬──────┘ └───────┬─────────────────┘│
│         │               │                 │                  │
│         └───────────────┼─────────────────┘                  │
│                         │ Data Binding                       │
│         ┌───────────────┼─────────────────┐                  │
│  ┌──────▼──────┐ ┌──────▼──────┐ ┌────────▼───────┐         │
│  │WelcomeVM    │ │  BuildVM    │ │ ProfilesVM     │         │
│  └──────┬──────┘ └──────┬──────┘ └────────┬───────┘         │
│         │               │                  │                 │
│         └───────────────┼──────────────────┘                 │
│                         │ Commands/Services                  │
│         ┌───────────────▼─────────────────┐                  │
│         │       Service Layer             │                  │
│  ┌──────┴──────┐ ┌──────────┐ ┌───────────┴────┐            │
│  │ImageService │ │PSExecutor│ │FeatureServices │            │
│  └──────┬──────┘ └────┬─────┘ └────────┬───────┘            │
│         │             │                 │                    │
│         └─────────────┼─────────────────┘                    │
│                       │ PowerShell Execution                 │
│         ┌─────────────▼─────────────────┐                    │
│         │   PowerShell Backend          │                    │
│         │   (DeployForge.PowerShell)    │                    │
│         └───────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

### Solution File: `DeployForge.sln`

```
DeployForge/
├── src/
│   ├── DeployForge.PowerShell/           # PowerShell Module
│   │   ├── Core/
│   │   │   ├── ImageManager.psm1         # Image operations
│   │   │   ├── RegistryManager.psm1      # Registry operations
│   │   │   ├── PartitionManager.psm1     # UEFI/GPT management
│   │   │   └── Exceptions.psm1           # Error handling
│   │   ├── Features/
│   │   │   ├── Gaming.psm1               # Gaming optimizations
│   │   │   ├── DevEnvironment.psm1       # Developer tools
│   │   │   ├── Debloat.psm1              # Bloatware removal
│   │   │   ├── Browsers.psm1             # Browser management
│   │   │   ├── Privacy.psm1              # Privacy hardening
│   │   │   ├── UICustomization.psm1      # UI tweaks
│   │   │   ├── Backup.psm1               # Backup/recovery
│   │   │   ├── Drivers.psm1              # Driver injection
│   │   │   ├── Updates.psm1              # Windows Update control
│   │   │   └── Unattend.psm1             # Answer file generation
│   │   ├── Utilities/
│   │   │   ├── Logging.psm1              # Logging functions
│   │   │   ├── Progress.psm1             # Progress tracking
│   │   │   └── Validation.psm1           # Input validation
│   │   ├── DeployForge.psd1              # Module manifest
│   │   └── DeployForge.psm1              # Root module
│   │
│   ├── DeployForge.Core/                 # .NET 8 Class Library
│   │   ├── Models/
│   │   │   ├── ImageInfo.cs
│   │   │   ├── PartitionInfo.cs
│   │   │   ├── GamingConfig.cs
│   │   │   ├── DevEnvironmentConfig.cs
│   │   │   ├── DebloatConfig.cs
│   │   │   ├── BrowserConfig.cs
│   │   │   ├── PrivacyConfig.cs
│   │   │   ├── UnattendConfig.cs
│   │   │   ├── TemplateConfig.cs
│   │   │   └── BuildProfile.cs
│   │   ├── Enums/
│   │   │   ├── ImageFormat.cs
│   │   │   ├── GamingProfile.cs
│   │   │   ├── DevelopmentProfile.cs
│   │   │   ├── DebloatLevel.cs
│   │   │   ├── BrowserType.cs
│   │   │   ├── PrivacyLevel.cs
│   │   │   └── PartitionType.cs
│   │   ├── Exceptions/
│   │   │   ├── DeployForgeException.cs
│   │   │   ├── ImageNotFoundException.cs
│   │   │   ├── MountException.cs
│   │   │   └── ValidationException.cs
│   │   ├── Interfaces/
│   │   │   ├── IImageService.cs
│   │   │   ├── IPowerShellExecutor.cs
│   │   │   ├── IFeatureService.cs
│   │   │   ├── ITemplateService.cs
│   │   │   └── IProgressReporter.cs
│   │   └── DeployForge.Core.csproj
│   │
│   ├── DeployForge.Services/             # .NET 8 Class Library
│   │   ├── PowerShell/
│   │   │   ├── PowerShellExecutor.cs
│   │   │   ├── PowerShellResult.cs
│   │   │   └── ScriptBuilder.cs
│   │   ├── Image/
│   │   │   ├── ImageService.cs
│   │   │   ├── WimHandler.cs
│   │   │   ├── VhdHandler.cs
│   │   │   ├── IsoHandler.cs
│   │   │   └── PartitionService.cs
│   │   ├── Features/
│   │   │   ├── GamingService.cs
│   │   │   ├── DevEnvironmentService.cs
│   │   │   ├── DebloatService.cs
│   │   │   ├── BrowserService.cs
│   │   │   ├── PrivacyService.cs
│   │   │   ├── DriverService.cs
│   │   │   └── UnattendService.cs
│   │   ├── Template/
│   │   │   ├── TemplateService.cs
│   │   │   └── TemplateValidator.cs
│   │   ├── Configuration/
│   │   │   ├── AppSettings.cs
│   │   │   └── SettingsService.cs
│   │   └── DeployForge.Services.csproj
│   │
│   ├── DeployForge.App/                  # WinUI 3 Application
│   │   ├── ViewModels/
│   │   │   ├── MainViewModel.cs
│   │   │   ├── WelcomeViewModel.cs
│   │   │   ├── BuildViewModel.cs
│   │   │   ├── ProfilesViewModel.cs
│   │   │   ├── AnalyzeViewModel.cs
│   │   │   ├── SettingsViewModel.cs
│   │   │   └── ViewModelBase.cs
│   │   ├── Views/
│   │   │   ├── MainWindow.xaml(.cs)
│   │   │   ├── WelcomePage.xaml(.cs)
│   │   │   ├── BuildPage.xaml(.cs)
│   │   │   ├── ProfilesPage.xaml(.cs)
│   │   │   ├── AnalyzePage.xaml(.cs)
│   │   │   └── SettingsPage.xaml(.cs)
│   │   ├── Controls/
│   │   │   ├── FeatureToggle.xaml(.cs)
│   │   │   ├── ProfileCard.xaml(.cs)
│   │   │   ├── ProgressPanel.xaml(.cs)
│   │   │   └── ImageDropZone.xaml(.cs)
│   │   ├── Converters/
│   │   │   ├── BoolToVisibilityConverter.cs
│   │   │   ├── EnumToStringConverter.cs
│   │   │   └── FileSizeConverter.cs
│   │   ├── Helpers/
│   │   │   ├── NavigationHelper.cs
│   │   │   ├── ThemeHelper.cs
│   │   │   └── DialogHelper.cs
│   │   ├── Resources/
│   │   │   ├── Styles/
│   │   │   │   ├── ButtonStyles.xaml
│   │   │   │   ├── TextStyles.xaml
│   │   │   │   └── Colors.xaml
│   │   │   └── Themes/
│   │   │       ├── Light.xaml
│   │   │       └── Dark.xaml
│   │   ├── App.xaml(.cs)
│   │   ├── Package.appxmanifest
│   │   └── DeployForge.App.csproj
│   │
│   └── DeployForge.CLI/                  # .NET 8 Console App
│       ├── Commands/
│       │   ├── BuildCommand.cs
│       │   ├── InfoCommand.cs
│       │   ├── MountCommand.cs
│       │   ├── UnmountCommand.cs
│       │   └── ProfileCommand.cs
│       ├── Program.cs
│       └── DeployForge.CLI.csproj
│
├── tests/
│   ├── DeployForge.Core.Tests/
│   ├── DeployForge.Services.Tests/
│   └── DeployForge.App.Tests/
│
├── DeployForge.sln
├── Directory.Build.props
├── global.json
└── NuGet.config
```

---

## Component Mapping

### Python to PowerShell/C# Mapping

| Python Module | PowerShell Module | C# Service | C# ViewModel |
|---------------|-------------------|------------|--------------|
| `core/image_manager.py` | `Core/ImageManager.psm1` | `ImageService.cs` | `BuildViewModel.cs` |
| `core/base_handler.py` | N/A (native DISM) | `WimHandler.cs`, `VhdHandler.cs` | N/A |
| `core/exceptions.py` | `Core/Exceptions.psm1` | `Exceptions/*.cs` | N/A |
| `handlers/wim_handler.py` | `Core/ImageManager.psm1` | `WimHandler.cs` | N/A |
| `handlers/vhd_handler.py` | `Core/ImageManager.psm1` | `VhdHandler.cs` | N/A |
| `gaming.py` | `Features/Gaming.psm1` | `GamingService.cs` | `BuildViewModel.cs` |
| `devenv.py` | `Features/DevEnvironment.psm1` | `DevEnvironmentService.cs` | `BuildViewModel.cs` |
| `debloat.py` | `Features/Debloat.psm1` | `DebloatService.cs` | `BuildViewModel.cs` |
| `browsers.py` | `Features/Browsers.psm1` | `BrowserService.cs` | `BuildViewModel.cs` |
| `privacy_hardening.py` | `Features/Privacy.psm1` | `PrivacyService.cs` | `BuildViewModel.cs` |
| `registry.py` | `Core/RegistryManager.psm1` | `RegistryService.cs` | N/A |
| `templates.py` | N/A | `TemplateService.cs` | `ProfilesViewModel.cs` |
| `batch.py` | N/A | `BatchService.cs` | `BuildViewModel.cs` |
| `partitions.py` | `Core/PartitionManager.psm1` | `PartitionService.cs` | N/A |
| `unattend.py` | `Features/Unattend.psm1` | `UnattendService.cs` | `BuildViewModel.cs` |
| `cli.py` | N/A | N/A | CLI Commands |
| `gui_modern.py` | N/A | N/A | WinUI 3 Views |

---

## Implementation Phases

### Phase 1: Foundation (Core Infrastructure)
1. Set up .NET solution structure
2. Create PowerShell module scaffold
3. Implement core image management in PowerShell
4. Create C# models and interfaces
5. Implement PowerShell executor service

### Phase 2: Services Layer
1. Implement ImageService (mount, unmount, list, add, remove)
2. Implement RegistryService (load, unload, set, delete)
3. Implement PartitionService (GPT, UEFI)
4. Create feature services framework

### Phase 3: Feature Modules
1. Gaming optimizations
2. Developer environment
3. Debloat and privacy
4. Browsers and software
5. Drivers and updates
6. Unattend file generation

### Phase 4: MVVM ViewModels
1. Base ViewModel infrastructure
2. MainViewModel with navigation
3. Feature-specific ViewModels
4. Command implementations

### Phase 5: WinUI 3 Views
1. Main window and navigation
2. Welcome page
3. Build page with feature toggles
4. Profiles page
5. Analyze and Settings pages
6. Custom controls and styling

### Phase 6: CLI and Polish
1. CLI application
2. Error handling and logging
3. Settings persistence
4. Documentation

---

## Detailed Module Conversion

### 1. Image Management

**Python (`image_manager.py`):**
```python
class ImageManager:
    def mount(self, mount_point=None) -> Path:
    def unmount(self, save_changes=False) -> None:
    def list_files(self, path="/") -> list:
    def add_file(self, source, destination) -> None:
    def get_info(self) -> Dict[str, Any]:
```

**PowerShell (`ImageManager.psm1`):**
```powershell
function Mount-DeployForgeImage {
    param([string]$ImagePath, [int]$Index = 1, [string]$MountPath)
}
function Dismount-DeployForgeImage {
    param([string]$MountPath, [switch]$Save, [switch]$Discard)
}
function Get-DeployForgeImageInfo {
    param([string]$ImagePath, [int]$Index = 1)
}
function Get-DeployForgeImageFiles {
    param([string]$MountPath, [string]$Path = "/")
}
function Add-DeployForgeFile {
    param([string]$MountPath, [string]$Source, [string]$Destination)
}
```

**C# (`ImageService.cs`):**
```csharp
public interface IImageService
{
    Task<MountResult> MountAsync(string imagePath, int index = 1, string? mountPath = null);
    Task UnmountAsync(string mountPath, bool saveChanges = false);
    Task<ImageInfo> GetInfoAsync(string imagePath, int index = 1);
    Task<IEnumerable<FileInfo>> ListFilesAsync(string mountPath, string path = "/");
    Task AddFileAsync(string mountPath, string source, string destination);
}
```

### 2. Gaming Optimization

**Python (`gaming.py`):**
```python
class GamingProfile(Enum):
    COMPETITIVE = "competitive"
    BALANCED = "balanced"
    QUALITY = "quality"
    STREAMING = "streaming"

class GamingOptimizer:
    def apply_profile(self, profile: GamingProfile): ...
    def install_gaming_runtimes(self, runtimes_path: Path): ...
    def optimize_services(self): ...
```

**PowerShell (`Gaming.psm1`):**
```powershell
function Set-GamingProfile {
    param(
        [string]$MountPath,
        [ValidateSet('Competitive','Balanced','Quality','Streaming')]
        [string]$Profile = 'Competitive'
    )
}
function Enable-GameMode { param([string]$MountPath) }
function Disable-GameBar { param([string]$MountPath) }
function Optimize-NetworkLatency { param([string]$MountPath) }
function Install-GamingRuntimes { param([string]$MountPath, [string]$RuntimesPath) }
```

**C# (`GamingService.cs`):**
```csharp
public class GamingService : IGamingService
{
    private readonly IPowerShellExecutor _psExecutor;
    
    public Task ApplyProfileAsync(string mountPath, GamingProfile profile);
    public Task EnableGameModeAsync(string mountPath);
    public Task OptimizeNetworkAsync(string mountPath);
    public Task InstallRuntimesAsync(string mountPath, string runtimesPath);
}
```

### 3. Developer Environment

**PowerShell (`DevEnvironment.psm1`):**
```powershell
function Set-DeveloperMode {
    param([string]$MountPath, [switch]$Enable)
}
function Install-DevelopmentTools {
    param(
        [string]$MountPath,
        [string[]]$IDEs,
        [string[]]$Languages,
        [string[]]$Tools
    )
}
function Enable-WSL2 { param([string]$MountPath) }
function Set-GitConfiguration {
    param([string]$MountPath, [string]$Name, [string]$Email)
}
```

### 4. Debloat and Privacy

**PowerShell (`Debloat.psm1`):**
```powershell
function Remove-Bloatware {
    param(
        [string]$MountPath,
        [ValidateSet('Minimal','Moderate','Aggressive')]
        [string]$Level = 'Moderate'
    )
}
function Disable-Telemetry { param([string]$MountPath) }
function Set-PrivacySettings { param([string]$MountPath) }
function Disable-Cortana { param([string]$MountPath) }
```

---

## Technology Stack

### Runtime & Framework
- **.NET 8.0** - Latest LTS
- **C# 12** - Latest language features
- **WinUI 3** - Windows App SDK 1.5+
- **PowerShell 7.4+** - Cross-platform PowerShell

### NuGet Packages
```xml
<!-- Core -->
<PackageReference Include="Microsoft.PowerShell.SDK" Version="7.4.0" />
<PackageReference Include="System.Management.Automation" Version="7.4.0" />
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />

<!-- WinUI 3 -->
<PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.240227000" />
<PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.22621.2428" />
<PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.2" />
<PackageReference Include="CommunityToolkit.WinUI.UI" Version="7.1.2" />

<!-- CLI -->
<PackageReference Include="System.CommandLine" Version="2.0.0-beta4.22272.1" />
<PackageReference Include="Spectre.Console" Version="0.48.0" />

<!-- Testing -->
<PackageReference Include="xunit" Version="2.6.6" />
<PackageReference Include="Moq" Version="4.20.70" />
<PackageReference Include="FluentAssertions" Version="6.12.0" />
```

### Build Requirements
- Visual Studio 2022 17.8+
- Windows SDK 10.0.22621.0+
- .NET 8.0 SDK
- Windows App SDK 1.5+

---

## Key Design Decisions

### 1. PowerShell as Backend
- Native Windows integration (DISM, registry, services)
- No external dependencies for core functionality
- Script-based for easy customization
- Existing Windows admin tooling compatibility

### 2. C# with MVVM
- Type safety and compile-time checks
- Clean separation of concerns
- Testable architecture
- Async/await for responsive UI

### 3. WinUI 3 for GUI
- Modern Fluent Design
- Native Windows 11 look and feel
- MSIX packaging support
- High DPI support

### 4. Service Layer Pattern
- PowerShell executor abstracts PS calls
- Feature services wrap PS modules
- Consistent error handling
- Progress reporting infrastructure

---

## Migration Notes

### Breaking Changes
- Python CLI commands → C# System.CommandLine
- PyQt6 GUI → WinUI 3 XAML
- FastAPI REST → Optional (can add later)
- Cross-platform support → Windows-only

### Preserved Features
- All 150+ customization features
- 6 deployment profiles
- Template system
- Batch operations
- Audit logging
- UEFI/GPT partitioning
- Answer file generation
- Multi-language support

---

## Next Steps

1. Create solution structure
2. Implement PowerShell core modules
3. Create C# models and services
4. Build WinUI 3 application shell
5. Implement features incrementally
6. Add CLI application
7. Testing and documentation
