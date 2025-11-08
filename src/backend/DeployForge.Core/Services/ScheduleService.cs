using System.Text.Json;
using DeployForge.Common.Models;
using DeployForge.Common.Models.Scheduling;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;
using Quartz;
using Quartz.Impl;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for scheduling batch operations using Quartz.NET
/// </summary>
public class ScheduleService : IScheduleService
{
    private readonly ILogger<ScheduleService> _logger;
    private readonly IBatchOperationService _batchOperationService;
    private readonly INotificationService _notificationService;
    private readonly string _schedulesPath;
    private readonly string _executionHistoryPath;
    private readonly Dictionary<string, Schedule> _schedules = new();
    private readonly List<ScheduleExecution> _executionHistory = new();
    private IScheduler? _scheduler;

    public bool IsRunning => _scheduler?.IsStarted ?? false;

    public ScheduleService(
        ILogger<ScheduleService> logger,
        IBatchOperationService batchOperationService,
        INotificationService notificationService)
    {
        _logger = logger;
        _batchOperationService = batchOperationService;
        _notificationService = notificationService;

        // Set storage paths
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        var schedulingDir = Path.Combine(appData, "DeployForge", "Scheduling");
        Directory.CreateDirectory(schedulingDir);
        _schedulesPath = Path.Combine(schedulingDir, "schedules.json");
        _executionHistoryPath = Path.Combine(schedulingDir, "history.json");

        // Load data
        LoadSchedules();
        LoadExecutionHistory();
    }

