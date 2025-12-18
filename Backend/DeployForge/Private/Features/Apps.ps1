function Install-Applications {
    param (
        [string]$MountDir,
        [string[]]$AppList
    )

    Write-Verbose "Configuring Application Installers"

    $ScriptsDir = Join-Path $MountDir "Windows\Setup\Scripts"
    if (!(Test-Path $ScriptsDir)) { New-Item -Path $ScriptsDir -ItemType Directory -Force | Out-Null }

    $ScriptContent = @"
# WinGet Application Installer
`$Apps = @(
    $( $AppList | ForEach-Object { "'$_'" } ) -join ","
)

foreach (`$App in `$Apps) {
    Write-Host "Installing `$App..."
    winget install --id `$App --silent --accept-package-agreements --accept-source-agreements
}
"@

    Set-Content -Path (Join-Path $ScriptsDir "InstallApps.ps1") -Value $ScriptContent
    Add-Content -Path (Join-Path $ScriptsDir "SetupComplete.cmd") -Value "`npowershell -ExecutionPolicy Bypass -File InstallApps.ps1"
}
