#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Gaming Optimization Module
    
.DESCRIPTION
    Provides comprehensive gaming optimization features for Windows deployment images.
    Includes Game Mode, network latency optimization, service optimization, and runtime installation.
#>

# Gaming profiles configuration
$script:GamingProfiles = @{
    'Competitive' = @{
        EnableGameMode = $true
        DisableFullscreenOptimizations = $true
        OptimizeNetworkLatency = $true
        DisableGameBar = $true
        EnableHardwareAcceleration = $true
        DisableBackgroundRecording = $true
        OptimizeMousePolling = $true
        DisableNagleAlgorithm = $true
        PriorityBoost = 'High'
    }
    'Balanced' = @{
        EnableGameMode = $true
        DisableFullscreenOptimizations = $false
        OptimizeNetworkLatency = $true
        DisableGameBar = $false
        EnableHardwareAcceleration = $true
        DisableBackgroundRecording = $true
        OptimizeMousePolling = $false
        DisableNagleAlgorithm = $false
        PriorityBoost = 'Normal'
    }
    'Quality' = @{
        EnableGameMode = $true
        DisableFullscreenOptimizations = $false
        OptimizeNetworkLatency = $false
        DisableGameBar = $false
        EnableHardwareAcceleration = $true
        DisableBackgroundRecording = $false
        OptimizeMousePolling = $false
        DisableNagleAlgorithm = $false
        PriorityBoost = 'Normal'
    }
    'Streaming' = @{
        EnableGameMode = $true
        DisableFullscreenOptimizations = $false
        OptimizeNetworkLatency = $true
        DisableGameBar = $false
        EnableHardwareAcceleration = $true
        DisableBackgroundRecording = $false
        OptimizeMousePolling = $false
        DisableNagleAlgorithm = $true
        PriorityBoost = 'High'
    }
}

# Services to disable for gaming
$script:GamingServicesToDisable = @(
    'DiagTrack',           # Connected User Experiences and Telemetry
    'SysMain',             # Superfetch
    'WSearch',             # Windows Search
    'TabletInputService',  # Touch Keyboard
    'WMPNetworkSvc'        # Windows Media Player Network Sharing
)

function Set-GamingProfile {
    <#
    .SYNOPSIS
        Applies a gaming optimization profile to a mounted Windows image.
        
    .DESCRIPTION
        Configures the Windows image with gaming-optimized settings based on the selected profile.
        
    .PARAMETER MountPath
        Path where the Windows image is mounted.
        
    .PARAMETER Profile
        Gaming profile to apply (Competitive, Balanced, Quality, Streaming).
        
    .PARAMETER OptimizeServices
        Also optimize Windows services for gaming.
        
    .EXAMPLE
        Set-GamingProfile -MountPath "D:\Mount" -Profile Competitive
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$MountPath,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('Competitive', 'Balanced', 'Quality', 'Streaming')]
        [string]$Profile = 'Competitive',
        
        [Parameter(Mandatory = $false)]
        [switch]$OptimizeServices
    )
    
    begin {
        Write-Host "Applying gaming profile: $Profile" -ForegroundColor Cyan
        $config = $script:GamingProfiles[$Profile]
        $changes = @()
    }
    
    process {
        try {
            # Load SOFTWARE hive
            $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
            $softwareKey = "HKLM\DEPLOYFORGE_SOFTWARE_$(Get-Random -Maximum 9999)"
            
            $null = & reg.exe load $softwareKey $softwareHive 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to load SOFTWARE hive"
            }
            
            try {
                # Game Mode
                if ($config.EnableGameMode) {
                    $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f 2>&1
                    $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f 2>&1
                    $changes += "Game Mode: Enabled"
                }
                
                # Game Bar
                if ($config.DisableGameBar) {
                    $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v UseNexusForGameBarEnabled /t REG_DWORD /d 0 /f 2>&1
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f 2>&1
                    $changes += "Game Bar: Disabled"
                }
                
                # Background Recording
                if ($config.DisableBackgroundRecording) {
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f 2>&1
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameDVR" /v HistoricalCaptureEnabled /t REG_DWORD /d 0 /f 2>&1
                    $changes += "Background Recording: Disabled"
                }
                
                # Hardware Accelerated GPU Scheduling
                if ($config.EnableHardwareAcceleration) {
                    $null = & reg.exe add "$softwareKey\Microsoft\DirectX\GraphicsSettings" /v HwSchMode /t REG_DWORD /d 2 /f 2>&1
                    $changes += "Hardware Acceleration: Enabled"
                }
                
                # Fullscreen Optimizations
                if ($config.DisableFullscreenOptimizations) {
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameConfigStore" /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 2 /f 2>&1
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameConfigStore" /v GameDVR_HonorUserFSEBehaviorMode /t REG_DWORD /d 1 /f 2>&1
                    $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameConfigStore" /v GameDVR_FSEBehavior /t REG_DWORD /d 2 /f 2>&1
                    $changes += "Fullscreen Optimizations: Disabled"
                }
                
                # GPU Priority for Games
                $null = & reg.exe add "$softwareKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f 2>&1
                $null = & reg.exe add "$softwareKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f 2>&1
                $null = & reg.exe add "$softwareKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f 2>&1
                $null = & reg.exe add "$softwareKey\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f 2>&1
                $changes += "GPU Priority: Configured for games"
                
            }
            finally {
                # Unload SOFTWARE hive
                [GC]::Collect()
                [GC]::WaitForPendingFinalizers()
                Start-Sleep -Milliseconds 500
                $null = & reg.exe unload $softwareKey 2>&1
            }
            
            # Network optimizations if requested
            if ($config.OptimizeNetworkLatency) {
                $networkChanges = Optimize-NetworkLatency -MountPath $MountPath
                $changes += $networkChanges
            }
            
            # Service optimizations
            if ($OptimizeServices) {
                $serviceChanges = Optimize-GamingServices -MountPath $MountPath
                $changes += $serviceChanges
            }
            
            Write-Host "✓ Gaming profile applied successfully" -ForegroundColor Green
            foreach ($change in $changes) {
                Write-Host "  • $change" -ForegroundColor Gray
            }
            
            return [PSCustomObject]@{
                Success = $true
                Profile = $Profile
                Changes = $changes
                MountPath = $MountPath
            }
        }
        catch {
            Write-Error "Failed to apply gaming profile: $_"
            return [PSCustomObject]@{
                Success = $false
                Profile = $Profile
                Error = $_.Exception.Message
            }
        }
    }
}

