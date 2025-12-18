#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Registry Manager - Offline registry hive manipulation
    
.DESCRIPTION
    Provides functions for loading, modifying, and saving offline Windows registry hives
    from mounted deployment images.
#>

# Loaded hives tracking
$script:LoadedHives = @{}

# Registry hive paths relative to Windows mount point
$script:HivePaths = @{
    'SOFTWARE'   = 'Windows\System32\config\SOFTWARE'
    'SYSTEM'     = 'Windows\System32\config\SYSTEM'
    'SECURITY'   = 'Windows\System32\config\SECURITY'
    'SAM'        = 'Windows\System32\config\SAM'
    'DEFAULT'    = 'Windows\System32\config\DEFAULT'
    'NTUSER'     = 'Users\Default\NTUSER.DAT'
}

function Mount-OfflineRegistry {
    <#
    .SYNOPSIS
        Loads an offline registry hive for editing.
        
    .DESCRIPTION
        Loads a registry hive from a mounted Windows image into the current registry
        under a temporary key for offline editing.
        
    .PARAMETER MountPath
        Path where the Windows image is mounted.
        
    .PARAMETER Hive
        The hive to load (SOFTWARE, SYSTEM, SECURITY, SAM, DEFAULT, NTUSER).
        
    .PARAMETER KeyName
        The registry key name to mount the hive under. Default auto-generates.
        
    .EXAMPLE
        Mount-OfflineRegistry -MountPath "D:\Mount" -Hive SOFTWARE
        
    .EXAMPLE
        Mount-OfflineRegistry -MountPath "D:\Mount" -Hive NTUSER -KeyName "HKLM\OFFLINE_USER"
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ })]
        [string]$MountPath,
        
        [Parameter(Mandatory = $true)]
        [ValidateSet('SOFTWARE', 'SYSTEM', 'SECURITY', 'SAM', 'DEFAULT', 'NTUSER')]
        [string]$Hive,
        
        [Parameter(Mandatory = $false)]
        [string]$KeyName
    )
    
    begin {
        Write-Verbose "Mount-OfflineRegistry: Loading $Hive hive"
    }
    
    process {
        # Check if hive is already loaded
        if ($script:LoadedHives.ContainsKey($Hive)) {
            Write-Warning "$Hive hive is already loaded at $($script:LoadedHives[$Hive])"
            return [PSCustomObject]@{
                Success = $false
                Hive = $Hive
                KeyName = $script:LoadedHives[$Hive]
                Message = "Hive already loaded"
            }
        }
        
        # Build hive path
        $hivePath = Join-Path $MountPath $script:HivePaths[$Hive]
        
        if (-not (Test-Path $hivePath)) {
            throw "Registry hive not found: $hivePath"
        }
        
        # Generate key name if not provided
        if (-not $KeyName) {
            $KeyName = "HKLM\DEPLOYFORGE_$($Hive)_$(Get-Random -Maximum 9999)"
        }
        
        try {
            Write-Host "Loading registry hive: $Hive" -ForegroundColor Cyan
            Write-Host "  Source: $hivePath" -ForegroundColor Gray
            Write-Host "  Target: $KeyName" -ForegroundColor Gray
            
            # Load the hive using reg.exe
            $result = & reg.exe load $KeyName $hivePath 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                throw "reg.exe load failed: $result"
            }
            
            # Track the loaded hive
            $script:LoadedHives[$Hive] = $KeyName
            
            Write-Host "✓ Registry hive loaded successfully" -ForegroundColor Green
            
            return [PSCustomObject]@{
                Success = $true
                Hive = $Hive
                KeyName = $KeyName
                HivePath = $hivePath
                Message = "Hive loaded successfully"
            }
        }
        catch {
            Write-Error "Failed to load registry hive: $_"
            return [PSCustomObject]@{
                Success = $false
                Hive = $Hive
                Error = $_.Exception.Message
            }
        }
    }
}

