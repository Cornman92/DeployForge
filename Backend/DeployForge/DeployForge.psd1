@{
    RootModule = 'DeployForge.psm1'
    ModuleVersion = '2.0.0'
    GUID = '12345678-1234-1234-1234-123456789012'
    Author = 'DeployForge Team'
    CompanyName = 'DeployForge'
    Copyright = '(c) 2025 DeployForge. All rights reserved.'
    Description = 'Windows Native Deployment Automation Framework'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'New-ImageBuild',
        'Mount-DeployImage',
        'Dismount-DeployImage',
        'Get-DeployImageInfo',
        'Enable-GamingOptimizations',
        'Enable-PrivacyHardening',
        'Install-DevEnvironment',
        'Install-Applications',
        'Set-WindowsUI'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
