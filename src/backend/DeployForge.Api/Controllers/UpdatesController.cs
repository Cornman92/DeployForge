using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class UpdatesController : ControllerBase
{
    private readonly IUpdateService _updateService;
    private readonly ILogger<UpdatesController> _logger;

    public UpdatesController(
        IUpdateService updateService,
        ILogger<UpdatesController> logger)
    {
        _updateService = updateService;
        _logger = logger;
    }

    /// <summary>
    /// Get installed updates from a mounted image
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<UpdateInfo>>> GetInstalledUpdates(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting installed updates from {MountPath}", mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _updateService.GetInstalledUpdatesAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get installed updates: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Install updates to an image
    /// </summary>
    [HttpPost("install")]
    public async Task<ActionResult<UpdateOperationResult>> InstallUpdates(
        [FromBody] UpdateOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Installing {Count} updates to {MountPath}",
            request.UpdatePaths.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.UpdatePaths == null || request.UpdatePaths.Count == 0)
        {
            return BadRequest("At least one update path is required");
        }

        var result = await _updateService.InstallUpdatesAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to install updates: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Remove updates from an image
    /// </summary>
    [HttpPost("remove")]
    public async Task<ActionResult<UpdateOperationResult>> RemoveUpdates(
        [FromBody] RemoveUpdatesRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Removing {Count} updates from {MountPath}",
            request.UpdateNames.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.UpdateNames == null || request.UpdateNames.Count == 0)
        {
            return BadRequest("At least one update name is required");
        }

        var result = await _updateService.RemoveUpdatesAsync(
            request.MountPath, request.UpdateNames, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to remove updates: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Analyze update compatibility before installation
    /// </summary>
    [HttpPost("analyze-compatibility")]
    public async Task<ActionResult<UpdateCompatibilityResult>> AnalyzeCompatibility(
        [FromBody] UpdateCompatibilityRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Analyzing compatibility for {Count} updates", request.UpdatePaths.Count);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.UpdatePaths == null || request.UpdatePaths.Count == 0)
        {
            return BadRequest("At least one update path is required");
        }

        var result = await _updateService.AnalyzeCompatibilityAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to analyze compatibility: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Cleanup superseded components after updates
    /// </summary>
    [HttpPost("cleanup")]
    public async Task<ActionResult> CleanupSuperseded(
        [FromBody] CleanupRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Cleaning up superseded components in {MountPath}", request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _updateService.CleanupSupersededAsync(request.MountPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to cleanup superseded components: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Cleanup completed successfully" });
    }
}

/// <summary>
/// Request to remove updates
/// </summary>
public class RemoveUpdatesRequest
{
    public string MountPath { get; set; } = string.Empty;
    public List<string> UpdateNames { get; set; } = new();
}

/// <summary>
/// Request to cleanup superseded components
/// </summary>
public class CleanupRequest
{
    public string MountPath { get; set; } = string.Empty;
}
