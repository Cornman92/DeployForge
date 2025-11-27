<#
.SYNOPSIS
    Create bootable Windows deployment USB using native Windows tools

.DESCRIPTION
    This script creates a bootable USB drive for Windows deployment using
    native Windows diskpart, DISM, and PowerShell commands. Supports both
    UEFI and Legacy BIOS boot modes.

.PARAMETER IsoPath
    Path to Windows ISO file

.PARAMETER DriveLetter
    Target USB drive letter (e.g., "E:")

.PARAMETER BootMode
    Boot mode: UEFI, Legacy, or Both (default: UEFI)

.PARAMETER Label
    Volume label for USB drive (default: "WIN_DEPLOY")

.EXAMPLE
    .\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Windows11.iso" -DriveLetter "E:" -BootMode UEFI

.EXAMPLE
    .\Build-DeploymentUSB.ps1 -IsoPath "C:\ISOs\Windows10.iso" -DriveLetter "F:" -BootMode Both -Label "WIN10_PRO"

.NOTES
    Author: DeployForge Team
    Version: 0.3.0
    Requires: Administrator privileges, Windows 8+
    WARNING: This will erase all data on the target USB drive!
#>

#Requires -Version 5.1
#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({Test-Path $_})]
    [string]$IsoPath,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Z]:$')]
    [string]$DriveLetter,

    [Parameter(Mandatory = $false)]
    [ValidateSet('UEFI', 'Legacy', 'Both')]
    [string]$BootMode = 'UEFI',

    [Parameter(Mandatory = $false)]
    [ValidateLength(1, 32)]
    [string]$Label = 'WIN_DEPLOY'
)

$ErrorActionPreference = 'Stop'

Write-Host "`n=== DeployForge USB Deployment Creator ===" -ForegroundColor Cyan
Write-Host "ISO: $IsoPath" -ForegroundColor Yellow
Write-Host "Target Drive: $DriveLetter" -ForegroundColor Yellow
Write-Host "Boot Mode: $BootMode" -ForegroundColor Yellow
Write-Host "Label: $Label`n" -ForegroundColor Yellow

# Validate USB drive
$drive = Get-Volume -DriveLetter $DriveLetter.Replace(':', '') -ErrorAction SilentlyContinue
if (-not $drive) {
    Write-Error "Drive $DriveLetter not found. Please specify a valid drive letter."
    exit 1
}

$diskNumber = (Get-Partition -DriveLetter $DriveLetter.Replace(':', '')).DiskNumber
$disk = Get-Disk -Number $diskNumber

