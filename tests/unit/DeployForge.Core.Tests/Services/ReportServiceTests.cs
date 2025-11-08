using DeployForge.Core.Services;
using DeployForge.Core.Interfaces;
using DeployForge.Common.Models;
using DeployForge.Common.Models.Reports;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace DeployForge.Core.Tests.Services;

public class ReportServiceTests
{
    private readonly Mock<ILogger<ReportService>> _loggerMock;
    private readonly Mock<IAuditLogService> _auditLogServiceMock;
    private readonly Mock<IMonitoringService> _monitoringServiceMock;
    private readonly Mock<IBatchOperationService> _batchOperationServiceMock;
    private readonly ReportService _reportService;

    public ReportServiceTests()
    {
        _loggerMock = new Mock<ILogger<ReportService>>();
        _auditLogServiceMock = new Mock<IAuditLogService>();
        _monitoringServiceMock = new Mock<IMonitoringService>();
        _batchOperationServiceMock = new Mock<IBatchOperationService>();

        _reportService = new ReportService(
            _loggerMock.Object,
            _auditLogServiceMock.Object,
            _monitoringServiceMock.Object,
            _batchOperationServiceMock.Object);
    }

    [Fact]
    public async Task GenerateValidationReportAsync_HtmlFormat_ReturnsValidReport()
    {
        // Arrange
        var validationResult = new ValidationResult
        {
            ImagePath = @"C:\test\install.wim",
            Status = ValidationStatus.Completed,
            TotalChecks = 10,
            PassedChecks = 8,
            FailedChecks = 2,
            Checks = new List<ValidationCheck>
            {
                new ValidationCheck
                {
                    Name = "File Integrity",
                    Status = CheckStatus.Passed,
                    Message = "All files are intact",
                    Category = ValidationCategory.Integrity
                }
            }
        };

        // Act
        var result = await _reportService.GenerateValidationReportAsync(
            validationResult,
            ReportFormat.Html);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Data);
        Assert.Equal(ReportFormat.Html, result.Data.Format);
        Assert.Equal(ReportType.Validation, result.Data.Type);
        Assert.Contains("<!DOCTYPE html>", result.Data.Content);
        Assert.Contains("File Integrity", result.Data.Content);
    }

    [Fact]
    public async Task GenerateValidationReportAsync_JsonFormat_ReturnsValidJson()
    {
        // Arrange
        var validationResult = new ValidationResult
        {
            ImagePath = @"C:\test\install.wim",
            Status = ValidationStatus.Completed,
            TotalChecks = 5,
            PassedChecks = 5
        };

        // Act
        var result = await _reportService.GenerateValidationReportAsync(
            validationResult,
            ReportFormat.Json);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Data);
        Assert.Equal(ReportFormat.Json, result.Data.Format);
        Assert.Contains("\"Type\":", result.Data.Content);
        Assert.Contains("\"Validation\"", result.Data.Content);
    }

    [Fact]
    public async Task GenerateValidationReportAsync_MarkdownFormat_ReturnsValidMarkdown()
    {
        // Arrange
        var validationResult = new ValidationResult
        {
            ImagePath = @"C:\test\install.wim",
            Status = ValidationStatus.Completed
        };

        // Act
        var result = await _reportService.GenerateValidationReportAsync(
            validationResult,
            ReportFormat.Markdown);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Data);
        Assert.Equal(ReportFormat.Markdown, result.Data.Format);
        Assert.StartsWith("# ", result.Data.Content);
    }

    [Fact]
    public async Task GetReportAsync_ExistingReport_ReturnsReport()
    {
        // Arrange
        var validationResult = new ValidationResult { ImagePath = @"C:\test\install.wim" };
        var createResult = await _reportService.GenerateValidationReportAsync(validationResult);
        var reportId = createResult.Data!.Id;

        // Act
        var result = await _reportService.GetReportAsync(reportId);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Data);
        Assert.Equal(reportId, result.Data.Id);
    }

    [Fact]
    public async Task GetReportAsync_NonExistentReport_ReturnsFailure()
    {
        // Act
        var result = await _reportService.GetReportAsync("non-existent-id");

        // Assert
        Assert.False(result.Success);
        Assert.Equal("Report not found", result.ErrorMessage);
    }

    [Fact]
    public async Task DeleteReportAsync_ExistingReport_DeletesSuccessfully()
    {
        // Arrange
        var validationResult = new ValidationResult { ImagePath = @"C:\test\install.wim" };
        var createResult = await _reportService.GenerateValidationReportAsync(validationResult);
        var reportId = createResult.Data!.Id;

        // Act
        var deleteResult = await _reportService.DeleteReportAsync(reportId);
        var getResult = await _reportService.GetReportAsync(reportId);

        // Assert
        Assert.True(deleteResult.Success);
        Assert.False(getResult.Success);
    }

    [Fact]
    public async Task ListReportsAsync_FiltersCorrectly()
    {
        // Arrange
        var validationResult = new ValidationResult { ImagePath = @"C:\test\install.wim" };
        await _reportService.GenerateValidationReportAsync(validationResult);

        // Act
        var result = await _reportService.ListReportsAsync(ReportType.Validation);

        // Assert
        Assert.True(result.Success);
        Assert.NotNull(result.Data);
        Assert.All(result.Data, r => Assert.Equal(ReportType.Validation, r.Type));
    }

    [Fact]
    public async Task ExportReportAsync_ChangesFormat()
    {
        // Arrange
        var validationResult = new ValidationResult { ImagePath = @"C:\test\install.wim" };
        var createResult = await _reportService.GenerateValidationReportAsync(
            validationResult,
            ReportFormat.Html);
        var reportId = createResult.Data!.Id;

        // Act
        var exportResult = await _reportService.ExportReportAsync(
            reportId,
            ReportFormat.Json);

        // Assert
        Assert.True(exportResult.Success);
        Assert.NotNull(exportResult.Data);
        Assert.Equal(ReportFormat.Json, exportResult.Data.Format);
        Assert.Contains("{", exportResult.Data.Content);
    }
}
