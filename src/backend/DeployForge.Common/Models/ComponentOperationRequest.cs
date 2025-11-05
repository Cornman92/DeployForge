namespace DeployForge.Common.Models;

/// <summary>
/// Request to perform an operation on components
/// </summary>
public class ComponentOperationRequest
{
    /// <summary>
    /// Path to the mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// List of component IDs to operate on
    /// </summary>
    public List<string> ComponentIds { get; set; } = new();

    /// <summary>
    /// Type of operation
    /// </summary>
    public ComponentOperation Operation { get; set; }

    /// <summary>
    /// Whether to automatically handle dependencies
    /// </summary>
    public bool ResolveDependencies { get; set; } = true;

    /// <summary>
    /// Whether to force the operation even if it's risky
    /// </summary>
    public bool Force { get; set; }
}

/// <summary>
/// Types of component operations
/// </summary>
public enum ComponentOperation
{
    /// <summary>
    /// Remove/uninstall components
    /// </summary>
    Remove,

    /// <summary>
    /// Add/install components
    /// </summary>
    Add,

    /// <summary>
    /// Enable disabled components
    /// </summary>
    Enable,

    /// <summary>
    /// Disable components without removing
    /// </summary>
    Disable
}
