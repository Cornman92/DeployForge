#Requires -Version 5.1

<#
.SYNOPSIS
    WIM (Windows Imaging Format) handler.

.DESCRIPTION
    Handles mounting, modifying, and managing WIM image files using DISM.
#>

class DFWimHandler : DFBaseHandler {
    # Properties specific to WIM
    [int]$ImageCount
    [string[]]$ImageNames
    [hashtable[]]$ImageDetails

    # Constructor
    DFWimHandler([string]$imagePath) : base($imagePath) {
        $this.Metadata['Format'] = 'WIM'
        $this.PopulateImageInfo()
    }

    # Get WIM image information
    hidden [void] PopulateImageInfo() {
        try {
            $result = & dism.exe /Get-WimInfo /WimFile:"$($this.ImagePath)" 2>&1
            
            # Parse image count and names
            $this.ImageDetails = @()
            $currentImage = $null
            
            foreach ($line in $result) {
                if ($line -match "Index\s*:\s*(\d+)") {
                    if ($currentImage) {
                        $this.ImageDetails += $currentImage
                    }
                    $currentImage = @{ Index = [int]$Matches[1] }
                }
                elseif ($line -match "Name\s*:\s*(.+)") {
                    if ($currentImage) {
                        $currentImage['Name'] = $Matches[1].Trim()
                    }
                }
                elseif ($line -match "Description\s*:\s*(.+)") {
                    if ($currentImage) {
                        $currentImage['Description'] = $Matches[1].Trim()
                    }
                }
                elseif ($line -match "Size\s*:\s*(.+)") {
                    if ($currentImage) {
                        $currentImage['Size'] = $Matches[1].Trim()
                    }
                }
            }
            
            if ($currentImage) {
                $this.ImageDetails += $currentImage
            }

            $this.ImageCount = $this.ImageDetails.Count
            $this.ImageNames = $this.ImageDetails | ForEach-Object { $_['Name'] }
            
            Write-DFLog -Message "WIM contains $($this.ImageCount) image(s)" -Level Verbose
        }
        catch {
            Write-DFLog -Message "Failed to get WIM info: $_" -Level Warning
        }
    }

    # Mount the WIM image
    [string] Mount([string]$mountPoint, [int]$index) {
        $this.ValidateNotMounted()
        
        $this.Index = if ($index -gt 0) { $index } else { 1 }
        
        # Create mount point if not specified
        if (-not $mountPoint) {
            $mountPoint = $this.CreateTempMountPoint()
        }
        elseif (-not (Test-Path $mountPoint)) {
            New-Item -ItemType Directory -Path $mountPoint -Force | Out-Null
        }

        $this.MountStatus = [DFMountStatus]::Mounting
        Write-DFLog -Message "Mounting WIM index $($this.Index) to $mountPoint" -Level Info

        try {
            $dismArgs = @(
                "/Mount-Wim",
                "/WimFile:`"$($this.ImagePath)`"",
                "/Index:$($this.Index)",
                "/MountDir:`"$mountPoint`""
            )

            $result = & dism.exe $dismArgs 2>&1
            $exitCode = $LASTEXITCODE

            if ($exitCode -ne 0) {
                $this.MountStatus = [DFMountStatus]::Error
                throw [DFMountException]::new($this.ImagePath, $mountPoint, "DISM exit code: $exitCode")
            }

            $this.MountPoint = $mountPoint
            $this.MountStatus = [DFMountStatus]::Mounted
            $this.MountTime = Get-Date
            
            Write-DFLog -Message "WIM mounted successfully to $mountPoint" -Level Info
            return $mountPoint
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            $this.CleanupTempDirectory()
            throw
        }
    }

    # Dismount the WIM image
    [void] Dismount([bool]$saveChanges) {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            Write-DFLog -Message "WIM is not mounted" -Level Warning
            return
        }

