using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing Windows components (packages, features, capabilities, apps)
/// </summary>
public interface IComponentService
{
    /// <summary>
    /// Get all components from a mounted image
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="type">Filter by component type (null for all)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of components</returns>
    Task<OperationResult<List<ComponentInfo>>> GetComponentsAsync(
        string mountPath,
        ComponentType? type = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get detailed information about a specific component
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="componentId">Component identifier</param>
    /// <param name="type">Component type</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Component information</returns>
    Task<OperationResult<ComponentInfo>> GetComponentInfoAsync(
        string mountPath,
        string componentId,
        ComponentType type,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove one or more components from an image
    /// </summary>
    /// <param name="request">Component operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result with details</returns>
    Task<OperationResult<ComponentOperationResult>> RemoveComponentsAsync(
        ComponentOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Add components to an image
    /// </summary>
    /// <param name="request">Component operation request</param>
    /// <param name="packagePaths">Paths to package files</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result with details</returns>
    Task<OperationResult<ComponentOperationResult>> AddComponentsAsync(
        ComponentOperationRequest request,
        List<string> packagePaths,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Enable or disable features
    /// </summary>
    /// <param name="request">Component operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result with details</returns>
    Task<OperationResult<ComponentOperationResult>> ToggleFeaturesAsync(
        ComponentOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyze component dependencies
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="componentIds">Components to analyze</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Dependency graph</returns>
    Task<OperationResult<ComponentDependencyGraph>> AnalyzeDependenciesAsync(
        string mountPath,
        List<string> componentIds,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get components by category (bloatware, media, etc.)
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="category">Category name</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of components in category</returns>
    Task<OperationResult<List<ComponentInfo>>> GetComponentsByCategoryAsync(
        string mountPath,
        string category,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Represents a dependency graph for components
/// </summary>
public class ComponentDependencyGraph
{
    /// <summary>
    /// Nodes in the graph (components)
    /// </summary>
    public Dictionary<string, ComponentInfo> Nodes { get; set; } = new();

    /// <summary>
    /// Edges representing dependencies (from -> to)
    /// </summary>
    public List<DependencyEdge> Edges { get; set; } = new();

    /// <summary>
    /// Components that will be orphaned if requested components are removed
    /// </summary>
    public List<string> OrphanedComponents { get; set; } = new();

    /// <summary>
    /// Safe removal order (topologically sorted)
    /// </summary>
    public List<string> RemovalOrder { get; set; } = new();
}

/// <summary>
/// Represents a dependency relationship
/// </summary>
public class DependencyEdge
{
    /// <summary>
    /// Component that has the dependency
    /// </summary>
    public string FromComponentId { get; set; } = string.Empty;

    /// <summary>
    /// Component that is depended upon
    /// </summary>
    public string ToComponentId { get; set; } = string.Empty;

    /// <summary>
    /// Type of dependency
    /// </summary>
    public DependencyType Type { get; set; }
}

/// <summary>
/// Type of dependency relationship
/// </summary>
public enum DependencyType
{
    /// <summary>
    /// Hard dependency (required)
    /// </summary>
    Required,

    /// <summary>
    /// Optional dependency
    /// </summary>
    Optional,

    /// <summary>
    /// Recommended dependency
    /// </summary>
    Recommended
}
