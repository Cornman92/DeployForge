using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Monitoring Dashboard ViewModel for real-time system monitoring
/// </summary>
public partial class MonitoringDashboardViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ISignalRService _signalRService;
    private readonly ILogger<MonitoringDashboardViewModel> _logger;
    private System.Threading.Timer? _refreshTimer;

    private double _cpuUsage;
    private double _memoryUsage;
    private long _totalMemoryBytes;
    private long _availableMemoryBytes;
    private double _diskUsage;
    private int _activeOperations;
    private TimeSpan _uptime;
    private bool _isMonitoring;
    private DateTime _lastUpdate;

    // Performance metrics
    private double _avgCpuUsage;
    private double _avgMemoryUsage;
    private double _maxCpuUsage;
    private double _maxMemoryUsage;

    // Alert thresholds
    private double _cpuThreshold = 80.0;
    private double _memoryThreshold = 85.0;
    private double _diskThreshold = 90.0;

    public double CpuUsage
    {
        get => _cpuUsage;
        set => SetProperty(ref _cpuUsage, value);
    }

    public double MemoryUsage
    {
        get => _memoryUsage;
        set => SetProperty(ref _memoryUsage, value);
    }

    public long TotalMemoryBytes
    {
        get => _totalMemoryBytes;
        set => SetProperty(ref _totalMemoryBytes, value);
    }

    public long AvailableMemoryBytes
    {
        get => _availableMemoryBytes;
        set => SetProperty(ref _availableMemoryBytes, value);
    }

    public double DiskUsage
    {
        get => _diskUsage;
        set => SetProperty(ref _diskUsage, value);
    }

    public int ActiveOperations
    {
        get => _activeOperations;
        set => SetProperty(ref _activeOperations, value);
    }

    public TimeSpan Uptime
    {
        get => _uptime;
        set => SetProperty(ref _uptime, value);
    }

    public bool IsMonitoring
    {
        get => _isMonitoring;
        set => SetProperty(ref _isMonitoring, value);
    }

    public DateTime LastUpdate
    {
        get => _lastUpdate;
        set => SetProperty(ref _lastUpdate, value);
    }

    public double AvgCpuUsage
    {
        get => _avgCpuUsage;
        set => SetProperty(ref _avgCpuUsage, value);
    }

    public double AvgMemoryUsage
    {
        get => _avgMemoryUsage;
        set => SetProperty(ref _avgMemoryUsage, value);
    }

    public double MaxCpuUsage
    {
        get => _maxCpuUsage;
        set => SetProperty(ref _maxCpuUsage, value);
    }

    public double MaxMemoryUsage
    {
        get => _maxMemoryUsage;
        set => SetProperty(ref _maxMemoryUsage, value);
    }

    public double CpuThreshold
    {
        get => _cpuThreshold;
        set => SetProperty(ref _cpuThreshold, value);
    }

    public double MemoryThreshold
    {
        get => _memoryThreshold;
        set => SetProperty(ref _memoryThreshold, value);
    }

    public double DiskThreshold
    {
        get => _diskThreshold;
        set => SetProperty(ref _diskThreshold, value);
    }

    public string TotalMemoryDisplay => $"{TotalMemoryBytes / (1024.0 * 1024 * 1024):F2} GB";
    public string AvailableMemoryDisplay => $"{AvailableMemoryBytes / (1024.0 * 1024 * 1024):F2} GB";
    public string UptimeDisplay => $"{(int)Uptime.TotalDays}d {Uptime.Hours}h {Uptime.Minutes}m";

    public ObservableCollection<MetricHistory> CpuHistory { get; } = new();
    public ObservableCollection<MetricHistory> MemoryHistory { get; } = new();
    public ObservableCollection<AlertEventDisplay> RecentAlerts { get; } = new();

    public MonitoringDashboardViewModel(
        IApiClient apiClient,
        ISignalRService signalRService,
        ILogger<MonitoringDashboardViewModel> logger)
    {
        _apiClient = apiClient;
        _signalRService = signalRService;
        _logger = logger;

        // Subscribe to real-time updates
        _signalRService.OnMetricsUpdate(HandleMetricsUpdate);
        _signalRService.OnAlertReceived(HandleAlertReceived);
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();

        // Subscribe to monitoring and alerts via SignalR
        try
        {
            await _signalRService.SubscribeToMonitoringAsync();
            await _signalRService.SubscribeToAlertsAsync();
            _logger.LogInformation("Subscribed to real-time monitoring updates");
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to subscribe to real-time updates, falling back to polling");
            // Fall back to polling if SignalR fails
            StartAutoRefresh();
        }

        await LoadMonitoringDataAsync();
        await LoadPerformanceMetricsAsync();
        await LoadAlertHistoryAsync();
        await LoadAlertThresholdsAsync();
    }

    public override async Task CleanupAsync()
    {
        StopAutoRefresh();

        try
        {
            await _signalRService.UnsubscribeFromMonitoringAsync();
            await _signalRService.UnsubscribeFromAlertsAsync();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error unsubscribing from real-time updates");
        }

        await base.CleanupAsync();
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadMonitoringDataAsync();
        await LoadPerformanceMetricsAsync();
        await LoadAlertHistoryAsync();
    }

    [RelayCommand]
    private async Task ConfigureAlertsAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Configuring alert thresholds...";

            var thresholds = new
            {
                CpuThreshold = CpuThreshold,
                MemoryThreshold = MemoryThreshold,
                DiskThreshold = DiskThreshold,
                Enabled = true
            };

            await _apiClient.PostAsync<object, object>("health/alerts/configure", thresholds);
            StatusMessage = "Alert thresholds configured successfully";
            _logger.LogInformation("Alert thresholds configured: CPU={CpuThreshold}%, Memory={MemoryThreshold}%, Disk={DiskThreshold}%",
                CpuThreshold, MemoryThreshold, DiskThreshold);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to configure alert thresholds");
            StatusMessage = "Failed to configure alert thresholds";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ViewMetricsHistoryAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Loading metrics history...";

            var endTime = DateTime.UtcNow;
            var startTime = endTime.AddHours(-1);

            var history = await _apiClient.GetAsync<List<SystemMetric>>(
                $"health/metrics/history?startTime={startTime:o}&endTime={endTime:o}");

            if (history != null && history.Count > 0)
            {
                CpuHistory.Clear();
                MemoryHistory.Clear();

                foreach (var metric in history.TakeLast(50))
                {
                    CpuHistory.Add(new MetricHistory
                    {
                        Timestamp = metric.Timestamp,
                        Value = metric.CpuUsage
                    });

                    MemoryHistory.Add(new MetricHistory
                    {
                        Timestamp = metric.Timestamp,
                        Value = metric.MemoryUsage
                    });
                }

                StatusMessage = $"Loaded {history.Count} historical metrics";
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load metrics history");
            StatusMessage = "Failed to load metrics history";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadMonitoringDataAsync()
    {
        try
        {
            var metrics = await _apiClient.GetAsync<SystemMetric>("health/metrics");
            if (metrics != null)
            {
                CpuUsage = metrics.CpuUsage;
                MemoryUsage = metrics.MemoryUsage;
                TotalMemoryBytes = metrics.TotalMemoryBytes;
                AvailableMemoryBytes = metrics.AvailableMemoryBytes;
                DiskUsage = metrics.DiskUsage;
                ActiveOperations = metrics.ActiveOperations;
                Uptime = metrics.Uptime;
                LastUpdate = DateTime.Now;
                IsMonitoring = true;

                OnPropertyChanged(nameof(TotalMemoryDisplay));
                OnPropertyChanged(nameof(AvailableMemoryDisplay));
                OnPropertyChanged(nameof(UptimeDisplay));
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load monitoring data");
            IsMonitoring = false;
        }
    }

    private async Task LoadPerformanceMetricsAsync()
    {
        try
        {
            var performance = await _apiClient.GetAsync<PerformanceMetric>("health/performance");
            if (performance != null)
            {
                AvgCpuUsage = performance.AverageCpuUsage;
                AvgMemoryUsage = performance.AverageMemoryUsage;
                MaxCpuUsage = performance.MaxCpuUsage;
                MaxMemoryUsage = performance.MaxMemoryUsage;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load performance metrics");
        }
    }

    private async Task LoadAlertHistoryAsync()
    {
        try
        {
            var alerts = await _apiClient.GetAsync<List<AlertEventDisplay>>("health/alerts/history");
            if (alerts != null)
            {
                RecentAlerts.Clear();
                foreach (var alert in alerts.TakeLast(10))
                {
                    RecentAlerts.Add(alert);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load alert history");
        }
    }

    private async Task LoadAlertThresholdsAsync()
    {
        try
        {
            var thresholds = await _apiClient.GetAsync<AlertThresholdConfig>("health/alerts");
            if (thresholds != null)
            {
                CpuThreshold = thresholds.CpuThreshold;
                MemoryThreshold = thresholds.MemoryThreshold;
                DiskThreshold = thresholds.DiskThreshold;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load alert thresholds");
        }
    }

    private void StartAutoRefresh()
    {
        _refreshTimer = new System.Threading.Timer(
            async _ => await LoadMonitoringDataAsync(),
            null,
            TimeSpan.Zero,
            TimeSpan.FromSeconds(5));
    }

    private void StopAutoRefresh()
    {
        _refreshTimer?.Dispose();
        _refreshTimer = null;
    }

    private void HandleMetricsUpdate(MetricsUpdate metrics)
    {
        // Update UI on the UI thread
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            CpuUsage = metrics.CpuUsage;
            MemoryUsage = metrics.MemoryUsage;
            TotalMemoryBytes = metrics.TotalMemoryBytes;
            AvailableMemoryBytes = metrics.AvailableMemoryBytes;
            DiskUsage = metrics.DiskUsage;
            ActiveOperations = metrics.ActiveOperations;
            Uptime = metrics.Uptime;
            LastUpdate = DateTime.Now;
            IsMonitoring = true;

            OnPropertyChanged(nameof(TotalMemoryDisplay));
            OnPropertyChanged(nameof(AvailableMemoryDisplay));
            OnPropertyChanged(nameof(UptimeDisplay));

            // Add to history
            CpuHistory.Add(new MetricHistory
            {
                Timestamp = metrics.Timestamp,
                Value = metrics.CpuUsage
            });

            MemoryHistory.Add(new MetricHistory
            {
                Timestamp = metrics.Timestamp,
                Value = metrics.MemoryUsage
            });

            // Limit history size
            while (CpuHistory.Count > 50)
            {
                CpuHistory.RemoveAt(0);
            }

            while (MemoryHistory.Count > 50)
            {
                MemoryHistory.RemoveAt(0);
            }
        });
    }

    private void HandleAlertReceived(AlertReceived alert)
    {
        // Add alert to UI on the UI thread
        System.Windows.Application.Current?.Dispatcher.Invoke(() =>
        {
            RecentAlerts.Insert(0, new AlertEventDisplay
            {
                Timestamp = alert.Timestamp,
                MetricType = alert.MetricType,
                Value = alert.Value,
                Threshold = alert.Threshold,
                Message = alert.Message
            });

            // Limit alerts history
            while (RecentAlerts.Count > 10)
            {
                RecentAlerts.RemoveAt(RecentAlerts.Count - 1);
            }

            _logger.LogInformation("Received alert: {Message}", alert.Message);
        });
    }
}

public class SystemMetric
{
    public DateTime Timestamp { get; set; }
    public double CpuUsage { get; set; }
    public double MemoryUsage { get; set; }
    public long TotalMemoryBytes { get; set; }
    public long AvailableMemoryBytes { get; set; }
    public double DiskUsage { get; set; }
    public long TotalDiskSpaceBytes { get; set; }
    public int ActiveOperations { get; set; }
    public TimeSpan Uptime { get; set; }
}

public class PerformanceMetric
{
    public double AverageCpuUsage { get; set; }
    public double AverageMemoryUsage { get; set; }
    public double MaxCpuUsage { get; set; }
    public double MaxMemoryUsage { get; set; }
    public int TotalMetricsCollected { get; set; }
}

public class MetricHistory
{
    public DateTime Timestamp { get; set; }
    public double Value { get; set; }
}

public class AlertEventDisplay
{
    public DateTime Timestamp { get; set; }
    public string MetricType { get; set; } = string.Empty;
    public double Value { get; set; }
    public double Threshold { get; set; }
    public string Message { get; set; } = string.Empty;
}

public class AlertThresholdConfig
{
    public double CpuThreshold { get; set; }
    public double MemoryThreshold { get; set; }
    public double DiskThreshold { get; set; }
    public bool Enabled { get; set; }
}
