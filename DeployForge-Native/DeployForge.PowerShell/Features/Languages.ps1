#Requires -Version 5.1
# Multi-language support module for DeployForge

$script:LanguageCodes = @{
    "en-US" = "English (United States)"; "en-GB" = "English (United Kingdom)"
    "de-DE" = "German"; "fr-FR" = "French"; "es-ES" = "Spanish"
    "it-IT" = "Italian"; "ja-JP" = "Japanese"; "ko-KR" = "Korean"
    "zh-CN" = "Chinese (Simplified)"; "zh-TW" = "Chinese (Traditional)"
    "pt-BR" = "Portuguese (Brazil)"; "nl-NL" = "Dutch"; "ru-RU" = "Russian"
}

function Add-DFLanguagePack {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$LanguageCode, [string]$PackagePath)
    
    if ($PackagePath -and (Test-Path $PackagePath)) {
        & dism.exe /Image:"$MountPoint" /Add-Package /PackagePath:"$PackagePath" 2>&1 | Out-Null
        Write-DFLog "Language pack added: $LanguageCode" -Level Info
    }
    else {
        Write-DFLog "Language pack not found: $PackagePath" -Level Warning
    }
}

function Remove-DFLanguagePack {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$LanguageCode)
    
    & dism.exe /Image:"$MountPoint" /Remove-Package /PackageName:"Microsoft-Windows-Client-LanguagePack-Package~$LanguageCode" 2>&1 | Out-Null
    Write-DFLog "Language pack removed: $LanguageCode" -Level Info
}

function Get-DFLanguages {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint)
    
    $result = & dism.exe /Image:"$MountPoint" /Get-Intl 2>&1
    return $result
}

function Set-DFDefaultLanguage {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$MountPoint, [Parameter(Mandatory)][string]$LanguageCode)
    
    & dism.exe /Image:"$MountPoint" /Set-UILang:$LanguageCode 2>&1 | Out-Null
    & dism.exe /Image:"$MountPoint" /Set-SysLocale:$LanguageCode 2>&1 | Out-Null
    & dism.exe /Image:"$MountPoint" /Set-UserLocale:$LanguageCode 2>&1 | Out-Null
    & dism.exe /Image:"$MountPoint" /Set-InputLocale:$LanguageCode 2>&1 | Out-Null
    
    Write-DFLog "Default language set to: $LanguageCode" -Level Info
}

Write-Verbose "Loaded DeployForge Languages module"
