# DeployForge PowerShell Module
# Main module file

#Requires -Version 7.4
#Requires -RunAsAdministrator

# Module variables
$script:ModuleRoot = $PSScriptRoot
$script:ApiBaseUrl = "http://localhost:5000/api"
$script:ModuleVersion = "1.0.0-alpha"

# Import public functions
$PublicFunctions = @(
    Get-ChildItem -Path "$PSScriptRoot\Public\*.ps1" -Recurse -ErrorAction SilentlyContinue
)

# Import private functions
$PrivateFunctions = @(
    Get-ChildItem -Path "$PSScriptRoot\Private\*.ps1" -Recurse -ErrorAction SilentlyContinue
)

# Dot source the functions
foreach ($Function in @($PublicFunctions + $PrivateFunctions)) {
    try {
        . $Function.FullName
    }
    catch {
        Write-Error -Message "Failed to import function $($Function.FullName): $_"
    }
}

# Export public functions
Export-ModuleMember -Function $PublicFunctions.BaseName

# Module initialization
Write-Verbose "DeployForge PowerShell Module v$ModuleVersion loaded"
Write-Verbose "Module Root: $ModuleRoot"

# Check for required modules
$RequiredModules = @('DISM')
foreach ($Module in $RequiredModules) {
    if (-not (Get-Module -Name $Module -ListAvailable)) {
        Write-Warning "Required module '$Module' is not installed. Some functionality may be limited."
    }
}

# Set strict mode for better error handling
Set-StrictMode -Version Latest
