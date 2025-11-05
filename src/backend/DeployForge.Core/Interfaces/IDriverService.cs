using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing drivers in Windows images
/// </summary>
public interface IDriverService
{
    /// <summary>
    /// Get all drivers from a mounted image
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of drivers</returns>
    Task<OperationResult<List<DriverInfo>>> GetDriversAsync(
        string mountPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get detailed information about a specific driver
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="driverPath">Driver published name or path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Driver information</returns>
    Task<OperationResult<DriverInfo>> GetDriverInfoAsync(
        string mountPath,
        string driverPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Add drivers to an image
    /// </summary>
    /// <param name="request">Driver operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<DriverOperationResult>> AddDriversAsync(
        DriverOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove drivers from an image
    /// </summary>
    /// <param name="request">Driver operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<DriverOperationResult>> RemoveDriversAsync(
        DriverOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyze driver conflicts before adding
    /// </summary>
    /// <param name="request">Conflict analysis request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Conflict analysis result</returns>
    Task<OperationResult<DriverConflictAnalysis>> AnalyzeConflictsAsync(
        DriverConflictAnalysisRequest request,
        CancellationToken cancellationToken = default);
}
