#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge UI Customization Module
.DESCRIPTION
    Functions for customizing Windows UI elements including taskbar,
    Start menu, File Explorer, and visual settings.
#>

# UI Profiles
$Script:UIProfiles = @{
    Modern = @{
        DarkMode = $true
        TaskbarAlignment = 'Center'
        TaskbarSearchMode = 'Icon'
        ShowTaskView = $true
        ShowWidgets = $true
        ShowChat = $false
        StartLayoutMode = 'Default'
        ShowRecommendations = $true
    }
    Classic = @{
        DarkMode = $false
        TaskbarAlignment = 'Left'
        TaskbarSearchMode = 'Box'
        ShowTaskView = $false
        ShowWidgets = $false
        ShowChat = $false
        StartLayoutMode = 'MorePins'
        ShowRecommendations = $false
        ClassicContextMenu = $true
    }
    Minimal = @{
        DarkMode = $true
        TaskbarAlignment = 'Left'
        TaskbarSearchMode = 'Hide'
        ShowTaskView = $false
        ShowWidgets = $false
        ShowChat = $false
        StartLayoutMode = 'MorePins'
        ShowRecommendations = $false
    }
    Productivity = @{
        DarkMode = $true
        TaskbarAlignment = 'Left'
        TaskbarSearchMode = 'Box'
        ShowTaskView = $true
        ShowWidgets = $false
        ShowChat = $false
        StartLayoutMode = 'MorePins'
        ShowRecommendations = $false
        ShowDesktopIcons = $true
    }
    Gaming = @{
        DarkMode = $true
        TaskbarAlignment = 'Center'
        TaskbarSearchMode = 'Hide'
        ShowTaskView = $false
        ShowWidgets = $false
        ShowChat = $false
        StartLayoutMode = 'Default'
        ShowRecommendations = $false
        DisableTransparency = $true
    }
    Enterprise = @{
        DarkMode = $false
        TaskbarAlignment = 'Left'
        TaskbarSearchMode = 'Box'
        ShowTaskView = $true
        ShowWidgets = $false
        ShowChat = $false
        StartLayoutMode = 'MorePins'
        ShowRecommendations = $false
        LockTaskbar = $true
    }
}

