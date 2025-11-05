function Get-DFImageInfo {
    <#
    .SYNOPSIS
        Gets information about a Windows image file.

    .DESCRIPTION
        The Get-DFImageInfo cmdlet retrieves detailed information about a Windows
        image file including editions, sizes, and build information.

    .PARAMETER Path
        Specifies the path to the image file.

    .PARAMETER Index
        Specifies the index of the image to retrieve info for. If not specified,
        information for all images in the file is returned.

    .EXAMPLE
        Get-DFImageInfo -Path "C:\Images\install.wim"

        Gets information for all images in the WIM file.

    .EXAMPLE
        Get-DFImageInfo -Path "C:\Images\install.wim" -Index 1

        Gets information for the first image in the WIM file.

    .OUTPUTS
        PSCustomObject[] with image information.
    #>

    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true)]
        [ValidateScript({Test-Path $_ -PathType Leaf})]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [ValidateRange(1, [int]::MaxValue)]
        [int]$Index
    )

    begin {
        Write-Verbose "Get-DFImageInfo: Starting image info retrieval"
    }

    process {
        try {
            $FullPath = Resolve-Path -Path $Path
            Write-Verbose "Get-DFImageInfo: Image path: $FullPath"

            $Format = Get-ImageFormat -Path $FullPath
            Write-Verbose "Get-DFImageInfo: Format: $Format"

            if ($Format -eq 'WIM' -or $Format -eq 'ESD') {
                $images = Get-WindowsImage -ImagePath $FullPath

                if ($Index) {
                    $images = $images | Where-Object { $_.ImageIndex -eq $Index }
                }

                foreach ($img in $images) {
                    [PSCustomObject]@{
                        Path = $FullPath
                        Format = $Format
                        Index = $img.ImageIndex
                        Name = $img.ImageName
                        Description = $img.ImageDescription
                        Size = $img.ImageSize
                        Architecture = $img.Architecture
                        Version = $img.Version
                        SPBuild = $img.SPBuild
                        SPLevel = $img.SPLevel
                        Edition = $img.EditionId
                        InstallationType = $img.InstallationType
                        ProductType = $img.ProductType
                        Languages = $img.Languages -join ', '
                        CreatedTime = $img.CreatedTime
                        ModifiedTime = $img.ModifiedTime
                    }
                }
            }
            elseif ($Format -eq 'ISO') {
                # For ISO, we need to mount and check for WIM files
                Write-Verbose "Get-DFImageInfo: ISO file detected, examining contents"

                [PSCustomObject]@{
                    Path = $FullPath
                    Format = $Format
                    Size = (Get-Item $FullPath).Length
                    Note = "Mount ISO to view image details"
                }
            }
            else {
                # Other formats
                $fileInfo = Get-Item $FullPath

                [PSCustomObject]@{
                    Path = $FullPath
                    Format = $Format
                    Size = $fileInfo.Length
                    CreatedTime = $fileInfo.CreationTime
                    ModifiedTime = $fileInfo.LastWriteTime
                }
            }
        }
        catch {
            Write-Error "Failed to get image info: $_"
            throw
        }
    }

    end {
        Write-Verbose "Get-DFImageInfo: Operation completed"
    }
}
