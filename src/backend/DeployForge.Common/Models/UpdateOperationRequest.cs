namespace DeployForge.Common.Models;

/// <summary>
/// Request to perform update operations
/// </summary>
public class UpdateOperationRequest
{
    /// <summary>
    /// Path to the mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Paths to update files (.msu, .cab)
    /// </summary>
    public List<string> UpdatePaths { get; set; } = new();

    /// <summary>
    /// Prevent pending online actions
    /// </summary>
    public bool PreventPending { get; set; }

    /// <summary>
    /// Ignore package check failures
    /// </summary>
    public bool IgnoreCheck { get; set; }
}

/// <summary>
/// Result of update operations
/// </summary>
public class UpdateOperationResult
{
    /// <summary>
    /// Whether the operation succeeded overall
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Updates that were successfully installed
    /// </summary>
    public List<string> SuccessfulUpdates { get; set; } = new();

    /// <summary>
    /// Updates that failed to install
    /// </summary>
    public List<UpdateOperationError> FailedUpdates { get; set; } = new();

    /// <summary>
    /// Total number of updates processed
    /// </summary>
    public int TotalProcessed { get; set; }

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
/// Error details for a failed update operation
/// </summary>
public class UpdateOperationError
{
    /// <summary>
    /// Update path or KB number that failed
    /// </summary>
    public string UpdateId { get; set; } = string.Empty;

    /// <summary>
    /// Error message
    /// </summary>
    public string ErrorMessage { get; set; } = string.Empty;

    /// <summary>
    /// Error code if available
    /// </summary>
    public int? ErrorCode { get; set; }
}

/// <summary>
/// Request to analyze update compatibility
/// </summary>
public class UpdateCompatibilityRequest
{
    /// <summary>
    /// Path to the mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Update paths to analyze
    /// </summary>
    public List<string> UpdatePaths { get; set; } = new();
}

/// <summary>
/// Result of update compatibility analysis
/// </summary>
public class UpdateCompatibilityResult
{
    /// <summary>
    /// Compatible updates
    /// </summary>
    public List<string> CompatibleUpdates { get; set; } = new();

    /// <summary>
    /// Incompatible updates with reasons
    /// </summary>
    public List<UpdateIncompatibility> IncompatibleUpdates { get; set; } = new();

    /// <summary>
    /// Updates requiring prerequisites
    /// </summary>
    public List<UpdatePrerequisite> MissingPrerequisites { get; set; } = new();

    /// <summary>
    /// Recommended installation order
    /// </summary>
    public List<string> InstallationOrder { get; set; } = new();
}

/// <summary>
/// Represents an incompatible update
/// </summary>
public class UpdateIncompatibility
{
    /// <summary>
    /// Update path or identifier
    /// </summary>
    public string UpdatePath { get; set; } = string.Empty;

    /// <summary>
    /// Reason for incompatibility
    /// </summary>
    public string Reason { get; set; } = string.Empty;

    /// <summary>
    /// Incompatibility type
    /// </summary>
    public IncompatibilityType Type { get; set; }
}

/// <summary>
/// Represents missing prerequisites
/// </summary>
public class UpdatePrerequisite
{
    /// <summary>
    /// Update that requires prerequisites
    /// </summary>
    public string UpdatePath { get; set; } = string.Empty;

    /// <summary>
    /// Required KB numbers or updates
    /// </summary>
    public List<string> RequiredUpdates { get; set; } = new();
}

/// <summary>
/// Types of update incompatibility
/// </summary>
public enum IncompatibilityType
{
    /// <summary>
    /// Wrong OS version
    /// </summary>
    OSVersionMismatch,

    /// <summary>
    /// Wrong architecture (x86/x64/ARM64)
    /// </summary>
    ArchitectureMismatch,

    /// <summary>
    /// Update is superseded
    /// </summary>
    Superseded,

    /// <summary>
    /// Missing prerequisites
    /// </summary>
    MissingPrerequisites,

    /// <summary>
    /// Other reason
    /// </summary>
    Other
}
