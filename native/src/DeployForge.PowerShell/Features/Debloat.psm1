#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Debloat Module
    
.DESCRIPTION
    Removes bloatware applications and applies privacy/performance tweaks
    to Windows deployment images. Preserves Xbox and OneDrive by default.
#>

# Bloatware apps by level
$script:BloatwareApps = @{
    'Minimal' = @(
        'Microsoft.BingNews',
        'Microsoft.GetHelp',
        'Microsoft.Getstarted',
        'Microsoft.MicrosoftOfficeHub',
        'Microsoft.MicrosoftSolitaireCollection',
        'Microsoft.People',
        'Microsoft.WindowsFeedbackHub',
        'Microsoft.YourPhone',
        'Microsoft.549981C3F5F10',  # Cortana
        'MicrosoftCorporationII.QuickAssist',
        'Clipchamp.Clipchamp',
        'Microsoft.Todos',
        'Microsoft.PowerAutomateDesktop'
    )
    'Moderate' = @(
        'Microsoft.BingWeather',
        'Microsoft.WindowsMaps',
        'Microsoft.ZuneMusic',
        'Microsoft.ZuneVideo',
        'Microsoft.WindowsSoundRecorder',
        'Microsoft.MixedReality.Portal',
        'Microsoft.SkypeApp',
        'Microsoft.Messaging',
        'Microsoft.Print3D',
        'Microsoft.3DBuilder',
        'Microsoft.Microsoft3DViewer',
        'Microsoft.OneConnect',
        'Microsoft.Wallet',
        'Microsoft.MicrosoftStickyNotes',
        'Microsoft.Office.OneNote'
    )
    'Aggressive' = @(
        'Microsoft.WindowsCamera',
        'Microsoft.ScreenSketch',
        'Microsoft.WindowsAlarms',
        'Microsoft.WindowsCalculator',
        'Microsoft.Paint',
        'Microsoft.MSPaint',
        'Microsoft.Windows.Photos',
        'microsoft.windowscommunicationsapps',  # Mail/Calendar
        'Microsoft.WindowsStore',
        'Microsoft.StorePurchaseApp'
    )
}

# Apps to preserve (never remove)
$script:PreserveApps = @(
    'Microsoft.Xbox*',
    'Microsoft.OneDrive*',
    'Microsoft.WindowsTerminal',
    'Microsoft.WindowsNotepad',
    'Microsoft.DesktopAppInstaller',
    'Microsoft.VCLibs*',
    'Microsoft.NET*',
    'Microsoft.UI.Xaml*'
)

function Remove-Bloatware {
    <#
    .SYNOPSIS
        Removes bloatware applications from a mounted Windows image.
        
    .DESCRIPTION
        Removes pre-installed applications based on the selected level.
        Xbox and OneDrive are preserved by default.
        
    .PARAMETER MountPath
        Path where the Windows image is mounted.
        
    .PARAMETER Level
        Debloat level (Minimal, Moderate, Aggressive).
        
    .PARAMETER CustomApps
        Additional apps to remove (package names).
        
    .PARAMETER PreserveApps
        Additional apps to preserve.
        
    .EXAMPLE
        Remove-Bloatware -MountPath "D:\Mount" -Level Moderate
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$MountPath,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Minimal', 'Moderate', 'Aggressive')]
        [string]$Level = 'Moderate',
        
        [Parameter(Mandatory = $false)]
        [string[]]$CustomApps,
        
        [Parameter(Mandatory = $false)]
        [string[]]$PreserveApps
    )
    
    begin {
        Write-Host "Removing bloatware (Level: $Level)" -ForegroundColor Cyan
        $removedApps = @()
        $failedApps = @()
    }
    
    process {
        # Build list of apps to remove based on level
        $appsToRemove = @()
        $appsToRemove += $script:BloatwareApps['Minimal']
        
        if ($Level -in @('Moderate', 'Aggressive')) {
            $appsToRemove += $script:BloatwareApps['Moderate']
        }
        
        if ($Level -eq 'Aggressive') {
            $appsToRemove += $script:BloatwareApps['Aggressive']
        }
        
        # Add custom apps
        if ($CustomApps) {
            $appsToRemove += $CustomApps
        }
        
        # Build preserve list
        $preserveList = $script:PreserveApps
        if ($PreserveApps) {
            $preserveList += $PreserveApps
        }
        
        # Get provisioned packages
        $provisioned = Get-AppxProvisionedPackage -Path $MountPath -ErrorAction SilentlyContinue
        
        foreach ($app in $appsToRemove) {
            # Check if app should be preserved
            $shouldPreserve = $false
            foreach ($preserve in $preserveList) {
                if ($app -like $preserve) {
                    $shouldPreserve = $true
                    break
                }
            }
            
            if ($shouldPreserve) {
                Write-Verbose "Preserving: $app"
                continue
            }
            
            # Find matching packages
            $matchingPackages = $provisioned | Where-Object { $_.PackageName -like "*$app*" }
            
            foreach ($package in $matchingPackages) {
                try {
                    Write-Host "  Removing: $($package.DisplayName)" -ForegroundColor Gray
                    Remove-AppxProvisionedPackage -Path $MountPath -PackageName $package.PackageName -ErrorAction Stop | Out-Null
                    $removedApps += $package.DisplayName
                }
                catch {
                    Write-Verbose "Failed to remove $($package.PackageName): $_"
                    $failedApps += $package.DisplayName
                }
            }
        }
        
        Write-Host "✓ Bloatware removal complete" -ForegroundColor Green
        Write-Host "  Removed: $($removedApps.Count) apps" -ForegroundColor Gray
        if ($failedApps.Count -gt 0) {
            Write-Host "  Failed: $($failedApps.Count) apps" -ForegroundColor Yellow
        }
        
        return [PSCustomObject]@{
            Success = $true
            Level = $Level
            RemovedApps = $removedApps
            FailedApps = $failedApps
            TotalRemoved = $removedApps.Count
        }
    }
}

