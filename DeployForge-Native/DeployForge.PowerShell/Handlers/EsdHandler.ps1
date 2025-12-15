#Requires -Version 5.1

<#
.SYNOPSIS
    ESD (Electronic Software Delivery) handler.

.DESCRIPTION
    Handles ESD compressed WIM files. ESD files are highly compressed WIM files
    that can be converted to standard WIM for modification.
#>

class DFEsdHandler : DFBaseHandler {
    # Properties specific to ESD
    [int]$ImageCount
    [string[]]$ImageNames
    [hashtable[]]$ImageDetails
    [bool]$IsEncrypted
    hidden [string]$ConvertedWimPath
    hidden [DFWimHandler]$WimHandler

    # Constructor
    DFEsdHandler([string]$imagePath) : base($imagePath) {
        $this.Metadata['Format'] = 'ESD'
        $this.PopulateImageInfo()
    }

    # Get ESD image information
    hidden [void] PopulateImageInfo() {
        try {
            $result = & dism.exe /Get-WimInfo /WimFile:"$($this.ImagePath)" 2>&1
            
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
            }
            
            if ($currentImage) {
                $this.ImageDetails += $currentImage
            }

            $this.ImageCount = $this.ImageDetails.Count
            $this.ImageNames = $this.ImageDetails | ForEach-Object { $_['Name'] }

            # Check if encrypted (Windows Store ESD files)
            $this.IsEncrypted = $false
            foreach ($line in $result) {
                if ($line -match "encrypted") {
                    $this.IsEncrypted = $true
                    break
                }
            }
            
            Write-DFLog -Message "ESD contains $($this.ImageCount) image(s), Encrypted: $($this.IsEncrypted)" -Level Verbose
        }
        catch {
            Write-DFLog -Message "Failed to get ESD info: $_" -Level Warning
        }
    }

    # Convert ESD to WIM for mounting
    hidden [string] ConvertToWim() {
        $tempWim = Join-Path $env:TEMP "DeployForge_ESD_$(Get-Random -Minimum 10000 -Maximum 99999).wim"
        
        Write-DFLog -Message "Converting ESD to WIM for modification..." -Level Info

        $dismArgs = @(
            "/Export-Image",
            "/SourceImageFile:`"$($this.ImagePath)`"",
            "/SourceIndex:$($this.Index)",
            "/DestinationImageFile:`"$tempWim`"",
            "/Compress:max"
        )

        $result = & dism.exe $dismArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            throw [DFOperationException]::new("ConvertESD", $this.ImagePath, "DISM export failed: $exitCode")
        }

        $this.ConvertedWimPath = $tempWim
        Write-DFLog -Message "ESD converted to temporary WIM: $tempWim" -Level Info
        return $tempWim
    }

    # Mount the ESD (converts to WIM first)
    [string] Mount([string]$mountPoint, [int]$index) {
        $this.ValidateNotMounted()
        
        if ($this.IsEncrypted) {
            throw [DFOperationException]::new(
                "Mount", $this.ImagePath, 
                "Encrypted ESD files cannot be mounted. Convert to WIM first."
            )
        }

        $this.Index = if ($index -gt 0) { $index } else { 1 }
        
        $this.MountStatus = [DFMountStatus]::Mounting
        Write-DFLog -Message "Mounting ESD index $($this.Index)" -Level Info

        try {
            # Convert ESD to WIM
            $wimPath = $this.ConvertToWim()
            
            # Create WIM handler for the converted file
            $this.WimHandler = [DFWimHandler]::new($wimPath)
            
            # Mount the WIM
            $mountedPath = $this.WimHandler.Mount($mountPoint, 1)
            
            $this.MountPoint = $mountedPath
            $this.MountStatus = [DFMountStatus]::Mounted
            $this.MountTime = Get-Date
            
            Write-DFLog -Message "ESD mounted at $mountedPath" -Level Info
            return $mountedPath
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            $this.CleanupConvertedWim()
            throw [DFMountException]::new($this.ImagePath, $mountPoint, $_.Exception.Message)
        }
    }

    # Cleanup converted WIM
    hidden [void] CleanupConvertedWim() {
        if ($this.ConvertedWimPath -and (Test-Path $this.ConvertedWimPath)) {
            Remove-Item $this.ConvertedWimPath -Force -ErrorAction SilentlyContinue
            $this.ConvertedWimPath = $null
        }
    }

    # Dismount the ESD
    [void] Dismount([bool]$saveChanges) {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            Write-DFLog -Message "ESD is not mounted" -Level Warning
            return
        }

        $this.MountStatus = [DFMountStatus]::Dismounting

        try {
            if ($this.WimHandler) {
                $this.WimHandler.Dismount($saveChanges)
                $this.WimHandler = $null
            }

            if ($saveChanges) {
                Write-DFLog -Message "Changes saved to temporary WIM. Convert back to ESD if needed." -Level Info
                Write-DFLog -Message "Modified WIM location: $($this.ConvertedWimPath)" -Level Info
            }
            else {
                $this.CleanupConvertedWim()
            }
            
            $this.MountPoint = $null
            $this.MountStatus = [DFMountStatus]::NotMounted
            
            Write-DFLog -Message "ESD dismounted successfully" -Level Info
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw
        }
    }

    # Export modified WIM back to ESD
    [void] ExportAsEsd([string]$destinationPath) {
        if (-not $this.ConvertedWimPath -or -not (Test-Path $this.ConvertedWimPath)) {
            throw [DFOperationException]::new(
                "ExportESD", $destinationPath, 
                "No modified WIM available. Mount and modify the image first."
            )
        }

        Write-DFLog -Message "Exporting to ESD: $destinationPath" -Level Info

        $dismArgs = @(
            "/Export-Image",
            "/SourceImageFile:`"$($this.ConvertedWimPath)`"",
            "/SourceIndex:1",
            "/DestinationImageFile:`"$destinationPath`"",
            "/Compress:recovery"
        )

        $result = & dism.exe $dismArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            throw [DFOperationException]::new("ExportESD", $destinationPath, "DISM export failed: $exitCode")
        }

        Write-DFLog -Message "ESD export complete" -Level Info
    }

    # List files
    [DFFileEntry[]] ListFiles([string]$path) {
        if ($this.WimHandler) {
            return $this.WimHandler.ListFiles($path)
        }
        return $this.ListFilesFromMountPoint($path)
    }

    # Add file
    [void] AddFile([string]$source, [string]$destination) {
        if ($this.WimHandler) {
            $this.WimHandler.AddFile($source, $destination)
        }
        else {
            $this.AddFileToMountPoint($source, $destination)
        }
    }

    # Remove file
    [void] RemoveFile([string]$path) {
        if ($this.WimHandler) {
            $this.WimHandler.RemoveFile($path)
        }
        else {
            $this.RemoveFileFromMountPoint($path)
        }
    }

    # Extract file
    [void] ExtractFile([string]$source, [string]$destination) {
        if ($this.WimHandler) {
            $this.WimHandler.ExtractFile($source, $destination)
        }
        else {
            $this.ExtractFileFromMountPoint($source, $destination)
        }
    }

    # Get ESD information
    [hashtable] GetInfo() {
        $fileInfo = Get-Item $this.ImagePath
        
        return @{
            Path = $this.ImagePath
            Format = 'ESD'
            Size = $fileInfo.Length
            SizeFormatted = $this.FormatFileSize($fileInfo.Length)
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            Index = $this.Index
            ImageCount = $this.ImageCount
            ImageNames = $this.ImageNames
            ImageDetails = $this.ImageDetails
            IsEncrypted = $this.IsEncrypted
            ConvertedWimPath = $this.ConvertedWimPath
            LastModified = $fileInfo.LastWriteTime
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

Write-Verbose "Loaded DFEsdHandler class"
