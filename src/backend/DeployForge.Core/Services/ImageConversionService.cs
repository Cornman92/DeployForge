using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using System.Diagnostics;
using System.IO;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for converting between image formats
/// </summary>
[SupportedOSPlatform("windows")]
public class ImageConversionService : IImageConversionService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<ImageConversionService> _logger;

    public ImageConversionService(
        DismManager dismManager,
        ILogger<ImageConversionService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<ImageConversionResult>> ConvertImageAsync(
        ConvertImageRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var startTime = DateTime.UtcNow;
            var result = new ImageConversionResult
            {
                SourcePath = request.SourcePath,
                DestinationPath = request.DestinationPath
            };

            try
            {
                _logger.LogInformation("Converting image from {Source} to {Destination}",
                    request.SourcePath, request.DestinationPath);

                // Validate source file exists
                if (!File.Exists(request.SourcePath))
                {
                    return OperationResult<ImageConversionResult>.FailureResult(
                        "Source image file not found");
                }

                // Get source format and size
                var sourceFormat = DetectImageFormat(request.SourcePath);
                result.SourceFormat = sourceFormat;
                result.SourceSize = new FileInfo(request.SourcePath).Length;

                result.DestinationFormat = request.TargetFormat;

                // Check if conversion is supported
                if (!ImageConversionSupport.IsConversionSupported(sourceFormat, request.TargetFormat))
                {
                    return OperationResult<ImageConversionResult>.FailureResult(
                        $"Conversion from {sourceFormat} to {request.TargetFormat} is not supported");
                }

                // Handle same-format "conversion" (optimization)
                if (sourceFormat == request.TargetFormat)
                {
                    return HandleOptimization(request, result, startTime);
                }

                // Route to appropriate conversion method
                var conversionResult = (sourceFormat, request.TargetFormat) switch
                {
                    (ImageFormat.WIM, ImageFormat.ESD) => ConvertWimToEsd(request, result, cancellationToken),
                    (ImageFormat.ESD, ImageFormat.WIM) => ConvertEsdToWim(request, result, cancellationToken),
                    (ImageFormat.WIM, ImageFormat.VHD) => ConvertWimToVhd(request, result, false, cancellationToken),
                    (ImageFormat.WIM, ImageFormat.VHDX) => ConvertWimToVhd(request, result, true, cancellationToken),
                    (ImageFormat.ESD, ImageFormat.VHD) => ConvertEsdToVhd(request, result, false, cancellationToken),
                    (ImageFormat.ESD, ImageFormat.VHDX) => ConvertEsdToVhd(request, result, true, cancellationToken),
                    (ImageFormat.VHD, ImageFormat.VHDX) => ConvertVhdToVhdx(request, result, cancellationToken),
                    (ImageFormat.VHDX, ImageFormat.VHD) => ConvertVhdxToVhd(request, result, cancellationToken),
                    (ImageFormat.VHD, ImageFormat.WIM) => ConvertVhdToWim(request, result, false, cancellationToken),
                    (ImageFormat.VHDX, ImageFormat.WIM) => ConvertVhdToWim(request, result, true, cancellationToken),
                    _ => OperationResult<ImageConversionResult>.FailureResult("Unsupported conversion")
                };

                if (!conversionResult.Success)
                {
                    result.Success = false;
                    result.ErrorMessage = conversionResult.ErrorMessage;
                    return conversionResult;
                }

                // Get destination size
                if (File.Exists(request.DestinationPath))
                {
                    result.DestinationSize = new FileInfo(request.DestinationPath).Length;
                    result.SpaceSaved = result.SourceSize - result.DestinationSize;
                    result.CompressionRatio = result.DestinationSize / (double)result.SourceSize;
                }

                result.Duration = DateTime.UtcNow - startTime;
                result.Success = true;
                result.Message = $"Successfully converted {sourceFormat} to {request.TargetFormat} in {result.Duration.TotalSeconds:F1}s";

                _logger.LogInformation("Conversion completed: {Message}", result.Message);

                // Delete source if requested
                if (request.DeleteSource && result.Success)
                {
                    try
                    {
                        File.Delete(request.SourcePath);
                        _logger.LogInformation("Deleted source file: {Source}", request.SourcePath);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Failed to delete source file");
                    }
                }

                return OperationResult<ImageConversionResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to convert image");
                result.Success = false;
                result.ErrorMessage = ex.Message;
                result.Duration = DateTime.UtcNow - startTime;
                return OperationResult<ImageConversionResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<ISOExtractionResult>> ExtractISOAsync(
        ExtractISORequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var startTime = DateTime.UtcNow;
            var result = new ISOExtractionResult
            {
                ISOPath = request.ISOPath,
                DestinationPath = request.DestinationPath
            };

            try
            {
                _logger.LogInformation("Extracting ISO {ISO} to {Destination}",
                    request.ISOPath, request.DestinationPath);

                if (!File.Exists(request.ISOPath))
                {
                    return OperationResult<ISOExtractionResult>.FailureResult("ISO file not found");
                }

                // Create destination directory
                if (!Directory.Exists(request.DestinationPath))
                {
                    Directory.CreateDirectory(request.DestinationPath);
                }
                else if (!request.Overwrite && Directory.GetFileSystemEntries(request.DestinationPath).Length > 0)
                {
                    return OperationResult<ISOExtractionResult>.FailureResult(
                        "Destination directory is not empty and overwrite is false");
                }

                // Use PowerShell to mount and copy ISO
                var mountResult = MountAndExtractISO(request.ISOPath, request.DestinationPath, cancellationToken);

                if (!mountResult.Success)
                {
                    return OperationResult<ISOExtractionResult>.FailureResult(
                        mountResult.ErrorMessage ?? "Failed to extract ISO");
                }

                // Count files and directories
                result.FilesExtracted = Directory.GetFiles(request.DestinationPath, "*", SearchOption.AllDirectories).Length;
                result.DirectoriesCreated = Directory.GetDirectories(request.DestinationPath, "*", SearchOption.AllDirectories).Length;
                result.TotalSize = CalculateDirectorySize(request.DestinationPath);
                result.Duration = DateTime.UtcNow - startTime;
                result.Success = true;
                result.Message = $"Extracted {result.FilesExtracted} files in {result.Duration.TotalSeconds:F1}s";

                return OperationResult<ISOExtractionResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to extract ISO");
                result.Success = false;
                result.ErrorMessage = ex.Message;
                result.Duration = DateTime.UtcNow - startTime;
                return OperationResult<ISOExtractionResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public bool IsConversionSupported(ImageFormat source, ImageFormat target)
    {
        return ImageConversionSupport.IsConversionSupported(source, target);
    }

    public TimeSpan EstimateConversionTime(long sourceSize, ImageFormat source, ImageFormat target)
    {
        var complexity = ImageConversionSupport.GetConversionComplexity(source, target);

        // Rough estimates based on 1GB reference size
        var sizeInGB = sourceSize / (1024.0 * 1024.0 * 1024.0);

        var minutesPerGB = complexity switch
        {
            ConversionComplexity.Trivial => 0.5,
            ConversionComplexity.Simple => 2,
            ConversionComplexity.Medium => 5,
            ConversionComplexity.Complex => 10,
            _ => 0
        };

        return TimeSpan.FromMinutes(minutesPerGB * sizeInGB);
    }

    #region Private Helper Methods

    private ImageFormat DetectImageFormat(string filePath)
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
            _ => throw new ArgumentException($"Unknown image format: {extension}")
        };
    }

    private OperationResult<ImageConversionResult> HandleOptimization(
        ConvertImageRequest request,
        ImageConversionResult result,
        DateTime startTime)
    {
        _logger.LogInformation("Source and target formats are the same, performing optimization");

        // For same format, use DISM export to optimize
        var exportResult = _dismManager.ExportImage(
            request.SourcePath,
            request.SourceIndex,
            request.DestinationPath,
            1, // Export to index 1
            compress: request.Compression == ConversionCompressionLevel.Maximum);

        if (!exportResult.Success)
        {
            return OperationResult<ImageConversionResult>.FailureResult(
                exportResult.ErrorMessage ?? "Failed to optimize image");
        }

        result.Duration = DateTime.UtcNow - startTime;
        result.Success = true;
        result.Message = "Image optimized successfully";

        return OperationResult<ImageConversionResult>.SuccessResult(result);
    }

    private OperationResult<ImageConversionResult> ConvertWimToEsd(
        ConvertImageRequest request,
        ImageConversionResult result,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting WIM to ESD using DISM export with recovery compression");

        // Use DISM export with recovery compression
        var exportResult = _dismManager.ExportImage(
            request.SourcePath,
            request.SourceIndex,
            request.DestinationPath,
            1,
            compress: true); // Maximum compression for ESD

        if (!exportResult.Success)
        {
            return OperationResult<ImageConversionResult>.FailureResult(
                exportResult.ErrorMessage ?? "Failed to export to ESD");
        }

        result.CompletedStages.Add(new ConversionStage
        {
            Name = "Export to ESD",
            Status = StageStatus.Completed,
            Message = "Successfully exported WIM to ESD format"
        });

        return OperationResult<ImageConversionResult>.SuccessResult(result);
    }

    private OperationResult<ImageConversionResult> ConvertEsdToWim(
        ConvertImageRequest request,
        ImageConversionResult result,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting ESD to WIM using DISM export");

        // Use DISM export
        var exportResult = _dismManager.ExportImage(
            request.SourcePath,
            request.SourceIndex,
            request.DestinationPath,
            1,
            compress: request.Compression == ConversionCompressionLevel.Maximum);

        if (!exportResult.Success)
        {
            return OperationResult<ImageConversionResult>.FailureResult(
                exportResult.ErrorMessage ?? "Failed to export to WIM");
        }

        result.CompletedStages.Add(new ConversionStage
        {
            Name = "Export to WIM",
            Status = StageStatus.Completed,
            Message = "Successfully exported ESD to WIM format"
        });

        return OperationResult<ImageConversionResult>.SuccessResult(result);
    }

    private OperationResult<ImageConversionResult> ConvertWimToVhd(
        ConvertImageRequest request,
        ImageConversionResult result,
        bool useVhdx,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting WIM to {Format}", useVhdx ? "VHDX" : "VHD");

        // This requires:
        // 1. Create VHD/VHDX
        // 2. Mount VHD/VHDX
        // 3. Apply WIM to VHD
        // 4. Unmount VHD

        // For now, return a placeholder indicating this requires more complex implementation
        result.CompletedStages.Add(new ConversionStage
        {
            Name = $"Create {(useVhdx ? "VHDX" : "VHD")}",
            Status = StageStatus.Completed,
            Message = "VHD/VHDX conversion requires multi-stage process (mount, apply, unmount)"
        });

        // This would require PowerShell or native VHD APIs
        _logger.LogWarning("WIM to VHD/VHDX conversion requires additional implementation");

        return OperationResult<ImageConversionResult>.FailureResult(
            "WIM to VHD/VHDX conversion not yet fully implemented - requires VHD creation and image application");
    }

    private OperationResult<ImageConversionResult> ConvertEsdToVhd(
        ConvertImageRequest request,
        ImageConversionResult result,
        bool useVhdx,
        CancellationToken cancellationToken)
    {
        // First convert ESD to WIM, then WIM to VHD
        _logger.LogInformation("Converting ESD to {Format} via intermediate WIM",
            useVhdx ? "VHDX" : "VHD");

        var tempWim = Path.Combine(Path.GetTempPath(), $"temp_{Guid.NewGuid()}.wim");

        try
        {
            // Step 1: Convert ESD to WIM
            var esdToWimRequest = new ConvertImageRequest
            {
                SourcePath = request.SourcePath,
                SourceIndex = request.SourceIndex,
                DestinationPath = tempWim,
                TargetFormat = ImageFormat.WIM,
                CheckIntegrity = request.CheckIntegrity
            };

            var wimResult = ConvertEsdToWim(esdToWimRequest, result, cancellationToken);
            if (!wimResult.Success)
            {
                return wimResult;
            }

            // Step 2: Convert WIM to VHD/VHDX
            var wimToVhdRequest = new ConvertImageRequest
            {
                SourcePath = tempWim,
                SourceIndex = 1,
                DestinationPath = request.DestinationPath,
                TargetFormat = request.TargetFormat,
                MaxVirtualDiskSizeGB = request.MaxVirtualDiskSizeGB,
                DynamicExpansion = request.DynamicExpansion
            };

            return ConvertWimToVhd(wimToVhdRequest, result, useVhdx, cancellationToken);
        }
        finally
        {
            // Cleanup temp WIM
            if (File.Exists(tempWim))
            {
                try
                {
                    File.Delete(tempWim);
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to delete temporary WIM file");
                }
            }
        }
    }

    private OperationResult<ImageConversionResult> ConvertVhdToVhdx(
        ConvertImageRequest request,
        ImageConversionResult result,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting VHD to VHDX using PowerShell");

        // Use PowerShell Convert-VHD cmdlet
        var psScript = $@"
            Convert-VHD -Path '{request.SourcePath}' -DestinationPath '{request.DestinationPath}' -VHDType Dynamic
        ";

        var psResult = RunPowerShellScript(psScript, cancellationToken);

        if (!psResult.Success)
        {
            return OperationResult<ImageConversionResult>.FailureResult(
                psResult.ErrorMessage ?? "Failed to convert VHD to VHDX");
        }

        result.CompletedStages.Add(new ConversionStage
        {
            Name = "Convert VHD to VHDX",
            Status = StageStatus.Completed,
            Message = "Successfully converted VHD to VHDX"
        });

        return OperationResult<ImageConversionResult>.SuccessResult(result);
    }

    private OperationResult<ImageConversionResult> ConvertVhdxToVhd(
        ConvertImageRequest request,
        ImageConversionResult result,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting VHDX to VHD using PowerShell");

        // Use PowerShell Convert-VHD cmdlet
        var psScript = $@"
            Convert-VHD -Path '{request.SourcePath}' -DestinationPath '{request.DestinationPath}' -VHDType Dynamic
        ";

        var psResult = RunPowerShellScript(psScript, cancellationToken);

        if (!psResult.Success)
        {
            return OperationResult<ImageConversionResult>.FailureResult(
                psResult.ErrorMessage ?? "Failed to convert VHDX to VHD");
        }

        result.CompletedStages.Add(new ConversionStage
        {
            Name = "Convert VHDX to VHD",
            Status = StageStatus.Completed,
            Message = "Successfully converted VHDX to VHD"
        });

        return OperationResult<ImageConversionResult>.SuccessResult(result);
    }

    private OperationResult<ImageConversionResult> ConvertVhdToWim(
        ConvertImageRequest request,
        ImageConversionResult result,
        bool isVhdx,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Converting {Format} to WIM", isVhdx ? "VHDX" : "VHD");

        // This requires:
        // 1. Mount VHD/VHDX
        // 2. Capture to WIM
        // 3. Unmount VHD

        _logger.LogWarning("VHD/VHDX to WIM conversion requires additional implementation");

        return OperationResult<ImageConversionResult>.FailureResult(
            "VHD/VHDX to WIM conversion not yet fully implemented - requires VHD mounting and image capture");
    }

    private OperationResult MountAndExtractISO(
        string isoPath,
        string destinationPath,
        CancellationToken cancellationToken)
    {
        try
        {
            var psScript = $@"
                $iso = Mount-DiskImage -ImagePath '{isoPath}' -PassThru
                $drive = ($iso | Get-Volume).DriveLetter
                Copy-Item -Path ""$($drive):\*"" -Destination '{destinationPath}' -Recurse -Force
                Dismount-DiskImage -ImagePath '{isoPath}'
            ";

            return RunPowerShellScript(psScript, cancellationToken);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to mount and extract ISO");
            return OperationResult.ExceptionResult(ex);
        }
    }

    private OperationResult RunPowerShellScript(string script, CancellationToken cancellationToken)
    {
        try
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "powershell.exe",
                Arguments = $"-NoProfile -ExecutionPolicy Bypass -Command \"{script.Replace("\"", "`\"")}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var process = Process.Start(startInfo);
            if (process == null)
            {
                return OperationResult.FailureResult("Failed to start PowerShell process");
            }

            var output = process.StandardOutput.ReadToEnd();
            var error = process.StandardError.ReadToEnd();

            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                _logger.LogError("PowerShell script failed: {Error}", error);
                return OperationResult.FailureResult($"PowerShell error: {error}");
            }

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to run PowerShell script");
            return OperationResult.ExceptionResult(ex);
        }
    }

    private long CalculateDirectorySize(string directoryPath)
    {
        try
        {
            return Directory.GetFiles(directoryPath, "*", SearchOption.AllDirectories)
                .Sum(file => new FileInfo(file).Length);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to calculate directory size");
            return 0;
        }
    }

    #endregion
}
