using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Common.Models.Notifications;
using DeployForge.Core.Interfaces;
using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Logging;
using MimeKit;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for sending notifications via email and webhooks
/// </summary>
public class NotificationService : INotificationService
{
    private readonly ILogger<NotificationService> _logger;
    private readonly HttpClient _httpClient;
    private readonly string _settingsPath;
    private readonly List<NotificationHistory> _history = new();
    private NotificationSettings _settings = new();

    public NotificationService(
        ILogger<NotificationService> logger,
        IHttpClientFactory httpClientFactory)
    {
        _logger = logger;
        _httpClient = httpClientFactory.CreateClient();

        // Set settings path
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        var settingsDir = Path.Combine(appData, "DeployForge", "Notifications");
        Directory.CreateDirectory(settingsDir);
        _settingsPath = Path.Combine(settingsDir, "settings.json");

        // Load settings
        LoadSettings();
    }

    public async Task<OperationResult<bool>> SendNotificationAsync(
        NotificationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Sending notification for event {EventType}: {Title}",
                request.EventType, request.Title);

            var channels = request.Channels ?? DetermineChannels(request.EventType);
            var recipients = request.Recipients ?? DetermineRecipients(request.EventType);

            var success = true;
            var errors = new List<string>();

            foreach (var channel in channels)
            {
                switch (channel)
                {
                    case NotificationChannel.Email when _settings.EnableEmail:
                        var emailResult = await SendEmailAsync(
                            request.Title,
                            FormatEmailBody(request),
                            recipients,
                            cancellationToken);

                        if (!emailResult.Success)
                        {
                            success = false;
                            errors.Add(emailResult.ErrorMessage ?? "Email failed");
                        }
                        break;

                    case NotificationChannel.Webhook when _settings.EnableWebhooks:
                        foreach (var webhook in _settings.Webhooks.Where(w =>
                            w.Enabled && w.EventTypes.Contains(request.EventType)))
                        {
                            var webhookResult = await SendWebhookAsync(
                                webhook.Id,
                                request,
                                cancellationToken);

                            if (!webhookResult.Success)
                            {
                                success = false;
                                errors.Add(webhookResult.ErrorMessage ?? "Webhook failed");
                            }
                        }
                        break;

                    case NotificationChannel.Slack when _settings.Slack.Enabled:
                        var slackResult = await SendSlackNotificationAsync(request, cancellationToken);
                        if (!slackResult.Success)
                        {
                            success = false;
                            errors.Add(slackResult.ErrorMessage ?? "Slack failed");
                        }
                        break;

                    case NotificationChannel.Teams when _settings.Teams.Enabled:
                        var teamsResult = await SendTeamsNotificationAsync(request, cancellationToken);
                        if (!teamsResult.Success)
                        {
                            success = false;
                            errors.Add(teamsResult.ErrorMessage ?? "Teams failed");
                        }
                        break;
                }
            }

