#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Image Manager - Core image mounting and manipulation functions
    
.DESCRIPTION
    Provides functions for mounting, unmounting, and managing Windows deployment images
    using native DISM (Deployment Image Servicing and Management).
    
.NOTES
    Supports: WIM, ESD, VHD, VHDX image formats
#>

# Module variables
$script:MountPath = "$env:TEMP\DeployForge\Mount"

function Mount-DeployForgeImage {
    <#
    .SYNOPSIS
        Mounts a Windows deployment image.
        
    .DESCRIPTION
        Mounts a WIM, ESD, VHD, or VHDX image to a specified mount point using DISM.
        
    .PARAMETER ImagePath
        Path to the image file to mount.
        
    .PARAMETER Index
        Image index to mount (for WIM/ESD files). Default is 1.
        
    .PARAMETER MountPath
        Path where the image will be mounted. If not specified, uses the default mount path.
        
    .PARAMETER ReadOnly
        Mount the image in read-only mode.
        
    .EXAMPLE
        Mount-DeployForgeImage -ImagePath "C:\Images\install.wim" -Index 1
        
    .EXAMPLE
        Mount-DeployForgeImage -ImagePath "C:\Images\install.wim" -MountPath "D:\Mount" -ReadOnly
        
    .OUTPUTS
        PSCustomObject with mount information
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,
        
        [Parameter(Mandatory = $false)]
        [ValidateRange(1, 100)]
        [int]$Index = 1,
        
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(Mandatory = $false)]
        [switch]$ReadOnly
    )
    
    begin {
        Write-Verbose "Mount-DeployForgeImage: Starting mount operation"
        
        # Resolve full path
        $ImagePath = Resolve-Path $ImagePath
        $extension = [System.IO.Path]::GetExtension($ImagePath).ToLower()
        
        # Validate image type
        $validExtensions = @('.wim', '.esd', '.vhd', '.vhdx')
        if ($extension -notin $validExtensions) {
            throw "Unsupported image format: $extension. Supported formats: $($validExtensions -join ', ')"
        }
    }
    
    process {
        # Create mount directory
        if (-not (Test-Path $MountPath)) {
            New-Item -ItemType Directory -Path $MountPath -Force | Out-Null
            Write-Verbose "Created mount directory: $MountPath"
        }
        
        # Check if already mounted
        $existingMount = Get-WindowsImage -Mounted -ErrorAction SilentlyContinue | 
            Where-Object { $_.Path -eq $MountPath }
        
        if ($existingMount) {
            Write-Warning "An image is already mounted at $MountPath"
            return [PSCustomObject]@{
                Success = $false
                ImagePath = $ImagePath
                MountPath = $MountPath
                Index = $Index
                Message = "Mount point already in use"
                ExistingImage = $existingMount.ImagePath
            }
        }
        
        try {
            Write-Host "Mounting image: $([System.IO.Path]::GetFileName($ImagePath))" -ForegroundColor Cyan
            Write-Host "  Mount point: $MountPath" -ForegroundColor Gray
            Write-Host "  Index: $Index" -ForegroundColor Gray
            
            $startTime = Get-Date
            
            # Build mount command based on image type
            if ($extension -in @('.wim', '.esd')) {
                $mountParams = @{
                    ImagePath = $ImagePath
                    Index = $Index
                    Path = $MountPath
                    ErrorAction = 'Stop'
                }
                
                if ($ReadOnly) {
                    $mountParams['ReadOnly'] = $true
                }
                
                Mount-WindowsImage @mountParams | Out-Null
            }
            elseif ($extension -in @('.vhd', '.vhdx')) {
                # Mount VHD/VHDX
                $vhdParams = @{
                    Path = $ImagePath
                    ErrorAction = 'Stop'
                }
                
                if ($ReadOnly) {
                    $vhdParams['ReadOnly'] = $true
                }
                
                Mount-VHD @vhdParams | Out-Null
                
                # Get drive letter assigned to VHD
                $disk = Get-VHD -Path $ImagePath
                $driveLetter = (Get-Partition -DiskNumber $disk.DiskNumber | 
                    Where-Object { $_.Type -eq 'Basic' } | 
                    Select-Object -First 1).DriveLetter
                
                # Create junction to mount path
                if ($driveLetter) {
                    if (Test-Path $MountPath) {
                        Remove-Item $MountPath -Force
                    }
                    New-Item -ItemType Junction -Path $MountPath -Target "${driveLetter}:\" | Out-Null
                }
            }
            
            $duration = (Get-Date) - $startTime
            
            Write-Host "✓ Image mounted successfully" -ForegroundColor Green
            Write-Host "  Duration: $($duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Gray
            
            return [PSCustomObject]@{
                Success = $true
                ImagePath = $ImagePath
                MountPath = $MountPath
                Index = $Index
                ReadOnly = $ReadOnly.IsPresent
                Duration = $duration
                Message = "Image mounted successfully"
            }
        }
        catch {
            Write-Error "Failed to mount image: $_"
            
            return [PSCustomObject]@{
                Success = $false
                ImagePath = $ImagePath
                MountPath = $MountPath
                Index = $Index
                Message = $_.Exception.Message
                Error = $_
            }
        }
    }
}

