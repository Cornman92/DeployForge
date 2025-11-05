namespace DeployForge.Common.Models;

/// <summary>
/// Current state of a Windows component
/// </summary>
public enum ComponentState
{
    /// <summary>
    /// Component is not installed
    /// </summary>
    NotPresent,

    /// <summary>
    /// Component is installed but disabled
    /// </summary>
    Disabled,

    /// <summary>
    /// Component is installed and enabled
    /// </summary>
    Enabled,

    /// <summary>
    /// Component is staged but not yet installed
    /// </summary>
    Staged,

    /// <summary>
    /// Component is superseded by a newer version
    /// </summary>
    Superseded,

    /// <summary>
    /// Component is pending installation after reboot
    /// </summary>
    InstallPending,

    /// <summary>
    /// Component is pending removal after reboot
    /// </summary>
    UninstallPending
}
