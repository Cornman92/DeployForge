using Microsoft.AspNetCore.SignalR;

namespace DeployForge.Api;

/// <summary>
/// SignalR hub for real-time progress updates
/// </summary>
public class ProgressHub : Hub
{
    private readonly ILogger<ProgressHub> _logger;

    public ProgressHub(ILogger<ProgressHub> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Send progress update to all connected clients
    /// </summary>
    public async Task SendProgress(string operationId, int percentage, string message)
    {
        await Clients.All.SendAsync("ReceiveProgress", operationId, percentage, message);
    }

    /// <summary>
    /// Send progress update to specific client
    /// </summary>
    public async Task SendProgressToClient(string connectionId, string operationId, int percentage, string message)
    {
        await Clients.Client(connectionId).SendAsync("ReceiveProgress", operationId, percentage, message);
    }

    /// <summary>
    /// Send progress update to operation group
    /// </summary>
    public async Task SendProgressToGroup(string operationId, int percentage, string message, string? stage = null)
    {
        await Clients.Group(operationId).SendAsync("ReceiveProgress", new
        {
            OperationId = operationId,
            Percentage = percentage,
            Message = message,
            Stage = stage,
            Timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Send operation completed notification
    /// </summary>
    public async Task SendOperationCompleted(string operationId, bool success, string message)
    {
        await Clients.Group(operationId).SendAsync("OperationCompleted", new
        {
            OperationId = operationId,
            Success = success,
            Message = message,
            Timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Send operation error notification
    /// </summary>
    public async Task SendOperationError(string operationId, string errorMessage)
    {
        await Clients.Group(operationId).SendAsync("OperationError", new
        {
            OperationId = operationId,
            ErrorMessage = errorMessage,
            Timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Join a progress group for specific operation
    /// </summary>
    public async Task JoinOperationGroup(string operationId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, operationId);
        _logger.LogInformation("Client {ConnectionId} joined operation group {OperationId}",
            Context.ConnectionId, operationId);
    }

    /// <summary>
    /// Leave a progress group
    /// </summary>
    public async Task LeaveOperationGroup(string operationId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, operationId);
        _logger.LogInformation("Client {ConnectionId} left operation group {OperationId}",
            Context.ConnectionId, operationId);
    }

    public override async Task OnConnectedAsync()
    {
        await base.OnConnectedAsync();
        _logger.LogInformation("SignalR client connected: {ConnectionId}", Context.ConnectionId);
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        await base.OnDisconnectedAsync(exception);
        if (exception != null)
        {
            _logger.LogWarning(exception, "SignalR client disconnected with error: {ConnectionId}",
                Context.ConnectionId);
        }
        else
        {
            _logger.LogInformation("SignalR client disconnected: {ConnectionId}", Context.ConnectionId);
        }
    }
}
