@{
    # Module manifest for DeployForge PowerShell Backend
    
    # Script module or binary module file associated with this manifest.
    RootModule = 'DeployForge.psm1'
    
    # Version number of this module.
    ModuleVersion = '2.0.0'
    
    # Supported PSEditions
    CompatiblePSEditions = @('Core', 'Desktop')
    
    # ID used to uniquely identify this module
    GUID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    
    # Author of this module
    Author = 'DeployForge Team'
    
    # Company or vendor of this module
    CompanyName = 'DeployForge'
    
    # Copyright statement for this module
    Copyright = '(c) 2024 DeployForge. All rights reserved.'
    
    # Description of the functionality provided by this module
    Description = 'DeployForge PowerShell Backend - Windows Deployment Image Management and Customization'
    
    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '5.1'
    
    # Modules that must be imported into the global environment prior to importing this module
    RequiredModules = @()
    
    # Assemblies that must be loaded prior to importing this module
    RequiredAssemblies = @()
    
    # Script files (.ps1) that are run in the caller's environment prior to importing this module.
    ScriptsToProcess = @()
    
    # Type files (.ps1xml) to be loaded when importing this module
    TypesToProcess = @()
    
    # Format files (.ps1xml) to be loaded when importing this module
    FormatsToProcess = @()
    
    # Modules to import as nested modules of the module specified in RootModule/ModuleToProcess
    NestedModules = @(
        'Core\ImageManager.psm1',
        'Core\RegistryManager.psm1',
        'Core\PartitionManager.psm1',
        'Core\Exceptions.psm1',
        'Features\Gaming.psm1',
        'Features\DevEnvironment.psm1',
        'Features\Debloat.psm1',
        'Features\Browsers.psm1',
        'Features\Privacy.psm1',
        'Features\UICustomization.psm1',
        'Features\Backup.psm1',
        'Features\Drivers.psm1',
        'Features\Updates.psm1',
        'Features\Unattend.psm1',
        'Utilities\Logging.psm1',
        'Utilities\Progress.psm1',
        'Utilities\Validation.psm1'
    )
    
    # Functions to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no functions to export.
    FunctionsToExport = @(
        # Core - Image Management
        'Mount-DeployForgeImage',
        'Dismount-DeployForgeImage',
        'Get-DeployForgeImageInfo',
        'Get-DeployForgeImageFiles',
        'Add-DeployForgeFile',
        'Remove-DeployForgeFile',
        'Copy-DeployForgeFile',
        
        # Core - Registry
        'Mount-OfflineRegistry',
        'Dismount-OfflineRegistry',
        'Set-OfflineRegistryValue',
        'Get-OfflineRegistryValue',
        'Remove-OfflineRegistryValue',
        
        # Core - Partitions
        'Get-PartitionLayout',
        'New-UEFIPartitionLayout',
        'Set-PartitionLayout',
        'Export-PartitionLayout',
        'Import-PartitionLayout',
        
        # Features - Gaming
        'Set-GamingProfile',
        'Enable-GameMode',
        'Disable-GameBar',
        'Optimize-NetworkLatency',
        'Install-GamingRuntimes',
        'Optimize-GamingServices',
        
        # Features - DevEnvironment
        'Set-DeveloperMode',
        'Install-DevelopmentTools',
        'Install-ProgrammingLanguages',
        'Install-IDEs',
        'Enable-WSL2',
        'Set-GitConfiguration',
        'Install-CloudTools',
        'Install-DatabaseClients',
        
        # Features - Debloat
        'Remove-Bloatware',
        'Get-BloatwareList',
        'Disable-Telemetry',
        'Set-PrivacySettings',
        'Disable-Cortana',
        'Disable-DeliveryOptimization',
        
        # Features - Browsers
        'Install-Browsers',
        'Set-BrowserProfile',
        'Set-ChromePolicies',
        'Set-FirefoxPolicies',
        'Set-EdgePolicies',
        'Set-DefaultBrowser',
        
        # Features - Privacy
        'Set-PrivacyLevel',
        'Disable-AdvertisingId',
        'Disable-LocationTracking',
        'Disable-DiagnosticData',
        'Set-AppPermissions',
        
        # Features - UI Customization
        'Set-UIProfile',
        'Set-TaskbarSettings',
        'Set-StartMenuSettings',
        'Set-ExplorerSettings',
        'Set-ThemeSettings',
        
        # Features - Backup
        'Set-BackupProfile',
        'Enable-SystemRestore',
        'Configure-FileHistory',
        'Enable-VSS',
        
        # Features - Drivers
        'Add-Drivers',
        'Get-InstalledDrivers',
        'Remove-Driver',
        'Export-DriverList',
        
        # Features - Updates
        'Set-WindowsUpdatePolicy',
        'Disable-AutoUpdate',
        'Enable-AutoUpdate',
        'Set-UpdateDefer',
        
        # Features - Unattend
        'New-UnattendFile',
        'Set-UnattendUserAccount',
        'Set-UnattendRegional',
        'Set-UnattendNetwork',
        'Export-UnattendFile',
        
        # Utilities
        'Write-DeployForgeLog',
        'Get-DeployForgeLog',
        'New-DeployForgeProgress',
        'Update-DeployForgeProgress',
        'Complete-DeployForgeProgress',
        'Test-DeployForgeImage',
        'Test-AdminPrivileges'
    )
    
    # Cmdlets to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no cmdlets to export.
    CmdletsToExport = @()
    
    # Variables to export from this module
    VariablesToExport = @()
    
    # Aliases to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no aliases to export.
    AliasesToExport = @()
    
    # Private data to pass to the module specified in RootModule/ModuleToProcess.
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Deployment', 'Image', 'WIM', 'DISM', 'Customization', 'Enterprise')
            LicenseUri = 'https://github.com/DeployForge/DeployForge/blob/main/LICENSE'
            ProjectUri = 'https://github.com/DeployForge/DeployForge'
            IconUri = ''
            ReleaseNotes = 'Windows Native version 2.0.0 - Complete PowerShell backend'
        }
    }
    
    # Default prefix for commands exported from this module. Override the default prefix using Import-Module -Prefix.
    DefaultCommandPrefix = ''
}
