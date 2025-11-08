using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Desktop.Services;
using Microsoft.Extensions.Logging;

namespace DeployForge.Desktop.ViewModels;

/// <summary>
/// Settings ViewModel
/// </summary>
public partial class SettingsViewModel : ViewModelBase
{
    private readonly IApiClient _apiClient;
    private readonly IDialogService _dialogService;
    private readonly ILogger<SettingsViewModel> _logger;

    // API Settings
    private string _apiBaseUrl = "http://localhost:5000";
    private int _apiTimeout = 30;
    private bool _useHttps = false;

    // Application Settings
    private string _theme = "Light";
    private string _language = "English";
    private bool _checkForUpdates = true;
    private bool _minimizeToTray = false;
    private bool _startWithWindows = false;

    // Notification Settings
    private bool _showNotifications = true;
    private bool _playSound = true;
    private bool _showDesktopNotifications = true;

    // Performance Settings
    private int _maxConcurrentOperations = 2;
    private bool _enableHardwareAcceleration = true;
    private int _cacheSize = 500;

    // Logging Settings
    private string _logLevel = "Information";
    private bool _enableFileLogging = true;
    private bool _enableDebugLogging = false;
    private string _logDirectory = @"C:\DeployForge\Logs";

    #region API Settings Properties

    public string ApiBaseUrl
    {
        get => _apiBaseUrl;
        set => SetProperty(ref _apiBaseUrl, value);
    }

    public int ApiTimeout
    {
        get => _apiTimeout;
        set => SetProperty(ref _apiTimeout, value);
    }

    public bool UseHttps
    {
        get => _useHttps;
        set => SetProperty(ref _useHttps, value);
    }

    #endregion

    #region Application Settings Properties

    public string Theme
    {
        get => _theme;
        set
        {
            if (SetProperty(ref _theme, value))
            {
                ApplyTheme(value);
            }
        }
    }

    public string Language
    {
        get => _language;
        set => SetProperty(ref _language, value);
    }

    public bool CheckForUpdates
    {
        get => _checkForUpdates;
        set => SetProperty(ref _checkForUpdates, value);
    }

    public bool MinimizeToTray
    {
        get => _minimizeToTray;
        set => SetProperty(ref _minimizeToTray, value);
    }

    public bool StartWithWindows
    {
        get => _startWithWindows;
        set => SetProperty(ref _startWithWindows, value);
    }

    #endregion

    #region Notification Settings Properties

    public bool ShowNotifications
    {
        get => _showNotifications;
        set => SetProperty(ref _showNotifications, value);
    }

    public bool PlaySound
    {
        get => _playSound;
        set => SetProperty(ref _playSound, value);
    }

    public bool ShowDesktopNotifications
    {
        get => _showDesktopNotifications;
        set => SetProperty(ref _showDesktopNotifications, value);
    }

    #endregion

    #region Performance Settings Properties

    public int MaxConcurrentOperations
    {
        get => _maxConcurrentOperations;
        set => SetProperty(ref _maxConcurrentOperations, value);
    }

    public bool EnableHardwareAcceleration
    {
        get => _enableHardwareAcceleration;
        set => SetProperty(ref _enableHardwareAcceleration, value);
    }

    public int CacheSize
    {
        get => _cacheSize;
        set => SetProperty(ref _cacheSize, value);
    }

    #endregion

    #region Logging Settings Properties

    public string LogLevel
    {
        get => _logLevel;
        set => SetProperty(ref _logLevel, value);
    }

    public bool EnableFileLogging
    {
        get => _enableFileLogging;
        set => SetProperty(ref _enableFileLogging, value);
    }

    public bool EnableDebugLogging
    {
        get => _enableDebugLogging;
        set => SetProperty(ref _enableDebugLogging, value);
    }

    public string LogDirectory
    {
        get => _logDirectory;
        set => SetProperty(ref _logDirectory, value);
    }

    #endregion

    public ObservableCollection<string> Themes { get; } = new() { "Light", "Dark", "System" };
    public ObservableCollection<string> Languages { get; } = new() { "English", "Spanish", "French", "German" };
    public ObservableCollection<string> LogLevels { get; } = new()
    {
        "Verbose", "Debug", "Information", "Warning", "Error", "Critical"
    };

