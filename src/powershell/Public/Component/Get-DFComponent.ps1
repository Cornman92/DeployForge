function Get-DFComponent {
    <#
    .SYNOPSIS
        Lists Windows components in a mounted image.

    .DESCRIPTION
        The Get-DFComponent cmdlet retrieves a list of Windows components
        (packages, features, capabilities) from a mounted image.

    .PARAMETER MountPath
        Specifies the path where the image is mounted.

    .PARAMETER Type
        Specifies the type of components to retrieve. Valid values are:
        Package, Feature, Capability, All

    .PARAMETER Name
        Filter results by component name (supports wildcards).

    .EXAMPLE
        Get-DFComponent -MountPath "C:\Mount"

        Gets all components from the mounted image.

    .EXAMPLE
        Get-DFComponent -MountPath "C:\Mount" -Type Package

        Gets only packages from the mounted image.

    .EXAMPLE
        Get-DFComponent -MountPath "C:\Mount" -Name "*Edge*"

        Gets components with 'Edge' in the name.
    #>

    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [ValidateScript({Test-Path $_ -PathType Container})]
        [string]$MountPath,

        [Parameter(Mandatory = $false)]
        [ValidateSet('Package', 'Feature', 'Capability', 'All')]
        [string]$Type = 'All',

        [Parameter(Mandatory = $false)]
        [string]$Name = '*'
    )

    begin {
        Write-Verbose "Get-DFComponent: Retrieving components"

        if (-not (Test-Administrator)) {
            throw "This cmdlet requires administrative privileges."
        }
    }

    process {
        try {
            $FullPath = Resolve-Path -Path $MountPath
            Write-Verbose "Get-DFComponent: Mount path: $FullPath"

            $results = @()

            # Get packages
            if ($Type -eq 'Package' -or $Type -eq 'All') {
                Write-Verbose "Get-DFComponent: Getting packages..."
                $packages = Get-WindowsPackage -Path $FullPath |
                    Where-Object { $_.PackageName -like $Name }

                foreach ($pkg in $packages) {
                    $results += [PSCustomObject]@{
                        Type = 'Package'
                        Name = $pkg.PackageName
                        State = $pkg.PackageState
                        ReleaseType = $pkg.ReleaseType
                        InstallTime = $pkg.InstallTime
                    }
                }
            }

            # Get features
            if ($Type -eq 'Feature' -or $Type -eq 'All') {
                Write-Verbose "Get-DFComponent: Getting features..."
                $features = Get-WindowsOptionalFeature -Path $FullPath |
                    Where-Object { $_.FeatureName -like $Name }

                foreach ($feat in $features) {
                    $results += [PSCustomObject]@{
                        Type = 'Feature'
                        Name = $feat.FeatureName
                        State = $feat.State
                        Description = $feat.Description
                    }
                }
            }

            # Get capabilities
            if ($Type -eq 'Capability' -or $Type -eq 'All') {
                Write-Verbose "Get-DFComponent: Getting capabilities..."
                $capabilities = Get-WindowsCapability -Path $FullPath |
                    Where-Object { $_.Name -like $Name }

                foreach ($cap in $capabilities) {
                    $results += [PSCustomObject]@{
                        Type = 'Capability'
                        Name = $cap.Name
                        State = $cap.State
                        Description = $cap.Description
                    }
                }
            }

            return $results
        }
        catch {
            Write-Error "Failed to get components: $_"
            throw
        }
    }

    end {
        Write-Verbose "Get-DFComponent: Operation completed"
    }
}
