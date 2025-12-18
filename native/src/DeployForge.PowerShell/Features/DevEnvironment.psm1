#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    DeployForge Developer Environment Module
.DESCRIPTION
    Functions for configuring developer environments in Windows images.
    Includes IDE installation, language runtimes, and developer tools.
#>

# Development Profiles
$Script:DevelopmentProfiles = @{
    General = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $false
        Languages = @('Python', 'NodeJS')
        IDEs = @('VSCode')
        Tools = @('Git', 'PowerShell7')
    }
    WebDevelopment = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $true
        Languages = @('NodeJS', 'Python')
        IDEs = @('VSCode')
        Tools = @('Git', 'Docker', 'PowerShell7')
        Frameworks = @('React', 'Vue', 'Angular')
    }
    DotNet = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $false
        Languages = @('DotNet')
        IDEs = @('VisualStudio', 'VSCode', 'Rider')
        Tools = @('Git', 'Docker', 'SQLServer')
    }
    Python = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $true
        Languages = @('Python', 'Anaconda')
        IDEs = @('VSCode', 'PyCharm')
        Tools = @('Git', 'Docker')
    }
    Java = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $false
        Languages = @('Java', 'Kotlin')
        IDEs = @('IntelliJIDEA', 'Eclipse')
        Tools = @('Git', 'Maven', 'Gradle')
    }
    DataScience = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $true
        Languages = @('Python', 'R', 'Julia')
        IDEs = @('VSCode', 'JupyterLab')
        Tools = @('Git', 'Anaconda', 'Docker')
    }
    DevOps = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $true
        Languages = @('Python', 'Go')
        IDEs = @('VSCode')
        Tools = @('Git', 'Docker', 'Kubernetes', 'Terraform', 'Ansible')
    }
    Mobile = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $false
        Languages = @('Kotlin', 'Swift', 'DotNet')
        IDEs = @('AndroidStudio', 'VisualStudio')
        Tools = @('Git', 'ADB')
    }
    GameDev = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $false
        Languages = @('CSharp', 'CPlusPlus')
        IDEs = @('VisualStudio', 'Rider')
        Tools = @('Git', 'Unity', 'Unreal')
    }
    Embedded = @{
        EnableDeveloperMode = $true
        EnableWSL2 = $true
        Languages = @('C', 'CPlusPlus', 'Rust')
        IDEs = @('VSCode', 'PlatformIO')
        Tools = @('Git', 'Make', 'CMake')
    }
}

