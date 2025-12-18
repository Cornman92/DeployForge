function Enable-PrivacyHardening {
    param (
        [string]$MountDir,
        [hashtable]$Config
    )

    Write-Verbose "Applying Privacy Hardening..."

    $HivePath = Join-Path $MountDir "Windows\System32\config\SOFTWARE"
    $KeyName = "DeployForge_Privacy"

    reg load "HKLM\$KeyName" $HivePath | Out-Null

    try {
        # Telemetry
        if ($Config.DisableTelemetry) {
            Set-ItemProperty -Path "HKLM:\$KeyName\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Type DWord -Force
        }

        # Cortana
        if ($Config.DisableCortana) {
            $Path = "HKLM:\$KeyName\Policies\Microsoft\Windows\Windows Search"
            if (!(Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
            Set-ItemProperty -Path $Path -Name "AllowCortana" -Value 0 -Type DWord -Force
        }

        # Web Search
        if ($Config.DisableWebSearch) {
            $Path = "HKLM:\$KeyName\Policies\Microsoft\Windows\Windows Search"
            if (!(Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
            Set-ItemProperty -Path $Path -Name "DisableWebSearch" -Value 1 -Type DWord -Force
            Set-ItemProperty -Path $Path -Name "ConnectedSearchUseWeb" -Value 0 -Type DWord -Force
        }

        # Location
        if ($Config.DisableLocation) {
             $Path = "HKLM:\$KeyName\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
             if (!(Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
             Set-ItemProperty -Path $Path -Name "Value" -Value "Deny" -Type String -Force
        }

        # Hosts blocking
        if ($Config.BlockTelemetryIps) {
            $HostsPath = Join-Path $MountDir "Windows\System32\drivers\etc\hosts"
            $Domains = @(
                "vortex.data.microsoft.com",
                "vortex-win.data.microsoft.com",
                "telecommand.telemetry.microsoft.com"
            )
            
            Add-Content -Path $HostsPath -Value "`n# DeployForge Privacy Block"
            foreach ($Domain in $Domains) {
                Add-Content -Path $HostsPath -Value "0.0.0.0 $Domain"
            }
        }
    }
    finally {
        [gc]::Collect()
        reg unload "HKLM\$KeyName" | Out-Null
    }
}
