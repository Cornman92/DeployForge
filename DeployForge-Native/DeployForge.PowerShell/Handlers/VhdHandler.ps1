#Requires -Version 5.1

<#
.SYNOPSIS
    VHD/VHDX handler.

.DESCRIPTION
    Handles mounting and modifying VHD and VHDX virtual hard disk files.
#>

class DFVhdHandler : DFBaseHandler {
    # Properties specific to VHD
    [string]$DriveLetter
    [string]$VhdType  # Fixed, Dynamic, Differencing
    [long]$VirtualSize
    [int]$DiskNumber
    [int]$PartitionNumber
    hidden [object]$DiskImage

    # Constructor
    DFVhdHandler([string]$imagePath) : base($imagePath) {
        $extension = [System.IO.Path]::GetExtension($imagePath).ToLower()
        $this.Metadata['Format'] = if ($extension -eq '.vhdx') { 'VHDX' } else { 'VHD' }
        $this.PartitionNumber = 1  # Default to first partition
    }

    # Mount the VHD/VHDX
    [string] Mount([string]$mountPoint, [int]$partition) {
        $this.ValidateNotMounted()
        
        $this.PartitionNumber = if ($partition -gt 0) { $partition } else { 1 }
        
        $this.MountStatus = [DFMountStatus]::Mounting
        Write-DFLog -Message "Mounting VHD: $($this.ImagePath)" -Level Info

        try {
            # Mount the VHD
            $diskImage = Mount-DiskImage -ImagePath $this.ImagePath -PassThru -ErrorAction Stop
            $this.DiskImage = $diskImage

            # Wait for disk to be ready
            Start-Sleep -Milliseconds 500

            # Get disk number
            $disk = Get-DiskImage -ImagePath $this.ImagePath | Get-Disk
            $this.DiskNumber = $disk.Number
            $this.VhdType = $disk.PartitionStyle
            $this.VirtualSize = $disk.Size

            # Get the partition and drive letter
            $partition = Get-Partition -DiskNumber $this.DiskNumber -ErrorAction SilentlyContinue |
                Where-Object { $_.Type -ne 'Reserved' -and $_.Type -ne 'Unknown' } |
                Select-Object -Index ($this.PartitionNumber - 1)

            if ($partition) {
                if ($partition.DriveLetter) {
                    $this.DriveLetter = $partition.DriveLetter
                }
                else {
                    # Assign a drive letter
                    $availableLetter = (68..90 | ForEach-Object { [char]$_ } | 
                        Where-Object { -not (Test-Path "$($_):") } | 
                        Select-Object -First 1)
                    
                    $partition | Set-Partition -NewDriveLetter $availableLetter
                    $this.DriveLetter = $availableLetter
                }
                
                $this.MountPoint = "$($this.DriveLetter):\"
            }
            else {
                throw "Could not find partition $($this.PartitionNumber) in VHD"
            }

            $this.MountStatus = [DFMountStatus]::Mounted
            $this.MountTime = Get-Date
            
            Write-DFLog -Message "VHD mounted at $($this.MountPoint)" -Level Info
            return $this.MountPoint
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            # Try to cleanup on failure
            try { Dismount-DiskImage -ImagePath $this.ImagePath -ErrorAction SilentlyContinue } catch {}
            throw [DFMountException]::new($this.ImagePath, $mountPoint, $_.Exception.Message)
        }
    }

    # Dismount the VHD/VHDX
    [void] Dismount([bool]$saveChanges) {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            Write-DFLog -Message "VHD is not mounted" -Level Warning
            return
        }

        $this.MountStatus = [DFMountStatus]::Dismounting
        Write-DFLog -Message "Dismounting VHD (changes are automatically saved)" -Level Info

