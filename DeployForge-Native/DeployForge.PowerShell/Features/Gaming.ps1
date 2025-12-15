#Requires -Version 5.1

<#
.SYNOPSIS
    Gaming optimization module for DeployForge.

.DESCRIPTION
    Optimizes Windows images for gaming performance with registry tweaks,
    service optimization, network tuning, and runtime installation.
#>

# Gaming profile enumeration
enum DFGamingProfile {
    Competitive  # Maximum performance, minimal latency
    Balanced     # Good performance with some quality
    Quality      # Best visual quality
    Streaming    # Optimized for game streaming
}

# Gaming optimization configuration
class DFGamingConfig {
    [bool]$EnableGameMode = $true
    [bool]$DisableFullscreenOptimizations = $false
    [bool]$OptimizeNetworkLatency = $true
    [bool]$DisableGameBar = $false
    [bool]$EnableHardwareAcceleration = $true
    [bool]$DisableBackgroundRecording = $true
    [bool]$OptimizeMousePolling = $true
    [bool]$DisableNagleAlgorithm = $true
    [string]$PriorityBoost = "high"  # low, normal, high, realtime

    [hashtable] ToHashtable() {
        return @{
            EnableGameMode = $this.EnableGameMode
            DisableFullscreenOptimizations = $this.DisableFullscreenOptimizations
            OptimizeNetworkLatency = $this.OptimizeNetworkLatency
            DisableGameBar = $this.DisableGameBar
            EnableHardwareAcceleration = $this.EnableHardwareAcceleration
            DisableBackgroundRecording = $this.DisableBackgroundRecording
            OptimizeMousePolling = $this.OptimizeMousePolling
            DisableNagleAlgorithm = $this.DisableNagleAlgorithm
            PriorityBoost = $this.PriorityBoost
        }
    }

    static [DFGamingConfig] FromProfile([DFGamingProfile]$profile) {
        $config = [DFGamingConfig]::new()

        switch ($profile) {
            'Competitive' {
                $config.EnableGameMode = $true
                $config.DisableFullscreenOptimizations = $true
                $config.OptimizeNetworkLatency = $true
                $config.DisableGameBar = $true
                $config.EnableHardwareAcceleration = $true
                $config.DisableBackgroundRecording = $true
                $config.OptimizeMousePolling = $true
                $config.DisableNagleAlgorithm = $true
                $config.PriorityBoost = "high"
            }
            'Balanced' {
                $config.EnableGameMode = $true
                $config.OptimizeNetworkLatency = $true
                $config.DisableBackgroundRecording = $true
                $config.PriorityBoost = "normal"
            }
            'Quality' {
                $config.EnableGameMode = $true
                $config.EnableHardwareAcceleration = $true
                $config.PriorityBoost = "normal"
            }
            'Streaming' {
                $config.EnableGameMode = $true
                $config.EnableHardwareAcceleration = $true
                $config.DisableBackgroundRecording = $false
                $config.PriorityBoost = "high"
            }
        }

        return $config
    }
}

function Optimize-DFGaming {
    <#
    .SYNOPSIS
        Applies gaming optimizations to a mounted Windows image.

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER Profile
        Gaming profile (Competitive, Balanced, Quality, Streaming).

    .PARAMETER Config
        Custom gaming configuration object.

    .PARAMETER InstallRuntimes
        Install DirectX and Visual C++ runtimes.

    .EXAMPLE
        Optimize-DFGaming -MountPoint "C:\Mount" -Profile Competitive

    .EXAMPLE
        $config = [DFGamingConfig]::new()
        $config.DisableGameBar = $true
        Optimize-DFGaming -MountPoint "C:\Mount" -Config $config
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Container })]
        [string]$MountPoint,

        [Parameter(ParameterSetName = 'Profile')]
        [DFGamingProfile]$Profile = [DFGamingProfile]::Balanced,

        [Parameter(ParameterSetName = 'Custom')]
        [DFGamingConfig]$Config,

        [switch]$InstallRuntimes
    )

    Write-DFLog -Message "Applying gaming optimizations to $MountPoint" -Level Info

    # Get configuration
    $gamingConfig = if ($Config) {
        $Config
    }
    else {
        [DFGamingConfig]::FromProfile($Profile)
    }

    $tracker = New-DFProgressTracker -Activity "Gaming Optimization" -TotalSteps 5
    
    try {
        # Step 1: Apply registry optimizations
        Update-DFProgress -Tracker $tracker -Status "Applying registry optimizations..." -Step 1
        Set-DFGamingRegistry -MountPoint $MountPoint -Config $gamingConfig

        # Step 2: Optimize network settings
        Update-DFProgress -Tracker $tracker -Status "Optimizing network settings..." -Step 2
        if ($gamingConfig.OptimizeNetworkLatency) {
            Set-DFGamingNetwork -MountPoint $MountPoint
        }

        # Step 3: Optimize services
        Update-DFProgress -Tracker $tracker -Status "Optimizing services..." -Step 3
        Optimize-DFGamingServices -MountPoint $MountPoint

        # Step 4: Create runtime installation script
        Update-DFProgress -Tracker $tracker -Status "Configuring runtimes..." -Step 4
        if ($InstallRuntimes) {
            Install-DFGamingRuntimes -MountPoint $MountPoint
        }

        # Step 5: Complete
        Update-DFProgress -Tracker $tracker -Status "Finalizing..." -Step 5
        Complete-DFProgress -Tracker $tracker

        Write-DFLog -Message "Gaming optimization complete: $($Profile.ToString()) profile" -Level Info
        
        return [DFOperationResult]::Success("GamingOptimization", "Applied $($Profile.ToString()) profile successfully")
    }
    catch {
        Write-DFLog -Message "Gaming optimization failed: $($_.Exception.Message)" -Level Error -Exception $_.Exception
        throw
    }
}

