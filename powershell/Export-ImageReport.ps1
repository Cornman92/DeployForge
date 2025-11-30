<#
.SYNOPSIS
    Generate comprehensive report for Windows deployment image

.DESCRIPTION
    This script analyzes a Windows image and generates a detailed report
    including installed packages, drivers, features, capabilities, and more.

.PARAMETER ImagePath
    Path to the Windows image file (WIM/ESD)

.PARAMETER OutputPath
    Path where the report will be saved (default: same folder as image)

.PARAMETER Index
    Image index to analyze (default: 1)

.PARAMETER Format
    Report format: HTML, JSON, or Text (default: HTML)

.EXAMPLE
    .\Export-ImageReport.ps1 -ImagePath "C:\Images\install.wim" -Format HTML

.EXAMPLE
    .\Export-ImageReport.ps1 -ImagePath "C:\Images\custom.wim" -Index 2 -OutputPath "C:\Reports\image-report.html"

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

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [int]$Index = 1,

    [Parameter(Mandatory = $false)]
    [ValidateSet('HTML', 'JSON', 'Text')]
    [string]$Format = 'HTML'
)

# Import utilities
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\DeployForge-Utilities.psm1" -Force

$mountPath = "$env:TEMP\DeployForge\Mount"

# Determine output path
if (-not $OutputPath) {
    $imageFolder = Split-Path -Parent $ImagePath
    $imageName = [System.IO.Path]::GetFileNameWithoutExtension($ImagePath)
    $extension = switch ($Format) {
        'HTML' { 'html' }
        'JSON' { 'json' }
        'Text' { 'txt' }
    }
    $OutputPath = Join-Path $imageFolder "$imageName-report.$extension"
}

Write-Host "`n=== DeployForge Image Report Generator ===" -ForegroundColor Cyan
Write-Host "Image: $ImagePath" -ForegroundColor Yellow
Write-Host "Index: $Index" -ForegroundColor Yellow
Write-Host "Format: $Format" -ForegroundColor Yellow
Write-Host "Output: $OutputPath`n" -ForegroundColor Yellow

$reportData = @{
    GeneratedDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    ImagePath = $ImagePath
    Index = $Index
}

