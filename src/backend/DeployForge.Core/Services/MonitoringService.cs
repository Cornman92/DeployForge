using System.Diagnostics;
using System.Runtime.Versioning;
using DeployForge.Common.Models.Monitoring;
using DeployForge.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace DeployForge.Core.Services;

/// <summary>
/// Service for system monitoring and health metrics
/// </summary>
[SupportedOSPlatform("windows")]
public class MonitoringService : IMonitoringService
{
    private readonly ILogger<MonitoringService> _logger;
    private readonly IProgressService _progressService;
    private readonly Timer? _metricsCollectionTimer;
    private readonly object _lock = new();
    private readonly List<SystemMetrics> _metricsHistory = new();
    private readonly List<AlertEvent> _alertHistory = new();
    private readonly Dictionary<AlertType, DateTime> _lastAlertTimes = new();

    private const int MaxHistorySize = 1000; // Keep last 1000 metrics snapshots
    private const int CollectionIntervalMs = 5000; // Collect every 5 seconds

    private AlertThreshold _alertThresholds = new();
    private bool _isMonitoring;
    private DateTime _startTime = DateTime.UtcNow;
    private PerformanceCounter? _cpuCounter;
    private PerformanceCounter? _memoryCounter;

    public bool IsMonitoring => _isMonitoring;

    public MonitoringService(
        ILogger<MonitoringService> logger,
        IProgressService progressService)
    {
        _logger = logger;
        _progressService = progressService;

        try
        {
            // Initialize performance counters (Windows-specific)
            _cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
            _memoryCounter = new PerformanceCounter("Memory", "% Committed Bytes In Use");

            // Initial read to initialize counters
            _cpuCounter.NextValue();
            _memoryCounter.NextValue();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to initialize performance counters. Metrics may be limited.");
        }

        _metricsCollectionTimer = new Timer(CollectMetrics, null, Timeout.Infinite, Timeout.Infinite);
    }

    public Task<SystemMetrics> GetCurrentMetricsAsync(CancellationToken cancellationToken = default)
    {
        var metrics = CollectCurrentMetrics();
        return Task.FromResult(metrics);
    }

