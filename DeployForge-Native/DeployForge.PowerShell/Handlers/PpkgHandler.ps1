#Requires -Version 5.1

<#
.SYNOPSIS
    PPKG (Provisioning Package) handler.

.DESCRIPTION
    Handles Windows provisioning packages (.ppkg) files.
    PPKG files are used by Windows Configuration Designer (ICD) for automated setup.
#>

class DFPpkgHandler : DFBaseHandler {
    # Properties specific to PPKG
    [string]$PackageName
    [string]$PackageVersion
    [string]$Owner
    [string]$Rank
    [hashtable]$Settings
    hidden [string]$ExtractPath

    # Constructor
    DFPpkgHandler([string]$imagePath) : base($imagePath) {
        $this.Metadata['Format'] = 'PPKG'
        $this.Settings = @{}
        $this.PopulatePackageInfo()
    }

    # Get PPKG information
    hidden [void] PopulatePackageInfo() {
        try {
            # Extract package name from filename
            $this.PackageName = [System.IO.Path]::GetFileNameWithoutExtension($this.ImagePath)
            
            # PPKG files are ZIP archives with XML manifest
            # Try to read metadata
            Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
            
            $zip = [System.IO.Compression.ZipFile]::OpenRead($this.ImagePath)
            
            foreach ($entry in $zip.Entries) {
                if ($entry.Name -eq 'customizations.xml' -or $entry.Name -eq 'package.xml') {
                    $stream = $entry.Open()
                    $reader = New-Object System.IO.StreamReader($stream)
                    $content = $reader.ReadToEnd()
                    $reader.Close()
                    $stream.Close()
                    
                    # Parse XML for metadata
                    [xml]$xml = $content
                    
                    if ($xml.Package) {
                        $this.PackageName = $xml.Package.Name
                        $this.PackageVersion = $xml.Package.Version
                        $this.Owner = $xml.Package.Owner
                        $this.Rank = $xml.Package.Rank
                    }
                    
                    break
                }
            }
            
            $zip.Dispose()
            
            Write-DFLog -Message "PPKG: $($this.PackageName) v$($this.PackageVersion)" -Level Verbose
        }
        catch {
            Write-DFLog -Message "Failed to get PPKG info: $_" -Level Warning
        }
    }

    # Extract PPKG for viewing/modification
    [string] Mount([string]$mountPoint, [int]$index) {
        $this.ValidateNotMounted()
        
        $this.MountStatus = [DFMountStatus]::Mounting
        Write-DFLog -Message "Extracting PPKG: $($this.ImagePath)" -Level Info

        try {
            # Create extraction directory
            if (-not $mountPoint) {
                $mountPoint = $this.CreateTempMountPoint()
            }
            elseif (-not (Test-Path $mountPoint)) {
                New-Item -ItemType Directory -Path $mountPoint -Force | Out-Null
            }

            # Extract PPKG (it's a ZIP file)
            Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
            [System.IO.Compression.ZipFile]::ExtractToDirectory($this.ImagePath, $mountPoint)

            $this.ExtractPath = $mountPoint
            $this.MountPoint = $mountPoint
            $this.MountStatus = [DFMountStatus]::Mounted
            $this.MountTime = Get-Date
            
            Write-DFLog -Message "PPKG extracted to $mountPoint" -Level Info
            return $mountPoint
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            $this.CleanupTempDirectory()
            throw [DFMountException]::new($this.ImagePath, $mountPoint, $_.Exception.Message)
        }
    }

    # Repackage the PPKG
    [void] Dismount([bool]$saveChanges) {
        if ($this.MountStatus -ne [DFMountStatus]::Mounted) {
            Write-DFLog -Message "PPKG is not extracted" -Level Warning
            return
        }

        $this.MountStatus = [DFMountStatus]::Dismounting

        try {
            if ($saveChanges) {
                # Create backup of original
                $backupPath = "$($this.ImagePath).bak"
                Copy-Item $this.ImagePath $backupPath -Force
                
                # Recompress the PPKG
                Write-DFLog -Message "Repackaging PPKG with modifications" -Level Info
                
                Remove-Item $this.ImagePath -Force
                
                Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
                [System.IO.Compression.ZipFile]::CreateFromDirectory(
                    $this.MountPoint,
                    $this.ImagePath,
                    [System.IO.Compression.CompressionLevel]::Optimal,
                    $false
                )
                
                Write-DFLog -Message "PPKG repackaged successfully" -Level Info
            }

            $this.CleanupTempDirectory()
            $this.MountPoint = $null
            $this.ExtractPath = $null
            $this.MountStatus = [DFMountStatus]::NotMounted
            
            Write-DFLog -Message "PPKG processing complete" -Level Info
        }
        catch {
            $this.MountStatus = [DFMountStatus]::Error
            throw
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

    # Get PPKG information
    [hashtable] GetInfo() {
        $fileInfo = Get-Item $this.ImagePath
        
        return @{
            Path = $this.ImagePath
            Format = 'PPKG'
            Size = $fileInfo.Length
            SizeFormatted = $this.FormatFileSize($fileInfo.Length)
            MountStatus = $this.MountStatus.ToString()
            MountPoint = $this.MountPoint
            PackageName = $this.PackageName
            PackageVersion = $this.PackageVersion
            Owner = $this.Owner
            Rank = $this.Rank
            Settings = $this.Settings
            LastModified = $fileInfo.LastWriteTime
        }
    }

    # Get customization settings from PPKG
    [hashtable] GetCustomizations() {
        $this.ValidateMounted()
        
        $customizationsPath = Join-Path $this.MountPoint "customizations.xml"
        
        if (-not (Test-Path $customizationsPath)) {
            return @{}
        }

        try {
            [xml]$xml = Get-Content $customizationsPath
            $customizations = @{}
            
            # Parse and return customization settings
            # This would need to be expanded based on PPKG schema
            
            return $customizations
        }
        catch {
            Write-DFLog -Message "Failed to parse customizations: $_" -Level Warning
            return @{}
        }
    }

    # Apply PPKG to image (static method)
    static [void] ApplyToImage([string]$ppkgPath, [string]$imageMountPoint) {
        Write-DFLog -Message "Applying PPKG to image: $imageMountPoint" -Level Info

        $dismArgs = @(
            "/Image:`"$imageMountPoint`"",
            "/Add-ProvisioningPackage",
            "/PackagePath:`"$ppkgPath`""
        )

        $result = & dism.exe $dismArgs 2>&1
        $exitCode = $LASTEXITCODE

        if ($exitCode -ne 0) {
            throw [DFOperationException]::new("ApplyPPKG", $ppkgPath, "DISM failed: $exitCode")
        }

        Write-DFLog -Message "PPKG applied successfully" -Level Info
    }

    # Helper to format file size
    hidden [string] FormatFileSize([long]$bytes) {
        if ($bytes -ge 1GB) { return "{0:N2} GB" -f ($bytes / 1GB) }
        if ($bytes -ge 1MB) { return "{0:N2} MB" -f ($bytes / 1MB) }
        if ($bytes -ge 1KB) { return "{0:N2} KB" -f ($bytes / 1KB) }
        return "$bytes bytes"
    }
}

Write-Verbose "Loaded DFPpkgHandler class"
