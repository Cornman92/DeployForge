using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing Windows updates in images
/// </summary>
public interface IUpdateService
{
    /// <summary>
    /// Get installed updates from a mounted image
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of installed updates</returns>
    Task<OperationResult<List<UpdateInfo>>> GetInstalledUpdatesAsync(
        string mountPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Install updates to an image
    /// </summary>
    /// <param name="request">Update operation request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<UpdateOperationResult>> InstallUpdatesAsync(
        UpdateOperationRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove updates from an image
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="updateNames">Update package names to remove</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<UpdateOperationResult>> RemoveUpdatesAsync(
        string mountPath,
        List<string> updateNames,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Analyze update compatibility before installation
    /// </summary>
    /// <param name="request">Compatibility analysis request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Compatibility analysis result</returns>
    Task<OperationResult<UpdateCompatibilityResult>> AnalyzeCompatibilityAsync(
        UpdateCompatibilityRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Cleanup superseded components after update installation
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> CleanupSupersededAsync(
        string mountPath,
        CancellationToken cancellationToken = default);
}
