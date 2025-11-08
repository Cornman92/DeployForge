using DeployForge.Common.Models;
using DeployForge.Common.Models.Reports;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for report generation and management
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class ReportsController : ControllerBase
{
    private readonly IReportService _reportService;
    private readonly ILogger<ReportsController> _logger;

    public ReportsController(
        IReportService reportService,
        ILogger<ReportsController> logger)
    {
        _reportService = reportService;
        _logger = logger;
    }

    /// <summary>
    /// Generate a report
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<Report>> GenerateReport(
        [FromBody] ReportGenerationRequest request,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GenerateReportAsync(request, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Generate validation report
    /// </summary>
    [HttpPost("validation")]
    public async Task<ActionResult<Report>> GenerateValidationReport(
        [FromBody] ValidationResult validationResult,
        [FromQuery] ReportFormat format = ReportFormat.Html,
        [FromQuery] string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GenerateValidationReportAsync(
            validationResult,
            format,
            outputPath,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Generate audit report
    /// </summary>
    [HttpPost("audit")]
    public async Task<ActionResult<Report>> GenerateAuditReport(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate,
        [FromQuery] ReportFormat format = ReportFormat.Html,
        [FromQuery] string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GenerateAuditReportAsync(
            startDate,
            endDate,
            format,
            outputPath,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Generate statistics report
    /// </summary>
    [HttpPost("statistics")]
    public async Task<ActionResult<Report>> GenerateStatisticsReport(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate,
        [FromQuery] ReportFormat format = ReportFormat.Html,
        [FromQuery] string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GenerateStatisticsReportAsync(
            startDate,
            endDate,
            format,
            outputPath,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Generate batch operation report
    /// </summary>
    [HttpPost("batchoperation")]
    public async Task<ActionResult<Report>> GenerateBatchOperationReport(
        [FromQuery] string batchOperationId,
        [FromQuery] ReportFormat format = ReportFormat.Html,
        [FromQuery] string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GenerateBatchOperationReportAsync(
            batchOperationId,
            format,
            outputPath,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Get report by ID
    /// </summary>
    [HttpGet("{reportId}")]
    public async Task<ActionResult<Report>> GetReport(
        string reportId,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.GetReportAsync(reportId, cancellationToken);

        if (!result.Success || result.Data == null)
            return NotFound(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// List reports
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<Report>>> ListReports(
        [FromQuery] ReportType? type = null,
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.ListReportsAsync(type, startDate, endDate, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Delete report
    /// </summary>
    [HttpDelete("{reportId}")]
    public async Task<IActionResult> DeleteReport(
        string reportId,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.DeleteReportAsync(reportId, cancellationToken);

        if (!result.Success)
            return NotFound(result.ErrorMessage);

        return Ok(new { Message = "Report deleted successfully" });
    }

    /// <summary>
    /// Export report to different format
    /// </summary>
    [HttpPost("{reportId}/export")]
    public async Task<ActionResult<Report>> ExportReport(
        string reportId,
        [FromQuery] ReportFormat targetFormat,
        [FromQuery] string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _reportService.ExportReportAsync(
            reportId,
            targetFormat,
            outputPath,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }
}
