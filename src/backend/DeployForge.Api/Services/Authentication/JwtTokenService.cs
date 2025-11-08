using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using DeployForge.Api.Configuration;
using DeployForge.Api.Data;
using DeployForge.Api.Models.Authentication;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;

namespace DeployForge.Api.Services.Authentication;

/// <summary>
/// Implementation of JWT token service
/// </summary>
public class JwtTokenService : IJwtTokenService
{
    private readonly JwtConfiguration _jwtConfig;
    private readonly AuthenticationDbContext _dbContext;
    private readonly ILogger<JwtTokenService> _logger;
    private readonly SigningCredentials _signingCredentials;

    public JwtTokenService(
        IOptions<AuthenticationConfiguration> authConfig,
        AuthenticationDbContext dbContext,
        ILogger<JwtTokenService> logger)
    {
        _jwtConfig = authConfig.Value.Jwt;
        _dbContext = dbContext;
        _logger = logger;

        if (string.IsNullOrEmpty(_jwtConfig.SecretKey) || _jwtConfig.SecretKey.Length < 32)
        {
            throw new InvalidOperationException(
                "JWT Secret Key must be configured and at least 32 characters long. " +
                "Set Authentication:Jwt:SecretKey in appsettings.json");
        }

        var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtConfig.SecretKey));
        _signingCredentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);
    }

    /// <summary>
    /// Generates an access token for a user
    /// </summary>
    public string GenerateAccessToken(User user)
    {
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Role, user.Role),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(JwtRegisteredClaimNames.Iat, DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString(), ClaimValueTypes.Integer64)
        };

        var token = new JwtSecurityToken(
            issuer: _jwtConfig.Issuer,
            audience: _jwtConfig.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_jwtConfig.AccessTokenExpirationMinutes),
            signingCredentials: _signingCredentials
        );

        var tokenString = new JwtSecurityTokenHandler().WriteToken(token);

        _logger.LogInformation("Generated access token for user {Username} (ID: {UserId})", user.Username, user.Id);

        return tokenString;
    }

    /// <summary>
    /// Generates a refresh token for a user
    /// </summary>
    public async Task<RefreshToken> GenerateRefreshTokenAsync(User user, CancellationToken cancellationToken = default)
    {
        var refreshToken = new RefreshToken
        {
            Token = GenerateSecureRandomToken(),
            UserId = user.Id,
            ExpiresAt = DateTime.UtcNow.AddDays(_jwtConfig.RefreshTokenExpirationDays),
            CreatedAt = DateTime.UtcNow,
            IsUsed = false,
            IsRevoked = false
        };

        _dbContext.RefreshTokens.Add(refreshToken);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Generated refresh token for user {Username} (ID: {UserId})", user.Username, user.Id);

        return refreshToken;
    }

    /// <summary>
    /// Validates an access token and returns the claims principal
    /// </summary>
    public ClaimsPrincipal? ValidateAccessToken(string token)
    {
        try
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(_jwtConfig.SecretKey);

            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuer = _jwtConfig.ValidateIssuer,
                ValidateAudience = _jwtConfig.ValidateAudience,
                ValidateLifetime = _jwtConfig.ValidateLifetime,
                ValidateIssuerSigningKey = true,
                ValidIssuer = _jwtConfig.Issuer,
                ValidAudience = _jwtConfig.Audience,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ClockSkew = TimeSpan.FromMinutes(_jwtConfig.ClockSkewMinutes)
            };

            var principal = tokenHandler.ValidateToken(token, validationParameters, out var validatedToken);

            if (validatedToken is not JwtSecurityToken jwtToken ||
                !jwtToken.Header.Alg.Equals(SecurityAlgorithms.HmacSha256, StringComparison.InvariantCultureIgnoreCase))
            {
                _logger.LogWarning("Invalid JWT algorithm");
                return null;
            }

            return principal;
        }
        catch (SecurityTokenExpiredException)
        {
            _logger.LogDebug("Access token expired");
            return null;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to validate access token");
            return null;
        }
    }

    /// <summary>
    /// Validates a refresh token and returns the associated user
    /// </summary>
    public async Task<(bool IsValid, User? User)> ValidateRefreshTokenAsync(
        string refreshToken,
        CancellationToken cancellationToken = default)
    {
        var token = await _dbContext.RefreshTokens
            .Include(rt => rt.User)
            .FirstOrDefaultAsync(rt => rt.Token == refreshToken, cancellationToken);

        if (token == null)
        {
            _logger.LogWarning("Refresh token not found");
            return (false, null);
        }

        if (token.IsRevoked)
        {
            _logger.LogWarning("Refresh token has been revoked for user {UserId}", token.UserId);
            return (false, null);
        }

        if (token.IsUsed)
        {
            _logger.LogWarning("Refresh token has already been used for user {UserId}", token.UserId);
            return (false, null);
        }

        if (token.ExpiresAt < DateTime.UtcNow)
        {
            _logger.LogWarning("Refresh token has expired for user {UserId}", token.UserId);
            return (false, null);
        }

        if (!token.User.IsActive)
        {
            _logger.LogWarning("User {UserId} is not active", token.UserId);
            return (false, null);
        }

        return (true, token.User);
    }

    /// <summary>
    /// Revokes a refresh token
    /// </summary>
    public async Task RevokeRefreshTokenAsync(
        string refreshToken,
        string? replacedByToken = null,
        CancellationToken cancellationToken = default)
    {
        var token = await _dbContext.RefreshTokens
            .FirstOrDefaultAsync(rt => rt.Token == refreshToken, cancellationToken);

        if (token == null)
        {
            _logger.LogWarning("Attempted to revoke non-existent refresh token");
            return;
        }

        token.IsRevoked = true;
        token.RevokedAt = DateTime.UtcNow;
        token.ReplacedByToken = replacedByToken;

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Revoked refresh token for user {UserId}", token.UserId);
    }

    /// <summary>
    /// Revokes all refresh tokens for a user
    /// </summary>
    public async Task RevokeAllUserRefreshTokensAsync(string userId, CancellationToken cancellationToken = default)
    {
        var tokens = await _dbContext.RefreshTokens
            .Where(rt => rt.UserId == userId && !rt.IsRevoked)
            .ToListAsync(cancellationToken);

        foreach (var token in tokens)
        {
            token.IsRevoked = true;
            token.RevokedAt = DateTime.UtcNow;
        }

        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Revoked {Count} refresh tokens for user {UserId}", tokens.Count, userId);
    }

    /// <summary>
    /// Cleans up expired refresh tokens
    /// </summary>
    public async Task CleanupExpiredTokensAsync(CancellationToken cancellationToken = default)
    {
        var expiredTokens = await _dbContext.RefreshTokens
            .Where(rt => rt.ExpiresAt < DateTime.UtcNow)
            .ToListAsync(cancellationToken);

        _dbContext.RefreshTokens.RemoveRange(expiredTokens);
        await _dbContext.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Cleaned up {Count} expired refresh tokens", expiredTokens.Count);
    }

    /// <summary>
    /// Generates a cryptographically secure random token
    /// </summary>
    private static string GenerateSecureRandomToken()
    {
        var randomBytes = new byte[64];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }
}
