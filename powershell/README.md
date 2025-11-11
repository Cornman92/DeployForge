# DeployForge PowerShell Module

PowerShell module for Windows deployment image customization.

## Installation

### Prerequisites

- PowerShell 5.1 or later (PowerShell Core 7+ supported)
- Python 3.8 or later
- DeployForge Python package: `pip install deployforge`
- Windows 10/11 with DISM

### Import Module

```powershell
# Import from local path
Import-Module .\DeployForge.psm1

# Or install to PowerShell modules directory
Copy-Item -Recurse .\DeployForge $env:PSModulePath.Split(';')[0]
Import-Module DeployForge
```

## Quick Start

### Build a Gaming Image

```powershell
# Apply gaming profile to Windows image
Build-DeployForgeImage -ImagePath .\install.wim -Profile gamer -Output .\gaming.wim
```

### Interactive Mode

```powershell
# Interactive build with prompts
Build-DeployForgeImage -ImagePath .\install.wim -Interactive
```

### Analyze an Image

```powershell
# Get image information
Get-DeployForgeImageInfo -ImagePath .\install.wim

# Generate HTML report
Get-DeployForgeImageInfo -ImagePath .\install.wim -Format html -Output .\report.html
```

### Compare Images

```powershell
# Compare two images
Compare-DeployForgeImage -Image1 .\original.wim -Image2 .\customized.wim
```

## Available Cmdlets

### Image Building

| Cmdlet | Description |
|--------|-------------|
| `Build-DeployForgeImage` | Build customized Windows image with profile |
| `Set-DeployForgeProfile` | Apply profile to existing image |
| `Get-DeployForgeProfile` | List available profiles |

### Image Analysis

| Cmdlet | Description |
|--------|-------------|
| `Get-DeployForgeImageInfo` | Analyze image and generate report |
| `Compare-DeployForgeImage` | Compare two images and show differences |
| `Test-DeployForgeImage` | Validate image integrity and compatibility |

### Preset Management

| Cmdlet | Description |
|--------|-------------|
| `New-DeployForgePreset` | Create new customization preset |
| `Get-DeployForgePreset` | List available presets |
| `Set-DeployForgePreset` | Apply preset to image |

### Optimization

| Cmdlet | Description |
|--------|-------------|
| `Optimize-DeployForgeGaming` | Apply gaming optimizations |
| `Remove-DeployForgeBloatware` | Remove unwanted applications |

## Examples

### Example 1: Build Developer Image

```powershell
# Build image with developer tools
Build-DeployForgeImage `
    -ImagePath C:\Images\install.wim `
    -Profile developer `
    -Output C:\Images\developer.wim
```

### Example 2: Gaming Optimization

```powershell
# Apply competitive gaming profile
Optimize-DeployForgeGaming `
    -ImagePath .\install.wim `
    -Profile competitive
```

### Example 3: Debloat Image

```powershell
# Remove bloatware (moderate level)
Remove-DeployForgeBloatware `
    -ImagePath .\install.wim `
    -Level moderate
```

### Example 4: Create Custom Preset

```powershell
# Create new preset based on gamer profile
New-DeployForgePreset -Name "MyGamingSetup" -Base gamer

# Apply the preset
Set-DeployForgePreset `
    -ImagePath .\install.wim `
    -PresetName "MyGamingSetup" `
    -Output .\custom.wim
```

### Example 5: Validation and Testing

```powershell
# Validate image
Test-DeployForgeImage -ImagePath .\custom.wim

# Analyze with HTML report
Get-DeployForgeImageInfo `
    -ImagePath .\custom.wim `
    -Format html `
    -Output .\analysis.html
```

### Example 6: Pipeline Usage

```powershell
# Pipeline example
Get-ChildItem *.wim | ForEach-Object {
    Test-DeployForgeImage -ImagePath $_.FullName
}
```

## Profiles

| Profile | Description |
|---------|-------------|
| `gamer` | Gaming optimizations, performance tweaks, gaming launchers |
| `developer` | Development tools, WSL2, Hyper-V, programming languages |
| `enterprise` | Enterprise security, management features |
| `student` | Balanced profile for students with productivity tools |
| `creator` | Creative tools for content creators (OBS, GIMP, etc.) |
| `custom` | Minimal profile for manual customization |

## Advanced Usage

### Using With Scripts

```powershell
# Script to process multiple images
$profiles = @('gamer', 'developer', 'enterprise')

foreach ($profile in $profiles) {
    $outputPath = ".\images\$profile.wim"

    Build-DeployForgeImage `
        -ImagePath .\base\install.wim `
        -Profile $profile `
        -Output $outputPath

    # Validate
    Test-DeployForgeImage -ImagePath $outputPath

    # Generate report
    Get-DeployForgeImageInfo `
        -ImagePath $outputPath `
        -Format html `
        -Output ".\reports\$profile-report.html"
}
```

### Error Handling

```powershell
try {
    Build-DeployForgeImage `
        -ImagePath .\install.wim `
        -Profile gamer `
        -Output .\gaming.wim `
        -ErrorAction Stop

    Write-Host "Build succeeded!" -ForegroundColor Green
}
catch {
    Write-Error "Build failed: $_"
    # Handle error
}
```

## Troubleshooting

### Python Not Found

```powershell
# Verify Python installation
python --version

# Install DeployForge
pip install deployforge
```

### Module Not Loading

```powershell
# Check module path
$env:PSModulePath

# Import with full path
Import-Module C:\Path\To\DeployForge.psm1 -Force
```

### DISM Errors

Ensure you're running PowerShell as Administrator for DISM operations.

```powershell
# Run as admin
Start-Process powershell -Verb RunAs
```

## Contributing

Contributions are welcome! Please see the main repository for guidelines.

## License

See LICENSE file in the main repository.

## Links

- [Documentation](https://github.com/YourOrg/DeployForge)
- [Issue Tracker](https://github.com/YourOrg/DeployForge/issues)
- [Examples](https://github.com/YourOrg/DeployForge/tree/main/examples)