function Dismount-DeployForgeImage {
    <#
    .SYNOPSIS
        Dismounts a Windows deployment image.
        
    .DESCRIPTION
        Unmounts a previously mounted image, optionally saving or discarding changes.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER Save
        Save changes made to the image.
        
    .PARAMETER Discard
        Discard changes and unmount without saving.
        
    .EXAMPLE
        Dismount-DeployForgeImage -MountPath "D:\Mount" -Save
        
    .EXAMPLE
        Dismount-DeployForgeImage -Discard
    #>
    [CmdletBinding(DefaultParameterSetName = 'Save')]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $false, Position = 0)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(ParameterSetName = 'Save')]
        [switch]$Save,
        
        [Parameter(ParameterSetName = 'Discard')]
        [switch]$Discard
    )
    
    begin {
        Write-Verbose "Dismount-DeployForgeImage: Starting dismount operation"
    }
    
    process {
        # Check if image is mounted
        $mountedImage = Get-WindowsImage -Mounted -ErrorAction SilentlyContinue | 
            Where-Object { $_.Path -eq $MountPath }
        
        if (-not $mountedImage) {
            # Check for VHD junction
            $isVhdMount = (Get-Item $MountPath -ErrorAction SilentlyContinue).Attributes -band [System.IO.FileAttributes]::ReparsePoint
            
            if (-not $isVhdMount) {
                Write-Warning "No image mounted at $MountPath"
                return [PSCustomObject]@{
                    Success = $false
                    MountPath = $MountPath
                    Message = "No image mounted at specified path"
                }
            }
        }
        
        try {
            Write-Host "Dismounting image from: $MountPath" -ForegroundColor Cyan
            
            $startTime = Get-Date
            
            if ($mountedImage) {
                # WIM/ESD dismount
                if ($Discard) {
                    Write-Host "  Discarding changes..." -ForegroundColor Yellow
                    Dismount-WindowsImage -Path $MountPath -Discard -ErrorAction Stop | Out-Null
                }
                else {
                    Write-Host "  Saving changes..." -ForegroundColor Yellow
                    Dismount-WindowsImage -Path $MountPath -Save -ErrorAction Stop | Out-Null
                }
            }
            else {
                # VHD dismount
                $junction = Get-Item $MountPath
                $target = $junction.Target
                Remove-Item $MountPath -Force
                
                # Find and dismount the VHD
                $vhds = Get-VHD -Path (Get-Volume).Path -ErrorAction SilentlyContinue
                foreach ($vhd in $vhds) {
                    if ($vhd.Path) {
                        Dismount-VHD -Path $vhd.Path -ErrorAction SilentlyContinue
                    }
                }
            }
            
            $duration = (Get-Date) - $startTime
            
            $action = if ($Discard) { "discarded" } else { "saved" }
            Write-Host "✓ Image dismounted and changes $action" -ForegroundColor Green
            Write-Host "  Duration: $($duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Gray
            
            return [PSCustomObject]@{
                Success = $true
                MountPath = $MountPath
                ChangesSaved = -not $Discard.IsPresent
                Duration = $duration
                Message = "Image dismounted successfully"
            }
        }
        catch {
            Write-Error "Failed to dismount image: $_"
            
            # Attempt cleanup
            Write-Warning "Attempting cleanup dismount..."
            try {
                Dismount-WindowsImage -Path $MountPath -Discard -ErrorAction Stop | Out-Null
                Write-Host "✓ Cleanup dismount successful (changes discarded)" -ForegroundColor Yellow
            }
            catch {
                Write-Error "Cleanup failed. You may need to run: DISM /Cleanup-Mountpoints"
            }
            
            return [PSCustomObject]@{
                Success = $false
                MountPath = $MountPath
                Message = "Dismount failed: $($_.Exception.Message)"
                Error = $_
            }
        }
    }
}

