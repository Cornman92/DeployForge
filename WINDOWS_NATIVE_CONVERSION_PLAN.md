# DeployForge Windows Native Conversion Plan

## Overview

This document outlines the comprehensive plan to convert DeployForge from Python to Windows native technologies:
- **Backend**: PowerShell 7+ modules
- **Frontend**: C# with WinUI 3
- **GUI Framework**: Windows App SDK (WinUI 3)

## Current Python Codebase Analysis

### Statistics
- **Total Python Files**: 79
- **Total Lines of Code**: ~29,163
- **Modules**: 70+ feature modules
- **Image Formats**: 6 (ISO, WIM, ESD, PPKG, VHD, VHDX)
- **Interfaces**: CLI, GUI (PyQt6), REST API

### Core Components to Convert

1. **Core Architecture** (3 files)
   - `image_manager.py` → `DeployForge.Core.psm1`
   - `base_handler.py` → `DeployForge.Handlers.psm1`
   - `exceptions.py` → PowerShell error classes

2. **Image Handlers** (5 files)
   - `wim_handler.py` → `DeployForge.WimHandler.psm1`
   - `iso_handler.py` → `DeployForge.IsoHandler.psm1`
   - `esd_handler.py` → `DeployForge.EsdHandler.psm1`
   - `vhd_handler.py` → `DeployForge.VhdHandler.psm1`
   - `ppkg_handler.py` → `DeployForge.PpkgHandler.psm1`

3. **Feature Modules** (40+ files)
   - Gaming optimization
   - Debloating
   - Privacy hardening
   - Developer environment
   - Browser management
   - UI customization
   - Backup/Recovery
   - And many more...

4. **User Interface**
   - `gui_modern.py` (3,000+ lines) → WinUI 3 application

## New Project Structure

```
DeployForge-Native/
├── DeployForge.PowerShell/
│   ├── DeployForge.psd1                    # Module manifest
│   ├── DeployForge.psm1                    # Main module
│   ├── Core/
│   │   ├── ImageManager.ps1                # Factory pattern for handlers
│   │   ├── BaseHandler.ps1                 # Base handler class
│   │   └── Exceptions.ps1                  # Custom exception types
│   ├── Handlers/
│   │   ├── WimHandler.ps1                  # WIM format handler
│   │   ├── IsoHandler.ps1                  # ISO format handler
│   │   ├── EsdHandler.ps1                  # ESD format handler
│   │   ├── VhdHandler.ps1                  # VHD/VHDX format handler
│   │   └── PpkgHandler.ps1                 # PPKG format handler
│   ├── Features/
│   │   ├── Gaming.ps1                      # Gaming optimization
│   │   ├── Debloat.ps1                     # Bloatware removal
│   │   ├── Privacy.ps1                     # Privacy hardening
│   │   ├── DevEnvironment.ps1              # Developer tools
│   │   ├── Browsers.ps1                    # Browser management
│   │   ├── Drivers.ps1                     # Driver injection
│   │   ├── Registry.ps1                    # Registry editing
│   │   ├── Updates.ps1                     # Windows Update control
│   │   ├── Unattend.ps1                    # Answer file generation
│   │   ├── WinPE.ps1                       # WinPE customization
│   │   ├── Templates.ps1                   # Template system
│   │   ├── Batch.ps1                       # Batch operations
│   │   └── Languages.ps1                   # Multi-language support
│   └── Utilities/
│       ├── Logger.ps1                      # Logging utilities
│       ├── Progress.ps1                    # Progress tracking
│       └── Validation.ps1                  # Input validation
│
├── DeployForge.WinUI/
│   ├── DeployForge.WinUI.csproj
│   ├── App.xaml
│   ├── App.xaml.cs
│   ├── MainWindow.xaml
│   ├── MainWindow.xaml.cs
│   ├── Models/
│   │   ├── ImageInfo.cs
│   │   ├── BuildConfiguration.cs
│   │   ├── Profile.cs
│   │   ├── Feature.cs
│   │   └── OperationResult.cs
│   ├── Services/
│   │   ├── PowerShellService.cs            # PowerShell interop
│   │   ├── ImageService.cs                 # Image operations
│   │   ├── ProfileService.cs               # Profile management
│   │   ├── SettingsService.cs              # Settings management
│   │   └── NavigationService.cs            # Navigation
│   ├── ViewModels/
│   │   ├── MainViewModel.cs
│   │   ├── WelcomeViewModel.cs
│   │   ├── BuildViewModel.cs
│   │   ├── ProfilesViewModel.cs
│   │   ├── AnalyzeViewModel.cs
│   │   └── SettingsViewModel.cs
│   ├── Views/
│   │   ├── WelcomePage.xaml
│   │   ├── BuildPage.xaml
│   │   ├── ProfilesPage.xaml
│   │   ├── AnalyzePage.xaml
│   │   └── SettingsPage.xaml
│   ├── Controls/
│   │   ├── FeatureCard.xaml
│   │   ├── ProfileCard.xaml
│   │   ├── ProgressPanel.xaml
│   │   └── ImageDropZone.xaml
│   ├── Themes/
│   │   ├── LightTheme.xaml
│   │   └── DarkTheme.xaml
│   └── Assets/
│       ├── Logo.png
│       └── Icons/
│
└── DeployForge.sln                         # Visual Studio solution
```

## Technology Stack

### Backend (PowerShell 7+)
- Native Windows integration
- Direct DISM access
- Registry manipulation
- File system operations
- WMI/CIM cmdlets
- Background jobs for async operations

