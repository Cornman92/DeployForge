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
    private string _apiVersion = string.Empty;

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

    public string ApiVersion
    {
        get => _apiVersion;
        set => SetProperty(ref _apiVersion, value);
    }

    public ObservableCollection<RecentOperation> RecentOperations { get; } = new();

    public DashboardViewModel(
        IApiClient apiClient,
        ILogger<DashboardViewModel> logger)
    {
        _apiClient = apiClient;
        _logger = logger;
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
            }

            // Load mounted images count
            var mountedImages = await _apiClient.GetAsync<List<object>>("images/mounted");
            MountedImagesCount = mountedImages?.Count ?? 0;

            StatusMessage = "Dashboard loaded";
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
}

public class HealthInfo
{
    public string? Version { get; set; }
    public string? Environment { get; set; }
    public string? MachineName { get; set; }
    public string? OSVersion { get; set; }
    public int ProcessorCount { get; set; }
}
