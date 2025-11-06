using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Dashboard ViewModel
/// </summary>
public partial class DashboardViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ILogger<DashboardViewModel> _logger;

    private string _systemInfo = string.Empty;
    private int _mountedImagesCount;
    private int _runningOperationsCount;
    private int _activeBatchOperationsCount;
    private int _totalTemplatesCount;
    private string _apiVersion = string.Empty;
    private double _systemCpuUsage;
    private double _systemMemoryUsage;
    private string _lastAuditEntry = string.Empty;
    private DateTime _lastRefreshTime;

    // Statistics
    private int _totalOperationsToday;
    private int _successfulOperationsToday;
    private double _successRateToday;

    public string SystemInfo
    {
        get => _systemInfo;
        set => SetProperty(ref _systemInfo, value);
    }

    public int MountedImagesCount
    {
        get => _mountedImagesCount;
        set => SetProperty(ref _mountedImagesCount, value);
    }

    public int RunningOperationsCount
    {
        get => _runningOperationsCount;
        set => SetProperty(ref _runningOperationsCount, value);
    }

    public int ActiveBatchOperationsCount
    {
        get => _activeBatchOperationsCount;
        set => SetProperty(ref _activeBatchOperationsCount, value);
    }

    public int TotalTemplatesCount
    {
        get => _totalTemplatesCount;
        set => SetProperty(ref _totalTemplatesCount, value);
    }

    public string ApiVersion
    {
        get => _apiVersion;
        set => SetProperty(ref _apiVersion, value);
    }

    public double SystemCpuUsage
    {
        get => _systemCpuUsage;
        set => SetProperty(ref _systemCpuUsage, value);
    }

    public double SystemMemoryUsage
    {
        get => _systemMemoryUsage;
        set => SetProperty(ref _systemMemoryUsage, value);
    }

    public string LastAuditEntry
    {
        get => _lastAuditEntry;
        set => SetProperty(ref _lastAuditEntry, value);
    }

    public DateTime LastRefreshTime
    {
        get => _lastRefreshTime;
        set => SetProperty(ref _lastRefreshTime, value);
    }

    public int TotalOperationsToday
    {
        get => _totalOperationsToday;
        set => SetProperty(ref _totalOperationsToday, value);
    }

    public int SuccessfulOperationsToday
    {
        get => _successfulOperationsToday;
        set => SetProperty(ref _successfulOperationsToday, value);
    }

    public double SuccessRateToday
    {
        get => _successRateToday;
        set => SetProperty(ref _successRateToday, value);
    }

    public ObservableCollection<RecentOperation> RecentOperations { get; } = new();
    public ObservableCollection<QuickAction> QuickActions { get; } = new();

    public DashboardViewModel(
        IApiClient apiClient,
        ILogger<DashboardViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;

        InitializeQuickActions();
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        await LoadDashboardDataAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadDashboardDataAsync();
    }

    [RelayCommand]
    private async Task RunPreFlightChecksAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Running pre-flight checks...";

            var result = await _apiClient.GetAsync<PreFlightCheckResult>("validation/preflight");
            if (result != null)
            {
                var message = result.IsReady
                    ? "All pre-flight checks passed!"
                    : $"Pre-flight checks failed: {string.Join(", ", result.BlockingIssues)}";

                StatusMessage = message;
                _logger.LogInformation(message);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to run pre-flight checks");
            StatusMessage = "Failed to run pre-flight checks";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void InitializeQuickActions()
    {
        QuickActions.Add(new QuickAction
        {
            Name = "Mount Image",
            Icon = "ImagePlus",
            Description = "Mount a Windows image"
        });
        QuickActions.Add(new QuickAction
        {
            Name = "Apply Template",
            Icon = "FileDocument",
            Description = "Apply template to image"
        });
        QuickActions.Add(new QuickAction
        {
            Name = "Validate Image",
            Icon = "CheckCircle",
            Description = "Validate image integrity"
        });
        QuickActions.Add(new QuickAction
        {
            Name = "Batch Operations",
            Icon = "ViewList",
            Description = "Process multiple images"
        });
    }

    private async Task LoadDashboardDataAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading dashboard data...";

            // Load health info
            var health = await _apiClient.GetAsync<HealthInfo>("health/info");
            if (health != null)
            {
                ApiVersion = health.Version ?? "Unknown";
                SystemInfo = $"{health.MachineName} - {health.OSVersion}";
                SystemCpuUsage = health.CpuUsage;
                SystemMemoryUsage = health.MemoryUsage;
            }

            // Load mounted images count
            try
            {
                var mountedImages = await _apiClient.GetAsync<List<object>>("images/mounted");
                MountedImagesCount = mountedImages?.Count ?? 0;
            }
            catch
            {
                MountedImagesCount = 0;
            }

            // Load active batch operations
            try
            {
                var activeBatch = await _apiClient.GetAsync<List<object>>("batchoperations/active");
                ActiveBatchOperationsCount = activeBatch?.Count ?? 0;
            }
            catch
            {
                ActiveBatchOperationsCount = 0;
            }

            // Load templates count
            try
            {
                var templates = await _apiClient.GetAsync<List<object>>("imagetemplates");
                TotalTemplatesCount = templates?.Count ?? 0;
            }
            catch
            {
                TotalTemplatesCount = 0;
            }

            // Load audit log statistics
            try
            {
                var today = DateTime.Today;
                var auditStats = await _apiClient.GetAsync<AuditStatistics>(
                    $"auditlog/statistics?startDate={today:yyyy-MM-dd}");

                if (auditStats != null)
                {
                    TotalOperationsToday = auditStats.TotalOperations;
                    SuccessfulOperationsToday = auditStats.SuccessfulOperations;
                    SuccessRateToday = auditStats.SuccessRate;
                }
            }
            catch
            {
                TotalOperationsToday = 0;
                SuccessfulOperationsToday = 0;
                SuccessRateToday = 0;
            }

            // Load recent audit entries
            try
            {
                var recentLogs = await _apiClient.GetAsync<List<AuditEntry>>("auditlog/recent?count=10");
                if (recentLogs != null && recentLogs.Count > 0)
                {
                    RecentOperations.Clear();
                    foreach (var log in recentLogs.Take(5))
                    {
                        RecentOperations.Add(new RecentOperation
                        {
                            Name = $"{log.Category}: {log.Action}",
                            Timestamp = log.Timestamp,
                            Status = log.Result,
                            Duration = (int)log.DurationMs,
                            Description = log.Description
                        });
                    }

                    var lastLog = recentLogs.First();
                    LastAuditEntry = $"{lastLog.Action} - {lastLog.Result}";
                }
            }
            catch
            {
                LastAuditEntry = "No recent activity";
            }

            LastRefreshTime = DateTime.Now;
            StatusMessage = "Dashboard loaded successfully";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load dashboard data");
            StatusMessage = "Failed to load dashboard data";
        }
        finally
        {
            IsBusy = false;
        }
    }
}

public class RecentOperation
{
    public string Name { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public string Status { get; set; } = string.Empty;
    public int Duration { get; set; }
    public string Description { get; set; } = string.Empty;
}

public class QuickAction
{
    public string Name { get; set; } = string.Empty;
    public string Icon { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
}

public class HealthInfo
{
    public string? Version { get; set; }
    public string? Environment { get; set; }
    public string? MachineName { get; set; }
    public string? OSVersion { get; set; }
    public int ProcessorCount { get; set; }
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
}

public class PreFlightCheckResult
{
    public bool IsReady { get; set; }
    public List<string> BlockingIssues { get; set; } = new();
    public List<string> Warnings { get; set; } = new();
}

public class AuditStatistics
{
    public int TotalOperations { get; set; }
    public int SuccessfulOperations { get; set; }
    public int FailedOperations { get; set; }
    public double SuccessRate { get; set; }
}

public class AuditEntry
{
    public string Category { get; set; } = string.Empty;
    public string Action { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public string Result { get; set; } = string.Empty;
    public long DurationMs { get; set; }
    public string Description { get; set; } = string.Empty;
}
