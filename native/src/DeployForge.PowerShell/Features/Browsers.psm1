#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Browser Configuration Module
.DESCRIPTION
    Functions for installing and configuring web browsers in Windows images.
    Includes enterprise policies, privacy settings, and default browser configuration.
#>

# Browser definitions
$Script:BrowserPackages = @{
    Chrome = @{
        WingetId = 'Google.Chrome'
        Name = 'Google Chrome'
        PolicyPath = 'SOFTWARE\Policies\Google\Chrome'
    }
    Firefox = @{
        WingetId = 'Mozilla.Firefox'
        Name = 'Mozilla Firefox'
        PolicyPath = 'SOFTWARE\Policies\Mozilla\Firefox'
    }
    Edge = @{
        WingetId = 'Microsoft.Edge'
        Name = 'Microsoft Edge'
        PolicyPath = 'SOFTWARE\Policies\Microsoft\Edge'
    }
    Brave = @{
        WingetId = 'Brave.Brave'
        Name = 'Brave Browser'
        PolicyPath = 'SOFTWARE\Policies\BraveSoftware\Brave'
    }
    Vivaldi = @{
        WingetId = 'VivaldiTechnologies.Vivaldi'
        Name = 'Vivaldi'
        PolicyPath = 'SOFTWARE\Policies\Vivaldi'
    }
    Opera = @{
        WingetId = 'Opera.Opera'
        Name = 'Opera'
        PolicyPath = 'SOFTWARE\Policies\Opera'
    }
}

# Browser profiles
$Script:BrowserProfiles = @{
    Minimal = @{
        Browsers = @('Edge')
        ApplyPolicies = $false
        SetDefault = 'Edge'
    }
    Privacy = @{
        Browsers = @('Firefox', 'Brave')
        ApplyPolicies = $true
        SetDefault = 'Firefox'
        PolicySet = 'Privacy'
    }
    Enterprise = @{
        Browsers = @('Edge', 'Chrome')
        ApplyPolicies = $true
        SetDefault = 'Edge'
        PolicySet = 'Enterprise'
    }
    Developer = @{
        Browsers = @('Chrome', 'Firefox', 'Edge')
        ApplyPolicies = $true
        SetDefault = 'Chrome'
        PolicySet = 'Developer'
    }
    Standard = @{
        Browsers = @('Chrome', 'Edge')
        ApplyPolicies = $false
        SetDefault = 'Chrome'
    }
}

