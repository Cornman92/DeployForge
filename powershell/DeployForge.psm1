# DeployForge PowerShell Module
# Version 0.6.0
#
# Provides PowerShell cmdlets for Windows image customization
#
# Installation:
#   Import-Module .\DeployForge.psm1
#
# Usage:
#   Build-DeployForgeImage -ImagePath .\install.wim -Profile gamer -Output .\custom.wim
#   Test-DeployForgeImage -ImagePath .\custom.wim
#   Get-DeployForgeProfile
#

# Module configuration
$script:DeployForgePath = $null
$script:PythonPath = $null

# Initialize module
function Initialize-DeployForge {
    <#
    .SYNOPSIS
    Initializes DeployForge module and checks dependencies.

    .DESCRIPTION
    Verifies Python and DeployForge installation, sets up paths.

    .EXAMPLE
    Initialize-DeployForge
    #>

    [CmdletBinding()]
    param()

    Write-Verbose "Initializing DeployForge module..."

    # Find Python
    $script:PythonPath = Get-Command python -ErrorAction SilentlyContinue
    if (-not $script:PythonPath) {
        throw "Python not found. Please install Python 3.8 or later."
    }

    # Verify Python version
    $pythonVersion = & python --version 2>&1
    Write-Verbose "Found Python: $pythonVersion"

    # Check if deployforge is installed
    $deployforgeCheck = & python -m deployforge --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "DeployForge Python package not found. Install with: pip install deployforge"
    }

    Write-Verbose "DeployForge module initialized"
}

# Build image with profile
function Build-DeployForgeImage {
    <#
    .SYNOPSIS
    Builds a customized Windows image using DeployForge.

    .DESCRIPTION
    Applies a profile to a Windows installation image, customizing it with
    performance optimizations, applications, and configurations.

    .PARAMETER ImagePath
    Path to the source Windows image (WIM, ESD, or ISO).

    .PARAMETER Profile
    Profile to apply (gamer, developer, enterprise, student, creator, custom).

    .PARAMETER Output
    Path for the output customized image.

    .PARAMETER Interactive
    Enable interactive mode with prompts.

    .EXAMPLE
    Build-DeployForgeImage -ImagePath .\install.wim -Profile gamer -Output .\gaming.wim

    .EXAMPLE
    Build-DeployForgeImage -ImagePath .\install.wim -Interactive
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('gamer', 'developer', 'enterprise', 'student', 'creator', 'custom')]
        [string]$Profile = 'gamer',

        [Parameter(Mandatory = $false)]
        [string]$Output,

        [Parameter(Mandatory = $false)]
        [switch]$Interactive
    )

    Write-Host "Building DeployForge image..." -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'build',
        $ImagePath
    )

    if ($Profile) {
        $args += @('--profile', $Profile)
    }

    if ($Output) {
        $args += @('--output', $Output)
    }

    if ($Interactive) {
        $args += '--interactive'
    }

    & python $args

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Build completed successfully!" -ForegroundColor Green
    } else {
        Write-Error "Build failed with exit code $LASTEXITCODE"
    }
}

# Apply profile to image
function Set-DeployForgeProfile {
    <#
    .SYNOPSIS
    Applies a profile to an existing Windows image.

    .DESCRIPTION
    Applies configuration profile to customize Windows image.

    .PARAMETER ImagePath
    Path to the Windows image.

    .PARAMETER Profile
    Profile name to apply.

    .PARAMETER Config
    Optional configuration file path.

    .EXAMPLE
    Set-DeployForgeProfile -ImagePath .\install.wim -Profile gamer
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $true)]
        [string]$Profile,

        [Parameter(Mandatory = $false)]
        [string]$Config
    )

    Write-Host "Applying profile: $Profile" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'apply-profile',
        $Profile
    )

    if ($Config) {
        $args += @('--config', $Config)
    }

    & python $args
}

# List available profiles
function Get-DeployForgeProfile {
    <#
    .SYNOPSIS
    Lists all available DeployForge profiles.

    .DESCRIPTION
    Displays all built-in and custom profiles with descriptions.

    .EXAMPLE
    Get-DeployForgeProfile
    #>

    [CmdletBinding()]
    param()

    Write-Host "Available DeployForge Profiles:" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'list-profiles'
    )

    & python $args
}

# Analyze image
function Get-DeployForgeImageInfo {
    <#
    .SYNOPSIS
    Analyzes a Windows image and generates a report.

    .DESCRIPTION
    Examines a Windows image and provides detailed information about
    features, applications, drivers, and configuration.

    .PARAMETER ImagePath
    Path to the Windows image.

    .PARAMETER Format
    Output format (text, json, html).

    .PARAMETER Output
    Path to save the report file.

    .EXAMPLE
    Get-DeployForgeImageInfo -ImagePath .\install.wim

    .EXAMPLE
    Get-DeployForgeImageInfo -ImagePath .\install.wim -Format html -Output .\report.html
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('text', 'json', 'html')]
        [string]$Format = 'text',

        [Parameter(Mandatory = $false)]
        [string]$Output
    )

    Write-Host "Analyzing image: $ImagePath" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'analyze',
        $ImagePath,
        '--format', $Format
    )

    if ($Output) {
        $args += @('--output', $Output)
    }

    & python $args
}

# Compare images
function Compare-DeployForgeImage {
    <#
    .SYNOPSIS
    Compares two Windows images and shows differences.

    .DESCRIPTION
    Analyzes two images and reports differences in features, applications,
    drivers, and configuration.

    .PARAMETER Image1
    Path to the first image.

    .PARAMETER Image2
    Path to the second image.

    .EXAMPLE
    Compare-DeployForgeImage -Image1 .\original.wim -Image2 .\customized.wim
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$Image1,

        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$Image2
    )

    Write-Host "Comparing images..." -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'diff',
        $Image1,
        $Image2
    )

    & python $args
}

