function Get-DeployImageInfo {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$ImagePath
    )

    try {
        $Info = Get-WindowsImage -ImagePath $ImagePath
        return $Info
    }
    catch {
        Write-Error "Failed to get image info: $_"
        throw
    }
}
