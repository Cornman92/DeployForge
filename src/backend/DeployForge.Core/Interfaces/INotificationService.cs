using DeployForge.Common.Models;
using DeployForge.Common.Models.Notifications;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for sending notifications via email and webhooks
/// </summary>
public interface INotificationService
{
    /// <summary>
    /// Send notification
    /// </summary>
    Task<OperationResult<bool>> SendNotificationAsync(
        NotificationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Send email notification
    /// </summary>
    Task<OperationResult<bool>> SendEmailAsync(
        string subject,
        string body,
        List<string> recipients,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Send webhook notification
    /// </summary>
    Task<OperationResult<bool>> SendWebhookAsync(
        string webhookId,
        object payload,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Send test notification
    /// </summary>
    Task<OperationResult<bool>> SendTestNotificationAsync(
        NotificationChannel channel,
        string? recipient = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Configure notification settings
    /// </summary>
    Task<OperationResult<bool>> ConfigureSettingsAsync(
        NotificationSettings settings,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get notification settings
    /// </summary>
    Task<OperationResult<NotificationSettings>> GetSettingsAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Register webhook
    /// </summary>
    Task<OperationResult<string>> RegisterWebhookAsync(
        WebhookEndpoint webhook,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Unregister webhook
    /// </summary>
    Task<OperationResult<bool>> UnregisterWebhookAsync(
        string webhookId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get notification history
    /// </summary>
    Task<OperationResult<List<NotificationHistory>>> GetHistoryAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        NotificationEventType? eventType = null,
        CancellationToken cancellationToken = default);
}
