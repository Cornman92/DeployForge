using DeployForge.DismEngine;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Runtime.Versioning;
using System.Security.Principal;

namespace DeployForge.Api.Controllers;

/// <summary>
/// Health check and status controller
/// </summary>
[ApiController]
[Route("api/[controller]")]
[SupportedOSPlatform("windows")]
public class HealthController : ControllerBase
{
    private readonly DismManager _dismManager;
    private readonly ILogger<HealthController> _logger;

    public HealthController(
        DismManager dismManager,
        ILogger<HealthController> logger)
    {
        _dismManager = dismManager;
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
            Version = GetVersion(),
            Timestamp = DateTime.UtcNow,
            Uptime = GetUptime()
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
            Version = GetVersion(),
            Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"),
            MachineName = Environment.MachineName,
            OSVersion = Environment.OSVersion.ToString(),
            ProcessorCount = Environment.ProcessorCount,
            Is64BitOS = Environment.Is64BitOperatingSystem,
            DotNetVersion = Environment.Version.ToString(),
            Timestamp = DateTime.UtcNow,
            Uptime = GetUptime(),
            WorkingSetMB = Environment.WorkingSet / (1024 * 1024)
        });
    }

    /// <summary>
    /// Comprehensive diagnostics
    /// </summary>
    [HttpGet("diagnostics")]
    public IActionResult GetDiagnostics()
    {
        _logger.LogInformation("Running diagnostics check");

        var diagnostics = new
        {
            Status = "Healthy",
            Timestamp = DateTime.UtcNow,
            Version = GetVersion(),
            Uptime = GetUptime(),
            System = new
            {
                OperatingSystem = RuntimeInformation.OSDescription,
                Architecture = RuntimeInformation.OSArchitecture.ToString(),
                ProcessorCount = Environment.ProcessorCount,
                MachineName = Environment.MachineName,
                UserName = Environment.UserName,
                DotNetVersion = RuntimeInformation.FrameworkDescription,
                WorkingSetMB = Environment.WorkingSet / (1024 * 1024),
                Is64BitOS = Environment.Is64BitOperatingSystem,
                Is64BitProcess = Environment.Is64BitProcess
            },
            Dism = GetDismStatus(),
            Permissions = GetPermissionsStatus(),
            Services = GetServicesStatus()
        };

        return Ok(diagnostics);
    }

    /// <summary>
    /// Check DISM availability
    /// </summary>
    [HttpGet("dism")]
    public IActionResult CheckDism()
    {
        var status = GetDismStatus();
        return Ok(status);
    }

    /// <summary>
    /// Check permissions
    /// </summary>
    [HttpGet("permissions")]
    public IActionResult CheckPermissions()
    {
        var status = GetPermissionsStatus();
        return Ok(status);
    }

    #region Private Helper Methods

    private string GetVersion()
    {
        var assembly = typeof(HealthController).Assembly;
        var version = assembly.GetName().Version;
        return version?.ToString() ?? "1.0.0.0";
    }

    private TimeSpan GetUptime()
    {
        try
        {
            using var process = Process.GetCurrentProcess();
            return DateTime.UtcNow - process.StartTime.ToUniversalTime();
        }
        catch
        {
            return TimeSpan.Zero;
        }
    }

    private object GetDismStatus()
    {
        try
        {
            _dismManager.Initialize();
            return new
            {
                IsAvailable = true,
                IsInitialized = true,
                Message = "DISM is available and initialized"
            };
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "DISM check failed");
            return new
            {
                IsAvailable = false,
                IsInitialized = false,
                Message = $"DISM not available: {ex.Message}"
            };
        }
    }

    private object GetPermissionsStatus()
    {
        try
        {
            bool isAdmin = false;
            bool canAccessDism = false;
            bool canWriteTemp = false;

            // Check if running as administrator
            try
            {
                using var identity = WindowsIdentity.GetCurrent();
                var principal = new WindowsPrincipal(identity);
                isAdmin = principal.IsInRole(WindowsBuiltInRole.Administrator);
            }
            catch { }

            // Check if can access DISM
            try
            {
                _dismManager.Initialize();
                canAccessDism = true;
            }
            catch { }

            // Check if can write to temp
            var tempFile = Path.Combine(Path.GetTempPath(), $"deployforge_test_{Guid.NewGuid()}.tmp");
            try
            {
                System.IO.File.WriteAllText(tempFile, "test");
                System.IO.File.Delete(tempFile);
                canWriteTemp = true;
            }
            catch { }

            return new
            {
                IsAdministrator = isAdmin,
                CanAccessDism = canAccessDism,
                CanWriteTemp = canWriteTemp,
                Message = isAdmin && canAccessDism
                    ? "All permissions OK"
                    : "Administrator privileges required for full functionality"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to check permissions");
            return new
            {
                IsAdministrator = false,
                CanAccessDism = false,
                CanWriteTemp = false,
                Message = $"Permission check failed: {ex.Message}"
            };
        }
    }

    private object GetServicesStatus()
    {
        return new
        {
            DismManager = _dismManager != null ? "Available" : "Not registered",
            TotalServices = 11,
            RegisteredServices = new[]
            {
                "ImageService",
                "ImageConversionService",
                "BackupService",
                "ComponentService",
                "DriverService",
                "UpdateService",
                "RegistryService",
                "DebloatService",
                "WorkflowService",
                "DeploymentService",
                "LanguageService"
            }
        };
    }

    #endregion
}