function Get-BloatwareList {
    <#
    .SYNOPSIS
        Returns the list of bloatware apps by level.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [ValidateSet('Minimal', 'Moderate', 'Aggressive', 'All')]
        [string]$Level = 'All'
    )
    
    if ($Level -eq 'All') {
        return $script:BloatwareApps
    }
    
    return $script:BloatwareApps[$Level]
}

function Disable-Telemetry {
    <#
    .SYNOPSIS
        Disables Windows telemetry and diagnostic data collection.
        
    .PARAMETER MountPath
        Path where the image is mounted.
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $changes = @()
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        Write-Host "Disabling telemetry..." -ForegroundColor Cyan
        
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        
        # Disable telemetry
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\DataCollection" /v MaxTelemetryAllowed /t REG_DWORD /d 0 /f 2>&1
        $changes += "Telemetry: Disabled"
        
        # Disable diagnostic data
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack" /v ShowedToastAtLevel /t REG_DWORD /d 1 /f 2>&1
        $changes += "Diagnostic Data: Disabled"
        
        # Disable tailored experiences
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\Privacy" /v TailoredExperiencesWithDiagnosticDataEnabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "Tailored Experiences: Disabled"
        
        # Disable feedback
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\DataCollection" /v DoNotShowFeedbackNotifications /t REG_DWORD /d 1 /f 2>&1
        $changes += "Feedback Notifications: Disabled"
        
        # Disable CEIP
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\SQMClient\Windows" /v CEIPEnable /t REG_DWORD /d 0 /f 2>&1
        $changes += "Customer Experience Improvement: Disabled"
        
        Write-Host "✓ Telemetry disabled" -ForegroundColor Green
        
        return [PSCustomObject]@{
            Success = $true
            Changes = $changes
        }
    }
    catch {
        Write-Error "Failed to disable telemetry: $_"
        return [PSCustomObject]@{
            Success = $false
            Error = $_.Exception.Message
        }
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

function Set-PrivacySettings {
    <#
    .SYNOPSIS
        Applies privacy-focused registry settings to a mounted image.
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $changes = @()
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        Write-Host "Applying privacy settings..." -ForegroundColor Cyan
        
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        
        # Disable advertising ID
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "Advertising ID: Disabled"
        
        # Disable app suggestions
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-338389Enabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-353694Enabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-353696Enabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "App Suggestions: Disabled"
        
        # Disable lock screen tips
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenOverlayEnabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v RotatingLockScreenEnabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "Lock Screen Tips: Disabled"
        
        # Disable Windows tips
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SoftLandingEnabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "Windows Tips: Disabled"
        
        # Disable pre-installed apps
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v PreInstalledAppsEnabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v OemPreInstalledAppsEnabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SilentInstalledAppsEnabled /t REG_DWORD /d 0 /f 2>&1
        $changes += "Pre-installed Apps Auto-Install: Disabled"
        
        Write-Host "✓ Privacy settings applied" -ForegroundColor Green
        
        return [PSCustomObject]@{
            Success = $true
            Changes = $changes
        }
    }
    catch {
        Write-Error "Failed to apply privacy settings: $_"
        return [PSCustomObject]@{
            Success = $false
            Error = $_.Exception.Message
        }
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

function Disable-Cortana {
    <#
    .SYNOPSIS
        Disables Cortana in a mounted Windows image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        Write-Host "Disabling Cortana..." -ForegroundColor Cyan
        
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\Windows Search" /v AllowCortanaAboveLock /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\Windows Search" /v DisableWebSearch /t REG_DWORD /d 1 /f 2>&1
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\Windows Search" /v ConnectedSearchUseWeb /t REG_DWORD /d 0 /f 2>&1
        
        Write-Host "✓ Cortana disabled" -ForegroundColor Green
        return $true
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

function Disable-DeliveryOptimization {
    <#
    .SYNOPSIS
        Disables Windows Update delivery optimization (P2P updates).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        Write-Host "Disabling Delivery Optimization..." -ForegroundColor Cyan
        
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        
        # Disable P2P updates
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\DeliveryOptimization" /v DODownloadMode /t REG_DWORD /d 0 /f 2>&1
        
        Write-Host "✓ Delivery Optimization disabled" -ForegroundColor Green
        return $true
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

# Export functions
Export-ModuleMember -Function @(
    'Remove-Bloatware',
    'Get-BloatwareList',
    'Disable-Telemetry',
    'Set-PrivacySettings',
    'Disable-Cortana',
    'Disable-DeliveryOptimization'
)
