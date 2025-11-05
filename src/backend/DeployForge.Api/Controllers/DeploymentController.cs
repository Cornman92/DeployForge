using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DeploymentController : ControllerBase
{
    private readonly IDeploymentService _deploymentService;
    private readonly ILogger<DeploymentController> _logger;

    public DeploymentController(
        IDeploymentService deploymentService,
        ILogger<DeploymentController> logger)
    {
        _deploymentService = deploymentService;
        _logger = logger;
    }

    /// <summary>
    /// Create bootable ISO image
    /// </summary>
    [HttpPost("iso")]
    public async Task<ActionResult<MediaCreationResult>> CreateISO(
        [FromBody] ISOCreationRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating ISO from {SourcePath} to {OutputPath}",
            request.SourcePath, request.OutputPath);

        if (string.IsNullOrWhiteSpace(request.SourcePath))
        {
            return BadRequest("Source path is required");
        }

        if (string.IsNullOrWhiteSpace(request.OutputPath))
        {
            return BadRequest("Output path is required");
        }

        var result = await _deploymentService.CreateISOAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to create ISO: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Create bootable USB drive
    /// </summary>
    [HttpPost("usb")]
    public async Task<ActionResult<MediaCreationResult>> CreateBootableUSB(
        [FromBody] BootableUSBRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating bootable USB on {DriveLetter} from {SourcePath}",
            request.DriveLetter, request.SourcePath);

        if (string.IsNullOrWhiteSpace(request.SourcePath))
        {
            return BadRequest("Source path is required");
        }

        if (string.IsNullOrWhiteSpace(request.DriveLetter))
        {
            return BadRequest("Drive letter is required");
        }

        var result = await _deploymentService.CreateBootableUSBAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to create bootable USB: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Generate autounattend.xml file
    /// </summary>
    [HttpPost("autounattend")]
    public async Task<ActionResult<string>> GenerateAutounattend(
        [FromBody] GenerateAutounattendRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Generating autounattend.xml at {OutputPath}", request.OutputPath);

        if (string.IsNullOrWhiteSpace(request.OutputPath))
        {
            return BadRequest("Output path is required");
        }

        if (request.Config == null)
        {
            return BadRequest("Configuration is required");
        }

        var result = await _deploymentService.GenerateAutounattendAsync(
            request.Config, request.OutputPath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to generate autounattend.xml: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { path = result.Data, message = "autounattend.xml generated successfully" });
    }

    /// <summary>
    /// Get available removable drives
    /// </summary>
    [HttpGet("drives")]
    public async Task<ActionResult<List<Core.Interfaces.DriveInfo>>> GetRemovableDrives(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting removable drives");

        var result = await _deploymentService.GetRemovableDrivesAsync(cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get removable drives: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}

/// <summary>
/// Request to generate autounattend.xml
/// </summary>
public class GenerateAutounattendRequest
{
    public AutounattendConfig Config { get; set; } = new();
    public string OutputPath { get; set; } = string.Empty;
}
