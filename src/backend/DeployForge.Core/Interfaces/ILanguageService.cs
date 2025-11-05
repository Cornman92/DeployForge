using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing language packs
/// </summary>
public interface ILanguageService
{
    /// <summary>
    /// Get installed language packs
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of language packs</returns>
    Task<OperationResult<List<LanguagePackInfo>>> GetLanguagePacksAsync(
        string mountPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Add language packs to an image
    /// </summary>
    /// <param name="request">Add language pack request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<LanguageOperationResult>> AddLanguagePacksAsync(
        AddLanguagePackRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Remove language packs from an image
    /// </summary>
    /// <param name="request">Remove language pack request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult<LanguageOperationResult>> RemoveLanguagePacksAsync(
        RemoveLanguagePackRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Set default languages for an image
    /// </summary>
    /// <param name="request">Set default languages request</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> SetDefaultLanguagesAsync(
        SetDefaultLanguagesRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get default language settings
    /// </summary>
    /// <param name="mountPath">Path to mounted image</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Default language settings</returns>
    Task<OperationResult<SetDefaultLanguagesRequest>> GetDefaultLanguagesAsync(
        string mountPath,
        CancellationToken cancellationToken = default);
}
