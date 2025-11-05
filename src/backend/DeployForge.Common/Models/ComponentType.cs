namespace DeployForge.Common.Models;

/// <summary>
/// Types of Windows components that can be managed
/// </summary>
public enum ComponentType
{
    /// <summary>
    /// Windows Package (.cab, .msu)
    /// </summary>
    Package,

    /// <summary>
    /// Optional Feature (DISM features)
    /// </summary>
    Feature,

    /// <summary>
    /// Windows Capability (e.g., Language packs, FOD)
    /// </summary>
    Capability,

    /// <summary>
    /// Provisioned App Package (AppX)
    /// </summary>
    AppPackage
}
