#Requires -Version 5.1
# WinPE customization module for DeployForge

enum DFWinPEComponent { PowerShell; WMI; NetFX; Network; WiFi; Storage; Recovery; SecureBoot; BitLocker; HTML }

function Mount-DFWinPE {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$WimPath, [string]$MountPoint, [int]$Index = 1)
    
    if (-not $MountPoint) { $MountPoint = Join-Path $env:TEMP "WinPE_$(Get-Random)" }
    New-Item -ItemType Directory -Path $MountPoint -Force | Out-Null
    
    & dism.exe /Mount-Wim /WimFile:"$WimPath" /Index:$Index /MountDir:"$MountPoint" 2>&1 | Out-Null
    Write-DFLog "WinPE mounted to $MountPoint" -Level Info
    return $MountPoint
}

function Dismount-DFWinPE {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [switch]$Save)
    
    $action = if ($Save) { "/Commit" } else { "/Discard" }
    & dism.exe /Unmount-Wim /MountDir:"$MountPoint" $action 2>&1 | Out-Null
    Write-DFLog "WinPE dismounted" -Level Info
}

function Add-DFWinPEComponent {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][DFWinPEComponent]$Component, [string]$ADKPath)
    
    if (-not $ADKPath) { $ADKPath = "${env:ProgramFiles(x86)}\Windows Kits\10\Assessment and Deployment Kit" }
    $packagesPath = Join-Path $ADKPath "Windows Preinstallation Environment\amd64\WinPE_OCs"
    
    $componentMap = @{
        PowerShell = @("WinPE-WMI", "WinPE-NetFX", "WinPE-Scripting", "WinPE-PowerShell")
        WMI = @("WinPE-WMI"); NetFX = @("WinPE-NetFX"); Network = @("WinPE-WDS-Tools")
    }
    
    $packages = $componentMap[$Component.ToString()]
    foreach ($pkg in $packages) {
        $cabPath = Join-Path $packagesPath "$pkg.cab"
        if (Test-Path $cabPath) {
            & dism.exe /Image:"$MountPoint" /Add-Package /PackagePath:"$cabPath" 2>&1 | Out-Null
            Write-DFLog "Added WinPE component: $pkg" -Level Verbose
        }
    }
}

function Add-DFWinPEDriver {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$DriverPath, [switch]$ForceUnsigned)
    
    Add-DFDriver -MountPoint $MountPoint -DriverPaths @($DriverPath) -ForceUnsigned:$ForceUnsigned -Recurse
}

function Set-DFWinPEStartup {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$Script)
    
    $startnetPath = Join-Path $MountPoint "Windows\System32\startnet.cmd"
    Set-Content -Path $startnetPath -Value $Script -Encoding ASCII
    Write-DFLog "WinPE startup script configured" -Level Info
}

function New-DFWinPEISO {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$SourcePath, [Parameter(Mandatory)][string]$OutputPath, [string]$Label = "WinPE")
    
    $oscdimg = "${env:ProgramFiles(x86)}\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
    if (-not (Test-Path $oscdimg)) { throw "oscdimg.exe not found. Install Windows ADK." }
    
    & $oscdimg -m -o -u2 -udfver102 -l"$Label" $SourcePath $OutputPath
    Write-DFLog "WinPE ISO created: $OutputPath" -Level Info
}

Write-Verbose "Loaded DeployForge WinPE module"