function Set-BrowserConfiguration {
    <#
    .SYNOPSIS
        Configures browsers in mounted Windows image.
    .PARAMETER MountPath
        Path to mounted Windows image.
    .PARAMETER DefaultBrowser
        Default browser to set.
    .PARAMETER InstallChrome
        Install Google Chrome.
    .PARAMETER InstallFirefox
        Install Mozilla Firefox.
    .PARAMETER InstallBrave
        Install Brave Browser.
    .PARAMETER ApplyPolicies
        Apply enterprise browser policies.
    .PARAMETER Profile
        Browser profile to apply.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('Edge', 'Chrome', 'Firefox', 'Brave', 'Vivaldi', 'Opera')]
        [string]$DefaultBrowser = 'Edge',
        
        [Parameter()]
        [bool]$InstallChrome = $false,
        
        [Parameter()]
        [bool]$InstallFirefox = $false,
        
        [Parameter()]
        [bool]$InstallBrave = $false,
        
        [Parameter()]
        [bool]$ApplyPolicies = $false,
        
        [Parameter()]
        [ValidateSet('Minimal', 'Privacy', 'Enterprise', 'Developer', 'Standard')]
        [string]$Profile
    )
    
    begin {
        Write-Verbose "Configuring browser settings"
        $browsersToInstall = @()
    }
    
    process {
        try {
            # Determine browsers to install
            if ($Profile) {
                $profileConfig = $Script:BrowserProfiles[$Profile]
                $browsersToInstall = $profileConfig.Browsers
                $DefaultBrowser = $profileConfig.SetDefault
                $ApplyPolicies = $profileConfig.ApplyPolicies
            }
            else {
                if ($InstallChrome) { $browsersToInstall += 'Chrome' }
                if ($InstallFirefox) { $browsersToInstall += 'Firefox' }
                if ($InstallBrave) { $browsersToInstall += 'Brave' }
            }
            
            # Create installation script
            $installScript = New-BrowserInstallScript -Browsers $browsersToInstall
            
            $scriptPath = Join-Path $MountPath "Windows\Setup\Scripts"
            if (-not (Test-Path $scriptPath)) {
                New-Item -Path $scriptPath -ItemType Directory -Force | Out-Null
            }
            
            $installScript | Out-File -FilePath (Join-Path $scriptPath "InstallBrowsers.ps1") -Encoding UTF8 -Force
            
            # Apply browser policies
            if ($ApplyPolicies) {
                $policySet = if ($Profile -and $Script:BrowserProfiles[$Profile].PolicySet) {
                    $Script:BrowserProfiles[$Profile].PolicySet
                } else {
                    'Standard'
                }
                
                Set-BrowserPolicies -MountPath $MountPath -PolicySet $policySet
            }
            
            # Configure default browser
            Set-DefaultBrowser -MountPath $MountPath -Browser $DefaultBrowser
            
            Write-Verbose "Browser configuration complete"
            
            return @{
                Success = $true
                DefaultBrowser = $DefaultBrowser
                InstalledBrowsers = $browsersToInstall
                PoliciesApplied = $ApplyPolicies
            }
        }
        catch {
            Write-Error "Failed to configure browsers: $_"
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}

function New-BrowserInstallScript {
    <#
    .SYNOPSIS
        Creates a PowerShell script to install browsers at first boot.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string[]]$Browsers
    )
    
    $script = @"
# DeployForge Browser Installation Script
# This script runs at first boot to install browsers

`$ErrorActionPreference = 'SilentlyContinue'

# Wait for winget
`$retries = 0
while (-not (Get-Command winget -ErrorAction SilentlyContinue) -and `$retries -lt 30) {
    Write-Host "Waiting for Windows Package Manager..."
    Start-Sleep -Seconds 10
    `$retries++
}

# Install browsers
"@
    
    foreach ($browser in $Browsers) {
        if ($Script:BrowserPackages.ContainsKey($browser)) {
            $package = $Script:BrowserPackages[$browser]
            $script += @"

Write-Host "Installing $($package.Name)..."
winget install --id $($package.WingetId) --silent --accept-package-agreements --accept-source-agreements
"@
        }
    }
    
    $script += @"

Write-Host "Browser installation complete!"
"@
    
    return $script
}

