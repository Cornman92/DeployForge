using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ComponentsController : ControllerBase
{
    private readonly IComponentService _componentService;
    private readonly ILogger<ComponentsController> _logger;

    public ComponentsController(
        IComponentService componentService,
        ILogger<ComponentsController> logger)
    {
        _componentService = componentService;
        _logger = logger;
    }

    /// <summary>
    /// Get all components from a mounted image
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<ComponentInfo>>> GetComponents(
        [FromQuery] string mountPath,
        [FromQuery] ComponentType? type = null,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting components from {MountPath}, type filter: {Type}", mountPath, type);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _componentService.GetComponentsAsync(mountPath, type, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get components: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get detailed information about a specific component
    /// </summary>
    [HttpGet("{componentId}")]
    public async Task<ActionResult<ComponentInfo>> GetComponentInfo(
        string componentId,
        [FromQuery] string mountPath,
        [FromQuery] ComponentType type,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting component info for {ComponentId} from {MountPath}", componentId, mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (string.IsNullOrWhiteSpace(componentId))
        {
            return BadRequest("Component ID is required");
        }

        var result = await _componentService.GetComponentInfoAsync(mountPath, componentId, type, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get component info: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get components by category
    /// </summary>
    [HttpGet("category/{category}")]
    public async Task<ActionResult<List<ComponentInfo>>> GetComponentsByCategory(
        string category,
        [FromQuery] string mountPath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting components in category {Category} from {MountPath}", category, mountPath);

        if (string.IsNullOrWhiteSpace(mountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (string.IsNullOrWhiteSpace(category))
        {
            return BadRequest("Category is required");
        }

        var result = await _componentService.GetComponentsByCategoryAsync(mountPath, category, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get components by category: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Remove components from an image
    /// </summary>
    [HttpPost("remove")]
    public async Task<ActionResult<ComponentOperationResult>> RemoveComponents(
        [FromBody] ComponentOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Removing {Count} components from {MountPath}",
            request.ComponentIds.Count, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.ComponentIds == null || request.ComponentIds.Count == 0)
        {
            return BadRequest("At least one component ID is required");
        }

        var result = await _componentService.RemoveComponentsAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to remove components: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Add packages to an image
    /// </summary>
    [HttpPost("add")]
    public async Task<ActionResult<ComponentOperationResult>> AddComponents(
        [FromBody] AddComponentsRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Adding {Count} packages to {MountPath}",
            request.PackagePaths.Count, request.Request.MountPath);

        if (string.IsNullOrWhiteSpace(request.Request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.PackagePaths == null || request.PackagePaths.Count == 0)
        {
            return BadRequest("At least one package path is required");
        }

        var result = await _componentService.AddComponentsAsync(
            request.Request, request.PackagePaths, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to add components: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Enable or disable features
    /// </summary>
    [HttpPost("toggle")]
    public async Task<ActionResult<ComponentOperationResult>> ToggleFeatures(
        [FromBody] ComponentOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Toggling {Count} features in {MountPath} (operation: {Operation})",
            request.ComponentIds.Count, request.MountPath, request.Operation);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.ComponentIds == null || request.ComponentIds.Count == 0)
        {
            return BadRequest("At least one component ID is required");
        }

        if (request.Operation != ComponentOperation.Enable && request.Operation != ComponentOperation.Disable)
        {
            return BadRequest("Operation must be Enable or Disable");
        }

        var result = await _componentService.ToggleFeaturesAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to toggle features: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Analyze component dependencies
    /// </summary>
    [HttpPost("analyze-dependencies")]
    public async Task<ActionResult<ComponentDependencyGraph>> AnalyzeDependencies(
        [FromBody] AnalyzeDependenciesRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Analyzing dependencies for {Count} components", request.ComponentIds.Count);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        if (request.ComponentIds == null || request.ComponentIds.Count == 0)
        {
            return BadRequest("At least one component ID is required");
        }

        var result = await _componentService.AnalyzeDependenciesAsync(
            request.MountPath, request.ComponentIds, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to analyze dependencies: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}

/// <summary>
/// Request to add components
/// </summary>
public class AddComponentsRequest
{
    public ComponentOperationRequest Request { get; set; } = new();
    public List<string> PackagePaths { get; set; } = new();
}

/// <summary>
/// Request to analyze dependencies
/// </summary>
public class AnalyzeDependenciesRequest
{
    public string MountPath { get; set; } = string.Empty;
    public List<string> ComponentIds { get; set; } = new();
}
