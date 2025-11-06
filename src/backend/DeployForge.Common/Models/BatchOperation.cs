namespace DeployForge.Common.Models;

/// <summary>
/// Represents a batch operation that processes multiple images
/// </summary>
public class BatchOperation
{
    /// <summary>
    /// Unique identifier for the batch operation
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Batch operation name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Batch operation description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Type of batch operation
    /// </summary>
    public BatchOperationType Type { get; set; }

    /// <summary>
    /// Current status of the batch operation
    /// </summary>
    public BatchOperationStatus Status { get; set; } = BatchOperationStatus.Pending;

    /// <summary>
    /// Creation timestamp
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Start timestamp
    /// </summary>
    public DateTime? StartedAt { get; set; }

    /// <summary>
    /// Completion timestamp
    /// </summary>
    public DateTime? CompletedAt { get; set; }

    /// <summary>
    /// Total duration in milliseconds
    /// </summary>
    public long DurationMs { get; set; }

    /// <summary>
    /// User who created the batch operation
    /// </summary>
    public string CreatedBy { get; set; } = Environment.UserName;

    /// <summary>
    /// List of target images for the batch operation
    /// </summary>
    public List<BatchTargetImage> TargetImages { get; set; } = new();

    /// <summary>
    /// Operation configuration/parameters
    /// </summary>
    public Dictionary<string, object> Configuration { get; set; } = new();

    /// <summary>
    /// Template ID if using a template
    /// </summary>
    public string? TemplateId { get; set; }

    /// <summary>
    /// Profile ID if using a configuration profile
    /// </summary>
    public string? ProfileId { get; set; }

    /// <summary>
    /// Priority of the batch operation (1-10, higher is more important)
    /// </summary>
    public int Priority { get; set; } = 5;

    /// <summary>
    /// Maximum number of parallel operations
    /// </summary>
    public int MaxParallelOperations { get; set; } = 2;

    /// <summary>
    /// Whether to continue on errors
    /// </summary>
    public bool ContinueOnError { get; set; } = true;

    /// <summary>
    /// Overall progress percentage (0-100)
    /// </summary>
    public int ProgressPercentage { get; set; }

    /// <summary>
    /// Current status message
    /// </summary>
    public string StatusMessage { get; set; } = string.Empty;

    /// <summary>
    /// Summary of the batch operation
    /// </summary>
    public BatchOperationSummary Summary { get; set; } = new();

    /// <summary>
    /// Error message if batch operation failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Tags for categorization
    /// </summary>
    public List<string> Tags { get; set; } = new();
}

/// <summary>
/// Batch operation type enumeration
/// </summary>
public enum BatchOperationType
{
    /// <summary>Apply template to multiple images</summary>
    ApplyTemplate,

    /// <summary>Mount multiple images</summary>
    MountImages,

    /// <summary>Unmount multiple images</summary>
    UnmountImages,

    /// <summary>Validate multiple images</summary>
    ValidateImages,

    /// <summary>Optimize multiple images</summary>
    OptimizeImages,

    /// <summary>Export multiple images</summary>
    ExportImages,

    /// <summary>Convert multiple images</summary>
    ConvertImages,

    /// <summary>Backup multiple images</summary>
    BackupImages,

    /// <summary>Deploy multiple images</summary>
    DeployImages,

    /// <summary>Apply debloat to multiple images</summary>
    DebloatImages,

    /// <summary>Install updates on multiple images</summary>
    InstallUpdates,

    /// <summary>Add drivers to multiple images</summary>
    AddDrivers,

    /// <summary>Remove components from multiple images</summary>
    RemoveComponents,

    /// <summary>Apply registry changes to multiple images</summary>
    ApplyRegistryChanges,

    /// <summary>Custom batch operation</summary>
    Custom
}

/// <summary>
/// Batch operation status enumeration
/// </summary>
public enum BatchOperationStatus
{
    /// <summary>Batch operation is pending</summary>
    Pending,

