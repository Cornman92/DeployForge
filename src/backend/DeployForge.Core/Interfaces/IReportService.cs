using DeployForge.Common.Models;
using DeployForge.Common.Models.Reports;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for generating various types of reports
/// </summary>
public interface IReportService
{
    /// <summary>
    /// Generate a report
    /// </summary>
    Task<OperationResult<Report>> GenerateReportAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generate validation report
    /// </summary>
    Task<OperationResult<Report>> GenerateValidationReportAsync(
        ValidationResult validationResult,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generate audit report
    /// </summary>
    Task<OperationResult<Report>> GenerateAuditReportAsync(
        DateTime startDate,
        DateTime endDate,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generate statistics report
    /// </summary>
    Task<OperationResult<Report>> GenerateStatisticsReportAsync(
        DateTime startDate,
        DateTime endDate,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Generate batch operation report
    /// </summary>
    Task<OperationResult<Report>> GenerateBatchOperationReportAsync(
        string batchOperationId,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get report by ID
    /// </summary>
    Task<OperationResult<Report>> GetReportAsync(
        string reportId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// List generated reports
    /// </summary>
    Task<OperationResult<List<Report>>> ListReportsAsync(
        ReportType? type = null,
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete report
    /// </summary>
    Task<OperationResult<bool>> DeleteReportAsync(
        string reportId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Export report to different format
    /// </summary>
    Task<OperationResult<Report>> ExportReportAsync(
        string reportId,
        ReportFormat targetFormat,
        string? outputPath = null,
        CancellationToken cancellationToken = default);
}
