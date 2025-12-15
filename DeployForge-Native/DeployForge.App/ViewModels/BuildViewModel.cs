using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Models;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class BuildViewModel : ObservableObject
{
    private readonly IImageService _imageService;
    private readonly IDialogService _dialogService;
    private readonly IProfileService _profileService;
    private readonly ISettingsService _settingsService;
    
    // Source
    [ObservableProperty] private string? _sourceImagePath;
    [ObservableProperty] private ImageInfo? _sourceImageInfo;
    [ObservableProperty] private int _selectedIndex = 1;
    
    // Output
    [ObservableProperty] private string? _outputPath;
    [ObservableProperty] private OutputFormat _outputFormat = OutputFormat.WIM;
    
    // Features - Debloat
    [ObservableProperty] private bool _enableDebloat;
    [ObservableProperty] private DebloatLevel _debloatLevel = DebloatLevel.Moderate;
    
    // Features - Privacy
    [ObservableProperty] private bool _enablePrivacy;
    [ObservableProperty] private PrivacyLevel _privacyLevel = PrivacyLevel.Balanced;
    [ObservableProperty] private bool _disableTelemetry;
    [ObservableProperty] private bool _disableCortana;
    [ObservableProperty] private bool _blockTelemetryDomains;
    
    // Features - Gaming
    [ObservableProperty] private bool _enableGaming;
    [ObservableProperty] private GamingProfile _gamingProfile = GamingProfile.Balanced;
    [ObservableProperty] private bool _installGamingRuntimes;
    [ObservableProperty] private bool _optimizeNetwork;
    
    // Features - Developer
    [ObservableProperty] private bool _enableDeveloper;
    [ObservableProperty] private bool _installWsl2;
    [ObservableProperty] private List<string> _selectedDevTools = new();
    
    // Features - Performance
    [ObservableProperty] private bool _optimizeServices;
    [ObservableProperty] private bool _disableAnimations;
    
    // Unattend
    [ObservableProperty] private bool _generateUnattend;
    [ObservableProperty] private string _computerName = "DESKTOP-PC";
    [ObservableProperty] private string _username = "Admin";
    [ObservableProperty] private string? _password;
    [ObservableProperty] private bool _skipOobe = true;
    
    // Build state
    [ObservableProperty] private bool _isBuilding;
    [ObservableProperty] private BuildProgress? _buildProgress;
    [ObservableProperty] private BuildResult? _buildResult;
    [ObservableProperty] private List<string> _buildLogs = new();
    
    private CancellationTokenSource? _buildCts;
    
    public BuildViewModel(
        IImageService imageService,
        IDialogService dialogService,
        IProfileService profileService,
        ISettingsService settingsService)
    {
        _imageService = imageService;
        _dialogService = dialogService;
        _profileService = profileService;
        _settingsService = settingsService;
    }
    
    public void Initialize(object? parameter)
    {
        if (parameter is string imagePath)
        {
            SourceImagePath = imagePath;
            LoadSourceImageAsync(imagePath).ConfigureAwait(false);
        }
        else if (parameter is BuildConfiguration config)
        {
            ApplyConfiguration(config);
        }
    }
    
    private async Task LoadSourceImageAsync(string path)
    {
        SourceImageInfo = await _imageService.GetImageInfoAsync(path);
        
        if (string.IsNullOrEmpty(OutputPath))
        {
            var dir = _settingsService.Settings.Paths.DefaultOutputDirectory;
            var name = Path.GetFileNameWithoutExtension(path) + "_custom" + Path.GetExtension(path);
            OutputPath = Path.Combine(dir, name);
        }
    }
    
    private void ApplyConfiguration(BuildConfiguration config)
    {
        SourceImagePath = config.SourceImage;
        SelectedIndex = config.SourceIndex;
        OutputPath = config.OutputPath;
        OutputFormat = config.OutputFormat;
        
        var f = config.Features;
        EnableDebloat = f.RemoveBloatware;
        DebloatLevel = f.DebloatLevel;
        EnablePrivacy = f.DisableTelemetry || f.DisableCortana;
        PrivacyLevel = f.PrivacyLevel;
        DisableTelemetry = f.DisableTelemetry;
        DisableCortana = f.DisableCortana;
        BlockTelemetryDomains = f.BlockTelemetryDomains;
        EnableGaming = f.EnableGameMode;
        GamingProfile = f.GamingProfile;
        InstallGamingRuntimes = f.InstallGamingRuntimes;
        OptimizeNetwork = f.OptimizeNetwork;
        EnableDeveloper = f.EnableDeveloperMode;
        InstallWsl2 = f.InstallWSL2;
        SelectedDevTools = f.DevTools;
        OptimizeServices = f.OptimizeServices;
        DisableAnimations = f.DisableAnimations;
        
        LoadSourceImageAsync(config.SourceImage).ConfigureAwait(false);
    }
    
    [RelayCommand]
    private async Task BrowseSourceAsync()
    {
        var path = await _dialogService.PickFileAsync(new[] { ".wim", ".esd", ".iso" }, "Select Source Image");
        if (!string.IsNullOrEmpty(path))
        {
            SourceImagePath = path;
            await LoadSourceImageAsync(path);
        }
    }
    
    [RelayCommand]
    private async Task BrowseOutputAsync()
    {
        var ext = OutputFormat.ToString().ToLowerInvariant();
        var path = await _dialogService.SaveFileAsync($"custom.{ext}", new[] { ext }, "Save Output Image");
        if (!string.IsNullOrEmpty(path))
        {
            OutputPath = path;
        }
    }
    
    [RelayCommand]
    private void ApplyProfile(Profile profile)
    {
        var f = profile.Features;
        EnableDebloat = f.RemoveBloatware;
        DebloatLevel = f.DebloatLevel;
        EnablePrivacy = f.DisableTelemetry || f.DisableCortana;
        PrivacyLevel = f.PrivacyLevel;
        DisableTelemetry = f.DisableTelemetry;
        DisableCortana = f.DisableCortana;
        BlockTelemetryDomains = f.BlockTelemetryDomains;
        EnableGaming = f.EnableGameMode;
        GamingProfile = f.GamingProfile;
        InstallGamingRuntimes = f.InstallGamingRuntimes;
        OptimizeNetwork = f.OptimizeNetwork;
        EnableDeveloper = f.EnableDeveloperMode;
        InstallWsl2 = f.InstallWSL2;
        SelectedDevTools = f.DevTools.ToList();
        OptimizeServices = f.OptimizeServices;
        DisableAnimations = f.DisableAnimations;
    }
    
    [RelayCommand]
    private async Task StartBuildAsync()
    {
        if (string.IsNullOrEmpty(SourceImagePath))
        {
            await _dialogService.ShowDialogAsync("Error", "Please select a source image first.");
            return;
        }
        
        IsBuilding = true;
        BuildLogs.Clear();
        BuildResult = null;
        _buildCts = new CancellationTokenSource();
        
        var config = CreateBuildConfiguration();
        
        var progress = new Progress<BuildProgress>(p =>
        {
            BuildProgress = p;
            if (!string.IsNullOrEmpty(p.StatusMessage))
            {
                BuildLogs.Add($"[{p.PercentComplete:F0}%] {p.StatusMessage}");
            }
        });
        
        try
        {
            BuildResult = await _imageService.BuildImageAsync(config, progress, _buildCts.Token);
            
            if (BuildResult.Success)
            {
                await _dialogService.ShowDialogAsync("Build Complete", $"Image saved to:\n{BuildResult.OutputPath}");
            }
            else
            {
                var errors = string.Join("\n", BuildResult.Errors.Select(e => e.Message));
                await _dialogService.ShowDialogAsync("Build Failed", errors);
            }
        }
        catch (OperationCanceledException)
        {
            BuildLogs.Add("Build cancelled by user.");
        }
        catch (Exception ex)
        {
            await _dialogService.ShowDialogAsync("Build Error", ex.Message);
        }
        finally
        {
            IsBuilding = false;
            _buildCts?.Dispose();
            _buildCts = null;
        }
    }
    
    [RelayCommand]
    private void CancelBuild()
    {
        _buildCts?.Cancel();
    }
    
    private BuildConfiguration CreateBuildConfiguration() => new()
    {
        SourceImage = SourceImagePath!,
        SourceIndex = SelectedIndex,
        OutputPath = OutputPath ?? "",
        OutputFormat = OutputFormat,
        Features = new ProfileFeatures
        {
            RemoveBloatware = EnableDebloat,
            DebloatLevel = DebloatLevel,
            DisableTelemetry = DisableTelemetry,
            DisableCortana = DisableCortana,
            BlockTelemetryDomains = BlockTelemetryDomains,
            PrivacyLevel = PrivacyLevel,
            EnableGameMode = EnableGaming,
            GamingProfile = GamingProfile,
            InstallGamingRuntimes = InstallGamingRuntimes,
            OptimizeNetwork = OptimizeNetwork,
            EnableDeveloperMode = EnableDeveloper,
            InstallWSL2 = InstallWsl2,
            DevTools = SelectedDevTools,
            OptimizeServices = OptimizeServices,
            DisableAnimations = DisableAnimations
        },
        Unattend = GenerateUnattend ? new UnattendConfiguration
        {
            ComputerName = ComputerName,
            Username = Username,
            Password = Password,
            SkipOOBE = SkipOobe
        } : null
    };
}
