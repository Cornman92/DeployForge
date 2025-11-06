using System.Collections.Concurrent;
using System.Diagnostics;
using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing batch operations with queue and parallel execution
/// </summary>
public class BatchOperationService : IBatchOperationService
{
    private readonly ILogger<BatchOperationService> _logger;
    private readonly IProgressService _progressService;
    private readonly IImageTemplateService _imageTemplateService;
    private readonly IAuditLogService _auditLogService;
    private readonly string _storageDirectory;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly ConcurrentDictionary<string, BatchOperation> _activeOperations;
    private readonly ConcurrentDictionary<string, CancellationTokenSource> _cancellationTokens;
    private readonly SemaphoreSlim _queueSemaphore;

    public BatchOperationService(
        ILogger<BatchOperationService> logger,
        IProgressService progressService,
        IImageTemplateService imageTemplateService,
        IAuditLogService auditLogService)
    {
        _logger = logger;
        _progressService = progressService;
        _imageTemplateService = imageTemplateService;
        _auditLogService = auditLogService;

        // Store batch operations in AppData\DeployForge\BatchOperations
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        _storageDirectory = Path.Combine(appDataPath, "DeployForge", "BatchOperations");
        Directory.CreateDirectory(_storageDirectory);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNameCaseInsensitive = true
        };

        _activeOperations = new ConcurrentDictionary<string, BatchOperation>();
        _cancellationTokens = new ConcurrentDictionary<string, CancellationTokenSource>();
        _queueSemaphore = new SemaphoreSlim(1, 1);

