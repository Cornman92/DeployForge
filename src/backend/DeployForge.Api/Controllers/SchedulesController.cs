using DeployForge.Common.Models.Scheduling;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Controller for schedule management
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class SchedulesController : ControllerBase
{
    private readonly IScheduleService _scheduleService;
    private readonly ILogger<SchedulesController> _logger;

    public SchedulesController(
        IScheduleService scheduleService,
        ILogger<SchedulesController> logger)
    {
        _scheduleService = scheduleService;
        _logger = logger;
    }

    /// <summary>
    /// Create schedule
    /// </summary>
    [HttpPost]
    public async Task<ActionResult<Schedule>> CreateSchedule(
        [FromBody] Schedule schedule,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.CreateScheduleAsync(schedule, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Update schedule
    /// </summary>
    [HttpPut("{scheduleId}")]
    public async Task<ActionResult<Schedule>> UpdateSchedule(
        string scheduleId,
        [FromBody] Schedule schedule,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.UpdateScheduleAsync(scheduleId, schedule, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Delete schedule
    /// </summary>
    [HttpDelete("{scheduleId}")]
    public async Task<IActionResult> DeleteSchedule(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.DeleteScheduleAsync(scheduleId, cancellationToken);

        if (!result.Success)
            return NotFound(result.ErrorMessage);

        return Ok(new { Message = "Schedule deleted successfully" });
    }

    /// <summary>
    /// Get schedule by ID
    /// </summary>
    [HttpGet("{scheduleId}")]
    public async Task<ActionResult<Schedule>> GetSchedule(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.GetScheduleAsync(scheduleId, cancellationToken);

        if (!result.Success || result.Data == null)
            return NotFound(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// List all schedules
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<Schedule>>> ListSchedules(
        [FromQuery] bool? enabledOnly = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.ListSchedulesAsync(enabledOnly, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }

    /// <summary>
    /// Manually execute schedule
    /// </summary>
    [HttpPost("{scheduleId}/execute")]
    public async Task<IActionResult> ExecuteSchedule(
        string scheduleId,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.ExecuteScheduleAsync(scheduleId, cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(new { ExecutionId = result.Data, Message = "Schedule executed successfully" });
    }

    /// <summary>
    /// Get execution history for schedule
    /// </summary>
    [HttpGet("{scheduleId}/history")]
    public async Task<ActionResult<List<ScheduleExecution>>> GetExecutionHistory(
        string scheduleId,
        [FromQuery] DateTime? startDate = null,
        [FromQuery] DateTime? endDate = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _scheduleService.GetExecutionHistoryAsync(
            scheduleId,
            startDate,
            endDate,
            cancellationToken);

        if (!result.Success || result.Data == null)
            return BadRequest(result.ErrorMessage);

        return Ok(result.Data);
    }
}