function Get-DeployForgeImageInfo {
    <#
    .SYNOPSIS
        Gets detailed information about a Windows deployment image.
        
    .DESCRIPTION
        Retrieves comprehensive information about a WIM/ESD image including
        all available indexes, editions, sizes, and metadata.
        
    .PARAMETER ImagePath
        Path to the image file.
        
    .PARAMETER Index
        Specific index to get detailed information for.
        
    .EXAMPLE
        Get-DeployForgeImageInfo -ImagePath "C:\Images\install.wim"
        
    .EXAMPLE
        Get-DeployForgeImageInfo -ImagePath "C:\Images\install.wim" -Index 1
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({ Test-Path $_ })]
        [string]$ImagePath,
        
        [Parameter(Mandatory = $false)]
        [int]$Index
    )
    
    begin {
        $ImagePath = Resolve-Path $ImagePath
        Write-Verbose "Getting image info for: $ImagePath"
    }
    
    process {
        try {
            $fileInfo = Get-Item $ImagePath
            
            if ($Index) {
                # Get specific index info
                $imageInfo = Get-WindowsImage -ImagePath $ImagePath -Index $Index -ErrorAction Stop
                
                return [PSCustomObject]@{
                    ImagePath = $ImagePath
                    FileName = $fileInfo.Name
                    FileSizeGB = [math]::Round($fileInfo.Length / 1GB, 2)
                    Format = $fileInfo.Extension.TrimStart('.').ToUpper()
                    Index = $imageInfo.ImageIndex
                    Name = $imageInfo.ImageName
                    Description = $imageInfo.ImageDescription
                    ImageSizeGB = [math]::Round($imageInfo.ImageSize / 1GB, 2)
                    Architecture = $imageInfo.Architecture
                    Version = "$($imageInfo.MajorVersion).$($imageInfo.MinorVersion).$($imageInfo.Build).$($imageInfo.SPBuild)"
                    EditionId = $imageInfo.EditionId
                    InstallationType = $imageInfo.InstallationType
                    Languages = $imageInfo.Languages
                    DefaultLanguage = $imageInfo.DefaultLanguage
                    ProductType = $imageInfo.ProductType
                    ProductSuite = $imageInfo.ProductSuite
                    SystemRoot = $imageInfo.SystemRoot
                    WIMBoot = $imageInfo.WIMBoot
                    LastModified = $fileInfo.LastWriteTime
                }
            }
            else {
                # Get all indexes
                $images = Get-WindowsImage -ImagePath $ImagePath -ErrorAction Stop
                
                $results = foreach ($img in $images) {
                    $detailedInfo = Get-WindowsImage -ImagePath $ImagePath -Index $img.ImageIndex
                    
                    [PSCustomObject]@{
                        Index = $img.ImageIndex
                        Name = $img.ImageName
                        Description = $img.ImageDescription
                        ImageSizeGB = [math]::Round($img.ImageSize / 1GB, 2)
                        Architecture = $detailedInfo.Architecture
                        Version = "$($detailedInfo.MajorVersion).$($detailedInfo.MinorVersion).$($detailedInfo.Build)"
                        EditionId = $detailedInfo.EditionId
                        Languages = ($detailedInfo.Languages -join ', ')
                    }
                }
                
                return [PSCustomObject]@{
                    ImagePath = $ImagePath
                    FileName = $fileInfo.Name
                    FileSizeGB = [math]::Round($fileInfo.Length / 1GB, 2)
                    Format = $fileInfo.Extension.TrimStart('.').ToUpper()
                    ImageCount = $images.Count
                    LastModified = $fileInfo.LastWriteTime
                    Images = $results
                }
            }
        }
        catch {
            Write-Error "Failed to get image info: $_"
            throw
        }
    }
}