function Set-UICustomization {
    <#
    .SYNOPSIS
        Configures Windows UI customizations.
    .PARAMETER MountPath
        Path to mounted Windows image.
    .PARAMETER Profile
        UI profile to apply.
    .PARAMETER DarkMode
        Enable dark mode.
    .PARAMETER DisableWidgets
        Disable Windows widgets.
    .PARAMETER DisableNews
        Disable News and Interests.
    .PARAMETER ClassicContextMenu
        Use Windows 10 style context menu.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('Modern', 'Classic', 'Minimal', 'Productivity', 'Gaming', 'Enterprise')]
        [string]$Profile = 'Modern',
        
        [Parameter()]
        [bool]$DarkMode,
        
        [Parameter()]
        [bool]$DisableWidgets,
        
        [Parameter()]
        [bool]$DisableNews,
        
        [Parameter()]
        [bool]$ClassicContextMenu
    )
    
    begin {
        Write-Verbose "Applying $Profile UI customization"
        $profileConfig = $Script:UIProfiles[$Profile]
    }
    
    process {
        try {
            # Apply profile defaults if not overridden
            if (-not $PSBoundParameters.ContainsKey('DarkMode')) {
                $DarkMode = $profileConfig.DarkMode
            }
            if (-not $PSBoundParameters.ContainsKey('DisableWidgets')) {
                $DisableWidgets = -not $profileConfig.ShowWidgets
            }
            if (-not $PSBoundParameters.ContainsKey('ClassicContextMenu')) {
                $ClassicContextMenu = $profileConfig.ClassicContextMenu -eq $true
            }
            
            # Apply dark/light mode
            if ($DarkMode) {
                Enable-DarkMode -MountPath $MountPath
            }
            else {
                Disable-DarkMode -MountPath $MountPath
            }
            
            # Configure taskbar
            Set-TaskbarSettings -MountPath $MountPath `
                -Alignment $profileConfig.TaskbarAlignment `
                -SearchMode $profileConfig.TaskbarSearchMode `
                -ShowTaskView $profileConfig.ShowTaskView `
                -ShowWidgets (-not $DisableWidgets) `
                -ShowChat $profileConfig.ShowChat
            
            # Configure Start menu
            Set-StartMenuSettings -MountPath $MountPath `
                -LayoutMode $profileConfig.StartLayoutMode `
                -ShowRecommendations $profileConfig.ShowRecommendations
            
            # Configure context menu
            if ($ClassicContextMenu) {
                Enable-ClassicContextMenu -MountPath $MountPath
            }
            
            # Disable News and Interests if requested
            if ($DisableNews) {
                Disable-NewsAndInterests -MountPath $MountPath
            }
            
            # Configure File Explorer
            Set-FileExplorerSettings -MountPath $MountPath
            
            Write-Verbose "UI customization complete"
            
            return @{
                Success = $true
                Profile = $Profile
                DarkMode = $DarkMode
                DisableWidgets = $DisableWidgets
                ClassicContextMenu = $ClassicContextMenu
            }
        }
        catch {
            Write-Error "Failed to apply UI customization: $_"
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}

function Enable-DarkMode {
    <#
    .SYNOPSIS
        Enables system-wide dark mode.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Enabling dark mode"
    
    # Set default user theme
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_DARK"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        $themePath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        reg add $themePath /v AppsUseLightTheme /t REG_DWORD /d 0 /f | Out-Null
        reg add $themePath /v SystemUsesLightTheme /t REG_DWORD /d 0 /f | Out-Null
        reg add $themePath /v ColorPrevalence /t REG_DWORD /d 1 /f | Out-Null
        
        Write-Verbose "Dark mode enabled"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Disable-DarkMode {
    <#
    .SYNOPSIS
        Disables dark mode (enables light mode).
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Enabling light mode"
    
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_LIGHT"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        $themePath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        reg add $themePath /v AppsUseLightTheme /t REG_DWORD /d 1 /f | Out-Null
        reg add $themePath /v SystemUsesLightTheme /t REG_DWORD /d 1 /f | Out-Null
        
        Write-Verbose "Light mode enabled"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Set-TaskbarSettings {
    <#
    .SYNOPSIS
        Configures taskbar settings.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('Left', 'Center')]
        [string]$Alignment = 'Center',
        
        [Parameter()]
        [ValidateSet('Hide', 'Icon', 'Box')]
        [string]$SearchMode = 'Icon',
        
        [Parameter()]
        [bool]$ShowTaskView = $true,
        
        [Parameter()]
        [bool]$ShowWidgets = $false,
        
        [Parameter()]
        [bool]$ShowChat = $false
    )
    
    Write-Verbose "Configuring taskbar settings"
    
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_TASKBAR"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        # Taskbar alignment (Windows 11)
        $alignValue = if ($Alignment -eq 'Left') { 0 } else { 1 }
        $advancedPath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        reg add $advancedPath /v TaskbarAl /t REG_DWORD /d $alignValue /f | Out-Null
        
        # Search mode
        $searchValue = switch ($SearchMode) {
            'Hide' { 0 }
            'Icon' { 1 }
            'Box' { 2 }
        }
        $searchPath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
        reg add $searchPath /v SearchboxTaskbarMode /t REG_DWORD /d $searchValue /f | Out-Null
        
        # Task View button
        $taskViewValue = if ($ShowTaskView) { 1 } else { 0 }
        reg add $advancedPath /v ShowTaskViewButton /t REG_DWORD /d $taskViewValue /f | Out-Null
        
        # Widgets
        $widgetsValue = if ($ShowWidgets) { 1 } else { 0 }
        reg add $advancedPath /v TaskbarDa /t REG_DWORD /d $widgetsValue /f | Out-Null
        
        # Chat (Teams)
        $chatValue = if ($ShowChat) { 1 } else { 0 }
        reg add $advancedPath /v TaskbarMn /t REG_DWORD /d $chatValue /f | Out-Null
        
        Write-Verbose "Taskbar settings configured"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Set-StartMenuSettings {
    <#
    .SYNOPSIS
        Configures Start menu settings.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('Default', 'MorePins', 'MoreRecommendations')]
        [string]$LayoutMode = 'Default',
        
        [Parameter()]
        [bool]$ShowRecommendations = $true
    )
    
    Write-Verbose "Configuring Start menu settings"
    
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_START"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        $startPath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        
        # Layout mode
        $layoutValue = switch ($LayoutMode) {
            'MorePins' { 1 }
            'MoreRecommendations' { 2 }
            default { 0 }
        }
        reg add $startPath /v Start_Layout /t REG_DWORD /d $layoutValue /f | Out-Null
        
        # Show/hide recommendations
        $recoValue = if ($ShowRecommendations) { 1 } else { 0 }
        reg add $startPath /v Start_IrisRecommendations /t REG_DWORD /d $recoValue /f | Out-Null
        
        Write-Verbose "Start menu settings configured"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Enable-ClassicContextMenu {
    <#
    .SYNOPSIS
        Enables Windows 10 style context menu.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Enabling classic context menu"
    
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_CONTEXT"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        $clsidPath = "$tempKey\SOFTWARE\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
        reg add $clsidPath /ve /t REG_SZ /d "" /f | Out-Null
        
        Write-Verbose "Classic context menu enabled"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Disable-NewsAndInterests {
    <#
    .SYNOPSIS
        Disables News and Interests widget.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Disabling News and Interests"
    
    $hivePath = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $tempKey = "HKLM\OFFLINE_SW_NEWS"
    
    try {
        reg load $tempKey $hivePath 2>$null
        
        $policyPath = "$tempKey\Policies\Microsoft\Dsh"
        reg add $policyPath /v AllowNewsAndInterests /t REG_DWORD /d 0 /f | Out-Null
        
        Write-Verbose "News and Interests disabled"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Set-FileExplorerSettings {
    <#
    .SYNOPSIS
        Configures File Explorer settings.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [bool]$ShowExtensions = $true,
        
        [Parameter()]
        [bool]$ShowHiddenFiles = $false,
        
        [Parameter()]
        [bool]$CompactView = $false
    )
    
    Write-Verbose "Configuring File Explorer settings"
    
    $defaultUserHive = Join-Path $MountPath "Users\Default\NTUSER.DAT"
    $tempKey = "HKLM\OFFLINE_DEFUSER_EXPLORER"
    
    try {
        reg load $tempKey $defaultUserHive 2>$null
        
        $advPath = "$tempKey\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        
        # Show file extensions
        $extValue = if ($ShowExtensions) { 0 } else { 1 }
        reg add $advPath /v HideFileExt /t REG_DWORD /d $extValue /f | Out-Null
        
        # Show hidden files
        $hiddenValue = if ($ShowHiddenFiles) { 1 } else { 2 }
        reg add $advPath /v Hidden /t REG_DWORD /d $hiddenValue /f | Out-Null
        
        # Compact view
        $compactValue = if ($CompactView) { 1 } else { 0 }
        reg add $advPath /v UseCompactMode /t REG_DWORD /d $compactValue /f | Out-Null
        
        # Open to This PC instead of Quick Access
        reg add $advPath /v LaunchTo /t REG_DWORD /d 1 /f | Out-Null
        
        Write-Verbose "File Explorer settings configured"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

# Export functions
Export-ModuleMember -Function @(
    'Set-UICustomization',
    'Enable-DarkMode',
    'Disable-DarkMode',
    'Set-TaskbarSettings',
    'Set-StartMenuSettings',
    'Enable-ClassicContextMenu',
    'Disable-NewsAndInterests',
    'Set-FileExplorerSettings'
)
