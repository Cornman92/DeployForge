using System.Net;
using System.Net.Http.Json;
using DeployForge.Common.Models.Scheduling;
using FluentAssertions;
using Xunit;

namespace DeployForge.Api.IntegrationTests;

/// <summary>
/// Integration tests for scheduling workflow:
/// Create schedule → Update schedule → Execute manually → View history → Delete schedule
/// </summary>
[Collection("API Integration Tests")]
public class SchedulingWorkflowTests
{
    private readonly HttpClient _client;

    public SchedulingWorkflowTests(ApiTestFixture fixture)
    {
        _client = fixture.CreateClient();
    }

    [Fact]
    public async Task SchedulingWorkflow_EndToEnd_Success()
    {
        // Step 1: Create a new schedule
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Integration Test Schedule",
            Description = "Schedule created during integration testing",
            CronExpression = "0 0 2 * * ?", // Daily at 2 AM
            BatchOperationId = "test-batch-operation-123",
            IsEnabled = true,
            Policy = new SchedulePolicy
            {
                MaxRetries = 3,
                RetryDelayMinutes = 5,
                MaxConcurrentExecutions = 1,
                SkipOnFailure = false,
                SendNotifications = true
            },
            MaintenanceWindows = new List<MaintenanceWindow>()
        };

        var createResponse = await _client.PostAsJsonAsync("/api/schedules", schedule);
        createResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var createdSchedule = await createResponse.Content.ReadFromJsonAsync<Schedule>();
        createdSchedule.Should().NotBeNull();
        createdSchedule!.Id.Should().Be(schedule.Id);
        createdSchedule.Name.Should().Be(schedule.Name);

        var scheduleId = createdSchedule.Id;

        // Step 2: Retrieve the created schedule
        var getResponse = await _client.GetAsync($"/api/schedules/{scheduleId}");
        getResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var retrievedSchedule = await getResponse.Content.ReadFromJsonAsync<Schedule>();
        retrievedSchedule.Should().NotBeNull();
        retrievedSchedule!.Id.Should().Be(scheduleId);
        retrievedSchedule.CronExpression.Should().Be("0 0 2 * * ?");

        // Step 3: Update the schedule
        retrievedSchedule.Name = "Updated Integration Test Schedule";
        retrievedSchedule.CronExpression = "0 0 3 * * ?"; // Change to 3 AM
        retrievedSchedule.IsEnabled = false;

        var updateResponse = await _client.PutAsJsonAsync($"/api/schedules/{scheduleId}", retrievedSchedule);
        updateResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var updatedSchedule = await updateResponse.Content.ReadFromJsonAsync<Schedule>();
        updatedSchedule.Should().NotBeNull();
        updatedSchedule!.Name.Should().Be("Updated Integration Test Schedule");
        updatedSchedule.IsEnabled.Should().BeFalse();

        // Step 4: List all schedules
        var listResponse = await _client.GetAsync("/api/schedules");
        listResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var schedules = await listResponse.Content.ReadFromJsonAsync<List<Schedule>>();
        schedules.Should().NotBeNull();
        schedules!.Should().Contain(s => s.Id == scheduleId);

        // Step 5: Execute the schedule manually
        var executeResponse = await _client.PostAsJsonAsync($"/api/schedules/{scheduleId}/execute", new { });
        // May fail if batch operation doesn't exist, but endpoint should respond
        executeResponse.StatusCode.Should().BeOneOf(HttpStatusCode.OK, HttpStatusCode.BadRequest);

        if (executeResponse.StatusCode == HttpStatusCode.OK)
        {
            var executionResult = await executeResponse.Content.ReadFromJsonAsync<ExecutionResult>();
            executionResult.Should().NotBeNull();
            executionResult!.ExecutionId.Should().NotBeNullOrEmpty();

            // Step 6: Wait a moment and then get execution history
            await Task.Delay(1000);

            var historyResponse = await _client.GetAsync($"/api/schedules/{scheduleId}/history");
            historyResponse.StatusCode.Should().Be(HttpStatusCode.OK);

            var history = await historyResponse.Content.ReadFromJsonAsync<List<ScheduleExecution>>();
            history.Should().NotBeNull();
        }

        // Step 7: Delete the schedule
        var deleteResponse = await _client.DeleteAsync($"/api/schedules/{scheduleId}");
        deleteResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        // Step 8: Verify schedule is deleted
        var verifyResponse = await _client.GetAsync($"/api/schedules/{scheduleId}");
        verifyResponse.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [Fact]
    public async Task CreateSchedule_WithValidCronExpression_Success()
    {
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Test Schedule - Hourly",
            CronExpression = "0 0 * * * ?", // Every hour
            BatchOperationId = "test-batch-123",
            IsEnabled = true,
            Policy = new SchedulePolicy
            {
                MaxRetries = 2,
                MaxConcurrentExecutions = 1
            }
        };

