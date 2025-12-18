using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.App.ViewModels;

/// <summary>
/// ViewModel for the Welcome page.
/// </summary>
public partial class WelcomeViewModel : PageViewModelBase
{
    private readonly MainViewModel _mainViewModel;
    private readonly IImageService _imageService;
    private readonly ISettingsService _settingsService;
    
    public override string Title => "Welcome";
    public override string Icon => "\uE80F";
    
    [ObservableProperty]
    private string _selectedImagePath = string.Empty;
    
    [ObservableProperty]
    private ImageInfo? _imageInfo;
    
    [ObservableProperty]
    private bool _hasSelectedImage;
    
    [ObservableProperty]
    private bool _isDragOver;
    
    /// <summary>
    /// Recent image files.
    /// </summary>
    public ObservableCollection<RecentImageItem> RecentImages { get; } = new();
    
    /// <summary>
    /// Quick action buttons.
    /// </summary>
    public ObservableCollection<QuickAction> QuickActions { get; } = new();
    
    public WelcomeViewModel(
        MainViewModel mainViewModel,
        IImageService imageService,
        ISettingsService settingsService)
    {
        _mainViewModel = mainViewModel;
        _imageService = imageService;
        _settingsService = settingsService;
        
        // Initialize quick actions
        QuickActions.Add(new QuickAction("New Build", "\uE8F1", "Create a customized Windows image", OpenNewBuildAsync));
        QuickActions.Add(new QuickAction("Load Template", "\uE8A5", "Load a saved configuration template", LoadTemplateAsync));
        QuickActions.Add(new QuickAction("Gaming Profile", "\uE7FC", "Quick setup for gaming PC", ApplyGamingProfileAsync));
        QuickActions.Add(new QuickAction("Developer Profile", "\uE943", "Quick setup for development workstation", ApplyDevProfileAsync));
    }
    
    public override async Task OnNavigatedToAsync()
    {
        await LoadRecentImagesAsync();
    }
    
    /// <summary>
    /// Loads recent images from settings.
    /// </summary>
    private async Task LoadRecentImagesAsync()
    {
        RecentImages.Clear();
        
        foreach (var path in _settingsService.RecentImages)
        {
            if (!File.Exists(path)) continue;
            
            try
            {
                var fileInfo = new FileInfo(path);
                RecentImages.Add(new RecentImageItem
                {
                    Path = path,
                    FileName = fileInfo.Name,
                    Size = FormatFileSize(fileInfo.Length),
                    LastModified = fileInfo.LastWriteTime.ToString("g")
                });
            }
            catch
            {
                // Skip invalid files
            }
        }
        
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Opens a file picker to select an image.
    /// </summary>
    [RelayCommand]
    private async Task BrowseImageAsync()
    {
        // Note: File picker will be implemented in the View using Windows.Storage.Pickers
        // This method will be called by the View after file selection
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// Opens an image by path.
    /// </summary>
    [RelayCommand]
    private async Task OpenImageAsync(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return;
        
        await _mainViewModel.OpenImageCommand.ExecuteAsync(path);
    }
    
    /// <summary>
    /// Handles a dropped file.
    /// </summary>
    [RelayCommand]
    private async Task HandleDropAsync(string path)
    {
        IsDragOver = false;
        
        if (string.IsNullOrWhiteSpace(path)) return;
        
        var extension = Path.GetExtension(path).ToLowerInvariant();
        if (extension is ".wim" or ".esd" or ".vhd" or ".vhdx" or ".iso")
        {
            await OpenImageAsync(path);
        }
    }
    
    /// <summary>
    /// Sets drag state.
    /// </summary>
    [RelayCommand]
    private void SetDragOver(bool isDragOver)
    {
        IsDragOver = isDragOver;
    }
    
    /// <summary>
    /// Opens a recent image.
    /// </summary>
    [RelayCommand]
    private async Task OpenRecentAsync(RecentImageItem item)
    {
        if (item == null) return;
        await OpenImageAsync(item.Path);
    }
    
    /// <summary>
    /// Clears recent images list.
    /// </summary>
    [RelayCommand]
    private async Task ClearRecentAsync()
    {
        if (_settingsService is SettingsService ss)
        {
            ss.ClearRecentImages();
            await ss.SaveAsync();
        }
        
        RecentImages.Clear();
    }
    
    private async Task OpenNewBuildAsync()
    {
        await _mainViewModel.NavigateToCommand.ExecuteAsync(_mainViewModel.BuildPage);
    }
    
    private async Task LoadTemplateAsync()
    {
        await _mainViewModel.NavigateToCommand.ExecuteAsync(_mainViewModel.ProfilesPage);
    }
    
    private async Task ApplyGamingProfileAsync()
    {
        _mainViewModel.ProfilesPage.SelectProfile(Core.Enums.BuildProfileType.Gaming);
        await _mainViewModel.NavigateToCommand.ExecuteAsync(_mainViewModel.BuildPage);
    }
    
    private async Task ApplyDevProfileAsync()
    {
        _mainViewModel.ProfilesPage.SelectProfile(Core.Enums.BuildProfileType.Developer);
        await _mainViewModel.NavigateToCommand.ExecuteAsync(_mainViewModel.BuildPage);
    }
    
    private static string FormatFileSize(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double size = bytes;
        int order = 0;
        
        while (size >= 1024 && order < sizes.Length - 1)
        {
            order++;
            size /= 1024;
        }
        
        return $"{size:0.##} {sizes[order]}";
    }
}

/// <summary>
/// Recent image item for display.
/// </summary>
public class RecentImageItem
{
    public string Path { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string Size { get; set; } = string.Empty;
    public string LastModified { get; set; } = string.Empty;
}

/// <summary>
/// Quick action button.
/// </summary>
public class QuickAction
{
    public string Title { get; }
    public string Icon { get; }
    public string Description { get; }
    public Func<Task> Action { get; }
    
    public QuickAction(string title, string icon, string description, Func<Task> action)
    {
        Title = title;
        Icon = icon;
        Description = description;
        Action = action;
    }
}
