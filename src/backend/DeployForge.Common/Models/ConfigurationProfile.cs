namespace DeployForge.Common.Models;

/// <summary>
/// Represents a user configuration profile for customizing application behavior
/// </summary>
public class ConfigurationProfile
{
    /// <summary>
    /// Unique identifier for the profile
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Profile name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Profile description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Profile owner/author
    /// </summary>
    public string Owner { get; set; } = Environment.UserName;

    /// <summary>
    /// Whether this is the default profile
    /// </summary>
    public bool IsDefault { get; set; }

    /// <summary>
    /// Whether this profile is shared with team
    /// </summary>
    public bool IsShared { get; set; }

    /// <summary>
    /// Creation timestamp
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Last modified timestamp
    /// </summary>
    public DateTime ModifiedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Tags for categorization
    /// </summary>
    public List<string> Tags { get; set; } = new();

    /// <summary>
    /// General application settings
    /// </summary>
    public GeneralSettings General { get; set; } = new();

    /// <summary>
    /// Image operation preferences
    /// </summary>
    public ImageOperationSettings ImageOperations { get; set; } = new();

    /// <summary>
    /// Deployment preferences
    /// </summary>
    public DeploymentSettings Deployment { get; set; } = new();

    /// <summary>
    /// Backup and snapshot preferences
    /// </summary>
    public BackupSettings Backup { get; set; } = new();

    /// <summary>
    /// Workflow execution preferences
    /// </summary>
    public WorkflowSettings Workflow { get; set; } = new();

    /// <summary>
    /// Advanced settings
    /// </summary>
    public AdvancedSettings Advanced { get; set; } = new();
}

/// <summary>
/// General application settings
/// </summary>
public class GeneralSettings
{
    /// <summary>
    /// Default mount path for images
    /// </summary>
    public string DefaultMountPath { get; set; } = @"C:\Mount";

    /// <summary>
    /// Default scratch directory
    /// </summary>
    public string DefaultScratchPath { get; set; } = @"C:\Scratch";

    /// <summary>
    /// Default log directory
    /// </summary>
    public string DefaultLogPath { get; set; } = @"C:\DeployForge\Logs";

    /// <summary>
    /// Whether to automatically create mount directories
    /// </summary>
    public bool AutoCreateDirectories { get; set; } = true;

    /// <summary>
    /// Logging level (Information, Debug, Warning, Error)
    /// </summary>
    public string LogLevel { get; set; } = "Information";

    /// <summary>
    /// Maximum log file size in MB
    /// </summary>
    public int MaxLogFileSizeMB { get; set; } = 100;

    /// <summary>
    /// Number of log files to retain
    /// </summary>
    public int LogRetentionCount { get; set; } = 10;
}

/// <summary>
/// Image operation settings
/// </summary>
public class ImageOperationSettings
{
    /// <summary>
    /// Default image index to use (1-based)
    /// </summary>
    public int DefaultImageIndex { get; set; } = 1;

    /// <summary>
    /// Whether to verify image integrity before operations
    /// </summary>
    public bool VerifyIntegrityBeforeOperation { get; set; } = true;

    /// <summary>
    /// Whether to optimize images after modifications
    /// </summary>
    public bool AutoOptimizeAfterModification { get; set; } = true;

    /// <summary>
    /// Whether to create checkpoints automatically
    /// </summary>
    public bool AutoCreateCheckpoints { get; set; } = true;

    /// <summary>
    /// Checkpoint interval in minutes (0 = disabled)
    /// </summary>
    public int CheckpointIntervalMinutes { get; set; } = 30;

    /// <summary>
    /// Default WIM compression type (None, Fast, Maximum, LZX, LZMS)
    /// </summary>
    public string DefaultCompressionType { get; set; } = "Maximum";

    /// <summary>
    /// Whether to split WIM files over 4GB
    /// </summary>
    public bool AutoSplitLargeWim { get; set; } = true;

    /// <summary>
    /// Split size in MB
    /// </summary>
    public int WimSplitSizeMB { get; set; } = 4000;
}

/// <summary>
/// Deployment settings
/// </summary>
public class DeploymentSettings
{
    /// <summary>
    /// Default deployment method (USB, Network, ISO)
    /// </summary>
    public string DefaultDeploymentMethod { get; set; } = "USB";

    /// <summary>
    /// Whether to verify deployment after completion
    /// </summary>
    public bool VerifyAfterDeployment { get; set; } = true;

    /// <summary>
    /// Whether to eject media after deployment
    /// </summary>
    public bool AutoEjectAfterDeployment { get; set; } = true;

    /// <summary>
    /// Network deployment share path
    /// </summary>
    public string NetworkSharePath { get; set; } = string.Empty;

    /// <summary>
    /// Network deployment credentials (encrypted)
    /// </summary>
    public string NetworkCredentials { get; set; } = string.Empty;

    /// <summary>
    /// ISO volume label
    /// </summary>
    public string IsoVolumeLabel { get; set; } = "DEPLOYFORGE";

