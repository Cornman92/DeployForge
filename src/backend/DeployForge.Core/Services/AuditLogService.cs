using System.Text;
using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing audit logs with file-based storage
/// </summary>
public class AuditLogService : IAuditLogService
{
    private readonly ILogger<AuditLogService> _logger;
    private readonly string _logsDirectory;
    private readonly JsonSerializerOptions _jsonOptions;
    private readonly object _lockObject = new();

    public AuditLogService(ILogger<AuditLogService> logger)
    {
        _logger = logger;

        // Store logs in AppData\DeployForge\AuditLogs
        var appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        _logsDirectory = Path.Combine(appDataPath, "DeployForge", "AuditLogs");

        // Ensure directory exists
        Directory.CreateDirectory(_logsDirectory);

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            PropertyNameCaseInsensitive = true
        };

        _logger.LogInformation("Audit log service initialized with storage at: {Path}", _logsDirectory);
    }

    public async Task<OperationResult<string>> LogAsync(
        AuditLogEntry entry,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Ensure ID is set
            if (string.IsNullOrEmpty(entry.Id))
                entry.Id = Guid.NewGuid().ToString();

            // Ensure timestamp is set
            if (entry.Timestamp == default)
                entry.Timestamp = DateTime.UtcNow;

            // Get the log file path for today
            var logFilePath = GetLogFilePath(entry.Timestamp);

            // Write log entry
            lock (_lockObject)
            {
                var json = JsonSerializer.Serialize(entry, _jsonOptions);
                File.AppendAllText(logFilePath, json + Environment.NewLine);
            }

            _logger.LogDebug("Logged audit entry {EntryId}: {Category}.{Action} - {Result}",
                entry.Id, entry.Category, entry.Action, entry.Result);

            return OperationResult<string>.SuccessResult(entry.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to log audit entry");
            return OperationResult<string>.FailureResult($"Failed to log entry: {ex.Message}");
        }
    }

    public async Task<OperationResult<string>> LogSuccessAsync(
        AuditCategory category,
        string action,
        string resource,
        string description,
        long durationMs = 0,
        Dictionary<string, object>? metadata = null,
        CancellationToken cancellationToken = default)
    {
        var entry = new AuditLogEntry
        {
            Category = category,
            Action = action,
            Resource = resource,
            Description = description,
            Result = AuditResult.Success,
            DurationMs = durationMs,
            Metadata = metadata ?? new Dictionary<string, object>(),
            Severity = AuditSeverity.Information
        };

        return await LogAsync(entry, cancellationToken);
    }

    public async Task<OperationResult<string>> LogFailureAsync(
        AuditCategory category,
        string action,
        string resource,
        string errorMessage,
        long durationMs = 0,
        Dictionary<string, object>? metadata = null,
        CancellationToken cancellationToken = default)
    {
        var entry = new AuditLogEntry
        {
            Category = category,
            Action = action,
            Resource = resource,
            Description = $"Operation failed: {action}",
            Result = AuditResult.Failure,
            ErrorMessage = errorMessage,
            DurationMs = durationMs,
            Metadata = metadata ?? new Dictionary<string, object>(),
            Severity = AuditSeverity.Error
        };

        return await LogAsync(entry, cancellationToken);
    }

    public async Task<OperationResult<AuditLogQueryResult>> QueryLogsAsync(
        AuditLogQuery query,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Querying audit logs with filters");

            var allEntries = await LoadEntriesAsync(query.StartDate, query.EndDate, cancellationToken);

            // Apply filters
            var filteredEntries = allEntries.AsEnumerable();

            if (!string.IsNullOrEmpty(query.User))
                filteredEntries = filteredEntries.Where(e => e.User.Equals(query.User, StringComparison.OrdinalIgnoreCase));

            if (query.Category.HasValue)
                filteredEntries = filteredEntries.Where(e => e.Category == query.Category.Value);

            if (!string.IsNullOrEmpty(query.Action))
                filteredEntries = filteredEntries.Where(e => e.Action.Contains(query.Action, StringComparison.OrdinalIgnoreCase));

            if (!string.IsNullOrEmpty(query.Resource))
                filteredEntries = filteredEntries.Where(e => e.Resource.Contains(query.Resource, StringComparison.OrdinalIgnoreCase));

            if (query.Result.HasValue)
                filteredEntries = filteredEntries.Where(e => e.Result == query.Result.Value);

            if (!string.IsNullOrEmpty(query.OperationId))
                filteredEntries = filteredEntries.Where(e => e.OperationId == query.OperationId);

            if (query.MinSeverity.HasValue)
                filteredEntries = filteredEntries.Where(e => e.Severity >= query.MinSeverity.Value);

            // Sort
            filteredEntries = query.SortDirection.ToLowerInvariant() == "asc"
                ? filteredEntries.OrderBy(e => GetSortValue(e, query.SortBy))
                : filteredEntries.OrderByDescending(e => GetSortValue(e, query.SortBy));

            var filteredList = filteredEntries.ToList();
            var totalCount = filteredList.Count;

            // Paginate
            var pagedEntries = filteredList
                .Skip((query.PageNumber - 1) * query.PageSize)
                .Take(query.PageSize)
                .ToList();

            var totalPages = (int)Math.Ceiling(totalCount / (double)query.PageSize);

            var result = new AuditLogQueryResult
            {
                Entries = pagedEntries,
                TotalCount = totalCount,
                PageNumber = query.PageNumber,
                PageSize = query.PageSize,
                TotalPages = totalPages,
                HasNextPage = query.PageNumber < totalPages,
                HasPreviousPage = query.PageNumber > 1
            };

            _logger.LogInformation("Query returned {Count} entries (page {Page} of {TotalPages})",
                pagedEntries.Count, query.PageNumber, totalPages);

            return OperationResult<AuditLogQueryResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to query audit logs");
            return OperationResult<AuditLogQueryResult>.FailureResult($"Query failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<AuditLogEntry>> GetEntryAsync(
        string entryId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var allEntries = await LoadEntriesAsync(null, null, cancellationToken);
            var entry = allEntries.FirstOrDefault(e => e.Id == entryId);

            if (entry == null)
            {
                return OperationResult<AuditLogEntry>.FailureResult($"Entry '{entryId}' not found");
            }

            return OperationResult<AuditLogEntry>.SuccessResult(entry);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get audit entry {EntryId}", entryId);
            return OperationResult<AuditLogEntry>.FailureResult($"Failed to get entry: {ex.Message}");
        }
    }

    public async Task<OperationResult<AuditLogStatistics>> GetStatisticsAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        AuditCategory? category = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Generating audit log statistics");

            var entries = await LoadEntriesAsync(startDate, endDate, cancellationToken);

            if (category.HasValue)
                entries = entries.Where(e => e.Category == category.Value).ToList();

            var statistics = new AuditLogStatistics
            {
                TotalOperations = entries.Count,
                SuccessfulOperations = entries.Count(e => e.Result == AuditResult.Success),
                FailedOperations = entries.Count(e => e.Result == AuditResult.Failure),
                StartDate = startDate,
                EndDate = endDate
            };

            statistics.SuccessRate = statistics.TotalOperations > 0
                ? (statistics.SuccessfulOperations / (double)statistics.TotalOperations) * 100
                : 0;

            statistics.AverageDurationMs = entries.Any()
                ? entries.Average(e => e.DurationMs)
                : 0;

            // Operations by category
            statistics.OperationsByCategory = entries
                .GroupBy(e => e.Category)
                .ToDictionary(g => g.Key, g => g.Count());

            // Operations by user
            statistics.OperationsByUser = entries
                .GroupBy(e => e.User)
                .ToDictionary(g => g.Key, g => g.Count());

            // Operations by result
            statistics.OperationsByResult = entries
                .GroupBy(e => e.Result)
                .ToDictionary(g => g.Key, g => g.Count());

            // Most active users
            statistics.MostActiveUsers = entries
                .GroupBy(e => e.User)
                .Select(g => new UserActivity
                {
                    User = g.Key,
                    OperationCount = g.Count(),
                    SuccessRate = (g.Count(e => e.Result == AuditResult.Success) / (double)g.Count()) * 100
                })
                .OrderByDescending(u => u.OperationCount)
                .Take(10)
                .ToList();

            // Most common actions
            statistics.MostCommonActions = entries
                .GroupBy(e => new { e.Action, e.Category })
                .Select(g => new ActionFrequency
                {
                    Action = g.Key.Action,
                    Category = g.Key.Category,
                    Count = g.Count()
                })
                .OrderByDescending(a => a.Count)
                .Take(10)
                .ToList();

            _logger.LogInformation("Statistics generated for {Count} operations", statistics.TotalOperations);

            return OperationResult<AuditLogStatistics>.SuccessResult(statistics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate audit log statistics");
            return OperationResult<AuditLogStatistics>.FailureResult($"Statistics generation failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<string>> ExportLogsAsync(
        ExportAuditLogsRequest request,
        string outputPath,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Exporting audit logs to {Path} in {Format} format",
                outputPath, request.Format);

            var queryResult = await QueryLogsAsync(request.Query, cancellationToken);
            if (!queryResult.Success || queryResult.Data == null)
            {
                return OperationResult<string>.FailureResult("Failed to query logs for export");
            }

            // Ensure output directory exists
            var directory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            switch (request.Format.ToUpperInvariant())
            {
                case "JSON":
                    var json = JsonSerializer.Serialize(queryResult.Data.Entries, _jsonOptions);
                    await File.WriteAllTextAsync(outputPath, json, cancellationToken);
                    break;

                case "CSV":
                    var csv = GenerateCsv(queryResult.Data.Entries, request.IncludeMetadata);
                    await File.WriteAllTextAsync(outputPath, csv, cancellationToken);
                    break;

                case "TXT":
                    var text = GenerateTextReport(queryResult.Data.Entries);
                    await File.WriteAllTextAsync(outputPath, text, cancellationToken);
                    break;

                default:
                    return OperationResult<string>.FailureResult($"Unsupported export format: {request.Format}");
            }

            _logger.LogInformation("Exported {Count} entries to {Path}", queryResult.Data.Entries.Count, outputPath);
            return OperationResult<string>.SuccessResult(outputPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to export audit logs");
            return OperationResult<string>.FailureResult($"Export failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<int>> DeleteOldLogsAsync(
        DateTime olderThan,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Deleting audit logs older than {Date}", olderThan);

            var deletedCount = 0;
            var logFiles = Directory.GetFiles(_logsDirectory, "audit-*.log");

            foreach (var logFile in logFiles)
            {
                var fileDate = GetDateFromLogFileName(logFile);
                if (fileDate.HasValue && fileDate.Value < olderThan.Date)
                {
                    File.Delete(logFile);
                    deletedCount++;
                    _logger.LogInformation("Deleted old log file: {File}", Path.GetFileName(logFile));
                }
            }

            _logger.LogInformation("Deleted {Count} old log files", deletedCount);
            return OperationResult<int>.SuccessResult(deletedCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete old logs");
            return OperationResult<int>.FailureResult($"Deletion failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<int>> ArchiveOldLogsAsync(
        DateTime olderThan,
        string archivePath,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Archiving audit logs older than {Date} to {Path}",
                olderThan, archivePath);

            Directory.CreateDirectory(archivePath);

            var archivedCount = 0;
            var logFiles = Directory.GetFiles(_logsDirectory, "audit-*.log");

            foreach (var logFile in logFiles)
            {
                var fileDate = GetDateFromLogFileName(logFile);
                if (fileDate.HasValue && fileDate.Value < olderThan.Date)
                {
                    var fileName = Path.GetFileName(logFile);
                    var archiveFile = Path.Combine(archivePath, fileName);
                    File.Move(logFile, archiveFile, overwrite: true);
                    archivedCount++;
                    _logger.LogInformation("Archived log file: {File}", fileName);
                }
            }

            _logger.LogInformation("Archived {Count} log files", archivedCount);
            return OperationResult<int>.SuccessResult(archivedCount);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to archive old logs");
            return OperationResult<int>.FailureResult($"Archive failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<string>> ApplyRetentionPolicyAsync(
        AuditRetentionPolicy policy,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Applying audit log retention policy: {Days} days retention",
                policy.RetentionDays);

            var results = new StringBuilder();
            var now = DateTime.UtcNow;

            // Archive old logs if configured
            if (!string.IsNullOrEmpty(policy.ArchivePath) && policy.AutoArchiveAfterDays > 0)
            {
                var archiveDate = now.AddDays(-policy.AutoArchiveAfterDays);
                var archiveResult = await ArchiveOldLogsAsync(archiveDate, policy.ArchivePath, cancellationToken);
                if (archiveResult.Success)
                {
                    results.AppendLine($"Archived {archiveResult.Data} log files");
                }
            }

            // Delete old logs if retention period is set
            if (policy.RetentionDays > 0)
            {
                var deleteDate = now.AddDays(-policy.RetentionDays);
                var deleteResult = await DeleteOldLogsAsync(deleteDate, cancellationToken);
                if (deleteResult.Success)
                {
                    results.AppendLine($"Deleted {deleteResult.Data} old log files");
                }
            }

            var message = results.Length > 0 ? results.ToString() : "No logs required retention action";
            _logger.LogInformation("Retention policy applied: {Message}", message);

            return OperationResult<string>.SuccessResult(message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply retention policy");
            return OperationResult<string>.FailureResult($"Retention policy failed: {ex.Message}");
        }
    }

    public async Task<OperationResult<List<AuditLogEntry>>> GetLogsByOperationIdAsync(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var allEntries = await LoadEntriesAsync(null, null, cancellationToken);
            var entries = allEntries
                .Where(e => e.OperationId == operationId)
                .OrderBy(e => e.Timestamp)
                .ToList();

            return OperationResult<List<AuditLogEntry>>.SuccessResult(entries);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get logs for operation {OperationId}", operationId);
            return OperationResult<List<AuditLogEntry>>.FailureResult($"Failed to get logs: {ex.Message}");
        }
    }

    public async Task<OperationResult<List<AuditLogEntry>>> GetRecentLogsAsync(
        int count = 100,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var allEntries = await LoadEntriesAsync(null, null, cancellationToken);
            var recentEntries = allEntries
                .OrderByDescending(e => e.Timestamp)
                .Take(count)
                .ToList();

            return OperationResult<List<AuditLogEntry>>.SuccessResult(recentEntries);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get recent logs");
            return OperationResult<List<AuditLogEntry>>.FailureResult($"Failed to get recent logs: {ex.Message}");
        }
    }

    public async Task<OperationResult<AuditLogQueryResult>> SearchLogsAsync(
        string searchText,
        int pageNumber = 1,
        int pageSize = 50,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var allEntries = await LoadEntriesAsync(null, null, cancellationToken);

            var searchResults = allEntries
                .Where(e =>
                    e.Action.Contains(searchText, StringComparison.OrdinalIgnoreCase) ||
                    e.Description.Contains(searchText, StringComparison.OrdinalIgnoreCase) ||
                    e.Resource.Contains(searchText, StringComparison.OrdinalIgnoreCase) ||
                    (e.ErrorMessage != null && e.ErrorMessage.Contains(searchText, StringComparison.OrdinalIgnoreCase)))
                .OrderByDescending(e => e.Timestamp)
                .ToList();

            var totalCount = searchResults.Count;
            var pagedResults = searchResults
                .Skip((pageNumber - 1) * pageSize)
                .Take(pageSize)
                .ToList();

            var totalPages = (int)Math.Ceiling(totalCount / (double)pageSize);

            var result = new AuditLogQueryResult
            {
                Entries = pagedResults,
                TotalCount = totalCount,
                PageNumber = pageNumber,
                PageSize = pageSize,
                TotalPages = totalPages,
                HasNextPage = pageNumber < totalPages,
                HasPreviousPage = pageNumber > 1
            };

            return OperationResult<AuditLogQueryResult>.SuccessResult(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to search audit logs");
            return OperationResult<AuditLogQueryResult>.FailureResult($"Search failed: {ex.Message}");
        }
    }

    // Private helper methods

    private string GetLogFilePath(DateTime date)
    {
        var fileName = $"audit-{date:yyyy-MM-dd}.log";
        return Path.Combine(_logsDirectory, fileName);
    }

    private DateTime? GetDateFromLogFileName(string filePath)
    {
        try
        {
            var fileName = Path.GetFileNameWithoutExtension(filePath);
            var datePart = fileName.Replace("audit-", "");
            return DateTime.ParseExact(datePart, "yyyy-MM-dd", null);
        }
        catch
        {
            return null;
        }
    }

    private async Task<List<AuditLogEntry>> LoadEntriesAsync(
        DateTime? startDate,
        DateTime? endDate,
        CancellationToken cancellationToken)
    {
        var entries = new List<AuditLogEntry>();
        var logFiles = Directory.GetFiles(_logsDirectory, "audit-*.log");

        foreach (var logFile in logFiles)
        {
            var fileDate = GetDateFromLogFileName(logFile);
            if (fileDate.HasValue)
            {
                // Skip files outside the date range
                if (startDate.HasValue && fileDate.Value < startDate.Value.Date)
                    continue;
                if (endDate.HasValue && fileDate.Value > endDate.Value.Date)
                    continue;
            }

            var lines = await File.ReadAllLinesAsync(logFile, cancellationToken);
            foreach (var line in lines)
            {
                if (string.IsNullOrWhiteSpace(line))
                    continue;

                try
                {
                    var entry = JsonSerializer.Deserialize<AuditLogEntry>(line, _jsonOptions);
                    if (entry != null)
                    {
                        // Additional date filtering for precise time ranges
                        if (startDate.HasValue && entry.Timestamp < startDate.Value)
                            continue;
                        if (endDate.HasValue && entry.Timestamp > endDate.Value)
                            continue;

                        entries.Add(entry);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to parse audit log line in {File}", logFile);
                }
            }
        }

        return entries;
    }

    private object GetSortValue(AuditLogEntry entry, string sortBy)
    {
        return sortBy.ToLowerInvariant() switch
        {
            "timestamp" => entry.Timestamp,
            "user" => entry.User,
            "category" => entry.Category.ToString(),
            "action" => entry.Action,
            "result" => entry.Result.ToString(),
            "duration" => entry.DurationMs,
            _ => entry.Timestamp
        };
    }

    private string GenerateCsv(List<AuditLogEntry> entries, bool includeMetadata)
    {
        var sb = new StringBuilder();

        // Header
        sb.AppendLine("Timestamp,User,Machine,Category,Action,Resource,Result,Duration (ms),Description,Error");

        // Rows
        foreach (var entry in entries)
        {
            sb.AppendLine($"\"{entry.Timestamp:O}\",\"{entry.User}\",\"{entry.MachineName}\"," +
                         $"\"{entry.Category}\",\"{entry.Action}\",\"{entry.Resource}\"," +
                         $"\"{entry.Result}\",{entry.DurationMs}," +
                         $"\"{EscapeCsv(entry.Description)}\",\"{EscapeCsv(entry.ErrorMessage ?? "")}\"");
        }

        return sb.ToString();
    }

    private string EscapeCsv(string value)
    {
        return value.Replace("\"", "\"\"");
    }

    private string GenerateTextReport(List<AuditLogEntry> entries)
    {
        var sb = new StringBuilder();
        sb.AppendLine("=== DEPLOYFORGE AUDIT LOG REPORT ===");
        sb.AppendLine($"Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC");
        sb.AppendLine($"Total Entries: {entries.Count}");
        sb.AppendLine();

        foreach (var entry in entries)
        {
            sb.AppendLine($"[{entry.Timestamp:yyyy-MM-dd HH:mm:ss}] {entry.Category}.{entry.Action}");
            sb.AppendLine($"  User: {entry.User}@{entry.MachineName}");
            sb.AppendLine($"  Resource: {entry.Resource}");
            sb.AppendLine($"  Result: {entry.Result}");
            sb.AppendLine($"  Duration: {entry.DurationMs}ms");
            sb.AppendLine($"  Description: {entry.Description}");
            if (!string.IsNullOrEmpty(entry.ErrorMessage))
                sb.AppendLine($"  Error: {entry.ErrorMessage}");
            sb.AppendLine();
        }

        return sb.ToString();
    }
}
