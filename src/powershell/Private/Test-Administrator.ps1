function Test-Administrator {
    <#
    .SYNOPSIS
        Tests if the current session has administrator privileges.
    #>

    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