    /// <summary>
    /// Whether to make ISO bootable
    /// </summary>
    public bool CreateBootableIso { get; set; } = true;
}

/// <summary>
/// Backup and snapshot settings
/// </summary>
public class BackupSettings
{
    /// <summary>
    /// Default backup location
    /// </summary>
    public string DefaultBackupPath { get; set; } = @"C:\DeployForge\Backups";

    /// <summary>
    /// Whether to automatically backup before major operations
    /// </summary>
    public bool AutoBackupBeforeOperation { get; set; } = true;

    /// <summary>
    /// Backup retention policy (days, 0 = unlimited)
    /// </summary>
    public int BackupRetentionDays { get; set; } = 30;

    /// <summary>
    /// Maximum number of backups to keep per image
    /// </summary>
    public int MaxBackupsPerImage { get; set; } = 5;

    /// <summary>
    /// Whether to compress backups
    /// </summary>
    public bool CompressBackups { get; set; } = true;

    /// <summary>
    /// Whether to verify backup integrity after creation
    /// </summary>
    public bool VerifyBackupIntegrity { get; set; } = true;

    /// <summary>
    /// Whether to enable incremental backups
    /// </summary>
    public bool EnableIncrementalBackups { get; set; } = true;
}

/// <summary>
/// Workflow execution settings
/// </summary>
public class WorkflowSettings
{
    /// <summary>
    /// Whether to continue workflow on non-critical errors
    /// </summary>
    public bool ContinueOnNonCriticalErrors { get; set; } = true;

    /// <summary>
    /// Maximum parallel workflow steps
    /// </summary>
    public int MaxParallelSteps { get; set; } = 3;

    /// <summary>
    /// Step timeout in minutes (0 = no timeout)
    /// </summary>
    public int StepTimeoutMinutes { get; set; } = 60;

    /// <summary>
    /// Whether to send notifications on workflow completion
    /// </summary>
    public bool SendCompletionNotifications { get; set; } = true;

    /// <summary>
    /// Notification email addresses
    /// </summary>
    public List<string> NotificationEmails { get; set; } = new();

    /// <summary>
    /// Whether to automatically retry failed steps
    /// </summary>
    public bool AutoRetryFailedSteps { get; set; } = true;

    /// <summary>
    /// Maximum retry attempts
    /// </summary>
    public int MaxRetryAttempts { get; set; } = 3;
}

/// <summary>
/// Advanced settings
/// </summary>
public class AdvancedSettings
{
    /// <summary>
    /// Enable experimental features
    /// </summary>
    public bool EnableExperimentalFeatures { get; set; } = false;

    /// <summary>
    /// Enable detailed diagnostics
    /// </summary>
    public bool EnableDetailedDiagnostics { get; set; } = false;

    /// <summary>
    /// Maximum concurrent operations
    /// </summary>
    public int MaxConcurrentOperations { get; set; } = 2;

    /// <summary>
    /// Memory limit in MB (0 = no limit)
    /// </summary>
    public int MemoryLimitMB { get; set; } = 0;

    /// <summary>
    /// Temp file cleanup policy (Immediate, OnCompletion, Manual)
    /// </summary>
    public string TempFileCleanupPolicy { get; set; } = "OnCompletion";

    /// <summary>
    /// Cache size in MB
    /// </summary>
    public int CacheSizeMB { get; set; } = 500;

    /// <summary>
    /// Cache expiration in hours
    /// </summary>
    public int CacheExpirationHours { get; set; } = 24;

    /// <summary>
    /// Custom DISM arguments
    /// </summary>
    public string CustomDismArguments { get; set; } = string.Empty;

    /// <summary>
    /// Performance monitoring enabled
    /// </summary>
    public bool EnablePerformanceMonitoring { get; set; } = true;
}

// Request/Response Models

/// <summary>
/// Request to create a new configuration profile
/// </summary>
public class CreateProfileRequest
{
    public ConfigurationProfile Profile { get; set; } = new();
}

/// <summary>
/// Request to update an existing profile
/// </summary>
public class UpdateProfileRequest
{
    public ConfigurationProfile Profile { get; set; } = new();
}

/// <summary>
/// Request to set a profile as default
/// </summary>
public class SetDefaultProfileRequest
{
    public string ProfileId { get; set; } = string.Empty;
}

/// <summary>
/// Request to export a profile
/// </summary>
public class ExportProfileRequest
{
    public string DestinationPath { get; set; } = string.Empty;
}

/// <summary>
/// Request to import a profile
/// </summary>
public class ImportProfileRequest
{
    public string FilePath { get; set; } = string.Empty;
    public bool SetAsDefault { get; set; } = false;
}

/// <summary>
/// Request to apply profile overrides for an operation
/// </summary>
public class ApplyProfileOverrideRequest
{
    public string ProfileId { get; set; } = string.Empty;
    public Dictionary<string, object> Overrides { get; set; } = new();
}