function Set-DFGamingProfile {
    <#
    .SYNOPSIS
        Applies a predefined gaming profile.

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER Profile
        Gaming profile to apply.

    .EXAMPLE
        Set-DFGamingProfile -MountPoint "C:\Mount" -Profile Competitive
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint,

        [Parameter(Mandatory = $true)]
        [DFGamingProfile]$Profile
    )

    Optimize-DFGaming -MountPoint $MountPoint -Profile $Profile
}

function Set-DFGamingRegistry {
    <#
    .SYNOPSIS
        Applies gaming registry optimizations.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint,

        [Parameter(Mandatory = $true)]
        [DFGamingConfig]$Config
    )

    Write-DFLog -Message "Applying gaming registry tweaks" -Level Verbose

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
    $hiveKey = "HKLM\TEMP_DF_SOFTWARE"

    try {
        # Load hive
        $result = & reg.exe load $hiveKey $hivePath 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to load registry hive: $result"
        }

        # Enable Game Mode
        if ($Config.EnableGameMode) {
            & reg.exe add "$hiveKey\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f | Out-Null
            Write-DFLog -Message "Enabled Game Mode" -Level Verbose
        }

        # Disable Game Bar
        if ($Config.DisableGameBar) {
            & reg.exe add "$hiveKey\Microsoft\GameBar" /v UseNexusForGameBarEnabled /t REG_DWORD /d 0 /f | Out-Null
            & reg.exe add "$hiveKey\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f | Out-Null
            Write-DFLog -Message "Disabled Game Bar" -Level Verbose
        }

        # Disable background recording
        if ($Config.DisableBackgroundRecording) {
            & reg.exe add "$hiveKey\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f | Out-Null
            Write-DFLog -Message "Disabled background recording" -Level Verbose
        }

        # Hardware-accelerated GPU scheduling
        if ($Config.EnableHardwareAcceleration) {
            & reg.exe add "$hiveKey\Microsoft\DirectX\GraphicsSettings" /v HwSchMode /t REG_DWORD /d 2 /f | Out-Null
            Write-DFLog -Message "Enabled hardware-accelerated GPU scheduling" -Level Verbose
        }

        # GPU priority for games
        & reg.exe add "$hiveKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f | Out-Null
        & reg.exe add "$hiveKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f | Out-Null
        & reg.exe add "$hiveKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f | Out-Null
        & reg.exe add "$hiveKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f | Out-Null

        Write-DFLog -Message "Gaming registry tweaks applied" -Level Info
    }
    finally {
        # Unload hive
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Set-DFGamingNetwork {
    <#
    .SYNOPSIS
        Optimizes network settings for gaming.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint
    )

    Write-DFLog -Message "Applying network optimizations" -Level Verbose

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SYSTEM"
    $hiveKey = "HKLM\TEMP_DF_SYSTEM"

    try {
        # Load hive
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null

        # Disable Nagle's algorithm
        & reg.exe add "$hiveKey\ControlSet001\Services\Tcpip\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f | Out-Null
        & reg.exe add "$hiveKey\ControlSet001\Services\Tcpip\Parameters" /v TCPNoDelay /t REG_DWORD /d 1 /f | Out-Null
        & reg.exe add "$hiveKey\ControlSet001\Services\Tcpip\Parameters" /v TcpDelAckTicks /t REG_DWORD /d 0 /f | Out-Null

        # Optimize network throttling
        & reg.exe add "$hiveKey\ControlSet001\Services\LanmanWorkstation\Parameters" /v DisableBandwidthThrottling /t REG_DWORD /d 1 /f | Out-Null
        & reg.exe add "$hiveKey\ControlSet001\Services\LanmanWorkstation\Parameters" /v DisableLargeMtu /t REG_DWORD /d 0 /f | Out-Null

        Write-DFLog -Message "Network optimizations applied" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Optimize-DFGamingServices {
    <#
    .SYNOPSIS
        Optimizes Windows services for gaming.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint
    )

    Write-DFLog -Message "Optimizing services for gaming" -Level Verbose

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SYSTEM"
    $hiveKey = "HKLM\TEMP_DF_SYSTEM"

    # Services to disable for gaming
    $servicesToDisable = @(
        "DiagTrack",          # Connected User Experiences and Telemetry
        "SysMain",            # Superfetch (can cause stuttering)
        "WSearch",            # Windows Search (optional)
        "TabletInputService", # Touch Keyboard
        "WMPNetworkSvc"       # Windows Media Player Network Sharing
    )

    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null

        foreach ($service in $servicesToDisable) {
            $serviceKey = "$hiveKey\ControlSet001\Services\$service"
            & reg.exe add $serviceKey /v Start /t REG_DWORD /d 4 /f 2>&1 | Out-Null
            Write-DFLog -Message "Disabled service: $service" -Level Verbose
        }

        Write-DFLog -Message "Disabled $($servicesToDisable.Count) services" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Install-DFGamingRuntimes {
    <#
    .SYNOPSIS
        Creates script to install gaming runtimes (DirectX, VC++).

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER RuntimesPath
        Path to runtime installers.

    .EXAMPLE
        Install-DFGamingRuntimes -MountPoint "C:\Mount"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint,

        [string]$RuntimesPath
    )

    Write-DFLog -Message "Configuring gaming runtimes installation" -Level Info

    $scriptsDir = Join-Path $MountPoint "Windows\Setup\Scripts"
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }

    # Create runtime installation script
    $scriptContent = @'
# Gaming Runtimes Installation Script
# Generated by DeployForge

Write-Host "Installing gaming runtimes..." -ForegroundColor Cyan

# Install DirectX
if (Test-Path "C:\Runtimes\DirectX") {
    Write-Host "Installing DirectX..."
    Start-Process -FilePath "C:\Runtimes\DirectX\DXSETUP.exe" -ArgumentList "/silent" -Wait
}

# Install Visual C++ Redistributables using winget if available
$winget = Get-Command winget -ErrorAction SilentlyContinue
if ($winget) {
    Write-Host "Installing Visual C++ Redistributables via winget..."
    
    $vcRedists = @(
        "Microsoft.VCRedist.2015+.x64",
        "Microsoft.VCRedist.2015+.x86",
        "Microsoft.VCRedist.2013.x64",
        "Microsoft.VCRedist.2013.x86",
        "Microsoft.VCRedist.2012.x64",
        "Microsoft.VCRedist.2012.x86",
        "Microsoft.VCRedist.2010.x64",
        "Microsoft.VCRedist.2010.x86"
    )
    
    foreach ($redist in $vcRedists) {
        Write-Host "Installing $redist..."
        winget install --id $redist --silent --accept-package-agreements --accept-source-agreements 2>$null
    }
}
else {
    Write-Host "winget not available. Install Visual C++ redistributables manually."
}

# Install DirectX via winget
if ($winget) {
    Write-Host "Installing DirectX Runtime..."
    winget install Microsoft.DirectX --silent --accept-package-agreements --accept-source-agreements 2>$null
}

Write-Host "Gaming runtimes installation complete!" -ForegroundColor Green
'@

    $scriptPath = Join-Path $scriptsDir "Install-GamingRuntimes.ps1"
    Set-Content -Path $scriptPath -Value $scriptContent -Encoding UTF8

    # Add to SetupComplete.cmd
    $setupCompletePath = Join-Path $scriptsDir "SetupComplete.cmd"
    $setupCompleteContent = if (Test-Path $setupCompletePath) {
        Get-Content $setupCompletePath -Raw
    }
    else {
        "@echo off`r`n"
    }

    $setupCompleteContent += "`r`npowershell.exe -ExecutionPolicy Bypass -File `"%~dp0Install-GamingRuntimes.ps1`"`r`n"
    Set-Content -Path $setupCompletePath -Value $setupCompleteContent -Encoding ASCII

    Write-DFLog -Message "Gaming runtimes installation configured" -Level Info
}

Write-Verbose "Loaded DeployForge Gaming module"
