namespace DeployForge.Common.Models.Notifications;

/// <summary>
/// Notification request
/// </summary>
public class NotificationRequest
{
    /// <summary>
    /// Event type
    /// </summary>
    public NotificationEventType EventType { get; set; }

    /// <summary>
    /// Notification title
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Notification message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Severity level
    /// </summary>
    public NotificationSeverity Severity { get; set; } = NotificationSeverity.Information;

    /// <summary>
    /// Additional data
    /// </summary>
    public Dictionary<string, object> Data { get; set; } = new();

    /// <summary>
    /// Specific recipients (overrides rules)
    /// </summary>
    public List<string>? Recipients { get; set; }

    /// <summary>
    /// Specific channels (overrides rules)
    /// </summary>
    public List<NotificationChannel>? Channels { get; set; }
}

/// <summary>
/// Notification severity
/// </summary>
public enum NotificationSeverity
{
    Information,
    Success,
    Warning,
    Error,
    Critical
}

/// <summary>
/// Notification history entry
/// </summary>
public class NotificationHistory
{
    /// <summary>
    /// Notification ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Timestamp
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Event type
    /// </summary>
    public NotificationEventType EventType { get; set; }

    /// <summary>
    /// Title
    /// </summary>
    public string Title { get; set; } = string.Empty;

    /// <summary>
    /// Message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Channel used
    /// </summary>
    public NotificationChannel Channel { get; set; }

    /// <summary>
    /// Success flag
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Error message if failed
    /// </summary>
    public string? ErrorMessage { get; set; }

    /// <summary>
    /// Recipient
    /// </summary>
    public string Recipient { get; set; } = string.Empty;
}
