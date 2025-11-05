#
# Module manifest for module 'DeployForge'
#

@{
    # Script module or binary module file associated with this manifest.
    RootModule = 'DeployForge.psm1'

    # Version number of this module.
    ModuleVersion = '1.0.0'

    # ID used to uniquely identify this module
    GUID = 'a1b2c3d4-e5f6-4789-0abc-def123456789'

    # Author of this module
    Author = 'DeployForge Team'

    # Company or vendor of this module
    CompanyName = 'DeployForge'

    # Copyright statement for this module
    Copyright = '(c) 2025 DeployForge Team. All rights reserved.'

    # Description of the functionality provided by this module
    Description = 'PowerShell module for DeployForge - Windows Image Configurator and Deployment Tool'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '7.4'

    # Functions to export from this module
    FunctionsToExport = @(
        # Image Operations
        'Mount-DFImage',
        'Dismount-DFImage',
        'Get-DFImageInfo',
        'Get-DFImageSession',
        'Convert-DFImage',
        'Optimize-DFImage',
        'Test-DFImage',

        # Component Operations
        'Get-DFComponent',
        'Add-DFComponent',
        'Remove-DFComponent',
        'Get-DFComponentDependency',

        # Registry Operations
        'Get-DFRegistryTweak',
        'Set-DFRegistryTweak',
        'Remove-DFRegistryTweak',
        'Export-DFRegistryTweak',
        'Import-DFRegistryTweak',

        # Deployment Operations
        'New-DFBootableUSB',
        'New-DFAutounattend',
        'Test-DFAutounattend',
        'New-DFDeploymentPackage',

        # Workflow Operations
        'Get-DFWorkflow',
        'New-DFWorkflow',
        'Start-DFWorkflow',
        'Stop-DFWorkflow',
        'Get-DFWorkflowExecution',

        # Testing Operations
        'Start-DFImageTest',
        'Get-DFTestResult',
        'New-DFTestReport'
    )

    # Cmdlets to export from this module
    CmdletsToExport = @()

    # Variables to export from this module
    VariablesToExport = @()

    # Aliases to export from this module
    AliasesToExport = @(
        'Mount-WinImage',
        'Dismount-WinImage'
    )

    # Private data to pass to the module
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @('Windows', 'Deployment', 'Image', 'DISM', 'Automation', 'WIM', 'ISO')

            # A URL to the license for this module.
            LicenseUri = 'https://github.com/Cornman92/DeployForge/blob/main/LICENSE'

            # A URL to the main website for this project.
            ProjectUri = 'https://github.com/Cornman92/DeployForge'

            # A URL to an icon representing this module.
            # IconUri = ''

            # ReleaseNotes of this module
            ReleaseNotes = 'Initial alpha release of DeployForge PowerShell module'
        }
    }
}