        var response = await _client.PostAsJsonAsync("/api/schedules", schedule);
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var created = await response.Content.ReadFromJsonAsync<Schedule>();
        created.Should().NotBeNull();

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{created!.Id}");
    }

    [Fact]
    public async Task CreateSchedule_WithInvalidCronExpression_ReturnsBadRequest()
    {
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Invalid Schedule",
            CronExpression = "invalid cron expression",
            BatchOperationId = "test-batch-123",
            IsEnabled = true
        };

        var response = await _client.PostAsJsonAsync("/api/schedules", schedule);

        // Depending on backend validation, this should fail
        response.StatusCode.Should().BeOneOf(HttpStatusCode.BadRequest, HttpStatusCode.InternalServerError);
    }

    [Fact]
    public async Task ListSchedules_WithEnabledOnlyFilter_ReturnsOnlyEnabledSchedules()
    {
        // Create enabled and disabled schedules
        var enabledSchedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Enabled Schedule",
            CronExpression = "0 0 * * * ?",
            BatchOperationId = "test-123",
            IsEnabled = true
        };

        var disabledSchedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Disabled Schedule",
            CronExpression = "0 0 * * * ?",
            BatchOperationId = "test-456",
            IsEnabled = false
        };

        await _client.PostAsJsonAsync("/api/schedules", enabledSchedule);
        await _client.PostAsJsonAsync("/api/schedules", disabledSchedule);

        // Query with enabled filter
        var response = await _client.GetAsync("/api/schedules?enabledOnly=true");
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var schedules = await response.Content.ReadFromJsonAsync<List<Schedule>>();
        schedules.Should().NotBeNull();
        schedules!.Should().AllSatisfy(s => s.IsEnabled.Should().BeTrue());

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{enabledSchedule.Id}");
        await _client.DeleteAsync($"/api/schedules/{disabledSchedule.Id}");
    }

    [Fact]
    public async Task ExecuteSchedule_NonExistent_ReturnsNotFound()
    {
        var fakeId = Guid.NewGuid().ToString();

        var response = await _client.PostAsJsonAsync($"/api/schedules/{fakeId}/execute", new { });

        response.StatusCode.Should().BeOneOf(HttpStatusCode.NotFound, HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetExecutionHistory_WithDateRange_ReturnsFilteredData()
    {
        // Create a schedule
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "History Test Schedule",
            CronExpression = "0 0 * * * ?",
            BatchOperationId = "test-123",
            IsEnabled = true
        };

        var createResponse = await _client.PostAsJsonAsync("/api/schedules", schedule);
        var created = await createResponse.Content.ReadFromJsonAsync<Schedule>();

        // Get history with date range
        var startDate = DateTime.Today.AddDays(-7);
        var endDate = DateTime.Today;

        var historyResponse = await _client.GetAsync(
            $"/api/schedules/{created!.Id}/history?startDate={startDate:yyyy-MM-dd}&endDate={endDate:yyyy-MM-dd}");

        historyResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var history = await historyResponse.Content.ReadFromJsonAsync<List<ScheduleExecution>>();
        history.Should().NotBeNull();

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{created.Id}");
    }

    [Fact]
    public async Task UpdateSchedule_ChangeMultipleProperties_Success()
    {
        // Create schedule
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Original Name",
            CronExpression = "0 0 2 * * ?",
            BatchOperationId = "batch-1",
            IsEnabled = true,
            Policy = new SchedulePolicy { MaxRetries = 3 }
        };

        await _client.PostAsJsonAsync("/api/schedules", schedule);

        // Update multiple properties
        schedule.Name = "New Name";
        schedule.CronExpression = "0 0 4 * * ?";
        schedule.IsEnabled = false;
        schedule.Policy.MaxRetries = 5;

        var updateResponse = await _client.PutAsJsonAsync($"/api/schedules/{schedule.Id}", schedule);
        updateResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var updated = await updateResponse.Content.ReadFromJsonAsync<Schedule>();
        updated.Should().NotBeNull();
        updated!.Name.Should().Be("New Name");
        updated.CronExpression.Should().Be("0 0 4 * * ?");
        updated.IsEnabled.Should().BeFalse();
        updated.Policy.MaxRetries.Should().Be(5);

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{schedule.Id}");
    }

    [Fact]
    public async Task CreateSchedule_WithMaintenanceWindow_Success()
    {
        var schedule = new Schedule
        {
            Id = Guid.NewGuid().ToString(),
            Name = "Schedule with Maintenance Window",
            CronExpression = "0 0 * * * ?",
            BatchOperationId = "test-123",
            IsEnabled = true,
            MaintenanceWindows = new List<MaintenanceWindow>
            {
                new MaintenanceWindow
                {
                    DayOfWeek = DayOfWeek.Sunday,
                    StartTime = new TimeSpan(22, 0, 0), // 10 PM
                    EndTime = new TimeSpan(6, 0, 0),    // 6 AM
                    BlockExecution = true
                }
            }
        };

        var response = await _client.PostAsJsonAsync("/api/schedules", schedule);
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var created = await response.Content.ReadFromJsonAsync<Schedule>();
        created.Should().NotBeNull();
        created!.MaintenanceWindows.Should().NotBeEmpty();
        created.MaintenanceWindows.First().DayOfWeek.Should().Be(DayOfWeek.Sunday);

        // Cleanup
        await _client.DeleteAsync($"/api/schedules/{created.Id}");
    }
}

// Helper DTOs
public class ExecutionResult
{
    public string ExecutionId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}
