#Requires -Version 5.1

<#
.SYNOPSIS
    Base handler class for all image format handlers.

.DESCRIPTION
    Abstract base class that defines the interface for all image format handlers.
    Provides common functionality and enforces consistent API across formats.
#>

# Enumeration for mount status
enum DFMountStatus {
    NotMounted
    Mounting
    Mounted
    Dismounting
    Error
}

# Image information class
class DFImageInfo {
    [string]$Path
    [string]$Format
    [long]$Size
    [string]$SizeFormatted
    [DFMountStatus]$MountStatus
    [string]$MountPoint
    [int]$Index
    [hashtable]$Metadata

    DFImageInfo([string]$path) {
        $this.Path = $path
        $this.MountStatus = [DFMountStatus]::NotMounted
        $this.Metadata = @{}
        
        if (Test-Path $path) {
            $file = Get-Item $path
            $this.Size = $file.Length
            $this.SizeFormatted = $this.FormatSize($file.Length)
        }
    }

    hidden [string] FormatSize([long]$bytes) {
        if ($bytes -ge 1GB) { return "{0:N2} GB" -f ($bytes / 1GB) }
        if ($bytes -ge 1MB) { return "{0:N2} MB" -f ($bytes / 1MB) }
        if ($bytes -ge 1KB) { return "{0:N2} KB" -f ($bytes / 1KB) }
        return "$bytes bytes"
    }

    [hashtable] ToHashtable() {
        return @{
            Path = $this.Path
            Format = $this.Format
            Size = $this.Size
            SizeFormatted = $this.SizeFormatted
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            Index = $this.Index
            Metadata = $this.Metadata
        }
    }
}

# File entry class for listing
class DFFileEntry {
    [string]$Name
    [string]$Path
    [bool]$IsDirectory
    [long]$Size
    [datetime]$LastModified

    DFFileEntry([string]$name, [string]$path, [bool]$isDir, [long]$size, [datetime]$modified) {
        $this.Name = $name
        $this.Path = $path
        $this.IsDirectory = $isDir
        $this.Size = $size
        $this.LastModified = $modified
    }

    [hashtable] ToHashtable() {
        return @{
            Name = $this.Name
            Path = $this.Path
            IsDirectory = $this.IsDirectory
            Size = $this.Size
            LastModified = $this.LastModified
        }
    }
}

# Abstract base handler class
class DFBaseHandler {
    # Properties
    [string]$ImagePath
    [DFMountStatus]$MountStatus
    [string]$MountPoint
    [int]$Index
    [datetime]$MountTime
    [hashtable]$Metadata
    
    # Protected properties
    hidden [string]$TempDirectory

    # Constructor
    DFBaseHandler([string]$imagePath) {
        if (-not (Test-Path $imagePath -PathType Leaf)) {
            throw [DFImageNotFoundException]::new($imagePath)
        }

        $this.ImagePath = (Resolve-Path $imagePath).Path
        $this.MountStatus = [DFMountStatus]::NotMounted
        $this.Index = 1
        $this.Metadata = @{}
        
        Write-DFLog -Message "Created handler for: $($this.ImagePath)" -Level Verbose
    }

    # Abstract methods (must be overridden)
    [string] Mount([string]$mountPoint, [int]$index) {
        throw [System.NotImplementedException]::new("Mount must be implemented by derived class")
    }

    [void] Dismount([bool]$saveChanges) {
        throw [System.NotImplementedException]::new("Dismount must be implemented by derived class")
    }

    [DFFileEntry[]] ListFiles([string]$path) {
        throw [System.NotImplementedException]::new("ListFiles must be implemented by derived class")
    }

    [void] AddFile([string]$source, [string]$destination) {
        throw [System.NotImplementedException]::new("AddFile must be implemented by derived class")
    }

    [void] RemoveFile([string]$path) {
        throw [System.NotImplementedException]::new("RemoveFile must be implemented by derived class")
    }

    [void] ExtractFile([string]$source, [string]$destination) {
        throw [System.NotImplementedException]::new("ExtractFile must be implemented by derived class")
    }

    [hashtable] GetInfo() {
        throw [System.NotImplementedException]::new("GetInfo must be implemented by derived class")
    }

    # Common helper methods
    hidden [string] CreateTempMountPoint() {
        $tempPath = Join-Path $env:TEMP "DeployForge_$(Get-Random -Minimum 10000 -Maximum 99999)"
        New-Item -ItemType Directory -Path $tempPath -Force | Out-Null
        $this.TempDirectory = $tempPath
        return $tempPath
    }

    hidden [void] CleanupTempDirectory() {
        if ($this.TempDirectory -and (Test-Path $this.TempDirectory)) {
            Remove-Item $this.TempDirectory -Recurse -Force -ErrorAction SilentlyContinue
            $this.TempDirectory = $null
        }
    }

