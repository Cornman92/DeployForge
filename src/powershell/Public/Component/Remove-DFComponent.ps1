function Remove-DFComponent {
    <#
    .SYNOPSIS
        Removes Windows components from a mounted image.

    .DESCRIPTION
        The Remove-DFComponent cmdlet removes packages, features, or capabilities
        from a mounted Windows image.

    .PARAMETER MountPath
        Specifies the path where the image is mounted.

    .PARAMETER Name
        Specifies the name of the component to remove.

    .PARAMETER Type
        Specifies the type of component. Valid values: Package, Feature, Capability

    .EXAMPLE
        Remove-DFComponent -MountPath "C:\Mount" -Name "Microsoft-Windows-InternetExplorer" -Type Package

        Removes Internet Explorer package.

    .EXAMPLE
        Remove-DFComponent -MountPath "C:\Mount" -Name "TelnetClient" -Type Feature

        Removes Telnet Client feature.
    #>

    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({Test-Path $_ -PathType Container})]
        [string]$MountPath,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [ValidateSet('Package', 'Feature', 'Capability')]
        [string]$Type
    )

    begin {
        Write-Verbose "Remove-DFComponent: Starting component removal"

        if (-not (Test-Administrator)) {
            throw "This cmdlet requires administrative privileges."
        }
    }

    process {
        try {
            $FullPath = Resolve-Path -Path $MountPath

            if ($PSCmdlet.ShouldProcess($Name, "Remove $Type")) {
                Write-Verbose "Remove-DFComponent: Removing $Type '$Name' from $FullPath"

                switch ($Type) {
                    'Package' {
                        Remove-WindowsPackage -Path $FullPath -PackageName $Name -ErrorAction Stop
                    }
                    'Feature' {
                        Disable-WindowsOptionalFeature -Path $FullPath -FeatureName $Name -Remove -ErrorAction Stop
                    }
                    'Capability' {
                        Remove-WindowsCapability -Path $FullPath -Name $Name -ErrorAction Stop
                    }
                }

                Write-Host "Successfully removed $Type: $Name" -ForegroundColor Green

                return [PSCustomObject]@{
                    Success = $true
                    Type = $Type
                    Name = $Name
                    MountPath = $FullPath
                    Timestamp = Get-Date
                }
            }
        }
        catch {
            Write-Error "Failed to remove component: $_"
            throw
        }
    }

    end {
        Write-Verbose "Remove-DFComponent: Operation completed"
    }
}
