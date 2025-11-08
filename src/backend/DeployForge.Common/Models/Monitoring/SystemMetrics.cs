namespace DeployForge.Common.Models.Monitoring;

/// <summary>
/// System metrics snapshot
/// </summary>
public class SystemMetrics
{
    /// <summary>
    /// Timestamp of the metrics snapshot
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// CPU usage percentage (0-100)
    /// </summary>
    public double CpuUsage { get; set; }

    /// <summary>
    /// Memory usage percentage (0-100)
    /// </summary>
    public double MemoryUsage { get; set; }

    /// <summary>
    /// Total memory in bytes
    /// </summary>
    public long TotalMemoryBytes { get; set; }

    /// <summary>
    /// Available memory in bytes
    /// </summary>
    public long AvailableMemoryBytes { get; set; }

    /// <summary>
    /// Used memory in bytes
    /// </summary>
    public long UsedMemoryBytes { get; set; }

    /// <summary>
    /// Total disk space in bytes
    /// </summary>
    public long TotalDiskSpaceBytes { get; set; }

    /// <summary>
    /// Available disk space in bytes
    /// </summary>
    public long AvailableDiskSpaceBytes { get; set; }

    /// <summary>
    /// Disk usage percentage (0-100)
    /// </summary>
    public double DiskUsage { get; set; }

    /// <summary>
    /// Number of active operations
    /// </summary>
    public int ActiveOperations { get; set; }

    /// <summary>
    /// Application uptime
    /// </summary>
    public TimeSpan Uptime { get; set; }
}
