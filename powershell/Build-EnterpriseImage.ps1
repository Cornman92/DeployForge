<#
.SYNOPSIS
    Build an enterprise-hardened Windows image using native DISM and PowerShell

.DESCRIPTION
    This script creates an enterprise-ready Windows deployment image with
    security hardening using native Windows tools.

.PARAMETER ImagePath
    Path to the Windows image file (WIM/ESD)

.PARAMETER OutputPath
    Path where the customized image will be saved

.PARAMETER Index
    Image index to use (default: 1)

.PARAMETER EnableBitLocker
    Enable BitLocker preparation

.PARAMETER ApplyCISBenchmark
    Apply CIS Benchmark security settings

.EXAMPLE
    .\Build-EnterpriseImage.ps1 -ImagePath "C:\Images\install.wim" -OutputPath "C:\Images\enterprise.wim" -ApplyCISBenchmark

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges, Windows 10/11 Enterprise/Pro
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
    [switch]$EnableBitLocker,

    [Parameter(Mandatory = $false)]
    [switch]$ApplyCISBenchmark
)

# Import utilities
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\DeployForge-Utilities.psm1" -Force

$mountPath = "$env:TEMP\DeployForge\Mount"

Write-Host "`n=== DeployForge Enterprise Image Builder ===" -ForegroundColor Cyan
Write-Host "Source: $ImagePath" -ForegroundColor Yellow
Write-Host "Output: $OutputPath" -ForegroundColor Yellow
Write-Host "BitLocker: $EnableBitLocker" -ForegroundColor Yellow
Write-Host "CIS Benchmark: $ApplyCISBenchmark`n" -ForegroundColor Yellow

try {
    # Step 1: Copy source image
    Write-Host "[1/5] Copying source image..." -ForegroundColor Cyan
    Copy-Item -Path $ImagePath -Destination $OutputPath -Force
    Write-Host "✓ Image copied`n" -ForegroundColor Green

    # Step 2: Mount image
    Write-Host "[2/5] Mounting image..." -ForegroundColor Cyan
    Mount-WindowsDeploymentImage -ImagePath $OutputPath -Index $Index -MountPath $mountPath
    Write-Host ""

    # Step 3: Apply security hardening
    Write-Host "[3/5] Applying security hardening..." -ForegroundColor Cyan

    # Load SOFTWARE registry hive
    $regKey = "HKLM\TEMP_SOFTWARE"
    Mount-RegistryHive -Hive SOFTWARE -KeyName $regKey

    try {
        # Disable Cortana
        Write-Host "  - Disabling Cortana" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Policies\Microsoft\Windows\Windows Search" `
            -Name "AllowCortana" -Value 0 -Type DWord

        # Disable telemetry
        Write-Host "  - Disabling telemetry" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Policies\Microsoft\Windows\DataCollection" `
            -Name "AllowTelemetry" -Value 0 -Type DWord

        # Disable consumer features
        Write-Host "  - Disabling consumer features" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Policies\Microsoft\Windows\CloudContent" `
            -Name "DisableWindowsConsumerFeatures" -Value 1 -Type DWord

        # Enable Windows Defender
        Write-Host "  - Configuring Windows Defender" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\Policies\Microsoft\Windows Defender" `
            -Name "DisableAntiSpyware" -Value 0 -Type DWord

        if ($ApplyCISBenchmark) {
            Write-Host "  - Applying CIS Benchmark settings" -ForegroundColor Gray

            # Require CTRL+ALT+DEL at logon
            Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Policies\System" `
                -Name "DisableCAD" -Value 0 -Type DWord

            # Disable Anonymous SID enumeration
            Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Policies\System" `
                -Name "RestrictAnonymousSAM" -Value 1 -Type DWord

            # Enable SMB signing
            Set-OfflineRegistryValue -Path "$regKey\Microsoft\Windows\CurrentVersion\Policies\System" `
                -Name "RequireSecuritySignature" -Value 1 -Type DWord
        }
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    # Load SYSTEM registry hive
    $regKey = "HKLM\TEMP_SYSTEM"
    Mount-RegistryHive -Hive SYSTEM -KeyName $regKey

    try {
        # Enable Windows Firewall
        Write-Host "  - Enabling Windows Firewall" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile" `
            -Name "EnableFirewall" -Value 1 -Type DWord

        # Disable SMBv1
        Write-Host "  - Disabling SMBv1" -ForegroundColor Gray
        Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\LanmanServer\Parameters" `
            -Name "SMB1" -Value 0 -Type DWord

        if ($ApplyCISBenchmark) {
            # Additional CIS settings
            Write-Host "  - Applying additional CIS settings" -ForegroundColor Gray

            # Disable LLMNR
            Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Services\Dnscache\Parameters" `
                -Name "EnableMulticast" -Value 0 -Type DWord

            # Enable UAC
            Set-OfflineRegistryValue -Path "$regKey\ControlSet001\Control\Lsa" `
                -Name "LimitBlankPasswordUse" -Value 1 -Type DWord
        }
    }
    finally {
        Dismount-RegistryHive -KeyName $regKey
    }

    Write-Host "✓ Security hardening applied`n" -ForegroundColor Green

    # Step 4: Enable Windows features
    Write-Host "[4/5] Configuring Windows features..." -ForegroundColor Cyan

    if ($EnableBitLocker) {
        Write-Host "  - Enabling BitLocker" -ForegroundColor Gray
        Enable-WindowsImageFeature -FeatureName "BitLocker" -MountPath $mountPath -All
    }

    # Enable Windows Defender features
    Write-Host "  - Enabling Windows Defender features" -ForegroundColor Gray
    Enable-WindowsImageFeature -FeatureName "Windows-Defender-Default-Definitions" -MountPath $mountPath

    Write-Host "✓ Features configured`n" -ForegroundColor Green

    # Step 5: Dismount and save
    Write-Host "[5/5] Saving changes..." -ForegroundColor Cyan
    Dismount-WindowsDeploymentImage -MountPath $mountPath -Save
    Write-Host ""

    # Display results
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Output image: $OutputPath" -ForegroundColor Green

    $imageInfo = Get-WindowsImageInfo -ImagePath $OutputPath -Index $Index
    Write-Host "`nImage Information:" -ForegroundColor Cyan
    Write-Host "  Name: $($imageInfo.Name)" -ForegroundColor Gray
    Write-Host "  Size: $($imageInfo.Size) GB" -ForegroundColor Gray
    Write-Host "  Edition: $($imageInfo.EditionId)" -ForegroundColor Gray
    Write-Host ""

    Write-Host "✓ Enterprise image created successfully!" -ForegroundColor Green

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
