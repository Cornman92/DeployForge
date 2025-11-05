using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DriversController : ControllerBase
{
    private readonly IDriverService _driverService;
    private readonly ILogger<DriversController> _logger;

    public DriversController(
        IDriverService driverService,
        ILogger<DriversController> logger)
    {
        _driverService = driverService;
        _logger = logger;
    }

    /// <summary>
    /// Get all drivers from a mounted image
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<DriverInfo>>> GetDrivers(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting drivers from {MountPath}", mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _driverService.GetDriversAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get drivers: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get detailed information about a specific driver
    /// </summary>
    [HttpGet("{driverPath}")]
    public async Task<ActionResult<DriverInfo>> GetDriverInfo(
        string driverPath,
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting driver info for {DriverPath} from {MountPath}", driverPath, mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (string.IsNullOrWhiteSpace(driverPath))
        {
            return BadRequest("Driver path is required");
        }

        var result = await _driverService.GetDriverInfoAsync(mountPath, driverPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get driver info: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Add drivers to an image
    /// </summary>
    [HttpPost("add")]
    public async Task<ActionResult<DriverOperationResult>> AddDrivers(
        [FromBody] DriverOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Adding {Count} drivers to {MountPath}",
            request.Drivers.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.Drivers == null || request.Drivers.Count == 0)
        {
            return BadRequest("At least one driver path is required");
        }

        var result = await _driverService.AddDriversAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to add drivers: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Remove drivers from an image
    /// </summary>
    [HttpPost("remove")]
    public async Task<ActionResult<DriverOperationResult>> RemoveDrivers(
        [FromBody] DriverOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Removing {Count} drivers from {MountPath}",
            request.Drivers.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.Drivers == null || request.Drivers.Count == 0)
        {
            return BadRequest("At least one driver identifier is required");
        }

        var result = await _driverService.RemoveDriversAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to remove drivers: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Analyze driver conflicts before adding
    /// </summary>
    [HttpPost("analyze-conflicts")]
    public async Task<ActionResult<DriverConflictAnalysis>> AnalyzeConflicts(
        [FromBody] DriverConflictAnalysisRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Analyzing conflicts for {Count} drivers", request.NewDriverPaths.Count);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.NewDriverPaths == null || request.NewDriverPaths.Count == 0)
        {
            return BadRequest("At least one new driver path is required");
        }

        var result = await _driverService.AnalyzeConflictsAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to analyze conflicts: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
