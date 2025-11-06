namespace DeployForge.Common.Models;

/// <summary>
/// Audit log entry for tracking operations
/// </summary>
public class AuditLogEntry
{
    /// <summary>
    /// Unique identifier for the log entry
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Timestamp when the operation occurred
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// User who performed the operation
    /// </summary>
    public string User { get; set; } = Environment.UserName;

    /// <summary>
    /// Machine name where operation was performed
    /// </summary>
    public string MachineName { get; set; } = Environment.MachineName;

    /// <summary>
    /// Operation category
    /// </summary>
    public AuditCategory Category { get; set; }

    /// <summary>
    /// Specific action performed
    /// </summary>
    public string Action { get; set; } = string.Empty;

    /// <summary>
    /// Resource affected by the operation (e.g., image path, template ID)
    /// </summary>
    public string Resource { get; set; } = string.Empty;

    /// <summary>
    /// Operation result
    /// </summary>
    public AuditResult Result { get; set; }

    /// <summary>
    /// Duration of the operation in milliseconds
    /// </summary>
    public long DurationMs { get; set; }

    /// <summary>
    /// Error message if operation failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Detailed description of the operation
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Additional metadata about the operation
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();

    /// <summary>
    /// Changes made during the operation
    /// </summary>
    public List<AuditChange> Changes { get; set; } = new();

    /// <summary>
    /// IP address of the client (for API operations)
    /// </summary>
    public string? IpAddress { get; set; }

    /// <summary>
    /// User agent (for API operations)
    /// </summary>
    public string? UserAgent { get; set; }

    /// <summary>
    /// Session ID
    /// </summary>
    public string? SessionId { get; set; }

    /// <summary>
    /// Operation ID for correlation
    /// </summary>
    public string? OperationId { get; set; }

    /// <summary>
    /// Severity level of the audit entry
    /// </summary>
    public AuditSeverity Severity { get; set; } = AuditSeverity.Information;
}

/// <summary>
/// Audit log category enumeration
/// </summary>
public enum AuditCategory
{
    /// <summary>Image operations</summary>
    Image,

    /// <summary>Component operations</summary>
    Component,

    /// <summary>Driver operations</summary>
    Driver,

    /// <summary>Update operations</summary>
    Update,

    /// <summary>Registry operations</summary>
    Registry,

    /// <summary>Debloat operations</summary>
    Debloat,

    /// <summary>Workflow operations</summary>
    Workflow,

    /// <summary>Deployment operations</summary>
    Deployment,

    /// <summary>Backup operations</summary>
    Backup,

    /// <summary>Template operations</summary>
    Template,

    /// <summary>Configuration operations</summary>
    Configuration,

    /// <summary>Validation operations</summary>
    Validation,

    /// <summary>Language pack operations</summary>
    Language,

    /// <summary>System operations</summary>
    System,

    /// <summary>User authentication and authorization</summary>
    Authentication,

    /// <summary>Settings changes</summary>
    Settings
}

/// <summary>
/// Audit result enumeration
/// </summary>
public enum AuditResult
{
    /// <summary>Operation succeeded</summary>
    Success,

    /// <summary>Operation failed</summary>
    Failure,

    /// <summary>Operation partially succeeded</summary>
    PartialSuccess,

    /// <summary>Operation was cancelled</summary>
    Cancelled,

    /// <summary>Operation is in progress</summary>
    InProgress
}

/// <summary>
/// Audit severity level
/// </summary>
public enum AuditSeverity
{
    /// <summary>Verbose/debug level</summary>
    Verbose,

    /// <summary>Informational</summary>
    Information,

    /// <summary>Warning level</summary>
    Warning,

    /// <summary>Error level</summary>
    Error,

    /// <summary>Critical level</summary>
    Critical
}

/// <summary>
/// Represents a change made during an operation
/// </summary>
public class AuditChange
{
    /// <summary>
    /// Property or field that changed
    /// </summary>
    public string Property { get; set; } = string.Empty;

    /// <summary>
    /// Value before the change
    /// </summary>
    public string? OldValue { get; set; }

    /// <summary>
    /// Value after the change
    /// </summary>
    public string? NewValue { get; set; }

    /// <summary>
    /// Type of change
    /// </summary>
    public ChangeType Type { get; set; }
}

/// <summary>
/// Type of change
/// </summary>
public enum ChangeType
{
    /// <summary>Property was created/added</summary>
    Created,

    /// <summary>Property was modified</summary>
    Modified,

    /// <summary>Property was deleted/removed</summary>
    Deleted
}

/// <summary>
/// Audit log query request
/// </summary>
public class AuditLogQuery
{
    /// <summary>
    /// Start date filter
    /// </summary>
    public DateTime? StartDate { get; set; }

    /// <summary>
    /// End date filter
    /// </summary>
    public DateTime? EndDate { get; set; }

    /// <summary>
    /// User filter
    /// </summary>
    public string? User { get; set; }

    /// <summary>
    /// Category filter
    /// </summary>
    public AuditCategory? Category { get; set; }

    /// <summary>
    /// Action filter
    /// </summary>
    public string? Action { get; set; }

    /// <summary>
    /// Resource filter
    /// </summary>
    public string? Resource { get; set; }

    /// <summary>
    /// Result filter
    /// </summary>
    public AuditResult? Result { get; set; }

