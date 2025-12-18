using Microsoft.Extensions.DependencyInjection;
using Microsoft.UI.Xaml;
using DeployForge.App.ViewModels;
using DeployForge.App.Views;
using DeployForge.Core.Interfaces;
using DeployForge.Services;

namespace DeployForge.App;

/// <summary>
/// Provides application-specific behavior to supplement the default Application class.
/// </summary>
public partial class App : Application
{
    private Window? _window;
    
    /// <summary>
    /// Service provider for dependency injection.
    /// </summary>
    public static IServiceProvider Services { get; private set; } = null!;
    
    /// <summary>
    /// Main window.
    /// </summary>
    public static MainWindow? MainWindow { get; private set; }
    
    /// <summary>
    /// Gets the current app instance.
    /// </summary>
    public static new App Current => (App)Application.Current;
    
    /// <summary>
    /// Initializes the singleton application object.
    /// </summary>
    public App()
    {
        this.InitializeComponent();
        
        // Configure services
        var services = new ServiceCollection();
        ConfigureServices(services);
        Services = services.BuildServiceProvider();
    }
    
    /// <summary>
    /// Configures the service collection.
    /// </summary>
    private void ConfigureServices(IServiceCollection services)
    {
        // Add DeployForge services
        services.AddDeployForgeServices();
        
        // Add ViewModels
        services.AddSingleton<MainViewModel>();
        services.AddTransient<WelcomeViewModel>();
        services.AddTransient<BuildViewModel>();
        services.AddTransient<ProfilesViewModel>();
        services.AddTransient<SettingsViewModel>();
    }
    
    /// <summary>
    /// Invoked when the application is launched.
    /// </summary>
    /// <param name="args">Details about the launch request and process.</param>
    protected override async void OnLaunched(LaunchActivatedEventArgs args)
    {
        // Create main window
        _window = new MainWindow();
        MainWindow = (MainWindow)_window;
        
        // Initialize main ViewModel
        var mainViewModel = Services.GetRequiredService<MainViewModel>();
        await mainViewModel.InitializeAsync();
        
        // Set DataContext
        if (_window.Content is FrameworkElement element)
        {
            element.DataContext = mainViewModel;
        }
        
        // Activate window
        _window.Activate();
    }
    
    /// <summary>
    /// Gets a service of the specified type.
    /// </summary>
    public static T GetService<T>() where T : class
    {
        return Services.GetRequiredService<T>();
    }
}
