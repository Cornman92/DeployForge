function Mount-DFImage {
    <#
    .SYNOPSIS
        Mounts a Windows image file for editing.

    .DESCRIPTION
        The Mount-DFImage cmdlet mounts a Windows image file (WIM, ISO, VHDX, VHD, ESD, IMG)
        to a specified mount point for servicing and customization.

    .PARAMETER Path
        Specifies the path to the image file to mount.

    .PARAMETER Index
        Specifies the index of the image within the WIM/ESD file. Default is 1.

    .PARAMETER MountPath
        Specifies the path where the image will be mounted. If not specified,
        a temporary mount path will be created.

    .PARAMETER ReadOnly
        Mounts the image in read-only mode. Changes cannot be saved.

    .PARAMETER CheckIntegrity
        Verifies the integrity of the image before mounting.

    .EXAMPLE
        Mount-DFImage -Path "C:\ISOs\Win11.iso" -Index 1

        Mounts the first image from Win11.iso to a temporary mount point.

    .EXAMPLE
        Mount-DFImage -Path "C:\Images\install.wim" -Index 1 -MountPath "C:\Mount" -CheckIntegrity

        Mounts the first image from install.wim to C:\Mount after verifying integrity.

    .OUTPUTS
        PSCustomObject representing the mounted image session.

    .NOTES
        Requires administrative privileges.
        Supported formats: ISO, WIM, ESD, VHDX, VHD, IMG
    #>

    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true)]
        [ValidateScript({Test-Path $_ -PathType Leaf})]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [ValidateRange(1, [int]::MaxValue)]
        [int]$Index = 1,

        [Parameter(Mandatory = $false)]
        [string]$MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$ReadOnly,

        [Parameter(Mandatory = $false)]
        [switch]$CheckIntegrity
    )

    begin {
        Write-Verbose "Mount-DFImage: Starting image mount operation"

        # Check if running as administrator
        if (-not (Test-Administrator)) {
            throw "This cmdlet requires administrative privileges. Please run as Administrator."
        }
    }

    process {
        try {
            # Resolve full path
            $FullPath = Resolve-Path -Path $Path
            Write-Verbose "Mount-DFImage: Image path: $FullPath"

            # Detect image format
            $ImageFormat = Get-ImageFormat -Path $FullPath
            Write-Verbose "Mount-DFImage: Detected format: $ImageFormat"

            # Create mount path if not specified
            if (-not $MountPath) {
                $MountPath = New-TemporaryMountPath
                Write-Verbose "Mount-DFImage: Created temporary mount path: $MountPath"
            }

            # Ensure mount directory exists
            if (-not (Test-Path $MountPath)) {
                New-Item -Path $MountPath -ItemType Directory -Force | Out-Null
            }

            # Check integrity if requested
            if ($CheckIntegrity) {
                Write-Verbose "Mount-DFImage: Checking image integrity..."
                $IntegrityCheck = Test-ImageIntegrity -Path $FullPath -Format $ImageFormat
                if (-not $IntegrityCheck.IsValid) {
                    throw "Image integrity check failed: $($IntegrityCheck.ErrorMessage)"
                }
            }

            # Mount based on format
            $Session = switch ($ImageFormat) {
                'WIM' {
                    Mount-WimImage -Path $FullPath -Index $Index -MountPath $MountPath -ReadOnly:$ReadOnly
                }
                'ESD' {
                    Mount-EsdImage -Path $FullPath -Index $Index -MountPath $MountPath -ReadOnly:$ReadOnly
                }
                'ISO' {
                    Mount-IsoImage -Path $FullPath -MountPath $MountPath
                }
                'VHDX' {
                    Mount-VhdxImage -Path $FullPath -MountPath $MountPath -ReadOnly:$ReadOnly
                }
                'VHD' {
                    Mount-VhdImage -Path $FullPath -MountPath $MountPath -ReadOnly:$ReadOnly
                }
                'IMG' {
                    Mount-ImgImage -Path $FullPath -MountPath $MountPath
                }
                default {
                    throw "Unsupported image format: $ImageFormat"
                }
            }

            Write-Host "Successfully mounted image to: $MountPath" -ForegroundColor Green
            return $Session

        }
        catch {
            Write-Error "Failed to mount image: $_"

            # Cleanup on failure
            if ($MountPath -and (Test-Path $MountPath)) {
                try {
                    Remove-Item -Path $MountPath -Force -Recurse -ErrorAction SilentlyContinue
                }
                catch {
                    Write-Warning "Failed to cleanup mount path: $_"
                }
            }

            throw
        }
    }

    end {
        Write-Verbose "Mount-DFImage: Operation completed"
    }
}

# Alias for compatibility
New-Alias -Name Mount-WinImage -Value Mount-DFImage -Force
