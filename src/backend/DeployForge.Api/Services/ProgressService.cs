using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.SignalR;

namespace DeployForge.Api.Services;

/// <summary>
/// Progress service implementation using SignalR
/// </summary>
public class ProgressService : IProgressService
{
    private readonly IHubContext<ProgressHub> _hubContext;
    private readonly ILogger<ProgressService> _logger;

    public ProgressService(
        IHubContext<ProgressHub> hubContext,
        ILogger<ProgressService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
    }

    public async Task ReportProgressAsync(string operationId, int percentage, string message, string? stage = null)
    {
        try
        {
            await _hubContext.Clients.Group(operationId).SendAsync("ReceiveProgress", new
            {
                OperationId = operationId,
                Percentage = Math.Clamp(percentage, 0, 100),
                Message = message,
                Stage = stage,
                Timestamp = DateTime.UtcNow
            });

            _logger.LogDebug("Progress reported for operation {OperationId}: {Percentage}% - {Message}",
                operationId, percentage, message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to report progress for operation {OperationId}", operationId);
        }
    }

    public async Task ReportCompletionAsync(string operationId, bool success, string message)
    {
        try
        {
            await _hubContext.Clients.Group(operationId).SendAsync("OperationCompleted", new
            {
                OperationId = operationId,
                Success = success,
                Message = message,
                Timestamp = DateTime.UtcNow
            });

            _logger.LogInformation("Operation {OperationId} completed: Success={Success}, Message={Message}",
                operationId, success, message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to report completion for operation {OperationId}", operationId);
        }
    }

    public async Task ReportErrorAsync(string operationId, string errorMessage)
    {
        try
        {
            await _hubContext.Clients.Group(operationId).SendAsync("OperationError", new
            {
                OperationId = operationId,
                ErrorMessage = errorMessage,
                Timestamp = DateTime.UtcNow
            });

            _logger.LogError("Operation {OperationId} error: {ErrorMessage}", operationId, errorMessage);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to report error for operation {OperationId}", operationId);
        }
    }

    public IProgress<ProgressReport> CreateProgressReporter(string operationId)
    {
        return new Progress<ProgressReport>(async report =>
        {
            await ReportProgressAsync(operationId, report.Percentage, report.Message, report.Stage);
        });
    }
}
