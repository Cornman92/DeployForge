#Requires -Version 5.1

<#
.SYNOPSIS
    Image Manager for coordinating image operations.

.DESCRIPTION
    Factory class for creating appropriate handlers and managing image operations.
    Provides high-level API for working with Windows deployment images.
#>

# Image Manager class - Factory and coordinator
class DFImageManager {
    # Static properties
    static [hashtable]$RegisteredHandlers = @{}
    static [string]$ModuleVersion = "2.0.0"
    
    # Instance properties
    [string]$ImagePath
    [DFBaseHandler]$Handler
    [datetime]$CreatedAt

    # Static constructor - register default handlers
    static DFImageManager() {
        [DFImageManager]::RegisterHandler('.wim', [DFWimHandler])
        [DFImageManager]::RegisterHandler('.esd', [DFEsdHandler])
        [DFImageManager]::RegisterHandler('.iso', [DFIsoHandler])
        [DFImageManager]::RegisterHandler('.vhd', [DFVhdHandler])
        [DFImageManager]::RegisterHandler('.vhdx', [DFVhdHandler])
        [DFImageManager]::RegisterHandler('.ppkg', [DFPpkgHandler])
    }

    # Register a handler for a file extension
    static [void] RegisterHandler([string]$extension, [type]$handlerType) {
        $ext = $extension.ToLower()
        if (-not $ext.StartsWith('.')) {
            $ext = ".$ext"
        }
        [DFImageManager]::RegisteredHandlers[$ext] = $handlerType
        Write-Verbose "Registered handler $($handlerType.Name) for $ext"
    }

    # Get supported formats
    static [string[]] GetSupportedFormats() {
        return [DFImageManager]::RegisteredHandlers.Keys | Sort-Object
    }

    # Create handler for image
    static [DFBaseHandler] CreateHandler([string]$imagePath) {
        if (-not (Test-Path $imagePath -PathType Leaf)) {
            throw [DFImageNotFoundException]::new($imagePath)
        }

        $extension = [System.IO.Path]::GetExtension($imagePath).ToLower()
        
        if (-not [DFImageManager]::RegisteredHandlers.ContainsKey($extension)) {
            $supported = [DFImageManager]::RegisteredHandlers.Keys -join ', '
            throw [DFUnsupportedFormatException]::new($extension, $supported)
        }

        $handlerType = [DFImageManager]::RegisteredHandlers[$extension]
        return $handlerType::new($imagePath)
    }

    # Instance constructor
    DFImageManager([string]$imagePath) {
        $this.ImagePath = (Resolve-Path $imagePath).Path
        $this.Handler = [DFImageManager]::CreateHandler($imagePath)
        $this.CreatedAt = Get-Date
    }

    # Delegate methods to handler
    [string] Mount([string]$mountPoint, [int]$index) {
        return $this.Handler.Mount($mountPoint, $index)
    }

    [string] Mount() {
        return $this.Handler.Mount($null, 1)
    }

    [void] Dismount([bool]$saveChanges) {
        $this.Handler.Dismount($saveChanges)
    }

    [DFFileEntry[]] ListFiles([string]$path) {
        return $this.Handler.ListFiles($path)
    }

    [void] AddFile([string]$source, [string]$destination) {
        $this.Handler.AddFile($source, $destination)
    }

    [void] RemoveFile([string]$path) {
        $this.Handler.RemoveFile($path)
    }

    [void] ExtractFile([string]$source, [string]$destination) {
        $this.Handler.ExtractFile($source, $destination)
    }

    [hashtable] GetInfo() {
        return $this.Handler.GetInfo()
    }

    # Get mount point
    [string] GetMountPoint() {
        return $this.Handler.MountPoint
    }

    # Check if mounted
    [bool] IsMounted() {
        return $this.Handler.MountStatus -eq [DFMountStatus]::Mounted
    }

    # String representation
    [string] ToString() {
        return "ImageManager($($this.ImagePath))"
    }
}

# Profile enumeration for common use cases
enum DFProfile {
    Gaming
    Developer
    Enterprise
    Student
    Creator
    Minimal
    Custom
}

# Profile configuration class
class DFProfileConfig {
    [DFProfile]$Profile
    [string]$Name
    [string]$Description
    [hashtable]$Features
    [hashtable]$Optimizations
    [string[]]$RemovePackages
    [string[]]$InstallPackages