function Enable-GameMode {
    <#
    .SYNOPSIS
        Enables Windows Game Mode in a mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f 2>&1
        Write-Host "✓ Game Mode enabled" -ForegroundColor Green
        return $true
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

function Disable-GameBar {
    <#
    .SYNOPSIS
        Disables Windows Game Bar and DVR in a mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $softwareHive = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $softwareKey = "HKLM\TEMP_SOFTWARE_$(Get-Random)"
    
    try {
        $null = & reg.exe load $softwareKey $softwareHive 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\GameBar" /v UseNexusForGameBarEnabled /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Policies\Microsoft\Windows\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f 2>&1
        $null = & reg.exe add "$softwareKey\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f 2>&1
        Write-Host "✓ Game Bar and DVR disabled" -ForegroundColor Green
        return $true
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $softwareKey 2>&1
    }
}

function Optimize-NetworkLatency {
    <#
    .SYNOPSIS
        Applies network latency optimizations for gaming.
    #>
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $changes = @()
    $systemHive = Join-Path $MountPath "Windows\System32\config\SYSTEM"
    $systemKey = "HKLM\TEMP_SYSTEM_$(Get-Random)"
    
    try {
        $null = & reg.exe load $systemKey $systemHive 2>&1
        
        # Disable Nagle's Algorithm
        $null = & reg.exe add "$systemKey\ControlSet001\Services\Tcpip\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f 2>&1
        $null = & reg.exe add "$systemKey\ControlSet001\Services\Tcpip\Parameters" /v TCPNoDelay /t REG_DWORD /d 1 /f 2>&1
        $changes += "Nagle's Algorithm: Disabled"
        
        # Optimize TCP acknowledgment
        $null = & reg.exe add "$systemKey\ControlSet001\Services\Tcpip\Parameters" /v TcpDelAckTicks /t REG_DWORD /d 0 /f 2>&1
        $changes += "TCP Acknowledgment: Optimized"
        
        # Disable network throttling
        $null = & reg.exe add "$systemKey\ControlSet001\Services\LanmanWorkstation\Parameters" /v DisableBandwidthThrottling /t REG_DWORD /d 1 /f 2>&1
        $null = & reg.exe add "$systemKey\ControlSet001\Services\LanmanWorkstation\Parameters" /v DisableLargeMtu /t REG_DWORD /d 0 /f 2>&1
        $changes += "Network Throttling: Disabled"
        
        Write-Host "✓ Network latency optimizations applied" -ForegroundColor Green
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $systemKey 2>&1
    }
    
    return $changes
}

function Install-GamingRuntimes {
    <#
    .SYNOPSIS
        Configures gaming runtime installation scripts for first boot.
        
    .DESCRIPTION
        Creates PowerShell scripts to install DirectX, Visual C++ Redistributables,
        and other gaming runtimes on first boot.
        
    .PARAMETER MountPath
        Path where the image is mounted.
        
    .PARAMETER RuntimesPath
        Optional path to pre-downloaded runtimes.
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath,
        
        [Parameter(Mandatory = $false)]
        [string]$RuntimesPath
    )
    
    $scriptsDir = Join-Path $MountPath "Windows\Setup\Scripts"
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }
    
    $scriptContent = @'
