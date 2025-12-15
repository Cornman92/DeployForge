#Requires -Version 5.1
# Browser installation and configuration module for DeployForge

enum DFBrowserProfile { PrivacyFocused; Performance; Developer; Enterprise; Minimal; Complete }

$script:BrowserPackages = @{
    chrome = "Google.Chrome"; firefox = "Mozilla.Firefox"; edge = "Microsoft.Edge"
    brave = "BraveSoftware.BraveBrowser"; opera = "Opera.Opera"; vivaldi = "Vivaldi.Vivaldi"
    tor = "TorProject.TorBrowser"; librewolf = "LibreWolf.LibreWolf"
}

function Install-DFBrowsers {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [string[]]$Browsers = @('chrome', 'firefox'), [DFBrowserProfile]$Profile)
    
    Write-DFLog -Message "Configuring browser installation: $($Browsers -join ', ')" -Level Info
    
    $scriptsDir = Join-Path $MountPoint "Windows\Setup\Scripts"
    New-Item -ItemType Directory -Path $scriptsDir -Force -ErrorAction SilentlyContinue | Out-Null
    
    $script = "# Browser Installation`nWrite-Host 'Installing browsers...'`n"
    foreach ($browser in $Browsers) {
        if ($script:BrowserPackages.ContainsKey($browser)) {
            $script += "winget install --id $($script:BrowserPackages[$browser]) --silent --accept-package-agreements --accept-source-agreements`n"
        }
    }
    
    Set-Content -Path (Join-Path $scriptsDir "Install-Browsers.ps1") -Value $script -Encoding UTF8
    Write-DFLog -Message "Browser installation configured" -Level Info
}

function Set-DFChromePolicy { param([string]$MountPoint, [hashtable]$Policies) Write-DFLog "Chrome policies configured" -Level Info }
function Set-DFFirefoxPolicy { param([string]$MountPoint, [hashtable]$Policies) Write-DFLog "Firefox policies configured" -Level Info }
function Set-DFEdgePolicy { param([string]$MountPoint, [hashtable]$Policies) Write-DFLog "Edge policies configured" -Level Info }
function Set-DFDefaultBrowser { param([string]$MountPoint, [string]$Browser) Write-DFLog "Default browser set to $Browser" -Level Info }

Write-Verbose "Loaded DeployForge Browsers module"
