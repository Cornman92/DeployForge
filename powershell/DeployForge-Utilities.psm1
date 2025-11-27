# DeployForge PowerShell Utilities
# Native Windows DISM and PowerShell functions for image management

#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Utility functions for Windows image manipulation using native DISM

.DESCRIPTION
    This module provides PowerShell functions that wrap native Windows DISM
    commands for managing Windows deployment images. All functions use
    native Windows tools without external dependencies.

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges, Windows 10/11 or Windows Server
#>

# Module variables
$script:MountPath = "$env:TEMP\DeployForge\Mount"
$script:LogPath = "$env:TEMP\DeployForge\Logs"

#region Helper Functions

<#
.SYNOPSIS
    Initialize DeployForge environment
#>
function Initialize-DeployForgeEnvironment {
    [CmdletBinding()]
    param()

    Write-Verbose "Initializing DeployForge environment..."

    # Create mount directory
    if (-not (Test-Path $script:MountPath)) {
        New-Item -ItemType Directory -Path $script:MountPath -Force | Out-Null
        Write-Verbose "Created mount directory: $script:MountPath"
    }

    # Create log directory
    if (-not (Test-Path $script:LogPath)) {
        New-Item -ItemType Directory -Path $script:LogPath -Force | Out-Null
        Write-Verbose "Created log directory: $script:LogPath"
    }

    # Verify DISM is available
    try {
        $dismVersion = (dism.exe /English /Online /Get-CurrentEdition | Select-String "Version").ToString()
        Write-Verbose "DISM is available: $dismVersion"
    }
    catch {
        throw "DISM is not available. Ensure you're running on Windows 10/11 or Windows Server."
    }
}

<#
.SYNOPSIS
    Get information about a Windows image
#>
function Get-WindowsImageInfo {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_})]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [int]$Index = 1
    )

    Write-Verbose "Getting image info for: $ImagePath (Index: $Index)"

    try {
        $imageInfo = Get-WindowsImage -ImagePath $ImagePath -Index $Index

        $info = [PSCustomObject]@{
            ImagePath        = $ImagePath
            Index            = $imageInfo.ImageIndex
            Name             = $imageInfo.ImageName
            Description      = $imageInfo.ImageDescription
            Size             = [math]::Round($imageInfo.ImageSize / 1GB, 2)
            Architecture     = $imageInfo.Architecture
            Version          = $imageInfo.Version
            SPBuild          = $imageInfo.SPBuild
            SPLevel          = $imageInfo.SPLevel
            Languages        = $imageInfo.Languages -join ', '
            DefaultLanguage  = $imageInfo.DefaultLanguage
            EditionId        = $imageInfo.EditionId
            InstallationType = $imageInfo.InstallationType
            ProductType      = $imageInfo.ProductType
            ProductSuite     = $imageInfo.ProductSuite
            SystemRoot       = $imageInfo.SystemRoot
        }

        return $info
    }
    catch {
        Write-Error "Failed to get image info: $_"
        throw
    }
}

<#
.SYNOPSIS
    Mount a Windows image
#>
function Mount-WindowsDeploymentImage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_})]
        [string]$ImagePath,

        [Parameter(Mandatory = $false)]
        [int]$Index = 1,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$ReadOnly
    )

    Initialize-DeployForgeEnvironment

    Write-Host "Mounting image: $ImagePath" -ForegroundColor Cyan
    Write-Host "Mount point: $MountPath" -ForegroundColor Cyan
    Write-Host "Index: $Index" -ForegroundColor Cyan

    # Check if already mounted
    $mounted = Get-WindowsImage -Mounted | Where-Object { $_.Path -eq $MountPath }
    if ($mounted) {
        Write-Warning "Image already mounted at $MountPath"
        return $MountPath
    }

    # Create mount directory
    if (-not (Test-Path $MountPath)) {
        New-Item -ItemType Directory -Path $MountPath -Force | Out-Null
    }

    try {
        $params = @{
            ImagePath = $ImagePath
            Index     = $Index
            Path      = $MountPath
        }

        if ($ReadOnly) {
            $params['ReadOnly'] = $true
        }

        Mount-WindowsImage @params -ErrorAction Stop | Out-Null

        Write-Host "✓ Image mounted successfully" -ForegroundColor Green
        return $MountPath
    }
    catch {
        Write-Error "Failed to mount image: $_"
        throw
    }
}

<#
.SYNOPSIS
    Dismount a Windows image
