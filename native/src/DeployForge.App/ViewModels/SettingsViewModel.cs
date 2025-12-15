using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Interfaces;

namespace DeployForge.App.ViewModels;

/// <summary>
/// ViewModel for the Settings page.
/// </summary>
public partial class SettingsViewModel : PageViewModelBase
{
    private readonly ISettingsService _settingsService;
    
    public override string Title => "Settings";
    public override string Icon => "\uE713";
    
    #region General Settings
    
    [ObservableProperty]
    private string _theme = "Dark";
    
    [ObservableProperty]
    private bool _showAdvancedOptions;
    
    [ObservableProperty]
    private bool _checkForUpdates = true;
    
    [ObservableProperty]
    private bool _showConfirmations = true;
    
    #endregion
    
    #region Path Settings
    
    [ObservableProperty]
    private string _defaultMountPath = string.Empty;
    
    [ObservableProperty]
    private string _backupDirectory = string.Empty;
    
    [ObservableProperty]
    private string _templatesDirectory = string.Empty;
    
    #endregion
    
    #region Image Settings
    
    [ObservableProperty]
    private bool _createBackups = true;
    
    [ObservableProperty]
    private int _maxConcurrentOperations = 4;
    
    #endregion
    
    #region Logging Settings
    
    [ObservableProperty]
    private string _logLevel = "Info";
    
    #endregion
    
    /// <summary>
    /// Available themes.
    /// </summary>
    public ObservableCollection<string> Themes { get; } = new()
    {
        "Dark",
        "Light",
        "System"
    };
    
    /// <summary>
    /// Available log levels.
    /// </summary>
    public ObservableCollection<string> LogLevels { get; } = new()
    {
        "Debug",
        "Info",
        "Warning",
        "Error"
    };
    
    /// <summary>
    /// App version information.
    /// </summary>
    public string AppVersion => "2.0.0";
    
    /// <summary>
    /// App copyright.
    /// </summary>
    public string Copyright => "© 2024 DeployForge";
    
    public SettingsViewModel(ISettingsService settingsService)
    {
        _settingsService = settingsService;
    }
    
    public override async Task OnNavigatedToAsync()
    {
        await LoadSettingsAsync();
    }
    
    /// <summary>
    /// Loads settings from the service.
    /// </summary>
    private async Task LoadSettingsAsync()
    {
        try
        {
            await _settingsService.LoadAsync();
            
            Theme = _settingsService.Theme;
            ShowAdvancedOptions = _settingsService.ShowAdvancedOptions;
            DefaultMountPath = _settingsService.DefaultMountPath;
            
            if (_settingsService is SettingsService ss)
            {
                CheckForUpdates = ss.CheckForUpdates;
                ShowConfirmations = ss.ShowConfirmations;
                BackupDirectory = ss.BackupDirectory;
                CreateBackups = ss.CreateBackups;
                MaxConcurrentOperations = ss.MaxConcurrentOperations;
                LogLevel = ss.LogLevel;
            }
        }
        catch
        {
            SetError("Failed to load settings");
        }
    }
    
    /// <summary>
    /// Saves settings.
    /// </summary>
    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        try
        {
            _settingsService.Theme = Theme;
            _settingsService.ShowAdvancedOptions = ShowAdvancedOptions;
            _settingsService.DefaultMountPath = DefaultMountPath;
            
            if (_settingsService is SettingsService ss)
            {
                ss.CheckForUpdates = CheckForUpdates;
                ss.ShowConfirmations = ShowConfirmations;
                ss.BackupDirectory = BackupDirectory;
                ss.CreateBackups = CreateBackups;
                ss.MaxConcurrentOperations = MaxConcurrentOperations;
                ss.LogLevel = LogLevel;
            }
            
            await _settingsService.SaveAsync();
            ClearError();
        }
        catch (Exception ex)
        {
            SetError($"Failed to save settings: {ex.Message}");
        }
    }
    
    /// <summary>
    /// Resets settings to defaults.
    /// </summary>
    [RelayCommand]
    private async Task ResetSettingsAsync()
    {
        if (_settingsService is SettingsService ss)
        {
            await ss.ResetAsync();
        }
        
        await LoadSettingsAsync();
    }
    
    /// <summary>
    /// Browses for mount path.
    /// </summary>
    [RelayCommand]
    private async Task BrowseMountPathAsync()
    {
        // Folder picker will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Sets the mount path.
    /// </summary>
    public void SetMountPath(string path)
    {
        if (!string.IsNullOrWhiteSpace(path))
        {
            DefaultMountPath = path;
        }
    }
    
    /// <summary>
    /// Browses for backup directory.
    /// </summary>
    [RelayCommand]
    private async Task BrowseBackupDirectoryAsync()
    {
        // Folder picker will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Sets the backup directory.
    /// </summary>
    public void SetBackupDirectory(string path)
    {
        if (!string.IsNullOrWhiteSpace(path))
        {
            BackupDirectory = path;
        }
    }
    
    /// <summary>
    /// Opens the logs folder.
    /// </summary>
    [RelayCommand]
    private async Task OpenLogsFolderAsync()
    {
        try
        {
            var logsPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "DeployForge",
                "Logs");
            
            if (!Directory.Exists(logsPath))
            {
                Directory.CreateDirectory(logsPath);
            }
            
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = logsPath,
                UseShellExecute = true
            });
        }
        catch
        {
            // Ignore errors
        }
        
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Opens the templates folder.
    /// </summary>
    [RelayCommand]
    private async Task OpenTemplatesFolderAsync()
    {
        try
        {
            var templatesPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "DeployForge",
                "Templates");
            
            if (!Directory.Exists(templatesPath))
            {
                Directory.CreateDirectory(templatesPath);
            }
            
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = templatesPath,
                UseShellExecute = true
            });
        }
        catch
        {
            // Ignore errors
        }
        
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Exports settings to file.
    /// </summary>
    [RelayCommand]
    private async Task ExportSettingsAsync()
    {
        // File save dialog will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Imports settings from file.
    /// </summary>
    [RelayCommand]
    private async Task ImportSettingsAsync()
    {
        // File open dialog will be handled in View
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Exports settings to a path.
    /// </summary>
    public async Task ExportToPathAsync(string path)
    {
        if (_settingsService is SettingsService ss)
        {
            await ss.ExportAsync(path);
        }
    }
    
    /// <summary>
    /// Imports settings from a path.
    /// </summary>
    public async Task ImportFromPathAsync(string path)
    {
        if (_settingsService is SettingsService ss)
        {
            await ss.ImportAsync(path);
            await LoadSettingsAsync();
        }
    }
    
    /// <summary>
    /// Clears recent images.
    /// </summary>
    [RelayCommand]
    private async Task ClearRecentImagesAsync()
    {
        if (_settingsService is SettingsService ss)
        {
            ss.ClearRecentImages();
            await ss.SaveAsync();
        }
    }
    
    partial void OnThemeChanged(string value)
    {
        // Theme change will trigger app-level theme update
        _ = SaveSettingsAsync();
    }
}
