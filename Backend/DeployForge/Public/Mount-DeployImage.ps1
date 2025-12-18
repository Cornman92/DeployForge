function Mount-DeployImage {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$ImagePath,

        [Parameter(Mandatory=$false)]
        [int]$Index = 1,

        [Parameter(Mandatory=$false)]
        [string]$MountDir
    )

    if (-not $MountDir) {
        $MountDir = Join-Path $env:TEMP ("DeployForge_Mount_" + [Guid]::NewGuid().ToString())
    }

    if (-not (Test-Path $MountDir)) {
        New-Item -ItemType Directory -Path $MountDir -Force | Out-Null
    }

    Write-Verbose "Mounting image $ImagePath (Index: $Index) to $MountDir"

    try {
        Mount-WindowsImage -ImagePath $ImagePath -Index $Index -Path $MountDir -ErrorAction Stop
        
        return [PSCustomObject]@{
            ImagePath = $ImagePath
            MountDir  = $MountDir
            Index     = $Index
            Mounted   = $true
        }
    }
    catch {
        Write-Error "Failed to mount image: $_"
        throw
    }
}
