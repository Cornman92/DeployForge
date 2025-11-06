using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Main window ViewModel
/// </summary>
public partial class MainViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly ISignalRService _signalRService;
    private readonly ISettingsService _settingsService;
    private readonly IDialogService _dialogService;
    private readonly ILogger<MainViewModel> _logger;

    private ViewModelBase? _currentViewModel;
    private bool _isConnected;
    private string _apiStatus = "Disconnected";

    public ViewModelBase? CurrentViewModel
    {
        get => _currentViewModel;
        set => SetProperty(ref _currentViewModel, value);
    }

    public bool IsConnected
    {
        get => _isConnected;
        set => SetProperty(ref _isConnected, value);
    }

    public string ApiStatus
    {
        get => _apiStatus;
        set => SetProperty(ref _apiStatus, value);
    }

    public ObservableCollection<NavigationItem> NavigationItems { get; } = new();

    public MainViewModel(
        IApiClient apiClient,
        ISignalRService signalRService,
        ISettingsService settingsService,
        IDialogService dialogService,
        ILogger<MainViewModel> logger)
    {
        _apiClient = apiClient;
        _signalRService = signalRService;
        _settingsService = settingsService;
        _dialogService = dialogService;
        _logger = logger;

        InitializeNavigationItems();
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();

        // Test API connection
        await TestConnectionAsync();

        // Connect to SignalR
        try
        {
            await _signalRService.ConnectAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to connect to SignalR");
        }
    }

    private void InitializeNavigationItems()
    {
        NavigationItems.Add(new NavigationItem
        {
            Title = "Dashboard",
            Icon = "ViewDashboard",
            ViewModelType = typeof(DashboardViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Image Management",
            Icon = "Harddisk",
            ViewModelType = typeof(ImageManagementViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Component Manager",
            Icon = "PackageVariantClosed",
            ViewModelType = typeof(ComponentManagerViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Workflow Designer",
            Icon = "FlowChart",
            ViewModelType = typeof(WorkflowDesignerViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Debloat Wizard",
            Icon = "Broom",
            ViewModelType = typeof(DebloatWizardViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Backup Manager",
            Icon = "Backup",
            ViewModelType = typeof(BackupManagerViewModel)
        });

        NavigationItems.Add(new NavigationItem
        {
            Title = "Settings",
            Icon = "Cog",
            ViewModelType = typeof(SettingsViewModel)
        });
    }

    [RelayCommand]
    private async Task TestConnectionAsync()
    {
        try
        {
            IsBusy = true;
            ApiStatus = "Testing...";

            var connected = await _apiClient.TestConnectionAsync();

            IsConnected = connected;
            ApiStatus = connected ? "Connected" : "Disconnected";

            if (!connected)
            {
                _dialogService.ShowWarning("API Offline",
                    "Cannot connect to DeployForge API. Please ensure the API is running on localhost:5000");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Connection test failed");
            IsConnected = false;
            ApiStatus = "Error";
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void Navigate(NavigationItem item)
    {
        _logger.LogInformation("Navigating to {ViewModelType}", item.ViewModelType.Name);

        // In a full implementation, this would resolve the ViewModel from DI
        // and set CurrentViewModel
        StatusMessage = $"Navigated to {item.Title}";
    }

    public override async Task CleanupAsync()
    {
        await _signalRService.DisconnectAsync();
        await _settingsService.SaveAsync();
        await base.CleanupAsync();
    }
}

public class NavigationItem
{
    public string Title { get; set; } = string.Empty;
    public string Icon { get; set; } = string.Empty;
    public Type? ViewModelType { get; set; }
}
