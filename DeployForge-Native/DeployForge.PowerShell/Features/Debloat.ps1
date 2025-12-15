#Requires -Version 5.1

<#
.SYNOPSIS
    Debloating module for DeployForge.

.DESCRIPTION
    Removes bloatware and applies privacy tweaks to Windows images.
    Xbox and OneDrive are preserved by default.
#>

# Debloat level enumeration
enum DFDebloatLevel {
    Minimal     # Remove only obvious bloat
    Moderate    # Remove most unnecessary apps
    Aggressive  # Remove everything non-essential
}

# Bloatware app lists
$script:BloatwareApps = @{
    Minimal = @(
        "Microsoft.BingNews",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
        "Microsoft.MicrosoftOfficeHub",
        "Microsoft.MicrosoftSolitaireCollection",
        "Microsoft.People",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.YourPhone",
        "Microsoft.549981C3F5F10",  # Cortana
        "MicrosoftCorporationII.QuickAssist"
    )
    Moderate = @(
        "Microsoft.BingWeather",
        "Microsoft.WindowsMaps",
        "Microsoft.ZuneMusic",
        "Microsoft.ZuneVideo",
        "Microsoft.WindowsSoundRecorder",
        "Microsoft.MixedReality.Portal",
        "Microsoft.SkypeApp",
        "Microsoft.Messaging",
        "Microsoft.Print3D",
        "Microsoft.3DBuilder"
    )
    Aggressive = @(
        "Microsoft.WindowsCamera",
        "Microsoft.ScreenSketch",
        "Microsoft.WindowsAlarms",
        "Microsoft.WindowsCalculator",
        "Microsoft.Paint",
        "Microsoft.MSPaint"
    )
}

function Remove-DFBloatware {
    <#
    .SYNOPSIS
        Removes bloatware applications from a mounted Windows image.

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER Level
        Debloating level (Minimal, Moderate, Aggressive).

    .PARAMETER CustomApps
        Additional apps to remove.

    .PARAMETER PreserveApps
        Apps to preserve (not remove).

    .EXAMPLE
        Remove-DFBloatware -MountPoint "C:\Mount" -Level Moderate

    .EXAMPLE
        Remove-DFBloatware -MountPoint "C:\Mount" -Level Minimal -CustomApps @("ClipChamp.Clipchamp")
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Container })]
        [string]$MountPoint,

        [DFDebloatLevel]$Level = [DFDebloatLevel]::Moderate,

        [string[]]$CustomApps = @(),

        [string[]]$PreserveApps = @("Microsoft.Xbox*", "Microsoft.OneDrive*")
    )

    Write-DFLog -Message "Removing bloatware: $($Level.ToString()) level" -Level Info

    # Build list of apps to remove
    $appsToRemove = @()
    $appsToRemove += $script:BloatwareApps.Minimal

    if ($Level -in @([DFDebloatLevel]::Moderate, [DFDebloatLevel]::Aggressive)) {
        $appsToRemove += $script:BloatwareApps.Moderate
    }

    if ($Level -eq [DFDebloatLevel]::Aggressive) {
        $appsToRemove += $script:BloatwareApps.Aggressive
    }

    # Add custom apps
    $appsToRemove += $CustomApps

    # Filter out preserved apps
    $appsToRemove = $appsToRemove | Where-Object {
        $app = $_
        $preserve = $false
        foreach ($pattern in $PreserveApps) {
            if ($app -like $pattern) {
                $preserve = $true
                break
            }
        }
        -not $preserve
    }

    $removedCount = 0
    $failedCount = 0

    $tracker = New-DFProgressTracker -Activity "Removing Bloatware" -TotalSteps $appsToRemove.Count

    foreach ($app in $appsToRemove) {
        $step = $appsToRemove.IndexOf($app) + 1
        Update-DFProgress -Tracker $tracker -Status "Removing $app..." -Step $step

        try {
            $result = & dism.exe /Image:"$MountPoint" /Remove-ProvisionedAppxPackage /PackageName:$app 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $removedCount++
                Write-DFLog -Message "Removed: $app" -Level Verbose
            }
        }
        catch {
            $failedCount++
            Write-DFLog -Message "Could not remove $app" -Level Debug
        }
    }

    Complete-DFProgress -Tracker $tracker

    Write-DFLog -Message "Removed $removedCount bloatware apps (Failed: $failedCount)" -Level Info

    return [DFOperationResult]::Success("RemoveBloatware", "Removed $removedCount apps")
}

