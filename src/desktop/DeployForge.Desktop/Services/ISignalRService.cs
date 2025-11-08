namespace DeployForge.Desktop.Services;

/// <summary>
/// SignalR service for real-time updates
/// </summary>
public interface ISignalRService
{
    /// <summary>
    /// Connect to SignalR hub
    /// </summary>
    Task ConnectAsync();

    /// <summary>
    /// Disconnect from SignalR hub
    /// </summary>
    Task DisconnectAsync();

    /// <summary>
    /// Join operation group to receive progress updates
    /// </summary>
    Task JoinOperationGroupAsync(string operationId);

    /// <summary>
    /// Leave operation group
    /// </summary>
    Task LeaveOperationGroupAsync(string operationId);

    /// <summary>
    /// Subscribe to progress updates
    /// </summary>
    void OnProgressUpdate(Action<ProgressUpdate> handler);

    /// <summary>
    /// Subscribe to operation completed events
    /// </summary>
    void OnOperationCompleted(Action<OperationCompleted> handler);

    /// <summary>
    /// Subscribe to operation error events
    /// </summary>
    void OnOperationError(Action<OperationError> handler);

    /// <summary>
    /// Subscribe to monitoring metrics updates
    /// </summary>
    Task SubscribeToMonitoringAsync();

    /// <summary>
    /// Unsubscribe from monitoring metrics updates
    /// </summary>
    Task UnsubscribeFromMonitoringAsync();

    /// <summary>
    /// Subscribe to alert notifications
    /// </summary>
    Task SubscribeToAlertsAsync();

    /// <summary>
    /// Unsubscribe from alert notifications
    /// </summary>
    Task UnsubscribeFromAlertsAsync();

    /// <summary>
    /// Subscribe to monitoring metrics events
    /// </summary>
    void OnMetricsUpdate(Action<MetricsUpdate> handler);

    /// <summary>
    /// Subscribe to alert events
    /// </summary>
    void OnAlertReceived(Action<AlertReceived> handler);

    /// <summary>
    /// Is connected
    /// </summary>
    bool IsConnected { get; }
}

public class ProgressUpdate
{
    public string OperationId { get; set; } = string.Empty;
    public int Percentage { get; set; }
    public string Message { get; set; } = string.Empty;
    public string? Stage { get; set; }
    public DateTime Timestamp { get; set; }
}

public class OperationCompleted
{
    public string OperationId { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
}

public class OperationError
{
    public string OperationId { get; set; } = string.Empty;
    public string ErrorMessage { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
}

public class MetricsUpdate
{
    public DateTime Timestamp { get; set; }
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
    public long TotalMemoryBytes { get; set; }
    public long AvailableMemoryBytes { get; set; }
    public double DiskUsage { get; set; }
    public long TotalDiskSpaceBytes { get; set; }
    public int ActiveOperations { get; set; }
    public TimeSpan Uptime { get; set; }
}

public class AlertReceived
{
    public DateTime Timestamp { get; set; }
    public string MetricType { get; set; } = string.Empty;
    public double Value { get; set; }
    public double Threshold { get; set; }
    public string Message { get; set; } = string.Empty;
}