try {
    # Step 1: Get basic image info
    Write-Host "[1/8] Gathering basic image information..." -ForegroundColor Cyan
    $imageInfo = Get-WindowsImageInfo -ImagePath $ImagePath -Index $Index
    $reportData.ImageInfo = $imageInfo
    Write-Host "✓ Image: $($imageInfo.Name) ($($imageInfo.EditionId))`n" -ForegroundColor Green

    # Step 2: Mount image (read-only)
    Write-Host "[2/8] Mounting image (read-only)..." -ForegroundColor Cyan
    Mount-WindowsDeploymentImage -ImagePath $ImagePath -Index $Index -MountPath $mountPath -ReadOnly
    Write-Host ""

    # Step 3: Get installed packages
    Write-Host "[3/8] Enumerating installed packages..." -ForegroundColor Cyan
    $packages = Get-AppxProvisionedPackage -Path $mountPath
    $reportData.Packages = $packages | Select-Object DisplayName, Version, Architecture
    Write-Host "✓ Found $($packages.Count) provisioned packages`n" -ForegroundColor Green

    # Step 4: Get drivers
    Write-Host "[4/8] Enumerating drivers..." -ForegroundColor Cyan
    $drivers = Get-WindowsDriver -Path $mountPath
    $reportData.Drivers = $drivers | Select-Object ClassName, ProviderName, Version, Date
    Write-Host "✓ Found $($drivers.Count) drivers`n" -ForegroundColor Green

    # Step 5: Get Windows features
    Write-Host "[5/8] Enumerating Windows features..." -ForegroundColor Cyan
    $features = Get-WindowsOptionalFeature -Path $mountPath
    $enabledFeatures = $features | Where-Object { $_.State -eq 'Enabled' }
    $reportData.Features = @{
        Total = $features.Count
        Enabled = $enabledFeatures.Count
        EnabledList = $enabledFeatures | Select-Object FeatureName, State
    }
    Write-Host "✓ Found $($features.Count) features ($($enabledFeatures.Count) enabled)`n" -ForegroundColor Green

    # Step 6: Get capabilities
    Write-Host "[6/8] Enumerating capabilities..." -ForegroundColor Cyan
    $capabilities = Get-WindowsCapability -Path $mountPath
    $installedCapabilities = $capabilities | Where-Object { $_.State -eq 'Installed' }
    $reportData.Capabilities = @{
        Total = $capabilities.Count
        Installed = $installedCapabilities.Count
        InstalledList = $installedCapabilities | Select-Object Name, State
    }
    Write-Host "✓ Found $($capabilities.Count) capabilities ($($installedCapabilities.Count) installed)`n" -ForegroundColor Green

    # Step 7: Get file statistics
    Write-Host "[7/8] Calculating file statistics..." -ForegroundColor Cyan
    $fileCount = (Get-ChildItem -Path $mountPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    $folderCount = (Get-ChildItem -Path $mountPath -Recurse -Directory -ErrorAction SilentlyContinue | Measure-Object).Count
    $reportData.FileSystem = @{
        Files = $fileCount
        Folders = $folderCount
    }
    Write-Host "✓ $fileCount files in $folderCount folders`n" -ForegroundColor Green

    # Step 8: Dismount image
    Write-Host "[8/8] Dismounting image..." -ForegroundColor Cyan
    Dismount-WindowsDeploymentImage -MountPath $mountPath -Discard
    Write-Host ""

    # Generate report
    Write-Host "Generating report..." -ForegroundColor Cyan

    switch ($Format) {
        'HTML' {
            $html = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Windows Image Report - $($imageInfo.Name)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0078D4; border-bottom: 3px solid #0078D4; padding-bottom: 10px; }
        h2 { color: #106EBE; margin-top: 30px; border-bottom: 2px solid #E1E1E1; padding-bottom: 8px; }
        h3 { color: #2B579A; margin-top: 20px; }
        .info-grid { display: grid; grid-template-columns: 200px 1fr; gap: 10px; margin: 20px 0; }
        .info-label { font-weight: bold; color: #555; }
        .info-value { color: #333; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0078D4; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #E1E1E1; }
        tr:hover { background: #F8F8F8; }
        .metric { display: inline-block; background: #E1F5FF; padding: 15px 25px; margin: 10px; border-radius: 5px; border-left: 4px solid #0078D4; }
        .metric-value { font-size: 24px; font-weight: bold; color: #0078D4; }
        .metric-label { color: #555; font-size: 14px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #E1E1E1; color: #777; font-size: 12px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖼️ Windows Image Report</h1>
        <p><strong>Generated:</strong> $($reportData.GeneratedDate)</p>

        <h2>📋 Image Information</h2>
        <div class="info-grid">
            <div class="info-label">Image Path:</div>
            <div class="info-value">$ImagePath</div>
            <div class="info-label">Image Name:</div>
            <div class="info-value">$($imageInfo.Name)</div>
            <div class="info-label">Edition:</div>
            <div class="info-value">$($imageInfo.EditionId)</div>
            <div class="info-label">Architecture:</div>
            <div class="info-value">$($imageInfo.Architecture)</div>
            <div class="info-label">Version:</div>
            <div class="info-value">$($imageInfo.Version)</div>
            <div class="info-label">Build:</div>
            <div class="info-value">$($imageInfo.Build)</div>
            <div class="info-label">Size:</div>
            <div class="info-value">$($imageInfo.Size) GB</div>
            <div class="info-label">Language:</div>
            <div class="info-value">$($imageInfo.Languages -join ', ')</div>
        </div>

        <h2>📊 Summary Statistics</h2>
        <div>
            <div class="metric">
                <div class="metric-value">$($packages.Count)</div>
                <div class="metric-label">Provisioned Packages</div>
            </div>
            <div class="metric">
                <div class="metric-value">$($drivers.Count)</div>
                <div class="metric-label">Drivers</div>
            </div>
            <div class="metric">
                <div class="metric-value">$($enabledFeatures.Count)</div>
                <div class="metric-label">Enabled Features</div>
            </div>
            <div class="metric">
                <div class="metric-value">$($installedCapabilities.Count)</div>
                <div class="metric-label">Installed Capabilities</div>
            </div>
            <div class="metric">
                <div class="metric-value">$fileCount</div>
                <div class="metric-label">Files</div>
            </div>
        </div>

        <h2>📦 Provisioned Packages (Top 20)</h2>
        <table>
            <tr><th>Package Name</th><th>Version</th><th>Architecture</th></tr>
"@
            $packages | Select-Object -First 20 | ForEach-Object {
                $html += "<tr><td>$($_.DisplayName)</td><td>$($_.Version)</td><td>$($_.Architecture)</td></tr>`n"
            }

            $html += @"
        </table>

        <h2>🔧 Installed Drivers (Top 20)</h2>
        <table>
            <tr><th>Class</th><th>Provider</th><th>Version</th><th>Date</th></tr>
"@
            $drivers | Select-Object -First 20 | ForEach-Object {
                $html += "<tr><td>$($_.ClassName)</td><td>$($_.ProviderName)</td><td>$($_.Version)</td><td>$($_.Date)</td></tr>`n"
            }

            $html += @"
        </table>

        <h2>⚙️ Enabled Windows Features (Top 20)</h2>
        <table>
            <tr><th>Feature Name</th><th>State</th></tr>
"@
            $enabledFeatures | Select-Object -First 20 | ForEach-Object {
                $html += "<tr><td>$($_.FeatureName)</td><td>$($_.State)</td></tr>`n"
            }

            $html += @"
        </table>

        <h2>🎯 Installed Capabilities</h2>
        <table>
            <tr><th>Capability Name</th><th>State</th></tr>
"@
            $installedCapabilities | ForEach-Object {
                $html += "<tr><td>$($_.Name)</td><td>$($_.State)</td></tr>`n"
            }

            $html += @"
        </table>

        <div class="footer">
            Generated by DeployForge v0.3.0 | Windows Image Report
        </div>
    </div>
</body>
</html>
"@
            Set-Content -Path $OutputPath -Value $html -Encoding UTF8
        }

        'JSON' {
            $reportData | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8
        }

        'Text' {
            $text = @"
==========================================
Windows Image Report
==========================================

Generated: $($reportData.GeneratedDate)
Image Path: $ImagePath

IMAGE INFORMATION
-----------------
Name: $($imageInfo.Name)
Edition: $($imageInfo.EditionId)
Architecture: $($imageInfo.Architecture)
Version: $($imageInfo.Version)
Build: $($imageInfo.Build)
Size: $($imageInfo.Size) GB
Languages: $($imageInfo.Languages -join ', ')

SUMMARY STATISTICS
------------------
Provisioned Packages: $($packages.Count)
Drivers: $($drivers.Count)
Enabled Features: $($enabledFeatures.Count) / $($features.Count)
Installed Capabilities: $($installedCapabilities.Count) / $($capabilities.Count)
Files: $fileCount
Folders: $folderCount

PROVISIONED PACKAGES (Top 20)
------------------------------
"@
            $packages | Select-Object -First 20 | ForEach-Object {
                $text += "$($_.DisplayName) - v$($_.Version) ($($_.Architecture))`n"
            }

            $text += "`nINSTALLED DRIVERS (Top 20)`n"
            $text += "----------------------------`n"
            $drivers | Select-Object -First 20 | ForEach-Object {
                $text += "$($_.ClassName): $($_.ProviderName) v$($_.Version)`n"
            }

            $text += "`nENABLED WINDOWS FEATURES (Top 20)`n"
            $text += "-----------------------------------`n"
            $enabledFeatures | Select-Object -First 20 | ForEach-Object {
                $text += "$($_.FeatureName)`n"
            }

            $text += "`nINSTALLED CAPABILITIES`n"
            $text += "----------------------`n"
            $installedCapabilities | ForEach-Object {
                $text += "$($_.Name)`n"
            }

            $text += "`n==========================================`n"
            $text += "Generated by DeployForge v0.3.0`n"

            Set-Content -Path $OutputPath -Value $text -Encoding UTF8
        }
    }

    Write-Host "✓ Report generated successfully!`n" -ForegroundColor Green
    Write-Host "Report saved to: $OutputPath" -ForegroundColor Green
    Write-Host ""

    # Display summary
    Write-Host "=== Report Summary ===" -ForegroundColor Cyan
    Write-Host "Image: $($imageInfo.Name) ($($imageInfo.EditionId))" -ForegroundColor Gray
    Write-Host "Packages: $($packages.Count)" -ForegroundColor Gray
    Write-Host "Drivers: $($drivers.Count)" -ForegroundColor Gray
    Write-Host "Features: $($enabledFeatures.Count) enabled" -ForegroundColor Gray
    Write-Host "Capabilities: $($installedCapabilities.Count) installed" -ForegroundColor Gray
    Write-Host "Files: $fileCount" -ForegroundColor Gray
    Write-Host ""

    # Open report if HTML
    if ($Format -eq 'HTML') {
        $openReport = Read-Host "Open report in browser? (Y/N)"
        if ($openReport -eq 'Y' -or $openReport -eq 'y') {
            Start-Process $OutputPath
        }
    }
}
catch {
    Write-Error "Report generation failed: $_"

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