function Disable-DFTelemetry {
    <#
    .SYNOPSIS
        Disables Windows telemetry and diagnostic data collection.

    .PARAMETER MountPoint
        Path to the mounted image.

    .EXAMPLE
        Disable-DFTelemetry -MountPoint "C:\Mount"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Container })]
        [string]$MountPoint
    )

    Write-DFLog -Message "Disabling telemetry" -Level Info

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
    $hiveKey = "HKLM\TEMP_DF_SOFTWARE"

    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null

        # Disable telemetry
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f | Out-Null
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\DataCollection" /v MaxTelemetryAllowed /t REG_DWORD /d 0 /f | Out-Null
        
        # Disable diagnostic data
        & reg.exe add "$hiveKey\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack" /v ShowedToastAtLevel /t REG_DWORD /d 1 /f | Out-Null
        
        # Disable app diagnostics
        & reg.exe add "$hiveKey\Microsoft\Windows\CurrentVersion\Privacy" /v TailoredExperiencesWithDiagnosticDataEnabled /t REG_DWORD /d 0 /f | Out-Null

        # Disable Connected User Experiences
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\DataCollection" /v DoNotShowFeedbackNotifications /t REG_DWORD /d 1 /f | Out-Null

        Write-DFLog -Message "Telemetry disabled" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Set-DFPrivacyTweaks {
    <#
    .SYNOPSIS
        Applies privacy-focused registry tweaks.

    .PARAMETER MountPoint
        Path to the mounted image.

    .EXAMPLE
        Set-DFPrivacyTweaks -MountPoint "C:\Mount"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Container })]
        [string]$MountPoint
    )

    Write-DFLog -Message "Applying privacy tweaks" -Level Info

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
    $hiveKey = "HKLM\TEMP_DF_SOFTWARE"

    $privacyTweaks = @(
        # Disable advertising ID
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\AdvertisingInfo"; Name = "Enabled"; Value = 0 },
        
        # Disable Windows tips
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SubscribedContent-338389Enabled"; Value = 0 },
        
        # Disable suggested content
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SubscribedContent-353694Enabled"; Value = 0 },
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SubscribedContent-353696Enabled"; Value = 0 },
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SubscribedContent-353698Enabled"; Value = 0 },
        
        # Disable lock screen tips
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "RotatingLockScreenOverlayEnabled"; Value = 0 },
        
        # Disable suggested apps in Start
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SystemPaneSuggestionsEnabled"; Value = 0 },
        
        # Disable Windows Spotlight
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "RotatingLockScreenEnabled"; Value = 0 },
        
        # Disable pre-installed apps
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "PreInstalledAppsEnabled"; Value = 0 },
        @{ Key = "$hiveKey\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"; Name = "SilentInstalledAppsEnabled"; Value = 0 }
    )

    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null

        foreach ($tweak in $privacyTweaks) {
            & reg.exe add $tweak.Key /v $tweak.Name /t REG_DWORD /d $tweak.Value /f 2>&1 | Out-Null
        }

        Write-DFLog -Message "Applied $($privacyTweaks.Count) privacy tweaks" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Disable-DFCortana {
    <#
    .SYNOPSIS
        Disables Cortana.

    .PARAMETER MountPoint
        Path to the mounted image.

    .EXAMPLE
        Disable-DFCortana -MountPoint "C:\Mount"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Container })]
        [string]$MountPoint
    )

    Write-DFLog -Message "Disabling Cortana" -Level Info

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
    $hiveKey = "HKLM\TEMP_DF_SOFTWARE"

    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null

        # Disable Cortana
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f | Out-Null
        
        # Disable web search in Start menu
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\Windows Search" /v DisableWebSearch /t REG_DWORD /d 1 /f | Out-Null
        & reg.exe add "$hiveKey\Policies\Microsoft\Windows\Windows Search" /v ConnectedSearchUseWeb /t REG_DWORD /d 0 /f | Out-Null

        Write-DFLog -Message "Cortana disabled" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Start-DFDebloat {
    <#
    .SYNOPSIS
        Comprehensive debloating function.

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER Level
        Debloating level.

    .PARAMETER DisableTelemetry
        Disable telemetry.

    .PARAMETER DisableCortana
        Disable Cortana.

    .PARAMETER ApplyPrivacyTweaks
        Apply privacy tweaks.

    .EXAMPLE
        Start-DFDebloat -MountPoint "C:\Mount" -Level Moderate -DisableTelemetry -DisableCortana
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint,

        [DFDebloatLevel]$Level = [DFDebloatLevel]::Moderate,

        [switch]$DisableTelemetry,

        [switch]$DisableCortana,

        [switch]$ApplyPrivacyTweaks
    )

    Write-DFLog -Message "Starting comprehensive debloat" -Level Info

    $results = @()

    # Remove bloatware
    $results += Remove-DFBloatware -MountPoint $MountPoint -Level $Level

    # Apply privacy tweaks
    if ($ApplyPrivacyTweaks) {
        Set-DFPrivacyTweaks -MountPoint $MountPoint
    }

    # Disable telemetry
    if ($DisableTelemetry) {
        Disable-DFTelemetry -MountPoint $MountPoint
    }

    # Disable Cortana
    if ($DisableCortana) {
        Disable-DFCortana -MountPoint $MountPoint
    }

    Write-DFLog -Message "Debloating complete" -Level Info

    return [DFOperationResult]::Success("Debloat", "Debloating completed successfully")
}

Write-Verbose "Loaded DeployForge Debloat module"
