using System.Threading.RateLimiting;

namespace DeployForge.Api.Configuration;

/// <summary>
/// Configuration for API rate limiting
/// </summary>
public class RateLimitConfiguration
{
    /// <summary>
    /// Global rate limit configuration
    /// </summary>
    public GlobalRateLimitOptions Global { get; set; } = new();

    /// <summary>
    /// Per-endpoint rate limit configuration
    /// </summary>
    public EndpointRateLimitOptions Endpoints { get; set; } = new();

    /// <summary>
    /// Per-IP rate limit configuration
    /// </summary>
    public IpRateLimitOptions IpRateLimiting { get; set; } = new();
}

/// <summary>
/// Global rate limit options
/// </summary>
public class GlobalRateLimitOptions
{
    /// <summary>
    /// Whether global rate limiting is enabled
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Maximum requests per window
    /// </summary>
    public int PermitLimit { get; set; } = 100;

    /// <summary>
    /// Time window in seconds
    /// </summary>
    public int WindowSeconds { get; set; } = 60;

    /// <summary>
    /// Queue limit for requests exceeding the limit
    /// </summary>
    public int QueueLimit { get; set; } = 10;
}

/// <summary>
/// Per-endpoint rate limit options
/// </summary>
public class EndpointRateLimitOptions
{
    /// <summary>
    /// Health check endpoints
    /// </summary>
    public EndpointLimit Health { get; set; } = new() { PermitLimit = 60, WindowSeconds = 60 };

    /// <summary>
    /// Monitoring endpoints
    /// </summary>
    public EndpointLimit Monitoring { get; set; } = new() { PermitLimit = 120, WindowSeconds = 60 };

    /// <summary>
    /// Notification endpoints
    /// </summary>
    public EndpointLimit Notifications { get; set; } = new() { PermitLimit = 30, WindowSeconds = 60 };

    /// <summary>
    /// Report generation endpoints
    /// </summary>
    public EndpointLimit Reports { get; set; } = new() { PermitLimit = 10, WindowSeconds = 60 };

    /// <summary>
    /// Schedule endpoints
    /// </summary>
    public EndpointLimit Schedules { get; set; } = new() { PermitLimit = 20, WindowSeconds = 60 };

    /// <summary>
    /// Image operation endpoints
    /// </summary>
    public EndpointLimit ImageOperations { get; set; } = new() { PermitLimit = 30, WindowSeconds = 60 };
}

/// <summary>
/// Endpoint-specific limit configuration
/// </summary>
public class EndpointLimit
{
    /// <summary>
    /// Maximum requests per window
    /// </summary>
    public int PermitLimit { get; set; }

    /// <summary>
    /// Time window in seconds
    /// </summary>
    public int WindowSeconds { get; set; }

    /// <summary>
    /// Queue limit for requests exceeding the limit
    /// </summary>
    public int QueueLimit { get; set; } = 0;
}

/// <summary>
/// Per-IP rate limiting options
/// </summary>
public class IpRateLimitOptions
{
    /// <summary>
    /// Whether IP-based rate limiting is enabled
    /// </summary>
    public bool Enabled { get; set; } = true;

    /// <summary>
    /// Maximum requests per IP per window
    /// </summary>
    public int PermitLimit { get; set; } = 1000;

    /// <summary>
    /// Time window in seconds
    /// </summary>
    public int WindowSeconds { get; set; } = 60;

    /// <summary>
    /// IP whitelist (no rate limiting)
    /// </summary>
    public List<string> Whitelist { get; set; } = new() { "127.0.0.1", "::1" };

    /// <summary>
    /// IP blacklist (always reject)
    /// </summary>
    public List<string> Blacklist { get; set; } = new();
}