### Frontend (C# / WinUI 3)
- Windows App SDK 1.4+
- MVVM architecture with CommunityToolkit
- Fluent Design System
- Mica/Acrylic materials
- Light/Dark theme support
- Drag-and-drop support

### Integration
- PowerShell SDK for C# integration
- JSON-based configuration exchange
- Event-based progress reporting
- Named pipes for real-time communication

## Conversion Mapping

### Core Classes

| Python | PowerShell | C# |
|--------|------------|-----|
| `ImageManager` | `DeployForge.ImageManager` class | `ImageService` |
| `BaseImageHandler` | `DeployForge.BaseHandler` class | `IImageHandler` interface |
| `DeployForgeError` | `DeployForgeException` class | `DeployForgeException` |

### Feature Modules

| Python Module | PowerShell Function Prefix | C# Service |
|--------------|---------------------------|------------|
| `gaming.py` | `Optimize-DFGaming*` | `GamingService` |
| `debloat.py` | `Remove-DFBloatware*` | `DebloatService` |
| `devenv.py` | `Install-DFDevEnv*` | `DevEnvService` |
| `browsers.py` | `Install-DFBrowser*` | `BrowserService` |
| `privacy_hardening.py` | `Set-DFPrivacy*` | `PrivacyService` |
| `drivers.py` | `Add-DFDriver*` | `DriverService` |
| `registry.py` | `Set-DFRegistry*` | `RegistryService` |
| `unattend.py` | `New-DFUnattend*` | `UnattendService` |
| `winpe.py` | `Build-DFWinPE*` | `WinPEService` |

### GUI Mapping

| Python (PyQt6) | WinUI 3 |
|----------------|---------|
| `QMainWindow` | `Window` |
| `QStackedWidget` | `Frame` + `NavigationView` |
| `QCheckBox` | `CheckBox` |
| `QComboBox` | `ComboBox` |
| `QPushButton` | `Button` |
| `QProgressBar` | `ProgressBar` + `ProgressRing` |
| `QLabel` | `TextBlock` |
| `QLineEdit` | `TextBox` |
| `QGroupBox` | `Expander` |
| `QScrollArea` | `ScrollViewer` |
| `QTabWidget` | `TabView` |
| `QListWidget` | `ListView` |
| `QTreeWidget` | `TreeView` |

## Implementation Phases

### Phase 1: PowerShell Core (Week 1-2)
1. Create module structure and manifest
2. Implement ImageManager factory
3. Implement BaseHandler class
4. Create custom exception types
5. Implement WIM handler (primary)
6. Implement remaining handlers

### Phase 2: Feature Modules (Week 3-4)
1. Gaming optimization
2. Debloating
3. Privacy hardening
4. Developer environment
5. Browser management
6. Driver injection
7. Registry editing
8. Answer file generation
9. Template system

### Phase 3: WinUI 3 Application (Week 5-6)
1. Create project structure
2. Implement MVVM architecture
3. Create navigation framework
4. Implement Welcome page
5. Implement Build page with features
6. Implement Profiles page
7. Implement Analyze page
8. Implement Settings page

### Phase 4: Integration & Testing (Week 7-8)
1. PowerShell-C# integration
2. Progress reporting
3. Error handling
4. Unit tests
5. Integration tests
6. UI testing

## Feature Parity Checklist

### Core Features
- [ ] Mount/unmount WIM images
- [ ] Mount/unmount ISO images
- [ ] Mount/unmount VHD/VHDX
- [ ] Handle ESD format
- [ ] Handle PPKG format
- [ ] File operations (add, remove, extract, list)
- [ ] Image information retrieval

### Optimization Features
- [ ] Gaming optimization (4 profiles)
- [ ] Debloating (3 levels)
- [ ] Privacy hardening (4 levels)
- [ ] Network optimization
- [ ] Power optimization
- [ ] Service optimization

### Installation Features
- [ ] Developer environment (10 profiles)
- [ ] Browser installation (17+ browsers)
- [ ] Creative software
- [ ] Gaming launchers (12+ platforms)
- [ ] Portable applications

### Customization Features
- [ ] Registry editing
- [ ] Driver injection
- [ ] Feature enable/disable
- [ ] Unattend.xml generation
- [ ] WinPE customization
- [ ] Multi-language support
- [ ] UI customization (6 profiles)

### Enterprise Features
- [ ] Batch operations
- [ ] Template system
- [ ] Audit logging
- [ ] GPO configuration
- [ ] Certificate management
- [ ] Encryption support

### GUI Features
- [ ] Dark/Light theme
- [ ] Mica material
- [ ] Drag-and-drop
- [ ] 5-page navigation
- [ ] Profile selection (6 profiles)
- [ ] 150+ feature checkboxes
- [ ] Progress tracking
- [ ] Settings persistence

## Benefits of Windows Native

1. **Performance**: Direct DISM access without Python overhead
2. **Compatibility**: Native Windows integration
3. **Maintenance**: Easier updates with Windows versions
4. **Distribution**: No Python dependency installation
5. **UI Quality**: Modern Fluent Design with WinUI 3
6. **Integration**: Better Windows 11 integration
7. **Security**: Native code signing and security features

## Dependencies

### PowerShell
- PowerShell 7.0+
- Windows 10/11
- DISM (built-in)
- No external modules required

### WinUI 3
- .NET 8.0 SDK
- Windows App SDK 1.4+
- Visual Studio 2022
- Windows 10 1809+ / Windows 11

## Next Steps

1. Create PowerShell module directory structure
2. Implement core module with ImageManager
3. Create C#/WinUI 3 project
4. Implement PowerShell interop service
5. Build UI components
6. Test and validate feature parity