#>
function Dismount-WindowsDeploymentImage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$Save,

        [Parameter(Mandatory = $false)]
        [switch]$Discard
    )

    Write-Host "Dismounting image from: $MountPath" -ForegroundColor Cyan

    # Check if mounted
    $mounted = Get-WindowsImage -Mounted | Where-Object { $_.Path -eq $MountPath }
    if (-not $mounted) {
        Write-Warning "No image mounted at $MountPath"
        return
    }

    try {
        if ($Save) {
            Write-Host "Saving changes..." -ForegroundColor Yellow
            Dismount-WindowsImage -Path $MountPath -Save -ErrorAction Stop | Out-Null
            Write-Host "✓ Image dismounted and changes saved" -ForegroundColor Green
        }
        elseif ($Discard) {
            Write-Host "Discarding changes..." -ForegroundColor Yellow
            Dismount-WindowsImage -Path $MountPath -Discard -ErrorAction Stop | Out-Null
            Write-Host "✓ Image dismounted without saving" -ForegroundColor Green
        }
        else {
            # Default: save changes
            Dismount-WindowsImage -Path $MountPath -Save -ErrorAction Stop | Out-Null
            Write-Host "✓ Image dismounted and changes saved" -ForegroundColor Green
        }
    }
    catch {
        Write-Error "Failed to dismount image: $_"
        Write-Warning "Attempting cleanup..."

        try {
            Dismount-WindowsImage -Path $MountPath -Discard -ErrorAction Stop | Out-Null
            Write-Host "✓ Image dismounted (changes discarded)" -ForegroundColor Yellow
        }
        catch {
            Write-Error "Cleanup failed. You may need to run: DISM /Cleanup-Mountpoints"
        }
    }
}

<#
.SYNOPSIS
    Cleanup all mount points
#>
function Clear-DismMountPoints {
    [CmdletBinding()]
    param()

    Write-Host "Cleaning up DISM mount points..." -ForegroundColor Cyan

    try {
        $result = dism.exe /English /Cleanup-Mountpoints
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Mount points cleaned up successfully" -ForegroundColor Green
        }
        else {
            Write-Warning "Cleanup may have encountered issues"
        }
    }
    catch {
        Write-Error "Failed to cleanup mount points: $_"
    }
}

#endregion

#region Registry Operations

<#
.SYNOPSIS
    Load registry hive from mounted image
#>
function Mount-RegistryHive {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('SOFTWARE', 'SYSTEM', 'NTUSER.DAT', 'DEFAULT')]
        [string]$Hive,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [string]$KeyName = "HKLM\TEMP_HIVE"
    )

    $hivePaths = @{
        'SOFTWARE'    = "$MountPath\Windows\System32\config\SOFTWARE"
        'SYSTEM'      = "$MountPath\Windows\System32\config\SYSTEM"
        'DEFAULT'     = "$MountPath\Windows\System32\config\DEFAULT"
        'NTUSER.DAT'  = "$MountPath\Users\Default\NTUSER.DAT"
    }

    $hivePath = $hivePaths[$Hive]

    if (-not (Test-Path $hivePath)) {
        throw "Registry hive not found: $hivePath"
    }

    Write-Verbose "Loading registry hive: $hivePath to $KeyName"

    try {
        $result = reg.exe load $KeyName $hivePath
        if ($LASTEXITCODE -eq 0) {
            Write-Verbose "✓ Registry hive loaded successfully"
            return $KeyName
        }
        else {
            throw "reg load failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Error "Failed to load registry hive: $_"
        throw
    }
}

<#
.SYNOPSIS
    Unload registry hive
#>
function Dismount-RegistryHive {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$KeyName
    )

    Write-Verbose "Unloading registry hive: $KeyName"

    try {
        $result = reg.exe unload $KeyName
        if ($LASTEXITCODE -eq 0) {
            Write-Verbose "✓ Registry hive unloaded successfully"
        }
        else {
            throw "reg unload failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Error "Failed to unload registry hive: $_"
        throw
    }
}

<#
.SYNOPSIS
    Set registry value in offline image
#>
function Set-OfflineRegistryValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        $Value,

        [Parameter(Mandatory = $false)]
        [ValidateSet('String', 'ExpandString', 'Binary', 'DWord', 'MultiString', 'QWord')]
        [string]$Type = 'DWord'
    )

    try {
        # Ensure path exists
        if (-not (Test-Path "Registry::$Path")) {
            New-Item -Path "Registry::$Path" -Force | Out-Null
        }

        Set-ItemProperty -Path "Registry::$Path" -Name $Name -Value $Value -Type $Type -Force
        Write-Verbose "✓ Set registry value: $Path\$Name = $Value"
    }
    catch {
        Write-Error "Failed to set registry value: $_"
        throw
    }
}

