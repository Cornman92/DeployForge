using System.Diagnostics;
using System.Text;

namespace DeployForge.Api.Middleware;

/// <summary>
/// Request/Response logging middleware
/// </summary>
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public RequestLoggingMiddleware(
        RequestDelegate next,
        ILogger<RequestLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        // Generate request ID
        var requestId = Guid.NewGuid().ToString("N");
        context.Items["RequestId"] = requestId;

        // Start timer
        var stopwatch = Stopwatch.StartNew();

        // Log request
        await LogRequest(context, requestId);

        // Capture original response body stream
        var originalBodyStream = context.Response.Body;

        try
        {
            using var responseBody = new MemoryStream();
            context.Response.Body = responseBody;

            // Execute the request
            await _next(context);

            // Log response
            stopwatch.Stop();
            await LogResponse(context, requestId, stopwatch.ElapsedMilliseconds);

            // Copy response to original stream
            await responseBody.CopyToAsync(originalBodyStream);
        }
        finally
        {
            context.Response.Body = originalBodyStream;
        }
    }

    private async Task LogRequest(HttpContext context, string requestId)
    {
        var request = context.Request;

        var logData = new
        {
            RequestId = requestId,
            Method = request.Method,
            Path = request.Path.ToString(),
            QueryString = request.QueryString.ToString(),
            Headers = GetSafeHeaders(request.Headers),
            RemoteIp = context.Connection.RemoteIpAddress?.ToString(),
            UserAgent = request.Headers["User-Agent"].ToString()
        };

        _logger.LogInformation("HTTP Request: {Method} {Path}{QueryString} [{RequestId}]",
            logData.Method, logData.Path, logData.QueryString, logData.RequestId);

        // Log body for POST/PUT/PATCH (excluding large file uploads)
        if ((request.Method == "POST" || request.Method == "PUT" || request.Method == "PATCH") &&
            request.ContentLength.HasValue && request.ContentLength.Value < 10 * 1024) // < 10KB
        {
            request.EnableBuffering();
            var body = await ReadRequestBody(request);
            if (!string.IsNullOrEmpty(body))
            {
                _logger.LogDebug("Request Body [{RequestId}]: {Body}", requestId, body);
            }
        }
    }

    private async Task LogResponse(HttpContext context, string requestId, long elapsedMs)
    {
        var response = context.Response;

        var logLevel = response.StatusCode >= 500 ? LogLevel.Error :
                       response.StatusCode >= 400 ? LogLevel.Warning :
                       LogLevel.Information;

        _logger.Log(logLevel,
            "HTTP Response: {StatusCode} {Method} {Path} - {ElapsedMs}ms [{RequestId}]",
            response.StatusCode,
            context.Request.Method,
            context.Request.Path,
            elapsedMs,
            requestId);

        // Log slow requests
        if (elapsedMs > 5000) // > 5 seconds
        {
            _logger.LogWarning("Slow request detected: {Method} {Path} took {ElapsedMs}ms [{RequestId}]",
                context.Request.Method, context.Request.Path, elapsedMs, requestId);
        }
    }

    private async Task<string> ReadRequestBody(HttpRequest request)
    {
        try
        {
            request.Body.Position = 0;
            using var reader = new StreamReader(request.Body, Encoding.UTF8, leaveOpen: true);
            var body = await reader.ReadToEndAsync();
            request.Body.Position = 0;
            return body;
        }
        catch
        {
            return string.Empty;
        }
    }

    private Dictionary<string, string> GetSafeHeaders(IHeaderDictionary headers)
    {
        var safeHeaders = new Dictionary<string, string>();
        var sensitiveHeaders = new[] { "Authorization", "Cookie", "Set-Cookie", "X-API-Key" };

        foreach (var header in headers)
        {
            if (sensitiveHeaders.Contains(header.Key, StringComparer.OrdinalIgnoreCase))
            {
                safeHeaders[header.Key] = "***REDACTED***";
            }
            else
            {
                safeHeaders[header.Key] = header.Value.ToString();
            }
        }

        return safeHeaders;
    }
}

/// <summary>
/// Extension methods for registering the middleware
/// </summary>
public static class RequestLoggingMiddlewareExtensions
{
    public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<RequestLoggingMiddleware>();
    }
}