function Dismount-OfflineRegistry {
    <#
    .SYNOPSIS
        Unloads an offline registry hive.
        
    .DESCRIPTION
        Unloads a previously loaded offline registry hive, saving any changes.
        
    .PARAMETER Hive
        The hive to unload (or 'All' to unload all loaded hives).
        
    .EXAMPLE
        Dismount-OfflineRegistry -Hive SOFTWARE
        
    .EXAMPLE
        Dismount-OfflineRegistry -Hive All
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Hive
    )
    
    process {
        if ($Hive -eq 'All') {
            # Unload all hives
            $results = @()
            foreach ($loadedHive in $script:LoadedHives.Keys.Clone()) {
                $results += Dismount-OfflineRegistry -Hive $loadedHive
            }
            return $results
        }
        
        if (-not $script:LoadedHives.ContainsKey($Hive)) {
            Write-Warning "$Hive hive is not loaded"
            return [PSCustomObject]@{
                Success = $false
                Hive = $Hive
                Message = "Hive not loaded"
            }
        }
        
        $keyName = $script:LoadedHives[$Hive]
        
        try {
            Write-Host "Unloading registry hive: $Hive" -ForegroundColor Cyan
            
            # Force garbage collection to release any handles
            [GC]::Collect()
            [GC]::WaitForPendingFinalizers()
            Start-Sleep -Milliseconds 500
            
            # Unload the hive
            $result = & reg.exe unload $keyName 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                throw "reg.exe unload failed: $result"
            }
            
            # Remove from tracking
            $script:LoadedHives.Remove($Hive)
            
            Write-Host "✓ Registry hive unloaded successfully" -ForegroundColor Green
            
            return [PSCustomObject]@{
                Success = $true
                Hive = $Hive
                KeyName = $keyName
                Message = "Hive unloaded successfully"
            }
        }
        catch {
            Write-Error "Failed to unload registry hive: $_"
            return [PSCustomObject]@{
                Success = $false
                Hive = $Hive
                Error = $_.Exception.Message
            }
        }
    }
}

function Set-OfflineRegistryValue {
    <#
    .SYNOPSIS
        Sets a registry value in an offline hive.
        
    .DESCRIPTION
        Creates or modifies a registry value in a loaded offline registry hive.
        
    .PARAMETER Hive
        The loaded hive to modify.
        
    .PARAMETER Path
        The subkey path (relative to the hive root).
        
    .PARAMETER Name
        The value name.
        
    .PARAMETER Value
        The value data.
        
    .PARAMETER Type
        The value type (String, DWord, QWord, Binary, ExpandString, MultiString).
        
    .EXAMPLE
        Set-OfflineRegistryValue -Hive SOFTWARE -Path "Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Type DWord
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('SOFTWARE', 'SYSTEM', 'SECURITY', 'SAM', 'DEFAULT', 'NTUSER')]
        [string]$Hive,
        
        [Parameter(Mandatory = $true)]
        [string]$Path,
        
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter(Mandatory = $true)]
        $Value,
        
        [Parameter(Mandatory = $false)]
        [ValidateSet('String', 'DWord', 'QWord', 'Binary', 'ExpandString', 'MultiString')]
        [string]$Type = 'DWord'
    )
    
    process {
        if (-not $script:LoadedHives.ContainsKey($Hive)) {
            throw "$Hive hive is not loaded. Call Mount-OfflineRegistry first."
        }
        
        $keyName = $script:LoadedHives[$Hive]
        $fullPath = "$keyName\$Path"
        
        # Map type to reg.exe type
        $regType = switch ($Type) {
            'String' { 'REG_SZ' }
            'DWord' { 'REG_DWORD' }
            'QWord' { 'REG_QWORD' }
            'Binary' { 'REG_BINARY' }
            'ExpandString' { 'REG_EXPAND_SZ' }
            'MultiString' { 'REG_MULTI_SZ' }
        }
        
        try {
            Write-Verbose "Setting registry value: $fullPath\$Name = $Value ($Type)"
            
            # Create key if it doesn't exist
            $null = & reg.exe add $fullPath /f 2>&1
            
            # Set value
            $result = & reg.exe add $fullPath /v $Name /t $regType /d $Value /f 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                throw "reg.exe add failed: $result"
            }
            
            Write-Verbose "✓ Registry value set successfully"
            
            return [PSCustomObject]@{
                Success = $true
                Hive = $Hive
                Path = $Path
                Name = $Name
                Value = $Value
                Type = $Type
            }
        }
        catch {
            Write-Error "Failed to set registry value: $_"
            return [PSCustomObject]@{
                Success = $false
                Hive = $Hive
                Path = $Path
                Name = $Name
                Error = $_.Exception.Message
            }
        }
    }
}

