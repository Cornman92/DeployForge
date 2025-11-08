using DeployForge.Common.Models;
using DeployForge.Common.Models.Scheduling;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for scheduling batch operations
/// </summary>
public interface IScheduleService
{
    /// <summary>
    /// Create schedule
    /// </summary>
    Task<OperationResult<Schedule>> CreateScheduleAsync(
        Schedule schedule,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Update schedule
    /// </summary>
    Task<OperationResult<Schedule>> UpdateScheduleAsync(
        string scheduleId,
        Schedule schedule,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete schedule
    /// </summary>
    Task<OperationResult<bool>> DeleteScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get schedule by ID
    /// </summary>
    Task<OperationResult<Schedule>> GetScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// List all schedules
    /// </summary>
    Task<OperationResult<List<Schedule>>> ListSchedulesAsync(
        bool? enabledOnly = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Manually execute schedule
    /// </summary>
    Task<OperationResult<string>> ExecuteScheduleAsync(
        string scheduleId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get execution history for schedule
    /// </summary>
    Task<OperationResult<List<ScheduleExecution>>> GetExecutionHistoryAsync(
        string scheduleId,
        DateTime? startDate = null,
        DateTime? endDate = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Start scheduler
    /// </summary>
    Task StartAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Stop scheduler
    /// </summary>
    Task StopAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if scheduler is running
    /// </summary>
    bool IsRunning { get; }
}
