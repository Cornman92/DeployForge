using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class BackupController : ControllerBase
{
    private readonly IBackupService _backupService;
    private readonly ILogger<BackupController> _logger;

    public BackupController(
        IBackupService backupService,
        ILogger<BackupController> logger)
    {
        _backupService = backupService;
        _logger = logger;
    }

    /// <summary>
    /// Create a backup
    /// </summary>
    [HttpPost("create")]
    public async Task<ActionResult<BackupOperationResult>> CreateBackup(
        [FromBody] CreateBackupRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating backup of {Image}", request.ImagePath);

        if (string.IsNullOrWhiteSpace(request.ImagePath))
        {
            return BadRequest("Image path is required");
        }

        if (string.IsNullOrWhiteSpace(request.BackupPath))
        {
            return BadRequest("Backup path is required");
        }

        var result = await _backupService.CreateBackupAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to create backup: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Restore from backup
    /// </summary>
    [HttpPost("restore")]
    public async Task<ActionResult<BackupOperationResult>> RestoreBackup(
        [FromBody] RestoreBackupRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Restoring backup {BackupId}", request.BackupId);

        if (string.IsNullOrWhiteSpace(request.BackupId))
        {
            return BadRequest("Backup ID is required");
        }

        if (string.IsNullOrWhiteSpace(request.DestinationPath))
        {
            return BadRequest("Destination path is required");
        }

        var result = await _backupService.RestoreBackupAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to restore backup: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get all backups
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<BackupInfo>>> GetBackups(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting all backups");

        var result = await _backupService.GetBackupsAsync(cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get backups: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get backup by ID
    /// </summary>
    [HttpGet("{backupId}")]
    public async Task<ActionResult<BackupInfo>> GetBackup(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting backup {BackupId}", backupId);

        if (string.IsNullOrWhiteSpace(backupId))
        {
            return BadRequest("Backup ID is required");
        }

        var result = await _backupService.GetBackupAsync(backupId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get backup: {Error}", result.ErrorMessage);
            return StatusCode(404, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Delete a backup
    /// </summary>
    [HttpDelete("{backupId}")]
    public async Task<ActionResult> DeleteBackup(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting backup {BackupId}", backupId);

        if (string.IsNullOrWhiteSpace(backupId))
        {
            return BadRequest("Backup ID is required");
        }

        var result = await _backupService.DeleteBackupAsync(backupId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to delete backup: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Backup deleted successfully" });
    }

    /// <summary>
    /// Verify backup integrity
    /// </summary>
    [HttpPost("{backupId}/verify")]
    public async Task<ActionResult<VerificationResult>> VerifyBackup(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Verifying backup {BackupId}", backupId);

        if (string.IsNullOrWhiteSpace(backupId))
        {
            return BadRequest("Backup ID is required");
        }

        var result = await _backupService.VerifyBackupAsync(backupId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to verify backup: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get backup chain
    /// </summary>
    [HttpGet("{backupId}/chain")]
    public async Task<ActionResult<BackupChain>> GetBackupChain(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting backup chain for {BackupId}", backupId);

        if (string.IsNullOrWhiteSpace(backupId))
        {
            return BadRequest("Backup ID is required");
        }

        var result = await _backupService.GetBackupChainAsync(backupId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get backup chain: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Create a snapshot
    /// </summary>
    [HttpPost("snapshots/create")]
    public async Task<ActionResult<SnapshotInfo>> CreateSnapshot(
        [FromBody] CreateSnapshotRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating snapshot of {Image}", request.ImagePath);

        if (string.IsNullOrWhiteSpace(request.ImagePath))
        {
            return BadRequest("Image path is required");
        }

        if (string.IsNullOrWhiteSpace(request.Name))
        {
            return BadRequest("Snapshot name is required");
        }

        var result = await _backupService.CreateSnapshotAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to create snapshot: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Restore from snapshot
    /// </summary>
    [HttpPost("snapshots/restore")]
    public async Task<ActionResult> RestoreSnapshot(
        [FromBody] RestoreSnapshotRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Restoring snapshot {SnapshotId}", request.SnapshotId);

        if (string.IsNullOrWhiteSpace(request.SnapshotId))
        {
            return BadRequest("Snapshot ID is required");
        }

        var result = await _backupService.RestoreSnapshotAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to restore snapshot: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Snapshot restored successfully" });
    }

    /// <summary>
    /// Get snapshots for an image
    /// </summary>
    [HttpGet("snapshots")]
    public async Task<ActionResult<List<SnapshotInfo>>> GetSnapshots(
        [FromQuery] string imagePath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting snapshots for {Image}", imagePath);

        if (string.IsNullOrWhiteSpace(imagePath))
        {
            return BadRequest("Image path is required");
        }

        var result = await _backupService.GetSnapshotsAsync(imagePath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get snapshots: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Delete a snapshot
    /// </summary>
    [HttpDelete("snapshots/{snapshotId}")]
    public async Task<ActionResult> DeleteSnapshot(
        string snapshotId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting snapshot {SnapshotId}", snapshotId);

        if (string.IsNullOrWhiteSpace(snapshotId))
        {
            return BadRequest("Snapshot ID is required");
        }

        var result = await _backupService.DeleteSnapshotAsync(snapshotId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to delete snapshot: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Snapshot deleted successfully" });
    }
}