function Get-DeployForgeImageFiles {
    <#
    .SYNOPSIS
        Lists files within a mounted Windows image.
        
    .DESCRIPTION
        Retrieves a list of files and directories at a specified path within
        the mounted image.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER Path
        Relative path within the image to list. Default is root.
        
    .PARAMETER Recurse
        Include subdirectories recursively.
        
    .PARAMETER Filter
        Filter pattern for file names.
        
    .EXAMPLE
        Get-DeployForgeImageFiles -MountPath "D:\Mount" -Path "Windows\System32"
    #>
    [CmdletBinding()]
    [OutputType([System.IO.FileSystemInfo[]])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(Mandatory = $false)]
        [string]$Path = "",
        
        [Parameter(Mandatory = $false)]
        [switch]$Recurse,
        
        [Parameter(Mandatory = $false)]
        [string]$Filter = "*"
    )
    
    begin {
        if (-not (Test-Path $MountPath)) {
            throw "Mount path does not exist: $MountPath"
        }
    }
    
    process {
        $targetPath = Join-Path $MountPath $Path.TrimStart('\', '/')
        
        if (-not (Test-Path $targetPath)) {
            Write-Warning "Path not found in image: $Path"
            return @()
        }
        
        $params = @{
            Path = $targetPath
            Filter = $Filter
            ErrorAction = 'SilentlyContinue'
        }
        
        if ($Recurse) {
            $params['Recurse'] = $true
        }
        
        return Get-ChildItem @params
    }
}

function Add-DeployForgeFile {
    <#
    .SYNOPSIS
        Adds a file to a mounted Windows image.
        
    .DESCRIPTION
        Copies a file from the host system into the mounted image.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER Source
        Path to the source file or directory.
        
    .PARAMETER Destination
        Destination path within the image.
        
    .EXAMPLE
        Add-DeployForgeFile -Source "C:\Config\setup.exe" -Destination "Windows\Setup\Scripts"
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$Source,
        
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )
    
    begin {
        if (-not (Test-Path $MountPath)) {
            throw "Mount path does not exist: $MountPath"
        }
    }
    
    process {
        try {
            $targetPath = Join-Path $MountPath $Destination.TrimStart('\', '/')
            $parentPath = Split-Path $targetPath -Parent
            
            # Create destination directory if it doesn't exist
            if (-not (Test-Path $parentPath)) {
                New-Item -ItemType Directory -Path $parentPath -Force | Out-Null
            }
            
            $sourceItem = Get-Item $Source
            
            if ($sourceItem.PSIsContainer) {
                # Copy directory
                Copy-Item -Path $Source -Destination $targetPath -Recurse -Force
                Write-Host "✓ Directory copied: $($sourceItem.Name)" -ForegroundColor Green
            }
            else {
                # Copy file
                Copy-Item -Path $Source -Destination $targetPath -Force
                Write-Host "✓ File copied: $($sourceItem.Name)" -ForegroundColor Green
            }
            
            return [PSCustomObject]@{
                Success = $true
                Source = $Source
                Destination = $targetPath
                IsDirectory = $sourceItem.PSIsContainer
                Size = if ($sourceItem.PSIsContainer) { 0 } else { $sourceItem.Length }
            }
        }
        catch {
            Write-Error "Failed to add file: $_"
            return [PSCustomObject]@{
                Success = $false
                Source = $Source
                Destination = $Destination
                Error = $_.Exception.Message
            }
        }
    }
}