        _logger.LogInformation("Batch operation service initialized with storage at: {Path}", _storageDirectory);
    }

    public async Task<OperationResult<BatchOperation>> CreateBatchOperationAsync(
        CreateBatchOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Creating batch operation: {Name} ({Type})", request.Name, request.Type);

            var batchOperation = new BatchOperation
            {
                Name = request.Name,
                Description = request.Description,
                Type = request.Type,
                TargetImages = request.TargetImages,
                Configuration = request.Configuration,
                TemplateId = request.TemplateId,
                ProfileId = request.ProfileId,
                Priority = request.Priority,
                MaxParallelOperations = request.MaxParallelOperations,
                ContinueOnError = request.ContinueOnError,
                Status = BatchOperationStatus.Pending,
                Tags = request.Tags
            };

            // Calculate summary
            batchOperation.Summary.TotalImages = batchOperation.TargetImages.Count;

            // Save to storage
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            // Log to audit
            await _auditLogService.LogSuccessAsync(
                AuditCategory.System,
                "CreateBatchOperation",
                batchOperation.Id,
                $"Created batch operation '{request.Name}' with {request.TargetImages.Count} images",
                metadata: new Dictionary<string, object>
                {
                    ["BatchOperationId"] = batchOperation.Id,
                    ["Type"] = request.Type.ToString(),
                    ["ImageCount"] = request.TargetImages.Count
                },
                cancellationToken: cancellationToken);

            // Start immediately if requested
            if (request.StartImmediately)
            {
                _ = Task.Run(async () =>
                {
                    await StartBatchOperationAsync(batchOperation.Id, CancellationToken.None);
                }, CancellationToken.None);
            }

            _logger.LogInformation("Batch operation created: {Id}", batchOperation.Id);
            return OperationResult<BatchOperation>.SuccessResult(batchOperation);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create batch operation");
            return OperationResult<BatchOperation>.FailureResult($"Failed to create batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult<BatchOperation>> GetBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Check active operations first
            if (_activeOperations.TryGetValue(operationId, out var activeOp))
            {
                return OperationResult<BatchOperation>.SuccessResult(activeOp);
            }

            // Load from storage
            var batchOperation = await LoadBatchOperationAsync(operationId, cancellationToken);
            if (batchOperation == null)
            {
                return OperationResult<BatchOperation>.FailureResult($"Batch operation '{operationId}' not found");
            }

            return OperationResult<BatchOperation>.SuccessResult(batchOperation);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get batch operation {OperationId}", operationId);
            return OperationResult<BatchOperation>.FailureResult($"Failed to get batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult<BatchOperationQueryResult>> QueryBatchOperationsAsync(
        BatchOperationQuery query,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Querying batch operations");

            var allOperations = await LoadAllBatchOperationsAsync(cancellationToken);

            // Apply filters
            var filtered = allOperations.AsEnumerable();

            if (query.Status.HasValue)
                filtered = filtered.Where(o => o.Status == query.Status.Value);

            if (query.Type.HasValue)
                filtered = filtered.Where(o => o.Type == query.Type.Value);

            if (!string.IsNullOrEmpty(query.CreatedBy))
                filtered = filtered.Where(o => o.CreatedBy.Equals(query.CreatedBy, StringComparison.OrdinalIgnoreCase));

            if (!string.IsNullOrEmpty(query.Tag))
                filtered = filtered.Where(o => o.Tags.Contains(query.Tag, StringComparer.OrdinalIgnoreCase));

            if (query.StartDate.HasValue)
                filtered = filtered.Where(o => o.CreatedAt >= query.StartDate.Value);

            if (query.EndDate.HasValue)
                filtered = filtered.Where(o => o.CreatedAt <= query.EndDate.Value);

            // Sort
            filtered = query.SortDirection.ToLowerInvariant() == "asc"
                ? filtered.OrderBy(o => GetSortValue(o, query.SortBy))
                : filtered.OrderByDescending(o => GetSortValue(o, query.SortBy));

            var filteredList = filtered.ToList();
            var totalCount = filteredList.Count;

            // Paginate
            var paged = filteredList
                .Skip((query.PageNumber - 1) * query.PageSize)
                .Take(query.PageSize)
                .ToList();

            var totalPages = (int)Math.Ceiling(totalCount / (double)query.PageSize);

            var result = new BatchOperationQueryResult
            {
                Operations = paged,
                TotalCount = totalCount,
                PageNumber = query.PageNumber,
                PageSize = query.PageSize,
                TotalPages = totalPages,
                HasNextPage = query.PageNumber < totalPages,
                HasPreviousPage = query.PageNumber > 1
            };

            return OperationResult<BatchOperationQueryResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to query batch operations");
            return OperationResult<BatchOperationQueryResult>.FailureResult($"Query failed: {ex.Message}");
        }
    }

    public async Task<OperationResult> StartBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Starting batch operation: {OperationId}", operationId);

            var opResult = await GetBatchOperationAsync(operationId, cancellationToken);
            if (!opResult.Success || opResult.Data == null)
            {
                return OperationResult.FailureResult($"Batch operation '{operationId}' not found");
            }

            var batchOperation = opResult.Data;

            if (batchOperation.Status != BatchOperationStatus.Pending &&
                batchOperation.Status != BatchOperationStatus.Paused)
            {
                return OperationResult.FailureResult($"Batch operation is in '{batchOperation.Status}' state and cannot be started");
            }

            // Update status
            batchOperation.Status = BatchOperationStatus.Queued;
            batchOperation.StartedAt = DateTime.UtcNow;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            // Add to active operations
            _activeOperations[operationId] = batchOperation;

            // Create cancellation token
            var cts = new CancellationTokenSource();
            _cancellationTokens[operationId] = cts;

            // Start execution in background
            _ = Task.Run(async () => await ExecuteBatchOperationAsync(batchOperation, cts.Token), CancellationToken.None);

            await _auditLogService.LogSuccessAsync(
                AuditCategory.System,
                "StartBatchOperation",
                operationId,
                $"Started batch operation '{batchOperation.Name}'",
                cancellationToken: cancellationToken);

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start batch operation {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to start batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult> PauseBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_activeOperations.TryGetValue(operationId, out var batchOperation))
            {
                return OperationResult.FailureResult($"Batch operation '{operationId}' is not running");
            }

            if (batchOperation.Status != BatchOperationStatus.Running)
            {
                return OperationResult.FailureResult($"Batch operation is not in running state");
            }

            batchOperation.Status = BatchOperationStatus.Paused;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            _logger.LogInformation("Paused batch operation: {OperationId}", operationId);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to pause batch operation {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to pause batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult> ResumeBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_activeOperations.TryGetValue(operationId, out var batchOperation))
            {
                return OperationResult.FailureResult($"Batch operation '{operationId}' is not active");
            }

            if (batchOperation.Status != BatchOperationStatus.Paused)
            {
                return OperationResult.FailureResult($"Batch operation is not paused");
            }

            batchOperation.Status = BatchOperationStatus.Running;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            _logger.LogInformation("Resumed batch operation: {OperationId}", operationId);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to resume batch operation {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to resume batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult> CancelBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Cancelling batch operation: {OperationId}", operationId);

            if (_activeOperations.TryGetValue(operationId, out var batchOperation))
            {
                // Cancel the operation
                if (_cancellationTokens.TryGetValue(operationId, out var cts))
                {
                    cts.Cancel();
                }

                batchOperation.Status = BatchOperationStatus.Cancelled;
                await SaveBatchOperationAsync(batchOperation, cancellationToken);
            }

            await _auditLogService.LogSuccessAsync(
                AuditCategory.System,
                "CancelBatchOperation",
                operationId,
                "Cancelled batch operation",
                cancellationToken: cancellationToken);

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to cancel batch operation {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to cancel batch operation: {ex.Message}");
        }
    }

    public async Task<OperationResult> DeleteBatchOperationAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Deleting batch operation: {OperationId}", operationId);

            // Cannot delete active operations
            if (_activeOperations.ContainsKey(operationId))
            {
                return OperationResult.FailureResult("Cannot delete an active batch operation. Cancel it first.");
            }

            var filePath = GetBatchOperationFilePath(operationId);
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }

            await _auditLogService.LogSuccessAsync(
                AuditCategory.System,
                "DeleteBatchOperation",
                operationId,
                "Deleted batch operation",
                cancellationToken: cancellationToken);

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete batch operation {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to delete batch operation: {ex.Message}");
        }
    }

    public Task<OperationResult<BatchOperation>> GetBatchOperationStatusAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        return GetBatchOperationAsync(operationId, cancellationToken);
    }

    public async Task<OperationResult<BatchOperationStatistics>> GetStatisticsAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Generating batch operation statistics");

            var operations = await LoadAllBatchOperationsAsync(cancellationToken);

            // Filter by date
            if (startDate.HasValue)
                operations = operations.Where(o => o.CreatedAt >= startDate.Value).ToList();
            if (endDate.HasValue)
                operations = operations.Where(o => o.CreatedAt <= endDate.Value).ToList();

            var statistics = new BatchOperationStatistics
            {
                TotalBatchOperations = operations.Count,
                CompletedBatchOperations = operations.Count(o => o.Status == BatchOperationStatus.Completed),
                FailedBatchOperations = operations.Count(o => o.Status == BatchOperationStatus.Failed),
                RunningBatchOperations = operations.Count(o => o.Status == BatchOperationStatus.Running),
                TotalImagesProcessed = operations.Sum(o => o.Summary.SuccessfulImages + o.Summary.FailedImages)
            };

            statistics.SuccessRate = statistics.TotalBatchOperations > 0
                ? (statistics.CompletedBatchOperations / (double)statistics.TotalBatchOperations) * 100
                : 0;

            var completedOps = operations.Where(o => o.CompletedAt.HasValue).ToList();
            statistics.AverageBatchDurationMs = completedOps.Any()
                ? completedOps.Average(o => o.DurationMs)
                : 0;

            statistics.OperationsByType = operations
                .GroupBy(o => o.Type)
                .ToDictionary(g => g.Key, g => g.Count());

            statistics.OperationsByStatus = operations
                .GroupBy(o => o.Status)
                .ToDictionary(g => g.Key, g => g.Count());

            return OperationResult<BatchOperationStatistics>.SuccessResult(statistics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate statistics");
            return OperationResult<BatchOperationStatistics>.FailureResult($"Statistics generation failed: {ex.Message}");
        }
    }

    public async Task<OperationResult> RetryFailedImagesAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var opResult = await GetBatchOperationAsync(operationId, cancellationToken);
            if (!opResult.Success || opResult.Data == null)
            {
                return OperationResult.FailureResult($"Batch operation '{operationId}' not found");
            }

            var batchOperation = opResult.Data;

            // Reset failed images to pending
            foreach (var image in batchOperation.TargetImages.Where(i => i.Status == ImageOperationStatus.Failed))
            {
                image.Status = ImageOperationStatus.Pending;
                image.ErrorMessage = null;
                image.ProgressPercentage = 0;
            }

            batchOperation.Status = BatchOperationStatus.Pending;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            // Restart the operation
            return await StartBatchOperationAsync(operationId, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to retry failed images for {OperationId}", operationId);
            return OperationResult.FailureResult($"Failed to retry: {ex.Message}");
        }
    }

    public async Task<OperationResult<List<BatchOperation>>> GetActiveBatchOperationsAsync(
        CancellationToken cancellationToken = default)
    {
        try
        {
            var activeOps = _activeOperations.Values.ToList();
            return OperationResult<List<BatchOperation>>.SuccessResult(activeOps);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get active batch operations");
            return OperationResult<List<BatchOperation>>.FailureResult($"Failed to get active operations: {ex.Message}");
        }
    }

    // Private helper methods

    private async Task ExecuteBatchOperationAsync(BatchOperation batchOperation, CancellationToken cancellationToken)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            _logger.LogInformation("Executing batch operation: {Id} - {Name}", batchOperation.Id, batchOperation.Name);

            batchOperation.Status = BatchOperationStatus.Running;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            var progress = _progressService.CreateProgressReporter(batchOperation.Id);

            // Process images with parallelism
            var semaphore = new SemaphoreSlim(batchOperation.MaxParallelOperations);
            var tasks = new List<Task>();

            var pendingImages = batchOperation.TargetImages.Where(i => i.Status == ImageOperationStatus.Pending).ToList();

            foreach (var image in pendingImages)
            {
                if (cancellationToken.IsCancellationRequested)
                    break;

                await semaphore.WaitAsync(cancellationToken);

                var task = Task.Run(async () =>
                {
                    try
                    {
                        await ProcessImageAsync(batchOperation, image, progress, cancellationToken);
                    }
                    finally
                    {
                        semaphore.Release();
                    }
                }, cancellationToken);

                tasks.Add(task);
            }

            await Task.WhenAll(tasks);

            // Update final status
            batchOperation.CompletedAt = DateTime.UtcNow;
            batchOperation.DurationMs = stopwatch.ElapsedMilliseconds;

            // Calculate summary
            UpdateSummary(batchOperation);

            if (batchOperation.Summary.FailedImages > 0)
            {
                batchOperation.Status = BatchOperationStatus.CompletedWithErrors;
            }
            else
            {
                batchOperation.Status = BatchOperationStatus.Completed;
            }

            batchOperation.ProgressPercentage = 100;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            await _auditLogService.LogSuccessAsync(
                AuditCategory.System,
                "CompleteBatchOperation",
                batchOperation.Id,
                $"Batch operation completed: {batchOperation.Summary.SuccessfulImages}/{batchOperation.Summary.TotalImages} successful",
                stopwatch.ElapsedMilliseconds,
                new Dictionary<string, object>
                {
                    ["SuccessfulImages"] = batchOperation.Summary.SuccessfulImages,
                    ["FailedImages"] = batchOperation.Summary.FailedImages,
                    ["TotalImages"] = batchOperation.Summary.TotalImages
                },
                cancellationToken);

            _logger.LogInformation("Batch operation completed: {Id} - {Status}", batchOperation.Id, batchOperation.Status);
        }
        catch (OperationCanceledException)
        {
            batchOperation.Status = BatchOperationStatus.Cancelled;
            await SaveBatchOperationAsync(batchOperation, CancellationToken.None);
            _logger.LogInformation("Batch operation cancelled: {Id}", batchOperation.Id);
        }
        catch (Exception ex)
        {
            batchOperation.Status = BatchOperationStatus.Failed;
            batchOperation.ErrorMessage = ex.Message;
            await SaveBatchOperationAsync(batchOperation, CancellationToken.None);

            await _auditLogService.LogFailureAsync(
                AuditCategory.System,
                "ExecuteBatchOperation",
                batchOperation.Id,
                ex.Message,
                stopwatch.ElapsedMilliseconds,
                cancellationToken: CancellationToken.None);

            _logger.LogError(ex, "Batch operation failed: {Id}", batchOperation.Id);
        }
        finally
        {
            _activeOperations.TryRemove(batchOperation.Id, out _);
            _cancellationTokens.TryRemove(batchOperation.Id, out _);
        }
    }

    private async Task ProcessImageAsync(
        BatchOperation batchOperation,
        BatchTargetImage image,
        IProgress<ProgressReport> progress,
        CancellationToken cancellationToken)
    {
        var stopwatch = Stopwatch.StartNew();

        try
        {
            image.Status = ImageOperationStatus.Running;
            image.StartedAt = DateTime.UtcNow;
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            _logger.LogInformation("Processing image: {Path}", image.ImagePath);

            // Simulate image processing (in production, would call actual services)
            // Example: Apply template, validate, optimize, etc.
            await Task.Delay(100, cancellationToken); // Simulate work

            image.Status = ImageOperationStatus.Completed;
            image.ProgressPercentage = 100;
            image.CompletedAt = DateTime.UtcNow;
            image.DurationMs = stopwatch.ElapsedMilliseconds;

            // Update batch progress
            UpdateBatchProgress(batchOperation);
            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            _logger.LogInformation("Image processed successfully: {Path}", image.ImagePath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to process image: {Path}", image.ImagePath);

            image.Status = ImageOperationStatus.Failed;
            image.ErrorMessage = ex.Message;
            image.CompletedAt = DateTime.UtcNow;
            image.DurationMs = stopwatch.ElapsedMilliseconds;

            await SaveBatchOperationAsync(batchOperation, cancellationToken);

            if (!batchOperation.ContinueOnError)
            {
                throw;
            }
        }
    }

    private void UpdateBatchProgress(BatchOperation batchOperation)
    {
        var totalImages = batchOperation.TargetImages.Count;
        var completed = batchOperation.TargetImages.Count(i =>
            i.Status == ImageOperationStatus.Completed ||
            i.Status == ImageOperationStatus.Failed ||
            i.Status == ImageOperationStatus.Skipped);

        batchOperation.ProgressPercentage = totalImages > 0
            ? (int)((completed / (double)totalImages) * 100)
            : 0;
    }

    private void UpdateSummary(BatchOperation batchOperation)
    {
        batchOperation.Summary.TotalImages = batchOperation.TargetImages.Count;
        batchOperation.Summary.SuccessfulImages = batchOperation.TargetImages.Count(i => i.Status == ImageOperationStatus.Completed);
        batchOperation.Summary.FailedImages = batchOperation.TargetImages.Count(i => i.Status == ImageOperationStatus.Failed);
        batchOperation.Summary.SkippedImages = batchOperation.TargetImages.Count(i => i.Status == ImageOperationStatus.Skipped);
        batchOperation.Summary.CancelledImages = batchOperation.TargetImages.Count(i => i.Status == ImageOperationStatus.Cancelled);

        batchOperation.Summary.SuccessRate = batchOperation.Summary.TotalImages > 0
            ? (batchOperation.Summary.SuccessfulImages / (double)batchOperation.Summary.TotalImages) * 100
            : 0;

        var completedImages = batchOperation.TargetImages.Where(i => i.CompletedAt.HasValue).ToList();
        batchOperation.Summary.AverageDurationMs = completedImages.Any()
            ? completedImages.Average(i => i.DurationMs)
            : 0;
    }

    private string GetBatchOperationFilePath(string operationId)
    {
        return Path.Combine(_storageDirectory, $"{operationId}.json");
    }

    private async Task SaveBatchOperationAsync(BatchOperation batchOperation, CancellationToken cancellationToken)
    {
        var filePath = GetBatchOperationFilePath(batchOperation.Id);
        var json = JsonSerializer.Serialize(batchOperation, _jsonOptions);
        await File.WriteAllTextAsync(filePath, json, cancellationToken);
    }

    private async Task<BatchOperation?> LoadBatchOperationAsync(string operationId, CancellationToken cancellationToken)
    {
        var filePath = GetBatchOperationFilePath(operationId);
        if (!File.Exists(filePath))
            return null;

        var json = await File.ReadAllTextAsync(filePath, cancellationToken);
        return JsonSerializer.Deserialize<BatchOperation>(json, _jsonOptions);
    }

    private async Task<List<BatchOperation>> LoadAllBatchOperationsAsync(CancellationToken cancellationToken)
    {
        var operations = new List<BatchOperation>();
        var files = Directory.GetFiles(_storageDirectory, "*.json");

        foreach (var file in files)
        {
            try
            {
                var json = await File.ReadAllTextAsync(file, cancellationToken);
                var operation = JsonSerializer.Deserialize<BatchOperation>(json, _jsonOptions);
                if (operation != null)
                {
                    operations.Add(operation);
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to load batch operation from {File}", file);
            }
        }

        return operations;
    }

    private object GetSortValue(BatchOperation operation, string sortBy)
    {
        return sortBy.ToLowerInvariant() switch
        {
            "createdat" => operation.CreatedAt,
            "name" => operation.Name,
            "type" => operation.Type.ToString(),
            "status" => operation.Status.ToString(),
            "priority" => operation.Priority,
            _ => operation.CreatedAt
        };
    }
}
