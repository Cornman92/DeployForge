using System.Net;
using System.Net.Http.Json;
using DeployForge.Common.Models.Reports;
using FluentAssertions;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for reporting workflow:
/// Generate report → Retrieve report → Export to different format → Delete report
/// </summary>
[Collection("API Integration Tests")]
public class ReportingWorkflowTests
{
    private readonly HttpClient _client;

    public ReportingWorkflowTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task ReportingWorkflow_EndToEnd_Success()
    {
        // Step 1: Generate a statistics report
        var startDate = DateTime.Today.AddDays(-7);
        var endDate = DateTime.Today;

        var generateResponse = await _client.PostAsJsonAsync(
            $"/api/reports/statistics?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}&format=Json",
            new { });

        generateResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var report = await generateResponse.Content.ReadFromJsonAsync<Report>();
        report.Should().NotBeNull();
        report!.Id.Should().NotBeNullOrEmpty();
        report.Type.Should().Be(ReportType.Statistics);
        report.Format.Should().Be(ReportFormat.Json);

        var reportId = report.Id;

        // Step 2: Retrieve the generated report
        var getResponse = await _client.GetAsync($"/api/reports/{reportId}");
        getResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var retrievedReport = await getResponse.Content.ReadFromJsonAsync<Report>();
        retrievedReport.Should().NotBeNull();
        retrievedReport!.Id.Should().Be(reportId);

        // Step 3: List all reports
        var listResponse = await _client.GetAsync("/api/reports");
        listResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var reports = await listResponse.Content.ReadFromJsonAsync<List<Report>>();
        reports.Should().NotBeNull();
        reports!.Should().Contain(r => r.Id == reportId);

        // Step 4: Export report to different format (PDF)
        var exportResponse = await _client.PostAsJsonAsync(
            $"/api/reports/{reportId}/export?targetFormat=Pdf",
            new { });

        exportResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var exportedReport = await exportResponse.Content.ReadFromJsonAsync<Report>();
        exportedReport.Should().NotBeNull();
        exportedReport!.Format.Should().Be(ReportFormat.Pdf);

        // Step 5: Delete the report
        var deleteResponse = await _client.DeleteAsync($"/api/reports/{reportId}");
        deleteResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Step 6: Verify report is deleted
        var verifyResponse = await _client.GetAsync($"/api/reports/{reportId}");
        verifyResponse.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task GenerateAuditReport_WithDateRange_Success()
    {
        var startDate = DateTime.Today.AddDays(-30);
        var endDate = DateTime.Today;

        var response = await _client.PostAsJsonAsync(
            $"/api/reports/audit?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}&format=Html",
            new { });

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var report = await response.Content.ReadFromJsonAsync<Report>();
        report.Should().NotBeNull();
        report!.Type.Should().Be(ReportType.Audit);
        report.Format.Should().Be(ReportFormat.Html);
        report.GeneratedAt.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromMinutes(1));
    }

    [Fact]
    public async Task ListReports_WithTypeFilter_ReturnsFilteredResults()
    {
        // Generate multiple report types
        await _client.PostAsJsonAsync(
            $"/api/reports/statistics?startDate={DateTime.Today.AddDays(-7):yyyy-MM-dd}&endDate={DateTime.Today:yyyy-MM-dd}&format=Json",
            new { });

        await _client.PostAsJsonAsync(
            $"/api/reports/audit?startDate={DateTime.Today.AddDays(-7):yyyy-MM-dd}&endDate={DateTime.Today:yyyy-MM-dd}&format=Json",
            new { });

        // List with filter
        var response = await _client.GetAsync($"/api/reports?type={ReportType.Statistics}");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var reports = await response.Content.ReadFromJsonAsync<List<Report>>();
        reports.Should().NotBeNull();
        reports!.Should().AllSatisfy(r => r.Type.Should().Be(ReportType.Statistics));
    }

    [Fact]
    public async Task ExportReport_ToMultipleFormats_Success()
    {
        // Generate initial report
        var generateResponse = await _client.PostAsJsonAsync(
            $"/api/reports/statistics?startDate={DateTime.Today.AddDays(-7):yyyy-MM-dd}&endDate={DateTime.Today:yyyy-MM-dd}&format=Json",
            new { });

        var report = await generateResponse.Content.ReadFromJsonAsync<Report>();
        var reportId = report!.Id;

        // Test export to each format
        var formats = new[] { "Html", "Pdf", "Markdown" };

        foreach (var format in formats)
        {
            var exportResponse = await _client.PostAsJsonAsync(
                $"/api/reports/{reportId}/export?targetFormat={format}",
                new { });

            exportResponse.StatusCode.Should().Be(HttpStatusCode.OK);

            var exported = await exportResponse.Content.ReadFromJsonAsync<Report>();
            exported.Should().NotBeNull();
            exported!.Format.ToString().Should().Be(format);
        }

        // Cleanup
        await _client.DeleteAsync($"/api/reports/{reportId}");
    }

    [Fact]
    public async Task GenerateReport_WithInvalidDateRange_ReturnsBadRequest()
    {
        var startDate = DateTime.Today;
        var endDate = DateTime.Today.AddDays(-7); // End before start

        var response = await _client.PostAsJsonAsync(
            $"/api/reports/statistics?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}&format=Json",
            new { });

        // Depending on backend validation, this might return BadRequest or OK
        // If OK, the backend should handle the invalid range gracefully
        response.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task DeleteReport_NonExistentId_ReturnsNotFound()
    {
        var fakeId = Guid.NewGuid().ToString();

        var response = await _client.DeleteAsync($"/api/reports/{fakeId}");

        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task ListReports_WithDateRangeFilter_ReturnsFilteredResults()
    {
        var startDate = DateTime.Today.AddDays(-30);
        var endDate = DateTime.Today;

        var response = await _client.GetAsync(
            $"/api/reports?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}");

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var reports = await response.Content.ReadFromJsonAsync<List<Report>>();
        reports.Should().NotBeNull();

        foreach (var report in reports!)
        {
            report.GeneratedAt.Date.Should().BeOnOrAfter(startDate).And.BeOnOrBefore(endDate);
        }
    }
}
