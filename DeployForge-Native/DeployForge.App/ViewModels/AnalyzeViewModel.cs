using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Models;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class AnalyzeViewModel : ObservableObject
{
    private readonly IImageService _imageService;
    private readonly IDialogService _dialogService;
    private readonly IPowerShellService _psService;
    
    [ObservableProperty]
    private string? _imagePath;
    
    [ObservableProperty]
    private ImageInfo? _imageInfo;
    
    [ObservableProperty]
    private bool _isAnalyzing;
    
    [ObservableProperty]
    private List<InstalledPackage> _installedPackages = new();
    
    [ObservableProperty]
    private List<InstalledDriver> _installedDrivers = new();
    
    [ObservableProperty]
    private List<WindowsFeature> _windowsFeatures = new();
    
    [ObservableProperty]
    private List<LanguagePack> _languagePacks = new();
    
    [ObservableProperty]
    private ImageAnalysisResult? _analysisResult;
    
    [ObservableProperty]
    private string _selectedTab = "Overview";
    
    public AnalyzeViewModel(
        IImageService imageService,
        IDialogService dialogService,
        IPowerShellService psService)
    {
        _imageService = imageService;
        _dialogService = dialogService;
        _psService = psService;
    }
    
    public void Initialize(object? parameter)
    {
        if (parameter is string path)
        {
            ImagePath = path;
            AnalyzeImageAsync().ConfigureAwait(false);
        }
    }
    
    [RelayCommand]
    private async Task BrowseImageAsync()
    {
        var path = await _dialogService.PickFileAsync(
            new[] { ".wim", ".esd", ".iso", ".vhd", ".vhdx" },
            "Select Windows Image to Analyze");
        
        if (!string.IsNullOrEmpty(path))
        {
            ImagePath = path;
            await AnalyzeImageAsync();
        }
    }
    
    [RelayCommand]
    private async Task AnalyzeImageAsync()
    {
        if (string.IsNullOrEmpty(ImagePath)) return;
        
        IsAnalyzing = true;
        InstalledPackages.Clear();
        InstalledDrivers.Clear();
        WindowsFeatures.Clear();
        LanguagePacks.Clear();
        
        try
        {
            // Get basic image info
            ImageInfo = await _imageService.GetImageInfoAsync(ImagePath);
            
            // Mount image temporarily for analysis
            var mountResult = await _imageService.MountImageAsync(ImagePath);
            if (mountResult == null)
            {
                await _dialogService.ShowDialogAsync("Error", "Failed to mount image for analysis.");
                return;
            }
            
            var mountPoint = mountResult.MountPoint;
            
            try
            {
                // Get installed packages
                var packagesResult = await _psService.InvokeAsync($"dism /Image:'{mountPoint}' /Get-Packages");
                // Parse results...
                
                // Get drivers
                var driversResult = await _psService.InvokeAsync($"dism /Image:'{mountPoint}' /Get-Drivers");
                // Parse results...
                
                // Get features
                var featuresResult = await _psService.InvokeAsync($"dism /Image:'{mountPoint}' /Get-Features");
                // Parse results...
                
                // Create analysis summary
                AnalysisResult = new ImageAnalysisResult
                {
                    ImagePath = ImagePath,
                    AnalyzedAt = DateTime.Now,
                    PackageCount = InstalledPackages.Count,
                    DriverCount = InstalledDrivers.Count,
                    FeatureCount = WindowsFeatures.Count,
                    LanguageCount = LanguagePacks.Count
                };
            }
            finally
            {
                // Always dismount
                await _imageService.DismountImageAsync(mountPoint, saveChanges: false);
            }
        }
        catch (Exception ex)
        {
            await _dialogService.ShowDialogAsync("Analysis Error", ex.Message);
        }
        finally
        {
            IsAnalyzing = false;
        }
    }
    
    [RelayCommand]
    private async Task ExportReportAsync()
    {
        if (AnalysisResult == null) return;
        
        var path = await _dialogService.SaveFileAsync("image-analysis.json", new[] { ".json" }, "Export Analysis Report");
        
        if (!string.IsNullOrEmpty(path))
        {
            var report = new
            {
                AnalysisResult,
                ImageInfo,
                InstalledPackages,
                InstalledDrivers,
                WindowsFeatures,
                LanguagePacks
            };
            
            var json = System.Text.Json.JsonSerializer.Serialize(report, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });
            await File.WriteAllTextAsync(path, json);
            
            _dialogService.ShowNotification("Export Complete", $"Report saved to {path}", NotificationType.Success);
        }
    }
}

public record InstalledPackage(string Name, string Version, string State);
public record InstalledDriver(string Name, string Version, string Provider, string ClassName);
public record WindowsFeature(string Name, string State, string DisplayName);
public record LanguagePack(string Code, string Name, bool IsDefault);
public record ImageAnalysisResult
{
    public string ImagePath { get; init; } = "";
    public DateTime AnalyzedAt { get; init; }
    public int PackageCount { get; init; }
    public int DriverCount { get; init; }
    public int FeatureCount { get; init; }
    public int LanguageCount { get; init; }
}
