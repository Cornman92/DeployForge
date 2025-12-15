#Requires -Version 5.1
# Unattend.xml generation module for DeployForge

function New-DFUnattendConfig {
    [CmdletBinding()]
    param(
        [string]$ProductKey, [string]$ComputerName, [string]$TimeZone = "Pacific Standard Time",
        [string]$Organization, [string]$Owner, [string]$Username = "Admin", [string]$Password,
        [string]$Domain, [string]$Workgroup = "WORKGROUP", [switch]$SkipOOBE
    )
    
    return @{
        ProductKey = $ProductKey; ComputerName = $ComputerName; TimeZone = $TimeZone
        Organization = $Organization; Owner = $Owner; Username = $Username; Password = $Password
        Domain = $Domain; Workgroup = $Workgroup; SkipOOBE = $SkipOOBE.IsPresent
    }
}

function New-DFBasicUnattend {
    [CmdletBinding()]
    param([string]$Username = "Admin", [string]$Password, [string]$ComputerName = "DESKTOP-PC", [string]$TimeZone = "Pacific Standard Time")
    return New-DFUnattendConfig -Username $Username -Password $Password -ComputerName $ComputerName -TimeZone $TimeZone -SkipOOBE
}

function New-DFEnterpriseUnattend {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Domain, [string]$DomainUsername, [string]$DomainPassword, [string]$ProductKey, [string]$ComputerName)
    return New-DFUnattendConfig -Domain $Domain -ProductKey $ProductKey -ComputerName $ComputerName -SkipOOBE
}

function Save-DFUnattend {
    [CmdletBinding()]
    param([Parameter(Mandatory)][hashtable]$Config, [Parameter(Mandatory)][string]$OutputPath)
    
    $xml = @"
<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
    <settings pass="oobeSystem">
        <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <OOBE>
                <HideEULAPage>true</HideEULAPage>
                <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
                <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
                <ProtectYourPC>3</ProtectYourPC>
            </OOBE>
            <TimeZone>$($Config.TimeZone)</TimeZone>
            $(if($Config.ComputerName){"<ComputerName>$($Config.ComputerName)</ComputerName>"})
            <UserAccounts>
                <LocalAccounts>
                    <LocalAccount wcm:action="add">
                        <Name>$($Config.Username)</Name>
                        <Group>Administrators</Group>
                        <Password><Value>$($Config.Password)</Value><PlainText>true</PlainText></Password>
                    </LocalAccount>
                </LocalAccounts>
            </UserAccounts>
        </component>
    </settings>
</unattend>
"@
    
    Set-Content -Path $OutputPath -Value $xml -Encoding UTF8
    Write-DFLog "Unattend.xml saved to $OutputPath" -Level Info
}

Write-Verbose "Loaded DeployForge Unattend module"
