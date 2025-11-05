using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using System.Runtime.Versioning;
using System.Security.Cryptography;
using System.Text.Json;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for backup and snapshot management
/// </summary>
[SupportedOSPlatform("windows")]
public class BackupService : IBackupService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<BackupService> _logger;
    private readonly string _backupMetadataPath;
    private readonly string _snapshotMetadataPath;

    public BackupService(
        DismManager dismManager,
        ILogger<BackupService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;

        // Store metadata in user's AppData
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        var appPath = Path.Combine(appDataPath, "DeployForge");
        _backupMetadataPath = Path.Combine(appPath, "Backups");
        _snapshotMetadataPath = Path.Combine(appPath, "Snapshots");

        Directory.CreateDirectory(_backupMetadataPath);
        Directory.CreateDirectory(_snapshotMetadataPath);
    }

    public async Task<OperationResult<BackupOperationResult>> CreateBackupAsync(
        CreateBackupRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var startTime = DateTime.UtcNow;
            var result = new BackupOperationResult();

            try
            {
                _logger.LogInformation("Creating {Type} backup of {Image} to {Backup}",
                    request.Type, request.ImagePath, request.BackupPath);

                if (!File.Exists(request.ImagePath))
                {
                    return OperationResult<BackupOperationResult>.FailureResult("Source image not found");
                }

                // Create backup info
                var backupInfo = new BackupInfo
                {
                    BackupId = Guid.NewGuid().ToString(),
                    OriginalImagePath = request.ImagePath,
                    BackupPath = request.BackupPath,
                    Type = request.Type,
                    Format = DetectImageFormat(request.ImagePath),
                    CreatedDate = DateTime.UtcNow,
                    Description = request.Description,
                    Tags = request.Tags,
                    IsCompressed = request.UseCompression,
                    Status = BackupStatus.Creating,
                    ParentBackupId = request.ParentBackupId,
                    Metadata = request.Metadata
                };

                // Perform backup based on type
                OperationResult backupResult;

                switch (request.Type)
                {
                    case BackupType.Full:
                        backupResult = CreateFullBackup(request, backupInfo, cancellationToken);
                        break;

                    case BackupType.Incremental:
                    case BackupType.Differential:
                        backupResult = CreateIncrementalBackup(request, backupInfo, cancellationToken);
                        break;

                    case BackupType.Snapshot:
                        backupResult = CreateSnapshotBackup(request, backupInfo, cancellationToken);
                        break;

                    default:
                        return OperationResult<BackupOperationResult>.FailureResult("Unknown backup type");
                }

                if (!backupResult.Success)
                {
                    return OperationResult<BackupOperationResult>.FailureResult(
                        backupResult.ErrorMessage ?? "Backup failed");
                }

                // Update backup info with file size
                if (File.Exists(request.BackupPath))
                {
                    backupInfo.Size = new FileInfo(request.BackupPath).Length;
                }

                backupInfo.Status = BackupStatus.Available;

                // Verify if requested
                if (request.VerifyBackup)
                {
                    _logger.LogInformation("Verifying backup {BackupId}", backupInfo.BackupId);
                    var verifyResult = VerifyBackupInternal(backupInfo, cancellationToken);
                    result.VerificationResult = verifyResult;

                    if (!verifyResult.IsValid)
                    {
                        backupInfo.Status = BackupStatus.Corrupted;
                    }
                }

                // Save backup metadata
                SaveBackupMetadata(backupInfo);

                result.Success = true;
                result.BackupInfo = backupInfo;
                result.Duration = DateTime.UtcNow - startTime;
                result.Message = $"Successfully created {request.Type} backup in {result.Duration.TotalSeconds:F1}s";

                _logger.LogInformation("Backup completed: {Message}", result.Message);

                return OperationResult<BackupOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create backup");
                result.Success = false;
                result.ErrorMessage = ex.Message;
                result.Duration = DateTime.UtcNow - startTime;
                return OperationResult<BackupOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<BackupOperationResult>> RestoreBackupAsync(
        RestoreBackupRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var startTime = DateTime.UtcNow;
            var result = new BackupOperationResult();

            try
            {
                _logger.LogInformation("Restoring backup {BackupId} to {Destination}",
                    request.BackupId, request.DestinationPath);

                // Load backup metadata
                var backupInfo = LoadBackupMetadata(request.BackupId);
                if (backupInfo == null)
                {
                    return OperationResult<BackupOperationResult>.FailureResult("Backup not found");
                }

                if (!File.Exists(backupInfo.BackupPath))
                {
                    backupInfo.Status = BackupStatus.Missing;
                    SaveBackupMetadata(backupInfo);
                    return OperationResult<BackupOperationResult>.FailureResult("Backup file not found");
                }

                // Check if destination exists
                if (File.Exists(request.DestinationPath) && !request.Overwrite)
                {
                    return OperationResult<BackupOperationResult>.FailureResult(
                        "Destination file exists and overwrite is false");
                }

                backupInfo.Status = BackupStatus.Restoring;
                SaveBackupMetadata(backupInfo);

                // Restore backup
                File.Copy(backupInfo.BackupPath, request.DestinationPath, request.Overwrite);

                // Verify if requested
                if (request.VerifyIntegrity)
                {
                    _logger.LogInformation("Verifying restored image");
                    var verifyResult = VerifyImageIntegrity(request.DestinationPath);
                    result.VerificationResult = verifyResult;
                }

                backupInfo.Status = BackupStatus.Available;
                SaveBackupMetadata(backupInfo);

                result.Success = true;
                result.BackupInfo = backupInfo;
                result.Duration = DateTime.UtcNow - startTime;
                result.Message = $"Successfully restored backup in {result.Duration.TotalSeconds:F1}s";

                return OperationResult<BackupOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restore backup");
                result.Success = false;
                result.ErrorMessage = ex.Message;
                result.Duration = DateTime.UtcNow - startTime;
                return OperationResult<BackupOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<BackupInfo>>> GetBackupsAsync(
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var backups = new List<BackupInfo>();
                var metadataFiles = Directory.GetFiles(_backupMetadataPath, "*.json");

                foreach (var file in metadataFiles)
                {
                    var backup = LoadBackupMetadata(Path.GetFileNameWithoutExtension(file));
                    if (backup != null)
                    {
                        // Update status if file is missing
                        if (!File.Exists(backup.BackupPath))
                        {
                            backup.Status = BackupStatus.Missing;
                            SaveBackupMetadata(backup);
                        }
                        backups.Add(backup);
                    }
                }

                return OperationResult<List<BackupInfo>>.SuccessResult(
                    backups.OrderByDescending(b => b.CreatedDate).ToList());
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get backups");
                return OperationResult<List<BackupInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<BackupInfo>> GetBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var backup = LoadBackupMetadata(backupId);
                if (backup == null)
                {
                    return OperationResult<BackupInfo>.FailureResult("Backup not found");
                }

                return OperationResult<BackupInfo>.SuccessResult(backup);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get backup");
                return OperationResult<BackupInfo>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> DeleteBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var backup = LoadBackupMetadata(backupId);
                if (backup == null)
                {
                    return OperationResult.FailureResult("Backup not found");
                }

                // Delete backup file
                if (File.Exists(backup.BackupPath))
                {
                    File.Delete(backup.BackupPath);
                }

                // Delete metadata
                var metadataFile = Path.Combine(_backupMetadataPath, $"{backupId}.json");
                if (File.Exists(metadataFile))
                {
                    File.Delete(metadataFile);
                }

                _logger.LogInformation("Deleted backup {BackupId}", backupId);
                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to delete backup");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<VerificationResult>> VerifyBackupAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var backup = LoadBackupMetadata(backupId);
                if (backup == null)
                {
                    return OperationResult<VerificationResult>.FailureResult("Backup not found");
                }

                backup.Status = BackupStatus.Verifying;
                SaveBackupMetadata(backup);

                var result = VerifyBackupInternal(backup, cancellationToken);

                backup.Status = result.IsValid ? BackupStatus.Available : BackupStatus.Corrupted;
                SaveBackupMetadata(backup);

                return OperationResult<VerificationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to verify backup");
                return OperationResult<VerificationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<BackupChain>> GetBackupChainAsync(
        string backupId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var backup = LoadBackupMetadata(backupId);
                if (backup == null)
                {
                    return OperationResult<BackupChain>.FailureResult("Backup not found");
                }

                // Build backup chain
                var chain = new BackupChain();

                // Find base backup
                var current = backup;
                while (current.ParentBackupId != null)
                {
                    var parent = LoadBackupMetadata(current.ParentBackupId);
                    if (parent == null) break;
                    current = parent;
                }

                chain.BaseBackup = current;

                // Find all incremental backups
                var allBackups = GetBackupsAsync(cancellationToken).Result;
                if (allBackups.Success && allBackups.Data != null)
                {
                    chain.IncrementalBackups = allBackups.Data
                        .Where(b => b.ParentBackupId == chain.BaseBackup.BackupId)
                        .OrderBy(b => b.CreatedDate)
                        .ToList();
                }

                chain.TotalSize = chain.BaseBackup.Size +
                    chain.IncrementalBackups.Sum(b => b.Size);
                chain.IsValid = chain.IncrementalBackups.All(b => b.Status == BackupStatus.Available);
                chain.LastBackupDate = chain.IncrementalBackups.Any()
                    ? chain.IncrementalBackups.Max(b => b.CreatedDate)
                    : chain.BaseBackup.CreatedDate;

                return OperationResult<BackupChain>.SuccessResult(chain);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get backup chain");
                return OperationResult<BackupChain>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<SnapshotInfo>> CreateSnapshotAsync(
        CreateSnapshotRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Creating snapshot of {Image}", request.ImagePath);

                if (!File.Exists(request.ImagePath))
                {
                    return OperationResult<SnapshotInfo>.FailureResult("Image file not found");
                }

                var snapshot = new SnapshotInfo
                {
                    SnapshotId = Guid.NewGuid().ToString(),
                    ImagePath = request.ImagePath,
                    Name = request.Name,
                    Description = request.Description,
                    CreatedDate = DateTime.UtcNow,
                    Metadata = request.Metadata
                };

                // Capture current state
                snapshot.State["FileSize"] = new FileInfo(request.ImagePath).Length;
                snapshot.State["LastModified"] = File.GetLastWriteTimeUtc(request.ImagePath);
                snapshot.State["Checksum"] = CalculateChecksum(request.ImagePath);

                // Save snapshot metadata
                SaveSnapshotMetadata(snapshot);

                _logger.LogInformation("Created snapshot {SnapshotId}", snapshot.SnapshotId);
                return OperationResult<SnapshotInfo>.SuccessResult(snapshot);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create snapshot");
                return OperationResult<SnapshotInfo>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> RestoreSnapshotAsync(
        RestoreSnapshotRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Restoring snapshot {SnapshotId}", request.SnapshotId);

                var snapshot = LoadSnapshotMetadata(request.SnapshotId);
                if (snapshot == null)
                {
                    return OperationResult.FailureResult("Snapshot not found");
                }

                // Snapshot restoration would require more complex logic
                // For now, this is a placeholder
                _logger.LogWarning("Snapshot restoration requires additional implementation");

                return OperationResult.FailureResult(
                    "Snapshot restoration not yet fully implemented");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restore snapshot");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<SnapshotInfo>>> GetSnapshotsAsync(
        string imagePath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var snapshots = new List<SnapshotInfo>();
                var metadataFiles = Directory.GetFiles(_snapshotMetadataPath, "*.json");

                foreach (var file in metadataFiles)
                {
                    var snapshot = LoadSnapshotMetadata(Path.GetFileNameWithoutExtension(file));
                    if (snapshot != null && snapshot.ImagePath == imagePath)
                    {
                        snapshots.Add(snapshot);
                    }
                }

                return OperationResult<List<SnapshotInfo>>.SuccessResult(
                    snapshots.OrderByDescending(s => s.CreatedDate).ToList());
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get snapshots");
                return OperationResult<List<SnapshotInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> DeleteSnapshotAsync(
        string snapshotId,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var metadataFile = Path.Combine(_snapshotMetadataPath, $"{snapshotId}.json");
                if (File.Exists(metadataFile))
                {
                    File.Delete(metadataFile);
                }

                _logger.LogInformation("Deleted snapshot {SnapshotId}", snapshotId);
                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to delete snapshot");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private ImageFormat DetectImageFormat(string filePath)
    {
        var extension = Path.GetExtension(filePath).ToLowerInvariant();
        return extension switch
        {
            ".wim" => ImageFormat.WIM,
            ".esd" => ImageFormat.ESD,
            ".vhd" => ImageFormat.VHD,
            ".vhdx" => ImageFormat.VHDX,
            _ => ImageFormat.WIM
        };
    }

    private OperationResult CreateFullBackup(
        CreateBackupRequest request,
        BackupInfo backupInfo,
        CancellationToken cancellationToken)
    {
        try
        {
            // Use DISM export for full backup
            var exportResult = _dismManager.ExportImage(
                request.ImagePath,
                request.ImageIndex,
                request.BackupPath,
                1,
                compress: request.UseCompression);

            return exportResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create full backup");
            return OperationResult.ExceptionResult(ex);
        }
    }

    private OperationResult CreateIncrementalBackup(
        CreateBackupRequest request,
        BackupInfo backupInfo,
        CancellationToken cancellationToken)
    {
        try
        {
            // Incremental backups would require tracking changes
            // For now, fall back to full backup
            _logger.LogWarning("Incremental backup not fully implemented, creating full backup");
            return CreateFullBackup(request, backupInfo, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create incremental backup");
            return OperationResult.ExceptionResult(ex);
        }
    }

    private OperationResult CreateSnapshotBackup(
        CreateBackupRequest request,
        BackupInfo backupInfo,
        CancellationToken cancellationToken)
    {
        try
        {
            // Snapshot backup just copies the file
            File.Copy(request.ImagePath, request.BackupPath, true);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create snapshot backup");
            return OperationResult.ExceptionResult(ex);
        }
    }

    private VerificationResult VerifyBackupInternal(BackupInfo backup, CancellationToken cancellationToken)
    {
        var result = new VerificationResult
        {
            Method = "File existence and checksum"
        };

        try
        {
            if (!File.Exists(backup.BackupPath))
            {
                result.IsValid = false;
                result.Message = "Backup file not found";
                result.Issues.Add("File missing");
                return result;
            }

            // Calculate checksum
            var checksum = CalculateChecksum(backup.BackupPath);
            result.Checksum = checksum;

            result.IsValid = true;
            result.Message = "Backup verification successful";
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to verify backup");
            result.IsValid = false;
            result.Message = $"Verification failed: {ex.Message}";
            result.Issues.Add(ex.Message);
            return result;
        }
    }

    private VerificationResult VerifyImageIntegrity(string imagePath)
    {
        var result = new VerificationResult
        {
            Method = "DISM image info"
        };

        try
        {
            // Use DISM to verify image
            var imageInfo = _dismManager.GetImageInfo(imagePath);

            if (imageInfo.Success)
            {
                result.IsValid = true;
                result.Message = "Image verification successful";
            }
            else
            {
                result.IsValid = false;
                result.Message = "Image verification failed";
                result.Issues.Add(imageInfo.ErrorMessage ?? "Unknown error");
            }

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to verify image");
            result.IsValid = false;
            result.Message = $"Verification failed: {ex.Message}";
            result.Issues.Add(ex.Message);
            return result;
        }
    }

    private string CalculateChecksum(string filePath)
    {
        try
        {
            using var sha256 = SHA256.Create();
            using var stream = File.OpenRead(filePath);
            var hash = sha256.ComputeHash(stream);
            return Convert.ToBase64String(hash);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to calculate checksum");
            return string.Empty;
        }
    }

    private void SaveBackupMetadata(BackupInfo backup)
    {
        try
        {
            var metadataFile = Path.Combine(_backupMetadataPath, $"{backup.BackupId}.json");
            var json = JsonSerializer.Serialize(backup, new JsonSerializerOptions
            {
                WriteIndented = true
            });
            File.WriteAllText(metadataFile, json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save backup metadata");
        }
    }

    private BackupInfo? LoadBackupMetadata(string backupId)
    {
        try
        {
            var metadataFile = Path.Combine(_backupMetadataPath, $"{backupId}.json");
            if (!File.Exists(metadataFile))
            {
                return null;
            }

            var json = File.ReadAllText(metadataFile);
            return JsonSerializer.Deserialize<BackupInfo>(json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load backup metadata");
            return null;
        }
    }

    private void SaveSnapshotMetadata(SnapshotInfo snapshot)
    {
        try
        {
            var metadataFile = Path.Combine(_snapshotMetadataPath, $"{snapshot.SnapshotId}.json");
            var json = JsonSerializer.Serialize(snapshot, new JsonSerializerOptions
            {
                WriteIndented = true
            });
            File.WriteAllText(metadataFile, json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save snapshot metadata");
        }
    }

    private SnapshotInfo? LoadSnapshotMetadata(string snapshotId)
    {
        try
        {
            var metadataFile = Path.Combine(_snapshotMetadataPath, $"{snapshotId}.json");
            if (!File.Exists(metadataFile))
            {
                return null;
            }

            var json = File.ReadAllText(metadataFile);
            return JsonSerializer.Deserialize<SnapshotInfo>(json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load snapshot metadata");
            return null;
        }
    }

    #endregion
}
