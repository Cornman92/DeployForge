using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Enums;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.App.ViewModels;

/// <summary>
/// ViewModel for the Build page.
/// </summary>
public partial class BuildViewModel : PageViewModelBase
{
    private readonly MainViewModel _mainViewModel;
    private readonly IImageService _imageService;
    private readonly IFeatureService _featureService;
    private readonly ITemplateService _templateService;
    
    public override string Title => "Build";
    public override string Icon => "\uE8F1";
    
    #region Observable Properties
    
    [ObservableProperty]
    private bool _isImageMounted;
    
    [ObservableProperty]
    private string _mountPath = string.Empty;
    
    [ObservableProperty]
    private BuildProfile _currentProfile = new();
    
    [ObservableProperty]
    private int _selectedTabIndex;
    
    [ObservableProperty]
    private int _buildProgress;
    
    [ObservableProperty]
    private string _buildStatus = string.Empty;
    
    [ObservableProperty]
    private bool _isBuilding;
    
    // Gaming options
    [ObservableProperty]
    private bool _enableGaming;
    
    [ObservableProperty]
    private GamingProfile _selectedGamingProfile = GamingProfile.Balanced;
    
    [ObservableProperty]
    private bool _enableGameMode = true;
    
    [ObservableProperty]
    private bool _disableGameBar;
    
    [ObservableProperty]
    private bool _optimizeNetwork = true;
    
    [ObservableProperty]
    private bool _installRuntimes = true;
    
    // Debloat options
    [ObservableProperty]
    private bool _enableDebloat;
    
    [ObservableProperty]
    private DebloatLevel _selectedDebloatLevel = DebloatLevel.Standard;
    
    [ObservableProperty]
    private bool _disableTelemetry = true;
    
    [ObservableProperty]
    private bool _disableCortana = true;
    
    [ObservableProperty]
    private PrivacyLevel _selectedPrivacyLevel = PrivacyLevel.Standard;
    
    // Developer options
    [ObservableProperty]
    private bool _enableDevEnvironment;
    
    [ObservableProperty]
    private DevelopmentProfile _selectedDevProfile = DevelopmentProfile.General;
    
    [ObservableProperty]
    private bool _enableDeveloperMode;
    
    [ObservableProperty]
    private bool _enableWSL2;
    
    // Browser options
    [ObservableProperty]
    private bool _enableBrowsers;
    
    [ObservableProperty]
    private BrowserType _selectedDefaultBrowser = BrowserType.Edge;
    
    [ObservableProperty]
    private bool _installChrome;
    
    [ObservableProperty]
    private bool _installFirefox;
    
    // UI customization
    [ObservableProperty]
    private bool _enableUICustomization;
    
    [ObservableProperty]
    private UIProfile _selectedUIProfile = UIProfile.Modern;
    
    [ObservableProperty]
    private bool _enableDarkMode = true;
    
    [ObservableProperty]
    private bool _disableWidgets;
    
    #endregion
    
    /// <summary>
    /// Available gaming profiles.
    /// </summary>
    public ObservableCollection<GamingProfile> GamingProfiles { get; } = new(Enum.GetValues<GamingProfile>());
    
    /// <summary>
    /// Available debloat levels.
    /// </summary>
    public ObservableCollection<DebloatLevel> DebloatLevels { get; } = new(Enum.GetValues<DebloatLevel>());
    
    /// <summary>
    /// Available development profiles.
    /// </summary>
    public ObservableCollection<DevelopmentProfile> DevelopmentProfiles { get; } = new(Enum.GetValues<DevelopmentProfile>());
    
    /// <summary>
    /// Available browser types.
    /// </summary>
    public ObservableCollection<BrowserType> BrowserTypes { get; } = new(Enum.GetValues<BrowserType>());
    
    /// <summary>
    /// Available UI profiles.
    /// </summary>
    public ObservableCollection<UIProfile> UIProfiles { get; } = new(Enum.GetValues<UIProfile>());
    
    /// <summary>
    /// Available privacy levels.
    /// </summary>
    public ObservableCollection<PrivacyLevel> PrivacyLevels { get; } = new(Enum.GetValues<PrivacyLevel>());
    
