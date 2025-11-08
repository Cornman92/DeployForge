namespace DeployForge.Common.Models.Monitoring;

/// <summary>
/// Performance metrics and statistics
/// </summary>
public class PerformanceMetrics
{
    /// <summary>
    /// Timestamp
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Total operations completed
    /// </summary>
    public long TotalOperations { get; set; }

    /// <summary>
    /// Successful operations
    /// </summary>
    public long SuccessfulOperations { get; set; }

    /// <summary>
    /// Failed operations
    /// </summary>
    public long FailedOperations { get; set; }

    /// <summary>
    /// Average operation duration in milliseconds
    /// </summary>
    public double AverageOperationDurationMs { get; set; }

    /// <summary>
    /// Minimum operation duration in milliseconds
    /// </summary>
    public double MinOperationDurationMs { get; set; }

    /// <summary>
    /// Maximum operation duration in milliseconds
    /// </summary>
    public double MaxOperationDurationMs { get; set; }

    /// <summary>
    /// Operations per minute (throughput)
    /// </summary>
    public double OperationsPerMinute { get; set; }

    /// <summary>
    /// Request count in last hour
    /// </summary>
    public int RequestsLastHour { get; set; }

    /// <summary>
    /// Request count in last day
    /// </summary>
    public int RequestsLastDay { get; set; }

    /// <summary>
    /// Average CPU usage over time period
    /// </summary>
    public double AverageCpuUsage { get; set; }

    /// <summary>
    /// Average memory usage over time period
    /// </summary>
    public double AverageMemoryUsage { get; set; }

    /// <summary>
    /// Peak CPU usage
    /// </summary>
    public double PeakCpuUsage { get; set; }

    /// <summary>
    /// Peak memory usage
    /// </summary>
    public double PeakMemoryUsage { get; set; }
}
