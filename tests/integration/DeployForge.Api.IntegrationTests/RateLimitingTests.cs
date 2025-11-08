using FluentAssertions;
using System.Net;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for rate limiting functionality
/// </summary>
public class RateLimitingTests : IClassFixture<ApiTestFixture>
{
    private readonly HttpClient _client;

    public RateLimitingTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task Health_Endpoint_Should_Apply_Rate_Limiting()
    {
        // Arrange
        const int requestCount = 70; // Exceeds 60 requests/minute limit for health endpoint
        var tasks = new List<Task<HttpResponseMessage>>();

        // Act - Send requests rapidly
        for (int i = 0; i < requestCount; i++)
        {
            tasks.Add(_client.GetAsync("/api/health"));
        }

        var responses = await Task.WhenAll(tasks);

        // Assert - At least one request should be rate limited
        var rateLimitedResponses = responses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        rateLimitedResponses.Should().BeGreaterThan(0, "Rate limiting should block some requests");

        var successfulResponses = responses.Count(r => r.StatusCode == HttpStatusCode.OK);
        successfulResponses.Should().BeLessOrEqualTo(60, "Should not exceed permit limit");

        // Check for Retry-After header in rate limited responses
        var rateLimitedResponse = responses.FirstOrDefault(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        if (rateLimitedResponse != null)
        {
            rateLimitedResponse.Headers.Should().ContainKey("Retry-After");
        }
    }

    [Fact]
    public async Task Reports_Endpoint_Should_Have_Lower_Rate_Limit()
    {
        // Arrange
        const int requestCount = 15; // Exceeds 10 requests/minute limit for reports endpoint
        var tasks = new List<Task<HttpResponseMessage>>();

        // Act - Send requests rapidly
        for (int i = 0; i < requestCount; i++)
        {
            tasks.Add(_client.GetAsync("/api/reports"));
        }

        var responses = await Task.WhenAll(tasks);

        // Assert - Rate limiting should be stricter for expensive operations
        var rateLimitedResponses = responses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        rateLimitedResponses.Should().BeGreaterThan(0, "Report generation should have strict rate limiting");

        var successfulResponses = responses.Count(r => r.StatusCode == HttpStatusCode.OK || r.StatusCode == HttpStatusCode.NoContent);
        successfulResponses.Should().BeLessOrEqualTo(10, "Should not exceed report permit limit");
    }

    [Fact]
    public async Task Rate_Limit_Response_Should_Include_Problem_Details()
    {
        // Arrange
        const int requestCount = 70;
        var tasks = new List<Task<HttpResponseMessage>>();

        // Act
        for (int i = 0; i < requestCount; i++)
        {
            tasks.Add(_client.GetAsync("/api/health"));
        }

        var responses = await Task.WhenAll(tasks);

        // Assert
        var rateLimitedResponse = responses.FirstOrDefault(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        if (rateLimitedResponse != null)
        {
            var content = await rateLimitedResponse.Content.ReadAsStringAsync();
            content.Should().Contain("Too Many Requests");
            content.Should().Contain("Rate limit exceeded");
            content.Should().Contain("retryAfter");
        }
    }

    [Fact]
    public async Task Monitoring_Endpoint_Should_Have_Higher_Rate_Limit()
    {
        // Arrange
        const int requestCount = 130; // Monitoring has 120 requests/minute limit
        var tasks = new List<Task<HttpResponseMessage>>();

        // Act
        for (int i = 0; i < requestCount; i++)
        {
            tasks.Add(_client.GetAsync("/api/health/metrics"));
        }

        var responses = await Task.WhenAll(tasks);

        // Assert - Should allow more requests for monitoring
        var successfulResponses = responses.Count(r => r.StatusCode == HttpStatusCode.OK);
        successfulResponses.Should().BeGreaterThan(100, "Monitoring endpoints should have higher limits");

        var rateLimitedResponses = responses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        rateLimitedResponses.Should().BeGreaterThan(0, "Should still enforce a limit");
    }

    [Fact]
    public async Task Different_Endpoints_Should_Have_Independent_Rate_Limits()
    {
        // Arrange
        var healthRequests = new List<Task<HttpResponseMessage>>();
        var scheduleRequests = new List<Task<HttpResponseMessage>>();

        // Act - Hit health endpoint limit
        for (int i = 0; i < 70; i++)
        {
            healthRequests.Add(_client.GetAsync("/api/health"));
        }
        var healthResponses = await Task.WhenAll(healthRequests);

        // Then try schedules endpoint
        for (int i = 0; i < 10; i++)
        {
            scheduleRequests.Add(_client.GetAsync("/api/schedules"));
        }
        var scheduleResponses = await Task.WhenAll(scheduleRequests);

        // Assert - Schedule requests should succeed despite health being rate limited
        var healthRateLimited = healthResponses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        healthRateLimited.Should().BeGreaterThan(0, "Health endpoint should be rate limited");

        var scheduleSuccessful = scheduleResponses.Count(r => r.StatusCode == HttpStatusCode.OK || r.StatusCode == HttpStatusCode.NoContent);
        scheduleSuccessful.Should().BeGreaterThan(0, "Schedule endpoint should still accept requests");
    }

    [Fact]
    public async Task Rate_Limit_Should_Reset_After_Window()
    {
        // Arrange
        const int firstBatchCount = 70;
        var firstBatch = new List<Task<HttpResponseMessage>>();

        // Act - First batch (should hit limit)
        for (int i = 0; i < firstBatchCount; i++)
        {
            firstBatch.Add(_client.GetAsync("/api/health"));
        }
        var firstResponses = await Task.WhenAll(firstBatch);

        var firstRateLimited = firstResponses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        firstRateLimited.Should().BeGreaterThan(0, "First batch should be rate limited");

        // Wait for rate limit window to reset (with sliding window, wait partial window)
        await Task.Delay(TimeSpan.FromSeconds(25));

        // Second batch (should succeed after window slides)
        var secondResponse = await _client.GetAsync("/api/health");

        // Assert
        secondResponse.StatusCode.Should().Be(HttpStatusCode.OK, "Request should succeed after window slides");
    }

    [Fact]
    public async Task Concurrent_Requests_Should_Be_Limited_Globally()
    {
        // Arrange
        const int requestCount = 150; // Exceeds global limit of 100 requests/minute
        var tasks = new List<Task<HttpResponseMessage>>();
        var endpoints = new[] { "/api/health", "/api/health/metrics", "/api/schedules" };

        // Act - Send requests to various endpoints
        for (int i = 0; i < requestCount; i++)
        {
            var endpoint = endpoints[i % endpoints.Length];
            tasks.Add(_client.GetAsync(endpoint));
        }

        var responses = await Task.WhenAll(tasks);

        // Assert - Global rate limiter should kick in
        var rateLimitedResponses = responses.Count(r => r.StatusCode == HttpStatusCode.TooManyRequests);
        rateLimitedResponses.Should().BeGreaterThan(0, "Global rate limiter should block excessive requests");

        var totalSuccessful = responses.Count(r => r.IsSuccessStatusCode);
        totalSuccessful.Should().BeLessOrEqualTo(100, "Should not exceed global permit limit significantly");
    }
}
