using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.UI.Xaml;
using DeployForge.App.Services;
using DeployForge.App.ViewModels;
using DeployForge.App.Views;

namespace DeployForge.App;

public partial class App : Application
{
    public static IHost Host { get; private set; } = null!;
    public static T GetService<T>() where T : class => Host.Services.GetRequiredService<T>();
    
    private Window? _mainWindow;
    
    public App()
    {
        Host = Microsoft.Extensions.Hosting.Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                // Core Services
                services.AddSingleton<INavigationService, NavigationService>();
                services.AddSingleton<IThemeService, ThemeService>();
                services.AddSingleton<IDialogService, DialogService>();
                services.AddSingleton<ISettingsService, SettingsService>();
                services.AddSingleton<IPowerShellService, PowerShellService>();
                services.AddSingleton<IImageService, ImageService>();
                services.AddSingleton<IProfileService, ProfileService>();
                
                // ViewModels
                services.AddTransient<MainViewModel>();
                services.AddTransient<WelcomeViewModel>();
                services.AddTransient<BuildViewModel>();
                services.AddTransient<ProfilesViewModel>();
                services.AddTransient<AnalyzeViewModel>();
                services.AddTransient<SettingsViewModel>();
                
                // Views
                services.AddTransient<MainWindow>();
                services.AddTransient<WelcomePage>();
                services.AddTransient<BuildPage>();
                services.AddTransient<ProfilesPage>();
                services.AddTransient<AnalyzePage>();
                services.AddTransient<SettingsPage>();
            })
            .Build();
        
        this.InitializeComponent();
    }
    
    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _mainWindow = GetService<MainWindow>();
        _mainWindow.Activate();
    }
}
