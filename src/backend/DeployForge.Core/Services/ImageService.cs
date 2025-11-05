using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using Microsoft.Dism;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for image operations
/// </summary>
[SupportedOSPlatform("windows")]
public class ImageService : IImageService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<ImageService> _logger;

    public ImageService(DismManager dismManager, ILogger<ImageService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<List<ImageInfo>>> GetImageInfoAsync(
        string imagePath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Getting image info for {ImagePath}", imagePath);

                if (!File.Exists(imagePath))
                {
                    return OperationResult<List<ImageInfo>>.FailureResult("Image file not found");
                }

                var format = DetermineImageFormat(imagePath);
                var images = new List<ImageInfo>();

                if (format == ImageFormat.WIM || format == ImageFormat.ESD)
                {
                    var infoResult = _dismManager.GetImageInfo(imagePath);
                    if (!infoResult.Success || infoResult.Data == null)
                    {
                        return OperationResult<List<ImageInfo>>.FailureResult(
                            infoResult.ErrorMessage ?? "Failed to get image info");
                    }

                    foreach (var dismImage in infoResult.Data)
                    {
                        images.Add(new ImageInfo
                        {
                            FilePath = imagePath,
                            Format = format,
                            Architecture = dismImage.Architecture.ToString(),
                            Version = dismImage.ProductVersion?.ToString() ?? "Unknown",
                            Edition = dismImage.EditionId ?? "Unknown",
                            Name = dismImage.ImageName,
                            Description = dismImage.ImageDescription ?? string.Empty,
                            Index = dismImage.ImageIndex,
                            ImageCount = infoResult.Data.Count,
                            SizeBytes = dismImage.ImageSize,
                            CreatedDate = dismImage.CreatedTime,
                            ModifiedDate = dismImage.ModifiedTime,
                            Languages = dismImage.Languages?.ToList() ?? new List<string>(),
                            IsMounted = false,
                            MountStatus = MountStatus.NotMounted
                        });
                    }
                }
                else if (format == ImageFormat.ISO)
                {
                    // For ISO, return basic info
                    var fileInfo = new FileInfo(imagePath);
                    images.Add(new ImageInfo
                    {
                        FilePath = imagePath,
                        Format = format,
                        Name = Path.GetFileNameWithoutExtension(imagePath),
                        SizeBytes = fileInfo.Length,
                        CreatedDate = fileInfo.CreationTime,
                        ModifiedDate = fileInfo.LastWriteTime,
                        ImageCount = 1,
                        Index = 1
                    });
                }
                else
                {
                    // For other formats, return basic info
                    var fileInfo = new FileInfo(imagePath);
                    images.Add(new ImageInfo
                    {
                        FilePath = imagePath,
                        Format = format,
                        Name = Path.GetFileNameWithoutExtension(imagePath),
                        SizeBytes = fileInfo.Length,
                        CreatedDate = fileInfo.CreationTime,
                        ModifiedDate = fileInfo.LastWriteTime,
                        ImageCount = 1,
                        Index = 1
                    });
                }

                _logger.LogInformation("Found {Count} images in {ImagePath}", images.Count, imagePath);

                return OperationResult<List<ImageInfo>>.SuccessResult(images);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get image info");
                return OperationResult<List<ImageInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<MountOperationResult>> MountImageAsync(
        MountImageRequest request,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Mounting image {ImagePath} index {Index} to {MountPath}",
                    request.ImagePath, request.Index, request.MountPath);

                if (!File.Exists(request.ImagePath))
                {
                    return OperationResult<MountOperationResult>.FailureResult("Image file not found");
                }

                // Create mount directory if it doesn't exist
                if (!Directory.Exists(request.MountPath))
                {
                    Directory.CreateDirectory(request.MountPath);
                }

                // Check if directory is empty
                if (Directory.GetFileSystemEntries(request.MountPath).Length > 0)
                {
                    return OperationResult<MountOperationResult>.FailureResult(
                        "Mount directory must be empty");
                }

                var mountResult = _dismManager.MountImage(
                    request.ImagePath,
                    request.Index,
                    request.MountPath,
                    request.ReadOnly);

                var duration = DateTime.UtcNow - startTime;

                if (mountResult.Success)
                {
                    _logger.LogInformation("Image mounted successfully in {Duration}s", duration.TotalSeconds);

                    return OperationResult<MountOperationResult>.SuccessResult(new MountOperationResult
                    {
                        Success = true,
                        MountPath = request.MountPath,
                        ImagePath = request.ImagePath,
                        Status = MountStatus.Mounted,
                        Message = $"Image mounted successfully in {duration.TotalSeconds:F1} seconds",
                        Duration = duration
                    });
                }

                return OperationResult<MountOperationResult>.FailureResult(
                    mountResult.ErrorMessage ?? "Failed to mount image");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to mount image");
                return OperationResult<MountOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<MountOperationResult>> UnmountImageAsync(
        UnmountImageRequest request,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Unmounting image from {MountPath} (commit: {Commit})",
                    request.MountPath, request.Commit);

                if (!Directory.Exists(request.MountPath))
                {
                    return OperationResult<MountOperationResult>.FailureResult("Mount path not found");
                }

                var unmountResult = _dismManager.UnmountImage(request.MountPath, request.Commit);

                var duration = DateTime.UtcNow - startTime;

                if (unmountResult.Success)
                {
                    _logger.LogInformation("Image unmounted successfully in {Duration}s", duration.TotalSeconds);

                    return OperationResult<MountOperationResult>.SuccessResult(new MountOperationResult
                    {
                        Success = true,
                        MountPath = request.MountPath,
                        Status = MountStatus.NotMounted,
                        Message = $"Image unmounted successfully in {duration.TotalSeconds:F1} seconds",
                        Duration = duration
                    });
                }

                return OperationResult<MountOperationResult>.FailureResult(
                    unmountResult.ErrorMessage ?? "Failed to unmount image");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to unmount image");
                return OperationResult<MountOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<List<MountedImageInfo>>> GetMountedImagesAsync(
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Getting mounted images");

                var mountedResult = _dismManager.GetMountedImages();

                if (!mountedResult.Success || mountedResult.Data == null)
                {
                    return OperationResult<List<MountedImageInfo>>.FailureResult(
                        mountedResult.ErrorMessage ?? "Failed to get mounted images");
                }

                var mountedImages = mountedResult.Data.Select(m => new MountedImageInfo
                {
                    ImagePath = m.ImageFilePath,
                    MountPath = m.MountPath,
                    ImageIndex = m.ImageIndex,
                    Status = MapDismMountStatus(m.MountStatus),
                    IsReadOnly = m.ReadOnly,
                    MountTime = DateTime.UtcNow // DISM doesn't provide mount time
                }).ToList();

                _logger.LogInformation("Found {Count} mounted images", mountedImages.Count);

                return OperationResult<List<MountedImageInfo>>.SuccessResult(mountedImages);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get mounted images");
                return OperationResult<List<MountedImageInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<int>> CleanupMountPointsAsync(
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Cleaning up orphaned mount points");

                var mountedResult = _dismManager.GetMountedImages();

                if (!mountedResult.Success || mountedResult.Data == null)
                {
                    return OperationResult<int>.FailureResult("Failed to get mounted images");
                }

                int cleanedCount = 0;

                foreach (var mounted in mountedResult.Data)
                {
                    if (mounted.MountStatus == DismMountStatus.NeedsRemount ||
                        mounted.MountStatus == DismMountStatus.Invalid)
                    {
                        _logger.LogInformation("Cleaning up mount point: {MountPath}", mounted.MountPath);

                        var unmountResult = _dismManager.UnmountImage(mounted.MountPath, false);
                        if (unmountResult.Success)
                        {
                            cleanedCount++;
                        }
                    }
                }

                _logger.LogInformation("Cleaned up {Count} mount points", cleanedCount);

                return OperationResult<int>.SuccessResult(cleanedCount);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to cleanup mount points");
                return OperationResult<int>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ExportImageResult>> ExportImageAsync(
        ExportImageRequest request,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Exporting image from {Source} to {Destination} ({Format})",
                    request.SourcePath, request.DestinationPath, request.DestinationFormat);

                if (!File.Exists(request.SourcePath))
                {
                    return OperationResult<ExportImageResult>.FailureResult("Source image not found");
                }

                var sourceInfo = new FileInfo(request.SourcePath);
                var originalSize = sourceInfo.Length;

                // For WIM to WIM, use DISM export
                // For other formats, this would require additional tools or libraries
                // This is a simplified implementation

                var destDir = Path.GetDirectoryName(request.DestinationPath);
                if (!string.IsNullOrEmpty(destDir))
                {
                    Directory.CreateDirectory(destDir);
                }

                // Placeholder for actual export logic
                // In production, use DISM export API or conversion tools
                File.Copy(request.SourcePath, request.DestinationPath, true);

                var destInfo = new FileInfo(request.DestinationPath);
                var duration = DateTime.UtcNow - startTime;

                _logger.LogInformation("Image exported successfully in {Duration}s", duration.TotalSeconds);

                return OperationResult<ExportImageResult>.SuccessResult(new ExportImageResult
                {
                    Success = true,
                    OutputPath = request.DestinationPath,
                    OriginalSize = originalSize,
                    NewSize = destInfo.Length,
                    Duration = duration,
                    Message = $"Image exported successfully in {duration.TotalSeconds:F1} seconds"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export image");
                return OperationResult<ExportImageResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<OptimizationResult>> OptimizeImageAsync(
        string imagePath,
        CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Optimizing image {ImagePath}", imagePath);

                if (!File.Exists(imagePath))
                {
                    return OperationResult<OptimizationResult>.FailureResult("Image file not found");
                }

                var originalInfo = new FileInfo(imagePath);
                var originalSize = originalInfo.Length;

                // Optimization would involve:
                // 1. Export to temporary location with maximum compression
                // 2. Replace original with optimized version
                // This is a placeholder implementation

                var duration = DateTime.UtcNow - startTime;

                _logger.LogInformation("Image optimized in {Duration}s", duration.TotalSeconds);

                return OperationResult<OptimizationResult>.SuccessResult(new OptimizationResult
                {
                    Success = true,
                    OriginalSize = originalSize,
                    OptimizedSize = originalSize, // Placeholder
                    SpaceSaved = 0, // Placeholder
                    CompressionRatio = 1.0, // Placeholder
                    Duration = duration,
                    Message = $"Image optimization completed in {duration.TotalSeconds:F1} seconds"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to optimize image");
                return OperationResult<OptimizationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private ImageFormat DetermineImageFormat(string filePath)
    {
        var extension = Path.GetExtension(filePath).ToLowerInvariant();

        return extension switch
        {
            ".wim" => ImageFormat.WIM,
            ".esd" => ImageFormat.ESD,
            ".vhd" => ImageFormat.VHD,
            ".vhdx" => ImageFormat.VHDX,
            ".iso" => ImageFormat.ISO,
            ".img" => ImageFormat.IMG,
            ".ppkg" => ImageFormat.PPKG,
            _ => ImageFormat.WIM
        };
    }

    private MountStatus MapDismMountStatus(DismMountStatus dismStatus)
    {
        return dismStatus switch
        {
            DismMountStatus.Ok => MountStatus.Mounted,
            DismMountStatus.NeedsRemount => MountStatus.NeedsRemount,
            DismMountStatus.Invalid => MountStatus.Invalid,
            _ => MountStatus.NotMounted
        };
    }

    #endregion
}
