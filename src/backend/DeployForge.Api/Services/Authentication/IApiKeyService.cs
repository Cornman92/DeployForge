using DeployForge.Api.Models.Authentication;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Interface for API key service
/// </summary>
public interface IApiKeyService
{
    /// <summary>
    /// Creates a new API key for a user
    /// </summary>
    Task<(ApiKey ApiKey, string PlainKey)> CreateApiKeyAsync(
        string userId,
        string name,
        string role,
        int? expirationDays = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates an API key and returns the associated user
    /// </summary>
    Task<(bool IsValid, User? User)> ValidateApiKeyAsync(string apiKey, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets all API keys for a user
    /// </summary>
    Task<List<ApiKey>> GetUserApiKeysAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Revokes an API key
    /// </summary>
    Task<bool> RevokeApiKeyAsync(string apiKeyId, string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Updates the last used timestamp for an API key
    /// </summary>
    Task UpdateLastUsedAsync(string keyPrefix, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes expired API keys
    /// </summary>
    Task CleanupExpiredKeysAsync(CancellationToken cancellationToken = default);
}
