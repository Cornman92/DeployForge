using System.Net;
using System.Net.Http.Json;
using DeployForge.Common.Models.Monitoring;
using FluentAssertions;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for monitoring workflow:
/// System metrics collection → Alert threshold configuration → Alert triggered → Notification sent
/// </summary>
[Collection("API Integration Tests")]
public class MonitoringWorkflowTests
{
    private readonly HttpClient _client;

    public MonitoringWorkflowTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task MonitoringWorkflow_EndToEnd_Success()
    {
        // Step 1: Verify monitoring service is running
        var healthResponse = await _client.GetAsync("/api/health");
        healthResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var healthData = await healthResponse.Content.ReadFromJsonAsync<HealthResponse>();
        healthData.Should().NotBeNull();
        healthData!.Status.Should().Be("Healthy");

        // Step 2: Get current metrics
        var metricsResponse = await _client.GetAsync("/api/health/metrics");
        metricsResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var metrics = await metricsResponse.Content.ReadFromJsonAsync<SystemMetrics>();
        metrics.Should().NotBeNull();
        metrics!.CpuUsage.Should().BeGreaterThanOrEqualTo(0).And.BeLessThanOrEqualTo(100);
        metrics.MemoryUsage.Should().BeGreaterThanOrEqualTo(0).And.BeLessThanOrEqualTo(100);
        metrics.TotalMemoryBytes.Should().BeGreaterThan(0);

        // Step 3: Configure alert thresholds
        var alertConfig = new
        {
            CpuThreshold = 80.0,
            MemoryThreshold = 85.0,
            DiskThreshold = 90.0,
            Enabled = true
        };

        var configResponse = await _client.PostAsJsonAsync("/api/health/alerts/configure", alertConfig);
        configResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Step 4: Verify alert configuration was saved
        var getAlertsResponse = await _client.GetAsync("/api/health/alerts");
        getAlertsResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var savedConfig = await getAlertsResponse.Content.ReadFromJsonAsync<AlertThreshold>();
        savedConfig.Should().NotBeNull();
        savedConfig!.CpuThreshold.Should().Be(80.0);
        savedConfig.MemoryThreshold.Should().Be(85.0);
        savedConfig.DiskThreshold.Should().Be(90.0);

        // Step 5: Get performance metrics
        var perfResponse = await _client.GetAsync("/api/health/performance");
        perfResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var perfMetrics = await perfResponse.Content.ReadFromJsonAsync<PerformanceMetrics>();
        perfMetrics.Should().NotBeNull();
        perfMetrics!.TotalMetricsCollected.Should().BeGreaterThan(0);

        // Step 6: Get metrics history
        var endTime = DateTime.UtcNow;
        var startTime = endTime.AddMinutes(-5);
        var historyResponse = await _client.GetAsync(
            $"/api/health/metrics/history?startTime={startTime:o}&endTime={endTime:o}");
        historyResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await historyResponse.Content.ReadFromJsonAsync<List<SystemMetrics>>();
        history.Should().NotBeNull();
        history!.Should().NotBeEmpty();

        // Step 7: Get alert history
        var alertHistoryResponse = await _client.GetAsync("/api/health/alerts/history");
        alertHistoryResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var alertHistory = await alertHistoryResponse.Content.ReadFromJsonAsync<List<AlertEvent>>();
        alertHistory.Should().NotBeNull();
    }

    [Fact]
    public async Task GetCurrentMetrics_ReturnsValidData()
    {
        var response = await _client.GetAsync("/api/health/metrics");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var metrics = await response.Content.ReadFromJsonAsync<SystemMetrics>();
        metrics.Should().NotBeNull();
        metrics!.Timestamp.Should().BeCloseTo(DateTime.UtcNow, TimeSpan.FromMinutes(1));
    }

    [Fact]
    public async Task ConfigureAlerts_WithValidThresholds_Success()
    {
        var config = new
        {
            CpuThreshold = 75.0,
            MemoryThreshold = 80.0,
            DiskThreshold = 85.0,
            Enabled = true
        };

        var response = await _client.PostAsJsonAsync("/api/health/alerts/configure", config);
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task GetMetricsHistory_WithTimeRange_ReturnsFilteredData()
    {
        var endTime = DateTime.UtcNow;
        var startTime = endTime.AddHours(-1);

        var response = await _client.GetAsync(
            $"/api/health/metrics/history?startTime={startTime:o}&endTime={endTime:o}");

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await response.Content.ReadFromJsonAsync<List<SystemMetrics>>();
        history.Should().NotBeNull();

        foreach (var metric in history!)
        {
            metric.Timestamp.Should().BeOnOrAfter(startTime).And.BeOnOrBefore(endTime);
        }
    }

    [Fact]
    public async Task HealthDiagnostics_ReturnsComprehensiveInfo()
    {
        var response = await _client.GetAsync("/api/health/diagnostics");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var diagnostics = await response.Content.ReadFromJsonAsync<DiagnosticsResponse>();
        diagnostics.Should().NotBeNull();
        diagnostics!.Status.Should().Be("Healthy");
        diagnostics.System.Should().NotBeNull();
        diagnostics.Dism.Should().NotBeNull();
        diagnostics.Permissions.Should().NotBeNull();
    }
}

// Helper DTOs for integration tests
public class HealthResponse
{
    public string Status { get; set; } = string.Empty;
    public string Version { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public TimeSpan Uptime { get; set; }
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
}

public class DiagnosticsResponse
{
    public string Status { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public string Version { get; set; } = string.Empty;
    public TimeSpan Uptime { get; set; }
    public SystemInfo System { get; set; } = new();
    public DismStatus Dism { get; set; } = new();
    public PermissionsStatus Permissions { get; set; } = new();
    public ServicesStatus Services { get; set; } = new();
}

public class SystemInfo
{
    public string OperatingSystem { get; set; } = string.Empty;
    public string Architecture { get; set; } = string.Empty;
    public int ProcessorCount { get; set; }
    public string MachineName { get; set; } = string.Empty;
}

public class DismStatus
{
    public bool IsAvailable { get; set; }
    public bool IsInitialized { get; set; }
    public string Message { get; set; } = string.Empty;
}

public class PermissionsStatus
{
    public bool IsAdministrator { get; set; }
    public bool CanAccessDism { get; set; }
    public bool CanWriteTemp { get; set; }
    public string Message { get; set; } = string.Empty;
}

public class ServicesStatus
{
    public string DismManager { get; set; } = string.Empty;
    public int TotalServices { get; set; }
    public List<string> RegisteredServices { get; set; } = new();
}
