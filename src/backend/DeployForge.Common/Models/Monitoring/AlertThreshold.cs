namespace DeployForge.Common.Models.Monitoring;

/// <summary>
/// Alert threshold configuration
/// </summary>
public class AlertThreshold
{
    /// <summary>
    /// CPU usage threshold percentage (0-100)
    /// </summary>
    public double CpuThreshold { get; set; } = 90;

    /// <summary>
    /// Memory usage threshold percentage (0-100)
    /// </summary>
    public double MemoryThreshold { get; set; } = 90;

    /// <summary>
    /// Disk usage threshold percentage (0-100)
    /// </summary>
    public double DiskThreshold { get; set; } = 90;

    /// <summary>
    /// Maximum concurrent operations threshold
    /// </summary>
    public int MaxConcurrentOperations { get; set; } = 10;

    /// <summary>
    /// Operation duration threshold in milliseconds
    /// </summary>
    public long OperationDurationThresholdMs { get; set; } = 300000; // 5 minutes

    /// <summary>
    /// Enable CPU alerts
    /// </summary>
    public bool EnableCpuAlerts { get; set; } = true;

    /// <summary>
    /// Enable memory alerts
    /// </summary>
    public bool EnableMemoryAlerts { get; set; } = true;

    /// <summary>
    /// Enable disk alerts
    /// </summary>
    public bool EnableDiskAlerts { get; set; } = true;

    /// <summary>
    /// Enable operation alerts
    /// </summary>
    public bool EnableOperationAlerts { get; set; } = true;

    /// <summary>
    /// Alert cooldown period (minutes) to prevent spam
    /// </summary>
    public int AlertCooldownMinutes { get; set; } = 15;
}
