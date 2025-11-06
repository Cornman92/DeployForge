namespace DeployForge.Common.Models;

/// <summary>
/// Validation result for image or deployment validation
/// </summary>
public class ValidationResult
{
    /// <summary>
    /// Unique identifier for the validation run
    /// </summary>
    public string ValidationId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Overall validation status
    /// </summary>
    public ValidationStatus Status { get; set; } = ValidationStatus.Passed;

    /// <summary>
    /// Timestamp when validation was performed
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Duration of validation in milliseconds
    /// </summary>
    public long DurationMs { get; set; }

    /// <summary>
    /// Image path that was validated
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Mount path (if applicable)
    /// </summary>
    public string? MountPath { get; set; }

    /// <summary>
    /// Individual validation check results
    /// </summary>
    public List<ValidationCheck> Checks { get; set; } = new();

    /// <summary>
    /// Summary of validation results
    /// </summary>
    public ValidationSummary Summary { get; set; } = new();

    /// <summary>
    /// Warnings that don't prevent deployment
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// Critical errors that prevent deployment
    /// </summary>
    public List<string> Errors { get; set; } = new();

    /// <summary>
    /// Recommendations for improving the image
    /// </summary>
    public List<string> Recommendations { get; set; } = new();
}

/// <summary>
/// Validation status enumeration
/// </summary>
public enum ValidationStatus
{
    /// <summary>All checks passed</summary>
    Passed,

    /// <summary>Some checks passed with warnings</summary>
    PassedWithWarnings,

    /// <summary>Some checks failed but deployment may continue</summary>
    Failed,

    /// <summary>Critical checks failed, deployment cannot continue</summary>
    Critical,

    /// <summary>Validation is in progress</summary>
    InProgress,

    /// <summary>Validation was skipped</summary>
    Skipped
}

/// <summary>
/// Individual validation check result
/// </summary>
public class ValidationCheck
{
    /// <summary>
    /// Name of the validation check
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Category of the validation check
    /// </summary>
    public ValidationCategory Category { get; set; }

    /// <summary>
    /// Check status
    /// </summary>
    public CheckStatus Status { get; set; }

    /// <summary>
    /// Severity level
    /// </summary>
    public ValidationSeverity Severity { get; set; }

    /// <summary>
    /// Description of the check
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Message providing details about the check result
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Duration of this check in milliseconds
    /// </summary>
    public long DurationMs { get; set; }

    /// <summary>
    /// Additional data about the check
    /// </summary>
    public Dictionary<string, object> Data { get; set; } = new();
}

/// <summary>
/// Validation category enumeration
/// </summary>
public enum ValidationCategory
{
    /// <summary>Image integrity checks</summary>
    ImageIntegrity,

    /// <summary>Boot file validation</summary>
    BootFiles,

    /// <summary>Component dependency validation</summary>
    ComponentDependencies,

    /// <summary>Registry validation</summary>
    Registry,

    /// <summary>Driver validation</summary>
    Drivers,

    /// <summary>Update validation</summary>
    Updates,

    /// <summary>Language pack validation</summary>
    LanguagePacks,

    /// <summary>Disk space validation</summary>
    DiskSpace,

    /// <summary>File system validation</summary>
    FileSystem,

    /// <summary>Security validation</summary>
    Security,

    /// <summary>Performance validation</summary>
    Performance,

    /// <summary>Deployment readiness</summary>
    DeploymentReadiness
}

/// <summary>
/// Check status enumeration
/// </summary>
public enum CheckStatus
{
    /// <summary>Check passed</summary>
    Passed,

    /// <summary>Check failed</summary>
    Failed,

    /// <summary>Check was skipped</summary>
    Skipped,

    /// <summary>Check is in progress</summary>
    InProgress,

    /// <summary>Check encountered an error</summary>
    Error
}

/// <summary>
/// Validation severity enumeration
/// </summary>
public enum ValidationSeverity
{
    /// <summary>Informational only</summary>
    Info,

    /// <summary>Warning, but deployment can continue</summary>
    Warning,

    /// <summary>Error that should be fixed</summary>
    Error,

    /// <summary>Critical error that prevents deployment</summary>
    Critical
}

/// <summary>
/// Summary of validation results
/// </summary>
public class ValidationSummary
{
    /// <summary>
    /// Total number of checks performed
    /// </summary>
    public int TotalChecks { get; set; }

    /// <summary>
    /// Number of checks that passed
    /// </summary>
    public int PassedChecks { get; set; }

    /// <summary>
    /// Number of checks that failed
    /// </summary>
    public int FailedChecks { get; set; }

    /// <summary>
    /// Number of checks that were skipped
    /// </summary>
    public int SkippedChecks { get; set; }

    /// <summary>
    /// Number of warnings
    /// </summary>
    public int WarningCount { get; set; }

    /// <summary>
    /// Number of errors
    /// </summary>
    public int ErrorCount { get; set; }

    /// <summary>
    /// Number of critical issues
    /// </summary>
    public int CriticalCount { get; set; }