    /// <summary>
    /// Build log entries.
    /// </summary>
    public ObservableCollection<BuildLogEntry> BuildLog { get; } = new();
    
    public BuildViewModel(
        MainViewModel mainViewModel,
        IImageService imageService,
        IFeatureService featureService,
        ITemplateService templateService)
    {
        _mainViewModel = mainViewModel;
        _imageService = imageService;
        _featureService = featureService;
        _templateService = templateService;
    }
    
    /// <summary>
    /// Updates mount status from main ViewModel.
    /// </summary>
    public void UpdateMountStatus(bool isMounted, string mountPath)
    {
        IsImageMounted = isMounted;
        MountPath = mountPath;
    }
    
    /// <summary>
    /// Applies a predefined profile.
    /// </summary>
    public void ApplyProfile(BuildProfile profile)
    {
        CurrentProfile = profile;
        
        // Update UI based on profile
        EnableGaming = profile.EnableGaming;
        EnableDebloat = profile.EnableDebloat;
        EnableDevEnvironment = profile.EnableDevEnvironment;
        EnableBrowsers = profile.EnableBrowsers;
        EnableUICustomization = profile.EnableUICustomization;
        
        if (profile.Gaming != null)
        {
            SelectedGamingProfile = profile.Gaming.Profile;
            EnableGameMode = profile.Gaming.EnableGameMode;
            DisableGameBar = profile.Gaming.DisableGameBar;
            OptimizeNetwork = profile.Gaming.OptimizeNetwork;
            InstallRuntimes = profile.Gaming.InstallRuntimes;
        }
        
        if (profile.Debloat != null)
        {
            SelectedDebloatLevel = profile.Debloat.Level;
            DisableTelemetry = profile.Debloat.DisableTelemetry;
            DisableCortana = profile.Debloat.DisableCortana;
            SelectedPrivacyLevel = profile.Debloat.PrivacyLevel;
        }
        
        if (profile.DevEnvironment != null)
        {
            SelectedDevProfile = profile.DevEnvironment.Profile;
            EnableDeveloperMode = profile.DevEnvironment.EnableDeveloperMode;
            EnableWSL2 = profile.DevEnvironment.EnableWSL2;
        }
        
        if (profile.Browsers != null)
        {
            SelectedDefaultBrowser = profile.Browsers.DefaultBrowser;
            InstallChrome = profile.Browsers.InstallChrome;
            InstallFirefox = profile.Browsers.InstallFirefox;
        }
        
        if (profile.UICustomization != null)
        {
            SelectedUIProfile = profile.UICustomization.Profile;
            EnableDarkMode = profile.UICustomization.EnableDarkMode;
            DisableWidgets = profile.UICustomization.DisableWidgets;
        }
        
        AddLogEntry($"Applied profile: {profile.Name}", LogLevel.Info);
    }
    
    /// <summary>
    /// Mounts the image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanMountImage))]
    private async Task MountImageAsync()
    {
        await _mainViewModel.MountImageCommand.ExecuteAsync(1);
    }
    
    private bool CanMountImage() => !IsImageMounted && _mainViewModel.CurrentImageInfo != null;
    
    /// <summary>
    /// Unmounts the image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUnmountImage))]
    private async Task UnmountImageAsync()
    {
        await _mainViewModel.UnmountImageCommand.ExecuteAsync(false);
    }
    
    private bool CanUnmountImage() => IsImageMounted;
    
