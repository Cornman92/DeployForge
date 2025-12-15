#Requires -Version 5.1

<#
.SYNOPSIS
    ISO image handler.

.DESCRIPTION
    Handles mounting and extracting ISO image files using Windows built-in capabilities.
#>

class DFIsoHandler : DFBaseHandler {
    # Properties specific to ISO
    [string]$DriveLetter
    [string]$VolumeLabel
    [long]$VolumeSize
    hidden [object]$DiskImage

    # Constructor
    DFIsoHandler([string]$imagePath) : base($imagePath) {
        $this.Metadata['Format'] = 'ISO'
    }

    # Mount the ISO image
    [string] Mount([string]$mountPoint, [int]$index) {
        $this.ValidateNotMounted()
        
        $this.MountStatus = [DFMountStatus]::Mounting
        Write-DFLog -Message "Mounting ISO: $($this.ImagePath)" -Level Info

        try {
            # Mount using PowerShell cmdlet
            $diskImage = Mount-DiskImage -ImagePath $this.ImagePath -PassThru -ErrorAction Stop
            $this.DiskImage = $diskImage

            # Get the drive letter
            $volume = Get-Volume -DiskImage $diskImage -ErrorAction SilentlyContinue
            
            if ($volume) {
                $this.DriveLetter = $volume.DriveLetter
                $this.VolumeLabel = $volume.FileSystemLabel
                $this.VolumeSize = $volume.Size
                $this.MountPoint = "$($this.DriveLetter):\"
            }
            else {
                # Try alternative method
                Start-Sleep -Milliseconds 500
                $partition = Get-Partition -DiskNumber $diskImage.Number -ErrorAction SilentlyContinue | 
                    Where-Object { $_.DriveLetter }
                
                if ($partition) {
                    $this.DriveLetter = $partition.DriveLetter
                    $this.MountPoint = "$($this.DriveLetter):\"
                }
                else {
                    throw "Could not determine drive letter for mounted ISO"
                }
            }

            $this.MountStatus = [DFMountStatus]::Mounted
            $this.MountTime = Get-Date
            
            Write-DFLog -Message "ISO mounted at $($this.MountPoint)" -Level Info
            return $this.MountPoint
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw [DFMountException]::new($this.ImagePath, $mountPoint, $_.Exception.Message)
        }
    }

    # Dismount the ISO image
    [void] Dismount([bool]$saveChanges) {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            Write-DFLog -Message "ISO is not mounted" -Level Warning
            return
        }

        if ($saveChanges) {
            Write-DFLog -Message "ISO format does not support in-place modifications. Changes not saved." -Level Warning
        }

        $this.MountStatus = [DFMountStatus]::Dismounting
        Write-DFLog -Message "Dismounting ISO" -Level Info

        try {
            Dismount-DiskImage -ImagePath $this.ImagePath -ErrorAction Stop
            
            $this.DriveLetter = $null
            $this.MountPoint = $null
            $this.DiskImage = $null
            $this.MountStatus = [DFMountStatus]::NotMounted
            
            Write-DFLog -Message "ISO dismounted successfully" -Level Info
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw [DFDismountException]::new($this.MountPoint, $saveChanges, $_.Exception.Message)
        }
    }

    # List files in the mounted ISO
    [DFFileEntry[]] ListFiles([string]$path) {
        return $this.ListFilesFromMountPoint($path)
    }

    # ISO is read-only - throw error for add
    [void] AddFile([string]$source, [string]$destination) {
        throw [DFOperationException]::new(
            "Add", $destination, "ISO format is read-only. Cannot add files directly."
        )
    }

    # ISO is read-only - throw error for remove
    [void] RemoveFile([string]$path) {
        throw [DFOperationException]::new(
            "Remove", $path, "ISO format is read-only. Cannot remove files directly."
        )
    }

    # Extract file from mounted ISO
    [void] ExtractFile([string]$source, [string]$destination) {
        $this.ExtractFileFromMountPoint($source, $destination)
    }

    # Get ISO information
    [hashtable] GetInfo() {
        $fileInfo = Get-Item $this.ImagePath
        
        $info = @{
            Path = $this.ImagePath
            Format = 'ISO 9660'
            Size = $fileInfo.Length
            SizeFormatted = $this.FormatFileSize($fileInfo.Length)
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            DriveLetter = $this.DriveLetter
            VolumeLabel = $this.VolumeLabel
            LastModified = $fileInfo.LastWriteTime
            ReadOnly = $true
        }

        return $info
    }

    # Extract entire ISO to directory
    [void] ExtractAll([string]$destination) {
        $this.ValidateMounted()
        
        Write-DFLog -Message "Extracting entire ISO to $destination" -Level Info
        
        if (-not (Test-Path $destination)) {
            New-Item -ItemType Directory -Path $destination -Force | Out-Null
        }

        Copy-Item -Path "$($this.MountPoint)*" -Destination $destination -Recurse -Force
        
        Write-DFLog -Message "ISO extraction complete" -Level Info
    }

    # Create new ISO from directory (static method)
    static [void] CreateIso([string]$sourceDirectory, [string]$outputPath, [string]$volumeLabel) {
        Write-DFLog -Message "Creating ISO from $sourceDirectory" -Level Info
        
        # Check for oscdimg.exe (from Windows ADK)
        $oscdimgPath = Get-Command oscdimg.exe -ErrorAction SilentlyContinue
        
        if (-not $oscdimgPath) {
            # Try common paths
            $adkPaths = @(
                "${env:ProgramFiles(x86)}\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe",
                "${env:ProgramFiles}\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
            )
            
            foreach ($path in $adkPaths) {
                if (Test-Path $path) {
                    $oscdimgPath = $path
                    break
                }
            }
        }

        if (-not $oscdimgPath) {
            throw [DFOperationException]::new(
                "CreateISO", $outputPath, 
                "oscdimg.exe not found. Install Windows ADK."
            )
        }

        # Build bootable ISO with UEFI support
        $etfsboot = Join-Path $sourceDirectory "boot\etfsboot.com"
        $efisys = Join-Path $sourceDirectory "efi\microsoft\boot\efisys.bin"

        $args = @("-m", "-o", "-u2", "-udfver102")
        
        if ((Test-Path $etfsboot) -and (Test-Path $efisys)) {
            $args += "-bootdata:2#p0,e,b$etfsboot#pEF,e,b$efisys"
        }
        elseif (Test-Path $etfsboot) {
            $args += "-b$etfsboot"
        }

        if ($volumeLabel) {
            $args += "-l$volumeLabel"
        }

        $args += $sourceDirectory
        $args += $outputPath

        & $oscdimgPath $args

        if ($LASTEXITCODE -ne 0) {
            throw [DFOperationException]::new("CreateISO", $outputPath, "oscdimg failed with exit code $LASTEXITCODE")
        }

        Write-DFLog -Message "ISO created successfully: $outputPath" -Level Info
    }

    # Helper to format file size
    hidden [string] FormatFileSize([long]$bytes) {
        if ($bytes -ge 1GB) { return "{0:N2} GB" -f ($bytes / 1GB) }
        if ($bytes -ge 1MB) { return "{0:N2} MB" -f ($bytes / 1MB) }
        if ($bytes -ge 1KB) { return "{0:N2} KB" -f ($bytes / 1KB) }
        return "$bytes bytes"
    }
}

Write-Verbose "Loaded DFIsoHandler class"
