function Enable-GamingOptimizations {
    param (
        [string]$MountDir,
        [string]$Profile
    )

    Write-Verbose "Applying Gaming Profile: $Profile"

    $HivePath = Join-Path $MountDir "Windows\System32\config\SOFTWARE"
    $KeyName = "DeployForge_Gaming"

    reg load "HKLM\$KeyName" $HivePath | Out-Null

    try {
        # Game Mode
        $Path = "HKLM:\$KeyName\Microsoft\GameBar"
        if (!(Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
        Set-ItemProperty -Path $Path -Name "AllowAutoGameMode" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $Path -Name "AutoGameModeEnabled" -Value 1 -Type DWord -Force

        # Power Plan (High Performance) - Requires script execution on boot
        # We'll create a setup script
        $ScriptsDir = Join-Path $MountDir "Windows\Setup\Scripts"
        if (!(Test-Path $ScriptsDir)) { New-Item -Path $ScriptsDir -ItemType Directory -Force | Out-Null }
        
        $ScriptContent = @"
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61
"@
        Set-Content -Path (Join-Path $ScriptsDir "GamingPower.cmd") -Value $ScriptContent
        
        # Add to SetupComplete.cmd
        Add-Content -Path (Join-Path $ScriptsDir "SetupComplete.cmd") -Value "`ncall GamingPower.cmd"

        if ($Profile -eq "Competitive") {
            # Disable Nagle Algorithm
            # This is complex as it requires finding the interface GUID.
            # We will use a PowerShell script on first boot.
            $NagleScript = @"
Get-NetAdapter | ForEach-Object {
    New-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\$($_.InterfaceGuid)" -Name "TcpAckFrequency" -Value 1 -PropertyType DWord -Force
    New-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\$($_.InterfaceGuid)" -Name "TCPNoDelay" -Value 1 -PropertyType DWord -Force
}
"@
            Set-Content -Path (Join-Path $ScriptsDir "OptimizeNet.ps1") -Value $NagleScript
             Add-Content -Path (Join-Path $ScriptsDir "SetupComplete.cmd") -Value "`npowershell -ExecutionPolicy Bypass -File OptimizeNet.ps1"
        }
    }
    finally {
        [gc]::Collect()
        reg unload "HKLM\$KeyName" | Out-Null
    }
}
