using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for image operations (mount, unmount, info)
/// </summary>
public interface IImageService
{
    /// <summary>
    /// Get information about an image file
    /// </summary>
    /// <param name="imagePath">Path to image file</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Image information</returns>
    Task<OperationResult<List<ImageInfo>>> GetImageInfoAsync(
        string imagePath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Mount an image
    /// </summary>
    /// <param name="request">Mount request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Mount operation result</returns>
    Task<OperationResult<MountOperationResult>> MountImageAsync(
        MountImageRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Unmount an image
    /// </summary>
    /// <param name="request">Unmount request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Unmount operation result</returns>
    Task<OperationResult<MountOperationResult>> UnmountImageAsync(
        UnmountImageRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get all currently mounted images
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of mounted images</returns>
    Task<OperationResult<List<MountedImageInfo>>> GetMountedImagesAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Cleanup orphaned mount points
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Cleanup result</returns>
    Task<OperationResult<int>> CleanupMountPointsAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Export an image to a different format
    /// </summary>
    /// <param name="request">Export request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Export result</returns>
    Task<OperationResult<ExportImageResult>> ExportImageAsync(
        ExportImageRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Optimize an image (reduce size)
    /// </summary>
    /// <param name="imagePath">Image path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Optimization result</returns>
    Task<OperationResult<OptimizationResult>> OptimizeImageAsync(
        string imagePath,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Request to export an image
/// </summary>
public class ExportImageRequest
{
    /// <summary>
    /// Source image path
    /// </summary>
    public string SourcePath { get; set; } = string.Empty;

    /// <summary>
    /// Source image index
    /// </summary>
    public int SourceIndex { get; set; } = 1;

    /// <summary>
    /// Destination path
    /// </summary>
    public string DestinationPath { get; set; } = string.Empty;

    /// <summary>
    /// Destination format
    /// </summary>
    public ImageFormat DestinationFormat { get; set; }

    /// <summary>
    /// Compression type
    /// </summary>
    public CompressionType Compression { get; set; } = CompressionType.Maximum;

    /// <summary>
    /// Check integrity
    /// </summary>
    public bool CheckIntegrity { get; set; } = true;

    /// <summary>
    /// Verify export
    /// </summary>
    public bool Verify { get; set; } = true;
}

/// <summary>
/// Compression types
/// </summary>
public enum CompressionType
{
    None,
    Fast,
    Maximum,
    Recovery
}

/// <summary>
/// Export result
/// </summary>
public class ExportImageResult
{
    public bool Success { get; set; }
    public string OutputPath { get; set; } = string.Empty;
    public long OriginalSize { get; set; }
    public long NewSize { get; set; }
    public TimeSpan Duration { get; set; }
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Optimization result
/// </summary>
public class OptimizationResult
{
    public bool Success { get; set; }
    public long OriginalSize { get; set; }
    public long OptimizedSize { get; set; }
    public long SpaceSaved { get; set; }
    public double CompressionRatio { get; set; }
    public TimeSpan Duration { get; set; }
    public string Message { get; set; } = string.Empty;
}
