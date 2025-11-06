using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for managing audit logs
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class AuditLogController : ControllerBase
{
    private readonly IAuditLogService _auditLogService;
    private readonly ILogger<AuditLogController> _logger;

    public AuditLogController(
        IAuditLogService auditLogService,
        ILogger<AuditLogController> logger)
    {
        _auditLogService = auditLogService;
        _logger = logger;
    }

    /// <summary>
    /// Queries audit logs with filtering and pagination
    /// </summary>
    /// <param name="query">Query parameters</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Query results</returns>
    [HttpPost("query")]
    [ProducesResponseType(typeof(AuditLogQueryResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<AuditLogQueryResult>> QueryLogs(
        [FromBody] AuditLogQuery query,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Querying audit logs");

        var result = await _auditLogService.QueryLogsAsync(query, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets a specific audit log entry
    /// </summary>
    /// <param name="entryId">Entry identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Audit log entry</returns>
    [HttpGet("{entryId}")]
    [ProducesResponseType(typeof(AuditLogEntry), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<AuditLogEntry>> GetEntry(
        string entryId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting audit entry: {EntryId}", entryId);

        var result = await _auditLogService.GetEntryAsync(entryId, cancellationToken);

        if (!result.Success)
        {
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets audit log statistics
    /// </summary>
    /// <param name="startDate">Start date filter</param>
    /// <param name="endDate">End date filter</param>
    /// <param name="category">Category filter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Audit log statistics</returns>
    [HttpGet("statistics")]
    [ProducesResponseType(typeof(AuditLogStatistics), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<AuditLogStatistics>> GetStatistics(
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null,
        [FromQuery] AuditCategory? category = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting audit log statistics");

        var result = await _auditLogService.GetStatisticsAsync(
            startDate,
            endDate,
            category,
            cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Exports audit logs to a file
    /// </summary>
    /// <param name="request">Export request</param>
    /// <param name="outputPath">Output file path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Path to exported file</returns>
    [HttpPost("export")]
    [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> ExportLogs(
        [FromBody] ExportAuditLogsRequest request,
        [FromQuery] string outputPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Exporting audit logs to {Path} in {Format} format",
            outputPath, request.Format);

        var result = await _auditLogService.ExportLogsAsync(request, outputPath, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(new { ExportPath = result.Data });
    }

    /// <summary>
    /// Deletes old audit logs
    /// </summary>
    /// <param name="olderThan">Delete logs older than this date</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Number of entries deleted</returns>
    [HttpDelete("delete-old")]
    [ProducesResponseType(typeof(int), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> DeleteOldLogs(
        [FromQuery] DateTime olderThan,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting audit logs older than {Date}", olderThan);

        var result = await _auditLogService.DeleteOldLogsAsync(olderThan, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(new { DeletedCount = result.Data });
    }

    /// <summary>
    /// Archives old audit logs
    /// </summary>
    /// <param name="olderThan">Archive logs older than this date</param>
    /// <param name="archivePath">Archive destination path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Number of entries archived</returns>
    [HttpPost("archive")]
    [ProducesResponseType(typeof(int), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> ArchiveOldLogs(
        [FromQuery] DateTime olderThan,
        [FromQuery] string archivePath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Archiving audit logs older than {Date} to {Path}",
            olderThan, archivePath);

        var result = await _auditLogService.ArchiveOldLogsAsync(
            olderThan,
            archivePath,
            cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(new { ArchivedCount = result.Data });
    }

    /// <summary>
    /// Applies retention policy to audit logs
    /// </summary>
    /// <param name="policy">Retention policy</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    [HttpPost("apply-retention")]
    [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> ApplyRetentionPolicy(
        [FromBody] AuditRetentionPolicy policy,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Applying retention policy: {Days} days", policy.RetentionDays);

        var result = await _auditLogService.ApplyRetentionPolicyAsync(policy, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return Ok(new { Message = result.Data });
    }

    /// <summary>
    /// Gets logs for a specific operation
    /// </summary>
    /// <param name="operationId">Operation identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of audit log entries</returns>
    [HttpGet("operation/{operationId}")]
    [ProducesResponseType(typeof(List<AuditLogEntry>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<AuditLogEntry>>> GetLogsByOperation(
        string operationId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting logs for operation: {OperationId}", operationId);

        var result = await _auditLogService.GetLogsByOperationIdAsync(operationId, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Gets recent audit logs
    /// </summary>
    /// <param name="count">Number of recent logs to retrieve</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Recent audit log entries</returns>
    [HttpGet("recent")]
    [ProducesResponseType(typeof(List<AuditLogEntry>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<List<AuditLogEntry>>> GetRecentLogs(
        [FromQuery] int count = 100,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting {Count} recent audit logs", count);

        var result = await _auditLogService.GetRecentLogsAsync(count, cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Searches audit logs by text
    /// </summary>
    /// <param name="searchText">Text to search for</param>
    /// <param name="pageNumber">Page number</param>
    /// <param name="pageSize">Page size</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Search results</returns>
    [HttpGet("search")]
    [ProducesResponseType(typeof(AuditLogQueryResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<AuditLogQueryResult>> SearchLogs(
        [FromQuery] string searchText,
        [FromQuery] int pageNumber = 1,
        [FromQuery] int pageSize = 50,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Searching audit logs for: {SearchText}", searchText);

        if (string.IsNullOrWhiteSpace(searchText))
        {
            return BadRequest("Search text is required");
        }

        var result = await _auditLogService.SearchLogsAsync(
            searchText,
            pageNumber,
            pageSize,
            cancellationToken);

        if (!result.Success)
        {
            return StatusCode(StatusCodes.Status500InternalServerError, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Manually logs an audit entry (for testing or manual operations)
    /// </summary>
    /// <param name="entry">Audit log entry</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Entry ID</returns>
    [HttpPost("log")]
    [ProducesResponseType(typeof(string), StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult> LogEntry(
        [FromBody] AuditLogEntry entry,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Manually logging audit entry: {Category}.{Action}",
            entry.Category, entry.Action);

        // Capture HTTP context information
        entry.IpAddress = HttpContext.Connection.RemoteIpAddress?.ToString();
        entry.UserAgent = HttpContext.Request.Headers.UserAgent.ToString();

        var result = await _auditLogService.LogAsync(entry, cancellationToken);

        if (!result.Success)
        {
            return BadRequest(result.ErrorMessage);
        }

        return CreatedAtAction(
            nameof(GetEntry),
            new { entryId = result.Data },
            new { EntryId = result.Data });
    }
}