    /// <summary>
    /// Starts the build process.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanBuild))]
    private async Task BuildAsync()
    {
        if (!IsImageMounted)
        {
            AddLogEntry("Image must be mounted before building", LogLevel.Error);
            return;
        }
        
        IsBuilding = true;
        BuildLog.Clear();
        BuildProgress = 0;
        BuildStatus = "Starting build...";
        
        try
        {
            var profile = BuildCurrentProfile();
            
            AddLogEntry($"Starting build with profile: {profile.Name}", LogLevel.Info);
            
            var progress = new Progress<ProgressInfo>(info =>
            {
                BuildProgress = info.Percentage;
                BuildStatus = info.Message;
                AddLogEntry(info.Message, LogLevel.Info);
            });
            
            var result = await _featureService.ApplyProfileAsync(
                MountPath, 
                profile, 
                progress);
            
            if (result.Success)
            {
                BuildProgress = 100;
                BuildStatus = "Build completed successfully!";
                AddLogEntry($"Build completed in {result.Duration.TotalSeconds:0.0}s", LogLevel.Success);
                
                foreach (var change in result.Changes)
                {
                    AddLogEntry(change, LogLevel.Info);
                }
            }
            else
            {
                BuildStatus = "Build failed";
                AddLogEntry($"Build failed: {result.Error}", LogLevel.Error);
            }
            
            foreach (var warning in result.Warnings)
            {
                AddLogEntry(warning, LogLevel.Warning);
            }
        }
        catch (Exception ex)
        {
            BuildStatus = "Build failed";
            AddLogEntry($"Error: {ex.Message}", LogLevel.Error);
        }
        finally
        {
            IsBuilding = false;
        }
    }
    
    private bool CanBuild() => IsImageMounted && !IsBuilding;
    
    /// <summary>
    /// Saves the current configuration as a template.
    /// </summary>
    [RelayCommand]
    private async Task SaveAsTemplateAsync(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return;
        
        var profile = BuildCurrentProfile();
        profile.Name = name;
        profile.Type = BuildProfileType.Custom;
        
        if (_templateService is TemplateService ts)
        {
            await ts.SaveTemplateAsync(profile);
            AddLogEntry($"Saved template: {name}", LogLevel.Success);
        }
    }
    
    /// <summary>
    /// Builds the current profile from UI settings.
    /// </summary>
    private BuildProfile BuildCurrentProfile()
    {
        return new BuildProfile
        {
            Name = CurrentProfile.Name ?? "Custom Build",
            Description = "Custom build configuration",
            Type = BuildProfileType.Custom,
            EnableGaming = EnableGaming,
            EnableDebloat = EnableDebloat,
            EnableDevEnvironment = EnableDevEnvironment,
            EnableBrowsers = EnableBrowsers,
            EnableUICustomization = EnableUICustomization,
            PrivacyLevel = SelectedPrivacyLevel,
            Gaming = EnableGaming ? new GamingConfig
            {
                Profile = SelectedGamingProfile,
                EnableGameMode = EnableGameMode,
                DisableGameBar = DisableGameBar,
                OptimizeNetwork = OptimizeNetwork,
                InstallRuntimes = InstallRuntimes
            } : null,
            Debloat = EnableDebloat ? new DebloatConfig
            {
                Level = SelectedDebloatLevel,
                DisableTelemetry = DisableTelemetry,
                DisableCortana = DisableCortana,
                PrivacyLevel = SelectedPrivacyLevel
            } : null,
            DevEnvironment = EnableDevEnvironment ? new DevEnvironmentConfig
            {
                Profile = SelectedDevProfile,
                EnableDeveloperMode = EnableDeveloperMode,
                EnableWSL2 = EnableWSL2
            } : null,
            Browsers = EnableBrowsers ? new BrowserConfig
            {
                DefaultBrowser = SelectedDefaultBrowser,
                InstallChrome = InstallChrome,
                InstallFirefox = InstallFirefox
            } : null,
            UICustomization = EnableUICustomization ? new UIConfig
            {
                Profile = SelectedUIProfile,
                EnableDarkMode = EnableDarkMode,
                DisableWidgets = DisableWidgets
            } : null
        };
    }
    
    private void AddLogEntry(string message, LogLevel level)
    {
        BuildLog.Add(new BuildLogEntry
        {
            Timestamp = DateTime.Now,
            Message = message,
            Level = level
        });
    }
}

/// <summary>
/// Build log entry.
/// </summary>
public class BuildLogEntry
{
    public DateTime Timestamp { get; set; }
    public string Message { get; set; } = string.Empty;
    public LogLevel Level { get; set; }
    
    public string LevelIcon => Level switch
    {
        LogLevel.Info => "\uE946",
        LogLevel.Success => "\uE73E",
        LogLevel.Warning => "\uE7BA",
        LogLevel.Error => "\uE711",
        _ => "\uE946"
    };
}

/// <summary>
/// Log level for build entries.
/// </summary>
public enum LogLevel
{
    Info,
    Success,
    Warning,
    Error
}
