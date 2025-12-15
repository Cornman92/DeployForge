#Requires -Version 5.1

<#
.SYNOPSIS
    Validation utilities for DeployForge.

.DESCRIPTION
    Provides input validation, path checking, and administrator verification.
#>

function Test-DFAdministrator {
    <#
    .SYNOPSIS
        Checks if running with administrator privileges.

    .OUTPUTS
        Boolean indicating admin status.

    .EXAMPLE
        if (Test-DFAdministrator) { Write-Host "Running as admin" }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-DFPath {
    <#
    .SYNOPSIS
        Validates a path exists and is accessible.

    .PARAMETER Path
        Path to validate.

    .PARAMETER Type
        Type of path (File, Directory, Any).

    .PARAMETER CreateIfNotExists
        Create directory if it doesn't exist.

    .OUTPUTS
        Boolean indicating path validity.

    .EXAMPLE
        Test-DFPath -Path "C:\Images\install.wim" -Type File
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [ValidateSet('File', 'Directory', 'Any')]
        [string]$Type = 'Any',

        [switch]$CreateIfNotExists
    )

    if ($CreateIfNotExists -and $Type -eq 'Directory') {
        if (-not (Test-Path $Path -PathType Container)) {
            try {
                New-Item -ItemType Directory -Path $Path -Force | Out-Null
                return $true
            }
            catch {
                return $false
            }
        }
    }

    switch ($Type) {
        'File' { return Test-Path $Path -PathType Leaf }
        'Directory' { return Test-Path $Path -PathType Container }
        'Any' { return Test-Path $Path }
    }

    return $false
}

function Test-DFImageFormat {
    <#
    .SYNOPSIS
        Validates that a file is a supported image format.

    .PARAMETER Path
        Path to the image file.

    .OUTPUTS
        Boolean indicating if format is supported.

    .EXAMPLE
        Test-DFImageFormat -Path "install.wim"
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $supportedExtensions = @('.wim', '.esd', '.iso', '.vhd', '.vhdx', '.ppkg')
    $extension = [System.IO.Path]::GetExtension($Path).ToLower()
    
    return $extension -in $supportedExtensions
}

function Test-DFDismAvailable {
    <#
    .SYNOPSIS
        Checks if DISM is available.

    .OUTPUTS
        Boolean indicating DISM availability.

    .EXAMPLE
        if (Test-DFDismAvailable) { Write-Host "DISM is available" }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    $dism = Get-Command dism.exe -ErrorAction SilentlyContinue
    return $null -ne $dism
}

function Test-DFWingetAvailable {
    <#
    .SYNOPSIS
        Checks if WinGet (Windows Package Manager) is available.

    .OUTPUTS
        Boolean indicating WinGet availability.

    .EXAMPLE
        if (Test-DFWingetAvailable) { Install-DFPackage "Git.Git" }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $winget = Get-Command winget -ErrorAction SilentlyContinue
        return $null -ne $winget
    }
    catch {
        return $false
    }
}

function Assert-DFAdministrator {
    <#
    .SYNOPSIS
        Throws if not running as administrator.

    .EXAMPLE
        Assert-DFAdministrator
    #>
    [CmdletBinding()]
    param()

    if (-not (Test-DFAdministrator)) {
        throw [DFValidationException]::new(
            "Administrator privileges required. Please run as Administrator."
        )
    }
}

function Assert-DFPath {
    <#
    .SYNOPSIS
        Throws if path doesn't exist.

    .PARAMETER Path
        Path to validate.

    .PARAMETER Type
        Expected path type.

    .EXAMPLE
        Assert-DFPath -Path "C:\install.wim" -Type File
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [ValidateSet('File', 'Directory', 'Any')]
        [string]$Type = 'Any'
    )

    if (-not (Test-DFPath -Path $Path -Type $Type)) {
        throw [DFValidationException]::new(
            "Path", $Path, "$Type not found: $Path"
        )
    }
}

function Confirm-DFImageFormat {
    <#
    .SYNOPSIS
        Throws if image format is not supported.

    .PARAMETER Path
        Path to the image file.

    .EXAMPLE
        Confirm-DFImageFormat -Path "install.wim"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-DFImageFormat -Path $Path)) {
        $extension = [System.IO.Path]::GetExtension($Path)
        $supported = Get-DFSupportedFormats
        throw [DFUnsupportedFormatException]::new($extension, $supported)
    }
}

function Get-DFSystemInfo {
    <#
    .SYNOPSIS
        Gets system information for DeployForge operations.

    .OUTPUTS
        Hashtable with system information.

    .EXAMPLE
        $info = Get-DFSystemInfo
    #>
    [CmdletBinding()]
    [OutputType([hashtable])]
    param()

    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $mem = Get-CimInstance Win32_ComputerSystem

    return @{
        ComputerName = $env:COMPUTERNAME
        OSName = $os.Caption
        OSVersion = $os.Version
        OSBuild = $os.BuildNumber
        Architecture = $os.OSArchitecture
        Processor = $cpu.Name
        ProcessorCores = $cpu.NumberOfCores
        ProcessorLogical = $cpu.NumberOfLogicalProcessors
        TotalMemoryGB = [math]::Round($mem.TotalPhysicalMemory / 1GB, 2)
        FreeMemoryGB = [math]::Round($os.FreePhysicalMemory * 1KB / 1GB, 2)
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        IsAdministrator = Test-DFAdministrator
        DismAvailable = Test-DFDismAvailable
        WingetAvailable = Test-DFWingetAvailable
        WindowsADK = Test-Path "${env:ProgramFiles(x86)}\Windows Kits\10\Assessment and Deployment Kit"
    }
}

function Test-DFMountPoint {
    <#
    .SYNOPSIS
        Checks if a path is a valid mount point.

    .PARAMETER Path
        Path to check.

    .OUTPUTS
        Boolean indicating if path is a valid mount point.
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path -PathType Container)) {
        return $false
    }

    # Check if it's a DISM mount point
    $dismMounts = & dism.exe /Get-MountedImageInfo 2>$null
    
    foreach ($line in $dismMounts) {
        if ($line -match "Mount Dir\s*:\s*(.+)" -and $Matches[1].Trim() -eq $Path) {
            return $true
        }
    }

    return $false
}

function Get-DFMountedImages {
    <#
    .SYNOPSIS
        Gets all currently mounted images.

    .OUTPUTS
        Array of mounted image information.

    .EXAMPLE
        Get-DFMountedImages | Format-Table
    #>
    [CmdletBinding()]
    [OutputType([hashtable[]])]
    param()

    $mountedImages = @()
    $dismOutput = & dism.exe /Get-MountedImageInfo 2>$null

    $currentImage = $null
    foreach ($line in $dismOutput) {
        if ($line -match "Mount Dir\s*:\s*(.+)") {
            if ($currentImage) {
                $mountedImages += $currentImage
            }
            $currentImage = @{
                MountDir = $Matches[1].Trim()
            }
        }
        elseif ($line -match "Image File\s*:\s*(.+)") {
            if ($currentImage) {
                $currentImage['ImageFile'] = $Matches[1].Trim()
            }
        }
        elseif ($line -match "Image Index\s*:\s*(\d+)") {
            if ($currentImage) {
                $currentImage['ImageIndex'] = [int]$Matches[1]
            }
        }
        elseif ($line -match "Status\s*:\s*(.+)") {
            if ($currentImage) {
                $currentImage['Status'] = $Matches[1].Trim()
            }
        }
    }

    if ($currentImage) {
        $mountedImages += $currentImage
    }

    return $mountedImages
}

Write-Verbose "Loaded DeployForge validation utilities"
