using System.Net;
using System.Text.Json;

namespace DeployForge.Api.Middleware;

/// <summary>
/// Global error handling middleware
/// </summary>
public class ErrorHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ErrorHandlingMiddleware> _logger;

    public ErrorHandlingMiddleware(
        RequestDelegate next,
        ILogger<ErrorHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception occurred");
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        context.Response.ContentType = "application/json";

        var response = new ErrorResponse
        {
            Timestamp = DateTime.UtcNow,
            Path = context.Request.Path,
            Method = context.Request.Method
        };

        switch (exception)
        {
            case ArgumentException argEx:
                context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
                response.Error = "Bad Request";
                response.Message = argEx.Message;
                break;

            case ArgumentNullException nullEx:
                context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
                response.Error = "Bad Request";
                response.Message = $"Required parameter is null: {nullEx.ParamName}";
                break;

            case InvalidOperationException invalidOp:
                context.Response.StatusCode = (int)HttpStatusCode.Conflict;
                response.Error = "Invalid Operation";
                response.Message = invalidOp.Message;
                break;

            case UnauthorizedAccessException:
                context.Response.StatusCode = (int)HttpStatusCode.Forbidden;
                response.Error = "Forbidden";
                response.Message = "Insufficient permissions. Administrator privileges may be required.";
                break;

            case FileNotFoundException fileNotFound:
                context.Response.StatusCode = (int)HttpStatusCode.NotFound;
                response.Error = "Not Found";
                response.Message = fileNotFound.Message;
                break;

            case DirectoryNotFoundException dirNotFound:
                context.Response.StatusCode = (int)HttpStatusCode.NotFound;
                response.Error = "Not Found";
                response.Message = dirNotFound.Message;
                break;

            case TimeoutException:
                context.Response.StatusCode = (int)HttpStatusCode.RequestTimeout;
                response.Error = "Request Timeout";
                response.Message = "The operation timed out. Consider increasing the timeout value.";
                break;

            case NotImplementedException notImpl:
                context.Response.StatusCode = (int)HttpStatusCode.NotImplemented;
                response.Error = "Not Implemented";
                response.Message = notImpl.Message;
                break;

            case OperationCanceledException:
                context.Response.StatusCode = 499; // Client Closed Request
                response.Error = "Operation Cancelled";
                response.Message = "The operation was cancelled.";
                break;

            default:
                context.Response.StatusCode = (int)HttpStatusCode.InternalServerError;
                response.Error = "Internal Server Error";
                response.Message = "An unexpected error occurred. Please check logs for details.";

                // Only include stack trace in development
                if (context.RequestServices.GetRequiredService<IWebHostEnvironment>().IsDevelopment())
                {
                    response.Details = exception.ToString();
                }
                break;
        }

        response.StatusCode = context.Response.StatusCode;

        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };

        var json = JsonSerializer.Serialize(response, options);
        await context.Response.WriteAsync(json);
    }
}

/// <summary>
/// Error response model
/// </summary>
public class ErrorResponse
{
    public int StatusCode { get; set; }
    public string Error { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public string? Details { get; set; }
    public DateTime Timestamp { get; set; }
    public string Path { get; set; } = string.Empty;
    public string Method { get; set; } = string.Empty;
}

/// <summary>
/// Extension methods for registering the middleware
/// </summary>
public static class ErrorHandlingMiddlewareExtensions
{
    public static IApplicationBuilder UseErrorHandling(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<ErrorHandlingMiddleware>();
    }
}
