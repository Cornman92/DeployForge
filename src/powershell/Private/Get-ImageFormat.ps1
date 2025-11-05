function Get-ImageFormat {
    <#
    .SYNOPSIS
        Detects the format of a Windows image file.
    #>

    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $extension = [System.IO.Path]::GetExtension($Path).ToLower()

    switch ($extension) {
        '.wim' { return 'WIM' }
        '.esd' { return 'ESD' }
        '.iso' { return 'ISO' }
        '.vhdx' { return 'VHDX' }
        '.vhd' { return 'VHD' }
        '.img' { return 'IMG' }
        '.ppkg' { return 'PPKG' }
        default { return 'Unknown' }
    }
}
