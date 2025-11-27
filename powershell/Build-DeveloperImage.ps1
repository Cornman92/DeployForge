<#
.SYNOPSIS
    Build a developer-optimized Windows image using native DISM and PowerShell

.DESCRIPTION
    This script creates a developer workstation image with development tools,
    IDE configurations, and productivity optimizations using native Windows tools.

.PARAMETER ImagePath
    Path to the Windows image file (WIM/ESD)

.PARAMETER OutputPath
    Path where the customized image will be saved

.PARAMETER Index
    Image index to use (default: 1)

.PARAMETER DevProfile
    Development profile: FullStack, Backend, Frontend, DataScience, or DevOps

.EXAMPLE
    .\Build-DeveloperImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\developer.wim" -DevProfile FullStack

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges, Windows 10/11 Pro/Enterprise
#>

#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({Test-Path $_})]
    [string]$ImagePath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [int]$Index = 1,

    [Parameter(Mandatory = $false)]
    [ValidateSet('FullStack', 'Backend', 'Frontend', 'DataScience', 'DevOps')]
    [string]$DevProfile = 'FullStack'
)

# Import utilities
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\DeployForge-Utilities.psm1" -Force

$mountPath = "$env:TEMP\DeployForge\Mount"

Write-Host "`n=== DeployForge Developer Image Builder ===" -ForegroundColor Cyan
Write-Host "Profile: $DevProfile" -ForegroundColor Yellow
Write-Host "Source: $ImagePath" -ForegroundColor Yellow
Write-Host "Output: $OutputPath`n" -ForegroundColor Yellow

