using Microsoft.AspNetCore.SignalR.Client;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.Services;

/// <summary>
/// SignalR service implementation
/// </summary>
public class SignalRService : ISignalRService
{
    private readonly ILogger<SignalRService> _logger;
    private HubConnection? _connection;
    private readonly List<Action<ProgressUpdate>> _progressHandlers = new();
    private readonly List<Action<OperationCompleted>> _completedHandlers = new();
    private readonly List<Action<OperationError>> _errorHandlers = new();
    private readonly List<Action<MetricsUpdate>> _metricsHandlers = new();
    private readonly List<Action<AlertReceived>> _alertHandlers = new();

    public bool IsConnected => _connection?.State == HubConnectionState.Connected;

    public SignalRService(ILogger<SignalRService> logger)
    {
        _logger = logger;
    }

    public async Task ConnectAsync()
    {
        if (_connection != null && IsConnected)
        {
            _logger.LogWarning("Already connected to SignalR hub");
            return;
        }

        try
        {
            _connection = new HubConnectionBuilder()
                .WithUrl("http://localhost:5000/hubs/progress")
                .WithAutomaticReconnect()
                .Build();

            // Register handlers
            _connection.On<object>("ReceiveProgress", HandleProgressUpdate);
            _connection.On<object>("OperationCompleted", HandleOperationCompleted);
            _connection.On<object>("OperationError", HandleOperationError);
            _connection.On<object>("ReceiveMetrics", HandleMetricsUpdate);
            _connection.On<object>("ReceiveAlert", HandleAlertReceived);

            _connection.Closed += async (error) =>
            {
                if (error != null)
                {
                    _logger.LogError(error, "SignalR connection closed with error");
                }
                else
                {
                    _logger.LogInformation("SignalR connection closed");
                }
                await Task.Delay(TimeSpan.FromSeconds(5));
            };

            _connection.Reconnecting += (error) =>
            {
                _logger.LogWarning(error, "SignalR reconnecting...");
                return Task.CompletedTask;
            };

            _connection.Reconnected += (connectionId) =>
            {
                _logger.LogInformation("SignalR reconnected: {ConnectionId}", connectionId);
                return Task.CompletedTask;
            };

            await _connection.StartAsync();
            _logger.LogInformation("Connected to SignalR hub");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to connect to SignalR hub");
            throw;
        }
    }

    public async Task DisconnectAsync()
    {
        if (_connection != null)
        {
            try
            {
                await _connection.StopAsync();
                await _connection.DisposeAsync();
                _connection = null;
                _logger.LogInformation("Disconnected from SignalR hub");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error disconnecting from SignalR hub");
            }
        }
    }

    public async Task JoinOperationGroupAsync(string operationId)
    {
        if (_connection == null || !IsConnected)
        {
            throw new InvalidOperationException("Not connected to SignalR hub");
        }

        await _connection.InvokeAsync("JoinOperationGroup", operationId);
        _logger.LogInformation("Joined operation group: {OperationId}", operationId);
    }

    public async Task LeaveOperationGroupAsync(string operationId)
    {
        if (_connection == null || !IsConnected)
        {
            return;
        }

        await _connection.InvokeAsync("LeaveOperationGroup", operationId);
        _logger.LogInformation("Left operation group: {OperationId}", operationId);
    }

    public void OnProgressUpdate(Action<ProgressUpdate> handler)
    {
        _progressHandlers.Add(handler);
    }

    public void OnOperationCompleted(Action<OperationCompleted> handler)
    {
        _completedHandlers.Add(handler);
    }

    public void OnOperationError(Action<OperationError> handler)
    {
        _errorHandlers.Add(handler);
    }

    public async Task SubscribeToMonitoringAsync()
    {
        if (_connection == null || !IsConnected)
        {
            throw new InvalidOperationException("Not connected to SignalR hub");
        }

        await _connection.InvokeAsync("SubscribeToMonitoring");
        _logger.LogInformation("Subscribed to monitoring updates");
    }

    public async Task UnsubscribeFromMonitoringAsync()
    {
        if (_connection == null || !IsConnected)
        {
            return;
        }

        await _connection.InvokeAsync("UnsubscribeFromMonitoring");
        _logger.LogInformation("Unsubscribed from monitoring updates");
    }

    public async Task SubscribeToAlertsAsync()
    {
        if (_connection == null || !IsConnected)
        {
            throw new InvalidOperationException("Not connected to SignalR hub");
        }

        await _connection.InvokeAsync("SubscribeToAlerts");
        _logger.LogInformation("Subscribed to alerts");
    }

    public async Task UnsubscribeFromAlertsAsync()
    {
        if (_connection == null || !IsConnected)
        {
            return;
        }

        await _connection.InvokeAsync("UnsubscribeFromAlerts");
        _logger.LogInformation("Unsubscribed from alerts");
    }

    public void OnMetricsUpdate(Action<MetricsUpdate> handler)
    {
        _metricsHandlers.Add(handler);
    }

    public void OnAlertReceived(Action<AlertReceived> handler)
    {
        _alertHandlers.Add(handler);
    }

    private void HandleProgressUpdate(object data)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(data);
            var update = System.Text.Json.JsonSerializer.Deserialize<ProgressUpdate>(json);

            if (update != null)
            {
                foreach (var handler in _progressHandlers)
                {
                    handler(update);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling progress update");
        }
    }

    private void HandleOperationCompleted(object data)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(data);
            var completed = System.Text.Json.JsonSerializer.Deserialize<OperationCompleted>(json);

            if (completed != null)
            {
                foreach (var handler in _completedHandlers)
                {
                    handler(completed);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling operation completed");
        }
    }

    private void HandleOperationError(object data)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(data);
            var error = System.Text.Json.JsonSerializer.Deserialize<OperationError>(json);

            if (error != null)
            {
                foreach (var handler in _errorHandlers)
                {
                    handler(error);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling operation error");
        }
    }

    private void HandleMetricsUpdate(object data)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(data);
            var metrics = System.Text.Json.JsonSerializer.Deserialize<MetricsUpdate>(json);

            if (metrics != null)
            {
                foreach (var handler in _metricsHandlers)
                {
                    handler(metrics);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling metrics update");
        }
    }

    private void HandleAlertReceived(object data)
    {
        try
        {
            var json = System.Text.Json.JsonSerializer.Serialize(data);
            var alert = System.Text.Json.JsonSerializer.Deserialize<AlertReceived>(json);

            if (alert != null)
            {
                foreach (var handler in _alertHandlers)
                {
                    handler(alert);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error handling alert");
        }
    }
}