    /// <summary>
    /// Operation ID filter
    /// </summary>
    public string? OperationId { get; set; }

    /// <summary>
    /// Minimum severity level
    /// </summary>
    public AuditSeverity? MinSeverity { get; set; }

    /// <summary>
    /// Page number (1-based)
    /// </summary>
    public int PageNumber { get; set; } = 1;

    /// <summary>
    /// Page size
    /// </summary>
    public int PageSize { get; set; } = 50;

    /// <summary>
    /// Sort by field
    /// </summary>
    public string SortBy { get; set; } = "Timestamp";

    /// <summary>
    /// Sort direction (asc/desc)
    /// </summary>
    public string SortDirection { get; set; } = "desc";
}

/// <summary>
/// Audit log query result
/// </summary>
public class AuditLogQueryResult
{
    /// <summary>
    /// Log entries
    /// </summary>
    public List<AuditLogEntry> Entries { get; set; } = new();

    /// <summary>
    /// Total number of matching entries
    /// </summary>
    public int TotalCount { get; set; }

    /// <summary>
    /// Current page number
    /// </summary>
    public int PageNumber { get; set; }

    /// <summary>
    /// Page size
    /// </summary>
    public int PageSize { get; set; }

    /// <summary>
    /// Total number of pages
    /// </summary>
    public int TotalPages { get; set; }

    /// <summary>
    /// Whether there is a next page
    /// </summary>
    public bool HasNextPage { get; set; }

    /// <summary>
    /// Whether there is a previous page
    /// </summary>
    public bool HasPreviousPage { get; set; }
}

/// <summary>
/// Audit log statistics
/// </summary>
public class AuditLogStatistics
{
    /// <summary>
    /// Total number of operations
    /// </summary>
    public int TotalOperations { get; set; }

    /// <summary>
    /// Number of successful operations
    /// </summary>
    public int SuccessfulOperations { get; set; }

    /// <summary>
    /// Number of failed operations
    /// </summary>
    public int FailedOperations { get; set; }

    /// <summary>
    /// Success rate percentage
    /// </summary>
    public double SuccessRate { get; set; }

    /// <summary>
    /// Average operation duration in milliseconds
    /// </summary>
    public double AverageDurationMs { get; set; }

    /// <summary>
    /// Operations by category
    /// </summary>
    public Dictionary<AuditCategory, int> OperationsByCategory { get; set; } = new();

    /// <summary>
    /// Operations by user
    /// </summary>
    public Dictionary<string, int> OperationsByUser { get; set; } = new();

    /// <summary>
    /// Operations by result
    /// </summary>
    public Dictionary<AuditResult, int> OperationsByResult { get; set; } = new();

    /// <summary>
    /// Most active users
    /// </summary>
    public List<UserActivity> MostActiveUsers { get; set; } = new();

    /// <summary>
    /// Most common actions
    /// </summary>
    public List<ActionFrequency> MostCommonActions { get; set; } = new();

    /// <summary>
    /// Date range of statistics
    /// </summary>
    public DateTime? StartDate { get; set; }

    /// <summary>
    /// End date of statistics
    /// </summary>
    public DateTime? EndDate { get; set; }
}

/// <summary>
/// User activity statistics
/// </summary>
public class UserActivity
{
    /// <summary>
    /// User name
    /// </summary>
    public string User { get; set; } = string.Empty;

    /// <summary>
    /// Number of operations
    /// </summary>
    public int OperationCount { get; set; }

    /// <summary>
    /// Success rate
    /// </summary>
    public double SuccessRate { get; set; }
}

/// <summary>
/// Action frequency statistics
/// </summary>
public class ActionFrequency
{
    /// <summary>
    /// Action name
    /// </summary>
    public string Action { get; set; } = string.Empty;

    /// <summary>
    /// Category
    /// </summary>
    public AuditCategory Category { get; set; }

    /// <summary>
    /// Frequency count
    /// </summary>
    public int Count { get; set; }
}

/// <summary>
/// Request to export audit logs
/// </summary>
public class ExportAuditLogsRequest
{
    /// <summary>
    /// Query parameters for filtering
    /// </summary>
    public AuditLogQuery Query { get; set; } = new();

    /// <summary>
    /// Export format (JSON, CSV, Excel, PDF)
    /// </summary>
    public string Format { get; set; } = "JSON";

    /// <summary>
    /// Include metadata in export
    /// </summary>
    public bool IncludeMetadata { get; set; } = true;

    /// <summary>
    /// Include changes in export
    /// </summary>
    public bool IncludeChanges { get; set; } = true;
}

/// <summary>
/// Audit log retention policy
/// </summary>
public class AuditRetentionPolicy
{
    /// <summary>
    /// Retention period in days (0 = unlimited)
    /// </summary>
    public int RetentionDays { get; set; } = 365;

    /// <summary>
    /// Whether to compress old logs
    /// </summary>
    public bool CompressOldLogs { get; set; } = true;

    /// <summary>
    /// Archive path for old logs
    /// </summary>
    public string? ArchivePath { get; set; }

    /// <summary>
    /// Auto-archive logs older than days
    /// </summary>
    public int AutoArchiveAfterDays { get; set; } = 90;

    /// <summary>
    /// Maximum log file size in MB
    /// </summary>
    public int MaxLogFileSizeMB { get; set; } = 100;
}
