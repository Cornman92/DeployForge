using System.Security.Cryptography;
using DeployForge.Api.Configuration;
using DeployForge.Api.Data;
using DeployForge.Api.Models.Authentication;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using BCrypt.Net;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Implementation of API key service
/// </summary>
public class ApiKeyService : IApiKeyService
{
    private readonly ApiKeyConfiguration _apiKeyConfig;
    private readonly AuthenticationDbContext _dbContext;
    private readonly ILogger<ApiKeyService> _logger;

    public ApiKeyService(
        IOptions<AuthenticationConfiguration> authConfig,
        AuthenticationDbContext dbContext,
        ILogger<ApiKeyService> logger)
    {
        _apiKeyConfig = authConfig.Value.ApiKey;
        _dbContext = dbContext;
        _logger = logger;
    }

    /// <summary>
    /// Creates a new API key for a user
    /// </summary>
    public async Task<(ApiKey ApiKey, string PlainKey)> CreateApiKeyAsync(
        string userId,
        string name,
        string role,
        int? expirationDays = null,
        CancellationToken cancellationToken = default)
    {
        // Check if user exists
        var user = await _dbContext.Users.FindAsync(new object[] { userId }, cancellationToken);
        if (user == null)
        {
            throw new InvalidOperationException($"User {userId} not found");
        }

        // Check max keys limit
        var existingKeysCount = await _dbContext.ApiKeys
            .CountAsync(k => k.UserId == userId && k.IsActive, cancellationToken);

        if (existingKeysCount >= _apiKeyConfig.MaxKeysPerUser)
        {
            throw new InvalidOperationException(
                $"Maximum number of API keys ({_apiKeyConfig.MaxKeysPerUser}) reached for user {userId}");
        }

        // Generate API key
        var plainKey = GenerateApiKey(_apiKeyConfig.KeyLength);
        var keyHash = BCrypt.Net.BCrypt.HashPassword(plainKey, BCrypt.Net.BCrypt.GenerateSalt(12));
        var keyPrefix = plainKey.Substring(0, 8);

        var apiKey = new ApiKey
        {
            Name = name,
            KeyHash = keyHash,
            KeyPrefix = keyPrefix,
            Role = role,
            UserId = userId,
            IsActive = true,
            CreatedAt = DateTime.UtcNow,
            ExpiresAt = expirationDays.HasValue && expirationDays.Value > 0
                ? DateTime.UtcNow.AddDays(expirationDays.Value)
                : (_apiKeyConfig.ExpirationDays > 0
                    ? DateTime.UtcNow.AddDays(_apiKeyConfig.ExpirationDays)
                    : null)
        };

        _dbContext.ApiKeys.Add(apiKey);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Created API key '{Name}' for user {UserId} with role {Role}",
            name, userId, role);

        return (apiKey, plainKey);
    }

    /// <summary>
    /// Validates an API key and returns the associated user
    /// </summary>
    public async Task<(bool IsValid, User? User)> ValidateApiKeyAsync(
        string apiKey,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(apiKey) || apiKey.Length < 8)
        {
            _logger.LogDebug("Invalid API key format");
            return (false, null);
        }

        var keyPrefix = apiKey.Substring(0, 8);

        // Find API keys with matching prefix
        var possibleKeys = await _dbContext.ApiKeys
            .Include(k => k.User)
            .Where(k => k.KeyPrefix == keyPrefix && k.IsActive)
            .ToListAsync(cancellationToken);

        foreach (var key in possibleKeys)
        {
            try
            {
                if (BCrypt.Net.BCrypt.Verify(apiKey, key.KeyHash))
                {
                    // Check expiration
                    if (key.ExpiresAt.HasValue && key.ExpiresAt.Value < DateTime.UtcNow)
                    {
                        _logger.LogWarning("API key '{Name}' has expired", key.Name);
                        return (false, null);
                    }

                    // Check if user is active
                    if (!key.User.IsActive)
                    {
                        _logger.LogWarning("User {UserId} for API key '{Name}' is not active", key.UserId, key.Name);
                        return (false, null);
                    }

                    // Update last used timestamp (fire and forget)
                    _ = UpdateLastUsedAsync(keyPrefix, cancellationToken);

                    _logger.LogDebug("API key '{Name}' validated successfully for user {UserId}", key.Name, key.UserId);
                    return (true, key.User);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error verifying API key hash");
            }
        }

        _logger.LogWarning("API key validation failed - no matching key found");
        return (false, null);
    }

    /// <summary>
    /// Gets all API keys for a user
    /// </summary>
    public async Task<List<ApiKey>> GetUserApiKeysAsync(string userId, CancellationToken cancellationToken = default)
    {
        return await _dbContext.ApiKeys
            .Where(k => k.UserId == userId)
            .OrderByDescending(k => k.CreatedAt)
            .ToListAsync(cancellationToken);
    }

    /// <summary>
    /// Revokes an API key
    /// </summary>
    public async Task<bool> RevokeApiKeyAsync(string apiKeyId, string userId, CancellationToken cancellationToken = default)
    {
        var apiKey = await _dbContext.ApiKeys
            .FirstOrDefaultAsync(k => k.Id == apiKeyId && k.UserId == userId, cancellationToken);

        if (apiKey == null)
        {
            _logger.LogWarning("API key {ApiKeyId} not found for user {UserId}", apiKeyId, userId);
            return false;
        }

        apiKey.IsActive = false;
        apiKey.RevokedAt = DateTime.UtcNow;

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Revoked API key '{Name}' (ID: {ApiKeyId}) for user {UserId}",
            apiKey.Name, apiKeyId, userId);

        return true;
    }

    /// <summary>
    /// Updates the last used timestamp for an API key
    /// </summary>
    public async Task UpdateLastUsedAsync(string keyPrefix, CancellationToken cancellationToken = default)
    {
        try
        {
            var apiKey = await _dbContext.ApiKeys
                .FirstOrDefaultAsync(k => k.KeyPrefix == keyPrefix && k.IsActive, cancellationToken);

            if (apiKey != null)
            {
                apiKey.LastUsedAt = DateTime.UtcNow;
                await _dbContext.SaveChangesAsync(cancellationToken);
            }
        }
        catch (Exception ex)
        {
            // Log but don't fail the request
            _logger.LogError(ex, "Failed to update last used timestamp for API key");
        }
    }

    /// <summary>
    /// Deletes expired API keys
    /// </summary>
    public async Task CleanupExpiredKeysAsync(CancellationToken cancellationToken = default)
    {
        var expiredKeys = await _dbContext.ApiKeys
            .Where(k => k.ExpiresAt.HasValue && k.ExpiresAt.Value < DateTime.UtcNow)
            .ToListAsync(cancellationToken);

        _dbContext.ApiKeys.RemoveRange(expiredKeys);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Cleaned up {Count} expired API keys", expiredKeys.Count);
    }

    /// <summary>
    /// Generates a cryptographically secure API key
    /// </summary>
    private static string GenerateApiKey(int length)
    {
        const string chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789";
        var result = new char[length];
        var randomBytes = new byte[length];

        using (var rng = RandomNumberGenerator.Create())
        {
            rng.GetBytes(randomBytes);
        }

        for (int i = 0; i < length; i++)
        {
            result[i] = chars[randomBytes[i] % chars.Length];
        }

        return new string(result);
    }
}
