function Install-DevEnvironment {
    param (
        [string]$MountDir,
        [string]$Profile
    )

    Write-Verbose "Configuring Developer Environment: $Profile"

    $ScriptsDir = Join-Path $MountDir "Windows\Setup\Scripts"
    if (!(Test-Path $ScriptsDir)) { New-Item -Path $ScriptsDir -ItemType Directory -Force | Out-Null }

    $Packages = @("Microsoft.WindowsTerminal", "Git.Git")

    switch ($Profile) {
        "Web" {
            $Packages += "Microsoft.VisualStudioCode"
            $Packages += "OpenJS.NodeJS"
            $Packages += "Python.Python.3.11"
        }
        "DataScience" {
            $Packages += "Microsoft.VisualStudioCode"
            $Packages += "Python.Python.3.11"
            $Packages += "Julia.Julia"
        }
        "FullStack" {
            $Packages += "Microsoft.VisualStudioCode"
            $Packages += "OpenJS.NodeJS"
            $Packages += "Python.Python.3.11"
            $Packages += "Docker.DockerDesktop"
        }
    }

    $ScriptContent = @"
`$Packages = @(
    $( $Packages | ForEach-Object { "'$_'" } ) -join ","
)

foreach (`$Pkg in `$Packages) {
    winget install --id `$Pkg --silent --accept-package-agreements --accept-source-agreements
}
"@

    Set-Content -Path (Join-Path $ScriptsDir "InstallDevEnv.ps1") -Value $ScriptContent
    Add-Content -Path (Join-Path $ScriptsDir "SetupComplete.cmd") -Value "`npowershell -ExecutionPolicy Bypass -File InstallDevEnv.ps1"
    
    # Enable WSL
    dism /Image:$MountDir /Enable-Feature /FeatureName:Microsoft-Windows-Subsystem-Linux /All /NoRestart
    dism /Image:$MountDir /Enable-Feature /FeatureName:VirtualMachinePlatform /All /NoRestart
}
