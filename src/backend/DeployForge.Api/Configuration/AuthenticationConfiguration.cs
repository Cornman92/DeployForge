namespace DeployForge.Api.Configuration;

/// <summary>
/// Configuration for authentication and authorization
/// </summary>
public class AuthenticationConfiguration
{
    public JwtConfiguration Jwt { get; set; } = new();
    public ApiKeyConfiguration ApiKey { get; set; } = new();
    public UserConfiguration DefaultUsers { get; set; } = new();
}

/// <summary>
/// JWT token configuration
/// </summary>
public class JwtConfiguration
{
    /// <summary>
    /// Secret key for signing JWT tokens (minimum 256 bits / 32 characters)
    /// </summary>
    public string SecretKey { get; set; } = string.Empty;

    /// <summary>
    /// Token issuer (typically the API URL)
    /// </summary>
    public string Issuer { get; set; } = "DeployForge.Api";

    /// <summary>
    /// Token audience (typically the client application)
    /// </summary>
    public string Audience { get; set; } = "DeployForge.Client";

    /// <summary>
    /// Access token expiration in minutes (default: 15 minutes)
    /// </summary>
    public int AccessTokenExpirationMinutes { get; set; } = 15;

    /// <summary>
    /// Refresh token expiration in days (default: 7 days)
    /// </summary>
    public int RefreshTokenExpirationDays { get; set; } = 7;

    /// <summary>
    /// Require HTTPS for token validation (default: true, set false for development)
    /// </summary>
    public bool RequireHttpsMetadata { get; set; } = true;

    /// <summary>
    /// Validate token issuer
    /// </summary>
    public bool ValidateIssuer { get; set; } = true;

    /// <summary>
    /// Validate token audience
    /// </summary>
    public bool ValidateAudience { get; set; } = true;

    /// <summary>
    /// Validate token lifetime
    /// </summary>
    public bool ValidateLifetime { get; set; } = true;

    /// <summary>
    /// Clock skew for token validation (in minutes, default: 5)
    /// </summary>
    public int ClockSkewMinutes { get; set; } = 5;
}

/// <summary>
/// API key configuration
/// </summary>
public class ApiKeyConfiguration
{
    /// <summary>
    /// Enable API key authentication
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Header name for API key (default: X-API-Key)
    /// </summary>
    public string HeaderName { get; set; } = "X-API-Key";

    /// <summary>
    /// API key expiration in days (default: 365 days)
    /// 0 = never expires
    /// </summary>
    public int ExpirationDays { get; set; } = 365;

    /// <summary>
    /// Maximum number of API keys per user
    /// </summary>
    public int MaxKeysPerUser { get; set; } = 5;

    /// <summary>
    /// API key length (default: 32 characters)
    /// </summary>
    public int KeyLength { get; set; } = 32;
}

/// <summary>
/// Default user configuration for initial setup
/// </summary>
public class UserConfiguration
{
    /// <summary>
    /// Create default admin user on startup
    /// </summary>
    public bool CreateDefaultAdmin { get; set; } = true;

    /// <summary>
    /// Default admin username
    /// </summary>
    public string AdminUsername { get; set; } = "admin";

    /// <summary>
    /// Default admin password (should be changed immediately)
    /// </summary>
    public string AdminPassword { get; set; } = "Admin@123!ChangeME";

    /// <summary>
    /// Default admin email
    /// </summary>
    public string AdminEmail { get; set; } = "admin@deployforge.local";
}

/// <summary>
/// User roles for RBAC
/// </summary>
public static class Roles
{
    /// <summary>
    /// Administrator role - full access to all operations
    /// </summary>
    public const string Admin = "Admin";

    /// <summary>
    /// Standard user role - standard operations (no sensitive config changes)
    /// </summary>
    public const string User = "User";

    /// <summary>
    /// Read-only role - monitoring and report viewing only
    /// </summary>
    public const string ReadOnly = "ReadOnly";

    /// <summary>
    /// All roles as an array
    /// </summary>
    public static readonly string[] All = { Admin, User, ReadOnly };

    /// <summary>
    /// Admin and User roles (excluding ReadOnly)
    /// </summary>
    public static readonly string[] AdminAndUser = { Admin, User };
}
