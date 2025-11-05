using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for converting between image formats
/// </summary>
public interface IImageConversionService
{
    /// <summary>
    /// Convert an image from one format to another
    /// </summary>
    /// <param name="request">Conversion request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Conversion result</returns>
    Task<OperationResult<ImageConversionResult>> ConvertImageAsync(
        ConvertImageRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Extract ISO contents to a directory
    /// </summary>
    /// <param name="request">Extraction request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Extraction result</returns>
    Task<OperationResult<ISOExtractionResult>> ExtractISOAsync(
        ExtractISORequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Check if a conversion between formats is supported
    /// </summary>
    /// <param name="source">Source format</param>
    /// <param name="target">Target format</param>
    /// <returns>True if supported</returns>
    bool IsConversionSupported(ImageFormat source, ImageFormat target);

    /// <summary>
    /// Get estimated conversion time
    /// </summary>
    /// <param name="sourceSize">Source image size in bytes</param>
    /// <param name="source">Source format</param>
    /// <param name="target">Target format</param>
    /// <returns>Estimated duration</returns>
    TimeSpan EstimateConversionTime(long sourceSize, ImageFormat source, ImageFormat target);
}
