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
