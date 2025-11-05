namespace DeployForge.Common.Models;

/// <summary>
/// Represents a Windows component (package, feature, capability, or app)
/// </summary>
public class ComponentInfo
{
    /// <summary>
    /// Unique identifier for the component
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Display name of the component
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Type of component
    /// </summary>
    public ComponentType Type { get; set; }

    /// <summary>
    /// Current state of the component
    /// </summary>
    public ComponentState State { get; set; }

    /// <summary>
    /// Version string
    /// </summary>
    public string Version { get; set; } = string.Empty;

    /// <summary>
    /// Component description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Publisher or vendor
    /// </summary>
    public string Publisher { get; set; } = string.Empty;

    /// <summary>
    /// Install date (if available)
    /// </summary>
    public DateTime? InstallDate { get; set; }

    /// <summary>
    /// Size in bytes
    /// </summary>
    public long SizeBytes { get; set; }

    /// <summary>
    /// Whether this component can be safely removed
    /// </summary>
    public bool IsRemovable { get; set; }

    /// <summary>
    /// List of component IDs this component depends on
    /// </summary>
    public List<string> Dependencies { get; set; } = new();

    /// <summary>
    /// List of component IDs that depend on this component
    /// </summary>
    public List<string> DependentComponents { get; set; } = new();

    /// <summary>
    /// Category or group (e.g., "Bloatware", "Core", "Media", "Networking")
    /// </summary>
    public string Category { get; set; } = string.Empty;

    /// <summary>
    /// Tags for filtering and classification
    /// </summary>
    public List<string> Tags { get; set; } = new();

    /// <summary>
    /// Restart required after removal
    /// </summary>
    public bool RestartRequired { get; set; }
}
