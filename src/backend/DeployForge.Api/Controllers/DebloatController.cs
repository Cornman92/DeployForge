using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class DebloatController : ControllerBase
{
    private readonly IDebloatService _debloatService;
    private readonly ILogger<DebloatController> _logger;

    public DebloatController(
        IDebloatService debloatService,
        ILogger<DebloatController> logger)
    {
        _debloatService = debloatService;
        _logger = logger;
    }

    /// <summary>
    /// Get available debloat presets
    /// </summary>
    [HttpGet("presets")]
    public async Task<ActionResult<List<DebloatPreset>>> GetPresets(
        [FromQuery] DebloatLevel? level = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting debloat presets, level filter: {Level}", level);

        var result = await _debloatService.GetPresetsAsync(level, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get presets: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get a specific preset by ID
    /// </summary>
    [HttpGet("presets/{presetId}")]
    public async Task<ActionResult<DebloatPreset>> GetPreset(
        string presetId,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting debloat preset {PresetId}", presetId);

        var result = await _debloatService.GetPresetAsync(presetId, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get preset: {Error}", result.ErrorMessage);
            return NotFound(result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Analyze impact of applying a debloat preset
    /// </summary>
    [HttpPost("analyze")]
    public async Task<ActionResult<DebloatAnalysis>> AnalyzeImpact(
        [FromBody] ApplyDebloatRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Analyzing debloat impact for preset {PresetId} on {MountPath}",
            request.PresetId, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _debloatService.AnalyzeImpactAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to analyze impact: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Apply a debloat preset to an image
    /// </summary>
    [HttpPost("apply")]
    public async Task<ActionResult<DebloatResult>> ApplyPreset(
        [FromBody] ApplyDebloatRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Applying debloat preset {PresetId} to {MountPath} (DryRun: {DryRun})",
            request.PresetId, request.MountPath, request.DryRun);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (string.IsNullOrWhiteSpace(request.PresetId) && request.CustomPreset == null)
        {
            return BadRequest("Either PresetId or CustomPreset must be specified");
        }

        var result = await _debloatService.ApplyPresetAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to apply debloat preset: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
