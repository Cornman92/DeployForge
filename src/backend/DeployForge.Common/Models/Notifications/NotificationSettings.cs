namespace DeployForge.Common.Models.Notifications;

/// <summary>
/// Notification settings configuration
/// </summary>
public class NotificationSettings
{
    /// <summary>
    /// Enable email notifications
    /// </summary>
    public bool EnableEmail { get; set; }

    /// <summary>
    /// Enable webhook notifications
    /// </summary>
    public bool EnableWebhooks { get; set; }

    /// <summary>
    /// Email configuration
    /// </summary>
    public EmailSettings Email { get; set; } = new();

    /// <summary>
    /// Registered webhooks
    /// </summary>
    public List<WebhookEndpoint> Webhooks { get; set; } = new();

    /// <summary>
    /// Slack configuration
    /// </summary>
    public SlackSettings Slack { get; set; } = new();

    /// <summary>
    /// Microsoft Teams configuration
    /// </summary>
    public TeamsSettings Teams { get; set; } = new();

    /// <summary>
    /// Notification rules
    /// </summary>
    public List<NotificationRule> Rules { get; set; } = new();
}

/// <summary>
/// Slack settings
/// </summary>
public class SlackSettings
{
    /// <summary>
    /// Enable Slack notifications
    /// </summary>
    public bool Enabled { get; set; }

    /// <summary>
    /// Slack webhook URL
    /// </summary>
    public string WebhookUrl { get; set; } = string.Empty;

    /// <summary>
    /// Default channel
    /// </summary>
    public string DefaultChannel { get; set; } = "#general";

    /// <summary>
    /// Bot username
    /// </summary>
    public string BotUsername { get; set; } = "DeployForge";

    /// <summary>
    /// Bot icon emoji
    /// </summary>
    public string IconEmoji { get; set; } = ":robot_face:";
}

/// <summary>
/// Microsoft Teams settings
/// </summary>
public class TeamsSettings
{
    /// <summary>
    /// Enable Teams notifications
    /// </summary>
    public bool Enabled { get; set; }

    /// <summary>
    /// Teams webhook URL
    /// </summary>
    public string WebhookUrl { get; set; } = string.Empty;

    /// <summary>
    /// Theme color (hex)
    /// </summary>
    public string ThemeColor { get; set; } = "0076D7";
}

/// <summary>
/// Email settings
/// </summary>
public class EmailSettings
{
    /// <summary>
    /// SMTP server host
    /// </summary>
    public string SmtpHost { get; set; } = string.Empty;

    /// <summary>
    /// SMTP server port
    /// </summary>
    public int SmtpPort { get; set; } = 587;

    /// <summary>
    /// Enable SSL/TLS
    /// </summary>
    public bool UseSsl { get; set; } = true;

    /// <summary>
    /// SMTP username
    /// </summary>
    public string Username { get; set; } = string.Empty;

    /// <summary>
    /// SMTP password
    /// </summary>
    public string Password { get; set; } = string.Empty;

    /// <summary>
    /// From email address
    /// </summary>
    public string FromEmail { get; set; } = string.Empty;

    /// <summary>
    /// From display name
    /// </summary>
    public string FromName { get; set; } = "DeployForge";

    /// <summary>
    /// Default recipients
    /// </summary>
    public List<string> DefaultRecipients { get; set; } = new();
}

/// <summary>
/// Webhook endpoint
/// </summary>
public class WebhookEndpoint
{
    /// <summary>
    /// Webhook ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Webhook URL
    /// </summary>
    public string Url { get; set; } = string.Empty;

    /// <summary>
    /// Webhook name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Enabled flag
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Event types to trigger on
    /// </summary>
    public List<NotificationEventType> EventTypes { get; set; } = new();

    /// <summary>
    /// Custom headers
    /// </summary>
    public Dictionary<string, string> Headers { get; set; } = new();

    /// <summary>
    /// Secret for signature verification
    /// </summary>
    public string? Secret { get; set; }

    /// <summary>
    /// Previous secret (for rotation grace period)
    /// </summary>
    public string? PreviousSecret { get; set; }

    /// <summary>
    /// When the secret was created (UTC)
    /// </summary>
    public DateTime? SecretCreatedAt { get; set; }

    /// <summary>
    /// When the secret was last rotated (UTC)
    /// </summary>
    public DateTime? SecretRotatedAt { get; set; }

    /// <summary>
    /// Secret rotation interval in days (0 = no auto-rotation)
    /// </summary>
    public int SecretRotationDays { get; set; } = 90;
}

/// <summary>
/// Notification rule
/// </summary>
public class NotificationRule
{
    /// <summary>
    /// Rule ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Rule name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Enabled flag
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Event type to trigger on
    /// </summary>
    public NotificationEventType EventType { get; set; }

    /// <summary>
    /// Notification channels
    /// </summary>
    public List<NotificationChannel> Channels { get; set; } = new();

    /// <summary>
    /// Recipients (for email)
    /// </summary>
    public List<string> Recipients { get; set; } = new();
}

/// <summary>
/// Notification event type
/// </summary>
public enum NotificationEventType
{
    OperationCompleted,
    OperationFailed,
    ValidationCompleted,
    ValidationFailed,
    BatchOperationCompleted,
    BatchOperationFailed,
    HealthAlert,
    PerformanceAlert,
    SystemError
}

/// <summary>
/// Notification channel
/// </summary>
public enum NotificationChannel
{
    Email,
    Webhook,
    Slack,
    Teams
}