function Set-BrowserPolicies {
    <#
    .SYNOPSIS
        Applies enterprise browser policies.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('Standard', 'Privacy', 'Enterprise', 'Developer')]
        [string]$PolicySet = 'Standard'
    )
    
    Write-Verbose "Applying $PolicySet browser policies"
    
    $hivePath = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $tempKey = "HKLM\OFFLINE_SW_BROWSER"
    
    try {
        reg load $tempKey $hivePath 2>$null
        
        switch ($PolicySet) {
            'Privacy' {
                # Chrome privacy policies
                $chromePath = "$tempKey\Policies\Google\Chrome"
                reg add $chromePath /v BlockThirdPartyCookies /t REG_DWORD /d 1 /f | Out-Null
                reg add $chromePath /v SafeBrowsingEnabled /t REG_DWORD /d 1 /f | Out-Null
                reg add $chromePath /v MetricsReportingEnabled /t REG_DWORD /d 0 /f | Out-Null
                reg add $chromePath /v SpellCheckServiceEnabled /t REG_DWORD /d 0 /f | Out-Null
                reg add $chromePath /v SearchSuggestEnabled /t REG_DWORD /d 0 /f | Out-Null
                reg add $chromePath /v PasswordManagerEnabled /t REG_DWORD /d 0 /f | Out-Null
                
                # Firefox privacy policies
                $firefoxPath = "$tempKey\Policies\Mozilla\Firefox"
                reg add $firefoxPath /v DisableTelemetry /t REG_DWORD /d 1 /f | Out-Null
                reg add $firefoxPath /v DisableFirefoxStudies /t REG_DWORD /d 1 /f | Out-Null
                reg add $firefoxPath /v EnableTrackingProtection /t REG_DWORD /d 1 /f | Out-Null
                
                # Edge privacy policies
                $edgePath = "$tempKey\Policies\Microsoft\Edge"
                reg add $edgePath /v BlockThirdPartyCookies /t REG_DWORD /d 1 /f | Out-Null
                reg add $edgePath /v SendSiteInfoToImproveServices /t REG_DWORD /d 0 /f | Out-Null
                reg add $edgePath /v PersonalizationReportingEnabled /t REG_DWORD /d 0 /f | Out-Null
            }
            
            'Enterprise' {
                # Edge enterprise policies
                $edgePath = "$tempKey\Policies\Microsoft\Edge"
                reg add $edgePath /v BrowserSignin /t REG_DWORD /d 0 /f | Out-Null
                reg add $edgePath /v SyncDisabled /t REG_DWORD /d 1 /f | Out-Null
                reg add $edgePath /v ExtensionInstallBlocklist /t REG_SZ /d "*" /f | Out-Null
                reg add $edgePath /v PasswordManagerEnabled /t REG_DWORD /d 0 /f | Out-Null
                reg add $edgePath /v AutofillCreditCardEnabled /t REG_DWORD /d 0 /f | Out-Null
                
                # Chrome enterprise policies
                $chromePath = "$tempKey\Policies\Google\Chrome"
                reg add $chromePath /v BrowserSignin /t REG_DWORD /d 0 /f | Out-Null
                reg add $chromePath /v SyncDisabled /t REG_DWORD /d 1 /f | Out-Null
                reg add $chromePath /v AutofillCreditCardEnabled /t REG_DWORD /d 0 /f | Out-Null
            }
            
            'Developer' {
                # Chrome developer settings
                $chromePath = "$tempKey\Policies\Google\Chrome"
                reg add $chromePath /v DeveloperToolsAvailability /t REG_DWORD /d 1 /f | Out-Null
                reg add $chromePath /v ExtensionInstallAllowlist /t REG_SZ /d "*" /f | Out-Null
                
                # Edge developer settings
                $edgePath = "$tempKey\Policies\Microsoft\Edge"
                reg add $edgePath /v DeveloperToolsAvailability /t REG_DWORD /d 1 /f | Out-Null
            }
        }
        
        Write-Verbose "Browser policies applied"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Set-DefaultBrowser {
    <#
    .SYNOPSIS
        Configures the default browser.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [string]$Browser = 'Edge'
    )
    
    Write-Verbose "Setting $Browser as default browser"
    
    # Create script to set default browser at first logon
    $script = @"
# Set default browser
`$progId = switch ('$Browser') {
    'Chrome' { 'ChromeHTML' }
    'Firefox' { 'FirefoxHTML' }
    'Edge' { 'MSEdgeHTM' }
    'Brave' { 'BraveHTML' }
    default { 'MSEdgeHTM' }
}

# Set URL and HTTP/HTTPS associations
`$associations = @(
    'http',
    'https',
    '.html',
    '.htm'
)

foreach (`$assoc in `$associations) {
    try {
        `$null = New-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\`$assoc\UserChoice" -Name 'ProgId' -Value `$progId -Force -ErrorAction SilentlyContinue
    } catch { }
}

Write-Host "Default browser set to $Browser"
"@
    
    $scriptPath = Join-Path $MountPath "Windows\Setup\Scripts\SetDefaultBrowser.ps1"
    $script | Out-File -FilePath $scriptPath -Encoding UTF8 -Force
    
    Write-Verbose "Default browser script created"
}

# Export functions
Export-ModuleMember -Function @(
    'Set-BrowserConfiguration',
    'Set-BrowserPolicies',
    'Set-DefaultBrowser'
)