    /// <summary>
    /// Overall pass percentage
    /// </summary>
    public double PassPercentage { get; set; }
}

/// <summary>
/// Request to validate an image
/// </summary>
public class ValidateImageRequest
{
    /// <summary>
    /// Path to the image file
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Mount path (if image is already mounted)
    /// </summary>
    public string? MountPath { get; set; }

    /// <summary>
    /// Image index to validate (1-based)
    /// </summary>
    public int ImageIndex { get; set; } = 1;

    /// <summary>
    /// Categories of checks to perform (empty = all)
    /// </summary>
    public List<ValidationCategory> CheckCategories { get; set; } = new();

    /// <summary>
    /// Whether to perform deep validation (slower but more thorough)
    /// </summary>
    public bool DeepValidation { get; set; } = false;

    /// <summary>
    /// Whether to fail fast on first critical error
    /// </summary>
    public bool FailFast { get; set; } = false;

    /// <summary>
    /// Minimum severity level to report
    /// </summary>
    public ValidationSeverity MinimumSeverity { get; set; } = ValidationSeverity.Info;
}

/// <summary>
/// Request to validate deployment readiness
/// </summary>
public class ValidateDeploymentRequest
{
    /// <summary>
    /// Path to the image file
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Deployment method (USB, Network, ISO)
    /// </summary>
    public string DeploymentMethod { get; set; } = "USB";

    /// <summary>
    /// Target device (for USB deployment)
    /// </summary>
    public string? TargetDevice { get; set; }

    /// <summary>
    /// Network share path (for network deployment)
    /// </summary>
    public string? NetworkPath { get; set; }

    /// <summary>
    /// ISO output path (for ISO deployment)
    /// </summary>
    public string? IsoPath { get; set; }

    /// <summary>
    /// Whether to check target device compatibility
    /// </summary>
    public bool CheckTargetCompatibility { get; set; } = true;
}

/// <summary>
/// Request to validate component dependencies
/// </summary>
public class ValidateComponentDependenciesRequest
{
    /// <summary>
    /// Mount path of the image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// List of components to validate (empty = all)
    /// </summary>
    public List<string> Components { get; set; } = new();

    /// <summary>
    /// Whether to check for missing dependencies
    /// </summary>
    public bool CheckMissingDependencies { get; set; } = true;

    /// <summary>
    /// Whether to check for circular dependencies
    /// </summary>
    public bool CheckCircularDependencies { get; set; } = true;
}

/// <summary>
/// Request to validate boot files
/// </summary>
public class ValidateBootFilesRequest
{
    /// <summary>
    /// Mount path of the image
    /// </summary>
    public string MountPath { get; set; } = string.Empty;

    /// <summary>
    /// Whether to validate bootloader configuration
    /// </summary>
    public bool ValidateBootloader { get; set; } = true;

    /// <summary>
    /// Whether to validate BCD store
    /// </summary>
    public bool ValidateBcdStore { get; set; } = true;

    /// <summary>
    /// Whether to validate boot critical drivers
    /// </summary>
    public bool ValidateBootDrivers { get; set; } = true;
}

/// <summary>
/// Validation options
/// </summary>
public class ValidationOptions
{
    /// <summary>
    /// Whether to enable parallel validation checks
    /// </summary>
    public bool EnableParallelValidation { get; set; } = true;

    /// <summary>
    /// Maximum number of parallel validation tasks
    /// </summary>
    public int MaxParallelTasks { get; set; } = 4;

    /// <summary>
    /// Timeout for individual checks in seconds
    /// </summary>
    public int CheckTimeoutSeconds { get; set; } = 60;

    /// <summary>
    /// Whether to generate detailed reports
    /// </summary>
    public bool GenerateDetailedReports { get; set; } = true;

    /// <summary>
    /// Whether to include performance metrics
    /// </summary>
    public bool IncludePerformanceMetrics { get; set; } = true;
}

/// <summary>
/// Pre-flight check result
/// </summary>
public class PreFlightCheckResult
{
    /// <summary>
    /// Whether the system is ready for operations
    /// </summary>
    public bool IsReady { get; set; }

    /// <summary>
    /// System checks performed
    /// </summary>
    public List<SystemCheck> SystemChecks { get; set; } = new();

    /// <summary>
    /// Issues that need to be resolved
    /// </summary>
    public List<string> BlockingIssues { get; set; } = new();

    /// <summary>
    /// Warnings that should be addressed
    /// </summary>
    public List<string> Warnings { get; set; } = new();
}

/// <summary>
/// System check for pre-flight validation
/// </summary>
public class SystemCheck
{
    /// <summary>
    /// Name of the system check
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Whether the check passed
    /// </summary>
    public bool Passed { get; set; }

    /// <summary>
    /// Message about the check
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Required value
    /// </summary>
    public string? Required { get; set; }

    /// <summary>
    /// Actual value
    /// </summary>
    public string? Actual { get; set; }
}
