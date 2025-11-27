<#
.SYNOPSIS
    Inject drivers into Windows deployment image using native DISM

.DESCRIPTION
    This script automates driver injection into Windows images using native
    DISM commands. Supports both online and offline driver injection.

.PARAMETER ImagePath
    Path to the Windows image file (WIM/ESD)

.PARAMETER DriverPath
    Path to folder containing driver .inf files

.PARAMETER Index
    Image index to modify (default: 1)

.PARAMETER Recurse
    Search for drivers recursively in subfolders

.PARAMETER ForceUnsigned
    Allow unsigned drivers to be installed

.EXAMPLE
    .\Update-ImageDrivers.ps1 -ImagePath "C:\Images\install.wim" -DriverPath "C:\Drivers\Network" -Recurse

.EXAMPLE
    .\Update-ImageDrivers.ps1 -ImagePath "C:\Images\boot.wim" -DriverPath "C:\Drivers" -Index 2 -Recurse -ForceUnsigned

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges
#>

#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({Test-Path $_})]
    [string]$ImagePath,

    [Parameter(Mandatory = $true)]
    [ValidateScript({Test-Path $_})]
    [string]$DriverPath,

    [Parameter(Mandatory = $false)]
    [int]$Index = 1,

    [Parameter(Mandatory = $false)]
    [switch]$Recurse,

    [Parameter(Mandatory = $false)]
    [switch]$ForceUnsigned
)

# Import utilities
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\DeployForge-Utilities.psm1" -Force

$mountPath = "$env:TEMP\DeployForge\Mount"

Write-Host "`n=== DeployForge Driver Injection Tool ===" -ForegroundColor Cyan
Write-Host "Image: $ImagePath" -ForegroundColor Yellow
Write-Host "Drivers: $DriverPath" -ForegroundColor Yellow
Write-Host "Recurse: $Recurse" -ForegroundColor Yellow
Write-Host "Force Unsigned: $ForceUnsigned`n" -ForegroundColor Yellow

try {
    # Step 1: Scan driver folder
    Write-Host "[1/5] Scanning driver folder..." -ForegroundColor Cyan

    $infFiles = if ($Recurse) {
        Get-ChildItem -Path $DriverPath -Filter "*.inf" -Recurse -File
    } else {
        Get-ChildItem -Path $DriverPath -Filter "*.inf" -File
    }

    $driverCount = $infFiles.Count
    Write-Host "✓ Found $driverCount driver package(s)`n" -ForegroundColor Green

    if ($driverCount -eq 0) {
        Write-Warning "No driver .inf files found in $DriverPath"
        exit 0
    }

    # Display driver details
    Write-Host "Driver packages found:" -ForegroundColor Cyan
    foreach ($inf in $infFiles) {
        Write-Host "  - $($inf.Name) ($($inf.DirectoryName))" -ForegroundColor Gray
    }
    Write-Host ""

    # Step 2: Create backup
    Write-Host "[2/5] Creating backup..." -ForegroundColor Cyan
    $backupPath = "$ImagePath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item -Path $ImagePath -Destination $backupPath -Force
    Write-Host "✓ Backup created: $backupPath`n" -ForegroundColor Green

    # Step 3: Mount image
    Write-Host "[3/5] Mounting image..." -ForegroundColor Cyan
    Mount-WindowsDeploymentImage -ImagePath $ImagePath -Index $Index -MountPath $mountPath
    Write-Host ""

    # Step 4: Inject drivers
    Write-Host "[4/5] Injecting drivers..." -ForegroundColor Cyan

    $successCount = 0
    $failCount = 0
    $skippedCount = 0

    foreach ($inf in $infFiles) {
        try {
            Write-Host "  - Injecting: $($inf.Name)" -ForegroundColor Gray

            $driverArgs = @{
                Path = $mountPath
                Driver = $inf.FullName
                ErrorAction = 'Stop'
            }

            if ($ForceUnsigned) {
                $driverArgs.Add('ForceUnsigned', $true)
            }

            Add-WindowsDriver @driverArgs | Out-Null
            $successCount++
            Write-Host "    ✓ Success" -ForegroundColor Green
        }
        catch {
            if ($_.Exception.Message -like "*already installed*") {
                Write-Host "    ⚠ Already installed" -ForegroundColor Yellow
                $skippedCount++
            }
            else {
                Write-Host "    ✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
                $failCount++
            }
        }
    }

    Write-Host "`n✓ Driver injection complete" -ForegroundColor Green
    Write-Host "  Success: $successCount" -ForegroundColor Green
    Write-Host "  Skipped: $skippedCount" -ForegroundColor Yellow
    Write-Host "  Failed: $failCount`n" -ForegroundColor $(if ($failCount -gt 0) { 'Red' } else { 'Gray' })

    # Step 5: Dismount and save
    Write-Host "[5/5] Saving changes..." -ForegroundColor Cyan
    Dismount-WindowsDeploymentImage -MountPath $mountPath -Save
    Write-Host ""

    # Display final status
    Write-Host "=== Driver Injection Complete ===" -ForegroundColor Green
    Write-Host "Image: $ImagePath" -ForegroundColor Green
    Write-Host "Drivers injected: $successCount/$driverCount" -ForegroundColor Green

    if ($failCount -gt 0) {
        Write-Host "`nWarning: $failCount driver(s) failed to inject" -ForegroundColor Yellow
        Write-Host "Check DISM logs for details: C:\Windows\Logs\DISM\dism.log" -ForegroundColor Gray
    }

    Write-Host "`nBackup location: $backupPath" -ForegroundColor Cyan
    Write-Host ""

    # List drivers in image
    Write-Host "Drivers now in image:" -ForegroundColor Cyan
    $installedDrivers = Get-WindowsDriver -Path $mountPath
    $installedDrivers | ForEach-Object {
        Write-Host "  - $($_.ClassName): $($_.ProviderName) v$($_.Version)" -ForegroundColor Gray
    }
    Write-Host ""

    Write-Host "✓ Operation completed successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Driver injection failed: $_"

    Write-Host "`nCleaning up..." -ForegroundColor Yellow
    try {
        # Check if image is mounted
        $mountedImages = Get-WindowsImage -Mounted
        $ourMount = $mountedImages | Where-Object { $_.Path -eq $mountPath }

        if ($ourMount) {
            Write-Host "Discarding changes..." -ForegroundColor Yellow
            Dismount-WindowsDeploymentImage -MountPath $mountPath -Discard
        }
    }
    catch {
        Write-Warning "Failed to cleanup. Run: DISM /Cleanup-Mountpoints"
    }

    Write-Host "`nRestore from backup if needed: $backupPath" -ForegroundColor Yellow
    exit 1
}
finally {
    if (Test-Path $mountPath) {
        Remove-Item $mountPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}
