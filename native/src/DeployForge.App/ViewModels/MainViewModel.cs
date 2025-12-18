using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.Core.Interfaces;
using DeployForge.Core.Models;

namespace DeployForge.App.ViewModels;

/// <summary>
/// Main window ViewModel for navigation and app-level state.
/// </summary>
public partial class MainViewModel : ViewModelBase
{
    private readonly IImageService _imageService;
    private readonly ISettingsService _settingsService;
    
    [ObservableProperty]
    private PageViewModelBase? _currentPage;
    
    [ObservableProperty]
    private int _selectedNavigationIndex;
    
    [ObservableProperty]
    private bool _isImageMounted;
    
    [ObservableProperty]
    private string _currentImagePath = string.Empty;
    
    [ObservableProperty]
    private string _mountPath = string.Empty;
    
    [ObservableProperty]
    private ImageInfo? _currentImageInfo;
    
    [ObservableProperty]
    private string _statusMessage = "Ready";
    
    /// <summary>
    /// Available pages for navigation.
    /// </summary>
    public ObservableCollection<NavigationItem> NavigationItems { get; } = new();
    
    /// <summary>
    /// Recent image files.
    /// </summary>
    public ObservableCollection<string> RecentImages { get; } = new();
    
    /// <summary>
    /// Page ViewModels.
    /// </summary>
    public WelcomeViewModel WelcomePage { get; }
    public BuildViewModel BuildPage { get; }
    public ProfilesViewModel ProfilesPage { get; }
    public SettingsViewModel SettingsPage { get; }
    
    public MainViewModel(
        IImageService imageService,
        IFeatureService featureService,
        ITemplateService templateService,
        ISettingsService settingsService)
    {
        _imageService = imageService;
        _settingsService = settingsService;
        
        // Create page ViewModels
        WelcomePage = new WelcomeViewModel(this, imageService, settingsService);
        BuildPage = new BuildViewModel(this, imageService, featureService, templateService);
        ProfilesPage = new ProfilesViewModel(this, templateService);
        SettingsPage = new SettingsViewModel(settingsService);
        
        // Set up navigation items
        NavigationItems.Add(new NavigationItem("Welcome", "\uE80F", WelcomePage));
        NavigationItems.Add(new NavigationItem("Build", "\uE8F1", BuildPage));
        NavigationItems.Add(new NavigationItem("Profiles", "\uE77B", ProfilesPage));
        NavigationItems.Add(new NavigationItem("Settings", "\uE713", SettingsPage));
        
        CurrentPage = WelcomePage;
    }
    
    /// <summary>
    /// Initializes the ViewModel.
    /// </summary>
    public async Task InitializeAsync()
    {
        await _settingsService.LoadAsync();
        
        // Load recent images
        RecentImages.Clear();
        foreach (var image in _settingsService.RecentImages)
        {
            RecentImages.Add(image);
        }
        
        await WelcomePage.OnNavigatedToAsync();
    }
    
    /// <summary>
    /// Navigates to a page.
    /// </summary>
    [RelayCommand]
    private async Task NavigateToAsync(PageViewModelBase page)
    {
        if (CurrentPage == page) return;
        
        if (CurrentPage != null)
        {
            await CurrentPage.OnNavigatedFromAsync();
        }
        
        CurrentPage = page;
        await page.OnNavigatedToAsync();
        
        // Update selected index
        var item = NavigationItems.FirstOrDefault(n => n.Page == page);
        if (item != null)
        {
            SelectedNavigationIndex = NavigationItems.IndexOf(item);
        }
    }
    
    /// <summary>
    /// Navigates to page by index.
    /// </summary>
    [RelayCommand]
    private async Task NavigateByIndexAsync(int index)
    {
        if (index >= 0 && index < NavigationItems.Count)
        {
            await NavigateToAsync(NavigationItems[index].Page);
        }
    }
    
    /// <summary>
    /// Opens an image file.
    /// </summary>
    [RelayCommand]
    private async Task OpenImageAsync(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return;
        
        try
        {
            SetBusy("Loading image...");
            
            // Get image info
            var info = await _imageService.GetInfoAsync(path);
            CurrentImageInfo = info;
            CurrentImagePath = path;
            
            // Add to recent images
            _settingsService.AddRecentImage(path);
            await _settingsService.SaveAsync();
            
            if (!RecentImages.Contains(path))
            {
                RecentImages.Insert(0, path);
                if (RecentImages.Count > 10)
                {
                    RecentImages.RemoveAt(RecentImages.Count - 1);
                }
            }
            
            StatusMessage = $"Loaded: {Path.GetFileName(path)}";
            
            // Navigate to build page
            await NavigateToAsync(BuildPage);
        }
        catch (Exception ex)
        {
            SetError(ex.Message);
            StatusMessage = "Failed to load image";
        }
        finally
        {
            ClearBusy();
        }
    }
    
    /// <summary>
    /// Mounts the current image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanMountImage))]
    private async Task MountImageAsync(int index = 1)
    {
        if (string.IsNullOrWhiteSpace(CurrentImagePath)) return;
        
        try
        {
            SetBusy("Mounting image...");
            
            var result = await _imageService.MountAsync(
                CurrentImagePath, 
                index, 
                progress: Progress);
            
            IsImageMounted = true;
            MountPath = result.MountPath;
            StatusMessage = $"Image mounted at: {result.MountPath}";
            
            // Refresh build page
            BuildPage.UpdateMountStatus(true, result.MountPath);
        }
        catch (Exception ex)
        {
            SetError(ex.Message);
            StatusMessage = "Failed to mount image";
        }
        finally
        {
            ClearBusy();
        }
    }
    
    private bool CanMountImage() => !string.IsNullOrWhiteSpace(CurrentImagePath) && !IsImageMounted;
    
    /// <summary>
    /// Unmounts the current image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUnmountImage))]
    private async Task UnmountImageAsync(bool saveChanges = false)
    {
        if (string.IsNullOrWhiteSpace(MountPath)) return;
        
        try
        {
            SetBusy(saveChanges ? "Saving and unmounting..." : "Unmounting...");
            
            await _imageService.UnmountAsync(MountPath, saveChanges, Progress);
            
            IsImageMounted = false;
            MountPath = string.Empty;
            StatusMessage = saveChanges ? "Changes saved and image unmounted" : "Image unmounted";
            
            // Update build page
            BuildPage.UpdateMountStatus(false, string.Empty);
        }
        catch (Exception ex)
        {
            SetError(ex.Message);
            StatusMessage = "Failed to unmount image";
        }
        finally
        {
            ClearBusy();
        }
    }
    
    private bool CanUnmountImage() => IsImageMounted;
    
    partial void OnSelectedNavigationIndexChanged(int value)
    {
        if (value >= 0 && value < NavigationItems.Count)
        {
            _ = NavigateToAsync(NavigationItems[value].Page);
        }
    }
}

/// <summary>
/// Navigation item for the navigation view.
/// </summary>
public class NavigationItem
{
    /// <summary>
    /// Display name.
    /// </summary>
    public string Name { get; }
    
    /// <summary>
    /// Icon glyph (Segoe MDL2 Assets).
    /// </summary>
    public string Icon { get; }
    
    /// <summary>
    /// Associated page ViewModel.
    /// </summary>
    public PageViewModelBase Page { get; }
    
    public NavigationItem(string name, string icon, PageViewModelBase page)
    {
        Name = name;
        Icon = icon;
        Page = page;
    }
}