function Remove-DeployForgeFile {
    <#
    .SYNOPSIS
        Removes a file or directory from a mounted Windows image.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER Path
        Path to the file or directory to remove (relative to mount point).
        
    .PARAMETER Recurse
        Remove directories recursively.
        
    .EXAMPLE
        Remove-DeployForgeFile -Path "Windows\Temp\cache" -Recurse
    #>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(Mandatory = $true)]
        [string]$Path,
        
        [Parameter(Mandatory = $false)]
        [switch]$Recurse
    )
    
    process {
        $targetPath = Join-Path $MountPath $Path.TrimStart('\', '/')
        
        if (-not (Test-Path $targetPath)) {
            Write-Warning "Path not found: $Path"
            return [PSCustomObject]@{
                Success = $false
                Path = $Path
                Message = "Path not found"
            }
        }
        
        if ($PSCmdlet.ShouldProcess($targetPath, "Remove")) {
            try {
                Remove-Item -Path $targetPath -Recurse:$Recurse -Force
                Write-Host "✓ Removed: $Path" -ForegroundColor Green
                
                return [PSCustomObject]@{
                    Success = $true
                    Path = $Path
                    Message = "Successfully removed"
                }
            }
            catch {
                Write-Error "Failed to remove: $_"
                return [PSCustomObject]@{
                    Success = $false
                    Path = $Path
                    Error = $_.Exception.Message
                }
            }
        }
    }
}

function Copy-DeployForgeFile {
    <#
    .SYNOPSIS
        Extracts a file from a mounted Windows image to the host.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER Source
        Source path within the image.
        
    .PARAMETER Destination
        Destination path on the host system.
        
    .EXAMPLE
        Copy-DeployForgeFile -Source "Windows\System32\config\SOFTWARE" -Destination "C:\Backup"
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $false)]
        [string]$MountPath = $script:MountPath,
        
        [Parameter(Mandatory = $true)]
        [string]$Source,
        
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )
    
    process {
        $sourcePath = Join-Path $MountPath $Source.TrimStart('\', '/')
        
        if (-not (Test-Path $sourcePath)) {
            Write-Error "Source not found in image: $Source"
            return [PSCustomObject]@{
                Success = $false
                Source = $Source
                Message = "Source not found"
            }
        }
        
        try {
            # Create destination directory if needed
            $destParent = Split-Path $Destination -Parent
            if (-not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            
            Copy-Item -Path $sourcePath -Destination $Destination -Recurse -Force
            Write-Host "✓ Extracted: $Source" -ForegroundColor Green
            
            return [PSCustomObject]@{
                Success = $true
                Source = $Source
                Destination = $Destination
            }
        }
        catch {
            Write-Error "Failed to extract: $_"
            return [PSCustomObject]@{
                Success = $false
                Source = $Source
                Error = $_.Exception.Message
            }
        }
    }
}

# Export functions
Export-ModuleMember -Function @(
    'Mount-DeployForgeImage',
    'Dismount-DeployForgeImage',
    'Get-DeployForgeImageInfo',
    'Get-DeployForgeImageFiles',
    'Add-DeployForgeFile',
    'Remove-DeployForgeFile',
    'Copy-DeployForgeFile'
)
