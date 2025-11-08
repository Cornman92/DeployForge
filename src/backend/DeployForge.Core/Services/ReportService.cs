using System.Text;
using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Common.Models.Reports;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for generating various types of reports
/// </summary>
public class ReportService : IReportService
{
    private readonly ILogger<ReportService> _logger;
    private readonly IAuditLogService _auditLogService;
    private readonly IMonitoringService _monitoringService;
    private readonly IBatchOperationService _batchOperationService;
    private readonly Dictionary<string, Report> _reportCache = new();
    private readonly string _reportsDirectory;

    public ReportService(
        ILogger<ReportService> logger,
        IAuditLogService auditLogService,
        IMonitoringService monitoringService,
        IBatchOperationService batchOperationService)
    {
        _logger = logger;
        _auditLogService = auditLogService;
        _monitoringService = monitoringService;
        _batchOperationService = batchOperationService;

        // Set reports directory
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        _reportsDirectory = Path.Combine(appData, "DeployForge", "Reports");
        Directory.CreateDirectory(_reportsDirectory);

        // Configure QuestPDF license (community license for open source)
        QuestPDF.Settings.License = LicenseType.Community;
    }

    public async Task<OperationResult<Report>> GenerateReportAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Generating {Type} report in {Format} format", request.Type, request.Format);

            Report report = request.Type switch
            {
                ReportType.Validation => throw new NotImplementedException("Use GenerateValidationReportAsync"),
                ReportType.Audit => await GenerateAuditReportInternalAsync(request, cancellationToken),
                ReportType.Statistics => await GenerateStatisticsReportInternalAsync(request, cancellationToken),
                ReportType.BatchOperation => await GenerateBatchOperationReportInternalAsync(request, cancellationToken),
                ReportType.SystemHealth => await GenerateSystemHealthReportInternalAsync(request, cancellationToken),
                _ => throw new NotSupportedException($"Report type {request.Type} is not supported")
            };

            // Cache report
            _reportCache[report.Id] = report;

            // Save to file if requested
            if (!string.IsNullOrEmpty(request.OutputPath))
            {
                await SaveReportToFileAsync(report, request.OutputPath, cancellationToken);
                report.FilePath = request.OutputPath;
            }

