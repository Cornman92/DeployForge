function Set-WindowsUI {
    param (
        [string]$MountDir,
        [string]$Profile
    )

    Write-Verbose "Applying UI Profile: $Profile"

    $UserHive = Join-Path $MountDir "Users\Default\NTUSER.DAT"
    $KeyName = "DeployForge_User"

    reg load "HKLM\$KeyName" $UserHive | Out-Null

    try {
        if ($Profile -eq "Modern") {
            # Center Taskbar (Windows 11 default, explicitly set)
            $Path = "HKLM:\$KeyName\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            if (!(Test-Path $Path)) { New-Item -Path $Path -Force | Out-Null }
            Set-ItemProperty -Path $Path -Name "TaskbarAl" -Value 1 -Type DWord -Force
        }
        elseif ($Profile -eq "Classic") {
            # Left Align
            $Path = "HKLM:\$KeyName\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            Set-ItemProperty -Path $Path -Name "TaskbarAl" -Value 0 -Type DWord -Force
            
            # Restore Win10 Context Menu
            $ClsidPath = "HKLM:\$KeyName\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            New-Item -Path $ClsidPath -Force | Out-Null
            Set-Item -Path $ClsidPath -Value ""
        }

        # Dark Mode
        $ThemePath = "HKLM:\$KeyName\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        Set-ItemProperty -Path $ThemePath -Name "AppsUseLightTheme" -Value 0 -Type DWord -Force
        Set-ItemProperty -Path $ThemePath -Name "SystemUsesLightTheme" -Value 0 -Type DWord -Force
    }
    finally {
        [gc]::Collect()
        reg unload "HKLM\$KeyName" | Out-Null
    }
}
