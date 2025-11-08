using DeployForge.Common.Models.Notifications;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for notification management
/// </summary>
[ApiController]
[Route("api/[controller]")]
[EnableRateLimiting("notifications")]
public class NotificationsController : ControllerBase
{
    private readonly INotificationService _notificationService;
    private readonly ILogger<NotificationsController> _logger;

    public NotificationsController(
        INotificationService notificationService,
        ILogger<NotificationsController> logger)
    {
        _notificationService = notificationService;
        _logger = logger;
    }

    /// <summary>
    /// Send notification
    /// </summary>
    [HttpPost]
    public async Task<IActionResult> SendNotification(
        [FromBody] NotificationRequest request,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.SendNotificationAsync(request, cancellationToken);

        if (!result.Success)
            return BadRequest(result.ErrorMessage);

        return Ok(new { Message = "Notification sent successfully" });
    }

    /// <summary>
    /// Send email notification
    /// </summary>
    [HttpPost("email")]
    public async Task<IActionResult> SendEmail(
        [FromBody] EmailRequest request,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.SendEmailAsync(
            request.Subject,
            request.Body,
            request.Recipients,
            cancellationToken);

        if (!result.Success)
            return BadRequest(result.ErrorMessage);

        return Ok(new { Message = "Email sent successfully" });
    }

    /// <summary>
    /// Send test notification
    /// </summary>
    [HttpPost("test")]
    public async Task<IActionResult> SendTestNotification(
        [FromQuery] NotificationChannel channel,
        [FromQuery] string? recipient = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.SendTestNotificationAsync(
            channel,
            recipient,
            cancellationToken);

        if (!result.Success)
            return BadRequest(result.ErrorMessage);

        return Ok(new { Message = "Test notification sent successfully" });
    }

    /// <summary>
    /// Configure notification settings
    /// </summary>
    [HttpPost("configure")]
    public async Task<IActionResult> ConfigureSettings(
        [FromBody] NotificationSettings settings,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.ConfigureSettingsAsync(settings, cancellationToken);

        if (!result.Success)
            return BadRequest(result.ErrorMessage);

        return Ok(new { Message = "Notification settings configured successfully" });
    }

    /// <summary>
    /// Get notification settings
    /// </summary>
    [HttpGet("settings")]
    public async Task<ActionResult<NotificationSettings>> GetSettings(
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.GetSettingsAsync(cancellationToken);

        if (!result.Success || result.Data == null)
            return NotFound(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Register webhook
    /// </summary>
    [HttpPost("webhook")]
    public async Task<ActionResult<string>> RegisterWebhook(
        [FromBody] WebhookEndpoint webhook,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.RegisterWebhookAsync(webhook, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(new { WebhookId = result.Data, Message = "Webhook registered successfully" });
    }

    /// <summary>
    /// Unregister webhook
    /// </summary>
    [HttpDelete("webhook/{webhookId}")]
    public async Task<IActionResult> UnregisterWebhook(
        string webhookId,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.UnregisterWebhookAsync(webhookId, cancellationToken);

        if (!result.Success)
            return NotFound(result.ErrorMessage);

        return Ok(new { Message = "Webhook unregistered successfully" });
    }

    /// <summary>
    /// Get notification history
    /// </summary>
    [HttpGet("history")]
    public async Task<ActionResult<List<NotificationHistory>>> GetHistory(
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null,
        [FromQuery] NotificationEventType? eventType = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _notificationService.GetHistoryAsync(
            startDate,
            endDate,
            eventType,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }
}

/// <summary>
/// Email request
/// </summary>
public class EmailRequest
{
    public string Subject { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public List<string> Recipients { get; set; } = new();
}