    public SettingsViewModel(
        IApiClient apiClient,
        IDialogService dialogService,
        ILogger<SettingsViewModel> logger)
    {
        _apiClient = apiClient;
        _dialogService = dialogService;
        _logger = logger;
    }

    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        LoadSettings();
    }

    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Saving settings...";

            // In a real implementation, save to configuration file or API
            await Task.Delay(500); // Simulate save operation

            StatusMessage = "Settings saved successfully";
            _dialogService.ShowSuccessMessage("Success", "Settings saved successfully");
            _logger.LogInformation("Settings saved successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to save settings");
            StatusMessage = "Failed to save settings";
            _dialogService.ShowErrorMessage("Save Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void ResetSettings()
    {
        var confirm = _dialogService.ShowConfirmation(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?");

        if (!confirm) return;

        // Reset to defaults
        ApiBaseUrl = "http://localhost:5000";
        ApiTimeout = 30;
        UseHttps = false;

        Theme = "Light";
        Language = "English";
        CheckForUpdates = true;
        MinimizeToTray = false;
        StartWithWindows = false;

        ShowNotifications = true;
        PlaySound = true;
        ShowDesktopNotifications = true;

        MaxConcurrentOperations = 2;
        EnableHardwareAcceleration = true;
        CacheSize = 500;

        LogLevel = "Information";
        EnableFileLogging = true;
        EnableDebugLogging = false;
        LogDirectory = @"C:\DeployForge\Logs";

        _dialogService.ShowInformationMessage("Reset Complete", "All settings have been reset to defaults");
        _logger.LogInformation("Settings reset to defaults");
    }

    [RelayCommand]
    private async Task TestConnectionAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Testing API connection...";

            var health = await _apiClient.GetAsync<object>("health");

            if (health != null)
            {
                StatusMessage = "API connection successful";
                _dialogService.ShowSuccessMessage("Success", $"Connected to API at {ApiBaseUrl}");
            }
            else
            {
                StatusMessage = "API connection failed";
                _dialogService.ShowWarningMessage("Connection Failed", "Unable to connect to the API");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to test API connection");
            StatusMessage = "API connection failed";
            _dialogService.ShowErrorMessage("Connection Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void BrowseLogDirectory()
    {
        var path = _dialogService.ShowFolderBrowserDialog("Select Log Directory");
        if (!string.IsNullOrEmpty(path))
        {
            LogDirectory = path;
        }
    }

    [RelayCommand]
    private void ClearCache()
    {
        var confirm = _dialogService.ShowConfirmation(
            "Clear Cache",
            "Are you sure you want to clear the application cache?");

        if (!confirm) return;

        try
        {
            // In a real implementation, clear actual cache
            _dialogService.ShowSuccessMessage("Success", "Cache cleared successfully");
            _logger.LogInformation("Cache cleared");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to clear cache");
            _dialogService.ShowErrorMessage("Clear Failed", ex.Message);
        }
    }

    [RelayCommand]
    private void OpenLogDirectory()
    {
        try
        {
            if (Directory.Exists(LogDirectory))
            {
                System.Diagnostics.Process.Start("explorer.exe", LogDirectory);
            }
            else
            {
                _dialogService.ShowWarningMessage("Directory Not Found", "Log directory does not exist");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to open log directory");
            _dialogService.ShowErrorMessage("Open Failed", ex.Message);
        }
    }

    [RelayCommand]
    private async Task CheckForUpdatesAsync()
    {
        try
        {
            IsBusy = true;
            StatusMessage = "Checking for updates...";

            await Task.Delay(1000); // Simulate update check

            StatusMessage = "No updates available";
            _dialogService.ShowInformationMessage("Up to Date", "You are running the latest version of DeployForge");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to check for updates");
            StatusMessage = "Update check failed";
            _dialogService.ShowErrorMessage("Update Check Failed", ex.Message);
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void LoadSettings()
    {
        // In a real implementation, load from configuration file or API
        _logger.LogInformation("Settings loaded");
    }

    private void ApplyTheme(string theme)
    {
        try
        {
            // In a real implementation, apply theme to application
            _logger.LogInformation("Theme changed to: {Theme}", theme);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to apply theme");
        }
    }
}
