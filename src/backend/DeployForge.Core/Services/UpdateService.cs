using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using Microsoft.Dism;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing Windows updates in images
/// </summary>
[SupportedOSPlatform("windows")]
public class UpdateService : IUpdateService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<UpdateService> _logger;

    public UpdateService(DismManager dismManager, ILogger<UpdateService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<List<UpdateInfo>>> GetInstalledUpdatesAsync(
        string mountPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var packagesResult = _dismManager.GetPackages(mountPath);

                if (!packagesResult.Success || packagesResult.Data == null)
                {
                    return OperationResult<List<UpdateInfo>>.FailureResult(
                        packagesResult.ErrorMessage ?? "Failed to get packages");
                }

                // Filter packages that are updates (KB packages)
                var updates = packagesResult.Data
                    .Where(p => p.PackageName.Contains("KB", StringComparison.OrdinalIgnoreCase))
                    .Select(MapPackageToUpdate)
                    .ToList();

                _logger.LogInformation("Found {Count} installed updates in {MountPath}", updates.Count, mountPath);

                return OperationResult<List<UpdateInfo>>.SuccessResult(updates);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get installed updates from {MountPath}", mountPath);
                return OperationResult<List<UpdateInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<UpdateOperationResult>> InstallUpdatesAsync(
        UpdateOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new UpdateOperationResult();
            var successful = new List<string>();
            var failed = new List<UpdateOperationError>();
            bool restartRequired = false;

            try
            {
                _logger.LogInformation("Installing {Count} updates to {MountPath}",
                    request.UpdatePaths.Count, request.MountPath);

                foreach (var updatePath in request.UpdatePaths)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    try
                    {
                        if (!File.Exists(updatePath))
                        {
                            failed.Add(new UpdateOperationError
                            {
                                UpdateId = updatePath,
                                ErrorMessage = "Update file not found"
                            });
                            _logger.LogWarning("Update file not found: {UpdatePath}", updatePath);
                            continue;
                        }

                        // Determine if it's .msu or .cab
                        var extension = Path.GetExtension(updatePath).ToLowerInvariant();

                        if (extension == ".msu")
                        {
                            // Extract .cab from .msu (simplified - in production, use proper MSU extraction)
                            // For now, try to add directly as package
                            var addResult = _dismManager.AddPackage(
                                request.MountPath, updatePath, request.IgnoreCheck);

                            if (addResult.Success)
                            {
                                successful.Add(updatePath);
                                restartRequired = true;
                                _logger.LogInformation("Successfully installed update {UpdatePath}", updatePath);
                            }
                            else
                            {
                                failed.Add(new UpdateOperationError
                                {
                                    UpdateId = updatePath,
                                    ErrorMessage = addResult.ErrorMessage ?? "Failed to install update"
                                });
                                _logger.LogWarning("Failed to install update {UpdatePath}: {Error}",
                                    updatePath, addResult.ErrorMessage);
                            }
                        }
                        else if (extension == ".cab")
                        {
                            var addResult = _dismManager.AddPackage(
                                request.MountPath, updatePath, request.IgnoreCheck);

                            if (addResult.Success)
                            {
                                successful.Add(updatePath);
                                restartRequired = true;
                                _logger.LogInformation("Successfully installed update {UpdatePath}", updatePath);
                            }
                            else
                            {
                                failed.Add(new UpdateOperationError
                                {
                                    UpdateId = updatePath,
                                    ErrorMessage = addResult.ErrorMessage ?? "Failed to install update"
                                });
                                _logger.LogWarning("Failed to install update {UpdatePath}: {Error}",
                                    updatePath, addResult.ErrorMessage);
                            }
                        }
                        else
                        {
                            failed.Add(new UpdateOperationError
                            {
                                UpdateId = updatePath,
                                ErrorMessage = "Unsupported update format (must be .msu or .cab)"
                            });
                            _logger.LogWarning("Unsupported update format: {UpdatePath}", updatePath);
                        }
                    }
                    catch (Exception ex)
                    {
                        failed.Add(new UpdateOperationError
                        {
                            UpdateId = updatePath,
                            ErrorMessage = ex.Message
                        });
                        _logger.LogError(ex, "Exception while installing update {UpdatePath}", updatePath);
                    }
                }

                result.SuccessfulUpdates = successful;
                result.FailedUpdates = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.RestartRequired = restartRequired;
                result.Success = successful.Count > 0;
                result.Message = $"Installed {successful.Count} of {result.TotalProcessed} updates";

                return OperationResult<UpdateOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install updates");
                return OperationResult<UpdateOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<UpdateOperationResult>> RemoveUpdatesAsync(
        string mountPath,
        List<string> updateNames,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new UpdateOperationResult();
            var successful = new List<string>();
            var failed = new List<UpdateOperationError>();

            try
            {
                _logger.LogInformation("Removing {Count} updates from {MountPath}",
                    updateNames.Count, mountPath);

                foreach (var updateName in updateNames)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    var removeResult = _dismManager.RemovePackage(mountPath, updateName);

                    if (removeResult.Success)
                    {
                        successful.Add(updateName);
                        _logger.LogInformation("Successfully removed update {UpdateName}", updateName);
                    }
                    else
                    {
                        failed.Add(new UpdateOperationError
                        {
                            UpdateId = updateName,
                            ErrorMessage = removeResult.ErrorMessage ?? "Failed to remove update"
                        });
                        _logger.LogWarning("Failed to remove update {UpdateName}: {Error}",
                            updateName, removeResult.ErrorMessage);
                    }
                }

                result.SuccessfulUpdates = successful;
                result.FailedUpdates = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.RestartRequired = successful.Count > 0;
                result.Success = successful.Count > 0;
                result.Message = $"Removed {successful.Count} of {result.TotalProcessed} updates";

                return OperationResult<UpdateOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove updates");
                return OperationResult<UpdateOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<UpdateCompatibilityResult>> AnalyzeCompatibilityAsync(
        UpdateCompatibilityRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var result = new UpdateCompatibilityResult();

                _logger.LogInformation("Analyzing compatibility for {Count} updates", request.UpdatePaths.Count);

                // Simplified compatibility check
                // In production, this would parse update metadata and check OS version, architecture, etc.

                foreach (var updatePath in request.UpdatePaths)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    if (!File.Exists(updatePath))
                    {
                        result.IncompatibleUpdates.Add(new UpdateIncompatibility
                        {
                            UpdatePath = updatePath,
                            Reason = "File not found",
                            Type = IncompatibilityType.Other
                        });
                        continue;
                    }

                    var extension = Path.GetExtension(updatePath).ToLowerInvariant();
                    if (extension == ".msu" || extension == ".cab")
                    {
                        result.CompatibleUpdates.Add(updatePath);
                        result.InstallationOrder.Add(updatePath);
                    }
                    else
                    {
                        result.IncompatibleUpdates.Add(new UpdateIncompatibility
                        {
                            UpdatePath = updatePath,
                            Reason = "Unsupported file format (must be .msu or .cab)",
                            Type = IncompatibilityType.Other
                        });
                    }
                }

                _logger.LogInformation("Compatibility analysis complete. Compatible: {Compatible}, Incompatible: {Incompatible}",
                    result.CompatibleUpdates.Count, result.IncompatibleUpdates.Count);

                return OperationResult<UpdateCompatibilityResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to analyze update compatibility");
                return OperationResult<UpdateCompatibilityResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult> CleanupSupersededAsync(
        string mountPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                _logger.LogInformation("Cleaning up superseded components in {MountPath}", mountPath);

                // Get all packages
                var packagesResult = _dismManager.GetPackages(mountPath);

                if (!packagesResult.Success || packagesResult.Data == null)
                {
                    return OperationResult.FailureResult(
                        packagesResult.ErrorMessage ?? "Failed to get packages");
                }

                // Find superseded packages
                var superseded = packagesResult.Data
                    .Where(p => p.PackageState == DismPackageFeatureState.Superseded)
                    .ToList();

                _logger.LogInformation("Found {Count} superseded packages", superseded.Count);

                // Remove superseded packages
                int removed = 0;
                foreach (var package in superseded)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    var removeResult = _dismManager.RemovePackage(mountPath, package.PackageName);
                    if (removeResult.Success)
                    {
                        removed++;
                        _logger.LogInformation("Removed superseded package {PackageName}", package.PackageName);
                    }
                }

                _logger.LogInformation("Cleanup complete. Removed {Removed} of {Total} superseded packages",
                    removed, superseded.Count);

                return OperationResult.SuccessResult();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to cleanup superseded components");
                return OperationResult.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private UpdateInfo MapPackageToUpdate(DismPackage package)
    {
        // Extract KB number from package name
        var kbNumber = ExtractKBNumber(package.PackageName);

        return new UpdateInfo
        {
            KBNumber = kbNumber,
            Title = package.PackageName,
            Type = DetermineUpdateType(package.PackageName),
            Version = package.PackageName,
            ReleaseDate = package.InstallTime == DateTime.MinValue ? null : package.InstallTime,
            State = MapPackageStateToUpdateState(package.PackageState),
            IsInstalled = package.PackageState == DismPackageFeatureState.Installed,
            RestartRequired = package.RestartRequired == DismRestartType.Required
        };
    }

    private string ExtractKBNumber(string packageName)
    {
        var kbIndex = packageName.IndexOf("KB", StringComparison.OrdinalIgnoreCase);
        if (kbIndex >= 0)
        {
            var remaining = packageName.Substring(kbIndex);
            var match = System.Text.RegularExpressions.Regex.Match(remaining, @"KB\d+");
            if (match.Success)
            {
                return match.Value;
            }
        }
        return string.Empty;
    }

    private UpdateType DetermineUpdateType(string packageName)
    {
        var lower = packageName.ToLowerInvariant();

        if (lower.Contains("cumulative"))
            return UpdateType.CumulativeUpdate;
        if (lower.Contains("security"))
            return UpdateType.SecurityUpdate;
        if (lower.Contains("feature"))
            return UpdateType.FeatureUpdate;
        if (lower.Contains("servicepack") || lower.Contains("sp"))
            return UpdateType.ServicePack;
        if (lower.Contains("critical"))
            return UpdateType.CriticalUpdate;
        if (lower.Contains("definition"))
            return UpdateType.DefinitionUpdate;
        if (lower.Contains("driver"))
            return UpdateType.DriverUpdate;

        return UpdateType.Other;
    }

    private UpdateState MapPackageStateToUpdateState(DismPackageFeatureState state)
    {
        return state switch
        {
            DismPackageFeatureState.Installed => UpdateState.Installed,
            DismPackageFeatureState.Superseded => UpdateState.Superseded,
            DismPackageFeatureState.InstallPending => UpdateState.InstallPending,
            DismPackageFeatureState.UninstallPending => UpdateState.NotInstalled,
            _ => UpdateState.NotInstalled
        };
    }

    #endregion
}