    /// <summary>Batch operation is queued</summary>
    Queued,

    /// <summary>Batch operation is running</summary>
    Running,

    /// <summary>Batch operation is paused</summary>
    Paused,

    /// <summary>Batch operation completed successfully</summary>
    Completed,

    /// <summary>Batch operation completed with errors</summary>
    CompletedWithErrors,

    /// <summary>Batch operation failed</summary>
    Failed,

    /// <summary>Batch operation was cancelled</summary>
    Cancelled
}

/// <summary>
/// Target image for batch operation
/// </summary>
public class BatchTargetImage
{
    /// <summary>
    /// Image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Image index (1-based)
    /// </summary>
    public int ImageIndex { get; set; } = 1;

    /// <summary>
    /// Mount path (if applicable)
    /// </summary>
    public string? MountPath { get; set; }

    /// <summary>
    /// Current status of this image's operation
    /// </summary>
    public ImageOperationStatus Status { get; set; } = ImageOperationStatus.Pending;

    /// <summary>
    /// Progress percentage for this image (0-100)
    /// </summary>
    public int ProgressPercentage { get; set; }

    /// <summary>
    /// Status message for this image
    /// </summary>
    public string StatusMessage { get; set; } = string.Empty;

    /// <summary>
    /// Error message if operation failed for this image
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Start timestamp for this image
    /// </summary>
    public DateTime? StartedAt { get; set; }

    /// <summary>
    /// Completion timestamp for this image
    /// </summary>
    public DateTime? CompletedAt { get; set; }

    /// <summary>
    /// Duration in milliseconds for this image
    /// </summary>
    public long DurationMs { get; set; }

    /// <summary>
    /// Additional metadata for this image
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Image operation status
/// </summary>
public enum ImageOperationStatus
{
    /// <summary>Operation is pending</summary>
    Pending,

    /// <summary>Operation is queued</summary>
    Queued,

    /// <summary>Operation is running</summary>
    Running,

    /// <summary>Operation completed successfully</summary>
    Completed,

    /// <summary>Operation failed</summary>
    Failed,

    /// <summary>Operation was skipped</summary>
    Skipped,

    /// <summary>Operation was cancelled</summary>
    Cancelled
}

/// <summary>
/// Summary of batch operation results
/// </summary>
public class BatchOperationSummary
{
    /// <summary>
    /// Total number of images
    /// </summary>
    public int TotalImages { get; set; }

    /// <summary>
    /// Number of successfully processed images
    /// </summary>
    public int SuccessfulImages { get; set; }

    /// <summary>
    /// Number of failed images
    /// </summary>
    public int FailedImages { get; set; }

    /// <summary>
    /// Number of skipped images
    /// </summary>
    public int SkippedImages { get; set; }

    /// <summary>
    /// Number of cancelled images
    /// </summary>
    public int CancelledImages { get; set; }

    /// <summary>
    /// Success rate percentage
    /// </summary>
    public double SuccessRate { get; set; }

    /// <summary>
    /// Average duration per image in milliseconds
    /// </summary>
    public double AverageDurationMs { get; set; }

    /// <summary>
    /// Total data processed in bytes
    /// </summary>
    public long TotalBytesProcessed { get; set; }
}

/// <summary>
/// Request to create a batch operation
/// </summary>
public class CreateBatchOperationRequest
{
    /// <summary>
    /// Batch operation name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Batch operation description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Type of batch operation
    /// </summary>
    public BatchOperationType Type { get; set; }

    /// <summary>
    /// List of target images
    /// </summary>
    public List<BatchTargetImage> TargetImages { get; set; } = new();

    /// <summary>
    /// Operation configuration
    /// </summary>
    public Dictionary<string, object> Configuration { get; set; } = new();

    /// <summary>
    /// Template ID (if applicable)
    /// </summary>
    public string? TemplateId { get; set; }

