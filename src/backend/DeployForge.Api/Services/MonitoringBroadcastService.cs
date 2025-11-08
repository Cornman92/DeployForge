using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace DeployForge.Api.Services;

/// <summary>
/// Background service that broadcasts monitoring metrics to SignalR clients
/// </summary>
public class MonitoringBroadcastService : BackgroundService
{
    private readonly IHubContext<ProgressHub> _hubContext;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<MonitoringBroadcastService> _logger;
    private readonly TimeSpan _broadcastInterval = TimeSpan.FromSeconds(5);

    public MonitoringBroadcastService(
        IHubContext<ProgressHub> hubContext,
        IServiceProvider serviceProvider,
        ILogger<MonitoringBroadcastService> logger)
    {
        _hubContext = hubContext;
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Monitoring broadcast service started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await BroadcastMetricsAsync(stoppingToken);
                await Task.Delay(_broadcastInterval, stoppingToken);
            }
            catch (OperationCanceledException)
            {
                // Normal shutdown
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error broadcasting monitoring metrics");
                await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
            }
        }

        _logger.LogInformation("Monitoring broadcast service stopped");
    }

    private async Task BroadcastMetricsAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var monitoringService = scope.ServiceProvider.GetRequiredService<IMonitoringService>();

        // Get current metrics
        var metrics = await monitoringService.GetCurrentMetricsAsync(cancellationToken);

        if (metrics != null)
        {
            // Broadcast to monitoring group
            await _hubContext.Clients.Group("monitoring").SendAsync(
                "ReceiveMetrics",
                new
                {
                    metrics.Timestamp,
                    metrics.CpuUsage,
                    metrics.MemoryUsage,
                    metrics.TotalMemoryBytes,
                    metrics.AvailableMemoryBytes,
                    metrics.DiskUsage,
                    metrics.TotalDiskSpaceBytes,
                    metrics.ActiveOperations,
                    metrics.Uptime
                },
                cancellationToken);
        }

        // Check for alerts and broadcast if any
        var alertHistory = await monitoringService.GetAlertHistoryAsync(
            DateTime.UtcNow.AddSeconds(-10),
            DateTime.UtcNow,
            cancellationToken);

        if (alertHistory != null && alertHistory.Any())
        {
            foreach (var alert in alertHistory)
            {
                await _hubContext.Clients.Group("alerts").SendAsync(
                    "ReceiveAlert",
                    new
                    {
                        alert.Timestamp,
                        alert.MetricType,
                        alert.Value,
                        alert.Threshold,
                        alert.Message
                    },
                    cancellationToken);
            }
        }
    }
}
