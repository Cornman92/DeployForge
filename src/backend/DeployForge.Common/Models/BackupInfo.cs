namespace DeployForge.Common.Models;

/// <summary>
/// Information about an image backup
/// </summary>
public class BackupInfo
{
    /// <summary>
    /// Unique backup identifier
    /// </summary>
    public string BackupId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Original image path
    /// </summary>
    public string OriginalImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Backup file path
    /// </summary>
    public string BackupPath { get; set; } = string.Empty;

    /// <summary>
    /// Backup type
    /// </summary>
    public BackupType Type { get; set; }

    /// <summary>
    /// Backup format
    /// </summary>
    public ImageFormat Format { get; set; }

    /// <summary>
    /// Backup creation date
    /// </summary>
    public DateTime CreatedDate { get; set; }

    /// <summary>
    /// Backup size in bytes
    /// </summary>
    public long Size { get; set; }

    /// <summary>
    /// Backup description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Backup tags for organization
    /// </summary>
    public List<string> Tags { get; set; } = new();

    /// <summary>
    /// Is this backup compressed
    /// </summary>
    public bool IsCompressed { get; set; }

    /// <summary>
    /// Backup status
    /// </summary>
    public BackupStatus Status { get; set; }

    /// <summary>
    /// Parent backup ID (for incremental backups)
    /// </summary>
    public string? ParentBackupId { get; set; }

    /// <summary>
    /// Backup metadata
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();
}

/// <summary>
/// Backup types
/// </summary>
public enum BackupType
{
    /// <summary>
    /// Full backup (complete image copy)
    /// </summary>
    Full,

    /// <summary>
    /// Incremental backup (only changes since last backup)
    /// </summary>
    Incremental,

    /// <summary>
    /// Differential backup (changes since last full backup)
    /// </summary>
    Differential,

    /// <summary>
    /// Snapshot (point-in-time reference)
    /// </summary>
    Snapshot
}

/// <summary>
/// Backup status
/// </summary>
public enum BackupStatus
{
    /// <summary>
    /// Backup is valid and available
    /// </summary>
    Available,

    /// <summary>
    /// Backup is being created
    /// </summary>
    Creating,

    /// <summary>
    /// Backup is being restored
    /// </summary>
    Restoring,

    /// <summary>
    /// Backup is being verified
    /// </summary>
    Verifying,

    /// <summary>
    /// Backup is corrupted
    /// </summary>
    Corrupted,

    /// <summary>
    /// Backup file is missing
    /// </summary>
    Missing
}

/// <summary>
/// Request to create a backup
/// </summary>
public class CreateBackupRequest
{
    /// <summary>
    /// Image path to backup
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Image index (for WIM files)
    /// </summary>
    public int ImageIndex { get; set; } = 1;

    /// <summary>
    /// Backup destination path
    /// </summary>
    public string BackupPath { get; set; } = string.Empty;

    /// <summary>
    /// Backup type
    /// </summary>
    public BackupType Type { get; set; } = BackupType.Full;

    /// <summary>
    /// Backup description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Tags for organization
    /// </summary>
    public List<string> Tags { get; set; } = new();

    /// <summary>
    /// Use compression
    /// </summary>
    public bool UseCompression { get; set; } = true;

    /// <summary>
    /// Verify backup after creation
    /// </summary>
    public bool VerifyBackup { get; set; } = true;

    /// <summary>
    /// Parent backup ID (for incremental/differential)
    /// </summary>
    public string? ParentBackupId { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();
}

/// <summary>
/// Request to restore from backup
/// </summary>
public class RestoreBackupRequest
{
    /// <summary>
    /// Backup ID to restore
    /// </summary>
    public string BackupId { get; set; } = string.Empty;

    /// <summary>
    /// Destination path for restored image
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Overwrite existing file
    /// </summary>
    public bool Overwrite { get; set; } = false;

    /// <summary>
    /// Verify integrity after restore
    /// </summary>
    public bool VerifyIntegrity { get; set; } = true;

    /// <summary>
    /// Restore point-in-time (for incremental backups)
    /// </summary>
    public DateTime? RestorePointInTime { get; set; }
}

/// <summary>
/// Result of backup operation
/// </summary>
public class BackupOperationResult
{
    /// <summary>
    /// Whether operation succeeded
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Backup information
    /// </summary>
    public BackupInfo? BackupInfo { get; set; }

    /// <summary>
    /// Operation duration
    /// </summary>
    public TimeSpan Duration { get; set; }

    /// <summary>
    /// Result message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Error message (if failed)
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Backup verification result
    /// </summary>
    public VerificationResult? VerificationResult { get; set; }
}

/// <summary>
/// Verification result
/// </summary>
public class VerificationResult
{
    /// <summary>
    /// Is backup valid
    /// </summary>
    public bool IsValid { get; set; }

    /// <summary>
    /// Verification method used
    /// </summary>
    public string Method { get; set; } = string.Empty;

    /// <summary>
    /// Checksum (if computed)
    /// </summary>
    public string? Checksum { get; set; }

    /// <summary>
    /// Verification message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Issues found during verification
    /// </summary>
    public List<string> Issues { get; set; } = new();
}

/// <summary>
/// Snapshot information
/// </summary>
public class SnapshotInfo
{
    /// <summary>
    /// Snapshot ID
    /// </summary>
    public string SnapshotId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Snapshot name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Snapshot description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Creation date
    /// </summary>
    public DateTime CreatedDate { get; set; }

    /// <summary>
    /// Snapshot state data
    /// </summary>
    public Dictionary<string, object> State { get; set; } = new();

    /// <summary>
    /// Parent snapshot ID
    /// </summary>
    public string? ParentSnapshotId { get; set; }

    /// <summary>
    /// Snapshot metadata
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();
}

/// <summary>
/// Request to create a snapshot
/// </summary>
public class CreateSnapshotRequest
{
    /// <summary>
    /// Image path
    /// </summary>
    public string ImagePath { get; set; } = string.Empty;

    /// <summary>
    /// Snapshot name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Snapshot description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, string> Metadata { get; set; } = new();
}

/// <summary>
/// Request to restore from snapshot
/// </summary>
public class RestoreSnapshotRequest
{
    /// <summary>
    /// Snapshot ID to restore
    /// </summary>
    public string SnapshotId { get; set; } = string.Empty;

    /// <summary>
    /// Delete newer snapshots after restore
    /// </summary>
    public bool DeleteNewerSnapshots { get; set; } = false;
}

/// <summary>
/// Backup chain information (for incremental backups)
/// </summary>
public class BackupChain
{
    /// <summary>
    /// Chain ID
    /// </summary>
    public string ChainId { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Base full backup
    /// </summary>
    public BackupInfo BaseBackup { get; set; } = new();

    /// <summary>
    /// Incremental/differential backups
    /// </summary>
    public List<BackupInfo> IncrementalBackups { get; set; } = new();

    /// <summary>
    /// Total chain size
    /// </summary>
    public long TotalSize { get; set; }

    /// <summary>
    /// Is chain complete and valid
    /// </summary>
    public bool IsValid { get; set; }

    /// <summary>
    /// Last backup date
    /// </summary>
    public DateTime LastBackupDate { get; set; }
}
