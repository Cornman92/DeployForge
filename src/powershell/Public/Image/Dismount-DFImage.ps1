function Dismount-DFImage {
    <#
    .SYNOPSIS
        Unmounts a Windows image file.

    .DESCRIPTION
        The Dismount-DFImage cmdlet unmounts a Windows image that was previously
        mounted with Mount-DFImage, optionally saving or discarding changes.

    .PARAMETER MountPath
        Specifies the path where the image is mounted.

    .PARAMETER Save
        Commits changes made to the image. This is the default behavior.

    .PARAMETER Discard
        Discards all changes made to the image.

    .EXAMPLE
        Dismount-DFImage -MountPath "C:\Mount" -Save

        Unmounts the image at C:\Mount and saves all changes.

    .EXAMPLE
        Dismount-DFImage -MountPath "C:\Mount" -Discard

        Unmounts the image at C:\Mount without saving changes.

    .OUTPUTS
        PSCustomObject representing the operation result.

    .NOTES
        Requires administrative privileges.
    #>

    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipelineByPropertyName = $true)]
        [ValidateScript({Test-Path $_ -PathType Container})]
        [string]$MountPath,

        [Parameter(Mandatory = $false)]
        [switch]$Save,

        [Parameter(Mandatory = $false)]
        [switch]$Discard
    )

    begin {
        Write-Verbose "Dismount-DFImage: Starting unmount operation"

        if (-not (Test-Administrator)) {
            throw "This cmdlet requires administrative privileges."
        }

        if ($Save -and $Discard) {
            throw "Cannot specify both -Save and -Discard parameters."
        }

        # Default to Save if neither specified
        $commit = -not $Discard
    }

    process {
        try {
            $FullPath = Resolve-Path -Path $MountPath
            Write-Verbose "Dismount-DFImage: Mount path: $FullPath"

            # Verify image is mounted
            $mountedImages = Get-DismMountedImage
            $isMounted = $mountedImages | Where-Object { $_.MountPath -eq $FullPath }

            if (-not $isMounted) {
                throw "No image is mounted at path: $FullPath"
            }

            Write-Verbose "Dismount-DFImage: Unmounting image (Commit: $commit)"

            # Unmount using DISM
            Dismount-WindowsImage -Path $FullPath -Save:$commit -ErrorAction Stop

            if ($commit) {
                Write-Host "Successfully unmounted and saved image from: $FullPath" -ForegroundColor Green
            } else {
                Write-Host "Successfully unmounted and discarded changes from: $FullPath" -ForegroundColor Yellow
            }

            return [PSCustomObject]@{
                Success = $true
                MountPath = $FullPath
                ChangesSaved = $commit
                Timestamp = Get-Date
            }
        }
        catch {
            Write-Error "Failed to unmount image: $_"
            throw
        }
    }

    end {
        Write-Verbose "Dismount-DFImage: Operation completed"
    }
}

New-Alias -Name Dismount-WinImage -Value Dismount-DFImage -Force
