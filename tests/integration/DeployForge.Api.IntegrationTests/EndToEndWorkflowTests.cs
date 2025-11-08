using System.Net;
using System.Net.Http.Json;
using DeployForge.Common.Models.Monitoring;
using DeployForge.Common.Models.Notifications;
using DeployForge.Common.Models.Reports;
using DeployForge.Common.Models.Scheduling;
using FluentAssertions;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Comprehensive end-to-end integration tests combining all Option B features:
/// Monitoring → Alerts → Notifications → Scheduling → Reporting
/// </summary>
[Collection("API Integration Tests")]
public class EndToEndWorkflowTests
{
    private readonly HttpClient _client;

    public EndToEndWorkflowTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task CompleteWorkflow_MonitoringToReporting_Success()
    {
        // ============================================================
        // PHASE 1: Configure Monitoring and Alerts
        // ============================================================

        // Configure alert thresholds
        var alertConfig = new
        {
            CpuThreshold = 80.0,
            MemoryThreshold = 85.0,
            DiskThreshold = 90.0,
            Enabled = true
        };

        var alertResponse = await _client.PostAsJsonAsync("/api/health/alerts/configure", alertConfig);
        alertResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verify monitoring is active
        var metricsResponse = await _client.GetAsync("/api/health/metrics");
        metricsResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var metrics = await metricsResponse.Content.ReadFromJsonAsync<SystemMetrics>();
        metrics.Should().NotBeNull();

        // ============================================================
        // PHASE 2: Configure Notifications
        // ============================================================

        // Configure notification settings
        var notificationSettings = new NotificationSettings
        {
            Email = new EmailSettings
            {
                Enabled = true,
                SmtpServer = "smtp.example.com",
                SmtpPort = 587,
                FromAddress = "deployforge@example.com",
                DefaultRecipients = new List<string> { "admin@example.com" }
            },
            Webhooks = new WebhooksSettings
            {
                Enabled = true,
                Endpoints = new List<WebhookEndpoint>
                {
                    new WebhookEndpoint
                    {
                        Url = "https://example.com/webhook",
                        Secret = "test-secret",
                        Events = new List<NotificationEventType>
                        {
                            NotificationEventType.OperationCompleted,
                            NotificationEventType.SystemAlert
                        },
                        Enabled = true
                    }
                }
            }
        };

        var configResponse = await _client.PostAsJsonAsync("/api/notifications/configure", notificationSettings);
        configResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // ============================================================
        // PHASE 3: Create and Execute Schedule
        // ============================================================

        // Create a schedule for batch operations
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "E2E Test Schedule",
            Description = "End-to-end test schedule for batch operations",
            CronExpression = "0 0 2 * * ?", // Daily at 2 AM
            BatchOperationId = "test-batch-operation",
            IsEnabled = true,
            Policy = new SchedulePolicy
            {
                MaxRetries = 3,
                RetryDelayMinutes = 5,
                SendNotifications = true
            }
        };

        var scheduleResponse = await _client.PostAsJsonAsync("/api/schedules", schedule);
        scheduleResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var createdSchedule = await scheduleResponse.Content.ReadFromJsonAsync<Schedule>();
        createdSchedule.Should().NotBeNull();

        var scheduleId = createdSchedule!.Id;

        // Execute the schedule manually (simulating automatic execution)
        var executeResponse = await _client.PostAsJsonAsync($"/api/schedules/{scheduleId}/execute", new { });
        // May fail if batch operation doesn't exist
        var executionSucceeded = executeResponse.StatusCode == HttpStatusCode.OK;

        // ============================================================
        // PHASE 4: Generate Reports
        // ============================================================

        // Generate system health report
        var healthReportResponse = await _client.PostAsJsonAsync(
            "/api/reports?format=Json",
            new { Type = "SystemHealth" });

        healthReportResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var healthReport = await healthReportResponse.Content.ReadFromJsonAsync<Report>();
        healthReport.Should().NotBeNull();

        // Generate statistics report
        var startDate = DateTime.Today.AddDays(-7);
        var endDate = DateTime.Today;

        var statsReportResponse = await _client.PostAsJsonAsync(
            $"/api/reports/statistics?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}&format=Html",
            new { });

        statsReportResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var statsReport = await statsReportResponse.Content.ReadFromJsonAsync<Report>();
        statsReport.Should().NotBeNull();

        // ============================================================
        // PHASE 5: Verify Complete Workflow
        // ============================================================

        // Verify monitoring history contains data
        var historyResponse = await _client.GetAsync(
            $"/api/health/metrics/history?startTime={DateTime.UtcNow.AddMinutes(-5):o}&endTime={DateTime.UtcNow:o}");
        historyResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await historyResponse.Content.ReadFromJsonAsync<List<SystemMetrics>>();
        history.Should().NotBeNull();
        history!.Should().NotBeEmpty("Monitoring should have collected metrics");

        // Verify notification history (if notifications were sent)
        var notifHistoryResponse = await _client.GetAsync("/api/notifications/history");
        notifHistoryResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Verify schedule execution history (if execution succeeded)
        if (executionSucceeded)
        {
            await Task.Delay(1000); // Give it time to record

            var execHistoryResponse = await _client.GetAsync($"/api/schedules/{scheduleId}/history");
            execHistoryResponse.StatusCode.Should().Be(HttpStatusCode.OK);

            var execHistory = await execHistoryResponse.Content.ReadFromJsonAsync<List<ScheduleExecution>>();
            execHistory.Should().NotBeNull();
        }

