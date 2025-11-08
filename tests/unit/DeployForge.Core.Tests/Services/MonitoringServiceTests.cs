using DeployForge.Core.Services;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace DeployForge.Core.Tests.Services;

public class MonitoringServiceTests
{
    private readonly Mock<ILogger<MonitoringService>> _loggerMock;
    private readonly Mock<IProgressService> _progressServiceMock;
    private readonly MonitoringService _monitoringService;

    public MonitoringServiceTests()
    {
        _loggerMock = new Mock<ILogger<MonitoringService>>();
        _progressServiceMock = new Mock<IProgressService>();
        _progressServiceMock.Setup(x => x.GetActiveOperations()).Returns(5);

        _monitoringService = new MonitoringService(_loggerMock.Object, _progressServiceMock.Object);
    }

    [Fact]
    public async Task GetCurrentMetricsAsync_ReturnsValidMetrics()
    {
        // Act
        var metrics = await _monitoringService.GetCurrentMetricsAsync();

        // Assert
        Assert.NotNull(metrics);
        Assert.True(metrics.CpuUsage >= 0 && metrics.CpuUsage <= 100);
        Assert.True(metrics.MemoryUsage >= 0 && metrics.MemoryUsage <= 100);
        Assert.True(metrics.DiskUsage >= 0 && metrics.DiskUsage <= 100);
        Assert.Equal(5, metrics.ActiveOperations);
    }

    [Fact]
    public async Task StartMonitoringAsync_StartsMonitoring()
    {
        // Act
        await _monitoringService.StartMonitoringAsync();

        // Assert
        Assert.True(_monitoringService.IsMonitoring);
    }

    [Fact]
    public async Task StopMonitoringAsync_StopsMonitoring()
    {
        // Arrange
        await _monitoringService.StartMonitoringAsync();

        // Act
        await _monitoringService.StopMonitoringAsync();

        // Assert
        Assert.False(_monitoringService.IsMonitoring);
    }

    [Fact]
    public async Task GetMetricsHistoryAsync_ReturnsEmptyInitially()
    {
        // Act
        var history = await _monitoringService.GetMetricsHistoryAsync(
            DateTime.UtcNow.AddHours(-1),
            DateTime.UtcNow);

        // Assert
        Assert.NotNull(history);
        Assert.Empty(history);
    }

    [Fact]
    public async Task GetPerformanceMetricsAsync_ReturnsValidMetrics()
    {
        // Act
        var metrics = await _monitoringService.GetPerformanceMetricsAsync();

        // Assert
        Assert.NotNull(metrics);
        Assert.True(metrics.Timestamp > DateTime.MinValue);
    }

    [Fact]
    public async Task ConfigureAlertThresholdsAsync_UpdatesThresholds()
    {
        // Arrange
        var thresholds = new Common.Models.Monitoring.AlertThreshold
        {
            CpuThreshold = 85,
            MemoryThreshold = 85,
            DiskThreshold = 85,
            MaxConcurrentOperations = 15
        };

        // Act
        await _monitoringService.ConfigureAlertThresholdsAsync(thresholds);
        var result = await _monitoringService.GetAlertThresholdsAsync();

        // Assert
        Assert.NotNull(result);
        Assert.Equal(85, result.CpuThreshold);
        Assert.Equal(85, result.MemoryThreshold);
        Assert.Equal(15, result.MaxConcurrentOperations);
    }

    [Fact]
    public async Task GetAlertHistoryAsync_ReturnsEmptyInitially()
    {
        // Act
        var history = await _monitoringService.GetAlertHistoryAsync();

        // Assert
        Assert.NotNull(history);
        Assert.Empty(history);
    }
}
