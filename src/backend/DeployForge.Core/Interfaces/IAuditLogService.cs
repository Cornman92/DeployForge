using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing audit logs
/// </summary>
public interface IAuditLogService
{
    /// <summary>
    /// Logs an operation
    /// </summary>
    /// <param name="entry">Audit log entry</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The logged entry ID</returns>
    Task<OperationResult<string>> LogAsync(
        AuditLogEntry entry,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Logs a successful operation
    /// </summary>
    /// <param name="category">Operation category</param>
    /// <param name="action">Action performed</param>
    /// <param name="resource">Resource affected</param>
    /// <param name="description">Description</param>
    /// <param name="durationMs">Operation duration</param>
    /// <param name="metadata">Additional metadata</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The logged entry ID</returns>
    Task<OperationResult<string>> LogSuccessAsync(
        AuditCategory category,
        string action,
        string resource,
        string description,
        long durationMs = 0,
        Dictionary<string, object>? metadata = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Logs a failed operation
    /// </summary>
    /// <param name="category">Operation category</param>
    /// <param name="action">Action attempted</param>
    /// <param name="resource">Resource affected</param>
    /// <param name="errorMessage">Error message</param>
    /// <param name="durationMs">Operation duration</param>
    /// <param name="metadata">Additional metadata</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The logged entry ID</returns>
    Task<OperationResult<string>> LogFailureAsync(
        AuditCategory category,
        string action,
        string resource,
        string errorMessage,
        long durationMs = 0,
        Dictionary<string, object>? metadata = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Queries audit logs with filtering and pagination
    /// </summary>
    /// <param name="query">Query parameters</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Query results</returns>
    Task<OperationResult<AuditLogQueryResult>> QueryLogsAsync(
        AuditLogQuery query,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a specific audit log entry by ID
    /// </summary>
    /// <param name="entryId">Entry identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Audit log entry</returns>
    Task<OperationResult<AuditLogEntry>> GetEntryAsync(
        string entryId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets audit log statistics
    /// </summary>
    /// <param name="startDate">Start date filter</param>
    /// <param name="endDate">End date filter</param>
    /// <param name="category">Optional category filter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Audit log statistics</returns>
    Task<OperationResult<AuditLogStatistics>> GetStatisticsAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        AuditCategory? category = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Exports audit logs to a file
    /// </summary>
    /// <param name="request">Export request</param>
    /// <param name="outputPath">Output file path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Path to the exported file</returns>
    Task<OperationResult<string>> ExportLogsAsync(
        ExportAuditLogsRequest request,
        string outputPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes audit logs older than the specified date
    /// </summary>
    /// <param name="olderThan">Delete logs older than this date</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Number of entries deleted</returns>
    Task<OperationResult<int>> DeleteOldLogsAsync(
        DateTime olderThan,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Archives old audit logs
    /// </summary>
    /// <param name="olderThan">Archive logs older than this date</param>
    /// <param name="archivePath">Archive destination path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Number of entries archived</returns>
    Task<OperationResult<int>> ArchiveOldLogsAsync(
        DateTime olderThan,
        string archivePath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Applies retention policy to audit logs
    /// </summary>
    /// <param name="policy">Retention policy</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result with details</returns>
    Task<OperationResult<string>> ApplyRetentionPolicyAsync(
        AuditRetentionPolicy policy,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets logs for a specific operation ID
    /// </summary>
    /// <param name="operationId">Operation identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of audit log entries</returns>
    Task<OperationResult<List<AuditLogEntry>>> GetLogsByOperationIdAsync(
        string operationId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets recent logs
    /// </summary>
    /// <param name="count">Number of recent logs to retrieve</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Recent audit log entries</returns>
    Task<OperationResult<List<AuditLogEntry>>> GetRecentLogsAsync(
        int count = 100,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Searches audit logs by text
    /// </summary>
    /// <param name="searchText">Text to search for</param>
    /// <param name="pageNumber">Page number</param>
    /// <param name="pageSize">Page size</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Search results</returns>
    Task<OperationResult<AuditLogQueryResult>> SearchLogsAsync(
        string searchText,
        int pageNumber = 1,
        int pageSize = 50,
        CancellationToken cancellationToken = default);
}