        try {
            Dismount-DiskImage -ImagePath $this.ImagePath -ErrorAction Stop
            
            $this.DriveLetter = $null
            $this.MountPoint = $null
            $this.DiskImage = $null
            $this.DiskNumber = 0
            $this.MountStatus = [DFMountStatus]::NotMounted
            
            Write-DFLog -Message "VHD dismounted successfully" -Level Info
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw [DFDismountException]::new($this.MountPoint, $saveChanges, $_.Exception.Message)
        }
    }

    # List files
    [DFFileEntry[]] ListFiles([string]$path) {
        return $this.ListFilesFromMountPoint($path)
    }

    # Add file
    [void] AddFile([string]$source, [string]$destination) {
        $this.AddFileToMountPoint($source, $destination)
    }

    # Remove file
    [void] RemoveFile([string]$path) {
        $this.RemoveFileFromMountPoint($path)
    }

    # Extract file
    [void] ExtractFile([string]$source, [string]$destination) {
        $this.ExtractFileFromMountPoint($source, $destination)
    }

    # Get VHD information
    [hashtable] GetInfo() {
        $fileInfo = Get-Item $this.ImagePath
        
        $info = @{
            Path = $this.ImagePath
            Format = $this.Metadata['Format']
            Size = $fileInfo.Length
            SizeFormatted = $this.FormatFileSize($fileInfo.Length)
            VirtualSize = $this.VirtualSize
            VirtualSizeFormatted = $this.FormatFileSize($this.VirtualSize)
            VhdType = $this.VhdType
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            DriveLetter = $this.DriveLetter
            DiskNumber = $this.DiskNumber
            PartitionNumber = $this.PartitionNumber
            LastModified = $fileInfo.LastWriteTime
        }

        # Get additional VHD info if available
        try {
            $vhdInfo = Get-VHD -Path $this.ImagePath -ErrorAction SilentlyContinue
            if ($vhdInfo) {
                $info['VhdFormat'] = $vhdInfo.VhdFormat.ToString()
                $info['VhdType'] = $vhdInfo.VhdType.ToString()
                $info['PhysicalSectorSize'] = $vhdInfo.PhysicalSectorSize
                $info['LogicalSectorSize'] = $vhdInfo.LogicalSectorSize
                $info['BlockSize'] = $vhdInfo.BlockSize
            }
        }
        catch {
            # Get-VHD requires Hyper-V module
        }

        return $info
    }

    # Get partitions in VHD
    [hashtable[]] GetPartitions() {
        $this.ValidateMounted()
        
        $partitions = Get-Partition -DiskNumber $this.DiskNumber -ErrorAction SilentlyContinue |
            ForEach-Object {
                @{
                    PartitionNumber = $_.PartitionNumber
                    DriveLetter = $_.DriveLetter
                    Size = $_.Size
                    Type = $_.Type
                    IsActive = $_.IsActive
                    IsBoot = $_.IsBoot
                }
            }
        
        return $partitions
    }

    # Create new VHD (static method)
    static [void] CreateVhd([string]$path, [long]$sizeBytes, [bool]$dynamic, [bool]$vhdx) {
        Write-DFLog -Message "Creating VHD: $path ($($sizeBytes / 1GB) GB)" -Level Info

        $params = @{
            Path = $path
            SizeBytes = $sizeBytes
        }

        if ($dynamic) {
            $params['Dynamic'] = $true
        }
        else {
            $params['Fixed'] = $true
        }

        try {
            New-VHD @params -ErrorAction Stop
            Write-DFLog -Message "VHD created successfully" -Level Info
        }
        catch {
            # New-VHD requires Hyper-V module, try diskpart
            $diskpartScript = @"
create vdisk file="$path" maximum=$([math]::Ceiling($sizeBytes / 1MB)) type=$(if ($dynamic) { 'expandable' } else { 'fixed' })
"@
            $diskpartScript | diskpart

            if ($LASTEXITCODE -ne 0) {
                throw [DFOperationException]::new("CreateVHD", $path, "Failed to create VHD")
            }
            Write-DFLog -Message "VHD created using diskpart" -Level Info
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

Write-Verbose "Loaded DFVhdHandler class"
