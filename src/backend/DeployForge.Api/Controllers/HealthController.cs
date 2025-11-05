using Microsoft.AspNetCore.Mvc;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Health check and status controller
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    private readonly ILogger<HealthController> _logger;

    public HealthController(ILogger<HealthController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Basic health check endpoint
    /// </summary>
    /// <returns>Health status</returns>
    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            Status = "Healthy",
            Version = "1.0.0-alpha",
            Timestamp = DateTime.UtcNow
        });
    }

    /// <summary>
    /// Get detailed system information
    /// </summary>
    /// <returns>System information</returns>
    [HttpGet("info")]
    public IActionResult GetInfo()
    {
        return Ok(new
        {
            Version = "1.0.0-alpha",
            Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"),
            MachineName = Environment.MachineName,
            OSVersion = Environment.OSVersion.ToString(),
            ProcessorCount = Environment.ProcessorCount,
            Is64BitOS = Environment.Is64BitOperatingSystem,
            DotNetVersion = Environment.Version.ToString(),
            Timestamp = DateTime.UtcNow
        });
    }
}
