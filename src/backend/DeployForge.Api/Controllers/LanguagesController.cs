using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class LanguagesController : ControllerBase
{
    private readonly ILanguageService _languageService;
    private readonly ILogger<LanguagesController> _logger;

    public LanguagesController(
        ILanguageService languageService,
        ILogger<LanguagesController> logger)
    {
        _languageService = languageService;
        _logger = logger;
    }

    /// <summary>
    /// Get installed language packs
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<LanguagePackInfo>>> GetLanguagePacks(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting language packs from {MountPath}", mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _languageService.GetLanguagePacksAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get language packs: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Add language packs
    /// </summary>
    [HttpPost("add")]
    public async Task<ActionResult<LanguageOperationResult>> AddLanguagePacks(
        [FromBody] AddLanguagePackRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Adding {Count} language packs to {MountPath}",
            request.LanguagePackPaths.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.LanguagePackPaths == null || !request.LanguagePackPaths.Any())
        {
            return BadRequest("At least one language pack path is required");
        }

        var result = await _languageService.AddLanguagePacksAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to add language packs: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Remove language packs
    /// </summary>
    [HttpPost("remove")]
    public async Task<ActionResult<LanguageOperationResult>> RemoveLanguagePacks(
        [FromBody] RemoveLanguagePackRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Removing {Count} language packs from {MountPath}",
            request.LanguageTags.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.LanguageTags == null || !request.LanguageTags.Any())
        {
            return BadRequest("At least one language tag is required");
        }

        var result = await _languageService.RemoveLanguagePacksAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to remove language packs: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Set default languages
    /// </summary>
    [HttpPost("set-defaults")]
    public async Task<ActionResult> SetDefaultLanguages(
        [FromBody] SetDefaultLanguagesRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Setting default languages for {MountPath}", request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _languageService.SetDefaultLanguagesAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to set default languages: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Default languages set successfully" });
    }

    /// <summary>
    /// Get default language settings
    /// </summary>
    [HttpGet("defaults")]
    public async Task<ActionResult<SetDefaultLanguagesRequest>> GetDefaultLanguages(
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting default languages from {MountPath}", mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _languageService.GetDefaultLanguagesAsync(mountPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get default languages: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}