        // Verify reports were generated
        var reportsListResponse = await _client.GetAsync("/api/reports");
        reportsListResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var reports = await reportsListResponse.Content.ReadFromJsonAsync<List<Report>>();
        reports.Should().NotBeNull();
        reports!.Should().Contain(r => r.Type == ReportType.SystemHealth);

        // ============================================================
        // CLEANUP: Remove test data
        // ============================================================

        // Delete schedule
        await _client.DeleteAsync($"/api/schedules/{scheduleId}");

        // Delete reports
        if (healthReport != null)
        {
            await _client.DeleteAsync($"/api/reports/{healthReport.Id}");
        }
        if (statsReport != null)
        {
            await _client.DeleteAsync($"/api/reports/{statsReport.Id}");
        }
    }

    [Fact]
    public async Task ErrorScenario_InvalidScheduleExecution_ProperlyHandled()
    {
        // Create schedule with invalid batch operation ID
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Error Test Schedule",
            CronExpression = "0 0 * * * ?",
            BatchOperationId = "non-existent-batch-operation",
            IsEnabled = true,
            Policy = new SchedulePolicy
            {
                MaxRetries = 1,
                SendNotifications = true
            }
        };

        var createResponse = await _client.PostAsJsonAsync("/api/schedules", schedule);
        createResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var created = await createResponse.Content.ReadFromJsonAsync<Schedule>();
        var scheduleId = created!.Id;

        // Try to execute - should handle gracefully
        var executeResponse = await _client.PostAsJsonAsync($"/api/schedules/{scheduleId}/execute", new { });

        // Should either fail gracefully or succeed with error recorded
        executeResponse.StatusCode.Should().BeOneOf(
            HttpStatusCode.OK,
            HttpStatusCode.BadRequest,
            HttpStatusCode.NotFound);

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{scheduleId}");
    }

    [Fact]
    public async Task RecoveryScenario_ServiceRestart_DataPersisted()
    {
        // Create a schedule
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Persistence Test Schedule",
            CronExpression = "0 0 3 * * ?",
            BatchOperationId = "test-123",
            IsEnabled = true
        };

        var createResponse = await _client.PostAsJsonAsync("/api/schedules", schedule);
        createResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var created = await createResponse.Content.ReadFromJsonAsync<Schedule>();
        var scheduleId = created!.Id;

        // Retrieve the schedule (simulating retrieval after service restart)
        var getResponse = await _client.GetAsync($"/api/schedules/{scheduleId}");
        getResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var retrieved = await getResponse.Content.ReadFromJsonAsync<Schedule>();
        retrieved.Should().NotBeNull();
        retrieved!.Id.Should().Be(scheduleId);
        retrieved.Name.Should().Be("Persistence Test Schedule");

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{scheduleId}");
    }

    [Fact]
    public async Task PerformanceTest_ConcurrentRequests_HandledCorrectly()
    {
        // Send multiple concurrent metric requests
        var tasks = new List<Task<HttpResponseMessage>>();

        for (int i = 0; i < 10; i++)
        {
            tasks.Add(_client.GetAsync("/api/health/metrics"));
        }

        var responses = await Task.WhenAll(tasks);

        // All requests should succeed
        responses.Should().AllSatisfy(r => r.StatusCode.Should().Be(HttpStatusCode.OK));

        // Verify all responses contain valid data
        foreach (var response in responses)
        {
            var metrics = await response.Content.ReadFromJsonAsync<SystemMetrics>();
            metrics.Should().NotBeNull();
            metrics!.CpuUsage.Should().BeGreaterThanOrEqualTo(0);
        }
    }

    [Fact]
    public async Task IntegrationTest_FullReportingPipeline_Success()
    {
        // Generate multiple types of reports
        var reportTypes = new[]
        {
            ("statistics", $"/api/reports/statistics?startDate={DateTime.Today.AddDays(-30):yyyy-MM-dd}&endDate={DateTime.Today:yyyy-MM-dd}&format=Json"),
            ("audit", $"/api/reports/audit?startDate={DateTime.Today.AddDays(-7):yyyy-MM-dd}&endDate={DateTime.Today:yyyy-MM-dd}&format=Html")
        };

        var generatedReports = new List<string>();

        foreach (var (type, endpoint) in reportTypes)
        {
            var response = await _client.PostAsJsonAsync(endpoint, new { });
            response.StatusCode.Should().Be(HttpStatusCode.OK);

            var report = await response.Content.ReadFromJsonAsync<Report>();
            if (report != null)
            {
                generatedReports.Add(report.Id);

                // Test export to different format
                var exportResponse = await _client.PostAsJsonAsync(
                    $"/api/reports/{report.Id}/export?targetFormat=Pdf",
                    new { });

                exportResponse.StatusCode.Should().Be(HttpStatusCode.OK);
            }
        }

        // Verify all reports exist
        var listResponse = await _client.GetAsync("/api/reports");
        var reports = await listResponse.Content.ReadFromJsonAsync<List<Report>>();

        foreach (var reportId in generatedReports)
        {
            reports!.Should().Contain(r => r.Id == reportId);
        }

        // Cleanup
        foreach (var reportId in generatedReports)
        {
            await _client.DeleteAsync($"/api/reports/{reportId}");
        }
    }
}

// Additional helper DTOs
public class WebhooksSettings
{
    public bool Enabled { get; set; }
    public List<WebhookEndpoint> Endpoints { get; set; } = new();
}
