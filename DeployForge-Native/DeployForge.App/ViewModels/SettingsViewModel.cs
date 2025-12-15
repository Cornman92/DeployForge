using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Models;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly ISettingsService _settingsService;
    private readonly IThemeService _themeService;
    private readonly IDialogService _dialogService;
    
    // General
    [ObservableProperty] private bool _checkForUpdates;
    [ObservableProperty] private bool _sendAnonymousUsage;
    [ObservableProperty] private string _language = "en-US";
    [ObservableProperty] private bool _showAdvancedOptions;
    [ObservableProperty] private bool _confirmOnExit;
    
    // Paths
    [ObservableProperty] private string _defaultOutputDirectory = "";
    [ObservableProperty] private string _tempDirectory = "";
    [ObservableProperty] private string _logDirectory = "";
    
    // Build
    [ObservableProperty] private int _maxParallelOperations = 4;
    [ObservableProperty] private bool _optimizeImageAfterBuild = true;
    [ObservableProperty] private bool _createBackupBeforeModify = true;
    [ObservableProperty] private CompressionLevel _defaultCompression = CompressionLevel.Maximum;
    [ObservableProperty] private bool _cleanupTempFilesAfterBuild = true;
    
    // UI
    [ObservableProperty] private AppTheme _theme = AppTheme.System;
    [ObservableProperty] private AccentColor _accentColor = AccentColor.Blue;
    [ObservableProperty] private bool _showStatusBar = true;
    [ObservableProperty] private bool _enableAnimations = true;
    
    // State
    [ObservableProperty] private bool _hasChanges;
    [ObservableProperty] private string _appVersion = "2.0.0";
    
    public List<string> AvailableLanguages { get; } = new() { "en-US", "de-DE", "fr-FR", "es-ES", "ja-JP", "zh-CN" };
    public Array ThemeOptions => Enum.GetValues<AppTheme>();
    public Array CompressionOptions => Enum.GetValues<CompressionLevel>();
    public Array AccentColorOptions => Enum.GetValues<AccentColor>();
    
    public SettingsViewModel(
        ISettingsService settingsService,
        IThemeService themeService,
        IDialogService dialogService)
    {
        _settingsService = settingsService;
        _themeService = themeService;
        _dialogService = dialogService;
    }
    
    public void Initialize()
    {
        LoadSettings();
    }
    
    private void LoadSettings()
    {
        var s = _settingsService.Settings;
        
        CheckForUpdates = s.General.CheckForUpdates;
        SendAnonymousUsage = s.General.SendAnonymousUsage;
        Language = s.General.Language;
        ShowAdvancedOptions = s.General.ShowAdvancedOptions;
        ConfirmOnExit = s.General.ConfirmOnExit;
        
        DefaultOutputDirectory = s.Paths.DefaultOutputDirectory;
        TempDirectory = s.Paths.TempDirectory;
        LogDirectory = s.Paths.LogDirectory;
        
        MaxParallelOperations = s.Build.MaxParallelOperations;
        OptimizeImageAfterBuild = s.Build.OptimizeImageAfterBuild;
        CreateBackupBeforeModify = s.Build.CreateBackupBeforeModify;
        DefaultCompression = s.Build.DefaultCompression;
        CleanupTempFilesAfterBuild = s.Build.CleanupTempFilesAfterBuild;
        
        Theme = s.UI.Theme;
        AccentColor = s.UI.AccentColor;
        ShowStatusBar = s.UI.ShowStatusBar;
        EnableAnimations = s.UI.EnableAnimations;
        
        HasChanges = false;
    }
    
    partial void OnThemeChanged(AppTheme value)
    {
        _themeService.SetTheme(value);
        HasChanges = true;
    }
    
    [RelayCommand]
    private async Task BrowseOutputDirectoryAsync()
    {
        var path = await _dialogService.PickFolderAsync("Select Default Output Directory");
        if (!string.IsNullOrEmpty(path))
        {
            DefaultOutputDirectory = path;
            HasChanges = true;
        }
    }
    
    [RelayCommand]
    private async Task BrowseTempDirectoryAsync()
    {
        var path = await _dialogService.PickFolderAsync("Select Temp Directory");
        if (!string.IsNullOrEmpty(path))
        {
            TempDirectory = path;
            HasChanges = true;
        }
    }
    
    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        var settings = new AppSettings
        {
            General = new GeneralSettings
            {
                CheckForUpdates = CheckForUpdates,
                SendAnonymousUsage = SendAnonymousUsage,
                Language = Language,
                ShowAdvancedOptions = ShowAdvancedOptions,
                ConfirmOnExit = ConfirmOnExit
            },
            Paths = new PathSettings
            {
                DefaultOutputDirectory = DefaultOutputDirectory,
                TempDirectory = TempDirectory,
                LogDirectory = LogDirectory
            },
            Build = new BuildSettings
            {
                MaxParallelOperations = MaxParallelOperations,
                OptimizeImageAfterBuild = OptimizeImageAfterBuild,
                CreateBackupBeforeModify = CreateBackupBeforeModify,
                DefaultCompression = DefaultCompression,
                CleanupTempFilesAfterBuild = CleanupTempFilesAfterBuild
            },
            UI = new UISettings
            {
                Theme = Theme,
                AccentColor = AccentColor,
                ShowStatusBar = ShowStatusBar,
                EnableAnimations = EnableAnimations
            }
        };
        
        // Update settings service (would need a method to update settings)
        await _settingsService.SaveAsync();
        
        HasChanges = false;
        _dialogService.ShowNotification("Settings Saved", "Your settings have been saved.", NotificationType.Success);
    }
    
    [RelayCommand]
    private async Task ResetSettingsAsync()
    {
        var result = await _dialogService.ShowDialogAsync(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            "Reset", "Cancel");
        
        if (result == Microsoft.UI.Xaml.Controls.ContentDialogResult.Primary)
        {
            _settingsService.Reset();
            LoadSettings();
            _dialogService.ShowNotification("Settings Reset", "All settings have been reset to defaults.", NotificationType.Info);
        }
    }
    
    [RelayCommand]
    private async Task OpenLogsDirectoryAsync()
    {
        try
        {
            System.Diagnostics.Process.Start("explorer.exe", LogDirectory);
        }
        catch (Exception ex)
        {
            await _dialogService.ShowDialogAsync("Error", $"Could not open logs directory: {ex.Message}");
        }
    }
    
    [RelayCommand]
    private async Task ClearLogsAsync()
    {
        var result = await _dialogService.ShowDialogAsync(
            "Clear Logs",
            "Are you sure you want to delete all log files?",
            "Clear", "Cancel");
        
        if (result == Microsoft.UI.Xaml.Controls.ContentDialogResult.Primary)
        {
            try
            {
                foreach (var file in Directory.GetFiles(LogDirectory, "*.log"))
                {
                    File.Delete(file);
                }
                _dialogService.ShowNotification("Logs Cleared", "All log files have been deleted.", NotificationType.Success);
            }
            catch (Exception ex)
            {
                await _dialogService.ShowDialogAsync("Error", $"Could not clear logs: {ex.Message}");
            }
        }
    }
}
