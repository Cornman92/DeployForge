using Microsoft.Dism;
using DeployForge.Common.Models;
using System.Runtime.Versioning;

namespace DeployForge.DismEngine;

/// <summary>
/// Manages DISM operations for Windows image servicing
/// </summary>
[SupportedOSPlatform("windows")]
public class DismManager : IDisposable
{
    private bool _dismInitialized = false;
    private readonly object _lockObject = new object();

    /// <summary>
    /// Initializes the DISM API
    /// </summary>
    public OperationResult Initialize(DismLogLevel logLevel = DismLogLevel.LogErrors)
    {
        try
        {
            lock (_lockObject)
            {
                if (!_dismInitialized)
                {
                    DismApi.Initialize(logLevel);
                    _dismInitialized = true;
                }
            }

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Mounts a WIM image
    /// </summary>
    public OperationResult<string> MountImage(string imagePath, int imageIndex, string mountPath, bool readOnly = false)
    {
        try
        {
            if (!_dismInitialized)
            {
                var initResult = Initialize();
                if (!initResult.Success)
                    return OperationResult<string>.FailureResult("Failed to initialize DISM");
            }

            // Ensure mount directory exists
            if (!Directory.Exists(mountPath))
            {
                Directory.CreateDirectory(mountPath);
            }

            // Mount the image
            DismApi.MountImage(
                imageFilePath: imagePath,
                mountPath: mountPath,
                imageIndex: imageIndex,
                imageName: null,
                imageIdentifier: DismImageIdentifier.ImageIndex,
                readOnly: readOnly,
                options: DismMountImageOptions.None,
                progressCallback: null,
                userData: null
            );

            return OperationResult<string>.SuccessResult(mountPath);
        }
        catch (Exception ex)
        {
            return OperationResult<string>.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Unmounts a WIM image
    /// </summary>
    public OperationResult UnmountImage(string mountPath, bool commit = true)
    {
        try
        {
            if (!_dismInitialized)
            {
                return OperationResult.FailureResult("DISM not initialized");
            }

            var flags = commit ? DismMountImageOptions.None : DismMountImageOptions.Discard;
            DismApi.UnmountImage(mountPath, flags, null, null);

            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Gets information about a WIM file
    /// </summary>
    public OperationResult<DismImageInfoCollection> GetImageInfo(string imagePath)
    {
        try
        {
            if (!_dismInitialized)
            {
                var initResult = Initialize();
                if (!initResult.Success)
                    return OperationResult<DismImageInfoCollection>.FailureResult("Failed to initialize DISM");
            }

            var imageInfo = DismApi.GetImageInfo(imagePath);
            return OperationResult<DismImageInfoCollection>.SuccessResult(imageInfo);
        }
        catch (Exception ex)
        {
            return OperationResult<DismImageInfoCollection>.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Gets mounted images
    /// </summary>
    public OperationResult<DismMountedImageInfoCollection> GetMountedImages()
    {
        try
        {
            if (!_dismInitialized)
            {
                var initResult = Initialize();
                if (!initResult.Success)
                    return OperationResult<DismMountedImageInfoCollection>.FailureResult("Failed to initialize DISM");
            }

            var mountedImages = DismApi.GetMountedImages();
            return OperationResult<DismMountedImageInfoCollection>.SuccessResult(mountedImages);
        }
        catch (Exception ex)
        {
            return OperationResult<DismMountedImageInfoCollection>.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Opens a DISM session for a mounted image
    /// </summary>
    public OperationResult<DismSession> OpenSession(string mountPath)
    {
        try
        {
            if (!_dismInitialized)
            {
                var initResult = Initialize();
                if (!initResult.Success)
                    return OperationResult<DismSession>.FailureResult("Failed to initialize DISM");
            }

            var session = DismApi.OpenOfflineSession(mountPath);
            return OperationResult<DismSession>.SuccessResult(session);
        }
        catch (Exception ex)
        {
            return OperationResult<DismSession>.ExceptionResult(ex);
        }
    }

    /// <summary>
    /// Cleans up DISM resources
    /// </summary>
    public void Dispose()
    {
        lock (_lockObject)
        {
            if (_dismInitialized)
            {
                try
                {
                    DismApi.Shutdown();
                    _dismInitialized = false;
                }
                catch
                {
                    // Ignore errors during shutdown
                }
            }
        }

        GC.SuppressFinalize(this);
    }
}
