using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Notifications Center ViewModel for notification configuration and history
/// </summary>
public partial class NotificationsCenterViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<NotificationsCenterViewModel> _logger;

    private NotificationHistoryItem? _selectedHistory;
    private string _selectedChannel = "Email";
    private bool _emailEnabled = true;
    private bool _slackEnabled;
    private bool _teamsEnabled;
    private bool _webhooksEnabled;

    // Email settings
    private string _smtpServer = string.Empty;
    private int _smtpPort = 587;
    private string _smtpUsername = string.Empty;
    private string _smtpPassword = string.Empty;
    private bool _smtpUseSsl = true;
    private string _emailFrom = string.Empty;
    private string _emailTo = string.Empty;

    // Slack settings
    private string _slackWebhookUrl = string.Empty;
    private string _slackChannel = "#general";
    private string _slackUsername = "DeployForge";

    // Teams settings
    private string _teamsWebhookUrl = string.Empty;

    // Test notification
    private string _testSubject = "Test Notification";
    private string _testMessage = "This is a test notification from DeployForge";

    public NotificationHistoryItem? SelectedHistory
    {
        get => _selectedHistory;
        set => SetProperty(ref _selectedHistory, value);
    }

    public string SelectedChannel
    {
        get => _selectedChannel;
        set => SetProperty(ref _selectedChannel, value);
    }

    public bool EmailEnabled
    {
        get => _emailEnabled;
        set => SetProperty(ref _emailEnabled, value);
    }

    public bool SlackEnabled
    {
        get => _slackEnabled;
        set => SetProperty(ref _slackEnabled, value);
    }

    public bool TeamsEnabled
    {
        get => _teamsEnabled;
        set => SetProperty(ref _teamsEnabled, value);
    }

    public bool WebhooksEnabled
    {
        get => _webhooksEnabled;
        set => SetProperty(ref _webhooksEnabled, value);
    }

    // Email Settings
    public string SmtpServer
    {
        get => _smtpServer;
        set => SetProperty(ref _smtpServer, value);
    }

    public int SmtpPort
    {
        get => _smtpPort;
        set => SetProperty(ref _smtpPort, value);
    }

    public string SmtpUsername
    {
        get => _smtpUsername;
        set => SetProperty(ref _smtpUsername, value);
    }

    public string SmtpPassword
    {
        get => _smtpPassword;
        set => SetProperty(ref _smtpPassword, value);
    }

    public bool SmtpUseSsl
    {
        get => _smtpUseSsl;
        set => SetProperty(ref _smtpUseSsl, value);
    }

    public string EmailFrom
    {
        get => _emailFrom;
        set => SetProperty(ref _emailFrom, value);
    }

    public string EmailTo
    {
        get => _emailTo;
        set => SetProperty(ref _emailTo, value);
    }

    // Slack Settings
    public string SlackWebhookUrl
    {
        get => _slackWebhookUrl;
        set => SetProperty(ref _slackWebhookUrl, value);
    }

    public string SlackChannel
    {
        get => _slackChannel;
        set => SetProperty(ref _slackChannel, value);
    }

    public string SlackUsername
    {
        get => _slackUsername;
        set => SetProperty(ref _slackUsername, value);
    }

    // Teams Settings
    public string TeamsWebhookUrl
    {
        get => _teamsWebhookUrl;
        set => SetProperty(ref _teamsWebhookUrl, value);
    }

    // Test Notification
    public string TestSubject
    {
        get => _testSubject;
        set => SetProperty(ref _testSubject, value);
    }

    public string TestMessage
    {
        get => _testMessage;
        set => SetProperty(ref _testMessage, value);
    }

    public ObservableCollection<string> NotificationChannels { get; } = new()
    {
        "Email",
        "Slack",
        "Teams",
        "Webhook"
    };

    public ObservableCollection<NotificationHistoryItem> History { get; } = new();

    public NotificationsCenterViewModel(
        IApiClient apiClient,
        ILogger<NotificationsCenterViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadSettingsAsync();
        await LoadHistoryAsync();
    }

    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Saving notification settings...";

            var settings = new
            {
                Email = new
                {
                    Enabled = EmailEnabled,
                    SmtpServer,
                    SmtpPort,
                    Username = SmtpUsername,
                    Password = SmtpPassword,
                    UseSsl = SmtpUseSsl,
                    FromAddress = EmailFrom,
                    DefaultRecipients = EmailTo.Split(';', StringSplitOptions.RemoveEmptyEntries).ToList()
                },
                Slack = new
                {
                    Enabled = SlackEnabled,
                    WebhookUrl = SlackWebhookUrl,
                    DefaultChannel = SlackChannel,
                    BotUsername = SlackUsername,
                    IconEmoji = ":robot_face:"
                },
                Teams = new
                {
                    Enabled = TeamsEnabled,
                    WebhookUrl = TeamsWebhookUrl,
                    ThemeColor = "0076D7"
                },
                Webhooks = new
                {
                    Enabled = WebhooksEnabled,
                    Endpoints = new List<object>()
                }
            };

            await _apiClient.PostAsync<object, object>("notifications/configure", settings);
            StatusMessage = "Notification settings saved successfully";
            _logger.LogInformation("Notification settings saved");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save notification settings");
            StatusMessage = "Failed to save notification settings";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task SendTestNotificationAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = $"Sending test notification via {SelectedChannel}...";

            var channelParam = SelectedChannel switch
            {
                "Email" => "Email",
                "Slack" => "Slack",
                "Teams" => "Teams",
                "Webhook" => "Webhook",
                _ => "Email"
            };

            var recipient = SelectedChannel switch
            {
                "Email" => EmailTo.Split(';', StringSplitOptions.RemoveEmptyEntries).FirstOrDefault(),
                "Slack" => SlackChannel,
                _ => null
            };

            await _apiClient.PostAsync<object, object>(
                $"notifications/test?channel={channelParam}&recipient={recipient}",
                new { });

            StatusMessage = $"Test notification sent via {SelectedChannel}";
            _logger.LogInformation("Test notification sent via {Channel}", SelectedChannel);

            // Reload history to show the test notification
            await Task.Delay(1000);
            await LoadHistoryAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send test notification");
            StatusMessage = $"Failed to send test notification: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task RefreshHistoryAsync()
    {
        await LoadHistoryAsync();
    }

    [RelayCommand]
    private async Task ClearHistoryAsync()
    {
        History.Clear();
        StatusMessage = "History cleared";
    }

    private async Task LoadSettingsAsync()
    {
        try
        {
            var settings = await _apiClient.GetAsync<NotificationSettingsResponse>("notifications/settings");
            if (settings != null)
            {
                // Email settings
                EmailEnabled = settings.Email?.Enabled ?? true;
                SmtpServer = settings.Email?.SmtpServer ?? string.Empty;
                SmtpPort = settings.Email?.SmtpPort ?? 587;
                SmtpUsername = settings.Email?.Username ?? string.Empty;
                SmtpUseSsl = settings.Email?.UseSsl ?? true;
                EmailFrom = settings.Email?.FromAddress ?? string.Empty;
                EmailTo = string.Join(";", settings.Email?.DefaultRecipients ?? new List<string>());

                // Slack settings
                SlackEnabled = settings.Slack?.Enabled ?? false;
                SlackWebhookUrl = settings.Slack?.WebhookUrl ?? string.Empty;
                SlackChannel = settings.Slack?.DefaultChannel ?? "#general";
                SlackUsername = settings.Slack?.BotUsername ?? "DeployForge";

                // Teams settings
                TeamsEnabled = settings.Teams?.Enabled ?? false;
                TeamsWebhookUrl = settings.Teams?.WebhookUrl ?? string.Empty;

                // Webhooks
                WebhooksEnabled = settings.Webhooks?.Enabled ?? false;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load notification settings");
        }
    }

    private async Task LoadHistoryAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading notification history...";

            var history = await _apiClient.GetAsync<List<NotificationHistoryItem>>("notifications/history");
            if (history != null)
            {
                History.Clear();
                foreach (var item in history.OrderByDescending(h => h.SentAt).Take(100))
                {
                    History.Add(item);
                }
                StatusMessage = $"Loaded {history.Count} notifications";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load notification history");
            StatusMessage = "Failed to load notification history";
        }
        finally
        {
            IsBusy = false;
        }
    }
}

public class NotificationHistoryItem
{
    public string Id { get; set; } = string.Empty;
    public string Channel { get; set; } = string.Empty;
    public string EventType { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public string Recipient { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime SentAt { get; set; }
}

public class NotificationSettingsResponse
{
    public EmailSettingsResponse? Email { get; set; }
    public SlackSettingsResponse? Slack { get; set; }
    public TeamsSettingsResponse? Teams { get; set; }
    public WebhooksSettingsResponse? Webhooks { get; set; }
}

public class EmailSettingsResponse
{
    public bool Enabled { get; set; }
    public string? SmtpServer { get; set; }
    public int SmtpPort { get; set; }
    public string? Username { get; set; }
    public bool UseSsl { get; set; }
    public string? FromAddress { get; set; }
    public List<string>? DefaultRecipients { get; set; }
}

public class SlackSettingsResponse
{
    public bool Enabled { get; set; }
    public string? WebhookUrl { get; set; }
    public string? DefaultChannel { get; set; }
    public string? BotUsername { get; set; }
}

public class TeamsSettingsResponse
{
    public bool Enabled { get; set; }
    public string? WebhookUrl { get; set; }
}

public class WebhooksSettingsResponse
{
    public bool Enabled { get; set; }
}
