@{
    # Module manifest for DeployForge PowerShell Module

    # Script module or binary module file associated with this manifest
    RootModule = 'DeployForge.psm1'

    # Version number of this module
    ModuleVersion = '2.0.0'

    # Supported PSEditions
    CompatiblePSEditions = @('Desktop', 'Core')

    # ID used to uniquely identify this module
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'

    # Author of this module
    Author = 'DeployForge Team'

    # Company or vendor of this module
    CompanyName = 'DeployForge'

    # Copyright statement for this module
    Copyright = '(c) 2024-2025 DeployForge Team. All rights reserved.'

    # Description of the functionality provided by this module
    Description = 'Enterprise Windows Deployment Suite - Native PowerShell implementation for Windows image customization, optimization, and deployment automation.'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'

    # Modules that must be imported into the global environment prior to importing this module
    RequiredModules = @()

    # Assemblies that must be loaded prior to importing this module
    RequiredAssemblies = @()

    # Script files (.ps1) that are run in the caller's environment prior to importing this module
    ScriptsToProcess = @()

    # Type files (.ps1xml) to be loaded when importing this module
    TypesToProcess = @()

    # Format files (.ps1xml) to be loaded when importing this module
    FormatsToProcess = @()

    # Modules to import as nested modules of the module specified in RootModule
    NestedModules = @(
        'Core\Exceptions.ps1',
        'Core\BaseHandler.ps1',
        'Core\ImageManager.ps1',
        'Handlers\WimHandler.ps1',
        'Handlers\IsoHandler.ps1',
        'Handlers\EsdHandler.ps1',
        'Handlers\VhdHandler.ps1',
        'Handlers\PpkgHandler.ps1',
        'Features\Gaming.ps1',
        'Features\Debloat.ps1',
        'Features\Privacy.ps1',
        'Features\DevEnvironment.ps1',
        'Features\Browsers.ps1',
        'Features\Drivers.ps1',
        'Features\Registry.ps1',
        'Features\Unattend.ps1',
        'Features\WinPE.ps1',
        'Features\Templates.ps1',
        'Features\Batch.ps1',
        'Features\Languages.ps1',
        'Utilities\Logger.ps1',
        'Utilities\Progress.ps1',
        'Utilities\Validation.ps1'
    )

    # Functions to export from this module
    FunctionsToExport = @(
        # Image Management
        'Get-DFImageHandler',
        'Get-DFSupportedFormats',
        'Mount-DFImage',
        'Dismount-DFImage',
        'Get-DFImageInfo',
        'Get-DFImageFiles',
        'Add-DFImageFile',
        'Remove-DFImageFile',
        'Export-DFImageFile',
        
        # Gaming
        'Optimize-DFGaming',
        'Set-DFGamingProfile',
        'Install-DFGamingRuntimes',
        'Optimize-DFGamingServices',
        
        # Debloat
        'Remove-DFBloatware',
        'Disable-DFTelemetry',
        'Set-DFPrivacyTweaks',
        'Disable-DFCortana',
        
        # Privacy
        'Set-DFPrivacyLevel',
        'Block-DFTelemetryDomains',
        'Disable-DFAdvertisingId',
        'Set-DFPrivacyHardening',
        
        # Developer Environment
        'Install-DFDevEnvironment',
        'Set-DFDevProfile',
        'Enable-DFDeveloperMode',
        'Install-DFLanguages',
        'Install-DFIDEs',
        'Install-DFDevTools',
        'Install-DFCloudTools',
        'Set-DFGitConfig',
        'Enable-DFWSL2',
        
        # Browsers
        'Install-DFBrowsers',
        'Set-DFBrowserProfile',
        'Set-DFChromePolicy',
        'Set-DFFirefoxPolicy',
        'Set-DFEdgePolicy',
        'Set-DFDefaultBrowser',
        
        # Drivers
        'Add-DFDriver',
        'Get-DFDrivers',
        'Remove-DFDriver',
        
        # Registry
        'Set-DFRegistryValue',
        'Remove-DFRegistryValue',
        'Remove-DFRegistryKey',
        'Import-DFRegistryTweaks',
        'Export-DFRegistryHive',
        
        # Unattend
        'New-DFUnattendConfig',
        'New-DFBasicUnattend',
        'New-DFEnterpriseUnattend',
        'Save-DFUnattend',
        
        # WinPE
        'Mount-DFWinPE',
        'Dismount-DFWinPE',
        'Add-DFWinPEComponent',
        'Add-DFWinPEDriver',
        'Set-DFWinPEStartup',
        'New-DFWinPEISO',
        
        # Templates
        'Get-DFTemplate',
        'New-DFTemplate',
        'Save-DFTemplate',
        'Import-DFTemplate',
        'Export-DFTemplate',
        
        # Batch
        'Start-DFBatchOperation',
        'Get-DFBatchResult',
        'Export-DFBatchReport',
        
        # Languages
        'Add-DFLanguagePack',
        'Remove-DFLanguagePack',
        'Get-DFLanguages',
        'Set-DFDefaultLanguage',
        
        # Utilities
        'Write-DFLog',
        'Show-DFProgress',
        'Test-DFPath',
        'Test-DFAdministrator'
    )

    # Cmdlets to export from this module
    CmdletsToExport = @()

    # Variables to export from this module
    VariablesToExport = @()

    # Aliases to export from this module
    AliasesToExport = @(
        'dfmount',
        'dfdismount',
        'dfinfo',
        'dfoptimize',
        'dfdebloat'
    )

    # DSC resources to export from this module
    DscResourcesToExport = @()

    # List of all files packaged with this module
    FileList = @()

    # Private data to pass to the module specified in RootModule
    PrivateData = @{
        PSData = @{
            # Tags applied to this module
            Tags = @('Windows', 'Deployment', 'Image', 'WIM', 'DISM', 'Customization', 'Automation', 'Enterprise')

            # A URL to the license for this module
            LicenseUri = 'https://github.com/DeployForge/DeployForge-Native/blob/main/LICENSE'

            # A URL to the main website for this project
            ProjectUri = 'https://github.com/DeployForge/DeployForge-Native'

            # A URL to an icon representing this module
            IconUri = ''

            # ReleaseNotes of this module
            ReleaseNotes = @'
Version 2.0.0 - Windows Native Implementation
- Complete rewrite in PowerShell for native Windows integration
- Direct DISM integration without external dependencies
- WinUI 3 companion application
- Full feature parity with Python version
- 150+ customization features
- 6 image format support (WIM, ISO, ESD, VHD, VHDX, PPKG)
'@

            # Prerelease string of this module
            # Prerelease = ''

            # Flag to indicate whether the module requires explicit user acceptance for install/update/save
            RequireLicenseAcceptance = $false

            # External dependent modules of this module
            ExternalModuleDependencies = @()
        }
    }

    # HelpInfo URI of this module
    HelpInfoURI = 'https://github.com/DeployForge/DeployForge-Native/wiki'

    # Default prefix for commands exported from this module
    # DefaultCommandPrefix = 'DF'
}