try {
    # Step 1: Copy source image
    Write-Host "[1/7] Copying source image..." -ForegroundColor Cyan
    Copy-Item -Path $ImagePath -Destination $OutputPath -Force
    Write-Host "✓ Image copied`n" -ForegroundColor Green

    # Step 2: Mount image
    Write-Host "[2/7] Mounting image..." -ForegroundColor Cyan
    Mount-WindowsDeploymentImage -ImagePath $OutputPath -Index $Index -MountPath $mountPath
    Write-Host ""

    # Step 3: Enable Windows features for development
    Write-Host "[3/7] Enabling Windows development features..." -ForegroundColor Cyan

    # Core development features
    $devFeatures = @(
        'NetFx4-AdvSrvs',
        'NetFx4Extended-ASPNET45',
        'IIS-WebServerRole',
        'IIS-WebServer',
        'IIS-CommonHttpFeatures',
        'IIS-HttpErrors',
        'IIS-ApplicationDevelopment',
        'IIS-NetFxExtensibility45',
        'IIS-HealthAndDiagnostics',
        'IIS-HttpLogging',
        'IIS-Security',
        'IIS-RequestFiltering',
        'IIS-WebSockets',
        'Microsoft-Windows-Subsystem-Linux'
    )

    # Additional features based on profile
    switch ($DevProfile) {
        'FullStack' {
            $devFeatures += @('Containers', 'HypervisorPlatform', 'VirtualMachinePlatform')
        }
        'Backend' {
            $devFeatures += @('Containers', 'HypervisorPlatform')
        }
        'DataScience' {
            $devFeatures += @('HypervisorPlatform', 'VirtualMachinePlatform')
        }
        'DevOps' {
            $devFeatures += @('Containers', 'HypervisorPlatform', 'VirtualMachinePlatform', 'Microsoft-Hyper-V-All')
        }
    }

    foreach ($feature in $devFeatures) {
        try {
            Write-Host "  - Enabling: $feature" -ForegroundColor Gray
            Enable-WindowsImageFeature -FeatureName $feature -MountPath $mountPath -All -ErrorAction SilentlyContinue | Out-Null
        }
        catch {
            Write-Verbose "Could not enable $feature (may not be available in this edition)"
        }
    }

    Write-Host "✓ Development features enabled`n" -ForegroundColor Green

    # Step 4: Apply development optimizations
    Write-Host "[4/7] Applying development optimizations..." -ForegroundColor Cyan

    # Load SOFTWARE registry hive
    $regKey = "HKLM\TEMP_SOFTWARE"
    Mount-RegistryHive -Hive SOFTWARE -KeyName $regKey

    try {
        # Enable Developer Mode
        Write-Host "  - Enabling Developer Mode" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\AppModelUnlock" `
            -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\AppModelUnlock" `
            -Name "AllowAllTrustedApps" -Value 1 -Type DWord

        # Disable Windows Search indexing (performance)
        Write-Host "  - Configuring Windows Search" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows Search" `
            -Name "SetupCompletedSuccessfully" -Value 0 -Type DWord

        # Configure PowerShell execution policy
        Write-Host "  - Configuring PowerShell" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell" `
            -Name "ExecutionPolicy" -Value "RemoteSigned" -Type String

        # Enable long paths
        Write-Host "  - Enabling long path support" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Policies\System" `
            -Name "EnableLUA" -Value 1 -Type DWord

        # Disable unnecessary services for development
        Write-Host "  - Configuring services" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Policies\Explorer" `
            -Name "HideSCAMeetNow" -Value 1 -Type DWord

        # Explorer optimizations
        Write-Host "  - Optimizing File Explorer" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Explorer\Advanced" `
            -Name "HideFileExt" -Value 0 -Type DWord
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Explorer\Advanced" `
            -Name "Hidden" -Value 1 -Type DWord
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Explorer\Advanced" `
            -Name "ShowSuperHidden" -Value 1 -Type DWord

        # Performance optimizations
        Write-Host "  - Applying performance optimizations" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" `
            -Name "VisualFXSetting" -Value 2 -Type DWord

        # Git credential manager
        Write-Host "  - Configuring Git integration" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Uninstall\Git_is1" `
            -Name "Inno Setup: Selected Tasks" -Value "assoc,assoc_sh" -Type String
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    # Load SYSTEM registry hive
    $regKey = "HKLM\TEMP_SYSTEM"
    Mount-RegistryHive -Hive SYSTEM -KeyName $regKey

    try {
        # Enable long paths system-wide
        Write-Host "  - Enabling NTFS long paths" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Control\FileSystem" `
            -Name "LongPathsEnabled" -Value 1 -Type DWord

        # Network optimizations for Git/package managers
        Write-Host "  - Optimizing network stack" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\Tcpip\Parameters" `
            -Name "TcpAckFrequency" -Value 1 -Type DWord
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\Tcpip\Parameters" `
            -Name "TCPNoDelay" -Value 1 -Type DWord

        # Disable hibernation (free up disk space)
        Write-Host "  - Disabling hibernation" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Control\Power" `
            -Name "HibernateEnabled" -Value 0 -Type DWord
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    Write-Host "✓ Development optimizations applied`n" -ForegroundColor Green

    # Step 5: Remove bloatware
    Write-Host "[5/7] Removing unnecessary apps..." -ForegroundColor Cyan

    $bloatwareApps = @(
        '*3DBuilder*',
        '*BingNews*',
        '*BingWeather*',
        '*CandyCrush*',
        '*Getstarted*',
        '*MicrosoftSolitaire*',
        '*Netflix*',
        '*SkypeApp*',
        '*WindowsMaps*',
        '*XboxApp*',
        '*XboxGamingOverlay*',
        '*ZuneMusic*',
        '*ZuneVideo*'
    )

    foreach ($app in $bloatwareApps) {
        try {
            $packages = Get-AppxProvisionedPackage -Path $mountPath | Where-Object { $_.DisplayName -like $app }
            foreach ($package in $packages) {
                Write-Host "  - Removing: $($package.DisplayName)" -ForegroundColor Gray
                Remove-AppxProvisionedPackage -Path $mountPath -PackageName $package.PackageName -ErrorAction SilentlyContinue | Out-Null
            }
        }
        catch {
            Write-Verbose "Could not remove $app"
        }
    }

    Write-Host "✓ Unnecessary apps removed`n" -ForegroundColor Green

    # Step 6: Add development capabilities
    Write-Host "[6/7] Adding development capabilities..." -ForegroundColor Cyan

    $capabilities = @(
        'Tools.DeveloperMode.Core~~~~0.0.1.0',
        'OpenSSH.Client~~~~0.0.1.0'
    )

    foreach ($cap in $capabilities) {
        try {
            Write-Host "  - Adding: $cap" -ForegroundColor Gray
            Add-WindowsImageCapability -CapabilityName $cap -MountPath $mountPath -ErrorAction SilentlyContinue | Out-Null
        }
        catch {
            Write-Verbose "Could not add capability $cap"
        }
    }

    Write-Host "✓ Development capabilities added`n" -ForegroundColor Green

    # Step 7: Dismount and save
    Write-Host "[7/7] Saving changes..." -ForegroundColor Cyan
    Dismount-WindowsDeploymentImage -MountPath $mountPath -Save
    Write-Host ""

    # Display results
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output image: $OutputPath" -ForegroundColor Green
    Write-Host "Developer Profile: $DevProfile" -ForegroundColor Green

    $imageInfo = Get-WindowsImageInfo -ImagePath $OutputPath -Index $Index
    Write-Host "`nImage Information:" -ForegroundColor Cyan
    Write-Host "  Name: $($imageInfo.Name)" -ForegroundColor Gray
    Write-Host "  Size: $($imageInfo.Size) GB" -ForegroundColor Gray
    Write-Host "  Edition: $($imageInfo.EditionId)" -ForegroundColor Gray
    Write-Host ""

    Write-Host "✓ Developer image created successfully!" -ForegroundColor Green
    Write-Host "`nRecommended post-deployment steps:" -ForegroundColor Yellow
    Write-Host "  1. Install Visual Studio / VS Code" -ForegroundColor Gray
    Write-Host "  2. Install Git and configure credentials" -ForegroundColor Gray
    Write-Host "  3. Install Node.js, Python, or other runtimes" -ForegroundColor Gray
    Write-Host "  4. Configure WSL2 and Docker Desktop" -ForegroundColor Gray
    Write-Host "  5. Install package managers (chocolatey, scoop)" -ForegroundColor Gray
    Write-Host ""

}
catch {
    Write-Error "Build failed: $_"

    Write-Host "`nCleaning up..." -ForegroundColor Yellow
    try {
        Dismount-WindowsDeploymentImage -MountPath $mountPath -Discard
    }
    catch {
        Write-Warning "Failed to cleanup. Run: DISM /Cleanup-Mountpoints"
    }

    exit 1
}
finally {
    if (Test-Path $mountPath) {
        Remove-Item $mountPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}
