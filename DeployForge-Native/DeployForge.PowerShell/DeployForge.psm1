#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge - Enterprise Windows Deployment Suite

.DESCRIPTION
    DeployForge is a comprehensive Windows deployment automation suite that provides
    complete image customization capabilities. This native PowerShell implementation
    offers direct integration with Windows DISM and other deployment tools.

.NOTES
    Version:        2.0.0
    Author:         DeployForge Team
    Creation Date:  2024
    Purpose:        Windows image customization and deployment automation

.EXAMPLE
    Import-Module DeployForge
    $handler = Get-DFImageHandler -Path "C:\Images\install.wim"
    $handler.Mount()
    Optimize-DFGaming -MountPoint $handler.MountPoint -Profile Competitive
    $handler.Dismount($true)
#>

# Module-level variables
$script:ModuleVersion = '2.0.0'
$script:ModuleName = 'DeployForge'
$script:LogPath = Join-Path $env:TEMP "DeployForge"
$script:ConfigPath = Join-Path $env:APPDATA "DeployForge"
$script:RegisteredHandlers = @{}

# Ensure directories exist
if (-not (Test-Path $script:LogPath)) {
    New-Item -ItemType Directory -Path $script:LogPath -Force | Out-Null
}
if (-not (Test-Path $script:ConfigPath)) {
    New-Item -ItemType Directory -Path $script:ConfigPath -Force | Out-Null
}

#region Module Initialization

function Initialize-DeployForge {
    <#
    .SYNOPSIS
        Initializes the DeployForge module.

    .DESCRIPTION
        Performs module initialization, registers default handlers,
        and validates system requirements.
    #>
    [CmdletBinding()]
    param()

    Write-Verbose "Initializing DeployForge v$script:ModuleVersion..."

    # Check for administrator privileges
    if (-not (Test-DFAdministrator)) {
        Write-Warning "DeployForge requires administrator privileges for most operations."
    }

    # Check for DISM availability
    $dismPath = Get-Command dism.exe -ErrorAction SilentlyContinue
    if (-not $dismPath) {
        throw "DISM.exe not found. DeployForge requires Windows Deployment Image Servicing and Management."
    }

    # Register default image handlers
    Register-DefaultHandlers

    Write-Verbose "DeployForge initialized successfully."
}

function Register-DefaultHandlers {
    <#
    .SYNOPSIS
        Registers default image format handlers.
    #>
    [CmdletBinding()]
    param()

    # WIM Handler
    $script:RegisteredHandlers['.wim'] = 'DFWimHandler'
    
    # ISO Handler
    $script:RegisteredHandlers['.iso'] = 'DFIsoHandler'
    
    # ESD Handler
    $script:RegisteredHandlers['.esd'] = 'DFEsdHandler'
    
    # VHD/VHDX Handler
    $script:RegisteredHandlers['.vhd'] = 'DFVhdHandler'
    $script:RegisteredHandlers['.vhdx'] = 'DFVhdHandler'
    
    # PPKG Handler
    $script:RegisteredHandlers['.ppkg'] = 'DFPpkgHandler'

    Write-Verbose "Registered $($script:RegisteredHandlers.Count) image format handlers."
}

#endregion

#region Public Functions - Image Management

function Get-DFImageHandler {
    <#
    .SYNOPSIS
        Gets the appropriate handler for an image file.

    .DESCRIPTION
        Factory function that returns the correct handler class based on
        the image file extension.

    .PARAMETER Path
        Path to the image file.

    .EXAMPLE
        $handler = Get-DFImageHandler -Path "C:\Images\install.wim"
        $handler.Mount()

    .OUTPUTS
        DFBaseHandler - Handler instance for the image type
    #>
    [CmdletBinding()]
    [OutputType([DFBaseHandler])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$Path
    )

    $extension = [System.IO.Path]::GetExtension($Path).ToLower()
    
    if (-not $script:RegisteredHandlers.ContainsKey($extension)) {
        $supported = $script:RegisteredHandlers.Keys -join ', '
        throw [DFUnsupportedFormatException]::new(
            "Unsupported image format: $extension. Supported formats: $supported"
        )
    }

    $handlerType = $script:RegisteredHandlers[$extension]
    
    Write-DFLog -Message "Creating handler $handlerType for $Path" -Level Verbose
    
    switch ($handlerType) {
        'DFWimHandler' { return [DFWimHandler]::new($Path) }
        'DFIsoHandler' { return [DFIsoHandler]::new($Path) }
        'DFEsdHandler' { return [DFEsdHandler]::new($Path) }
        'DFVhdHandler' { return [DFVhdHandler]::new($Path) }
        'DFPpkgHandler' { return [DFPpkgHandler]::new($Path) }
        default { throw [DFUnsupportedFormatException]::new("No handler found for $extension") }
    }
}

function Get-DFSupportedFormats {
    <#
    .SYNOPSIS
        Gets list of supported image formats.

    .DESCRIPTION
        Returns all file extensions that DeployForge can handle.

    .EXAMPLE
        Get-DFSupportedFormats

    .OUTPUTS
        String[] - Array of supported file extensions
    #>
    [CmdletBinding()]
    [OutputType([string[]])]
    param()

    return $script:RegisteredHandlers.Keys | Sort-Object
}

