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
    /// Gets all packages from a mounted image
    /// </summary>
    public OperationResult<DismPackageCollection> GetPackages(string mountPath)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismPackageCollection>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var packages = DismApi.GetPackages(session);
            return OperationResult<DismPackageCollection>.SuccessResult(packages);
        }
        catch (Exception ex)
        {
            return OperationResult<DismPackageCollection>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets detailed information about a specific package
    /// </summary>
    public OperationResult<DismPackageInfo> GetPackageInfo(string mountPath, string packageName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismPackageInfo>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var packageInfo = DismApi.GetPackageInfo(session, packageName);
            return OperationResult<DismPackageInfo>.SuccessResult(packageInfo);
        }
        catch (Exception ex)
        {
            return OperationResult<DismPackageInfo>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Removes a package from a mounted image
    /// </summary>
    public OperationResult RemovePackage(string mountPath, string packageName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.RemovePackage(session, packageName, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Adds a package to a mounted image
    /// </summary>
    public OperationResult AddPackage(string mountPath, string packagePath, bool ignoreCheck = false)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.AddPackage(session, packagePath, ignoreCheck, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets all features from a mounted image
    /// </summary>
    public OperationResult<DismFeatureCollection> GetFeatures(string mountPath)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismFeatureCollection>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var features = DismApi.GetFeatures(session);
            return OperationResult<DismFeatureCollection>.SuccessResult(features);
        }
        catch (Exception ex)
        {
            return OperationResult<DismFeatureCollection>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets detailed information about a specific feature
    /// </summary>
    public OperationResult<DismFeatureInfo> GetFeatureInfo(string mountPath, string featureName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismFeatureInfo>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var featureInfo = DismApi.GetFeatureInfo(session, featureName);
            return OperationResult<DismFeatureInfo>.SuccessResult(featureInfo);
        }
        catch (Exception ex)
        {
            return OperationResult<DismFeatureInfo>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Enables a feature in a mounted image
    /// </summary>
    public OperationResult EnableFeature(string mountPath, string featureName, bool enableAll = false)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.EnableFeature(session, featureName, null, enableAll, null, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Disables a feature in a mounted image
    /// </summary>
    public OperationResult DisableFeature(string mountPath, string featureName, string? packageName = null, bool removePayload = false)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.DisableFeature(session, featureName, packageName, removePayload, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets all capabilities from a mounted image
    /// </summary>
    public OperationResult<DismCapabilityCollection> GetCapabilities(string mountPath)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismCapabilityCollection>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var capabilities = DismApi.GetCapabilities(session);
            return OperationResult<DismCapabilityCollection>.SuccessResult(capabilities);
        }
        catch (Exception ex)
        {
            return OperationResult<DismCapabilityCollection>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets detailed information about a specific capability
    /// </summary>
    public OperationResult<DismCapabilityInfo> GetCapabilityInfo(string mountPath, string capabilityName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismCapabilityInfo>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var capabilityInfo = DismApi.GetCapabilityInfo(session, capabilityName);
            return OperationResult<DismCapabilityInfo>.SuccessResult(capabilityInfo);
        }
        catch (Exception ex)
        {
            return OperationResult<DismCapabilityInfo>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Removes a capability from a mounted image
    /// </summary>
    public OperationResult RemoveCapability(string mountPath, string capabilityName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.RemoveCapability(session, capabilityName, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Adds a capability to a mounted image
    /// </summary>
    public OperationResult AddCapability(string mountPath, string capabilityName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.AddCapability(session, capabilityName, null, null, null);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Gets provisioned app packages from a mounted image
    /// </summary>
    public OperationResult<DismAppxPackageCollection> GetProvisionedAppPackages(string mountPath)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult<DismAppxPackageCollection>.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            var appPackages = DismApi.GetProvisionedAppxPackages(session);
            return OperationResult<DismAppxPackageCollection>.SuccessResult(appPackages);
        }
        catch (Exception ex)
        {
            return OperationResult<DismAppxPackageCollection>.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
        }
    }

    /// <summary>
    /// Removes a provisioned app package from a mounted image
    /// </summary>
    public OperationResult RemoveProvisionedAppPackage(string mountPath, string packageName)
    {
        DismSession? session = null;
        try
        {
            var sessionResult = OpenSession(mountPath);
            if (!sessionResult.Success)
                return OperationResult.FailureResult(sessionResult.ErrorMessage ?? "Failed to open session");

            session = sessionResult.Data;
            DismApi.RemoveProvisionedAppxPackage(session, packageName);
            return OperationResult.SuccessResult();
        }
        catch (Exception ex)
        {
            return OperationResult.ExceptionResult(ex);
        }
        finally
        {
            session?.Dispose();
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
