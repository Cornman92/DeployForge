# DeployForge Native

A Windows-native implementation of DeployForge - an enterprise-grade Windows deployment customization suite.

## Architecture

This project replaces the original Python implementation with:
- **PowerShell Backend**: Native Windows scripting for all image operations
- **C# / WinUI 3 Frontend**: Modern Windows App SDK-based GUI

## Project Structure

```
DeployForge-Native/
├── DeployForge.sln                    # Visual Studio Solution
├── DeployForge.App/                   # WinUI 3 Application
│   ├── App.xaml(.cs)                  # Application entry point
│   ├── Models/                        # Data models
│   │   ├── ImageInfo.cs               # Image metadata
│   │   ├── Profile.cs                 # Customization profiles
│   │   ├── BuildConfiguration.cs      # Build settings
│   │   └── AppSettings.cs             # Application settings
│   ├── Services/                      # Business logic services
│   │   ├── INavigationService.cs      # Page navigation
│   │   ├── IThemeService.cs           # Theme management
│   │   ├── IDialogService.cs          # Dialogs and file pickers
│   │   ├── ISettingsService.cs        # Settings persistence
│   │   ├── IPowerShellService.cs      # PowerShell integration
│   │   ├── IImageService.cs           # Image operations
│   │   └── IProfileService.cs         # Profile management
│   ├── ViewModels/                    # MVVM ViewModels
│   │   ├── MainViewModel.cs           # Main window logic
│   │   ├── WelcomeViewModel.cs        # Welcome page
│   │   ├── BuildViewModel.cs          # Build configuration
│   │   ├── ProfilesViewModel.cs       # Profile management
│   │   ├── AnalyzeViewModel.cs        # Image analysis
│   │   └── SettingsViewModel.cs       # App settings
│   ├── Views/                         # XAML UI pages
│   │   ├── MainWindow.xaml(.cs)       # Main application window
│   │   ├── WelcomePage.xaml(.cs)      # Welcome/home page
│   │   ├── BuildPage.xaml(.cs)        # Image customization
│   │   ├── ProfilesPage.xaml(.cs)     # Profile management
│   │   ├── AnalyzePage.xaml(.cs)      # Image analysis
│   │   └── SettingsPage.xaml(.cs)     # Settings page
│   ├── Converters/                    # XAML value converters
│   └── Themes/                        # App theming resources
│
└── DeployForge.PowerShell/            # PowerShell Module
    ├── DeployForge.psd1               # Module manifest
    ├── DeployForge.psm1               # Main module script
    ├── Core/                          # Core infrastructure
    │   ├── Exceptions.ps1             # Custom exceptions
    │   ├── BaseHandler.ps1            # Abstract handler base
    │   └── ImageManager.ps1           # Image factory/coordinator
    ├── Handlers/                      # Image format handlers
    │   ├── WimHandler.ps1             # WIM file support
    │   ├── IsoHandler.ps1             # ISO file support
    │   ├── EsdHandler.ps1             # ESD file support
    │   ├── VhdHandler.ps1             # VHD/VHDX support
    │   └── PpkgHandler.ps1            # PPKG support
    ├── Features/                      # Feature modules
    │   ├── Gaming.ps1                 # Gaming optimizations
    │   ├── Debloat.ps1                # Bloatware removal
    │   ├── Privacy.ps1                # Privacy hardening
    │   ├── DevEnvironment.ps1         # Developer setup
    │   ├── Browsers.ps1               # Browser configuration
    │   ├── Drivers.ps1                # Driver injection
    │   ├── Registry.ps1               # Registry editing
    │   ├── Unattend.ps1               # Answer file generation
    │   ├── WinPE.ps1                  # WinPE customization
    │   ├── Templates.ps1              # Template system
    │   ├── Batch.ps1                  # Batch operations
    │   └── Languages.ps1              # Multi-language support
    └── Utilities/                     # Helper utilities
        ├── Logger.ps1                 # Logging system
        ├── Progress.ps1               # Progress tracking
        └── Validation.ps1             # Input validation

```

## Features

### Image Support
- **WIM** - Windows Imaging Format (DISM)
- **ESD** - Electronic Software Delivery (compressed WIM)
- **ISO** - ISO 9660 optical disc images
- **VHD/VHDX** - Virtual hard disk images
- **PPKG** - Provisioning packages

### Customization Options
- **Debloat**: Remove unwanted apps and features
- **Privacy**: Disable telemetry, Cortana, and tracking
- **Gaming**: Optimize for gaming performance
- **Developer**: Enable dev mode, WSL2, install dev tools
- **Performance**: Service optimization, animation controls
- **Unattend**: Generate answer files for automated deployment
- **Drivers**: Inject device drivers
- **Languages**: Multi-language support

## Requirements

### For the PowerShell Backend
- Windows 10 version 1809 or later
- PowerShell 5.1 or PowerShell 7+
- Administrator privileges
- Windows Assessment and Deployment Kit (ADK) for advanced features

### For the WinUI 3 Application
- Windows 10 version 1809 (build 17763) or later
- .NET 8.0
- Windows App SDK 1.5
- Visual Studio 2022 with .NET Desktop workload

## Building

### PowerShell Module
The PowerShell module can be used directly without compilation:

```powershell
Import-Module .\DeployForge.PowerShell\DeployForge.psd1
```

### WinUI 3 Application
```bash
cd DeployForge-Native
dotnet build -c Release
```

Or open `DeployForge.sln` in Visual Studio 2022 and build.

## Usage

### PowerShell CLI
```powershell
# Import the module
Import-Module DeployForge

# Get image info
Get-DFImageInfo -ImagePath "C:\Images\install.wim"

# Mount an image
Mount-DFImage -ImagePath "C:\Images\install.wim" -MountPoint "C:\Mount" -Index 1

# Apply gaming optimizations
Optimize-DFGaming -MountPoint "C:\Mount" -Profile Performance

# Remove bloatware
Start-DFDebloat -MountPoint "C:\Mount" -Level Moderate

# Dismount and save
Dismount-DFImage -MountPoint "C:\Mount" -Save
```

### GUI Application
1. Run `DeployForge.App.exe`
2. Select a Windows image (.wim, .esd, .iso)
3. Choose a profile or customize features
4. Click "Build" to create your customized image

## Profiles

Built-in profiles:
- **Gaming**: Optimized for gaming with reduced latency
- **Developer**: Full dev environment with WSL2 and tools
- **Enterprise**: Secure deployment with compliance features
- **Student**: Balanced setup for education
- **Creator**: Optimized for content creation
- **Minimal**: Bare minimum Windows installation

## License

MIT License - See LICENSE file for details.