        $this.MountStatus = [DFMountStatus]::Dismounting
        $action = if ($saveChanges) { "/Commit" } else { "/Discard" }
        
        Write-DFLog -Message "Dismounting WIM (SaveChanges: $saveChanges)" -Level Info

        try {
            $dismArgs = @(
                "/Unmount-Wim",
                "/MountDir:`"$($this.MountPoint)`"",
                $action
            )

            $result = & dism.exe $dismArgs 2>&1
            $exitCode = $LASTEXITCODE

            if ($exitCode -ne 0) {
                throw [DFDismountException]::new($this.MountPoint, $saveChanges, "DISM exit code: $exitCode")
            }

            $this.CleanupTempDirectory()
            $this.MountPoint = $null
            $this.MountStatus = [DFMountStatus]::NotMounted
            
            Write-DFLog -Message "WIM dismounted successfully" -Level Info
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw
        }
    }

    # List files in the mounted WIM
    [DFFileEntry[]] ListFiles([string]$path) {
        return $this.ListFilesFromMountPoint($path)
    }

    # Add file to mounted WIM
    [void] AddFile([string]$source, [string]$destination) {
        $this.AddFileToMountPoint($source, $destination)
    }

    # Remove file from mounted WIM
    [void] RemoveFile([string]$path) {
        $this.RemoveFileFromMountPoint($path)
    }

    # Extract file from mounted WIM
    [void] ExtractFile([string]$source, [string]$destination) {
        $this.ExtractFileFromMountPoint($source, $destination)
    }

    # Get WIM information
    [hashtable] GetInfo() {
        $fileInfo = Get-Item $this.ImagePath
        
        return @{
            Path = $this.ImagePath
            Format = 'WIM'
            Size = $fileInfo.Length
            SizeFormatted = $this.FormatFileSize($fileInfo.Length)
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            Index = $this.Index
            ImageCount = $this.ImageCount
            ImageNames = $this.ImageNames
            ImageDetails = $this.ImageDetails
            LastModified = $fileInfo.LastWriteTime
        }
    }

    # Export to new WIM with compression
    [void] ExportImage([string]$destinationPath, [string]$compression) {
        Write-DFLog -Message "Exporting WIM to $destinationPath with $compression compression" -Level Info

        $validCompression = @('none', 'fast', 'max', 'recovery')
        if ($compression -notin $validCompression) {
            $compression = 'max'
        }

        $dismArgs = @(
            "/Export-Image",
            "/SourceImageFile:`"$($this.ImagePath)`"",
            "/SourceIndex:$($this.Index)",
            "/DestinationImageFile:`"$destinationPath`"",
            "/Compress:$compression"
        )

        $result = & dism.exe $dismArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            throw [DFOperationException]::new("Export", $destinationPath, "DISM exit code: $exitCode")
        }

        Write-DFLog -Message "WIM exported successfully" -Level Info
    }

    # Optimize/cleanup the WIM
    [void] Optimize() {
        $this.ValidateMounted()
        
        Write-DFLog -Message "Optimizing WIM image" -Level Info

        $dismArgs = @(
            "/Image:`"$($this.MountPoint)`"",
            "/Cleanup-Image",
            "/StartComponentCleanup",
            "/ResetBase"
        )

        $result = & dism.exe $dismArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            Write-DFLog -Message "WIM optimization completed with warnings" -Level Warning
        }
        else {
            Write-DFLog -Message "WIM optimization completed" -Level Info
        }
    }

    # Helper to format file size
    hidden [string] FormatFileSize([long]$bytes) {
        if ($bytes -ge 1GB) { return "{0:N2} GB" -f ($bytes / 1GB) }
        if ($bytes -ge 1MB) { return "{0:N2} MB" -f ($bytes / 1MB) }
        if ($bytes -ge 1KB) { return "{0:N2} KB" -f ($bytes / 1KB) }
        return "$bytes bytes"
    }
}

Write-Verbose "Loaded DFWimHandler class"