# Verify it's a removable drive
if ($disk.BusType -notin @('USB', 'File Backed Virtual')) {
    Write-Warning "Drive $DriveLetter does not appear to be a USB drive (Bus Type: $($disk.BusType))"
    $confirm = Read-Host "Continue anyway? (yes/no)"
    if ($confirm -ne 'yes') {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Display drive information
Write-Host "=== Target Drive Information ===" -ForegroundColor Cyan
Write-Host "Disk Number: $diskNumber" -ForegroundColor Gray
Write-Host "Size: $([Math]::Round($disk.Size / 1GB, 2)) GB" -ForegroundColor Gray
Write-Host "Bus Type: $($disk.BusType)" -ForegroundColor Gray
Write-Host "Current Label: $($drive.FileSystemLabel)" -ForegroundColor Gray
Write-Host ""

# Warning
Write-Host "⚠️  WARNING: This will ERASE ALL DATA on drive $DriveLetter!" -ForegroundColor Red
Write-Host "⚠️  Disk Number: $diskNumber" -ForegroundColor Red
Write-Host ""
$confirmation = Read-Host "Type 'DELETE ALL DATA' to continue"
if ($confirmation -ne 'DELETE ALL DATA') {
    Write-Host "Operation cancelled." -ForegroundColor Yellow
    exit 0
}

try {
    # Step 1: Mount ISO
    Write-Host "`n[1/6] Mounting ISO..." -ForegroundColor Cyan
    $isoMount = Mount-DiskImage -ImagePath $IsoPath -PassThru
    $isoDrive = ($isoMount | Get-Volume).DriveLetter + ':'
    Write-Host "✓ ISO mounted at $isoDrive`n" -ForegroundColor Green

    # Step 2: Prepare USB drive
    Write-Host "[2/6] Preparing USB drive..." -ForegroundColor Cyan

    # Create diskpart script
    $diskpartScript = @"
select disk $diskNumber
clean
$(if ($BootMode -in @('UEFI', 'Both')) { "convert gpt" } else { "convert mbr" })
create partition primary
$(if ($BootMode -in @('UEFI', 'Both')) { "format fs=fat32 quick label=`"$Label`"" } else { "format fs=ntfs quick label=`"$Label`"" })
assign letter=$($DriveLetter.Replace(':', ''))
active
exit
"@

    $diskpartScriptPath = "$env:TEMP\deployforge-diskpart.txt"
    Set-Content -Path $diskpartScriptPath -Value $diskpartScript -Encoding ASCII

    Write-Host "  - Cleaning and partitioning drive..." -ForegroundColor Gray
    $diskpartOutput = diskpart /s $diskpartScriptPath 2>&1

    # Wait for drive to be ready
    Start-Sleep -Seconds 3

    # Verify drive is ready
    $usbDrive = Get-Volume -DriveLetter $DriveLetter.Replace(':', '') -ErrorAction SilentlyContinue
    if (-not $usbDrive) {
        throw "Failed to create partition on USB drive"
    }

    Write-Host "✓ USB drive prepared`n" -ForegroundColor Green

    # Step 3: Copy Windows files
    Write-Host "[3/6] Copying Windows files..." -ForegroundColor Cyan
    Write-Host "  This may take 10-20 minutes depending on USB speed..." -ForegroundColor Gray

    $sourceFiles = Get-ChildItem -Path "$isoDrive\" -Recurse
    $totalFiles = $sourceFiles.Count
    $copiedFiles = 0

    foreach ($file in $sourceFiles) {
        $copiedFiles++
        $percentComplete = [math]::Round(($copiedFiles / $totalFiles) * 100, 1)

        if ($copiedFiles % 100 -eq 0) {
            Write-Progress -Activity "Copying Windows files" -Status "$percentComplete% Complete" -PercentComplete $percentComplete
        }

        $destination = $file.FullName.Replace($isoDrive, $DriveLetter)

        if ($file.PSIsContainer) {
            if (-not (Test-Path $destination)) {
                New-Item -ItemType Directory -Path $destination -Force | Out-Null
            }
        }
        else {
            # Handle large files (>4GB) for FAT32
            if ($BootMode -in @('UEFI', 'Both') -and $file.Length -gt 4GB) {
                Write-Host "`n  ⚠️  Large file detected: $($file.Name) ($([math]::Round($file.Length/1GB, 2)) GB)" -ForegroundColor Yellow
                Write-Host "  FAT32 has 4GB file size limit. Splitting file..." -ForegroundColor Yellow

                # For install.wim, split it
                if ($file.Name -eq 'install.wim') {
                    $sourcesPath = Join-Path $DriveLetter "sources"
                    if (-not (Test-Path $sourcesPath)) {
                        New-Item -ItemType Directory -Path $sourcesPath -Force | Out-Null
                    }

                    Write-Host "  Splitting install.wim into install.swm files..." -ForegroundColor Gray
                    & dism /Split-Image /ImageFile:"$($file.FullName)" /SWMFile:"$sourcesPath\install.swm" /FileSize:3800 | Out-Null
                    Write-Host "  ✓ install.wim split successfully" -ForegroundColor Green
                    continue
                }
            }

            Copy-Item -Path $file.FullName -Destination $destination -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Progress -Activity "Copying Windows files" -Completed
    Write-Host "✓ Windows files copied`n" -ForegroundColor Green

    # Step 4: Make bootable (UEFI)
    if ($BootMode -in @('UEFI', 'Both')) {
        Write-Host "[4/6] Configuring UEFI boot..." -ForegroundColor Cyan

        # UEFI boot files should already be in place
        $efiBootPath = Join-Path $DriveLetter "efi\boot"
        if (Test-Path $efiBootPath) {
            Write-Host "✓ UEFI boot files present`n" -ForegroundColor Green
        }
        else {
            Write-Warning "UEFI boot files not found. USB may not boot in UEFI mode."
        }
    }

    # Step 5: Make bootable (Legacy BIOS)
    if ($BootMode -in @('Legacy', 'Both')) {
        Write-Host "[5/6] Configuring Legacy BIOS boot..." -ForegroundColor Cyan

        $bootSectorSource = Join-Path $isoDrive "boot\bootsect.exe"
        if (Test-Path $bootSectorSource) {
            Write-Host "  - Writing boot sector..." -ForegroundColor Gray
            & "$bootSectorSource" /nt60 $DriveLetter /mbr /force | Out-Null
            Write-Host "✓ Legacy BIOS boot configured`n" -ForegroundColor Green
        }
        else {
            Write-Warning "bootsect.exe not found. Cannot configure Legacy BIOS boot."
        }
    }
    else {
        Write-Host "[5/6] Skipping Legacy BIOS configuration`n" -ForegroundColor Gray
    }

    # Step 6: Verify and cleanup
    Write-Host "[6/6] Verifying and cleaning up..." -ForegroundColor Cyan

    # Verify boot files
    $bootFiles = @{
        UEFI = @(
            "efi\boot\bootx64.efi",
            "efi\microsoft\boot\bcd"
        )
        Legacy = @(
            "bootmgr",
            "boot\bcd"
        )
    }

    $missingFiles = @()

    if ($BootMode -in @('UEFI', 'Both')) {
        foreach ($file in $bootFiles.UEFI) {
            if (-not (Test-Path (Join-Path $DriveLetter $file))) {
                $missingFiles += $file
            }
        }
    }

    if ($BootMode -in @('Legacy', 'Both')) {
        foreach ($file in $bootFiles.Legacy) {
            if (-not (Test-Path (Join-Path $DriveLetter $file))) {
                $missingFiles += $file
            }
        }
    }

    if ($missingFiles.Count -gt 0) {
        Write-Warning "Some boot files are missing:"
        $missingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        Write-Host ""
    }

    # Dismount ISO
    Dismount-DiskImage -ImagePath $IsoPath | Out-Null

    # Cleanup temp files
    Remove-Item $diskpartScriptPath -Force -ErrorAction SilentlyContinue

    Write-Host "✓ Verification complete`n" -ForegroundColor Green

    # Display results
    Write-Host "=== USB Creation Complete ===" -ForegroundColor Green
    Write-Host "Drive: $DriveLetter" -ForegroundColor Green
    Write-Host "Label: $Label" -ForegroundColor Green
    Write-Host "Boot Mode: $BootMode" -ForegroundColor Green
    Write-Host ""

    Write-Host "✓ Bootable USB drive created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Safely eject the USB drive" -ForegroundColor Gray
    Write-Host "  2. Boot target computer from USB" -ForegroundColor Gray
    if ($BootMode -eq 'UEFI') {
        Write-Host "  3. Ensure UEFI boot is enabled in BIOS" -ForegroundColor Gray
        Write-Host "  4. Disable Secure Boot if installation fails" -ForegroundColor Gray
    }
    elseif ($BootMode -eq 'Legacy') {
        Write-Host "  3. Ensure Legacy/CSM boot is enabled in BIOS" -ForegroundColor Gray
    }
    else {
        Write-Host "  3. Choose UEFI or Legacy boot in BIOS settings" -ForegroundColor Gray
    }
    Write-Host "  5. Follow Windows installation wizard" -ForegroundColor Gray
    Write-Host ""

}
catch {
    Write-Error "USB creation failed: $_"

    Write-Host "`nCleaning up..." -ForegroundColor Yellow
    try {
        # Dismount ISO if mounted
        Dismount-DiskImage -ImagePath $IsoPath -ErrorAction SilentlyContinue | Out-Null
    }
    catch {}

    try {
        # Cleanup temp files
        Remove-Item "$env:TEMP\deployforge-diskpart.txt" -Force -ErrorAction SilentlyContinue
    }
    catch {}

    exit 1
}
