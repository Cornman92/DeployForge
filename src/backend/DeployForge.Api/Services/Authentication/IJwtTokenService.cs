using System.Security.Claims;
using DeployForge.Api.Models.Authentication;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Interface for JWT token service
/// </summary>
public interface IJwtTokenService
{
    /// <summary>
    /// Generates an access token for a user
    /// </summary>
    string GenerateAccessToken(User user);

    /// <summary>
    /// Generates a refresh token for a user
    /// </summary>
    Task<RefreshToken> GenerateRefreshTokenAsync(User user, CancellationToken cancellationToken = default);

    /// <summary>
    /// Validates an access token and returns the claims principal
    /// </summary>
    ClaimsPrincipal? ValidateAccessToken(string token);

    /// <summary>
    /// Validates a refresh token and returns the associated user
    /// </summary>
    Task<(bool IsValid, User? User)> ValidateRefreshTokenAsync(string refreshToken, CancellationToken cancellationToken = default);

    /// <summary>
    /// Revokes a refresh token
    /// </summary>
    Task RevokeRefreshTokenAsync(string refreshToken, string? replacedByToken = null, CancellationToken cancellationToken = default);

    /// <summary>
    /// Revokes all refresh tokens for a user
    /// </summary>
    Task RevokeAllUserRefreshTokensAsync(string userId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Cleans up expired refresh tokens
    /// </summary>
    Task CleanupExpiredTokensAsync(CancellationToken cancellationToken = default);
}