#endregion

#region Package Management

<#
.SYNOPSIS
    Remove Windows capability from image
#>
function Remove-WindowsImageCapability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$CapabilityName,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath
    )

    Write-Host "Removing capability: $CapabilityName" -ForegroundColor Cyan

    try {
        Remove-WindowsCapability -Path $MountPath -Name $CapabilityName -ErrorAction Stop | Out-Null
        Write-Host "✓ Capability removed: $CapabilityName" -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to remove capability: $CapabilityName - $_"
    }
}

<#
.SYNOPSIS
    Remove Windows package from image
#>
function Remove-WindowsImagePackage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$PackageName,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath
    )

    Write-Host "Removing package: $PackageName" -ForegroundColor Cyan

    try {
        Remove-WindowsPackage -Path $MountPath -PackageName $PackageName -ErrorAction Stop | Out-Null
        Write-Host "✓ Package removed: $PackageName" -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to remove package: $PackageName - $_"
    }
}

<#
.SYNOPSIS
    Add Windows package to image
#>
function Add-WindowsImagePackage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_})]
        [string]$PackagePath,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath
    )

    Write-Host "Adding package: $PackagePath" -ForegroundColor Cyan

    try {
        Add-WindowsPackage -Path $MountPath -PackagePath $PackagePath -ErrorAction Stop | Out-Null
        Write-Host "✓ Package added successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to add package: $_"
        throw
    }
}

#endregion

#region Driver Management

<#
.SYNOPSIS
    Add drivers to Windows image
#>
function Add-WindowsImageDrivers {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_})]
        [string]$DriverPath,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$Recurse
    )

    Write-Host "Adding drivers from: $DriverPath" -ForegroundColor Cyan

    try {
        $params = @{
            Path       = $MountPath
            Driver     = $DriverPath
            ErrorAction = 'Stop'
        }

        if ($Recurse) {
            $params['Recurse'] = $true
        }

        Add-WindowsDriver @params | Out-Null
        Write-Host "✓ Drivers added successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to add drivers: $_"
        throw
    }
}

<#
.SYNOPSIS
    Get drivers in Windows image
#>
function Get-WindowsImageDrivers {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath
    )

    try {
        $drivers = Get-WindowsDriver -Path $MountPath
        return $drivers
    }
    catch {
        Write-Error "Failed to get drivers: $_"
        throw
    }
}

#endregion

#region Feature Management

<#
.SYNOPSIS
    Enable Windows optional feature
#>
function Enable-WindowsImageFeature {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FeatureName,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$All
    )

    Write-Host "Enabling feature: $FeatureName" -ForegroundColor Cyan

    try {
        $params = @{
            Path        = $MountPath
            FeatureName = $FeatureName
            ErrorAction = 'Stop'
        }

        if ($All) {
            $params['All'] = $true
        }

        Enable-WindowsOptionalFeature @params | Out-Null
        Write-Host "✓ Feature enabled: $FeatureName" -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to enable feature: $FeatureName - $_"
    }
}

<#
.SYNOPSIS
    Disable Windows optional feature
#>
function Disable-WindowsImageFeature {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$FeatureName,

        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$Remove
    )

    Write-Host "Disabling feature: $FeatureName" -ForegroundColor Cyan

    try {
        $params = @{
            Path        = $MountPath
            FeatureName = $FeatureName
            ErrorAction = 'Stop'
        }

        if ($Remove) {
            $params['Remove'] = $true
        }

        Disable-WindowsOptionalFeature @params | Out-Null
        Write-Host "✓ Feature disabled: $FeatureName" -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to disable feature: $FeatureName - $_"
    }
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Initialize-DeployForgeEnvironment',
    'Get-WindowsImageInfo',
    'Mount-WindowsDeploymentImage',
    'Dismount-WindowsDeploymentImage',
    'Clear-DismMountPoints',
    'Mount-RegistryHive',
    'Dismount-RegistryHive',
    'Set-OfflineRegistryValue',
    'Remove-WindowsImageCapability',
    'Remove-WindowsImagePackage',
    'Add-WindowsImagePackage',
    'Add-WindowsImageDrivers',
    'Get-WindowsImageDrivers',
    'Enable-WindowsImageFeature',
    'Disable-WindowsImageFeature'
)
