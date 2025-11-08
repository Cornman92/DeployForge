namespace DeployForge.Common.Models.Monitoring;

/// <summary>
/// Alert event record
/// </summary>
public class AlertEvent
{
    /// <summary>
    /// Alert ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Timestamp when alert was triggered
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Alert type
    /// </summary>
    public AlertType Type { get; set; }

    /// <summary>
    /// Alert severity
    /// </summary>
    public AlertSeverity Severity { get; set; }

    /// <summary>
    /// Alert message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Current value that triggered the alert
    /// </summary>
    public double CurrentValue { get; set; }

    /// <summary>
    /// Threshold value that was exceeded
    /// </summary>
    public double ThresholdValue { get; set; }

    /// <summary>
    /// Alert resolved timestamp (null if not resolved)
    /// </summary>
    public DateTime? ResolvedAt { get; set; }

    /// <summary>
    /// Whether alert has been acknowledged
    /// </summary>
    public bool Acknowledged { get; set; }

    /// <summary>
    /// Additional metadata
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Alert type enumeration
/// </summary>
public enum AlertType
{
    CpuUsage,
    MemoryUsage,
    DiskUsage,
    ConcurrentOperations,
    OperationDuration,
    SystemError
}

/// <summary>
/// Alert severity enumeration
/// </summary>
public enum AlertSeverity
{
    Information,
    Warning,
    Error,
    Critical
}
