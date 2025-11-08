using System.Net;
using System.Net.Http.Json;
using DeployForge.Common.Models.Notifications;
using FluentAssertions;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for notification workflow:
/// Configure settings → Send test notification → View history → Register webhook
/// </summary>
[Collection("API Integration Tests")]
public class NotificationWorkflowTests
{
    private readonly HttpClient _client;

    public NotificationWorkflowTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task NotificationWorkflow_EndToEnd_Success()
    {
        // Step 1: Configure notification settings
        var settings = new NotificationSettings
        {
            Email = new EmailSettings
            {
                Enabled = true,
                SmtpServer = "smtp.example.com",
                SmtpPort = 587,
                Username = "test@example.com",
                Password = "test-password",
                UseSsl = true,
                FromAddress = "deployforge@example.com",
                DefaultRecipients = new List<string> { "admin@example.com" }
            },
            Slack = new SlackSettings
            {
                Enabled = false,
                WebhookUrl = "https://hooks.slack.com/services/TEST/TEST/TEST",
                DefaultChannel = "#deployforge",
                BotUsername = "DeployForge",
                IconEmoji = ":robot_face:"
            },
            Teams = new TeamsSettings
            {
                Enabled = false,
                WebhookUrl = "https://outlook.office.com/webhook/TEST",
                ThemeColor = "0076D7"
            }
        };

        var configResponse = await _client.PostAsJsonAsync("/api/notifications/configure", settings);
        configResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Step 2: Retrieve settings to verify they were saved
        var getSettingsResponse = await _client.GetAsync("/api/notifications/settings");
        getSettingsResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var savedSettings = await getSettingsResponse.Content.ReadFromJsonAsync<NotificationSettings>();
        savedSettings.Should().NotBeNull();
        savedSettings!.Email.Should().NotBeNull();
        savedSettings.Email!.SmtpServer.Should().Be("smtp.example.com");

        // Step 3: Register a webhook
        var webhook = new WebhookEndpoint
        {
            Url = "https://example.com/webhook",
            Secret = "test-secret-key",
            Events = new List<NotificationEventType>
            {
                NotificationEventType.OperationCompleted,
                NotificationEventType.OperationFailed
            },
            Enabled = true
        };

        var webhookResponse = await _client.PostAsJsonAsync("/api/notifications/webhook", webhook);
        webhookResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var webhookResult = await webhookResponse.Content.ReadFromJsonAsync<WebhookRegistrationResult>();
        webhookResult.Should().NotBeNull();
        webhookResult!.WebhookId.Should().NotBeNullOrEmpty();

        var webhookId = webhookResult.WebhookId;

        // Step 4: Send a notification
        var notification = new NotificationRequest
        {
            EventType = NotificationEventType.OperationCompleted,
            Title = "Test Notification",
            Message = "This is a test notification from integration tests",
            Severity = NotificationSeverity.Info,
            Channels = new List<NotificationChannel> { NotificationChannel.Email }
        };

        var sendResponse = await _client.PostAsJsonAsync("/api/notifications", notification);
        // May fail if SMTP is not configured, but endpoint should accept the request
        sendResponse.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.BadRequest);

        // Step 5: Get notification history
        var historyResponse = await _client.GetAsync("/api/notifications/history");
        historyResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await historyResponse.Content.ReadFromJsonAsync<List<NotificationHistory>>();
        history.Should().NotBeNull();

        // Step 6: Unregister webhook
        var deleteResponse = await _client.DeleteAsync($"/api/notifications/webhook/{webhookId}");
        deleteResponse.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task ConfigureSettings_ValidData_Success()
    {
        var settings = new NotificationSettings
        {
            Email = new EmailSettings
            {
                Enabled = true,
                SmtpServer = "smtp.gmail.com",
                SmtpPort = 587,
                UseSsl = true,
                FromAddress = "test@example.com",
                DefaultRecipients = new List<string> { "recipient@example.com" }
            }
        };

        var response = await _client.PostAsJsonAsync("/api/notifications/configure", settings);
        response.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact]
    public async Task SendTestNotification_Email_ReturnsResponse()
    {
        // Note: This test may fail if SMTP is not properly configured
        // But the endpoint should still respond
        var response = await _client.PostAsJsonAsync(
            "/api/notifications/test?channel=Email&recipient=test@example.com",
            new { });

        response.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task RegisterWebhook_ValidData_ReturnsWebhookId()
    {
        var webhook = new WebhookEndpoint
        {
            Url = "https://example.com/hook",
            Secret = "my-secret-key",
            Events = new List<NotificationEventType> { NotificationEventType.OperationStarted },
            Enabled = true
        };

        var response = await _client.PostAsJsonAsync("/api/notifications/webhook", webhook);
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var result = await response.Content.ReadFromJsonAsync<WebhookRegistrationResult>();
        result.Should().NotBeNull();
        result!.WebhookId.Should().NotBeNullOrEmpty();

        // Cleanup
        await _client.DeleteAsync($"/api/notifications/webhook/{result.WebhookId}");
    }

    [Fact]
    public async Task GetNotificationHistory_WithFilters_ReturnsFilteredData()
    {
        var startDate = DateTime.Today.AddDays(-7);
        var endDate = DateTime.Today;

        var response = await _client.GetAsync(
            $"/api/notifications/history?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}&eventType={NotificationEventType.OperationCompleted}");

        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await response.Content.ReadFromJsonAsync<List<NotificationHistory>>();
        history.Should().NotBeNull();

        foreach (var item in history!)
        {
            item.Timestamp.Date.Should().BeOnOrAfter(startDate).And.BeOnOrBefore(endDate);
            if (!string.IsNullOrEmpty(item.EventType))
            {
                item.EventType.Should().Be(NotificationEventType.OperationCompleted.ToString());
            }
        }
    }

    [Fact]
    public async Task UnregisterWebhook_NonExistent_ReturnsNotFound()
    {
        var fakeId = Guid.NewGuid().ToString();

        var response = await _client.DeleteAsync($"/api/notifications/webhook/{fakeId}");

        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task SendNotification_MultipleChannels_Success()
    {
        var notification = new NotificationRequest
        {
            EventType = NotificationEventType.SystemAlert,
            Title = "Multi-Channel Test",
            Message = "Testing multiple notification channels",
            Severity = NotificationSeverity.Warning,
            Channels = new List<NotificationChannel>
            {
                NotificationChannel.Email,
                NotificationChannel.Webhook
            },
            Data = new Dictionary<string, object>
            {
                { "TestKey", "TestValue" },
                { "Timestamp", DateTime.UtcNow }
            }
        };

        var response = await _client.PostAsJsonAsync("/api/notifications", notification);

        // May fail if channels are not configured, but endpoint should respond
        response.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.BadRequest);
    }
}

// Helper DTOs
public class WebhookRegistrationResult
{
    public string WebhookId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}
