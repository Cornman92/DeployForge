<#
.SYNOPSIS
    Build a gaming-optimized Windows image using native DISM and PowerShell

.DESCRIPTION
    This script creates a gaming-optimized Windows deployment image using
    native Windows tools (DISM, reg.exe, PowerShell). No external dependencies required.

.PARAMETER ImagePath
    Path to the Windows image file (WIM/ESD)

.PARAMETER OutputPath
    Path where the customized image will be saved

.PARAMETER Index
    Image index to use (default: 1)

.PARAMETER Profile
    Gaming profile: Competitive, Balanced, Quality, or Streaming

.EXAMPLE
    .\Build-GamingImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\gaming.wim" -Profile Competitive

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges, Windows 10/11
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
    [ValidateSet('Competitive', 'Balanced', 'Quality', 'Streaming')]
    [string]$Profile = 'Balanced'
)

# Import utilities
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\DeployForge-Utilities.psm1" -Force

# Configuration
$mountPath = "$env:TEMP\DeployForge\Mount"

Write-Host "`n=== DeployForge Gaming Image Builder ===" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor Yellow
Write-Host "Source: $ImagePath" -ForegroundColor Yellow
Write-Host "Output: $OutputPath`n" -ForegroundColor Yellow

try {
    # Step 1: Copy source image
    Write-Host "[1/6] Copying source image..." -ForegroundColor Cyan
    Copy-Item -Path $ImagePath -Destination $OutputPath -Force
    Write-Host "✓ Image copied`n" -ForegroundColor Green

    # Step 2: Mount image
    Write-Host "[2/6] Mounting image..." -ForegroundColor Cyan
    Mount-WindowsDeploymentImage -ImagePath $OutputPath -Index $Index -MountPath $mountPath
    Write-Host ""

    # Step 3: Apply gaming optimizations
    Write-Host "[3/6] Applying gaming optimizations..." -ForegroundColor Cyan

    # Load SOFTWARE registry hive
    $regKey = "HKLM\TEMP_SOFTWARE"
    Mount-RegistryHive -Hive SOFTWARE -KeyName $regKey

    try {
        # Enable Game Mode
        Write-Host "  - Enabling Game Mode" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\GameBar" -Name "AutoGameModeEnabled" -Value 1 -Type DWord

        # Enable GPU Hardware Scheduling
        if ($Profile -in @('Competitive', 'Quality')) {
            Write-Host "  - Enabling GPU Hardware Scheduling" -ForegroundColor Gray
            Set-OfflineRegistryValue -Path "$regKey\Microsoft\DirectX" -Name "HwSchMode" -Value 2 -Type DWord
        }

        # Disable Fullscreen Optimizations (Competitive)
        if ($Profile -eq 'Competitive') {
            Write-Host "  - Disabling Fullscreen Optimizations" -ForegroundColor Gray
            Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers" `
                -Name "DisableFullscreenOptimizations" -Value 1 -Type DWord
        }

        # Disable Game DVR
        Write-Host "  - Disabling Game DVR" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -Value 0 -Type DWord
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\GameDVR" -Name "GameDVR_Enabled" -Value 0 -Type DWord

        # Network optimizations
        Write-Host "  - Applying network optimizations" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Microsoft\MSMQ\Parameters" -Name "TCPNoDelay" -Value 1 -Type DWord
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    # Load SYSTEM registry hive
    $regKey = "HKLM\TEMP_SYSTEM"
    Mount-RegistryHive -Hive SYSTEM -KeyName $regKey

    try {
        # Set Ultimate Performance power plan
        if ($Profile -in @('Competitive', 'Streaming')) {
            Write-Host "  - Configuring Ultimate Performance power plan" -ForegroundColor Gray
            Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Control\Power" -Name "CsEnabled" -Value 0 -Type DWord
        }

        # Disable unnecessary services
        Write-Host "  - Disabling unnecessary services" -ForegroundColor Gray
        $servicesToDisable = @('SysMain', 'WSearch', 'DiagTrack', 'dmwappushservice')
        foreach ($service in $servicesToDisable) {
            Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\$service" -Name "Start" -Value 4 -Type DWord
        }
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    Write-Host "✓ Gaming optimizations applied`n" -ForegroundColor Green

    # Step 4: Remove bloatware
    Write-Host "[4/6] Removing bloatware..." -ForegroundColor Cyan

    $bloatwareApps = @(
        '*3DBuilder*',
        '*BingNews*',
        '*BingSports*',
        '*BingWeather*',
        '*Getstarted*',
        '*MicrosoftOfficeHub*',
        '*SkypeApp*',
        '*Solitaire*',
        '*WindowsMaps*',
        '*ZuneMusic*',
        '*ZuneVideo*',
        '*Xbox.TCUI*',
        '*XboxApp*',
        '*XboxGameOverlay*',
        '*XboxGamingOverlay*',
        '*XboxIdentityProvider*',
        '*XboxSpeechToTextOverlay*'
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

    Write-Host "✓ Bloatware removed`n" -ForegroundColor Green

    # Step 5: Disable Windows capabilities
    Write-Host "[5/6] Disabling unnecessary capabilities..." -ForegroundColor Cyan

    $capabilitiesToRemove = @(
        'Microsoft.Windows.WordPad*',
        'Microsoft.Windows.PowerShell.ISE*',
        'App.Support.QuickAssist*'
    )

    foreach ($cap in $capabilitiesToRemove) {
        try {
            $capabilities = Get-WindowsCapability -Path $mountPath | Where-Object { $_.Name -like $cap }
            foreach ($capability in $capabilities) {
                if ($capability.State -eq 'Installed') {
                    Write-Host "  - Removing: $($capability.Name)" -ForegroundColor Gray
                    Remove-WindowsImageCapability -CapabilityName $capability.Name -MountPath $mountPath
                }
            }
        }
        catch {
            Write-Verbose "Could not remove capability $cap"
        }
    }

    Write-Host "✓ Capabilities removed`n" -ForegroundColor Green

    # Step 6: Dismount and save
    Write-Host "[6/6] Saving changes..." -ForegroundColor Cyan
    Dismount-WindowsDeploymentImage -MountPath $mountPath -Save
    Write-Host ""

    # Display results
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output image: $OutputPath" -ForegroundColor Green
    Write-Host "Profile: $Profile" -ForegroundColor Green

    $imageInfo = Get-WindowsImageInfo -ImagePath $OutputPath -Index $Index
    Write-Host "`nImage Information:" -ForegroundColor Cyan
    Write-Host "  Name: $($imageInfo.Name)" -ForegroundColor Gray
    Write-Host "  Size: $($imageInfo.Size) GB" -ForegroundColor Gray
    Write-Host "  Architecture: $($imageInfo.Architecture)" -ForegroundColor Gray
    Write-Host "  Version: $($imageInfo.Version)" -ForegroundColor Gray
    Write-Host ""

    Write-Host "✓ Gaming image created successfully!" -ForegroundColor Green

}
catch {
    Write-Error "Build failed: $_"

    # Cleanup on error
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
    # Cleanup temp files
    if (Test-Path $mountPath) {
        Remove-Item $mountPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}