function Set-DeveloperEnvironment {
    <#
    .SYNOPSIS
        Configures developer environment in mounted image.
    .PARAMETER MountPath
        Path to mounted Windows image.
    .PARAMETER Profile
        Development profile to apply.
    .PARAMETER EnableDeveloperMode
        Enable Windows Developer Mode.
    .PARAMETER EnableWSL2
        Enable Windows Subsystem for Linux 2.
    .PARAMETER Languages
        Programming languages to install.
    .PARAMETER IDEs
        IDEs to install.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath,
        
        [Parameter()]
        [ValidateSet('General', 'WebDevelopment', 'DotNet', 'Python', 'Java', 
                     'DataScience', 'DevOps', 'Mobile', 'GameDev', 'Embedded')]
        [string]$Profile = 'General',
        
        [Parameter()]
        [bool]$EnableDeveloperMode = $true,
        
        [Parameter()]
        [bool]$EnableWSL2 = $false,
        
        [Parameter()]
        [string[]]$Languages,
        
        [Parameter()]
        [string[]]$IDEs
    )
    
    begin {
        Write-Verbose "Configuring $Profile development environment"
        $profileConfig = $Script:DevelopmentProfiles[$Profile]
    }
    
    process {
        try {
            # Apply profile defaults if not specified
            if (-not $Languages) {
                $Languages = $profileConfig.Languages
            }
            if (-not $IDEs) {
                $IDEs = $profileConfig.IDEs
            }
            
            # Enable Developer Mode
            if ($EnableDeveloperMode) {
                Enable-DeveloperMode -MountPath $MountPath
            }
            
            # Enable WSL 2
            if ($EnableWSL2 -or $profileConfig.EnableWSL2) {
                Enable-WSL2 -MountPath $MountPath
            }
            
            # Create first-boot installation script
            $installScript = New-DeveloperInstallScript -Languages $Languages -IDEs $IDEs -Tools $profileConfig.Tools
            
            $scriptPath = Join-Path $MountPath "Windows\Setup\Scripts"
            if (-not (Test-Path $scriptPath)) {
                New-Item -Path $scriptPath -ItemType Directory -Force | Out-Null
            }
            
            $installScript | Out-File -FilePath (Join-Path $scriptPath "InstallDevTools.ps1") -Encoding UTF8 -Force
            
            # Configure Git
            Set-GitConfiguration -MountPath $MountPath
            
            Write-Verbose "Developer environment configured successfully"
            
            return @{
                Success = $true
                Profile = $Profile
                DeveloperMode = $EnableDeveloperMode
                WSL2 = $EnableWSL2
                Languages = $Languages
                IDEs = $IDEs
            }
        }
        catch {
            Write-Error "Failed to configure developer environment: $_"
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}

function Enable-DeveloperMode {
    <#
    .SYNOPSIS
        Enables Windows Developer Mode in mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Enabling Developer Mode"
    
    # Mount SOFTWARE hive
    $hivePath = Join-Path $MountPath "Windows\System32\config\SOFTWARE"
    $tempKey = "HKLM\OFFLINE_SW_DEV"
    
    try {
        reg load $tempKey $hivePath 2>$null
        
        # Enable Developer Mode
        $regPath = "$tempKey\Microsoft\Windows\CurrentVersion\AppModelUnlock"
        reg add $regPath /v AllowDevelopmentWithoutDevLicense /t REG_DWORD /d 1 /f | Out-Null
        reg add $regPath /v AllowAllTrustedApps /t REG_DWORD /d 1 /f | Out-Null
        
        # Enable PowerShell execution policy
        $psPath = "$tempKey\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell"
        reg add $psPath /v ExecutionPolicy /t REG_SZ /d "RemoteSigned" /f | Out-Null
        
        Write-Verbose "Developer Mode enabled"
    }
    finally {
        [GC]::Collect()
        Start-Sleep -Milliseconds 500
        reg unload $tempKey 2>$null
    }
}

function Enable-WSL2 {
    <#
    .SYNOPSIS
        Enables WSL 2 in mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Enabling WSL 2 features"
    
    try {
        # Enable required Windows features
        $features = @(
            'Microsoft-Windows-Subsystem-Linux',
            'VirtualMachinePlatform'
        )
        
        foreach ($feature in $features) {
            dism /Image:"$MountPath" /Enable-Feature /FeatureName:$feature /All /NoRestart 2>$null
        }
        
        # Create first-boot script to set WSL 2 as default
        $wslScript = @"
# Set WSL 2 as default
wsl --set-default-version 2

# Install Ubuntu if not present
wsl --install -d Ubuntu --no-launch
"@
        
        $scriptPath = Join-Path $MountPath "Windows\Setup\Scripts\ConfigureWSL.ps1"
        $wslScript | Out-File -FilePath $scriptPath -Encoding UTF8 -Force
        
        Write-Verbose "WSL 2 features enabled"
    }
    catch {
        Write-Warning "Failed to enable WSL 2: $_"
    }
}

function New-DeveloperInstallScript {
    <#
    .SYNOPSIS
        Creates a PowerShell script to install developer tools at first boot.
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string[]]$Languages,
        
        [Parameter()]
        [string[]]$IDEs,
        
        [Parameter()]
        [string[]]$Tools
    )
    
    $script = @"
# DeployForge Developer Tools Installation Script
# This script runs at first boot to install development tools

