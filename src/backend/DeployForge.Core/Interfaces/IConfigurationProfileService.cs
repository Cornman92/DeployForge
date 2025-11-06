using DeployForge.Common.Models;

namespace DeployForge.Core.Interfaces;

/// <summary>
/// Service for managing user configuration profiles
/// </summary>
public interface IConfigurationProfileService
{
    /// <summary>
    /// Gets all configuration profiles
    /// </summary>
    /// <param name="includeShared">Whether to include shared profiles</param>
    /// <param name="tag">Optional tag filter</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of configuration profiles</returns>
    Task<OperationResult<List<ConfigurationProfile>>> GetProfilesAsync(
        bool includeShared = true,
        string? tag = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets a specific configuration profile by ID
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The configuration profile</returns>
    Task<OperationResult<ConfigurationProfile>> GetProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the default configuration profile
    /// </summary>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The default profile</returns>
    Task<OperationResult<ConfigurationProfile>> GetDefaultProfileAsync(
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Creates a new configuration profile
    /// </summary>
    /// <param name="profile">Profile to create</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created profile</returns>
    Task<OperationResult<ConfigurationProfile>> CreateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates an existing configuration profile
    /// </summary>
    /// <param name="profile">Profile to update</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated profile</returns>
    Task<OperationResult<ConfigurationProfile>> UpdateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a configuration profile
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> DeleteProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Sets a profile as the default
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Operation result</returns>
    Task<OperationResult> SetDefaultProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Exports a profile to a file
    /// </summary>
    /// <param name="profileId">Profile identifier</param>
    /// <param name="destinationPath">Destination file path</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The exported file path</returns>
    Task<OperationResult<string>> ExportProfileAsync(
        string profileId,
        string destinationPath,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Imports a profile from a file
    /// </summary>
    /// <param name="filePath">Source file path</param>
    /// <param name="setAsDefault">Whether to set as default profile</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The imported profile</returns>
    Task<OperationResult<ConfigurationProfile>> ImportProfileAsync(
        string filePath,
        bool setAsDefault = false,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Duplicates an existing profile
    /// </summary>
    /// <param name="profileId">Profile to duplicate</param>
    /// <param name="newName">Name for the new profile</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The duplicated profile</returns>
    Task<OperationResult<ConfigurationProfile>> DuplicateProfileAsync(
        string profileId,
        string newName,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates a configuration profile
    /// </summary>
    /// <param name="profile">Profile to validate</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of validation errors (empty if valid)</returns>
    Task<OperationResult<List<string>>> ValidateProfileAsync(
        ConfigurationProfile profile,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Applies profile settings with optional overrides
    /// </summary>
    /// <param name="profileId">Profile to apply</param>
    /// <param name="overrides">Optional settings overrides</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The effective configuration after applying overrides</returns>
    Task<OperationResult<ConfigurationProfile>> ApplyProfileWithOverridesAsync(
        string profileId,
        Dictionary<string, object>? overrides = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Resets a profile to default settings
    /// </summary>
    /// <param name="profileId">Profile to reset</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The reset profile</returns>
    Task<OperationResult<ConfigurationProfile>> ResetProfileAsync(
        string profileId,
        CancellationToken cancellationToken = default);
}
