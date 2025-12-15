function Dismount-DeployImage {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$MountDir,

        [Parameter(Mandatory=$false)]
        [switch]$SaveChanges,

        [Parameter(Mandatory=$false)]
        [switch]$Force
    )

    Write-Verbose "Dismounting image from $MountDir (Save: $SaveChanges)"

    try {
        Dismount-WindowsImage -Path $MountDir -Save:$SaveChanges -Discard:(-not $SaveChanges) -ErrorAction Stop
        
        # Cleanup mount directory if empty/successful
        if (Test-Path $MountDir) {
            Remove-Item $MountDir -Force -Recurse -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Error "Failed to dismount image: $_"
        throw
    }
}