            return OperationResult<Report>.SuccessResult(report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate report");
            return OperationResult<Report>.FailureResult($"Failed to generate report: {ex.Message}");
        }
    }

    public async Task<OperationResult<Report>> GenerateValidationReportAsync(
        ValidationResult validationResult,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var report = new Report
            {
                Type = ReportType.Validation,
                Format = format,
                Title = $"Validation Report - {Path.GetFileName(validationResult.ImagePath)}",
                Description = $"Comprehensive validation report for Windows image"
            };

            // Build sections
            report.Sections.Add(new ReportSection
            {
                Title = "Summary",
                Order = 1,
                Type = SectionType.Table,
                Data = new
                {
                    ImagePath = validationResult.ImagePath,
                    Status = validationResult.Status.ToString(),
                    Duration = $"{validationResult.DurationMs}ms",
                    TotalChecks = validationResult.TotalChecks,
                    PassedChecks = validationResult.PassedChecks,
                    FailedChecks = validationResult.FailedChecks,
                    WarningChecks = validationResult.WarningChecks
                }
            });

            // Add checks details
            if (validationResult.Checks.Any())
            {
                var checksContent = new StringBuilder();
                foreach (var check in validationResult.Checks.OrderBy(c => c.Category))
                {
                    checksContent.AppendLine($"- [{check.Status}] {check.Name}: {check.Message}");
                }

                report.Sections.Add(new ReportSection
                {
                    Title = "Validation Checks",
                    Order = 2,
                    Type = SectionType.List,
                    Content = checksContent.ToString(),
                    Data = validationResult.Checks
                });
            }

            // Generate content based on format
            if (format == ReportFormat.Pdf)
            {
                // For PDF, we generate the file directly and set the path
                var pdfPath = outputPath ?? Path.Combine(_reportsDirectory, $"report_{report.Id}.pdf");
                GeneratePdfReport(report, pdfPath);
                report.FilePath = pdfPath;
                report.Content = $"PDF report generated at: {pdfPath}";
            }
            else
            {
                report.Content = format switch
                {
                    ReportFormat.Html => GenerateHtmlReport(report),
                    ReportFormat.Json => GenerateJsonReport(report),
                    ReportFormat.Markdown => GenerateMarkdownReport(report),
                    _ => throw new NotSupportedException($"Format {format} is not supported")
                };
            }

            // Save to file if requested
            if (!string.IsNullOrEmpty(outputPath))
            {
                await SaveReportToFileAsync(report, outputPath, cancellationToken);
                report.FilePath = outputPath;
            }

            _reportCache[report.Id] = report;

            return OperationResult<Report>.SuccessResult(report);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate validation report");
            return OperationResult<Report>.FailureResult($"Failed to generate validation report: {ex.Message}");
        }
    }

    public Task<OperationResult<Report>> GenerateAuditReportAsync(
        DateTime startDate,
        DateTime endDate,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var request = new ReportGenerationRequest
        {
            Type = ReportType.Audit,
            Format = format,
            StartDate = startDate,
            EndDate = endDate,
            OutputPath = outputPath
        };

        return GenerateReportAsync(request, cancellationToken);
    }

    public Task<OperationResult<Report>> GenerateStatisticsReportAsync(
        DateTime startDate,
        DateTime endDate,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var request = new ReportGenerationRequest
        {
            Type = ReportType.Statistics,
            Format = format,
            StartDate = startDate,
            EndDate = endDate,
            OutputPath = outputPath
        };

        return GenerateReportAsync(request, cancellationToken);
    }

    public Task<OperationResult<Report>> GenerateBatchOperationReportAsync(
        string batchOperationId,
        ReportFormat format = ReportFormat.Html,
        string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var request = new ReportGenerationRequest
        {
            Type = ReportType.BatchOperation,
            Format = format,
            ResourceId = batchOperationId,
            OutputPath = outputPath
        };

        return GenerateReportAsync(request, cancellationToken);
    }

    public Task<OperationResult<Report>> GetReportAsync(
        string reportId,
        CancellationToken cancellationToken = default)
    {
        if (_reportCache.TryGetValue(reportId, out var report))
        {
            return Task.FromResult(OperationResult<Report>.SuccessResult(report));
        }

        return Task.FromResult(OperationResult<Report>.FailureResult("Report not found"));
    }

    public Task<OperationResult<List<Report>>> ListReportsAsync(
        ReportType? type = null,
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        var reports = _reportCache.Values.AsEnumerable();

        if (type.HasValue)
            reports = reports.Where(r => r.Type == type.Value);

        if (startDate.HasValue)
            reports = reports.Where(r => r.GeneratedAt >= startDate.Value);

        if (endDate.HasValue)
            reports = reports.Where(r => r.GeneratedAt <= endDate.Value);

        return Task.FromResult(OperationResult<List<Report>>.SuccessResult(reports.ToList()));
    }

    public async Task<OperationResult<bool>> DeleteReportAsync(
        string reportId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (_reportCache.TryGetValue(reportId, out var report))
            {
                // Delete file if exists
                if (!string.IsNullOrEmpty(report.FilePath) && File.Exists(report.FilePath))
                {
                    File.Delete(report.FilePath);
                }

                _reportCache.Remove(reportId);
                return OperationResult<bool>.SuccessResult(true);
            }

            return OperationResult<bool>.FailureResult("Report not found");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete report {ReportId}", reportId);
            return OperationResult<bool>.FailureResult($"Failed to delete report: {ex.Message}");
        }
    }

    public async Task<OperationResult<Report>> ExportReportAsync(
        string reportId,
        ReportFormat targetFormat,
        string? outputPath = null,
        CancellationToken cancellationToken = default)
    {
        var reportResult = await GetReportAsync(reportId, cancellationToken);
        if (!reportResult.Success || reportResult.Data == null)
        {
            return OperationResult<Report>.FailureResult("Report not found");
        }

        var report = reportResult.Data;
        report.Format = targetFormat;
        report.Content = targetFormat switch
        {
            ReportFormat.Html => GenerateHtmlReport(report),
            ReportFormat.Json => GenerateJsonReport(report),
            ReportFormat.Markdown => GenerateMarkdownReport(report),
            _ => throw new NotSupportedException($"Format {targetFormat} is not supported")
        };

        if (!string.IsNullOrEmpty(outputPath))
        {
            await SaveReportToFileAsync(report, outputPath, cancellationToken);
            report.FilePath = outputPath;
        }

        return OperationResult<Report>.SuccessResult(report);
    }

    #region Private Helper Methods

    private async Task<Report> GenerateAuditReportInternalAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken)
    {
        var report = new Report
        {
            Type = ReportType.Audit,
            Format = request.Format,
            Title = request.Title ?? "Audit Report",
            Description = $"Audit log report from {request.StartDate} to {request.EndDate}"
        };

        // Add summary section
        report.Sections.Add(new ReportSection
        {
            Title = "Summary",
            Order = 1,
            Content = $"Period: {request.StartDate:yyyy-MM-dd} to {request.EndDate:yyyy-MM-dd}"
        });

        // Generate content
        report.Content = request.Format switch
        {
            ReportFormat.Html => GenerateHtmlReport(report),
            ReportFormat.Json => GenerateJsonReport(report),
            ReportFormat.Markdown => GenerateMarkdownReport(report),
            _ => throw new NotSupportedException($"Format {request.Format} is not supported")
        };

        return report;
    }

    private async Task<Report> GenerateStatisticsReportInternalAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken)
    {
        var report = new Report
        {
            Type = ReportType.Statistics,
            Format = request.Format,
            Title = request.Title ?? "Statistics Report",
            Description = "System statistics and performance metrics"
        };

        // Get performance metrics
        var metrics = await _monitoringService.GetPerformanceMetricsAsync(cancellationToken);

        report.Sections.Add(new ReportSection
        {
            Title = "Performance Metrics",
            Order = 1,
            Type = SectionType.Table,
            Data = metrics
        });

        report.Content = request.Format switch
        {
            ReportFormat.Html => GenerateHtmlReport(report),
            ReportFormat.Json => GenerateJsonReport(report),
            ReportFormat.Markdown => GenerateMarkdownReport(report),
            _ => throw new NotSupportedException($"Format {request.Format} is not supported")
        };

        return report;
    }

    private async Task<Report> GenerateBatchOperationReportInternalAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken)
    {
        var report = new Report
        {
            Type = ReportType.BatchOperation,
            Format = request.Format,
            Title = request.Title ?? "Batch Operation Report",
            Description = $"Report for batch operation {request.ResourceId}"
        };

        report.Sections.Add(new ReportSection
        {
            Title = "Operation Details",
            Order = 1,
            Content = $"Batch Operation ID: {request.ResourceId}"
        });

        report.Content = request.Format switch
        {
            ReportFormat.Html => GenerateHtmlReport(report),
            ReportFormat.Json => GenerateJsonReport(report),
            ReportFormat.Markdown => GenerateMarkdownReport(report),
            _ => throw new NotSupportedException($"Format {request.Format} is not supported")
        };

        return report;
    }

    private async Task<Report> GenerateSystemHealthReportInternalAsync(
        ReportGenerationRequest request,
        CancellationToken cancellationToken)
    {
        var report = new Report
        {
            Type = ReportType.SystemHealth,
            Format = request.Format,
            Title = request.Title ?? "System Health Report",
            Description = "Current system health and metrics"
        };

        // Get current metrics
        var metrics = await _monitoringService.GetCurrentMetricsAsync(cancellationToken);

        report.Sections.Add(new ReportSection
        {
            Title = "Current Metrics",
            Order = 1,
            Type = SectionType.Table,
            Data = metrics
        });

        report.Content = request.Format switch
        {
            ReportFormat.Html => GenerateHtmlReport(report),
            ReportFormat.Json => GenerateJsonReport(report),
            ReportFormat.Markdown => GenerateMarkdownReport(report),
            _ => throw new NotSupportedException($"Format {request.Format} is not supported")
        };

        return report;
    }

    private string GenerateHtmlReport(Report report)
    {
        var html = new StringBuilder();

        html.AppendLine("<!DOCTYPE html>");
        html.AppendLine("<html><head>");
        html.AppendLine($"<title>{report.Title}</title>");
        html.AppendLine("<style>");
        html.AppendLine("body { font-family: Arial, sans-serif; margin: 20px; }");
        html.AppendLine("h1 { color: #2c3e50; }");
        html.AppendLine("h2 { color: #34495e; }");
        html.AppendLine("table { border-collapse: collapse; width: 100%; margin: 20px 0; }");
        html.AppendLine("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }");
        html.AppendLine("th { background-color: #3498db; color: white; }");
        html.AppendLine(".section { margin: 20px 0; }");
        html.AppendLine("</style>");
        html.AppendLine("</head><body>");

        html.AppendLine($"<h1>{report.Title}</h1>");
        html.AppendLine($"<p>{report.Description}</p>");
        html.AppendLine($"<p><em>Generated: {report.GeneratedAt:yyyy-MM-dd HH:mm:ss} UTC</em></p>");

        foreach (var section in report.Sections.OrderBy(s => s.Order))
        {
            html.AppendLine("<div class='section'>");
            html.AppendLine($"<h2>{section.Title}</h2>");

            if (section.Type == SectionType.Table && section.Data != null)
            {
                html.AppendLine("<table>");
                var json = JsonSerializer.Serialize(section.Data, new JsonSerializerOptions { WriteIndented = true });
                var dict = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
                if (dict != null)
                {
                    foreach (var kvp in dict)
                    {
                        html.AppendLine($"<tr><th>{kvp.Key}</th><td>{kvp.Value}</td></tr>");
                    }
                }
                html.AppendLine("</table>");
            }
            else
            {
                html.AppendLine($"<p>{section.Content.Replace("\n", "<br/>")}</p>");
            }

            html.AppendLine("</div>");
        }

        html.AppendLine("</body></html>");

        return html.ToString();
    }

    private string GenerateJsonReport(Report report)
    {
        return JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
    }

    private string GenerateMarkdownReport(Report report)
    {
        var md = new StringBuilder();

        md.AppendLine($"# {report.Title}");
        md.AppendLine();
        md.AppendLine(report.Description);
        md.AppendLine();
        md.AppendLine($"*Generated: {report.GeneratedAt:yyyy-MM-dd HH:mm:ss} UTC*");
        md.AppendLine();

        foreach (var section in report.Sections.OrderBy(s => s.Order))
        {
            md.AppendLine($"## {section.Title}");
            md.AppendLine();
            md.AppendLine(section.Content);
            md.AppendLine();
        }

        return md.ToString();
    }

    private async Task SaveReportToFileAsync(Report report, string path, CancellationToken cancellationToken)
    {
        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        await File.WriteAllTextAsync(path, report.Content ?? string.Empty, cancellationToken);
        _logger.LogInformation("Report saved to {Path}", path);
    }

    private void GeneratePdfReport(Report report, string outputPath)
    {
        try
        {
            Document.Create(container =>
            {
                container.Page(page =>
                {
                    page.Size(PageSizes.A4);
                    page.Margin(2, Unit.Centimetre);
                    page.PageColor(Colors.White);
                    page.DefaultTextStyle(x => x.FontSize(11).FontFamily("Arial"));

                    page.Header()
                        .Row(row =>
                        {
                            row.RelativeItem().Column(column =>
                            {
                                column.Item().Text("DeployForge")
                                    .FontSize(20)
                                    .Bold()
                                    .FontColor(Colors.Blue.Medium);

                                column.Item().Text(report.Title)
                                    .FontSize(16)
                                    .SemiBold();
                            });

                            row.ConstantItem(100).AlignRight().Text($"{DateTime.UtcNow:yyyy-MM-dd}")
                                .FontSize(9);
                        });

                    page.Content()
                        .PaddingVertical(1, Unit.Centimetre)
                        .Column(column =>
                        {
                            column.Spacing(10);

                            // Description
                            column.Item().Text(report.Description)
                                .FontSize(11)
                                .Italic();

                            column.Item().LineHorizontal(1).LineColor(Colors.Grey.Lighten2);

                            // Generated timestamp
                            column.Item().Text($"Generated: {report.GeneratedAt:yyyy-MM-dd HH:mm:ss} UTC")
                                .FontSize(9)
                                .Italic()
                                .FontColor(Colors.Grey.Darken1);

                            column.Item().PaddingTop(10);

                            // Render sections
                            foreach (var section in report.Sections.OrderBy(s => s.Order))
                            {
                                column.Item().Text(section.Title)
                                    .FontSize(14)
                                    .SemiBold()
                                    .FontColor(Colors.Blue.Darken1);

                                if (section.Type == SectionType.Table && section.Data != null)
                                {
                                    column.Item().Table(table =>
                                    {
                                        table.ColumnsDefinition(columns =>
                                        {
                                            columns.RelativeColumn(2);
                                            columns.RelativeColumn(3);
                                        });

                                        var json = JsonSerializer.Serialize(section.Data);
                                        var dict = JsonSerializer.Deserialize<Dictionary<string, object>>(json);

                                        if (dict != null)
                                        {
                                            foreach (var kvp in dict)
                                            {
                                                table.Cell().Border(1).BorderColor(Colors.Grey.Lighten1)
                                                    .Padding(5).Background(Colors.Blue.Lighten4)
                                                    .Text(kvp.Key).Bold();

                                                table.Cell().Border(1).BorderColor(Colors.Grey.Lighten1)
                                                    .Padding(5)
                                                    .Text(kvp.Value?.ToString() ?? "");
                                            }
                                        }
                                    });
                                }
                                else
                                {
                                    column.Item().Text(section.Content)
                                        .FontSize(10);
                                }

                                column.Item().PaddingBottom(10);
                            }
                        });

                    page.Footer()
                        .AlignCenter()
                        .Text(x =>
                        {
                            x.Span("Page ");
                            x.CurrentPageNumber();
                            x.Span(" of ");
                            x.TotalPages();
                        });
                });
            })
            .GeneratePdf(outputPath);

            _logger.LogInformation("PDF report generated at {Path}", outputPath);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to generate PDF report");
            throw;
        }
    }

    #endregion
}
