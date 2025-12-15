#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge PowerShell Backend Module
    
.DESCRIPTION
    Provides comprehensive Windows deployment image management and customization
    capabilities using native Windows tools (DISM, Registry, diskpart).
    
.NOTES
    Author: DeployForge Team
    Version: 2.0.0
    Requires: Administrator privileges, Windows 10/11 or Windows Server
#>

# Module variables
$script:ModuleRoot = $PSScriptRoot
$script:MountPath = "$env:TEMP\DeployForge\Mount"
$script:LogPath = "$env:TEMP\DeployForge\Logs"
$script:CurrentOperation = $null

# Initialize module
function Initialize-DeployForge {
    <#
    .SYNOPSIS
        Initializes the DeployForge module environment.
        
    .DESCRIPTION
        Creates necessary directories, verifies DISM availability, and sets up logging.
    #>
    [CmdletBinding()]
    param()
    
    # Create required directories
    $directories = @(
        $script:MountPath,
        $script:LogPath,
        "$env:TEMP\DeployForge\Temp",
        "$env:TEMP\DeployForge\Backups"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Verbose "Created directory: $dir"
        }
    }
    
    # Verify DISM availability
    try {
        $null = Get-Command dism.exe -ErrorAction Stop
        Write-Verbose "DISM is available"
    }
    catch {
        throw "DISM is not available. This module requires Windows 10/11 or Windows Server."
    }
    
    # Verify running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "This module requires administrator privileges. Please run PowerShell as Administrator."
    }
    
    Write-Verbose "DeployForge module initialized successfully"
}

# Get module paths
function Get-DeployForgePaths {
    <#
    .SYNOPSIS
        Returns the configured paths for DeployForge operations.
    #>
    [CmdletBinding()]
    param()
    
    return [PSCustomObject]@{
        ModuleRoot = $script:ModuleRoot
        MountPath = $script:MountPath
        LogPath = $script:LogPath
        TempPath = "$env:TEMP\DeployForge\Temp"
        BackupPath = "$env:TEMP\DeployForge\Backups"
    }
}

# Set custom mount path
function Set-DeployForgeMountPath {
    <#
    .SYNOPSIS
        Sets a custom mount path for image operations.
        
    .PARAMETER Path
        The path to use for mounting images.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
    
    $script:MountPath = $Path
    Write-Verbose "Mount path set to: $Path"
}

# Check if image is mounted
function Test-ImageMounted {
    <#
    .SYNOPSIS
        Tests if an image is currently mounted at the specified path.
        
    .PARAMETER MountPath
        The mount path to check.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath
    )
    
    try {
        $mounted = Get-WindowsImage -Mounted -ErrorAction SilentlyContinue | 
            Where-Object { $_.Path -eq $MountPath }
        return $null -ne $mounted
    }
    catch {
        return $false
    }
}

# Get currently mounted image info
function Get-MountedImageInfo {
    <#
    .SYNOPSIS
        Gets information about currently mounted images.
    #>
    [CmdletBinding()]
    param()
    
    try {
        return Get-WindowsImage -Mounted -ErrorAction SilentlyContinue
    }
    catch {
        return $null
    }
}

# Cleanup stale mounts
function Clear-StaleMounts {
    <#
    .SYNOPSIS
        Cleans up any stale DISM mount points.
    #>
    [CmdletBinding()]
    param()
    
    Write-Verbose "Cleaning up stale DISM mount points..."
    
    try {
        $result = & dism.exe /English /Cleanup-Mountpoints 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Verbose "Mount points cleaned up successfully"
            return $true
        }
        else {
            Write-Warning "Mount point cleanup may have encountered issues"
            return $false
        }
    }
    catch {
        Write-Error "Failed to cleanup mount points: $_"
        return $false
    }
}

# Export helper functions
Export-ModuleMember -Function @(
    'Initialize-DeployForge',
    'Get-DeployForgePaths',
    'Set-DeployForgeMountPath',
    'Test-ImageMounted',
    'Get-MountedImageInfo',
    'Clear-StaleMounts'
)

# Initialize on import
Initialize-DeployForge

Write-Host "DeployForge PowerShell Backend v2.0.0 loaded" -ForegroundColor Green
Write-Host "Use 'Get-Command -Module DeployForge' to see available commands" -ForegroundColor Yellow
