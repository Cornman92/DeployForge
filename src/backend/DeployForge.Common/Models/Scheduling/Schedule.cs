namespace DeployForge.Common.Models.Scheduling;

/// <summary>
/// Scheduled operation
/// </summary>
public class Schedule
{
    /// <summary>
    /// Schedule ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Schedule name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Description
    /// </summary>
    public string Description { get; set; } = string.Empty;

    /// <summary>
    /// Enabled flag
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Cron expression
    /// </summary>
    public string CronExpression { get; set; } = string.Empty;

    /// <summary>
    /// Batch operation ID to execute
    /// </summary>
    public string BatchOperationId { get; set; } = string.Empty;

    /// <summary>
    /// Next run time
    /// </summary>
    public DateTime? NextRunTime { get; set; }

    /// <summary>
    /// Last run time
    /// </summary>
    public DateTime? LastRunTime { get; set; }

    /// <summary>
    /// Last run status
    /// </summary>
    public ScheduleExecutionStatus? LastRunStatus { get; set; }

    /// <summary>
    /// Created timestamp
    /// </summary>
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// Created by user
    /// </summary>
    public string CreatedBy { get; set; } = string.Empty;

    /// <summary>
    /// Maintenance windows (don't run during these times)
    /// </summary>
    public List<MaintenanceWindow> MaintenanceWindows { get; set; } = new();

    /// <summary>
    /// Execution policy
    /// </summary>
    public SchedulePolicy Policy { get; set; } = new();
}

/// <summary>
/// Maintenance window
/// </summary>
public class MaintenanceWindow
{
    /// <summary>
    /// Window name
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Start time (day of week and time)
    /// </summary>
    public DayOfWeek StartDay { get; set; }

    /// <summary>
    /// Start hour (0-23)
    /// </summary>
    public int StartHour { get; set; }

    /// <summary>
    /// End day of week
    /// </summary>
    public DayOfWeek EndDay { get; set; }

    /// <summary>
    /// End hour (0-23)
    /// </summary>
    public int EndHour { get; set; }
}

/// <summary>
/// Schedule policy
/// </summary>
public class SchedulePolicy
{
    /// <summary>
    /// Maximum concurrent executions
    /// </summary>
    public int MaxConcurrentExecutions { get; set; } = 1;

    /// <summary>
    /// Retry failed operations
    /// </summary>
    public bool RetryOnFailure { get; set; } = false;

    /// <summary>
    /// Max retry attempts
    /// </summary>
    public int MaxRetryAttempts { get; set; } = 3;

    /// <summary>
    /// Send notification on completion
    /// </summary>
    public bool NotifyOnCompletion { get; set; } = true;

    /// <summary>
    /// Send notification on failure
    /// </summary>
    public bool NotifyOnFailure { get; set; } = true;
}

/// <summary>
/// Schedule execution record
/// </summary>
public class ScheduleExecution
{
    /// <summary>
    /// Execution ID
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();

    /// <summary>
    /// Schedule ID
    /// </summary>
    public string ScheduleId { get; set; } = string.Empty;

    /// <summary>
    /// Schedule name
    /// </summary>
    public string ScheduleName { get; set; } = string.Empty;

    /// <summary>
    /// Start timestamp
    /// </summary>
    public DateTime StartTime { get; set; } = DateTime.UtcNow;

    /// <summary>
    /// End timestamp
    /// </summary>
    public DateTime? EndTime { get; set; }

    /// <summary>
    /// Execution status
    /// </summary>
    public ScheduleExecutionStatus Status { get; set; }

    /// <summary>
    /// Result message
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// Batch operation ID that was executed
    /// </summary>
    public string BatchOperationId { get; set; } = string.Empty;

    /// <summary>
    /// Error details if failed
    /// </summary>
    public string? ErrorDetails { get; set; }

    /// <summary>
    /// Duration in milliseconds
    /// </summary>
    public long DurationMs => EndTime.HasValue
        ? (long)(EndTime.Value - StartTime).TotalMilliseconds
        : 0;
}

/// <summary>
/// Schedule execution status
/// </summary>
public enum ScheduleExecutionStatus
{
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
    Skipped
}