# Gaming Runtimes Installation Script
# Generated by DeployForge

Write-Host "Installing gaming runtimes..." -ForegroundColor Cyan

# Install Visual C++ Redistributables via WinGet
$vcRedists = @(
    'Microsoft.VCRedist.2015+.x64',
    'Microsoft.VCRedist.2015+.x86',
    'Microsoft.VCRedist.2013.x64',
    'Microsoft.VCRedist.2013.x86',
    'Microsoft.VCRedist.2012.x64',
    'Microsoft.VCRedist.2012.x86',
    'Microsoft.VCRedist.2010.x64',
    'Microsoft.VCRedist.2010.x86'
)

foreach ($redist in $vcRedists) {
    Write-Host "Installing $redist..."
    winget install --id $redist --silent --accept-package-agreements --accept-source-agreements 2>$null
}

# Install DirectX
Write-Host "Installing DirectX..."
winget install --id Microsoft.DirectX --silent --accept-package-agreements --accept-source-agreements 2>$null

# Install .NET Framework 3.5 if not present
$net35 = Get-WindowsOptionalFeature -Online -FeatureName NetFx3 -ErrorAction SilentlyContinue
if ($net35.State -ne 'Enabled') {
    Write-Host "Enabling .NET Framework 3.5..."
    Enable-WindowsOptionalFeature -Online -FeatureName NetFx3 -All -NoRestart
}

Write-Host "Gaming runtimes installation complete!" -ForegroundColor Green
'@

    $scriptPath = Join-Path $scriptsDir "install_gaming_runtimes.ps1"
    $scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8 -Force
    
    # Add to SetupComplete.cmd
    $setupComplete = Join-Path $scriptsDir "SetupComplete.cmd"
    $setupLine = 'powershell.exe -ExecutionPolicy Bypass -File "%~dp0install_gaming_runtimes.ps1"'
    
    if (Test-Path $setupComplete) {
        $content = Get-Content $setupComplete -Raw
        if ($content -notlike "*install_gaming_runtimes*") {
            Add-Content -Path $setupComplete -Value $setupLine
        }
    }
    else {
        "@echo off`r`n$setupLine" | Out-File -FilePath $setupComplete -Encoding ASCII -Force
    }
    
    Write-Host "✓ Gaming runtimes installation configured" -ForegroundColor Green
    
    return [PSCustomObject]@{
        Success = $true
        ScriptPath = $scriptPath
        RuntimesConfigured = @('Visual C++ 2010-2022', 'DirectX', '.NET Framework 3.5')
    }
}

function Optimize-GamingServices {
    <#
    .SYNOPSIS
        Optimizes Windows services for gaming performance.
    #>
    [CmdletBinding()]
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPath
    )
    
    $changes = @()
    $systemHive = Join-Path $MountPath "Windows\System32\config\SYSTEM"
    $systemKey = "HKLM\TEMP_SYSTEM_$(Get-Random)"
    
    try {
        $null = & reg.exe load $systemKey $systemHive 2>&1
        
        foreach ($service in $script:GamingServicesToDisable) {
            $servicePath = "$systemKey\ControlSet001\Services\$service"
            $null = & reg.exe add $servicePath /v Start /t REG_DWORD /d 4 /f 2>&1
            $changes += "Service disabled: $service"
        }
        
        Write-Host "✓ Gaming services optimized ($($changes.Count) services adjusted)" -ForegroundColor Green
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 300
        $null = & reg.exe unload $systemKey 2>&1
    }
    
    return $changes
}

# Export functions
Export-ModuleMember -Function @(
    'Set-GamingProfile',
    'Enable-GameMode',
    'Disable-GameBar',
    'Optimize-NetworkLatency',
    'Install-GamingRuntimes',
    'Optimize-GamingServices'
)