    public Task<IEnumerable<SystemMetrics>> GetMetricsHistoryAsync(
        DateTime startTime,
        DateTime endTime,
        CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            var history = _metricsHistory
                .Where(m => m.Timestamp >= startTime && m.Timestamp <= endTime)
                .OrderBy(m => m.Timestamp)
                .ToList();

            return Task.FromResult<IEnumerable<SystemMetrics>>(history);
        }
    }

    public Task<PerformanceMetrics> GetPerformanceMetricsAsync(CancellationToken cancellationToken = default)
    {
        var metrics = CalculatePerformanceMetrics();
        return Task.FromResult(metrics);
    }

    public Task ConfigureAlertThresholdsAsync(AlertThreshold thresholds, CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            _alertThresholds = thresholds;
            _logger.LogInformation("Alert thresholds updated");
        }

        return Task.CompletedTask;
    }

    public Task<AlertThreshold> GetAlertThresholdsAsync(CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            return Task.FromResult(_alertThresholds);
        }
    }

    public Task<IEnumerable<AlertEvent>> GetAlertHistoryAsync(
        DateTime? startTime = null,
        DateTime? endTime = null,
        CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            var query = _alertHistory.AsEnumerable();

            if (startTime.HasValue)
                query = query.Where(a => a.Timestamp >= startTime.Value);

            if (endTime.HasValue)
                query = query.Where(a => a.Timestamp <= endTime.Value);

            var history = query.OrderByDescending(a => a.Timestamp).ToList();
            return Task.FromResult<IEnumerable<AlertEvent>>(history);
        }
    }

    public Task StartMonitoringAsync(CancellationToken cancellationToken = default)
    {
        if (_isMonitoring)
        {
            _logger.LogWarning("Monitoring is already started");
            return Task.CompletedTask;
        }

        _isMonitoring = true;
        _startTime = DateTime.UtcNow;
        _metricsCollectionTimer?.Change(0, CollectionIntervalMs);

        _logger.LogInformation("Monitoring started");
        return Task.CompletedTask;
    }

    public Task StopMonitoringAsync(CancellationToken cancellationToken = default)
    {
        if (!_isMonitoring)
        {
            _logger.LogWarning("Monitoring is not started");
            return Task.CompletedTask;
        }

        _isMonitoring = false;
        _metricsCollectionTimer?.Change(Timeout.Infinite, Timeout.Infinite);

        _logger.LogInformation("Monitoring stopped");
        return Task.CompletedTask;
    }

    private void CollectMetrics(object? state)
    {
        try
        {
            var metrics = CollectCurrentMetrics();

            lock (_lock)
            {
                _metricsHistory.Add(metrics);

                // Keep only the last MaxHistorySize metrics
                if (_metricsHistory.Count > MaxHistorySize)
                {
                    _metricsHistory.RemoveAt(0);
                }
            }

            // Check for threshold violations
            CheckThresholds(metrics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error collecting metrics");
        }
    }

    private SystemMetrics CollectCurrentMetrics()
    {
        var metrics = new SystemMetrics
        {
            Timestamp = DateTime.UtcNow,
            Uptime = DateTime.UtcNow - _startTime
        };

        try
        {
            // CPU Usage
            if (_cpuCounter != null)
            {
                metrics.CpuUsage = Math.Round(_cpuCounter.NextValue(), 2);
            }

            // Memory Usage
            if (_memoryCounter != null)
            {
                metrics.MemoryUsage = Math.Round(_memoryCounter.NextValue(), 2);
            }

            // Get memory info using GC
            var process = Process.GetCurrentProcess();
            metrics.UsedMemoryBytes = process.WorkingSet64;

            // Get total physical memory (Windows)
            var memoryStatus = new MEMORYSTATUSEX();
            if (GlobalMemoryStatusEx(memoryStatus))
            {
                metrics.TotalMemoryBytes = (long)memoryStatus.ullTotalPhys;
                metrics.AvailableMemoryBytes = (long)memoryStatus.ullAvailPhys;

                if (metrics.TotalMemoryBytes > 0)
                {
                    metrics.MemoryUsage = Math.Round(
                        ((double)(metrics.TotalMemoryBytes - metrics.AvailableMemoryBytes) / metrics.TotalMemoryBytes) * 100,
                        2);
                }
            }

            // Disk Usage
            var drives = DriveInfo.GetDrives()
                .Where(d => d.IsReady && d.DriveType == DriveType.Fixed);

            var primaryDrive = drives.FirstOrDefault();
            if (primaryDrive != null)
            {
                metrics.TotalDiskSpaceBytes = primaryDrive.TotalSize;
                metrics.AvailableDiskSpaceBytes = primaryDrive.AvailableFreeSpace;
                metrics.DiskUsage = Math.Round(
                    ((double)(metrics.TotalDiskSpaceBytes - metrics.AvailableDiskSpaceBytes) / metrics.TotalDiskSpaceBytes) * 100,
                    2);
            }

            // Active operations (from progress service)
            metrics.ActiveOperations = _progressService.GetActiveOperations();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error collecting system metrics");
        }

        return metrics;
    }

    private PerformanceMetrics CalculatePerformanceMetrics()
    {
        lock (_lock)
        {
            var metrics = new PerformanceMetrics
            {
                Timestamp = DateTime.UtcNow
            };

            if (_metricsHistory.Count == 0)
                return metrics;

            // Calculate averages
            metrics.AverageCpuUsage = Math.Round(_metricsHistory.Average(m => m.CpuUsage), 2);
            metrics.AverageMemoryUsage = Math.Round(_metricsHistory.Average(m => m.MemoryUsage), 2);
            metrics.PeakCpuUsage = Math.Round(_metricsHistory.Max(m => m.CpuUsage), 2);
            metrics.PeakMemoryUsage = Math.Round(_metricsHistory.Max(m => m.MemoryUsage), 2);

            // Request counts (from last hour and day)
            var oneHourAgo = DateTime.UtcNow.AddHours(-1);
            var oneDayAgo = DateTime.UtcNow.AddDays(-1);

            metrics.RequestsLastHour = _metricsHistory.Count(m => m.Timestamp >= oneHourAgo);
            metrics.RequestsLastDay = _metricsHistory.Count(m => m.Timestamp >= oneDayAgo);

            return metrics;
        }
    }

    private void CheckThresholds(SystemMetrics metrics)
    {
        lock (_lock)
        {
            // Check CPU threshold
            if (_alertThresholds.EnableCpuAlerts && metrics.CpuUsage > _alertThresholds.CpuThreshold)
            {
                TriggerAlert(AlertType.CpuUsage, AlertSeverity.Warning,
                    $"CPU usage ({metrics.CpuUsage}%) exceeded threshold ({_alertThresholds.CpuThreshold}%)",
                    metrics.CpuUsage, _alertThresholds.CpuThreshold);
            }

            // Check Memory threshold
            if (_alertThresholds.EnableMemoryAlerts && metrics.MemoryUsage > _alertThresholds.MemoryThreshold)
            {
                TriggerAlert(AlertType.MemoryUsage, AlertSeverity.Warning,
                    $"Memory usage ({metrics.MemoryUsage}%) exceeded threshold ({_alertThresholds.MemoryThreshold}%)",
                    metrics.MemoryUsage, _alertThresholds.MemoryThreshold);
            }

            // Check Disk threshold
            if (_alertThresholds.EnableDiskAlerts && metrics.DiskUsage > _alertThresholds.DiskThreshold)
            {
                TriggerAlert(AlertType.DiskUsage, AlertSeverity.Warning,
                    $"Disk usage ({metrics.DiskUsage}%) exceeded threshold ({_alertThresholds.DiskThreshold}%)",
                    metrics.DiskUsage, _alertThresholds.DiskThreshold);
            }

            // Check concurrent operations threshold
            if (_alertThresholds.EnableOperationAlerts && metrics.ActiveOperations > _alertThresholds.MaxConcurrentOperations)
            {
                TriggerAlert(AlertType.ConcurrentOperations, AlertSeverity.Warning,
                    $"Active operations ({metrics.ActiveOperations}) exceeded threshold ({_alertThresholds.MaxConcurrentOperations})",
                    metrics.ActiveOperations, _alertThresholds.MaxConcurrentOperations);
            }
        }
    }

    private void TriggerAlert(AlertType type, AlertSeverity severity, string message, double currentValue, double thresholdValue)
    {
        // Check cooldown period to prevent alert spam
        if (_lastAlertTimes.TryGetValue(type, out var lastTime))
        {
            var timeSinceLastAlert = DateTime.UtcNow - lastTime;
            if (timeSinceLastAlert.TotalMinutes < _alertThresholds.AlertCooldownMinutes)
            {
                return; // Skip this alert due to cooldown
            }
        }

        var alert = new AlertEvent
        {
            Type = type,
            Severity = severity,
            Message = message,
            CurrentValue = currentValue,
            ThresholdValue = thresholdValue,
            Timestamp = DateTime.UtcNow
        };

        _alertHistory.Add(alert);
        _lastAlertTimes[type] = DateTime.UtcNow;

        _logger.LogWarning("Alert triggered: {Type} - {Message}", type, message);
    }

    // Windows API for memory info
    [System.Runtime.InteropServices.DllImport("kernel32.dll", SetLastError = true)]
    [return: System.Runtime.InteropServices.MarshalAs(System.Runtime.InteropServices.UnmanagedType.Bool)]
    private static extern bool GlobalMemoryStatusEx([System.Runtime.InteropServices.In, System.Runtime.InteropServices.Out] MEMORYSTATUSEX lpBuffer);

    [System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential)]
    private class MEMORYSTATUSEX
    {
        public uint dwLength = (uint)System.Runtime.InteropServices.Marshal.SizeOf(typeof(MEMORYSTATUSEX));
        public uint dwMemoryLoad;
        public ulong ullTotalPhys;
        public ulong ullAvailPhys;
        public ulong ullTotalPageFile;
        public ulong ullAvailPageFile;
        public ulong ullTotalVirtual;
        public ulong ullAvailVirtual;
        public ulong ullAvailExtendedVirtual;
    }
}
