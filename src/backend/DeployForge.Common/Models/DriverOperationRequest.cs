namespace DeployForge.Common.Models;

/// <summary>
/// Request to perform driver operations
/// </summary>
public class DriverOperationRequest
{
    /// <summary>
    /// Path to the mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Driver paths or published names
    /// </summary>
    public List<string> Drivers { get; set; } = new();

    /// <summary>
    /// Force unsigned drivers (use with caution)
    /// </summary>
    public bool ForceUnsigned { get; set; }

    /// <summary>
    /// Recurse subdirectories when adding drivers
    /// </summary>
    public bool Recurse { get; set; } = true;
}

/// <summary>
/// Result of driver operations
/// </summary>
public class DriverOperationResult
{
    /// <summary>
    /// Whether the operation succeeded overall
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Drivers that were successfully processed
    /// </summary>
    public List<string> SuccessfulDrivers { get; set; } = new();

    /// <summary>
    /// Drivers that failed to process
    /// </summary>
    public List<DriverOperationError> FailedDrivers { get; set; } = new();

    /// <summary>
    /// Total number of drivers processed
    /// </summary>
    public int TotalProcessed { get; set; }

    /// <summary>
    /// Overall message
    /// </summary>
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Error details for a failed driver operation
/// </summary>
public class DriverOperationError
{
    /// <summary>
    /// Driver identifier that failed
    /// </summary>
    public string DriverId { get; set; } = string.Empty;

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
/// Request to analyze driver conflicts
/// </summary>
public class DriverConflictAnalysisRequest
{
    /// <summary>
    /// Path to the mounted image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// New driver paths to analyze
    /// </summary>
    public List<string> NewDriverPaths { get; set; } = new();
}

/// <summary>
/// Result of driver conflict analysis
/// </summary>
public class DriverConflictAnalysis
{
    /// <summary>
    /// Conflicts detected
    /// </summary>
    public List<DriverConflict> Conflicts { get; set; } = new();

    /// <summary>
    /// Safe to add all drivers
    /// </summary>
    public bool SafeToAdd { get; set; }

    /// <summary>
    /// Recommendations
    /// </summary>
    public List<string> Recommendations { get; set; } = new();
}

/// <summary>
/// Represents a driver conflict
/// </summary>
public class DriverConflict
{
    /// <summary>
    /// Existing driver
    /// </summary>
    public DriverInfo ExistingDriver { get; set; } = new();

    /// <summary>
    /// Conflicting new driver path
    /// </summary>
    public string NewDriverPath { get; set; } = string.Empty;

    /// <summary>
    /// Conflict type
    /// </summary>
    public ConflictType Type { get; set; }

    /// <summary>
    /// Conflict description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Severity level
    /// </summary>
    public ConflictSeverity Severity { get; set; }
}

/// <summary>
/// Types of driver conflicts
/// </summary>
public enum ConflictType
{
    /// <summary>
    /// Same hardware ID, different versions
    /// </summary>
    VersionConflict,

    /// <summary>
    /// Duplicate driver for same hardware
    /// </summary>
    DuplicateDriver,

    /// <summary>
    /// Incompatible architectures
    /// </summary>
    ArchitectureMismatch,

    /// <summary>
    /// Signature mismatch
    /// </summary>
    SignatureIssue
}

/// <summary>
/// Conflict severity levels
/// </summary>
public enum ConflictSeverity
{
    /// <summary>
    /// Informational only
    /// </summary>
    Info,

    /// <summary>
    /// Warning - review recommended
    /// </summary>
    Warning,

    /// <summary>
    /// Error - should not proceed
    /// </summary>
    Error
}
