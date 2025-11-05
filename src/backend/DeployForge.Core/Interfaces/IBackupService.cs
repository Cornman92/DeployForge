using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for backup and snapshot management
/// </summary>
public interface IBackupService
{
    /// <summary>
    /// Create a backup of an image
    /// </summary>
    /// <param name="request">Backup request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Backup operation result</returns>
    Task<OperationResult<BackupOperationResult>> CreateBackupAsync(
        CreateBackupRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Restore from a backup
    /// </summary>
    /// <param name="request">Restore request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Restore operation result</returns>
    Task<OperationResult<BackupOperationResult>> RestoreBackupAsync(
        RestoreBackupRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get all backups
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of backups</returns>
    Task<OperationResult<List<BackupInfo>>> GetBackupsAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get backup by ID
    /// </summary>
    /// <param name="backupId">Backup ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Backup information</returns>
    Task<OperationResult<BackupInfo>> GetBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a backup
    /// </summary>
    /// <param name="backupId">Backup ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> DeleteBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Verify backup integrity
    /// </summary>
    /// <param name="backupId">Backup ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Verification result</returns>
    Task<OperationResult<VerificationResult>> VerifyBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get backup chain information
    /// </summary>
    /// <param name="backupId">Any backup ID in the chain</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Backup chain</returns>
    Task<OperationResult<BackupChain>> GetBackupChainAsync(
        string backupId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Create a snapshot
    /// </summary>
    /// <param name="request">Snapshot request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Snapshot information</returns>
    Task<OperationResult<SnapshotInfo>> CreateSnapshotAsync(
        CreateSnapshotRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Restore from snapshot
    /// </summary>
    /// <param name="request">Restore request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> RestoreSnapshotAsync(
        RestoreSnapshotRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get all snapshots for an image
    /// </summary>
    /// <param name="imagePath">Image path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of snapshots</returns>
    Task<OperationResult<List<SnapshotInfo>>> GetSnapshotsAsync(
        string imagePath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a snapshot
    /// </summary>
    /// <param name="snapshotId">Snapshot ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> DeleteSnapshotAsync(
        string snapshotId,
        CancellationToken cancellationToken = default);
}
