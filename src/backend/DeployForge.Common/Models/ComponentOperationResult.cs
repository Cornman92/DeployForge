namespace DeployForge.Common.Models;

/// <summary>
/// Result of a component operation
/// </summary>
public class ComponentOperationResult
{
    /// <summary>
    /// Whether the operation succeeded overall
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Components that were successfully processed
    /// </summary>
    public List<string> SuccessfulComponents { get; set; } = new();

    /// <summary>
    /// Components that failed to process
    /// </summary>
    public List<ComponentOperationError> FailedComponents { get; set; } = new();

    /// <summary>
    /// Additional components that were affected (e.g., dependencies)
    /// </summary>
    public List<string> AffectedComponents { get; set; } = new();

    /// <summary>
    /// Whether a restart is required
    /// </summary>
    public bool RestartRequired { get; set; }

    /// <summary>
    /// Overall message
    /// </summary>
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Error details for a failed component operation
/// </summary>
public class ComponentOperationError
{
    /// <summary>
    /// Component ID that failed
    /// </summary>
    public string ComponentId { get; set; } = string.Empty;

    /// <summary>
    /// Error message
    /// </summary>
    public string ErrorMessage { get; set; } = string.Empty;

    /// <summary>
    /// Error code if available
    /// </summary>
    public int? ErrorCode { get; set; }
}
