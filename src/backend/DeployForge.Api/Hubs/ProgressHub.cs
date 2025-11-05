using Microsoft.AspNetCore.SignalR;

namespace DeployForge.Api;

/// <summary>
/// SignalR hub for real-time progress updates
/// </summary>
public class ProgressHub : Hub
{
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
    /// Join a progress group for specific operation
    /// </summary>
    public async Task JoinOperationGroup(string operationId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, operationId);
    }

    /// <summary>
    /// Leave a progress group
    /// </summary>
    public async Task LeaveOperationGroup(string operationId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, operationId);
    }

    public override async Task OnConnectedAsync()
    {
        await base.OnConnectedAsync();
        Console.WriteLine($"Client connected: {Context.ConnectionId}");
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        await base.OnDisconnectedAsync(exception);
        Console.WriteLine($"Client disconnected: {Context.ConnectionId}");
    }
}