function Get-OfflineRegistryValue {
    <#
    .SYNOPSIS
        Gets a registry value from an offline hive.
        
    .PARAMETER Hive
        The loaded hive to query.
        
    .PARAMETER Path
        The subkey path.
        
    .PARAMETER Name
        The value name (omit to get all values).
        
    .EXAMPLE
        Get-OfflineRegistryValue -Hive SOFTWARE -Path "Microsoft\Windows NT\CurrentVersion" -Name "ProductName"
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('SOFTWARE', 'SYSTEM', 'SECURITY', 'SAM', 'DEFAULT', 'NTUSER')]
        [string]$Hive,
        
        [Parameter(Mandatory = $true)]
        [string]$Path,
        
        [Parameter(Mandatory = $false)]
        [string]$Name
    )
    
    process {
        if (-not $script:LoadedHives.ContainsKey($Hive)) {
            throw "$Hive hive is not loaded"
        }
        
        $keyName = $script:LoadedHives[$Hive]
        $fullPath = "Registry::$keyName\$Path"
        
        try {
            if (-not (Test-Path $fullPath)) {
                return $null
            }
            
            if ($Name) {
                $value = Get-ItemProperty -Path $fullPath -Name $Name -ErrorAction SilentlyContinue
                if ($value) {
                    return [PSCustomObject]@{
                        Hive = $Hive
                        Path = $Path
                        Name = $Name
                        Value = $value.$Name
                    }
                }
            }
            else {
                return Get-ItemProperty -Path $fullPath -ErrorAction SilentlyContinue
            }
        }
        catch {
            Write-Error "Failed to get registry value: $_"
            return $null
        }
    }
}

function Remove-OfflineRegistryValue {
    <#
    .SYNOPSIS
        Removes a registry value from an offline hive.
        
    .PARAMETER Hive
        The loaded hive.
        
    .PARAMETER Path
        The subkey path.
        
    .PARAMETER Name
        The value name to remove.
        
    .PARAMETER DeleteKey
        Delete the entire key instead of just a value.
        
    .EXAMPLE
        Remove-OfflineRegistryValue -Hive SOFTWARE -Path "Policies\Microsoft\Edge" -Name "SyncDisabled"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('SOFTWARE', 'SYSTEM', 'SECURITY', 'SAM', 'DEFAULT', 'NTUSER')]
        [string]$Hive,
        
        [Parameter(Mandatory = $true)]
        [string]$Path,
        
        [Parameter(Mandatory = $false)]
        [string]$Name,
        
        [Parameter(Mandatory = $false)]
        [switch]$DeleteKey
    )
    
    process {
        if (-not $script:LoadedHives.ContainsKey($Hive)) {
            throw "$Hive hive is not loaded"
        }
        
        $keyName = $script:LoadedHives[$Hive]
        $fullPath = "$keyName\$Path"
        
        try {
            if ($DeleteKey) {
                if ($PSCmdlet.ShouldProcess($fullPath, "Delete key")) {
                    $result = & reg.exe delete $fullPath /f 2>&1
                    Write-Host "✓ Registry key deleted: $Path" -ForegroundColor Green
                }
            }
            else {
                if ($PSCmdlet.ShouldProcess("$fullPath\$Name", "Delete value")) {
                    $result = & reg.exe delete $fullPath /v $Name /f 2>&1
                    Write-Host "✓ Registry value deleted: $Path\$Name" -ForegroundColor Green
                }
            }
            
            return [PSCustomObject]@{
                Success = $true
                Hive = $Hive
                Path = $Path
                Name = $Name
                DeletedKey = $DeleteKey.IsPresent
            }
        }
        catch {
            Write-Error "Failed to delete registry value: $_"
            return [PSCustomObject]@{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}

# Helper function to get loaded hives
function Get-LoadedHives {
    <#
    .SYNOPSIS
        Returns the currently loaded offline registry hives.
    #>
    [CmdletBinding()]
    param()
    
    return $script:LoadedHives.Clone()
}

# Export functions
Export-ModuleMember -Function @(
    'Mount-OfflineRegistry',
    'Dismount-OfflineRegistry',
    'Set-OfflineRegistryValue',
    'Get-OfflineRegistryValue',
    'Remove-OfflineRegistryValue',
    'Get-LoadedHives'
)
