#Requires -Version 5.1

<#
.SYNOPSIS
    Privacy and security hardening module for DeployForge.

.DESCRIPTION
    Comprehensive privacy and security hardening for Windows deployment images.
#>

enum DFPrivacyLevel {
    Minimal    # Basic privacy without breaking features
    Moderate   # Good privacy balance
    Aggressive # Maximum privacy, some features disabled
    Paranoid   # Extreme privacy, many features disabled
}

$script:TelemetryDomains = @(
    "vortex.data.microsoft.com",
    "vortex-win.data.microsoft.com",
    "telecommand.telemetry.microsoft.com",
    "oca.telemetry.microsoft.com",
    "sqm.telemetry.microsoft.com",
    "watson.telemetry.microsoft.com",
    "statsfe2.ws.microsoft.com",
    "corpext.msitadfs.glbdns2.microsoft.com",
    "compatexchange.cloudapp.net",
    "cs1.wpc.v0cdn.net",
    "a-0001.a-msedge.net",
    "sls.update.microsoft.com.akadns.net"
)

function Set-DFPrivacyLevel {
    <#
    .SYNOPSIS
        Applies a predefined privacy level.

    .PARAMETER MountPoint
        Path to the mounted image.

    .PARAMETER Level
        Privacy level to apply.

    .EXAMPLE
        Set-DFPrivacyLevel -MountPoint "C:\Mount" -Level Aggressive
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint,

        [Parameter(Mandatory = $true)]
        [DFPrivacyLevel]$Level
    )

    Write-DFLog -Message "Applying privacy level: $($Level.ToString())" -Level Info

    switch ($Level) {
        'Minimal' {
            Disable-DFAdvertisingId -MountPoint $MountPoint
        }
        'Moderate' {
            Disable-DFAdvertisingId -MountPoint $MountPoint
            Disable-DFTelemetry -MountPoint $MountPoint
            Disable-DFCortana -MountPoint $MountPoint
        }
        'Aggressive' {
            Disable-DFAdvertisingId -MountPoint $MountPoint
            Disable-DFTelemetry -MountPoint $MountPoint
            Disable-DFCortana -MountPoint $MountPoint
            Set-DFPrivacyTweaks -MountPoint $MountPoint
            Block-DFTelemetryDomains -MountPoint $MountPoint
        }
        'Paranoid' {
            Disable-DFAdvertisingId -MountPoint $MountPoint
            Disable-DFTelemetry -MountPoint $MountPoint
            Disable-DFCortana -MountPoint $MountPoint
            Set-DFPrivacyTweaks -MountPoint $MountPoint
            Block-DFTelemetryDomains -MountPoint $MountPoint
            Set-DFPrivacyHardening -MountPoint $MountPoint
        }
    }

    Write-DFLog -Message "Privacy level $($Level.ToString()) applied" -Level Info
}

function Block-DFTelemetryDomains {
    <#
    .SYNOPSIS
        Blocks telemetry domains via hosts file.

    .PARAMETER MountPoint
        Path to the mounted image.

    .EXAMPLE
        Block-DFTelemetryDomains -MountPoint "C:\Mount"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint
    )

    Write-DFLog -Message "Blocking telemetry domains" -Level Info

    $hostsPath = Join-Path $MountPoint "Windows\System32\drivers\etc\hosts"

    $hostsContent = if (Test-Path $hostsPath) {
        Get-Content $hostsPath -Raw
    }
    else {
        ""
    }

    $hostsContent += "`n# DeployForge - Telemetry blocking`n"
    
    foreach ($domain in $script:TelemetryDomains) {
        $hostsContent += "0.0.0.0 $domain`n"
    }

    Set-Content -Path $hostsPath -Value $hostsContent -Encoding ASCII

    Write-DFLog -Message "Blocked $($script:TelemetryDomains.Count) telemetry domains" -Level Info
}

function Disable-DFAdvertisingId {
    <#
    .SYNOPSIS
        Disables the Windows advertising ID.

    .PARAMETER MountPoint
        Path to the mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint
    )

    Write-DFLog -Message "Disabling advertising ID" -Level Verbose

    $hivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
    $hiveKey = "HKLM\TEMP_DF_SOFTWARE"

    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null
        & reg.exe add "$hiveKey\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f | Out-Null
        Write-DFLog -Message "Advertising ID disabled" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Set-DFPrivacyHardening {
    <#
    .SYNOPSIS
        Applies extreme privacy hardening.

    .PARAMETER MountPoint
        Path to the mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$MountPoint
    )

    Write-DFLog -Message "Applying privacy hardening" -Level Info

    # Disable Windows Search indexing for privacy
    $systemHivePath = Join-Path $MountPoint "Windows\System32\config\SYSTEM"
    $systemHiveKey = "HKLM\TEMP_DF_SYSTEM"

    try {
        & reg.exe load $systemHiveKey $systemHivePath 2>&1 | Out-Null

        # Disable Windows Search
        & reg.exe add "$systemHiveKey\ControlSet001\Services\WSearch" /v Start /t REG_DWORD /d 4 /f | Out-Null

        # Disable WiFi Sense
        $softwareHivePath = Join-Path $MountPoint "Windows\System32\config\SOFTWARE"
        $softwareHiveKey = "HKLM\TEMP_DF_SOFTWARE2"
        
        & reg.exe load $softwareHiveKey $softwareHivePath 2>&1 | Out-Null
        & reg.exe add "$softwareHiveKey\Microsoft\WcmSvc\wifinetworkmanager\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f | Out-Null

        Write-DFLog -Message "Privacy hardening applied" -Level Info
    }
    finally {
        [gc]::Collect()
        Start-Sleep -Milliseconds 500
        & reg.exe unload $systemHiveKey 2>&1 | Out-Null
        & reg.exe unload $softwareHiveKey 2>&1 | Out-Null
    }
}

Write-Verbose "Loaded DeployForge Privacy module"
