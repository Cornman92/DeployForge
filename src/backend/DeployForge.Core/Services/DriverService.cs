using DeployForge.Common.Models;
using DeployForge.Core.Interfaces;
using DeployForge.DismEngine;
using Microsoft.Dism;
using System.Runtime.Versioning;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for managing drivers in Windows images
/// </summary>
[SupportedOSPlatform("windows")]
public class DriverService : IDriverService
{
    private readonly DismManager _dismManager;
    private readonly ILogger<DriverService> _logger;

    public DriverService(DismManager dismManager, ILogger<DriverService> logger)
    {
        _dismManager = dismManager;
        _logger = logger;
    }

    public async Task<OperationResult<List<DriverInfo>>> GetDriversAsync(
        string mountPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var driversResult = _dismManager.GetDrivers(mountPath);

                if (!driversResult.Success || driversResult.Data == null)
                {
                    return OperationResult<List<DriverInfo>>.FailureResult(
                        driversResult.ErrorMessage ?? "Failed to get drivers");
                }

                var drivers = driversResult.Data.Select(MapDismDriverToDriverInfo).ToList();
                return OperationResult<List<DriverInfo>>.SuccessResult(drivers);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get drivers from {MountPath}", mountPath);
                return OperationResult<List<DriverInfo>>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DriverInfo>> GetDriverInfoAsync(
        string mountPath,
        string driverPath,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var driverResult = _dismManager.GetDriverInfo(mountPath, driverPath);

                if (!driverResult.Success || driverResult.Data == null)
                {
                    return OperationResult<DriverInfo>.FailureResult(
                        driverResult.ErrorMessage ?? "Failed to get driver info");
                }

                var driverInfo = MapDismDriverToDriverInfo(driverResult.Data);
                return OperationResult<DriverInfo>.SuccessResult(driverInfo);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get driver info for {DriverPath}", driverPath);
                return OperationResult<DriverInfo>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DriverOperationResult>> AddDriversAsync(
        DriverOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new DriverOperationResult();
            var successful = new List<string>();
            var failed = new List<DriverOperationError>();

            try
            {
                _logger.LogInformation("Adding {Count} drivers to {MountPath}",
                    request.Drivers.Count, request.MountPath);

                foreach (var driverPath in request.Drivers)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    try
                    {
                        // Check if path is a directory or file
                        if (Directory.Exists(driverPath))
                        {
                            // Scan directory for .inf files
                            var infFiles = Directory.GetFiles(driverPath, "*.inf",
                                request.Recurse ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly);

                            foreach (var infFile in infFiles)
                            {
                                var addResult = _dismManager.AddDriver(
                                    request.MountPath, infFile, request.ForceUnsigned);

                                if (addResult.Success)
                                {
                                    successful.Add(infFile);
                                    _logger.LogInformation("Successfully added driver {DriverPath}", infFile);
                                }
                                else
                                {
                                    failed.Add(new DriverOperationError
                                    {
                                        DriverId = infFile,
                                        ErrorMessage = addResult.ErrorMessage ?? "Unknown error"
                                    });
                                    _logger.LogWarning("Failed to add driver {DriverPath}: {Error}",
                                        infFile, addResult.ErrorMessage);
                                }
                            }
                        }
                        else if (File.Exists(driverPath))
                        {
                            var addResult = _dismManager.AddDriver(
                                request.MountPath, driverPath, request.ForceUnsigned);

                            if (addResult.Success)
                            {
                                successful.Add(driverPath);
                                _logger.LogInformation("Successfully added driver {DriverPath}", driverPath);
                            }
                            else
                            {
                                failed.Add(new DriverOperationError
                                {
                                    DriverId = driverPath,
                                    ErrorMessage = addResult.ErrorMessage ?? "Unknown error"
                                });
                                _logger.LogWarning("Failed to add driver {DriverPath}: {Error}",
                                    driverPath, addResult.ErrorMessage);
                            }
                        }
                        else
                        {
                            failed.Add(new DriverOperationError
                            {
                                DriverId = driverPath,
                                ErrorMessage = "Path does not exist"
                            });
                            _logger.LogWarning("Driver path does not exist: {DriverPath}", driverPath);
                        }
                    }
                    catch (Exception ex)
                    {
                        failed.Add(new DriverOperationError
                        {
                            DriverId = driverPath,
                            ErrorMessage = ex.Message
                        });
                        _logger.LogError(ex, "Exception while adding driver {DriverPath}", driverPath);
                    }
                }

                result.SuccessfulDrivers = successful;
                result.FailedDrivers = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.Success = successful.Count > 0;
                result.Message = $"Added {successful.Count} of {result.TotalProcessed} drivers";

                return OperationResult<DriverOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add drivers");
                return OperationResult<DriverOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DriverOperationResult>> RemoveDriversAsync(
        DriverOperationRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            var result = new DriverOperationResult();
            var successful = new List<string>();
            var failed = new List<DriverOperationError>();

            try
            {
                _logger.LogInformation("Removing {Count} drivers from {MountPath}",
                    request.Drivers.Count, request.MountPath);

                foreach (var driverPath in request.Drivers)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    var removeResult = _dismManager.RemoveDriver(request.MountPath, driverPath);

                    if (removeResult.Success)
                    {
                        successful.Add(driverPath);
                        _logger.LogInformation("Successfully removed driver {DriverPath}", driverPath);
                    }
                    else
                    {
                        failed.Add(new DriverOperationError
                        {
                            DriverId = driverPath,
                            ErrorMessage = removeResult.ErrorMessage ?? "Unknown error"
                        });
                        _logger.LogWarning("Failed to remove driver {DriverPath}: {Error}",
                            driverPath, removeResult.ErrorMessage);
                    }
                }

                result.SuccessfulDrivers = successful;
                result.FailedDrivers = failed;
                result.TotalProcessed = successful.Count + failed.Count;
                result.Success = successful.Count > 0;
                result.Message = $"Removed {successful.Count} of {result.TotalProcessed} drivers";

                return OperationResult<DriverOperationResult>.SuccessResult(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove drivers");
                return OperationResult<DriverOperationResult>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    public async Task<OperationResult<DriverConflictAnalysis>> AnalyzeConflictsAsync(
        DriverConflictAnalysisRequest request,
        CancellationToken cancellationToken = default)
    {
        return await Task.Run(() =>
        {
            try
            {
                var analysis = new DriverConflictAnalysis
                {
                    SafeToAdd = true
                };

                // Get existing drivers
                var existingDriversResult = _dismManager.GetDrivers(request.MountPath);
                if (!existingDriversResult.Success || existingDriversResult.Data == null)
                {
                    return OperationResult<DriverConflictAnalysis>.FailureResult(
                        "Failed to get existing drivers");
                }

                var existingDrivers = existingDriversResult.Data.ToList();

                // Analyze each new driver for conflicts
                foreach (var newDriverPath in request.NewDriverPaths)
                {
                    if (cancellationToken.IsCancellationRequested)
                        break;

                    // For simplicity, this is a basic implementation
                    // A production version would parse INF files and check hardware IDs
                    var fileName = Path.GetFileName(newDriverPath);

                    // Check for duplicate file names (simple heuristic)
                    var duplicate = existingDrivers.FirstOrDefault(d =>
                        Path.GetFileName(d.OriginalFileName).Equals(fileName,
                            StringComparison.OrdinalIgnoreCase));

                    if (duplicate != null)
                    {
                        analysis.Conflicts.Add(new DriverConflict
                        {
                            ExistingDriver = MapDismDriverToDriverInfo(duplicate),
                            NewDriverPath = newDriverPath,
                            Type = ConflictType.DuplicateDriver,
                            Description = $"Driver with similar name already exists: {duplicate.PublishedName}",
                            Severity = ConflictSeverity.Warning
                        });

                        analysis.Recommendations.Add(
                            $"Review {fileName} - a similar driver is already present");
                    }
                }

                // Determine overall safety
                analysis.SafeToAdd = !analysis.Conflicts.Any(c => c.Severity == ConflictSeverity.Error);

                if (analysis.Conflicts.Count == 0)
                {
                    analysis.Recommendations.Add("No conflicts detected. Safe to proceed.");
                }

                _logger.LogInformation("Driver conflict analysis completed. Conflicts: {Count}, Safe: {Safe}",
                    analysis.Conflicts.Count, analysis.SafeToAdd);

                return OperationResult<DriverConflictAnalysis>.SuccessResult(analysis);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to analyze driver conflicts");
                return OperationResult<DriverConflictAnalysis>.ExceptionResult(ex);
            }
        }, cancellationToken);
    }

    #region Private Helper Methods

    private DriverInfo MapDismDriverToDriverInfo(DismDriver driver)
    {
        return new DriverInfo
        {
            PublishedName = driver.PublishedName ?? string.Empty,
            OriginalFileName = driver.OriginalFileName ?? string.Empty,
            InBox = driver.InBox,
            ProviderName = driver.ProviderName ?? string.Empty,
            ClassName = driver.ClassName ?? string.Empty,
            ClassGuid = driver.ClassGuid ?? string.Empty,
            ClassDescription = driver.ClassDescription ?? string.Empty,
            BootCritical = driver.BootCritical,
            DriverSignature = driver.DriverSignature.ToString(),
            Version = driver.Version?.ToString() ?? "Unknown",
            Date = driver.Date == DateTime.MinValue ? null : driver.Date,
            Architecture = driver.Architecture.ToString(),
            Manufacturer = driver.ManufacturerName ?? string.Empty,
            HardwareIds = driver.HardwareId != null ? new List<string> { driver.HardwareId } : new List<string>(),
            CompatibleIds = driver.CompatibleIds?.ToList() ?? new List<string>()
        };
    }

    #endregion
}