    hidden [void] ValidateMounted() {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            throw [DFOperationException]::new("Operation requires image to be mounted first")
        }
    }

    hidden [void] ValidateNotMounted() {
        if ($this.MountStatus -eq [DFMountStatus]::Mounted) {
            throw [DFOperationException]::new("Image is already mounted")
        }
    }

    # Common implementation for file listing from mount point
    hidden [DFFileEntry[]] ListFilesFromMountPoint([string]$relativePath) {
        $this.ValidateMounted()
        
        $targetPath = Join-Path $this.MountPoint ($relativePath.TrimStart('/\'))
        
        if (-not (Test-Path $targetPath)) {
            return @()
        }

        $entries = @()
        Get-ChildItem -Path $targetPath -ErrorAction SilentlyContinue | ForEach-Object {
            $entry = [DFFileEntry]::new(
                $_.Name,
                $_.FullName.Replace($this.MountPoint, '').Replace('\', '/'),
                $_.PSIsContainer,
                $(if ($_.PSIsContainer) { 0 } else { $_.Length }),
                $_.LastWriteTime
            )
            $entries += $entry
        }

        return $entries
    }

    # Common implementation for adding files
    hidden [void] AddFileToMountPoint([string]$source, [string]$destination) {
        $this.ValidateMounted()

        if (-not (Test-Path $source -PathType Leaf)) {
            throw [DFOperationException]::new("Add", $source, "Source file not found")
        }

        $destPath = Join-Path $this.MountPoint ($destination.TrimStart('/\'))
        $destDir = Split-Path $destPath -Parent

        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        Copy-Item -Path $source -Destination $destPath -Force
        Write-DFLog -Message "Added file: $source -> $destination" -Level Info
    }

    # Common implementation for removing files
    hidden [void] RemoveFileFromMountPoint([string]$path) {
        $this.ValidateMounted()

        $targetPath = Join-Path $this.MountPoint ($path.TrimStart('/\'))

        if (-not (Test-Path $targetPath)) {
            throw [DFOperationException]::new("Remove", $path, "Path not found")
        }

        Remove-Item -Path $targetPath -Recurse -Force
        Write-DFLog -Message "Removed: $path" -Level Info
    }

    # Common implementation for extracting files
    hidden [void] ExtractFileFromMountPoint([string]$source, [string]$destination) {
        $this.ValidateMounted()

        $sourcePath = Join-Path $this.MountPoint ($source.TrimStart('/\'))

        if (-not (Test-Path $sourcePath)) {
            throw [DFOperationException]::new("Extract", $source, "Source not found in image")
        }

        $destDir = Split-Path $destination -Parent
        if ($destDir -and -not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        if (Test-Path $sourcePath -PathType Container) {
            Copy-Item -Path $sourcePath -Destination $destination -Recurse -Force
        }
        else {
            Copy-Item -Path $sourcePath -Destination $destination -Force
        }

        Write-DFLog -Message "Extracted: $source -> $destination" -Level Info
    }

    # Run DISM command with error handling
    hidden [hashtable] RunDism([string[]]$arguments) {
        $process = Start-Process -FilePath "dism.exe" -ArgumentList $arguments -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\dism_out.txt" -RedirectStandardError "$env:TEMP\dism_err.txt"
        
        $stdout = Get-Content "$env:TEMP\dism_out.txt" -Raw -ErrorAction SilentlyContinue
        $stderr = Get-Content "$env:TEMP\dism_err.txt" -Raw -ErrorAction SilentlyContinue
        
        Remove-Item "$env:TEMP\dism_out.txt", "$env:TEMP\dism_err.txt" -Force -ErrorAction SilentlyContinue

        $result = @{
            ExitCode = $process.ExitCode
            Success = ($process.ExitCode -eq 0)
            StandardOutput = $stdout
            StandardError = $stderr
            Command = "dism.exe $($arguments -join ' ')"
        }

        if (-not $result.Success) {
            Write-DFLog -Message "DISM failed (Exit: $($result.ExitCode)): $stderr" -Level Error
        }

        return $result
    }

    # Alternative DISM execution using Invoke-Expression for simpler cases
    hidden [hashtable] InvokeDism([string]$arguments) {
        try {
            $output = & dism.exe $arguments.Split(' ') 2>&1
            $exitCode = $LASTEXITCODE
            
            return @{
                ExitCode = $exitCode
                Success = ($exitCode -eq 0)
                Output = $output -join "`n"
                Command = "dism.exe $arguments"
            }
        }
        catch {
            return @{
                ExitCode = -1
                Success = $false
                Output = $_.Exception.Message
                Command = "dism.exe $arguments"
            }
        }
    }

    # String representation
    [string] ToString() {
        return "[$($this.GetType().Name)] $($this.ImagePath) (Status: $($this.MountStatus))"
    }
}

Write-Verbose "Loaded DeployForge base handler classes"