`$ErrorActionPreference = 'SilentlyContinue'

# Check for winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "Waiting for Windows Package Manager..."
    Start-Sleep -Seconds 30
}

# Install Languages
"@
    
    $languagePackages = @{
        'Python' = 'Python.Python.3.12'
        'NodeJS' = 'OpenJS.NodeJS.LTS'
        'DotNet' = 'Microsoft.DotNet.SDK.8'
        'Java' = 'Microsoft.OpenJDK.21'
        'Go' = 'GoLang.Go'
        'Rust' = 'Rustlang.Rust.MSVC'
        'Ruby' = 'RubyInstallerTeam.Ruby.3.2'
        'PHP' = 'PHP.PHP'
        'Kotlin' = 'JetBrains.Kotlin.Compiler'
        'R' = 'RProject.R'
        'Julia' = 'Julialang.Julia'
        'Anaconda' = 'Anaconda.Anaconda3'
    }
    
    foreach ($lang in $Languages) {
        if ($languagePackages.ContainsKey($lang)) {
            $script += "winget install --id $($languagePackages[$lang]) --silent --accept-package-agreements`n"
        }
    }
    
    $script += "`n# Install IDEs`n"
    
    $idePackages = @{
        'VSCode' = 'Microsoft.VisualStudioCode'
        'VisualStudio' = 'Microsoft.VisualStudio.2022.Community'
        'Rider' = 'JetBrains.Rider'
        'PyCharm' = 'JetBrains.PyCharm.Community'
        'IntelliJIDEA' = 'JetBrains.IntelliJIDEA.Community'
        'WebStorm' = 'JetBrains.WebStorm'
        'AndroidStudio' = 'Google.AndroidStudio'
        'Eclipse' = 'Eclipse.Temurin.21.JDK'
        'Sublime' = 'SublimeHQ.SublimeText.4'
        'Atom' = 'GitHub.Atom'
        'Notepad++' = 'Notepad++.Notepad++'
    }
    
    foreach ($ide in $IDEs) {
        if ($idePackages.ContainsKey($ide)) {
            $script += "winget install --id $($idePackages[$ide]) --silent --accept-package-agreements`n"
        }
    }
    
    $script += "`n# Install Tools`n"
    
    $toolPackages = @{
        'Git' = 'Git.Git'
        'Docker' = 'Docker.DockerDesktop'
        'PowerShell7' = 'Microsoft.PowerShell'
        'WindowsTerminal' = 'Microsoft.WindowsTerminal'
        'Postman' = 'Postman.Postman'
        'Insomnia' = 'Insomnia.Insomnia'
        'HeidiSQL' = 'HeidiSQL.HeidiSQL'
        'DBeaver' = 'dbeaver.dbeaver'
    }
    
    foreach ($tool in $Tools) {
        if ($toolPackages.ContainsKey($tool)) {
            $script += "winget install --id $($toolPackages[$tool]) --silent --accept-package-agreements`n"
        }
    }
    
    $script += @"

# Refresh environment variables
`$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Developer tools installation complete!"
"@
    
    return $script
}

function Set-GitConfiguration {
    <#
    .SYNOPSIS
        Sets default Git configuration in mounted image.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$MountPath
    )
    
    Write-Verbose "Configuring Git defaults"
    
    # Create default .gitconfig template
    $gitConfig = @"
[core]
    autocrlf = true
    safecrlf = warn
    editor = code --wait
[init]
    defaultBranch = main
[pull]
    rebase = false
[push]
    default = current
[credential]
    helper = manager
[diff]
    tool = vscode
[difftool "vscode"]
    cmd = code --wait --diff `$LOCAL `$REMOTE
[merge]
    tool = vscode
[mergetool "vscode"]
    cmd = code --wait `$MERGED
"@
    
    # Store as template in Public Documents
    $templatePath = Join-Path $MountPath "Users\Public\Documents"
    if (-not (Test-Path $templatePath)) {
        New-Item -Path $templatePath -ItemType Directory -Force | Out-Null
    }
    
    $gitConfig | Out-File -FilePath (Join-Path $templatePath ".gitconfig.template") -Encoding UTF8 -Force
    
    Write-Verbose "Git configuration template created"
}

# Export functions
Export-ModuleMember -Function @(
    'Set-DeveloperEnvironment',
    'Enable-DeveloperMode',
    'Enable-WSL2',
    'Set-GitConfiguration'
)
