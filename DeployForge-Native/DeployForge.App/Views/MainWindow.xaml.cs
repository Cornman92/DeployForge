using Microsoft.UI.Xaml;
using DeployForge.App.Services;
using DeployForge.App.ViewModels;
using WinRT.Interop;

namespace DeployForge.App.Views;

public sealed partial class MainWindow : Window
{
    public MainViewModel ViewModel { get; }
    
    private readonly INavigationService _navigationService;
    private readonly IThemeService _themeService;
    private readonly IDialogService _dialogService;
    
    public MainWindow()
    {
        this.InitializeComponent();
        
        ViewModel = App.GetService<MainViewModel>();
        _navigationService = App.GetService<INavigationService>();
        _themeService = App.GetService<IThemeService>();
        _dialogService = App.GetService<IDialogService>();
        
        // Set up window
        Title = "DeployForge";
        ExtendsContentIntoTitleBar = false;
        
        // Initialize services
        _navigationService.Initialize(ContentFrame);
        _themeService.Initialize(this);
        
        // Get window handle for dialogs
        var hwnd = WindowNative.GetWindowHandle(this);
        _dialogService.Initialize(Content.XamlRoot!, hwnd);
        
        // Navigate to welcome page
        _navigationService.NavigateTo("Welcome");
        
        // Initialize ViewModel
        Loaded += async (s, e) =>
        {
            _dialogService.Initialize(Content.XamlRoot!, hwnd);
            await ViewModel.InitializeAsync();
        };
    }
}
