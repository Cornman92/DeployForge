#Requires -Version 5.1
# Driver injection module for DeployForge

function Add-DFDriver {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$MountPoint,
        [Parameter(Mandatory)][string[]]$DriverPaths,
        [switch]$ForceUnsigned, [switch]$Recurse
    )
    
    Write-DFLog -Message "Injecting drivers from $($DriverPaths.Count) path(s)" -Level Info
    
    foreach ($path in $DriverPaths) {
        $args = @("/Image:`"$MountPoint`"", "/Add-Driver", "/Driver:`"$path`"")
        if ($Recurse) { $args += "/Recurse" }
        if ($ForceUnsigned) { $args += "/ForceUnsigned" }
        
        $result = & dism.exe $args 2>&1
        if ($LASTEXITCODE -eq 0) { Write-DFLog "Driver added: $path" -Level Info }
        else { Write-DFLog "Failed to add driver: $path" -Level Warning }
    }
}

function Get-DFDrivers {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint)
    
    $result = & dism.exe /Image:"$MountPoint" /Get-Drivers 2>&1
    return $result
}

function Remove-DFDriver {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$DriverName)
    
    & dism.exe /Image:"$MountPoint" /Remove-Driver /Driver:$DriverName 2>&1 | Out-Null
    Write-DFLog "Driver removed: $DriverName" -Level Info
}

Write-Verbose "Loaded DeployForge Drivers module"
