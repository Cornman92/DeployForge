using DeployForge.Common.Models.Monitoring;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for system monitoring and health metrics
/// </summary>
public interface IMonitoringService
{
    /// <summary>
    /// Get current system metrics
    /// </summary>
    Task<SystemMetrics> GetCurrentMetricsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get historical metrics within a time range
    /// </summary>
    Task<IEnumerable<SystemMetrics>> GetMetricsHistoryAsync(
        DateTime startTime,
        DateTime endTime,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get performance statistics
    /// </summary>
    Task<PerformanceMetrics> GetPerformanceMetricsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Configure alert thresholds
    /// </summary>
    Task ConfigureAlertThresholdsAsync(AlertThreshold thresholds, CancellationToken cancellationToken = default);

    /// <summary>
    /// Get current alert configuration
    /// </summary>
    Task<AlertThreshold> GetAlertThresholdsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get alert history
    /// </summary>
    Task<IEnumerable<AlertEvent>> GetAlertHistoryAsync(
        DateTime? startTime = null,
        DateTime? endTime = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Start metrics collection
    /// </summary>
    Task StartMonitoringAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Stop metrics collection
    /// </summary>
    Task StopMonitoringAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if monitoring is active
    /// </summary>
    bool IsMonitoring { get; }
}
