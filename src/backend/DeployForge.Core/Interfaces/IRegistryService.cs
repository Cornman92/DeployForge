using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing offline registry hives
/// </summary>
public interface IRegistryService
{
    /// <summary>
    /// Load a registry hive from a mounted image
    /// </summary>
    /// <param name="request">Load hive request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> LoadHiveAsync(
        LoadHiveRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Unload a previously loaded registry hive
    /// </summary>
    /// <param name="mountPoint">Registry mount point</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> UnloadHiveAsync(
        string mountPoint,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get registry key information
    /// </summary>
    /// <param name="keyPath">Full registry key path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Registry key information</returns>
    Task<OperationResult<RegistryKeyInfo>> GetKeyInfoAsync(
        string keyPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get all values in a registry key
    /// </summary>
    /// <param name="keyPath">Full registry key path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of registry values</returns>
    Task<OperationResult<List<RegistryValueInfo>>> GetValuesAsync(
        string keyPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get subkeys of a registry key
    /// </summary>
    /// <param name="keyPath">Full registry key path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of subkey names</returns>
    Task<OperationResult<List<string>>> GetSubKeysAsync(
        string keyPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Set a registry value
    /// </summary>
    /// <param name="request">Set value request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> SetValueAsync(
        SetRegistryValueRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Delete a registry key or value
    /// </summary>
    /// <param name="request">Delete request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> DeleteAsync(
        DeleteRegistryRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Import a .reg file into a hive
    /// </summary>
    /// <param name="request">Import request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> ImportRegFileAsync(
        ImportRegFileRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Export registry keys to a .reg file
    /// </summary>
    /// <param name="request">Export request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> ExportRegFileAsync(
        ExportRegFileRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Apply a registry tweak preset
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="preset">Tweak preset</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> ApplyTweakPresetAsync(
        string mountPath,
        RegistryTweakPreset preset,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get available tweak presets
    /// </summary>
    /// <param name="category">Filter by category</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of presets</returns>
    Task<OperationResult<List<RegistryTweakPreset>>> GetTweakPresetsAsync(
        string? category = null,
        CancellationToken cancellationToken = default);
}
