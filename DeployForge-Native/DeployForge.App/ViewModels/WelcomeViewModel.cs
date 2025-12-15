using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Models;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class WelcomeViewModel : ObservableObject
{
    private readonly INavigationService _navigationService;
    private readonly IDialogService _dialogService;
    private readonly IImageService _imageService;
    private readonly IProfileService _profileService;
    
    [ObservableProperty]
    private string? _selectedImagePath;
    
    [ObservableProperty]
    private ImageInfo? _selectedImageInfo;
    
    [ObservableProperty]
    private bool _hasSelectedImage;
    
    [ObservableProperty]
    private bool _isAnalyzing;
    
    [ObservableProperty]
    private List<Profile> _quickProfiles = new();
    
    [ObservableProperty]
    private Profile? _selectedProfile;
    
    public WelcomeViewModel(
        INavigationService navigationService,
        IDialogService dialogService,
        IImageService imageService,
        IProfileService profileService)
    {
        _navigationService = navigationService;
        _dialogService = dialogService;
        _imageService = imageService;
        _profileService = profileService;
        
        QuickProfiles = _profileService.BuiltInProfiles.Take(4).ToList();
    }
    
    [RelayCommand]
    private async Task BrowseImageAsync()
    {
        var path = await _dialogService.PickFileAsync(new[] { ".wim", ".esd", ".iso", ".vhd", ".vhdx" }, "Select Windows Image");
        
        if (!string.IsNullOrEmpty(path))
        {
            await LoadImageAsync(path);
        }
    }
    
    [RelayCommand]
    private async Task LoadImageAsync(string path)
    {
        SelectedImagePath = path;
        HasSelectedImage = false;
        IsAnalyzing = true;
        
        try
        {
            SelectedImageInfo = await _imageService.GetImageInfoAsync(path);
            HasSelectedImage = SelectedImageInfo != null;
        }
        finally
        {
            IsAnalyzing = false;
        }
    }
    
    [RelayCommand]
    private void SelectProfile(Profile profile)
    {
        SelectedProfile = profile;
    }
    
    [RelayCommand]
    private void StartQuickBuild()
    {
        if (SelectedImageInfo != null && SelectedProfile != null)
        {
            var config = new BuildConfiguration
            {
                SourceImage = SelectedImagePath!,
                ProfileId = SelectedProfile.Id,
                Features = SelectedProfile.Features
            };
            
            _navigationService.NavigateTo("Build", config);
        }
    }
    
    [RelayCommand]
    private void NavigateToBuild()
    {
        _navigationService.NavigateTo("Build", SelectedImagePath);
    }
    
    [RelayCommand]
    private void NavigateToProfiles()
    {
        _navigationService.NavigateTo("Profiles");
    }
    
    [RelayCommand]
    private void NavigateToAnalyze()
    {
        _navigationService.NavigateTo("Analyze", SelectedImagePath);
    }
}
