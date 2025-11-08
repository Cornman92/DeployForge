using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class ImagesController : ControllerBase
{
    private readonly IImageService _imageService;
    private readonly ILogger<ImagesController> _logger;

    public ImagesController(
        IImageService imageService,
        ILogger<ImagesController> logger)
    {
        _imageService = imageService;
        _logger = logger;
    }

    /// <summary>
    /// Get information about an image file
    /// </summary>
    [HttpGet("info")]
    public async Task<ActionResult<List<ImageInfo>>> GetImageInfo(
        [FromQuery] string imagePath,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting image info for {ImagePath}", imagePath);

        if (string.IsNullOrWhiteSpace(imagePath))
        {
            return BadRequest("Image path is required");
        }

        var result = await _imageService.GetImageInfoAsync(imagePath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get image info: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Mount an image
    /// </summary>
    [HttpPost("mount")]
    public async Task<ActionResult<MountOperationResult>> MountImage(
        [FromBody] MountImageRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Mounting image {ImagePath} to {MountPath}",
            request.ImagePath, request.MountPath);

        if (string.IsNullOrWhiteSpace(request.ImagePath))
        {
            return BadRequest("Image path is required");
        }

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _imageService.MountImageAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to mount image: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Unmount an image
    /// </summary>
    [HttpPost("unmount")]
    public async Task<ActionResult<MountOperationResult>> UnmountImage(
        [FromBody] UnmountImageRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Unmounting image from {MountPath}", request.MountPath);

        if (string.IsNullOrWhiteSpace(request.MountPath))
        {
            return BadRequest("Mount path is required");
        }

        var result = await _imageService.UnmountImageAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to unmount image: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Get all currently mounted images
    /// </summary>
    [HttpGet("mounted")]
    public async Task<ActionResult<List<MountedImageInfo>>> GetMountedImages(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Getting mounted images");

        var result = await _imageService.GetMountedImagesAsync(cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to get mounted images: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Cleanup orphaned mount points
    /// </summary>
    [HttpPost("cleanup")]
    public async Task<ActionResult<int>> CleanupMountPoints(
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Cleaning up mount points");

        var result = await _imageService.CleanupMountPointsAsync(cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to cleanup mount points: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(new { cleanedCount = result.Data, message = $"Cleaned up {result.Data} mount points" });
    }

    /// <summary>
    /// Export an image to a different format
    /// </summary>
    [HttpPost("export")]
    public async Task<ActionResult<ExportImageResult>> ExportImage(
        [FromBody] ExportImageRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Exporting image from {Source} to {Destination}",
            request.SourcePath, request.DestinationPath);

        if (string.IsNullOrWhiteSpace(request.SourcePath))
        {
            return BadRequest("Source path is required");
        }

        if (string.IsNullOrWhiteSpace(request.DestinationPath))
        {
            return BadRequest("Destination path is required");
        }

        var result = await _imageService.ExportImageAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to export image: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Optimize an image (reduce size)
    /// </summary>
    [HttpPost("optimize")]
    public async Task<ActionResult<OptimizationResult>> OptimizeImage(
        [FromBody] OptimizeImageRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Optimizing image {ImagePath}", request.ImagePath);

        if (string.IsNullOrWhiteSpace(request.ImagePath))
        {
            return BadRequest("Image path is required");
        }

        var result = await _imageService.OptimizeImageAsync(request.ImagePath, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to optimize image: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }
}

/// <summary>
/// Request to optimize an image
/// </summary>
public class OptimizeImageRequest
{
    public string ImagePath { get; set; } = string.Empty;
}