            return success
                ? OperationResult<bool>.SuccessResult(true)
                : OperationResult<bool>.FailureResult(string.Join("; ", errors));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send notification");
            return OperationResult<bool>.FailureResult($"Failed to send notification: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> SendEmailAsync(
        string subject,
        string body,
        List<string> recipients,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_settings.EnableEmail || string.IsNullOrEmpty(_settings.Email.SmtpHost))
            {
                _logger.LogWarning("Email not configured");
                return OperationResult<bool>.FailureResult("Email not configured");
            }

            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(_settings.Email.FromName, _settings.Email.FromEmail));

            foreach (var recipient in recipients)
            {
                message.To.Add(MailboxAddress.Parse(recipient));
            }

            message.Subject = subject;
            message.Body = new TextPart("html") { Text = body };

            using var client = new SmtpClient();

            await client.ConnectAsync(
                _settings.Email.SmtpHost,
                _settings.Email.SmtpPort,
                _settings.Email.UseSsl ? SecureSocketOptions.StartTls : SecureSocketOptions.None,
                cancellationToken);

            if (!string.IsNullOrEmpty(_settings.Email.Username))
            {
                await client.AuthenticateAsync(
                    _settings.Email.Username,
                    _settings.Email.Password,
                    cancellationToken);
            }

            await client.SendAsync(message, cancellationToken);
            await client.DisconnectAsync(true, cancellationToken);

            _logger.LogInformation("Email sent successfully to {Recipients}", string.Join(", ", recipients));

            // Record history
            foreach (var recipient in recipients)
            {
                _history.Add(new NotificationHistory
                {
                    EventType = NotificationEventType.OperationCompleted,
                    Title = subject,
                    Message = body,
                    Channel = NotificationChannel.Email,
                    Success = true,
                    Recipient = recipient
                });
            }

            return OperationResult<bool>.SuccessResult(true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email");

            // Record failure
            foreach (var recipient in recipients)
            {
                _history.Add(new NotificationHistory
                {
                    EventType = NotificationEventType.OperationCompleted,
                    Title = subject,
                    Message = body,
                    Channel = NotificationChannel.Email,
                    Success = false,
                    ErrorMessage = ex.Message,
                    Recipient = recipient
                });
            }

            return OperationResult<bool>.FailureResult($"Failed to send email: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> SendWebhookAsync(
        string webhookId,
        object payload,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var webhook = _settings.Webhooks.FirstOrDefault(w => w.Id == webhookId);
            if (webhook == null)
            {
                return OperationResult<bool>.FailureResult("Webhook not found");
            }

            if (!webhook.Enabled)
            {
                return OperationResult<bool>.FailureResult("Webhook is disabled");
            }

            var request = new HttpRequestMessage(HttpMethod.Post, webhook.Url);

            // Add custom headers
            foreach (var header in webhook.Headers)
            {
                request.Headers.Add(header.Key, header.Value);
            }

            // Add signature if secret is configured
            if (!string.IsNullOrEmpty(webhook.Secret))
            {
                var payloadJson = JsonSerializer.Serialize(payload);
                var signature = ComputeSignature(payloadJson, webhook.Secret);
                request.Headers.Add("X-DeployForge-Signature", signature);
            }

            request.Content = JsonContent.Create(payload);

            var response = await _httpClient.SendAsync(request, cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Webhook {WebhookId} called successfully", webhookId);

                _history.Add(new NotificationHistory
                {
                    Title = "Webhook",
                    Message = $"Webhook {webhook.Name} called",
                    Channel = NotificationChannel.Webhook,
                    Success = true,
                    Recipient = webhook.Url
                });

                return OperationResult<bool>.SuccessResult(true);
            }
            else
            {
                var error = $"Webhook returned {response.StatusCode}";
                _logger.LogWarning("Webhook {WebhookId} failed: {Error}", webhookId, error);

                _history.Add(new NotificationHistory
                {
                    Title = "Webhook",
                    Message = $"Webhook {webhook.Name} called",
                    Channel = NotificationChannel.Webhook,
                    Success = false,
                    ErrorMessage = error,
                    Recipient = webhook.Url
                });

                return OperationResult<bool>.FailureResult(error);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send webhook {WebhookId}", webhookId);
            return OperationResult<bool>.FailureResult($"Failed to send webhook: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> SendTestNotificationAsync(
        NotificationChannel channel,
        string? recipient = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            switch (channel)
            {
                case NotificationChannel.Email:
                    var recipients = recipient != null
                        ? new List<string> { recipient }
                        : _settings.Email.DefaultRecipients;

                    return await SendEmailAsync(
                        "DeployForge Test Notification",
                        "<h1>Test Email</h1><p>This is a test notification from DeployForge.</p>",
                        recipients,
                        cancellationToken);

                case NotificationChannel.Webhook:
                    if (string.IsNullOrEmpty(recipient))
                    {
                        return OperationResult<bool>.FailureResult("Webhook ID required");
                    }

                    return await SendWebhookAsync(
                        recipient,
                        new { type = "test", message = "Test webhook notification" },
                        cancellationToken);

                default:
                    return OperationResult<bool>.FailureResult("Unsupported channel");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send test notification");
            return OperationResult<bool>.FailureResult($"Failed to send test notification: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> ConfigureSettingsAsync(
        NotificationSettings settings,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _settings = settings;
            await SaveSettingsAsync();
            _logger.LogInformation("Notification settings updated");
            return OperationResult<bool>.SuccessResult(true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to configure notification settings");
            return OperationResult<bool>.FailureResult($"Failed to configure settings: {ex.Message}");
        }
    }

    public Task<OperationResult<NotificationSettings>> GetSettingsAsync(
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(OperationResult<NotificationSettings>.SuccessResult(_settings));
    }

    public async Task<OperationResult<string>> RegisterWebhookAsync(
        WebhookEndpoint webhook,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _settings.Webhooks.Add(webhook);
            await SaveSettingsAsync();
            _logger.LogInformation("Webhook {WebhookId} registered", webhook.Id);
            return OperationResult<string>.SuccessResult(webhook.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to register webhook");
            return OperationResult<string>.FailureResult($"Failed to register webhook: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> UnregisterWebhookAsync(
        string webhookId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var webhook = _settings.Webhooks.FirstOrDefault(w => w.Id == webhookId);
            if (webhook == null)
            {
                return OperationResult<bool>.FailureResult("Webhook not found");
            }

            _settings.Webhooks.Remove(webhook);
            await SaveSettingsAsync();
            _logger.LogInformation("Webhook {WebhookId} unregistered", webhookId);
            return OperationResult<bool>.SuccessResult(true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to unregister webhook");
            return OperationResult<bool>.FailureResult($"Failed to unregister webhook: {ex.Message}");
        }
    }

    public Task<OperationResult<List<NotificationHistory>>> GetHistoryAsync(
        DateTime? startDate = null,
        DateTime? endDate = null,
        NotificationEventType? eventType = null,
        CancellationToken cancellationToken = default)
    {
        var query = _history.AsEnumerable();

        if (startDate.HasValue)
            query = query.Where(h => h.Timestamp >= startDate.Value);

        if (endDate.HasValue)
            query = query.Where(h => h.Timestamp <= endDate.Value);

        if (eventType.HasValue)
            query = query.Where(h => h.EventType == eventType.Value);

        var result = query.OrderByDescending(h => h.Timestamp).ToList();
        return Task.FromResult(OperationResult<List<NotificationHistory>>.SuccessResult(result));
    }

    private async Task<OperationResult<bool>> SendSlackNotificationAsync(
        NotificationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_settings.Slack.Enabled || string.IsNullOrEmpty(_settings.Slack.WebhookUrl))
            {
                return OperationResult<bool>.FailureResult("Slack not configured");
            }

            var color = request.Severity switch
            {
                NotificationSeverity.Success => "good",
                NotificationSeverity.Warning => "warning",
                NotificationSeverity.Error => "danger",
                NotificationSeverity.Critical => "danger",
                _ => "#17a2b8"
            };

            var payload = new
            {
                channel = _settings.Slack.DefaultChannel,
                username = _settings.Slack.BotUsername,
                icon_emoji = _settings.Slack.IconEmoji,
                attachments = new[]
                {
                    new
                    {
                        color,
                        title = request.Title,
                        text = request.Message,
                        fields = request.Data.Select(kvp => new
                        {
                            title = kvp.Key,
                            value = kvp.Value?.ToString() ?? "",
                            @short = true
                        }).ToArray(),
                        footer = "DeployForge",
                        ts = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
                    }
                }
            };

            var content = JsonContent.Create(payload);
            var response = await _httpClient.PostAsync(_settings.Slack.WebhookUrl, content, cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Slack notification sent successfully");

                _history.Add(new NotificationHistory
                {
                    EventType = request.EventType,
                    Title = request.Title,
                    Message = request.Message,
                    Channel = NotificationChannel.Slack,
                    Success = true,
                    Recipient = _settings.Slack.DefaultChannel
                });

                return OperationResult<bool>.SuccessResult(true);
            }
            else
            {
                var error = $"Slack returned {response.StatusCode}";
                _logger.LogWarning("Slack notification failed: {Error}", error);
                return OperationResult<bool>.FailureResult(error);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send Slack notification");
            return OperationResult<bool>.FailureResult($"Failed to send Slack notification: {ex.Message}");
        }
    }

    private async Task<OperationResult<bool>> SendTeamsNotificationAsync(
        NotificationRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_settings.Teams.Enabled || string.IsNullOrEmpty(_settings.Teams.WebhookUrl))
            {
                return OperationResult<bool>.FailureResult("Teams not configured");
            }

            var payload = new
            {
                type = "message",
                attachments = new[]
                {
                    new
                    {
                        contentType = "application/vnd.microsoft.card.adaptive",
                        contentUrl = (string?)null,
                        content = new
                        {
                            type = "AdaptiveCard",
                            body = new object[]
                            {
                                new
                                {
                                    type = "TextBlock",
                                    size = "Large",
                                    weight = "Bolder",
                                    text = request.Title
                                },
                                new
                                {
                                    type = "TextBlock",
                                    text = request.Message,
                                    wrap = true
                                },
                                new
                                {
                                    type = "FactSet",
                                    facts = request.Data.Select(kvp => new
                                    {
                                        title = kvp.Key,
                                        value = kvp.Value?.ToString() ?? ""
                                    }).ToArray()
                                }
                            },
                            actions = new object[0],
                            version = "1.4"
                        }
                    }
                }
            };

            var content = JsonContent.Create(payload);
            var response = await _httpClient.PostAsync(_settings.Teams.WebhookUrl, content, cancellationToken);

            if (response.IsSuccessStatusCode)
            {
                _logger.LogInformation("Teams notification sent successfully");

                _history.Add(new NotificationHistory
                {
                    EventType = request.EventType,
                    Title = request.Title,
                    Message = request.Message,
                    Channel = NotificationChannel.Teams,
                    Success = true,
                    Recipient = "Teams Channel"
                });

                return OperationResult<bool>.SuccessResult(true);
            }
            else
            {
                var error = $"Teams returned {response.StatusCode}";
                _logger.LogWarning("Teams notification failed: {Error}", error);
                return OperationResult<bool>.FailureResult(error);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send Teams notification");
            return OperationResult<bool>.FailureResult($"Failed to send Teams notification: {ex.Message}");
        }
    }

    #region Private Methods

    private List<NotificationChannel> DetermineChannels(NotificationEventType eventType)
    {
        var rule = _settings.Rules.FirstOrDefault(r => r.Enabled && r.EventType == eventType);
        return rule?.Channels ?? new List<NotificationChannel>();
    }

    private List<string> DetermineRecipients(NotificationEventType eventType)
    {
        var rule = _settings.Rules.FirstOrDefault(r => r.Enabled && r.EventType == eventType);
        return rule?.Recipients ?? _settings.Email.DefaultRecipients;
    }

    private string FormatEmailBody(NotificationRequest request)
    {
        var severityColor = request.Severity switch
        {
            NotificationSeverity.Success => "#28a745",
            NotificationSeverity.Warning => "#ffc107",
            NotificationSeverity.Error => "#dc3545",
            NotificationSeverity.Critical => "#c82333",
            _ => "#17a2b8"
        };

        var html = new StringBuilder();
        html.AppendLine("<html><body style='font-family: Arial, sans-serif;'>");
        html.AppendLine($"<div style='max-width: 600px; margin: 0 auto; padding: 20px;'>");
        html.AppendLine($"<h2 style='color: {severityColor};'>{request.Title}</h2>");
        html.AppendLine($"<p>{request.Message}</p>");

        if (request.Data.Any())
        {
            html.AppendLine("<h3>Details:</h3>");
            html.AppendLine("<table style='border-collapse: collapse; width: 100%;'>");
            foreach (var kvp in request.Data)
            {
                html.AppendLine($"<tr><th style='text-align: left; padding: 8px; border: 1px solid #ddd;'>{kvp.Key}</th>");
                html.AppendLine($"<td style='padding: 8px; border: 1px solid #ddd;'>{kvp.Value}</td></tr>");
            }
            html.AppendLine("</table>");
        }

        html.AppendLine($"<p style='margin-top: 30px; font-size: 12px; color: #666;'>Sent by DeployForge at {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC</p>");
        html.AppendLine("</div></body></html>");

        return html.ToString();
    }

    private string ComputeSignature(string payload, string secret)
    {
        using var hmac = new System.Security.Cryptography.HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(payload));
        return Convert.ToBase64String(hash);
    }

    private void LoadSettings()
    {
        try
        {
            if (File.Exists(_settingsPath))
            {
                var json = File.ReadAllText(_settingsPath);
                _settings = JsonSerializer.Deserialize<NotificationSettings>(json) ?? new NotificationSettings();
                _logger.LogInformation("Notification settings loaded");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load notification settings");
        }
    }

    private async Task SaveSettingsAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_settings, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_settingsPath, json);
            _logger.LogInformation("Notification settings saved");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save notification settings");
        }
    }

    #endregion
}