    /// <summary>
    /// Profile ID (if applicable)
    /// </summary>
    public string? ProfileId { get; set; }

    /// <summary>
    /// Priority (1-10)
    /// </summary>
    public int Priority { get; set; } = 5;

    /// <summary>
    /// Maximum parallel operations
    /// </summary>
    public int MaxParallelOperations { get; set; } = 2;

    /// <summary>
    /// Continue on error
    /// </summary>
    public bool ContinueOnError { get; set; } = true;

    /// <summary>
    /// Whether to start immediately
    /// </summary>
    public bool StartImmediately { get; set; } = true;

    /// <summary>
    /// Tags
    /// </summary>
    public List<string> Tags { get; set; } = new();
}

/// <summary>
/// Batch operation query request
/// </summary>
public class BatchOperationQuery
{
    /// <summary>
    /// Status filter
    /// </summary>
    public BatchOperationStatus? Status { get; set; }

    /// <summary>
    /// Type filter
    /// </summary>
    public BatchOperationType? Type { get; set; }

    /// <summary>
    /// Created by user filter
    /// </summary>
    public string? CreatedBy { get; set; }

    /// <summary>
    /// Tag filter
    /// </summary>
    public string? Tag { get; set; }

    /// <summary>
    /// Start date filter
    /// </summary>
    public DateTime? StartDate { get; set; }

    /// <summary>
    /// End date filter
    /// </summary>
    public DateTime? EndDate { get; set; }

    /// <summary>
    /// Page number
    /// </summary>
    public int PageNumber { get; set; } = 1;

    /// <summary>
    /// Page size
    /// </summary>
    public int PageSize { get; set; } = 50;

    /// <summary>
    /// Sort by field
    /// </summary>
    public string SortBy { get; set; } = "CreatedAt";

    /// <summary>
    /// Sort direction
    /// </summary>
    public string SortDirection { get; set; } = "desc";
}

/// <summary>
/// Batch operation query result
/// </summary>
public class BatchOperationQueryResult
{
    /// <summary>
    /// Batch operations
    /// </summary>
    public List<BatchOperation> Operations { get; set; } = new();

    /// <summary>
    /// Total count
    /// </summary>
    public int TotalCount { get; set; }

    /// <summary>
    /// Page number
    /// </summary>
    public int PageNumber { get; set; }

    /// <summary>
    /// Page size
    /// </summary>
    public int PageSize { get; set; }

    /// <summary>
    /// Total pages
    /// </summary>
    public int TotalPages { get; set; }

    /// <summary>
    /// Has next page
    /// </summary>
    public bool HasNextPage { get; set; }

    /// <summary>
    /// Has previous page
    /// </summary>
    public bool HasPreviousPage { get; set; }
}

/// <summary>
/// Batch operation statistics
/// </summary>
public class BatchOperationStatistics
{
    /// <summary>
    /// Total batch operations
    /// </summary>
    public int TotalBatchOperations { get; set; }

    /// <summary>
    /// Completed batch operations
    /// </summary>
    public int CompletedBatchOperations { get; set; }

    /// <summary>
    /// Failed batch operations
    /// </summary>
    public int FailedBatchOperations { get; set; }

    /// <summary>
    /// Running batch operations
    /// </summary>
    public int RunningBatchOperations { get; set; }

    /// <summary>
    /// Total images processed
    /// </summary>
    public int TotalImagesProcessed { get; set; }

    /// <summary>
    /// Success rate
    /// </summary>
    public double SuccessRate { get; set; }

    /// <summary>
    /// Average batch duration in milliseconds
    /// </summary>
    public double AverageBatchDurationMs { get; set; }

    /// <summary>
    /// Operations by type
    /// </summary>
    public Dictionary<BatchOperationType, int> OperationsByType { get; set; } = new();

    /// <summary>
    /// Operations by status
    /// </summary>
    public Dictionary<BatchOperationStatus, int> OperationsByStatus { get; set; } = new();
}
