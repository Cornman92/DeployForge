using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ImageConversionController : ControllerBase
{
    private readonly IImageConversionService _conversionService;
    private readonly ILogger<ImageConversionController> _logger;

    public ImageConversionController(
        IImageConversionService conversionService,
        ILogger<ImageConversionController> logger)
    {
        _conversionService = conversionService;
        _logger = logger;
    }

    /// <summary>
    /// Convert an image from one format to another
    /// </summary>
    [HttpPost("convert")]
    public async Task<ActionResult<ImageConversionResult>> ConvertImage(
        [FromBody] ConvertImageRequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Converting image from {Source} to {Destination}",
            request.SourcePath, request.DestinationPath);

        if (string.IsNullOrWhiteSpace(request.SourcePath))
        {
            return BadRequest("Source path is required");
        }

        if (string.IsNullOrWhiteSpace(request.DestinationPath))
        {
            return BadRequest("Destination path is required");
        }

        var result = await _conversionService.ConvertImageAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to convert image: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Extract ISO contents to a directory
    /// </summary>
    [HttpPost("extract-iso")]
    public async Task<ActionResult<ISOExtractionResult>> ExtractISO(
        [FromBody] ExtractISORequest request,
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Extracting ISO {ISO} to {Destination}",
            request.ISOPath, request.DestinationPath);

        if (string.IsNullOrWhiteSpace(request.ISOPath))
        {
            return BadRequest("ISO path is required");
        }

        if (string.IsNullOrWhiteSpace(request.DestinationPath))
        {
            return BadRequest("Destination path is required");
        }

        var result = await _conversionService.ExtractISOAsync(request, cancellationToken);

        if (!result.Success)
        {
            _logger.LogError("Failed to extract ISO: {Error}", result.ErrorMessage);
            return StatusCode(500, result.ErrorMessage);
        }

        return Ok(result.Data);
    }

    /// <summary>
    /// Check if a conversion is supported
    /// </summary>
    [HttpGet("check-support")]
    public ActionResult<ConversionSupportResponse> CheckConversionSupport(
        [FromQuery] ImageFormat source,
        [FromQuery] ImageFormat target)
    {
        _logger.LogInformation("Checking conversion support from {Source} to {Target}", source, target);

        var isSupported = _conversionService.IsConversionSupported(source, target);
        var complexity = ImageConversionSupport.GetConversionComplexity(source, target);

        var response = new ConversionSupportResponse
        {
            Source = source,
            Target = target,
            IsSupported = isSupported,
            Complexity = complexity,
            Message = isSupported
                ? $"Conversion from {source} to {target} is supported ({complexity} complexity)"
                : $"Conversion from {source} to {target} is not supported"
        };

        return Ok(response);
    }

    /// <summary>
    /// Get estimated conversion time
    /// </summary>
    [HttpGet("estimate-time")]
    public ActionResult<ConversionTimeEstimate> EstimateConversionTime(
        [FromQuery] long sourceSize,
        [FromQuery] ImageFormat source,
        [FromQuery] ImageFormat target)
    {
        _logger.LogInformation("Estimating conversion time for {SourceSize} bytes from {Source} to {Target}",
            sourceSize, source, target);

        var estimatedTime = _conversionService.EstimateConversionTime(sourceSize, source, target);
        var complexity = ImageConversionSupport.GetConversionComplexity(source, target);

        var response = new ConversionTimeEstimate
        {
            SourceSize = sourceSize,
            Source = source,
            Target = target,
            EstimatedDuration = estimatedTime,
            Complexity = complexity
        };

        return Ok(response);
    }

    /// <summary>
    /// Get all supported conversions
    /// </summary>
    [HttpGet("supported-conversions")]
    public ActionResult<List<ConversionPath>> GetSupportedConversions()
    {
        _logger.LogInformation("Getting all supported conversions");

        var formats = Enum.GetValues<ImageFormat>();
        var conversions = new List<ConversionPath>();

        foreach (var source in formats)
        {
            foreach (var target in formats)
            {
                if (ImageConversionSupport.IsConversionSupported(source, target))
                {
                    conversions.Add(new ConversionPath
                    {
                        Source = source,
                        Target = target,
                        Complexity = ImageConversionSupport.GetConversionComplexity(source, target)
                    });
                }
            }
        }

        return Ok(conversions);
    }
}

/// <summary>
/// Response for conversion support check
/// </summary>
public class ConversionSupportResponse
{
    public ImageFormat Source { get; set; }
    public ImageFormat Target { get; set; }
    public bool IsSupported { get; set; }
    public ConversionComplexity Complexity { get; set; }
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Response for conversion time estimate
/// </summary>
public class ConversionTimeEstimate
{
    public long SourceSize { get; set; }
    public ImageFormat Source { get; set; }
    public ImageFormat Target { get; set; }
    public TimeSpan EstimatedDuration { get; set; }
    public ConversionComplexity Complexity { get; set; }
}

/// <summary>
/// Supported conversion path
/// </summary>
public class ConversionPath
{
    public ImageFormat Source { get; set; }
    public ImageFormat Target { get; set; }
    public ConversionComplexity Complexity { get; set; }
}
