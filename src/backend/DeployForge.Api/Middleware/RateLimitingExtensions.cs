using System.Threading.RateLimiting;
using DeployForge.Api.Configuration;
using Microsoft.AspNetCore.RateLimiting;

namespace DeployForge.Api.Middleware;

/// <summary>
/// Extension methods for configuring rate limiting
/// </summary>
public static class RateLimitingExtensions
{
    /// <summary>
    /// Add rate limiting services and policies
    /// </summary>
    public static IServiceCollection AddRateLimitingPolicies(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        var rateLimitConfig = configuration.GetSection("RateLimiting").Get<RateLimitConfiguration>()
            ?? new RateLimitConfiguration();

        services.AddRateLimiter(options =>
        {
            // Set rejection status code
            options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

            // Global rate limiter
            if (rateLimitConfig.Global.Enabled)
            {
                options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(context =>
                {
                    var clientIp = GetClientIpAddress(context);

                    // Check IP whitelist
                    if (rateLimitConfig.IpRateLimiting.Whitelist.Contains(clientIp))
                    {
                        return RateLimitPartition.GetNoLimiter("whitelist");
                    }

                    // Check IP blacklist
                    if (rateLimitConfig.IpRateLimiting.Blacklist.Contains(clientIp))
                    {
                        return RateLimitPartition.GetFixedWindowLimiter("blacklist", _ =>
                            new FixedWindowRateLimiterOptions
                            {
                                PermitLimit = 0,
                                Window = TimeSpan.FromSeconds(1)
                            });
                    }

                    // Apply global limit
                    return RateLimitPartition.GetSlidingWindowLimiter(clientIp, _ =>
                        new SlidingWindowRateLimiterOptions
                        {
                            PermitLimit = rateLimitConfig.Global.PermitLimit,
                            Window = TimeSpan.FromSeconds(rateLimitConfig.Global.WindowSeconds),
                            SegmentsPerWindow = 3,
                            QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                            QueueLimit = rateLimitConfig.Global.QueueLimit
                        });
                });
            }

            // Health check endpoints - high limit
            options.AddPolicy("health", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.Health.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.Health.WindowSeconds),
                        SegmentsPerWindow = 3,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.Health.QueueLimit
                    }));

            // Monitoring endpoints - high limit for real-time data
            options.AddPolicy("monitoring", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.Monitoring.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.Monitoring.WindowSeconds),
                        SegmentsPerWindow = 3,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.Monitoring.QueueLimit
                    }));

            // Notification endpoints - medium limit
            options.AddPolicy("notifications", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.Notifications.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.Notifications.WindowSeconds),
                        SegmentsPerWindow = 2,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.Notifications.QueueLimit
                    }));

            // Report generation - low limit (expensive operation)
            options.AddPolicy("reports", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.Reports.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.Reports.WindowSeconds),
                        SegmentsPerWindow = 2,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.Reports.QueueLimit
                    }));

            // Schedule endpoints - medium limit
            options.AddPolicy("schedules", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.Schedules.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.Schedules.WindowSeconds),
                        SegmentsPerWindow = 2,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.Schedules.QueueLimit
                    }));

            // Image operations - medium limit
            options.AddPolicy("images", context =>
                RateLimitPartition.GetSlidingWindowLimiter(
                    GetClientIpAddress(context),
                    _ => new SlidingWindowRateLimiterOptions
                    {
                        PermitLimit = rateLimitConfig.Endpoints.ImageOperations.PermitLimit,
                        Window = TimeSpan.FromSeconds(rateLimitConfig.Endpoints.ImageOperations.WindowSeconds),
                        SegmentsPerWindow = 2,
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = rateLimitConfig.Endpoints.ImageOperations.QueueLimit
                    }));

            // Concurrency limiter for expensive operations
            options.AddConcurrencyLimiter("expensive-ops", limiterOptions =>
            {
                limiterOptions.PermitLimit = 2;
                limiterOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
                limiterOptions.QueueLimit = 5;
            });

            // Configure response when rate limit is exceeded
            options.OnRejected = async (context, cancellationToken) =>
            {
                context.HttpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
                context.HttpContext.Response.Headers.RetryAfter = "60";

                var problemDetails = new
                {
                    type = "https://tools.ietf.org/html/rfc6585#section-4",
                    title = "Too Many Requests",
                    status = StatusCodes.Status429TooManyRequests,
                    detail = "Rate limit exceeded. Please retry after 60 seconds.",
                    instance = context.HttpContext.Request.Path.Value,
                    retryAfter = 60
                };

                await context.HttpContext.Response.WriteAsJsonAsync(problemDetails, cancellationToken);
            };
        });

        return services;
    }

    /// <summary>
    /// Get client IP address from HTTP context
    /// </summary>
    private static string GetClientIpAddress(HttpContext context)
    {
        // Try to get IP from X-Forwarded-For header (for proxies/load balancers)
        var forwardedFor = context.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        if (!string.IsNullOrEmpty(forwardedFor))
        {
            var ips = forwardedFor.Split(',', StringSplitOptions.RemoveEmptyEntries);
            if (ips.Length > 0)
            {
                return ips[0].Trim();
            }
        }

        // Try X-Real-IP header
        var realIp = context.Request.Headers["X-Real-IP"].FirstOrDefault();
        if (!string.IsNullOrEmpty(realIp))
        {
            return realIp;
        }

        // Fallback to RemoteIpAddress
        return context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
    }
}
