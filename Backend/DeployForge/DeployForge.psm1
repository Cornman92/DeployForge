# DeployForge Root Module

# Import Private Core Logic
. $PSScriptRoot/Private/Core/ImageContext.ps1
. $PSScriptRoot/Private/Handlers/WimHandler.ps1

# Import Feature Modules
. $PSScriptRoot/Private/Features/Gaming.ps1
. $PSScriptRoot/Private/Features/Privacy.ps1
. $PSScriptRoot/Private/Features/Devenv.ps1
. $PSScriptRoot/Private/Features/Apps.ps1
. $PSScriptRoot/Private/Features/UI.ps1

# Import Public Functions
. $PSScriptRoot/Public/Mount-DeployImage.ps1
. $PSScriptRoot/Public/Dismount-DeployImage.ps1
. $PSScriptRoot/Public/Get-DeployImageInfo.ps1
. $PSScriptRoot/Public/New-ImageBuild.ps1
