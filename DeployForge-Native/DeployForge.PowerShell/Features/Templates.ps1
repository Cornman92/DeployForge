#Requires -Version 5.1
# Template system module for DeployForge

function Get-DFTemplate {
    [CmdletBinding()]
    param([string]$Name, [string]$Path = (Join-Path $env:APPDATA "DeployForge\Templates"))
    
    if ($Name) { return Get-Content (Join-Path $Path "$Name.json") | ConvertFrom-Json }
    return Get-ChildItem $Path -Filter "*.json" | ForEach-Object { Get-Content $_.FullName | ConvertFrom-Json }
}

function New-DFTemplate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name, [string]$Description, [string]$Author,
        [hashtable]$Features = @{}, [string[]]$RemovePackages = @(), [hashtable[]]$Registry = @(), [string[]]$Drivers = @()
    )
    return @{ Name = $Name; Description = $Description; Author = $Author; Version = "1.0"; Features = $Features; RemovePackages = $RemovePackages; Registry = $Registry; Drivers = $Drivers }
}

function Save-DFTemplate {
    [CmdletBinding()]
    param([Parameter(Mandatory)][hashtable]$Template, [string]$Path = (Join-Path $env:APPDATA "DeployForge\Templates"))
    
    New-Item -ItemType Directory -Path $Path -Force -ErrorAction SilentlyContinue | Out-Null
    $filePath = Join-Path $Path "$($Template.Name).json"
    $Template | ConvertTo-Json -Depth 10 | Set-Content $filePath -Encoding UTF8
    Write-DFLog "Template saved: $filePath" -Level Info
}

function Import-DFTemplate {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$FilePath)
    return Get-Content $FilePath | ConvertFrom-Json
}

function Export-DFTemplate {
    [CmdletBinding()]
    param([Parameter(Mandatory)][hashtable]$Template, [Parameter(Mandatory)][string]$FilePath)
    $Template | ConvertTo-Json -Depth 10 | Set-Content $FilePath -Encoding UTF8
}

# Predefined templates
$script:GamingTemplate = New-DFTemplate -Name "Gaming" -Description "Gaming optimized" -Features @{ GameMode = $true; Debloat = $true }
$script:EnterpriseTemplate = New-DFTemplate -Name "Enterprise" -Description "Enterprise deployment" -Features @{ BitLocker = $true; Telemetry = $false }

Write-Verbose "Loaded DeployForge Templates module"