function Mount-DFImage {
    <#
    .SYNOPSIS
        Mounts an image file.

    .DESCRIPTION
        Convenience function to mount an image and return the handler.

    .PARAMETER Path
        Path to the image file.

    .PARAMETER MountPoint
        Optional custom mount point.

    .PARAMETER Index
        Image index for WIM/ESD (default: 1).

    .EXAMPLE
        $handler = Mount-DFImage -Path "install.wim" -Index 1

    .OUTPUTS
        DFBaseHandler - Mounted handler instance
    #>
    [CmdletBinding()]
    [OutputType([DFBaseHandler])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$Path,

        [Parameter()]
        [string]$MountPoint,

        [Parameter()]
        [int]$Index = 1
    )

    $handler = Get-DFImageHandler -Path $Path
    
    if ($MountPoint) {
        $handler.Mount($MountPoint, $Index)
    }
    else {
        $handler.Mount($null, $Index)
    }

    return $handler
}

function Dismount-DFImage {
    <#
    .SYNOPSIS
        Dismounts an image.

    .DESCRIPTION
        Dismounts an image and optionally saves changes.

    .PARAMETER Handler
        Handler instance to dismount.

    .PARAMETER SaveChanges
        Whether to commit changes.

    .EXAMPLE
        Dismount-DFImage -Handler $handler -SaveChanges
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [DFBaseHandler]$Handler,

        [Parameter()]
        [switch]$SaveChanges
    )

    $Handler.Dismount($SaveChanges.IsPresent)
}

function Get-DFImageInfo {
    <#
    .SYNOPSIS
        Gets information about an image.

    .PARAMETER Path
        Path to the image file.

    .EXAMPLE
        Get-DFImageInfo -Path "install.wim"

    .OUTPUTS
        Hashtable - Image metadata
    #>
    [CmdletBinding()]
    [OutputType([hashtable])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$Path
    )

    $handler = Get-DFImageHandler -Path $Path
    return $handler.GetInfo()
}

function Get-DFImageFiles {
    <#
    .SYNOPSIS
        Lists files in a mounted image.

    .PARAMETER Handler
        Mounted handler instance.

    .PARAMETER Path
        Path within the image to list.

    .EXAMPLE
        Get-DFImageFiles -Handler $handler -Path "/Windows"

    .OUTPUTS
        Array of file information objects
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFBaseHandler]$Handler,

        [Parameter()]
        [string]$Path = "/"
    )

    return $Handler.ListFiles($Path)
}

function Add-DFImageFile {
    <#
    .SYNOPSIS
        Adds a file to a mounted image.

    .PARAMETER Handler
        Mounted handler instance.

    .PARAMETER Source
        Source file path.

    .PARAMETER Destination
        Destination path within image.

    .EXAMPLE
        Add-DFImageFile -Handler $handler -Source "script.ps1" -Destination "/Windows/Setup/Scripts/"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFBaseHandler]$Handler,

        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    $Handler.AddFile($Source, $Destination)
}

function Remove-DFImageFile {
    <#
    .SYNOPSIS
        Removes a file from a mounted image.

    .PARAMETER Handler
        Mounted handler instance.

    .PARAMETER Path
        Path within image to remove.

    .EXAMPLE
        Remove-DFImageFile -Handler $handler -Path "/Windows/Temp/file.tmp"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFBaseHandler]$Handler,

        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $Handler.RemoveFile($Path)
}

function Export-DFImageFile {
    <#
    .SYNOPSIS
        Extracts a file from a mounted image.

    .PARAMETER Handler
        Mounted handler instance.

    .PARAMETER Source
        Source path within image.

    .PARAMETER Destination
        Destination path on host.

    .EXAMPLE
        Export-DFImageFile -Handler $handler -Source "/Windows/notepad.exe" -Destination "C:\Temp"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [DFBaseHandler]$Handler,

        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    $Handler.ExtractFile($Source, $Destination)
}

#endregion

#region Aliases

Set-Alias -Name dfmount -Value Mount-DFImage
Set-Alias -Name dfdismount -Value Dismount-DFImage
Set-Alias -Name dfinfo -Value Get-DFImageInfo
Set-Alias -Name dfoptimize -Value Optimize-DFGaming
Set-Alias -Name dfdebloat -Value Remove-DFBloatware

#endregion

# Initialize module on import
Initialize-DeployForge

# Display welcome message
Write-Host @"

    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗   ██╗          ║
    ║   ██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝          ║
    ║   ██║  ██║█████╗  ██████╔╝██║     ██║   ██║ ╚████╔╝           ║
    ║   ██║  ██║██╔══╝  ██╔═══╝ ██║     ██║   ██║  ╚██╔╝            ║
    ║   ██████╔╝███████╗██║     ███████╗╚██████╔╝   ██║             ║
    ║   ╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝             ║
    ║                                                               ║
    ║   ███████╗ ██████╗ ██████╗  ██████╗ ███████╗                  ║
    ║   ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝                  ║
    ║   █████╗  ██║   ██║██████╔╝██║  ███╗█████╗                    ║
    ║   ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝                    ║
    ║   ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗                  ║
    ║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝                  ║
    ║                                                               ║
    ║   Enterprise Windows Deployment Suite v$($script:ModuleVersion.PadRight(24))║
    ║   Native PowerShell Implementation                           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Write-Host "  Use 'Get-Command -Module DeployForge' to see available commands." -ForegroundColor Yellow
Write-Host "  Use 'Get-DFSupportedFormats' to see supported image formats." -ForegroundColor Yellow
Write-Host ""