# Test/validate image
function Test-DeployForgeImage {
    <#
    .SYNOPSIS
    Validates a Windows image for integrity and compatibility.

    .DESCRIPTION
    Runs validation checks on a Windows image to ensure it's
    properly configured and bootable.

    .PARAMETER ImagePath
    Path to the Windows image.

    .EXAMPLE
    Test-DeployForgeImage -ImagePath .\custom.wim
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath
    )

    Write-Host "Validating image: $ImagePath" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'validate',
        $ImagePath
    )

    & python $args

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Validation passed!" -ForegroundColor Green
    } else {
        Write-Warning "Validation found issues. Review the output above."
    }
}

# Create preset
function New-DeployForgePreset {
    <#
    .SYNOPSIS
    Creates a new customization preset.

    .DESCRIPTION
    Creates a new preset configuration that can be saved and reused.

    .PARAMETER Name
    Name for the new preset.

    .PARAMETER Base
    Optional base profile to extend.

    .EXAMPLE
    New-DeployForgePreset -Name "MyCustomGaming" -Base gamer
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $false)]
        [string]$Base
    )

    Write-Host "Creating preset: $Name" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'create-preset',
        $Name
    )

    if ($Base) {
        $args += @('--base', $Base)
    }

    & python $args
}

# List presets
function Get-DeployForgePreset {
    <#
    .SYNOPSIS
    Lists all available DeployForge presets.

    .DESCRIPTION
    Displays all custom presets with descriptions.

    .EXAMPLE
    Get-DeployForgePreset
    #>

    [CmdletBinding()]
    param()

    Write-Host "Available DeployForge Presets:" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'list-presets'
    )

    & python $args
}

# Apply preset
function Set-DeployForgePreset {
    <#
    .SYNOPSIS
    Applies a preset to an image.

    .DESCRIPTION
    Applies a saved preset configuration to a Windows image.

    .PARAMETER ImagePath
    Path to the Windows image.

    .PARAMETER PresetName
    Name of the preset to apply.

    .PARAMETER Output
    Optional output path for customized image.

    .EXAMPLE
    Set-DeployForgePreset -ImagePath .\install.wim -PresetName "MyCustomGaming"
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $true)]
        [string]$PresetName,

        [Parameter(Mandatory = $false)]
        [string]$Output
    )

    Write-Host "Applying preset: $PresetName" -ForegroundColor Cyan

    $args = @(
        '-m', 'deployforge.cli',
        'preset', 'apply',
        $PresetName,
        $ImagePath
    )

    if ($Output) {
        $args += @('--output', $Output)
    }

    & python $args
}

# Gaming optimization
function Optimize-DeployForgeGaming {
    <#
    .SYNOPSIS
    Applies gaming optimizations to an image.

    .DESCRIPTION
    Optimizes Windows image for gaming performance with network tweaks,
    Game Mode, and performance settings.

    .PARAMETER ImagePath
    Path to the Windows image.

    .PARAMETER Profile
    Gaming profile (competitive, balanced, quality, streaming).

    .EXAMPLE
    Optimize-DeployForgeGaming -ImagePath .\install.wim -Profile competitive
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('competitive', 'balanced', 'quality', 'streaming')]
        [string]$Profile = 'competitive'
    )

    Write-Host "Applying gaming optimizations ($Profile)..." -ForegroundColor Cyan

    $pythonScript = @"
from pathlib import Path
from deployforge.gaming import GamingOptimizer, GamingProfile

optimizer = GamingOptimizer(Path('$ImagePath'))
optimizer.mount()
optimizer.apply_profile(GamingProfile.$(($Profile).ToUpper()))
optimizer.unmount(save_changes=True)
print('Gaming optimizations applied successfully!')
"@

    $pythonScript | & python
}

# Debloat image
function Remove-DeployForgeBloatware {
    <#
    .SYNOPSIS
    Removes bloatware from Windows image.

    .DESCRIPTION
    Removes unwanted applications and features from Windows image
    while preserving Xbox and OneDrive.

    .PARAMETER ImagePath
    Path to the Windows image.

    .PARAMETER Level
    Debloat level (minimal, moderate, aggressive).

    .EXAMPLE
    Remove-DeployForgeBloatware -ImagePath .\install.wim -Level moderate
    #>

    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('minimal', 'moderate', 'aggressive')]
        [string]$Level = 'moderate'
    )

    Write-Host "Removing bloatware ($Level)..." -ForegroundColor Cyan

    $pythonScript = @"
from pathlib import Path
from deployforge.debloat import DebloatManager, DebloatLevel

debloat = DebloatManager(Path('$ImagePath'))
debloat.mount()
debloat.remove_bloatware(DebloatLevel.$(($Level).ToUpper()))
debloat.unmount(save_changes=True)
print('Bloatware removal complete!')
"@

    $pythonScript | & python
}

# Export functions
Export-ModuleMember -Function @(
    'Initialize-DeployForge',
    'Build-DeployForgeImage',
    'Set-DeployForgeProfile',
    'Get-DeployForgeProfile',
    'Get-DeployForgeImageInfo',
    'Compare-DeployForgeImage',
    'Test-DeployForgeImage',
    'New-DeployForgePreset',
    'Get-DeployForgePreset',
    'Set-DeployForgePreset',
    'Optimize-DeployForgeGaming',
    'Remove-DeployForgeBloatware'
)

# Initialize on import
Initialize-DeployForge

Write-Host "DeployForge PowerShell Module loaded!" -ForegroundColor Green
Write-Host "Use 'Get-Command -Module DeployForge' to see available cmdlets." -ForegroundColor Yellow
