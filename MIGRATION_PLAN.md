# Migration Plan: Python to Windows Native (PowerShell + WinUI 3)

## Overview
This document outlines the strategy to migrate the DeployForge codebase from Python to a Windows-native architecture.
- **Backend**: PowerShell Core (Modules & Scripts)
- **Frontend**: C# / WinUI 3 (Desktop App)

## Architecture

### 1. Backend: PowerShell Modules (`DeployForge.Backend`)
The existing Python logic heavily relies on `subprocess.run(["dism", ...])`. PowerShell is the native environment for these commands, allowing for a significant reduction in wrapper code and improved integration.

**Directory Structure:**
```
DeployForge/
└── Backend/
    └── DeployForge/
        ├── DeployForge.psd1           # Module Manifest
        ├── DeployForge.psm1           # Root Module
        ├── Public/                    # Exported Functions
        │   ├── New-ImageBuild.ps1
        │   ├── Mount-Image.ps1
        │   ├── Dismount-Image.ps1
        │   └── ...
        ├── Private/                   # Internal Logic
        │   ├── Core/                  # ImageManager logic
        │   ├── Handlers/              # WIM/VHD handlers
        │   └── Utils/                 # Logging, Telemetry
        └── Features/                  # Feature Modules
            ├── Gaming.ps1             # gaming.py
            ├── Privacy.ps1            # privacy_hardening.py
            ├── Devenv.ps1             # devenv.py
            ├── AppInstaller.ps1       # applications.py
            └── ...
```

### 2. Frontend: WinUI 3 (`DeployForge.GUI`)
A modern Windows desktop application using the Windows App SDK.

**Components:**
- **PowerShellService**: A C# service using `System.Management.Automation` to host a PowerShell runspace and execute backend scripts.
- **ViewModels**: MVVM architecture to bind UI controls to backend parameters.
- **Views**:
  - `DashboardPage`: Overview and quick stats.
  - `BuildPage`: Drag-and-drop image selection and feature toggles.
  - `ProfilesPage`: Profile configuration.
  - `SettingsPage`: App settings.

## Migration Mapping

| Python Module | PowerShell Component | Functionality |
|--------------|----------------------|---------------|
| `core/image_manager.py` | `Core/ImageContext.ps1` | Manages mounting/dismounting |
| `handlers/*.py` | `Handlers/*.ps1` | Format-specific logic (WIM/VHD) |
| `gaming.py` | `Features/Gaming.ps1` | `Enable-GamingOptimizations` |
| `privacy_hardening.py` | `Features/Privacy.ps1` | `Enable-PrivacyHardening` |
| `applications.py` | `Features/Apps.ps1` | `Install-Package` (WinGet/MSI) |
| `devenv.py` | `Features/Devenv.ps1` | `Install-DevEnvironment` |
| `ui_customization.py` | `Features/UI.ps1` | `Set-WindowsUI` |
| `gui_modern.py` | `DeployForge.GUI` (C#) | Main UI Logic |

## Execution Steps

1.  **Initialize Backend**: Create the `Backend` directory and the main PowerShell module structure.
2.  **Port Core Logic**: Translate `ImageManager` and basic DISM wrappers to PowerShell.
3.  **Port Feature Modules**: Convert the 9 enhanced modules and key features (Gaming, Privacy, etc.) to PowerShell functions.
4.  **Initialize Frontend**: Generate the C# solution, project files, and basic XAML/CS files.
5.  **Bridge**: Implement the `PowerShellService` in C# to connect the two.
6.  **Cleanup**: Remove the `src/deployforge` Python directory.

## Implementation Details

### PowerShell Design
- Use `CmdletBinding` for standard PowerShell behavior.
- Use `Write-Progress` for UI feedback.
- Return custom `PSCustomObject` for structured data.

### C# Design
- Use `CommunityToolkit.Mvvm` for clean MVVM.
- Use `PowerShell` class for execution.
- redirect PowerShell streams (Output, Error, Progress) to UI events.
