using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using DeployForge.App.Services;

namespace DeployForge.App.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly INavigationService _navigationService;
    private readonly IThemeService _themeService;
    private readonly ISettingsService _settingsService;
    private readonly IPowerShellService _psService;
    
    [ObservableProperty]
    private string _currentPageTitle = "Welcome";
    
    [ObservableProperty]
    private bool _isLoading;
    
    [ObservableProperty]
    private string _statusMessage = "Ready";
    
    [ObservableProperty]
    private bool _isBackEnabled;
    
    [ObservableProperty]
    private string _selectedNavItem = "Welcome";
    
    public MainViewModel(
        INavigationService navigationService,
        IThemeService themeService,
        ISettingsService settingsService,
        IPowerShellService psService)
    {
        _navigationService = navigationService;
        _themeService = themeService;
        _settingsService = settingsService;
        _psService = psService;
    }
    
    public async Task InitializeAsync()
    {
        IsLoading = true;
        StatusMessage = "Initializing...";
        
        try
        {
            await _settingsService.LoadAsync();
            await _psService.InitializeAsync();
            
            StatusMessage = "Ready";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Initialization error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
    
    [RelayCommand]
    private void NavigateTo(string pageKey)
    {
        if (_navigationService.NavigateTo(pageKey))
        {
            CurrentPageTitle = pageKey;
            SelectedNavItem = pageKey;
            IsBackEnabled = _navigationService.CanGoBack;
        }
    }
    
    [RelayCommand]
    private void GoBack()
    {
        if (_navigationService.GoBack())
        {
            CurrentPageTitle = _navigationService.CurrentPageKey;
            SelectedNavItem = _navigationService.CurrentPageKey;
            IsBackEnabled = _navigationService.CanGoBack;
        }
    }
}