    public async Task<OperationResult<Schedule>> CreateScheduleAsync(
        Schedule schedule,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Validate cron expression
            if (!CronExpression.IsValidExpression(schedule.CronExpression))
            {
                return OperationResult<Schedule>.FailureResult("Invalid cron expression");
            }

            _schedules[schedule.Id] = schedule;

            // Calculate next run time
            var cronExpression = new CronExpression(schedule.CronExpression);
            schedule.NextRunTime = cronExpression.GetNextValidTimeAfter(DateTimeOffset.UtcNow)?.UtcDateTime;

            await SaveSchedulesAsync();

            // Schedule the job if enabled
            if (schedule.Enabled && _scheduler != null)
            {
                await ScheduleJobAsync(schedule);
            }

            _logger.LogInformation("Schedule {ScheduleId} created: {Name}", schedule.Id, schedule.Name);
            return OperationResult<Schedule>.SuccessResult(schedule);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create schedule");
            return OperationResult<Schedule>.FailureResult($"Failed to create schedule: {ex.Message}");
        }
    }

    public async Task<OperationResult<Schedule>> UpdateScheduleAsync(
        string scheduleId,
        Schedule schedule,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_schedules.ContainsKey(scheduleId))
            {
                return OperationResult<Schedule>.FailureResult("Schedule not found");
            }

            // Validate cron expression
            if (!CronExpression.IsValidExpression(schedule.CronExpression))
            {
                return OperationResult<Schedule>.FailureResult("Invalid cron expression");
            }

            _schedules[scheduleId] = schedule;

            // Recalculate next run time
            var cronExpression = new CronExpression(schedule.CronExpression);
            schedule.NextRunTime = cronExpression.GetNextValidTimeAfter(DateTimeOffset.UtcNow)?.UtcDateTime;

            await SaveSchedulesAsync();

            // Reschedule the job
            if (_scheduler != null)
            {
                var jobKey = new JobKey(scheduleId, "DeployForge");
                await _scheduler.DeleteJob(jobKey);

                if (schedule.Enabled)
                {
                    await ScheduleJobAsync(schedule);
                }
            }

            _logger.LogInformation("Schedule {ScheduleId} updated", scheduleId);
            return OperationResult<Schedule>.SuccessResult(schedule);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update schedule {ScheduleId}", scheduleId);
            return OperationResult<Schedule>.FailureResult($"Failed to update schedule: {ex.Message}");
        }
    }

    public async Task<OperationResult<bool>> DeleteScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_schedules.Remove(scheduleId))
            {
                return OperationResult<bool>.FailureResult("Schedule not found");
            }

            await SaveSchedulesAsync();

            // Remove from Quartz
            if (_scheduler != null)
            {
                var jobKey = new JobKey(scheduleId, "DeployForge");
                await _scheduler.DeleteJob(jobKey);
            }

            _logger.LogInformation("Schedule {ScheduleId} deleted", scheduleId);
            return OperationResult<bool>.SuccessResult(true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to delete schedule {ScheduleId}", scheduleId);
            return OperationResult<bool>.FailureResult($"Failed to delete schedule: {ex.Message}");
        }
    }

    public Task<OperationResult<Schedule>> GetScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        if (_schedules.TryGetValue(scheduleId, out var schedule))
        {
            return Task.FromResult(OperationResult<Schedule>.SuccessResult(schedule));
        }

        return Task.FromResult(OperationResult<Schedule>.FailureResult("Schedule not found"));
    }

    public Task<OperationResult<List<Schedule>>> ListSchedulesAsync(
        bool? enabledOnly = null,
        CancellationToken cancellationToken = default)
    {
        var schedules = _schedules.Values.AsEnumerable();

        if (enabledOnly.HasValue)
        {
            schedules = schedules.Where(s => s.Enabled == enabledOnly.Value);
        }

        return Task.FromResult(
            OperationResult<List<Schedule>>.SuccessResult(schedules.ToList()));
    }

    public async Task<OperationResult<string>> ExecuteScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            if (!_schedules.TryGetValue(scheduleId, out var schedule))
            {
                return OperationResult<string>.FailureResult("Schedule not found");
            }

            _logger.LogInformation("Manually executing schedule {ScheduleId}", scheduleId);

            var execution = new ScheduleExecution
            {
                ScheduleId = scheduleId,
                ScheduleName = schedule.Name,
                BatchOperationId = schedule.BatchOperationId,
                Status = ScheduleExecutionStatus.Running
            };

            _executionHistory.Add(execution);

            try
            {
                // Execute the batch operation (this would call the actual batch operation service)
                // For now, just simulate execution
                await Task.Delay(100, cancellationToken);

                execution.EndTime = DateTime.UtcNow;
                execution.Status = ScheduleExecutionStatus.Completed;
                execution.Message = "Batch operation completed successfully";

                schedule.LastRunTime = DateTime.UtcNow;
                schedule.LastRunStatus = ScheduleExecutionStatus.Completed;

                // Send notification if configured
                if (schedule.Policy.NotifyOnCompletion)
                {
                    await _notificationService.SendNotificationAsync(new Common.Models.Notifications.NotificationRequest
                    {
                        EventType = Common.Models.Notifications.NotificationEventType.OperationCompleted,
                        Title = $"Scheduled operation completed: {schedule.Name}",
                        Message = $"The scheduled batch operation '{schedule.Name}' has completed successfully.",
                        Severity = Common.Models.Notifications.NotificationSeverity.Success
                    });
                }
            }
            catch (Exception ex)
            {
                execution.EndTime = DateTime.UtcNow;
                execution.Status = ScheduleExecutionStatus.Failed;
                execution.Message = "Batch operation failed";
                execution.ErrorDetails = ex.Message;

                schedule.LastRunTime = DateTime.UtcNow;
                schedule.LastRunStatus = ScheduleExecutionStatus.Failed;

                // Send failure notification if configured
                if (schedule.Policy.NotifyOnFailure)
                {
                    await _notificationService.SendNotificationAsync(new Common.Models.Notifications.NotificationRequest
                    {
                        EventType = Common.Models.Notifications.NotificationEventType.OperationFailed,
                        Title = $"Scheduled operation failed: {schedule.Name}",
                        Message = $"The scheduled batch operation '{schedule.Name}' has failed: {ex.Message}",
                        Severity = Common.Models.Notifications.NotificationSeverity.Error
                    });
                }

                throw;
            }

            await SaveSchedulesAsync();
            await SaveExecutionHistoryAsync();

            return OperationResult<string>.SuccessResult(execution.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to execute schedule {ScheduleId}", scheduleId);
            return OperationResult<string>.FailureResult($"Failed to execute schedule: {ex.Message}");
        }
    }

    public Task<OperationResult<List<ScheduleExecution>>> GetExecutionHistoryAsync(
        string scheduleId,
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        var history = _executionHistory
            .Where(e => e.ScheduleId == scheduleId);

        if (startDate.HasValue)
            history = history.Where(e => e.StartTime >= startDate.Value);

        if (endDate.HasValue)
            history = history.Where(e => e.StartTime <= endDate.Value);

        return Task.FromResult(
            OperationResult<List<ScheduleExecution>>.SuccessResult(
                history.OrderByDescending(e => e.StartTime).ToList()));
    }

    public async Task StartAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Starting scheduler");

            // Create Quartz scheduler
            var factory = new StdSchedulerFactory();
            _scheduler = await factory.GetScheduler(cancellationToken);

            // Schedule all enabled schedules
            foreach (var schedule in _schedules.Values.Where(s => s.Enabled))
            {
                await ScheduleJobAsync(schedule);
            }

            await _scheduler.Start(cancellationToken);

            _logger.LogInformation("Scheduler started with {Count} active schedules",
                _schedules.Values.Count(s => s.Enabled));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to start scheduler");
            throw;
        }
    }

    public async Task StopAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            if (_scheduler != null)
            {
                await _scheduler.Shutdown(cancellationToken);
                _logger.LogInformation("Scheduler stopped");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to stop scheduler");
            throw;
        }
    }

    #region Private Methods

    private async Task ScheduleJobAsync(Schedule schedule)
    {
        if (_scheduler == null)
            return;

        var job = JobBuilder.Create<ScheduledBatchOperationJob>()
            .WithIdentity(schedule.Id, "DeployForge")
            .UsingJobData("scheduleId", schedule.Id)
            .Build();

        var trigger = TriggerBuilder.Create()
            .WithIdentity($"{schedule.Id}-trigger", "DeployForge")
            .WithCronSchedule(schedule.CronExpression)
            .Build();

        await _scheduler.ScheduleJob(job, trigger);

        _logger.LogInformation("Job scheduled for {ScheduleId} with cron: {Cron}",
            schedule.Id, schedule.CronExpression);
    }

    private void LoadSchedules()
    {
        try
        {
            if (File.Exists(_schedulesPath))
            {
                var json = File.ReadAllText(_schedulesPath);
                var schedules = JsonSerializer.Deserialize<List<Schedule>>(json);
                if (schedules != null)
                {
                    foreach (var schedule in schedules)
                    {
                        _schedules[schedule.Id] = schedule;
                    }
                }
                _logger.LogInformation("Loaded {Count} schedules", _schedules.Count);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load schedules");
        }
    }

    private async Task SaveSchedulesAsync()
    {
        try
        {
            var json = JsonSerializer.Serialize(_schedules.Values, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_schedulesPath, json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save schedules");
        }
    }

    private void LoadExecutionHistory()
    {
        try
        {
            if (File.Exists(_executionHistoryPath))
            {
                var json = File.ReadAllText(_executionHistoryPath);
                var history = JsonSerializer.Deserialize<List<ScheduleExecution>>(json);
                if (history != null)
                {
                    _executionHistory.AddRange(history);
                }
                _logger.LogInformation("Loaded {Count} execution records", _executionHistory.Count);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load execution history");
        }
    }

    private async Task SaveExecutionHistoryAsync()
    {
        try
        {
            // Keep only last 1000 executions
            var recentHistory = _executionHistory
                .OrderByDescending(e => e.StartTime)
                .Take(1000)
                .ToList();

            var json = JsonSerializer.Serialize(recentHistory, new JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(_executionHistoryPath, json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save execution history");
        }
    }

    #endregion
}

/// <summary>
/// Quartz job for executing scheduled batch operations
/// </summary>
public class ScheduledBatchOperationJob : IJob
{
    public Task Execute(IJobExecutionContext context)
    {
        var scheduleId = context.JobDetail.JobDataMap.GetString("scheduleId");
        // This would trigger the actual schedule execution
        // For now, just log it
        Console.WriteLine($"Executing scheduled job for schedule: {scheduleId}");
        return Task.CompletedTask;
    }
}
