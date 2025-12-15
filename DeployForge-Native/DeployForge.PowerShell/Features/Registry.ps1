#Requires -Version 5.1
# Registry editing module for DeployForge

$script:HivePaths = @{
    "HKLM\SOFTWARE" = "Windows\System32\config\SOFTWARE"
    "HKLM\SYSTEM" = "Windows\System32\config\SYSTEM"
    "HKLM\SECURITY" = "Windows\System32\config\SECURITY"
    "HKLM\SAM" = "Windows\System32\config\SAM"
    "HKU\.DEFAULT" = "Windows\System32\config\DEFAULT"
}

function Set-DFRegistryValue {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$MountPoint,
        [Parameter(Mandatory)][string]$Hive,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)]$Value,
        [ValidateSet('REG_SZ','REG_DWORD','REG_BINARY','REG_EXPAND_SZ','REG_MULTI_SZ')]
        [string]$Type = 'REG_SZ'
    )
    
    $hivePath = Join-Path $MountPoint $script:HivePaths[$Hive]
    $hiveKey = "HKLM\TEMP_DF_REG"
    
    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null
        & reg.exe add "$hiveKey\$Path" /v $Name /t $Type /d $Value /f 2>&1 | Out-Null
        Write-DFLog "Set registry: $Hive\$Path\$Name = $Value" -Level Verbose
    }
    finally {
        [gc]::Collect(); Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Remove-DFRegistryValue {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [string]$Hive, [string]$Path, [string]$Name)
    
    $hivePath = Join-Path $MountPoint $script:HivePaths[$Hive]
    $hiveKey = "HKLM\TEMP_DF_REG"
    
    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null
        & reg.exe delete "$hiveKey\$Path" /v $Name /f 2>&1 | Out-Null
    }
    finally {
        [gc]::Collect(); Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Remove-DFRegistryKey {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [string]$Hive, [string]$Path)
    
    $hivePath = Join-Path $MountPoint $script:HivePaths[$Hive]
    $hiveKey = "HKLM\TEMP_DF_REG"
    
    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null
        & reg.exe delete "$hiveKey\$Path" /f 2>&1 | Out-Null
    }
    finally {
        [gc]::Collect(); Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

function Import-DFRegistryTweaks {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][hashtable[]]$Tweaks)
    
    foreach ($tweak in $Tweaks) {
        Set-DFRegistryValue -MountPoint $MountPoint -Hive $tweak.Hive -Path $tweak.Path -Name $tweak.Name -Value $tweak.Value -Type ($tweak.Type ?? 'REG_DWORD')
    }
}

function Export-DFRegistryHive {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [string]$Hive, [string]$OutputPath)
    
    $hivePath = Join-Path $MountPoint $script:HivePaths[$Hive]
    $hiveKey = "HKLM\TEMP_DF_REG"
    
    try {
        & reg.exe load $hiveKey $hivePath 2>&1 | Out-Null
        & reg.exe export $hiveKey $OutputPath /y 2>&1 | Out-Null
    }
    finally {
        [gc]::Collect(); Start-Sleep -Milliseconds 500
        & reg.exe unload $hiveKey 2>&1 | Out-Null
    }
}

Write-Verbose "Loaded DeployForge Registry module"
