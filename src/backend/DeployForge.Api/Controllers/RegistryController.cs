using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/[controller]")]
public class RegistryController : ControllerBase
{
    private readonly IRegistryService _registryService;
    private readonly ILogger<RegistryController> _logger;

    public RegistryController(
        IRegistryService registryService,
        ILogger<RegistryController> logger)
    {
        _registryService = registryService;
        _logger = logger;
    }

    /// <summary>
    /// Load a registry hive from a mounted image
    /// </summary>
    [HttpPost("load-hive")]
    public async Task<ActionResult> LoadHive(
        [FromBody] LoadHiveRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Loading hive {HiveType} from {MountPath}", request.HiveType, request.MountPath);

        var result = await _registryService.LoadHiveAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to load hive: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Hive loaded successfully", mountPoint = request.MountPoint });
    }

    /// <summary>
    /// Unload a previously loaded registry hive
    /// </summary>
    [HttpPost("unload-hive")]
    public async Task<ActionResult> UnloadHive(
        [FromBody] UnloadHiveRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Unloading hive from {MountPoint}", request.MountPoint);

        var result = await _registryService.UnloadHiveAsync(request.MountPoint, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to unload hive: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Hive unloaded successfully" });
    }

    /// <summary>
    /// Get registry key information
    /// </summary>
    [HttpGet("keys")]
    public async Task<ActionResult<RegistryKeyInfo>> GetKeyInfo(
        [FromQuery] string keyPath,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(keyPath))
        {
            return BadRequest("Key path is required");
        }

        var result = await _registryService.GetKeyInfoAsync(keyPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get key info: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get all values in a registry key
    /// </summary>
    [HttpGet("values")]
    public async Task<ActionResult<List<RegistryValueInfo>>> GetValues(
        [FromQuery] string keyPath,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(keyPath))
        {
            return BadRequest("Key path is required");
        }

        var result = await _registryService.GetValuesAsync(keyPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get values: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get subkeys of a registry key
    /// </summary>
    [HttpGet("subkeys")]
    public async Task<ActionResult<List<string>>> GetSubKeys(
        [FromQuery] string keyPath,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(keyPath))
        {
            return BadRequest("Key path is required");
        }

        var result = await _registryService.GetSubKeysAsync(keyPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get subkeys: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Set a registry value
    /// </summary>
    [HttpPost("values")]
    public async Task<ActionResult> SetValue(
        [FromBody] SetRegistryValueRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Setting registry value {KeyPath}\\{ValueName}",
            request.KeyPath, request.ValueName);

        var result = await _registryService.SetValueAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to set value: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Value set successfully" });
    }

    /// <summary>
    /// Delete a registry key or value
    /// </summary>
    [HttpDelete]
    public async Task<ActionResult> Delete(
        [FromBody] DeleteRegistryRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Deleting registry {Type} {KeyPath}",
            string.IsNullOrEmpty(request.ValueName) ? "key" : "value",
            request.KeyPath);

        var result = await _registryService.DeleteAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to delete: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Deleted successfully" });
    }

    /// <summary>
    /// Import a .reg file
    /// </summary>
    [HttpPost("import")]
    public async Task<ActionResult> ImportRegFile(
        [FromBody] ImportRegFileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Importing .reg file {RegFilePath}", request.RegFilePath);

        var result = await _registryService.ImportRegFileAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to import .reg file: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Imported successfully" });
    }

    /// <summary>
    /// Export registry keys to a .reg file
    /// </summary>
    [HttpPost("export")]
    public async Task<ActionResult> ExportRegFile(
        [FromBody] ExportRegFileRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Exporting registry keys to {OutputPath}", request.OutputPath);

        var result = await _registryService.ExportRegFileAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to export .reg file: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Exported successfully", path = request.OutputPath });
    }

    /// <summary>
    /// Apply a registry tweak preset
    /// </summary>
    [HttpPost("apply-preset")]
    public async Task<ActionResult> ApplyPreset(
        [FromBody] ApplyPresetRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Applying preset to {MountPath}", request.MountPath);

        var result = await _registryService.ApplyTweakPresetAsync(
            request.MountPath, request.Preset, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to apply preset: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { message = "Preset applied successfully" });
    }

    /// <summary>
    /// Get available tweak presets
    /// </summary>
    [HttpGet("presets")]
    public async Task<ActionResult<List<RegistryTweakPreset>>> GetPresets(
        [FromQuery] string? category = null,
        CancellationToken cancellationToken = default)
    {
        var result = await _registryService.GetTweakPresetsAsync(category, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get presets: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}

/// <summary>
/// Request to unload a hive
/// </summary>
public class UnloadHiveRequest
{
    public string MountPoint { get; set; } = string.Empty;
}

/// <summary>
/// Request to apply a preset
/// </summary>
public class ApplyPresetRequest
{
    public string MountPath { get; set; } = string.Empty;
    public RegistryTweakPreset Preset { get; set; } = new();
}