    DFProfileConfig([DFProfile]$profile) {
        $this.Profile = $profile
        $this.Name = $profile.ToString()
        $this.Features = @{}
        $this.Optimizations = @{}
        $this.RemovePackages = @()
        $this.InstallPackages = @()

        switch ($profile) {
            'Gaming' {
                $this.Description = "Optimized for gaming performance with reduced latency and enhanced graphics"
                $this.Features = @{
                    GameMode = $true
                    FullscreenOptimizations = $false
                    GameBar = $false
                    GameDVR = $false
                    HardwareAcceleration = $true
                }
                $this.Optimizations = @{
                    NetworkLatency = $true
                    MousePolling = $true
                    PowerPlan = "High Performance"
                }
            }
            'Developer' {
                $this.Description = "Full development environment with tools and WSL2"
                $this.Features = @{
                    DeveloperMode = $true
                    WSL2 = $true
                    HyperV = $false
                    Containers = $true
                }
                $this.InstallPackages = @(
                    'Git.Git',
                    'Microsoft.VisualStudioCode',
                    'Microsoft.WindowsTerminal',
                    'Microsoft.PowerShell'
                )
            }
            'Enterprise' {
                $this.Description = "Corporate deployment with security hardening"
                $this.Features = @{
                    BitLocker = $true
                    WindowsDefender = $true
                    Telemetry = $false
                    CortanaEnabled = $false
                }
                $this.Optimizations = @{
                    GroupPolicy = $true
                    AuditLogging = $true
                }
            }
            'Student' {
                $this.Description = "Balanced setup for education and learning"
                $this.Features = @{
                    OfficeOnline = $true
                    OneDrive = $true
                    Calculator = $true
                    Paint = $true
                }
            }
            'Creator' {
                $this.Description = "Creative professional with media tools"
                $this.Features = @{
                    ColorManagement = $true
                    GraphicsTools = $true
                    MediaFeatures = $true
                }
            }
            'Minimal' {
                $this.Description = "Minimal installation with essential features only"
                $this.Features = @{
                    Cortana = $false
                    Xbox = $false
                    OneDrive = $false
                }
                $this.RemovePackages = @(
                    'Microsoft.BingWeather',
                    'Microsoft.GetHelp',
                    'Microsoft.Getstarted',
                    'Microsoft.MicrosoftOfficeHub',
                    'Microsoft.MicrosoftSolitaireCollection',
                    'Microsoft.People',
                    'Microsoft.WindowsFeedbackHub',
                    'Microsoft.YourPhone'
                )
            }
        }
    }

    [hashtable] ToHashtable() {
        return @{
            Profile = $this.Profile.ToString()
            Name = $this.Name
            Description = $this.Description
            Features = $this.Features
            Optimizations = $this.Optimizations
            RemovePackages = $this.RemovePackages
            InstallPackages = $this.InstallPackages
        }
    }
}

# Build configuration class
class DFBuildConfig {
    [string]$SourceImage
    [string]$OutputImage
    [DFProfileConfig]$Profile
    [int]$ImageIndex
    [hashtable]$CustomFeatures
    [string[]]$Drivers
    [string]$UnattendPath
    [bool]$SaveChanges

    DFBuildConfig() {
        $this.ImageIndex = 1
        $this.CustomFeatures = @{}
        $this.Drivers = @()
        $this.SaveChanges = $true
    }

    [void] SetProfile([DFProfile]$profile) {
        $this.Profile = [DFProfileConfig]::new($profile)
    }

    [hashtable] ToHashtable() {
        return @{
            SourceImage = $this.SourceImage
            OutputImage = $this.OutputImage
            Profile = $this.Profile.ToHashtable()
            ImageIndex = $this.ImageIndex
            CustomFeatures = $this.CustomFeatures
            Drivers = $this.Drivers
            UnattendPath = $this.UnattendPath
            SaveChanges = $this.SaveChanges
        }
    }
}

# Operation result class
class DFOperationResult {
    [bool]$Success
    [string]$Operation
    [string]$Message
    [datetime]$Timestamp
    [timespan]$Duration
    [hashtable]$Details

    DFOperationResult([bool]$success, [string]$operation, [string]$message) {
        $this.Success = $success
        $this.Operation = $operation
        $this.Message = $message
        $this.Timestamp = Get-Date
        $this.Details = @{}
    }

    static [DFOperationResult] Success([string]$operation, [string]$message) {
        return [DFOperationResult]::new($true, $operation, $message)
    }

    static [DFOperationResult] Failure([string]$operation, [string]$message) {
        return [DFOperationResult]::new($false, $operation, $message)
    }

    [hashtable] ToHashtable() {
        return @{
            Success = $this.Success
            Operation = $this.Operation
            Message = $this.Message
            Timestamp = $this.Timestamp
            Duration = $this.Duration.TotalSeconds
            Details = $this.Details
        }
    }

    [string] ToString() {
        $status = if ($this.Success) { "SUCCESS" } else { "FAILED" }
        return "[$status] $($this.Operation): $($this.Message)"
    }
}

Write-Verbose "Loaded DeployForge ImageManager classes"
